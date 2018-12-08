class TrelloException(Exception):
	pass

class TrelloBadRequest(TrelloException):
	pass

class TrelloUnauthorized(TrelloException):
	pass

class TrelloHttpError(TrelloException):
	pass

class TrelloNotFound(TrelloException):
	pass

class TrelloJsonError(TrelloException):
	pass
