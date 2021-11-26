import asyncio
import aiohttp
from .. import exceptions

async def do_request(method, url, params=None, key=None, token=None, loop=None, session=None):
	if not loop:
		loop = asyncio.get_event_loop()

	params = params or {}

	#close_session = False
	#if not session:
	#	session = aiohttp.ClientSession(loop=loop)
	#	close_session = True

	if key and token:
		params["key"] = key
		params["token"] = token

	for k, v in params.items():
		if isinstance(v, bool):
			params[k] = "true" if v else "false"

	try:
		async with aiohttp.ClientSession() as session:
			async with session.request(method, url, params=params) as response:
				if response.status == 400:
					raise exceptions.TrelloBadRequest(response)
				elif response.status == 401:
					raise exceptions.TrelloUnauthorized(response)
				elif response.status == 404:
					raise exceptions.TrelloNotFound(response)
				elif response.status != 200:
					raise exceptions.TrelloHttpError(response)

				json = await response.json()

		#if close_session:
		#	await session.close()

			return json

	except asyncio.TimeoutError:
		return None
