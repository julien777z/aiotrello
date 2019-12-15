import asyncio
import aiohttp
from .misc.constants import API_URL
from .structures.Board import Board
from .utils.request import do_request


class Trello:
	def __init__(
			self,
			*,
			key=None,
			token=None,
			loop=asyncio.get_event_loop(),
			session=None,
			use_cache=True
		):
		"""Initializes a new Trello client.
		Parameters
		----------
		key: str [optional]
			The key used for Trello authentication.
		token: str [optional]
			The token used for Trello authentication.
		loop: asyncio loop [optional] [default=asyncio.get_event_loop()]
			An asyncio event loop used for HTTP requests.
		session: aiohttp.ClientSession [optional]
			aiohttp client session used for HTTP requests.
		use_cache: boolean [optional] [default=True]
			Whether to avoid HTTP requests on short intervals
			whenever possible. False = always make a new HTTP request.
			NOTE: this is currently not implemented.

		Note: if a key and token is not provided, you may only use the static methods as well as a few methods which don't
			  require authentication, such as get_board().
		"""

		self.key = key
		self.token = token
		self.loop = loop
		self.synced = False
		self.boards = []
		self._use_cache = use_cache

		if session:
			self.session = session
		else:
			self.session = aiohttp.ClientSession(loop=loop)

	async def get_board(self, a, card_limit=None):
		if callable(a):
			for board in await self.get_boards(card_limit):
				if a(board):
					return board
		else:
			board = await Board.from_board(a, card_limit=card_limit, trello_instance=self)

			return board


	async def get_boards(self, card_limit=None):
		if not self.synced:
			await self.sync(card_limit=card_limit)

		return list(self.boards)


	async def sync(self, card_limit=None):
		self.boards.clear()

		boards = await do_request(
			"GET",
			f"{API_URL}/members/me/boards",
			key=self.key,
			token=self.token,
			loop=self.loop,
			session=self.session,
			params={"members": "all"}
		)

		for raw_board in boards:
			board = Board(raw_board, self)

			if board not in self.boards:
				await board.sync(card_limit)
				self.boards.append(board)

		if self._use_cache:
			self.synced = True

	async def create_board(self, name, **kwargs):
		kwargs["name"] = name
		board = Board(await do_request(
			"POST",
			f"{API_URL}/boards",
			key=self.key,
			token=self.token,
			loop=self.loop,
			params=kwargs,
			session=self.session
		), self)

		self.boards.append(board)
		return board

	new_board = create_board
