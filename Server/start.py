import random
import exceptions
from sockets import Connection
import multiprocessing


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset(cls):
        cls._instances = {}


class Game(metaclass=Singleton):
    def __init__(self):
        self.players = []
        self.player_ip = {}
        self.started = False
        self.port = 8888

    def join(self, ip):
        if ip in self.player_ip:
            return self.player_ip[ip].id, self.player_ip[ip].port
        player = Player(ip, self.port)
        self.port += 1
        self.players.append(player)
        self.player_ip[ip] = player
        return player.id, player.port

    def start(self, ip):
        if ip not in self.player_ip:
            return 'Invalid player'
        if(self.started):
            return self.player_ip[ip]
        if len(self.players) > 0:
            self.started = True
            player = self.player_ip[ip]
            for p in self.players:
                Dealer().deal(p)
            self.queue = multiprocessing.Queue()
            self.p = multiprocessing.Process(
                target=Connection, args=(Game(), Dealer(), self.queue))
            self.p.start()
            # p.join()
            return player
        else:
            return 'not enough players'

    def end(self):
        self.queue.put('end')
        self.p.terminate()
        self.started = False
        Game.reset()
        Dealer.reset()
        Deck.reset()
        Connection.reset()
        Cards.reset()


class Player:
    def __init__(self, ip, port):
        self.id = len(Game().players)
        self.ip_address = ip
        self.port = port
        self.cards = []


class Dealer(metaclass=Singleton):
    def __init__(self):
        self.deck = Deck()
        self.deck.shufle()
        self.jocker = self.deck.get_jocker()

    def deal(self, player: Player):
        if(len(player.cards) == 0):
            for i in range(13):
                player.cards.append(self.deck.get())

    def hit(self):
        try:
            card = self.deck.get()
        except:
            self.deck.add_deck()
            card = self.deck.get()
        return card


class Cards(metaclass=Singleton):
    def __init__(self):
        self.cards = []
        CARD_VALUES = ["A", "2", "3", "4", "5",
                       "6", "7", "8", "9", "10", "J", "Q", "K"]
        CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
        for card_num in CARD_VALUES:
            for card_suit in CARD_SUITS:
                # str_card = str(card_num) if card_num > 9 else str(card_num)
                self.cards.append(card_num + ' ' + card_suit)


class Deck(metaclass=Singleton):
    def __init__(self):
        self.deck = []
        self.jocker = None
        num_players = len(Game().players)
        # print(num_players)
        for i in range(num_players//2+num_players % 2):
            self.deck += Cards().cards.copy()

    def shufle(self):
        random.shuffle(self.deck)

    def get(self):
        if(len(self.deck) >= 1):
            return self.deck.pop()
        else:
            raise exceptions.DeckEmpty()

    def get_jocker(self):
        if self.jocker is None:
            self.jocker = self.deck.pop(random.randint(0, len(self.deck)-1))
        return self.jocker

    def add_cards(self):
        self.deck += Cards().cards.copy()
        self.shufle()
