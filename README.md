# Destipy

This is a asynchronous Python Wrapper around the Bungie API. It allows one to send requests to all given endpoints of the Bungie API seen in their [Bungie.Net API Documentation](https://bungie-net.github.io/multi/index.html).

NOTE:

* The endpoints are parsed from the API documentation and are therefore not tested, some of them might not work or are missing parameters due to inconsistencies in the documentation.
* Some of the code is inspired or taken from [pydest](https://github.com/jgayfer/pydest/tree/master/pydest) and [aiobungie](https://github.com/nxtlo/aiobungie) so check them out!

## Features

* Every endpoint in the documentation is implemented, POST and GET.
* Download and Extraction of the manifest to a .content file.
* Download and Extraction of the manifest to a MongoDB database (COMING SOON).
* Logging with own logger or with the default logger by adding a file "logs/Destipy.log" ('logs' being a folder) in the root folder.

## Examples

Here are a few examples:

* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)
* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)
* [COMING SOON](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)

### Requirements

* aiohttp

Install `Destipy`:

```
pip install Destipy
```

In you project you can use it as a simple client without authentication by initialize a client with your Api Key like this:

```
from destipy.destiny_client import DestinyClient

client = DestinyClient(<API_KEY>)
user = await client.user.GetBungieNetUserById(<MEMBERSHIP_ID>)
```

If you plan on using a specific category of endpoints multiple times you can also use the endpoint category itself as a class:

```
from destipy.destiny_client import DestinyClient

client = DestinyClient(<API_KEY>)
user_endpoints = client.user
user = await user_endpoints.GetBungieNetUserById(<MEMBERSHIP_ID>)
```

## Contact

Discord: `sedam79`
