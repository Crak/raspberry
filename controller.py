from common import Video, encode, decode
from common import LOG_FORMAT, HOST, COM_PORT, GST_PORT
from common import ID_BUMPER, ID_ROVER, ID_TELEMETRY

import RPIO
import subprocess
import threading
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
        self.raspivid = subprocess.Popen(RASPIVID, stdout=subprocess.PIPE)
        src = self.pipeline.get_by_name("local")
        src.set_property("fd", self.raspivid.stdout.fileno())
        self.play()
        
    def quit(self):
        """"""
        Video.quit(self)
        self.raspivid.terminate()

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
        
        RPIO.add_interrupt_callback(self.SW1_PIN, self.on_collision)
        RPIO.add_interrupt_callback(self.SW2_PIN, self.on_collision)

    def set_led1(self, state):
        RPIO.output(self.LED1_PIN, state)

    def set_led2(self, state):
        RPIO.output(self.LED2_PIN, state)

    def set_oc1(self, state):
        RPIO.output(self.OC1_PIN, state)

    def set_oc2(self, state):
        RPIO.output(self.OC2_PIN, state)

    def set_motors(self, left_go, left_dir, right_go, right_dir):
        RPIO.output(self.LEFT_GO_PIN, left_go)
        RPIO.output(self.LEFT_DIR_PIN, left_dir)
        RPIO.output(self.RIGHT_GO_PIN, right_go)
        RPIO.output(self.RIGHT_DIR_PIN, right_dir)

    def move(self, left_dir, right_dir):
        """"""
        #return
        self.set_motors(1, left_dir, 1, right_dir)
        time.sleep(0.03)
        self.set_motors(0, 0, 0, 0)        

    def send(self, msg):
        """"""
        for key, value in RPIO._rpio._tcp_client_sockets.items():
            value[0].send(msg)

    def on_collision(self, gpio_id, value):
        """"""
        result = value 
        if gpio_id == self.SW1_PIN and RPIO.input(self.SW2_PIN):
               result +=2
        elif gpio_id == self.SW2_PIN:
            result *= 2
            if RPIO.input(self.SW1_PIN):
               result +=1
        self.send(encode(ID_BUMPER, result))

class Controller(RaspiRobot2):
    """"""
    def __init__(self):
        """"""
        RaspiRobot2.__init__(self)
        
        self.exit = False
        self.video = VideoSrc()
        RPIO.add_tcp_callback(COM_PORT, self.process)
        self.start_timer()
 
    def start_timer(self):
        """"""
        if not self.exit:
            data = ["OK", self.wlan_status()]
            self.send(encode(ID_TELEMETRY, data))
            threading.Timer(1, self.start_timer).start()
            
    def wlan_status(self):
        """"""
        link = ""
        f = open("/proc/net/wireless", "r")
        for line in f.readlines():
            line = line.strip()
            if line.startswith("wlan0"):
                link = line.split(".")[0].split(" ")[-1]
        f.close()
        return link

    def process(self, socket, msg):
        """"""
        id, value = decode(msg)
        if id == ID_ROVER:
            if value == "1":
                self.move(0, 0)
            elif value == "2":
                self.move(1, 1)
            elif value == "3":
                self.move(0, 1)
            elif value == "4":
                self.move(1, 0)
        else:
            logger.info(id, value)
        
    def quit(self):
        """"""
        self.exit = True
        self.video.quit()

if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level="DEBUG")
    c = Controller()
    try:
        RPIO.wait_for_interrupts()
    except:
        logger.exception("Exception")
        c.quit()
