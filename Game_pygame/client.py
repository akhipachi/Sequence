from threading import Thread
from queue import Queue
import socket
from time import sleep
import re

class Message:
    def __init__(self,id,ip,msg):
        self.id=id
        self.ip=ip
        self.msg=msg

class Client(Thread):
    host='localhost'
    def __init__(self,read,write):
        Thread.__init__(self)
        self.read=read
        self.write=write
        self.s=socket.socket()
        self.s.connect((self.host,8888))
        self.message()
    def message(self):
        while(True):
            receive=self.s.recv(1024).decode()
            # print(receive)
            if '/' in receive:
                # receive=re.sub('?.*','',receive)
                receive=receive.strip('/')
                self.read.put(receive)
                print(receive)
            msg=self.write.queue
            if len(msg)==0:
                self.s.send('?'.encode())
                continue
            else:
                res=self.write.get().msg+'/'
                self.s.send(res.encode())
           
            