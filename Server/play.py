class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset(cls):
        cls._instances = {}


class Message:
    def __init__(self, id, ip, msg):
        self.id = id
        self.ip = ip
        self.msg = msg


class Play(metaclass=Singleton):
    def __init__(self, read, write, game, dealer, queue):
        self.queue = queue
        self.read = read
        self.write = write
        self.game = game
        self.end = False
        self.turn = 0
        self.dealer = dealer
        self.run()

    def message(self, id, msg):
        self.write.put(
            Message(id, self.game.players[id].ip_address, msg + "+" + str(id))
        )

    def run(self):
        next = True
        top = self.dealer.hit()
        self.dealer.open_deck.append(top)
        while self.queue.empty():
            # break
            if next:
                self.message(self.turn, "play:" + top)
                next = False
            receive = self.read.get()
            if receive:
                if "done" in receive.msg:
                    top = receive.msg.split(":")[1]
                    self.turn = self.turn + 1
                    if self.turn == len(self.game.players):
                        self.turn = 0
                    self.dealer.open_deck.pop()
                    self.dealer.open_deck.append(top)
                    self.message(self.turn, "play:" + top)
                if "get" in receive.msg:
                    card = self.dealer.hit()
                    self.dealer.open_deck.append(card)
                    self.message(self.turn, "card:" + card)
                if "jocker" in receive.msg:
                    self.message(receive.id, "jocker:" + self.dealer.jocker)
                if "won" in receive.msg:
                    print("won")
                    for player in self.game.players:
                        if player.id != receive.id:
                            self.message(player.id, "won:" + str(receive.id))
        return
