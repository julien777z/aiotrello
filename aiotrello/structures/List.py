from . import Board
from .Card import Card
from ..misc.constants import API_URL
from ..utils.request import do_request


class List:
	def __init__(self, data, cards=None, board=None):
		if not cards:
			cards = data.get("cards")

		self.parent = board
		self.board = board

		self.name = data.get("name")
		self.idBoard = data.get("idBoard")
		self.pos = data.get("pos")
		self.subscribed = data.get("subscribed")
		self.id = data["id"]

		self.cards = []

		self.synced = False
		self.trello_instance = getattr(board, "trello_instance", None)

		self._add_cards(cards)

		self.last_card_limit = None

	@staticmethod
	def resolve_id(list):
		if isinstance(list, List):
			return list.id
		elif isinstance(List, str):
			return list
		else:
			# TODO: raise TrelloRuntimeError? ..or TrelloUsageError
			pass
	"""
	@staticmethod
	async def parse_from(list):
		if isinstance(list, List):
			return list
		else:
			list_json = await do_request(
				"GET",
				f"{API_URL}/lists/{self.id}/cards",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
			)
	"""


	def _add_cards(self, cards):
		if cards:
			for _card in cards:
				card = Card(_card, self)
				self.cards.append(card)

	async def sync(self, data=None, card_limit=None, cards=None, **kwargs):
		self.synced = False

		if not data:
			data = await do_request(
				"GET",
				f"{API_URL}/lists/{self.id}",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
			)

		self.name = data.get("name")
		self.idBoard = data.get("idBoard")
		self.pos = data.get("pos")
		self.subscribed = data.get("subscribed")
		self.id = data["id"]
		self.cards.clear()

		card_data = None

		if card_limit:
			kwargs["limit"] = card_limit

		if cards:
			card_data = cards
		else:
			card_data = await do_request(
				"GET",
				f"{API_URL}/lists/{self.id}/cards",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
				params=kwargs
			)

		self._add_cards(card_data)
		self.synced = True
		self.last_card_limit = card_limit

	async def get_cards(self, limit=None, **kwargs):
		if not self.synced:
			await self.sync(card_limit=limit, **kwargs)

		return list(self.cards)

	async def get_card(self, predicate):
		if not self.synced:
			await self.sync(card_limit=self.last_card_limit)

		for card in self.cards:
			if predicate(card):
				return card

	async def archive(self):
		if not self.synced:
			await self.sync(card_limit=self.last_card_limit)

		await do_request(
			"PUT",
			f"{API_URL}/lists/{self.id}/closed",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params={"value": True}
		)

		self.parent.lists.remove(self)

	async def restore(self):
		if not self.synced:
			await self.sync(card_limit=self.last_card_limit)

		params = {"value": False}
		await do_request(
			"PUT",
			f"{API_URL}/lists/{self.id}/closed",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params=params
		)

		if self not in self.parent.boards:
			self.parent.board.append(self)

	async def edit(self, **kwargs):
		await do_request(
			"PUT",
			f"{API_URL}/lists/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params=kwargs
		)

		await self.sync(card_limit=self.last_card_limit)

	async def create_card(self, name=None, desc=None, **kwargs):
		kwargs["idList"] = self.id

		if name:
			kwargs["name"] = name
		if desc:
			kwargs["desc"] = desc

		card_json = await do_request(
			"POST",
			f"{API_URL}/cards/",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			session=self.trello_instance.session,
			params=kwargs
		)

		card = Card(card_json, self)

		self.cards.append(card)

		return card

	new_card = add_card = create_card
	delete = archive

	@staticmethod
	async def from_board(board, key=None, token=None):
		board_id = Board.resolve_id(board)
		# TODO: finish this


	def __str__(self):
		return f"List: {self.name} ({self.id})"

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return hasattr(other, "id") and self.id == other.id
