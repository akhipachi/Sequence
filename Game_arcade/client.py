from threading import Thread
from queue import Queue
import socket
from time import sleep
import re
import requests
import json


class Backend():
    host = 'http://localhost'
    __instance = None

    @staticmethod
    def get_instance():
        if Backend.__instance == None:
            Backend.__instance = Backend()
        return Backend.__instance

    def start(self):
        r = requests.get(self.host+':8000/join/start').content
        r = json.loads(r)
        return r['player']['cards']

    def end(self):
        r = requests.get(self.host+':8000/join/end')

    def join(self):
        r = requests.get(self.host+':8000/join').content
        r = json.loads(r)
        self.id = r['id']
        return self.id

    def communication(self):
        self.read = Queue()
        self.write = Queue()
        # self.client=multiprocessing.Process(target=Client,args=(self.read,self.write))
        # self.client.start()
        self.client = Client(self.read, self.write)


class Message:
    def __init__(self, id, ip, msg):
        self.id = id
        self.ip = ip
        self.msg = msg


class Client():
    host = 'localhost'

    def __init__(self, read, write):
        # Thread.__init__(self)
        self.read = read
        self.write = write
        self.s = socket.socket()
        self.s.connect((self.host, 8888))
        # self.message()

    def message(self):
        receive = self.s.recv(1024).decode()
        if '/' in receive:
            # receive=re.sub('?.*','',receive)
            receive = receive.strip('/')
            self.read.put(receive)
        msg = self.write.queue
        if len(msg) == 0:
            self.s.send('?'.encode())
        else:
            res = self.write.get()+'/'
            self.s.send(res.encode())
