import json
import socket
from queue import Queue
from threading import Thread

import requests
from exceptions import ErrorResponse


class Backend:
    host = None
    __instance = None
    read = None
    write = None
    client = None

    @staticmethod
    def get_instance():
        if Backend.__instance == None:
            Backend.__instance = Backend()
        return Backend.__instance

    def start(self):
        req = requests.get(self.host + ":8000/join/start").content
        response = json.loads(req)
        if "error" in response:
            raise ErrorResponse(response["error"])
        else:
            return response["player"]["cards"]

    def end(self):
        if self.client is not None:
            self.client.kill = False
        if self.host is not None:
            req = requests.get(self.host + ":8000/join/end", timeout=1)

    def join(self):
        req = requests.get(self.host + ":8000/join", timeout=1).content
        response = json.loads(req)
        if "error" in response:
            raise ErrorResponse(response["error"])
        else:
            self.id = response["id"]
            self.port = response["port"]
            return self.id

    def communication(self):
        self.read = Queue()
        self.write = Queue()
        self.client = Client(self.read, self.write, self.host, self.id, self.port)
        self.client.start()


class Message:
    def __init__(self, id, ip, msg):
        self.id = id
        self.ip = ip
        self.msg = msg


class Client(Thread):
    host = "localhost"

    def __init__(self, read, write, host, id, port):
        Thread.__init__(self)
        self.kill = True
        self.host = host.strip("http://")
        self.read = read
        self.write = write
        self.id = id
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, port))

    def run(self):
        receive = True
        try:
            while self.kill:
                if receive:
                    received = self.s.recv(1024).decode()
                    if "/" in received:
                        # receive=re.sub('?.*','',receive)
                        received = received.strip("/")
                        msg = received.split("+")
                        if msg[1] == str(self.id):
                            self.read.put(msg[0])
                            receive = False
                if not self.write.empty():
                    res = self.write.get() + "/"
                    self.s.send(res.encode())
                    receive = True
                    if "end" in res:
                        break
            exit()
        except Exception as e:
            print(e)
            return
        finally:
            self.s.close()
