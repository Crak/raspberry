import socket
import time

from rrb2 import RRB2

HOST = '192.168.2.3'
PORT = 9000

class Controller:
    """"""
    def __init__(self):
        """"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(0)
        
        self.r = RRB2()
        
    def connection(self):
        """"""
        conn, addr = self.socket.accept()
        print  "Connected: %s" % addr[0]
        alive = True 
        while alive:
            alive = self.process(conn.recv(1))
        conn.close() 
        print "Closed: %s" % addr[0]

    def process(self, value):
        """"""
        if value == "w":
            self.move(0, 0)
            print "forward"
        elif value == "s":
            self.move(1, 1,)
            print "reverse"
        elif value == "a":
            self.move(1, 0)
            print "left"
        elif value == "d":
            self.move(0, 1)
            print "right"
        else:
            print value
        return value
    
    def move(self, left_dir, right_dir):
        """"""
        self.r.set_motors(1, left_dir, 1, right_dir)
        time.sleep(0.03)
        self.r.set_motors(0, 0, 0, 0)

if __name__ == "__main__":
    c = Controller()
    while True:
        c.connection()
