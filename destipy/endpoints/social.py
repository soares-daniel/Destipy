from destipy.utils.http_method import HTTPMethod
from destipy.utils.requester import Requester

class Social:
    """Social endpoints."""
    def __init__(self, requester, logger):
        self.requester: Requester = requester
        self.logger = logger
        self.SOCIAL_URL = "https://www.bungie.net/Platform/Social/"

    async def GetFriendList(self, access_token: str, membership_id: str) -> dict:
        """Returns your Bungie Friend list

        Args:
            access_token (str): The token for authentication
            membership_id (str): The membership id of the user you wish to get the friend list of.

        Returns:
            dict: The friend list
        """
        try:
            self.logger.info("Getting friend list for {}...".format(membership_id))
            url = self.SOCIAL_URL + "Friends/"
            return await self.requester.request(method=HTTPMethod.GET, url=url, access_token=access_token)
        except Exception as ex:
            self.logger.exception(ex)

    async def GetFriendRequestList(self, access_token: str, membership_id: int) -> dict:
        """Returns your friend request queue.

        Args:
            access_token (str): The token to use for authentication
            membership_id (int): The membership id of the user you wish to get the friend request list of.

        Returns:
            dict: The friend request queue
        """
        try:
            self.logger.info("Getting friend request list for {}...".format(membership_id))
            url = self.SOCIAL_URL + "Friends/Requests/"
            return await self.requester.request(method=HTTPMethod.GET, url=url, access_token=access_token)
        except Exception as ex:
            self.logger.exception(ex)

    async def IssueFriendRequest(self, access_token: str, membership_id: str, to_issue_membership_id) -> dict:
        """Requests a friend relationship with the target user.
        Any of the target user's linked membership ids are valid inputs.

        Args:
            access_token (str): The token to use for authentication
            membership_id (str): The membership id of the user itself.
            to_issue_membership_id (str): The membership id of the user you wish to add.

        Returns:
            dict: Whether or not the friend request was issued.
        """
        try:
            self.logger.info("Issuing friend request to {} for {}...".format(to_issue_membership_id, membership_id))
            url = self.SOCIAL_URL + "Friends/Add/{}/".format(membership_id)
            return await self.requester.request(method=HTTPMethod.POST, url=url, access_token=access_token, data={})
        except Exception as ex:
            self.logger.exception(ex)

    async def AcceptFriendRequest(self, access_token: str, membership_id: str, to_accept_membership_id) -> dict:
        """Accepts a friend relationship with the target user.
        The user must be on your incoming friend request list, though no error will occur if they are not.

        Args:
            access_token (str): The token to use for authentication
            membership_id (str): The membership id of the user itself.
            to_accept_membership_id (str): The membership id of the user you wish to accept.

        Returns:
            dict: Whether or not the friend request was accepted.
        """
        try:
            self.logger.info("Accepting friend request from {} for {}...".format(to_accept_membership_id, membership_id))
            url = self.SOCIAL_URL + "Friends/Requests/Accept/{}/".format(membership_id)
            return await self.requester.request(method=HTTPMethod.POST, url=url, access_token=access_token, data={})
        except Exception as ex:
            self.logger.exception(ex)

    async def DeclineFriendRequest(self, access_token: str, membership_id: str, to_decline_membership_id: str) -> dict:
        """Declines a friend relationship with the target user.
        The user must be on your incoming friend request list, though no error will occur if they are not.

        Args:
            access_token (str): The token to use for authentication
            membership_id (str): The membership id of the user itself.
            to_decline_membership_id (str): The membership id of the user you wish to decline.

        Returns:
            dict: Whether or not the friend request was declined.
        """
        try:
            self.logger.info("Decline friend request from {} for {}...".format(to_decline_membership_id, membership_id))
            url = self.SOCIAL_URL + "Friends/Add/{}/".format(membership_id)
            return await self.requester.request(method=HTTPMethod.POST, url=url, access_token=access_token, data={})
        except Exception as ex:
            self.logger.exception(ex)

    async def RemoveFriend(self, access_token: str, membership_id: str, to_remove_membership_id: str) -> dict:
        """Remove a friend relationship with the target user.
        The user must be on your friend list, though no error will occur if they are not.

        Args:
            access_token (str): The token to use for authentication
            membership_id (str): The membership id of the user itself.
            to_remove_membership_id (str): The membership id of the user you wish to remove.

        Returns:
            dict: Whether or not the friend was removed.
        """
        try:
            self.logger.info("Removing friend {} for {}...".format(to_remove_membership_id, membership_id))
            url = self.SOCIAL_URL + "Friends/Remove/{}/".format(membership_id)
            return await self.requester.request(method=HTTPMethod.POST, url=url, access_token=access_token, data={})
        except Exception as ex:
            self.logger.exception(ex)

    async def RemoveFriendRequest(self, access_token: str, membership_id: str, to_remove_membership_id: str) -> dict:
        """Remove a friend relationship with the target user. The user must be on your outgoing request friend list, though no error will occur if they are not.

        Args:
            access_token (str): The token to use for authentication
            membership_id (str): The membership id of the user itself.
            to_remove_membership_id (str): The membership id of the user you wish to remove.
            

        Returns:
            dict: Whether or not the friend request was removed.
        """
        try:
            self.logger.info("Removing friend request from {} for {}...".format(to_remove_membership_id, membership_id))
            url = self.SOCIAL_URL + "Friends/Requests/Remove/{}/".format(membership_id)
            return await self.requester.request(method=HTTPMethod.POST, url=url, access_token=access_token, data={})
        except Exception as ex:
            self.logger.exception(ex)

    async def GetPlatformFriendList(self, friend_platform: int, page: str) -> dict:
        """Gets the platform friend of the requested type, with additional information if they have Bungie accounts. Must have a recent login session with said platform.

        Args:
            friend_platform (int): The platform friend type.
            page (str): The zero based page to return. Page size is 100

        Returns:
            dict: The platform friend list
        """
        try:
            self.logger.info("Getting platform friend list for {}...".format(friend_platform))
            url = self.SOCIAL_URL + "PlatformFriends/{}/{}/".format(friend_platform, page)
            return await self.requester.request(method=HTTPMethod.GET, url=url)
        except Exception as ex:
            self.logger.exception(ex)
