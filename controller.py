from common import Video, LOG_FORMAT, HOST, COM_PORT, GST_PORT

import RPIO
import subprocess
import socket
import time
import logging
logger = logging.getLogger()

RASPIVID = ["raspivid", "-t", "0", "-h", "600", "-w", "800", "-fps", "25",
    "-vs", "-vf", "-hf", "-b", "2000000", "-o", "-"]

class VideoSrc(Video):
    """"""
    ELEMENTS = [
    (("fdsrc", "local"), []),
    (("h264parse", None), []),
    (("rtph264pay", None), [("config-interval", 1), ("pt", 96)]),
    (("gdppay", None), []),
    (("tcpserversink", None), [("host", HOST), ("port", GST_PORT)])]
    
    def __init__(self):
        """"""
        Video.__init__(self)
        logger.debug(" ".join(RASPIVID))
        p = subprocess.Popen(RASPIVID, stdout=subprocess.PIPE)
        src = self.pipeline.get_by_name("local")
        src.set_property("fd", p.stdout.fileno())
        self.play()

class RaspiRobot2(object):
    """"""
    LEFT_GO_PIN = 17
    LEFT_DIR_PIN = 4
    RIGHT_GO_PIN = 10
    RIGHT_DIR_PIN = 25   
    SW1_PIN = 11
    SW2_PIN = 9
    LED1_PIN = 7
    LED2_PIN = 8
    OC1_PIN = 22
    OC2_PIN = 27
    TRIGGER_PIN = 18
    ECHO_PIN = 23

    def __init__(self):
        """"""
        RPIO.setmode(RPIO.BCM)
        RPIO.setwarnings(False)

        RPIO.setup(self.LEFT_GO_PIN, RPIO.OUT)
        RPIO.setup(self.LEFT_DIR_PIN, RPIO.OUT)
        
        RPIO.setup(self.RIGHT_GO_PIN, RPIO.OUT)
        RPIO.setup(self.RIGHT_DIR_PIN, RPIO.OUT)

        RPIO.setup(self.LED1_PIN, RPIO.OUT)
        RPIO.setup(self.LED2_PIN, RPIO.OUT)

        RPIO.setup(self.OC1_PIN, RPIO.OUT)
        RPIO.setup(self.OC2_PIN, RPIO.OUT)

        RPIO.setup(self.SW1_PIN, RPIO.IN)
        RPIO.setup(self.SW2_PIN, RPIO.IN)
        
        RPIO.setup(self.TRIGGER_PIN, RPIO.OUT)
        RPIO.setup(self.ECHO_PIN, RPIO.IN)

    def set_motors(self, left_go, left_dir, right_go, right_dir):
        RPIO.output(self.LEFT_GO_PIN, left_go)
        RPIO.output(self.LEFT_DIR_PIN, left_dir)
        RPIO.output(self.RIGHT_GO_PIN, right_go)
        RPIO.output(self.RIGHT_DIR_PIN, right_dir)

    def set_led1(self, state):
        RPIO.output(self.LED1_PIN, state)

    def set_led2(self, state):
        RPIO.output(self.LED2_PIN, state)

    def set_oc1(self, state):
        RPIO.output(self.OC1_PIN, state)

    def set_oc2(self, state):
        RPIO.output(self.OC2_PIN, state)    

    def _send_trigger_pulse(self):
        RPIO.output(self.TRIGGER_PIN, True)
        time.sleep(0.0001)
        RPIO.output(self.TRIGGER_PIN, False)

    def _wait_for_echo(self, value, timeout):
        count = timeout
        while RPIO.input(self.ECHO_PIN) != value and count > 0:
            count = count - 1

    def get_distance(self):
        self._send_trigger_pulse()
        self._wait_for_echo(True, 10000)
        start = time.time()
        self._wait_for_echo(False, 10000)
        finish = time.time()
        pulse_len = finish - start
        distance_cm = pulse_len / 0.000058
        return distance_cm

class Controller(RaspiRobot2):
    """"""
    def __init__(self):
        """"""
        #v = VideoSrc()
        RaspiRobot2.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, COM_PORT))
        self.socket.listen(0)
        
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
            self.move(1, 1)
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
        self.set_motors(1, left_dir, 1, right_dir)
        time.sleep(0.03)
        self.set_motors(0, 0, 0, 0)

if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level="DEBUG")
    c = Controller()
    while True:
        c.connection()
