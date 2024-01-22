from async_dns.core import types as DNSType
from async_dns.resolver import ProxyResolver
import httpx
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/profile/{profile}")
async def get_profile_info(request: Request, profile: str):
    did = None
    if profile.startswith('did:'):
        did = profile
    else:
        did = await resolve_handle(profile)

    pds, handle = await get_pds_and_handle(did)
    profile = await get_profile(pds, did)
    try:
        avatar = blob_url(pds, did, profile['value']['avatar']['ref']['$link'])
    except KeyError:
        avatar = None
    try:
        bio = profile['value']['description']
    except KeyError:
        bio = None
    try:
        display_name = profile['value']['displayName']
    except KeyError:
        display_name = None
    disregard = False
    try:
        values = profile['value']['labels']['values']
        for value in values:
            if value['val'] == '!no-unauthenticated':
                disregard = True
                break
    except KeyError:
        pass

    url = ('https://skychat.social/#profile/' if disregard else 'https://bsky.app/profile/') + did

    return templates.TemplateResponse(
        request=request, name="profile.html", context={
            "disregard": disregard,
            "display_name": display_name,
            "handle": handle,
            "avatar": avatar,
            "bio": bio,
            "url": url
        }
    )

@app.get("/profile/{profile}/post/{rkey}")
async def get_post_info(profile, rkey):
    did = None
    if profile.startswith('did:'):
        did = profile
    else:
        did = await resolve_handle(profile)

    pds, handle = await get_pds_and_handle(did)
    profile = await get_profile(pds, did)
    try:
        avatar = blob_url(pds, did, profile['value']['avatar']['ref']['$link'])
    except KeyError:
        avatar = None
    try:
        bio = profile['value']['description']
    except KeyError:
        bio = None
    try:
        display_name = profile['value']['displayName']
    except KeyError:
        display_name = None
    disregard = False
    try:
        values = profile['value']['labels']['values']
        for value in values:
            if value['val'] == '!no-unauthenticated':
                disregard = True
                break
    except KeyError:
        pass
    post = await get_post(pds, did, rkey)

    return f'[disregard: {disregard}] post from {display_name} (@{handle}) [avatar: {avatar}] [bio: {bio}] {post}'
    # todo embeds, replies

dns_resolver = ProxyResolver()
client = httpx.AsyncClient()

class CannotResolveHandleException(Exception):
    pass

async def resolve_handle(handle):
    res, _ = await dns_resolver.query('_atproto.' + handle, DNSType.TXT)
    if len(res.an) >= 1:
        data = res.an[0].data.data
        assert data.startswith('did=')
        return data[4:]
    try:
        res = await client.get(f'https://{handle}/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    except Exception:
        raise CannotResolveHandleException
    try:
        return res.json()['did']
    except (KeyError, json.decoder.JSONDecodeError):
        raise CannotResolveHandleException

class InvalidDIDException(Exception):
    pass

async def get_pds_and_handle(did):
    if did.startswith('did:plc:'):
        doc = (await client.get(f'https://plc.directory/{did}')).json()
    elif did.startswith('did:web:'):
        doc = (await client.get(f'https://{did[8:]}/.well-known/did.json')).json()
    else:
        raise InvalidDIDException
    
    handle = None
    for aka in doc.get('alsoKnownAs', []):
        if aka.startswith('at://'):
            handle = aka[5:]
            break
    if not handle:
        raise InvalidDIDException
    
    pds = None
    for service in doc.get('service', []):
        if service.get('id', '') == '#atproto_pds' and service.get('type', '') == 'AtprotoPersonalDataServer':
            pds = service.get('serviceEndpoint')
            break
    if not pds:
        raise InvalidDIDException
    
    return pds, handle

async def get_profile(pds, did):
    return (await client.get(f'{pds}/xrpc/com.atproto.repo.getRecord?repo={did}&collection=app.bsky.actor.profile&rkey=self')).json()

async def get_post(pds, did, rkey):
    return (await client.get(f'{pds}/xrpc/com.atproto.repo.getRecord?repo={did}&collection=app.bsky.feed.post&rkey={rkey}')).json()

def blob_url(pds, did, cid):
    return f'{pds}/xrpc/com.atproto.sync.getBlob?did={did}&cid={cid}'

# text only
# reply
# qrs
# image
# qrs with image