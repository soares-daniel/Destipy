# Destipy

This is a asynchronous Python Wrapper around the Bungie API. It allows one to send requests to all given endpoints of the Bungie API seen in their [Bungie.Net API Documentation](https://bungie-net.github.io/multi/index.html).

NOTE: 

* This is my first real project which was meant for a Discord Bot for my own Server but then decided to release, which means that bugs are likely.
* Some of the code is inspired or taken from [pydest](https://github.com/jgayfer/pydest/tree/master/pydest) and [aiobungie](https://github.com/nxtlo/aiobungie) so check them out!

ISSUES:

* Most of the POST requests are not working but already available to choose, so don't be surprised if they return nothing.
* I will also overwork the design but just wanted to get something done and release it already :).

## Features

* Every endpoint in the documentation is implemented, POST and GET.
* Download and Extraction of the manifest to a .content file.
* Download and Extraction of the manifest to a MongoDB database (COMING SOON).

## Examples

Here are a few examples:

* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)
* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)
* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)

## Usage

Install `Destipy`:

```
$ pip install destipy
```

In you project you can use it as a simple client without authentication by initialize a client with your Api Key like this:

```
client = DestinyClient(<API_KEY>)
user = await userEndpoints.GetBungieNetUserById(<MEMBERSHIP_ID>)
```

If you plan on using a specific category of endpoints multiple times you can also use the endpoint category itself as a class:

```
client = DestinyClient(<API_KEY>)
user_endpoints = client.user
user = await user_endpoints.GetBungieNetUserById(<MEMBERSHIP_ID>)
```

## Contact

Discord: `Sedamaso#5217`
