class DeckEmpty(Exception):
    def __str__(self):
        return "Deck is Empty"


class GameStarted(Exception):
    def __str__(self):
        return "Game already started"


class InvalidPlayer(Exception):
    def __str__(self):
        return "Player not joined"


class NotEnoughPlayer(Exception):
    def __str__(self):
        return "Players not enough"


class GameNotStarted(Exception):
    def __str__(self):
        return "Game not yet started"
