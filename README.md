# cbsky.app (see bsky)
bsky implemented embeds, but 
  - they also implemented a "ask other apps not to show my skeets to logged out users, and don't show it to them on the official app" feature, which makes it not work for those users
  - it doesn't work with links with dids currently (this is trivial to fix, but kinda funny that they prefer the type of link that can break)

and some of my friends still don't have a bsky account (and i get not wanting to do it until public federation, jack dorsey and all).

i see a funny skeet (that is fully public information, as explained in https://blueskyweb.zendesk.com/hc/en-us/articles/15835264007693-Data-Privacy). i want to show it to my friends. i post on discord.

<img width="436" alt="image" src="https://github.com/goeo-/cbsky.app/assets/6651009/e61f1344-4ce4-4d27-9a90-4ca8b22d825a">

no embed. the friend clicks it.

<img width="484" alt="image" src="https://github.com/goeo-/cbsky.app/assets/6651009/57fe5ee1-a63f-453e-9da5-dcb83e13b176">

sign in required?! but all the data is public!

OR

i put a c before bsky in the link before sending it

<img width="510" alt="image" src="https://github.com/goeo-/cbsky.app/assets/6651009/b5d2a576-7385-4454-9b1c-e537077f6d53">

friend clicks it

<img width="1100" alt="image" src="https://github.com/goeo-/cbsky.app/assets/6651009/950580ce-56f3-4bc7-90ac-2417aefa0258">

and it redirects to nice frontend they can use to view the public information.

## implementation detail

cbsky.app never authenticates with anything. it only relies on com.atproto lexicons, and only talks to PDSes. the images are linked directly as a PDS com.atproto.sync.getBlob call, so mirroring or relying on the bsky cdn is not required.

the "Discourage apps from showing my account to logged-out users
Bluesky will not show your profile and posts to logged-out users. Other apps may not honor this request. This does not make your account private.
Note: Bluesky is an open and public network. This setting only limits the visibility of your content on the Bluesky app and website, and other apps may not respect this setting. Your content may still be shown to logged-out users by other apps and websites." option is too much explanation necessary for a privacy feature, and it WILL cause confusion. some of the intent behind cbsky.app is to remind people that their bsky data is public, and this option really only adds a funny tag to your profile record.
