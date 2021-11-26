from . import Board, List
from ..misc.constants import API_URL
from ..utils.request import do_request

class Card:
	def __init__(self, data, list=None, trello_instance=None):
		self.parent = list
		self.list = list

		self.id = data["id"]
		self.name = data["name"]
		self.closed = data["closed"]
		self.date_last_activity = data.get("dateLastActivity")
		self.desc = self.description = data["desc"]
		self.desc_data = data["descData"]
		self.id_board = data["idBoard"]
		self.id_list = data["idList"]
		self.id_short = data["idShort"]
		self.url = data["url"]
		self.subscribed = data["subscribed"]
		self.short_url = data["shortUrl"]
		self.pos = self.position = data["pos"]
		self._labels = data["labels"]

		self.labels = [] # TODO
		self.comments = [] # TODO

		self.synced = False
		self.trello_instance = trello_instance or getattr(list, "trello_instance", None)

	async def sync(self, data=None):
		self.synced = False
		self.labels.clear()
		self.comments.clear()

		if not data:
			data = await do_request(
				"GET",
				f"{API_URL}/cards/{self.id}",
				key=self.trello_instance.key,
				token=self.trello_instance.token,
				loop=self.trello_instance.loop,
				#session=self.trello_instance.session,
			)

		self.id = data["id"]
		self.name = data["name"]
		self.closed = data["closed"]
		self.date_last_activity = data.get("dateLastActivity")
		self.desc = self.description = data["desc"]
		self.desc_data = data["descData"]
		self.id_board = data["idBoard"]
		self.id_list = data["idList"]
		self.id_short = data["idShort"]
		self.url = data["url"]
		self.subscribed = data["subscribed"]
		self.short_url = data["shortUrl"]
		self.pos = self.position = data["pos"]
		self._labels = data["labels"]

		if self.parent:
			if not self.parent.synced:
				await self.parent.sync(card_limit=self.parent.last_card_limit)

			if self.id_board != self.parent.id:
				# card changed lists

				if self in self.parent.cards:
					self.parent.cards.remove(self)

					if hasattr(self.parent, "parent") and self.trello_instance:
						board = await self.trello_instance.get_board(self.id_board)

						if not board:
							await self.trello_instance.sync(card_limit=self.trello_instance._last_card_limit)

							board = self.trello_instance.boards.get(self.id_board)

						if board:
							new_list = await board.get_list(lambda l: l.id == self.id_list)

							if new_list:
								new_list.cards.append(self)
								self.parent = new_list


		self.synced = True

	async def move_to(self, list, board=None):
		list_id = List.List.resolve_id(list) # pylint: disable=E1101

		params = {
			"idList": list_id,
			"idBoard": self.parent.parent.id
		}

		if board:
			params["idBoard"] = Board.resolve_id(board)

		await do_request(
			"PUT",
			f"{API_URL}/cards/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			#session=self.trello_instance.session,
			params=params
		)

		self.list.cards.remove(self)
		list.cards.append(self)

	async def delete(self):
		await do_request(
			"DELETE",
			f"{API_URL}/cards/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			#session=self.trello_instance.session,
		)
		if self in self.parent.cards:
			self.parent.cards.remove(self)

	async def edit(self, **kwargs):
		await do_request(
			"PUT",
			f"{API_URL}/cards/{self.id}",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			#session=self.trello_instance.session,
			params=kwargs
		)

	async def archive(self):
		if self in self.parent.cards:
			self.parent.cards.remove(self)

		await self.edit(closed=True)

	async def restore(self):
		if self not in self.parent.cards:
			self.parent.cards.append(self)

		await self.edit(closed=False)

	async def add_comment(self, text):
		# TODO: return a Comment object
		await do_request(
			"POST",
			f"{API_URL}/cards/{self.id}/actions/comments",
			key=self.trello_instance.key,
			token=self.trello_instance.token,
			loop=self.trello_instance.loop,
			#session=self.trello_instance.session,
			params={"text": text}
		)

	# aliases
	new_comment = create_comment = add_comment

	def __str__(self):
		return f"Card: {self.name} ({self.id})"

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return hasattr(other, "id") and self.id == other.id
