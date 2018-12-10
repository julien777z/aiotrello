# aiotrello

Async Trello Python library
## Installation

Install with [pip](https://pypi.org/project/pip/)

```sh
$ pip install aiotrello
```

## Examples

```py
import asyncio; loop = asyncio.get_event_loop()
from aiotrello import Trello

trello = Trello(key="123", token="abc123") # Initialize a new Trello client


async def main():
	# Create 10 boards and make a list for each
	for i in range(10):
		board = await trello.create_board(f"Board {i}")
		await board.create_list("My List")
	
	# Delete all boards that start with "Board"
	for board in await trello.get_boards():
		if board.name.startswith("Board"):
			await board.delete()
	
	# Get a board and list, then make a new card, and finally, add a comment to it
	my_board = await trello.get_board(lambda b: b.id == "123")
	my_list = await my_board.get_list(lambda l: l.name == "My List")
	card = await my_list.create_card("Hello World", "Here is my awesome card")
	await card.add_comment("aiotrello rocks!")

	# Move card (above example) to a different list
	my_other_list = await my_board.get_list(lambda l: l.name == "My Other List")
	await card.move_to(my_other_list)
	# also supports moving to external boards
	board2 = await trello.get_board(lambda b: b.name == "My Other Board")
	list2 = await board2.get_list(lambda l: l.name == "My Other List")
	await card.move_to(list2, board2)

	# Edit a card (above), archive it, and then delete it
	await card.edit(name="This card will be deleted soon..")
	await card.archive()
	await card.delete()


try:
	loop.run_until_complete(main())
finally:
	loop.run_until_complete(trello.session.close()) # Remember to close the session!


```

## Support

Join our [Discord Server](https://discord.gg/hK9DpQQ)

