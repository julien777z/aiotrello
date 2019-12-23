import re
from .List import List
from ..misc.constants import API_URL
from ..utils.request import do_request

compiled_board_regex = re.compile(r"b/(.*)/")

class Board:
	def __init__(self, json, card_limit=None, trello_instance=None):
		self.id = json["id"]
		self.name = json["name"]
		self.short_link = json.get("shortLink")
		self.closed = json.get("closed")
		self.id_organization = json.get("idOrganization")
		self.pinned = json.get("pinned")
		self.url = json.get("url")
		self.short_url = json.get("shortUrl")
		self.prefs = json.get("prefs")
		self.label_names = json.get("labelNames")
		self.starred = json.get("starred", False)
		self.limits = json.get("limits", [])
		self.memberships = json.get("memberships", [])
		self._members = json.get("members")

		self.lists = []
		self.members = []

		self.synced = False

		self.parent = trello_instance
		self.trello_instance = trello_instance

		self.last_card_limit = card_limit


	async def sync(self, card_limit=None, json=None):
		self.synced = False

		if not json:
			json = await do_request(
				"GET",
				f"{API_URL}/boards/{self.id}",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
			)

		self.id = json["id"]
		self.name = json["name"]
		self.closed = json["closed"]
		self.id_organization = json["idOrganization"]
		self.pinned = json["pinned"]
		self.url = json["url"]
		self.short_url = json["shortUrl"]
		self.prefs = json["prefs"]
		self.label_names = json["labelNames"]
		self.starred = json.get("starred", False)
		self.limits = json.get("limits", [])
		self.memberships = json.get("memberships", [])

		self.lists.clear()

		await self.load_lists(card_limit)

		self.synced = True
		self.last_card_limit = card_limit

	async def create_list(self, name, **kwargs):
		if not self.synced:
			await self.sync(self.last_card_limit)

		kwargs["name"] = name
		kwargs["idBoard"] = self.id

		json = await do_request(
			"POST",
			f"{API_URL}/lists/",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params=kwargs
		)

		new_list = List(json, [], self)

		await new_list.sync(new_list.last_card_limit)

		self.lists.append(new_list)

		return new_list

	async def load_lists(self, card_limit=None, **kwargs):
		params = kwargs or {"cards": "open"}
		json = await do_request(
			"GET",
			f"{API_URL}/boards/{self.id}/lists",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params=params
		)

		for trello_list in json:
			new_list = List(trello_list, trello_list.get("cards", [])[0:card_limit], self)

			if new_list not in self.lists:
				self.lists.append(new_list)


	@staticmethod
	def resolve_id(board):
		board_id = None

		if isinstance(board, Board):
			return board.id
		elif isinstance(board, str):
			board_id = compiled_board_regex.search(board, re.IGNORECASE)

			if board_id:
				return board_id.group(1)

			return board

	@staticmethod
	async def from_board(board, key=None, token=None, loop=None, card_limit=None, trello_instance=None):
		board_id = Board.resolve_id(board)

		if trello_instance and (not key or not token):
			key = trello_instance.key
			token = trello_instance.token

		board = Board(await do_request(
			"GET",
			f"{API_URL}/boards/{board_id}",
			key=key,
			token=token,
			loop=loop,
		))

		if trello_instance:
			board.trello_instance = trello_instance
			board.parent = trello_instance

		await board.sync(card_limit=card_limit)

		return board

	async def delete(self):
		if not self.synced:
			await self.sync(self.last_card_limit)

		await do_request(
			"DELETE",
			f"{API_URL}/boards/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
		)

		self.trello_instance.boards.remove(self)

	async def get_lists(self):
		if not self.synced:
			await self.sync(self.last_card_limit)

		return list(self.lists)

	async def get_list(self, predicate):
		if not self.synced:
			await self.sync(self.last_card_limit)

		for list in self.lists:
			if predicate(list):
				return list

	async def get_field(self, field):
		if not self.synced:
			await self.sync(self.last_card_limit)

		if hasattr(self, field):
			return getattr(self, field)
		else:
			field_json = await do_request(
				"GET",
				f"{API_URL}/boards/{field}",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
			)

			if field_json:
				setattr(self, field, field_json.get("_value"))

				return field_json.get("_value")

	async def edit(self, **kwargs):
		await do_request(
			"PUT",
			f"{API_URL}/boards/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			params=kwargs
		)

		await self.sync(self.last_card_limit)

	def __str__(self):
		return f"Board: {self.name} ({self.id})"

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return hasattr(other, "id") and self.id == other.id
