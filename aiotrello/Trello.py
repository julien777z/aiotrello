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
            cache_mode="full"
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
        cache_mode: str [optional] [default="all"]
            Specifies how items are internally cached.
                "full" = everything is cached, including all boards
                "some" = boards and other items aren't loaded by default,
                         but certain operations will cache them
                "none" = nothing is cached

        Note: if a key and token is not provided, you may only use the static methods as well as a few methods which don't
              require authentication, such as get_board() with a public board.
        """

        self.key = key
        self.token = token
        self.loop = loop
        self.synced = False
        self.boards = {}
        self._cache_mode = cache_mode
        self._last_card_limit = None

        if session:
            self.session = session
        else:
            self.session = aiohttp.ClientSession(loop=loop)

    async def get_board(self, a, card_limit=None):
        if not self.synced:
            await self.sync(card_limit=card_limit)

        if callable(a):
            for board in await self.get_boards(card_limit):
                if a(board):
                    return board
        else:
            board_id = Board.resolve_id(a)

            board = self.boards.get(board_id)

            if board:
                return board

            for board in self.boards.values():
                if board_id in (board.id, board.short_link):
                    return board

            board = await Board.from_board(a, card_limit=card_limit, trello_instance=self)

            return board


    async def get_boards(self, card_limit=None):
        if not self.synced:
            await self.sync(card_limit=card_limit)

        if self._cache_mode == "full":
            for board in self.boards.values():
                yield board
        else:
            async for board in self._get_boards(card_limit=card_limit):
                yield board

    async def _get_boards(self, card_limit=None):
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
            board = Board(raw_board, trello_instance=self)
            await board.sync(card_limit)

            yield board

    async def sync(self, card_limit=None):
        self._last_card_limit = card_limit

        if self._cache_mode == "full":
            self.boards.clear()

            async for board in self._get_boards(card_limit):
                self.boards[board.id] = board

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
        ), trello_instance=self)

        if self._cache_mode in ("full", "some"):
            self.boards[board.id] = board

        return board

    new_board = create_board
