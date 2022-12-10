"""This module contains the Requester class, which handles all the requests to the Bungie API.

NOTE: Most of the code is taken from:
    https://github.com/nxtlo/aiobungie/blob/master/aiobungie/rest.py
"""

import asyncio
import base64
import http
import random
import time
from typing import Optional

import aiohttp

from destipy.utils.error import (DestipyException, DestipyRunTimeError, HTTPError,
                    RateLimitedError)


class Requester:
    """
    This class handles all the requests to the Bungie API.
    """
    def __init__(self, api_key, max_retries, max_rate_limit_retries, logger):
        self.logger = logger
        self.api_key = api_key
        self.max_retries = max_retries
        self.max_rate_limit_retries = max_rate_limit_retries

    async def handle_ratelimit(self,
        response: aiohttp.ClientResponse,
        method: str,
        route: str,
        max_ratelimit_retries: int = 3,
    ) -> None:
        """Handles the ratelimiting for the client.

        Args:
            response (aiohttp.ClientResponse): The response to handle.
            method (str): The method of the request.
            route (str): The route of the request.
            max_ratelimit_retries (int, optional):
            The max retries number if requests hit a `429` status code. Defaults to 3.

        Raises:
        HTTPError: If too many requests are made.
            DestipyRunTimeError: If max rate limit retries are reached.
            RateLimitedError: If we are being rate limited.
        """
        if response.status != http.HTTPStatus.TOO_MANY_REQUESTS:
            return

        if response.content_type != "application/json":
            raise HTTPError(
                f"Being ratelimited on non JSON request, {response.content_type}.",
                http.HTTPStatus.TOO_MANY_REQUESTS,
            )

        count: int = 0
        json = await response.json()
        retry_after = float(json["ThrottleSeconds"])

        while True:
            if count == max_ratelimit_retries:
                raise DestipyRunTimeError()

            if retry_after <= 0:
                # We sleep for a little bit to avoid funky behavior.
                sleep_time = float(random.random() + 0.93) / 2

                self.logger.warning(
                    "We're being ratelimited with method %s route %s. Sleeping for %.2fs.",
                    method,
                    route,
                    sleep_time,
                )
                count += 1
                await asyncio.sleep(sleep_time)
                continue

            raise RateLimitedError(
                body=json,
                url=str(response.real_url),
                retry_after=retry_after,
            )

    async def request(
        self,
        method: str,
        url: str,
        access_token: Optional[str] = None,
        data: Optional[dict] = None,
        oauth: Optional[bool] = False,
        refresh: Optional[bool] = False,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> dict:
        """Makes a request to the Bungie API.

        Args:
            method (str): The method of the request.
            url (str): The url of the request.
            access_token (str, optional): The access token to use for the request. Defaults to None.
            data (str, optional): The data to send with post requests. Defaults to None.
            oauth (bool, optional): Whether or not the request is an oauth request
            (Only for token fetching). Defaults to False.
            refresh (bool, optional): Whether or not the request is a refresh request
            (Only for token refreshing). Defaults to False.
            client_id (str, optional): The client id of your application (Only for oauth needed).
            Defaults to None.
            client_secret (str, optional): The client secret of your application
            (Only for oauth needed). Defaults to None.
        Raises:
            DestipyException: If the request fails.

        Returns:
            dict: The response from the Bungie API.

        """
        retries: int = 0
        while True:
            try:
                if oauth:
                    encoded = base64.b64encode(f'{client_id}:{client_secret}'
                                         .encode('utf-8')).decode('utf-8')
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-API-Key": self.api_key,
                        "Authorization": f"Basic {encoded}",
                    }
                elif refresh:
                    headers = {
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/x-www-form-urlencoded",
                    }
                elif access_token:
                    headers = {
                        "X-API-Key": self.api_key,
                        "Authorization": "Bearer {}".format(access_token)
                    }
                else:
                    headers = {"X-API-Key": self.api_key}

                async with aiohttp.ClientSession() as session:
                    taken_time = time.monotonic()
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        data=data,
                        ) as response:
                        response_time = (time.monotonic() - taken_time)
                        self.logger.debug(f"GET {url} -> {response.status} {response.reason}. Taken time: {response_time}")

                        await self.handle_ratelimit(response, method, url,
                                                    self.max_rate_limit_retries)

                        if response.status == http.HTTPStatus.NO_CONTENT:
                            return {}

                        if 300 > response.status >= 200:
                            return await response.json()

                        if response.status in {500, 502, 503, 504} and retries < self.max_retries:
                            sleep_time = float(random.random() + 0.93) / 2
                            self.logger.warning("Got %s status code. Sleeping for %.2f seconds. Remaining retries: %i",
                                                response.status, sleep_time, self.max_retries - retries)
                            retries += 1
                            await asyncio.sleep(sleep_time)
                            continue

                        raise DestipyException(str(response))

            except DestipyRunTimeError:
                continue
