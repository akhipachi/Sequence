import socket
import sys
from queue import Queue
from threading import Thread

from play import Message, Play


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset(cls):
        cls._instances = {}


class Communicate(Thread):
    def __init__(self, read, write, id, port, queue):
        Thread.__init__(self)
        self.queue = queue
        self.read = read
        self.write = write
        self.port = port
        self.id = id
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("", port))
        self.s.listen(2)
        print(self.port)

    def run(self):
        c, addr = self.s.accept()
        print(addr)
        # file=open(str(self.port)+'.txt','w')
        try:
            while self.queue.empty():
                if not self.write.empty():
                    if self.write.queue[0].id == self.id:
                        msg = self.write.get().msg + "/"
                        c.send(msg.encode())
                        received = c.recv(1024).decode()
                        msg = received.strip("/")
                        self.read.put(Message(self.id, addr[0], msg))
            # file.close()
        except Exception as e:
            print(e)
            return
        finally:
            self.s.close()


class Connection(metaclass=Singleton):
    def __init__(self, game, dealer, queue):
        self.queue = queue
        self.read = Queue()
        self.write = Queue()
        self.end = False
        self.game = game
        self.dealer = dealer
        self.connect()

    def connect(self):
        sockets = []
        for player in self.game.players:
            # workers.append (Communicate(self.read, self.write, self.game,self.game.players[i].port))
            # workers[i].start()
            conn = Communicate(
                self.read, self.write, player.id, player.port, self.queue
            )
            sockets.append(conn)
            conn.start()
        Play(self.read, self.write, self.game, self.dealer, self.queue)
        Play.reset()
        print("exit")
        sys.exit()
        # requests.get('http://localhost:8000/join/end')


# Connection.get_instance()
