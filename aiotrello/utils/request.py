import asyncio
import aiohttp
from .. import exceptions

async def do_request(method, url, params=None, key=None, token=None, loop=None, session=None):
	if not loop:
		loop = asyncio.get_event_loop()

	close_session = False
	if not session:
		session = aiohttp.ClientSession(loop=loop)
		close_session = True

	if key and token:
		url = f"{url}?key={key}&token={token}"

		if params:
			params = [f"&{x}={'true' if y is True else 'false' if y is False else y}" for x, y in params.items()]
			url = url + "".join(params)

	async with session.request(method, url) as response:
		if response.status == 400:
			raise exceptions.TrelloBadRequest(response)
		elif response.status == 401:
			raise exceptions.TrelloUnauthorized(response)
		elif response.status == 404:
			raise exceptions.TrelloNotFound(response)
		elif response.status != 200:
			raise exceptions.TrelloHttpError(response)

		json = await response.json()

		if close_session:
			await session.close()

		return json
