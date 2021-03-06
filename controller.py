import common

from common import Video, encode, decode
from common import LOG_FORMAT, HOST, COM_PORT, GST_PORT

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

    def motors(self, left_dir, right_dir):
        """"""
        #return
        RPIO.output(self.LEFT_DIR_PIN, left_dir)
        RPIO.output(self.RIGHT_DIR_PIN, right_dir)
        RPIO.output(self.RIGHT_GO_PIN, 1)
        RPIO.output(self.LEFT_GO_PIN, 1)
        time.sleep(0.03)
        RPIO.output(self.RIGHT_GO_PIN, 0)
        RPIO.output(self.LEFT_GO_PIN, 0)

    def send(self, msg):
        """"""
        for key, value in RPIO._rpio._tcp_client_sockets.items():
            value[0].send(msg)
        
    def get_range(self):
        mean = 10
        distance = 0
        for i in range(mean):
            RPIO.setup(self.TRIGGER_PIN, RPIO.OUT)
            RPIO.output(self.TRIGGER_PIN, True)
            time.sleep(0.0001)
            RPIO.output(self.TRIGGER_PIN, False)
            RPIO.setup(self.TRIGGER_PIN, RPIO.IN)
            timeout = 10000
            while RPIO.input(self.TRIGGER_PIN) != True and timeout > 0:
                timeout = timeout - 1
            start = time.time()
            timeout = 10000
            while RPIO.input(self.TRIGGER_PIN) != False and timeout > 0:
                timeout = timeout - 1
            pulse_len = time.time() - start
            distance += pulse_len / 0.000058
        return distance/mean

    def on_collision(self, gpio_id, value):
        """"""
        result = value 
        if gpio_id == self.SW1_PIN and RPIO.input(self.SW2_PIN):
               result +=2
        elif gpio_id == self.SW2_PIN:
            result *= 2
            if RPIO.input(self.SW1_PIN):
               result +=1
        self.send(encode(common.ID_BUMPER, result))

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
            self.send(encode(common.ID_WLAN, self.wlan_status()))
            data = ["11.2", "%.2f" % self.get_range()]
            self.send(encode(common.ID_TELEMETRY, data))
            threading.Timer(1, self.start_timer).start()
 
    def wlan_status(self):
        """"""
        link = ""
        f = open("/proc/net/wireless", "r")
        for line in f.readlines():
            line = line.strip()
            if line.startswith("wlan0"):
                link = line.split(".")[1].strip()
        f.close()
        return link

    def process(self, socket, msg):
        """"""
        id, value = decode(msg)
        if id == common.ID_ROVER:
            self.move(value)
        elif id == common.ID_MAP:
            self.traverse_map(value)
        elif id == common.ID_LIGHTS:
            if value:
                self.set_led1(True)
                self.set_led2(True)
            else:
                self.set_led1(False)
                self.set_led2(False)
        else:
            logger.info(id, value)
            
    def traverse_map(self, map):
        """"""
        pos = 0
        for direction in map:
            self.send(encode(common.ID_ROVER, direction))
            self.move(direction)
            time.sleep(1)
            self.send(encode(common.ID_MAP, pos))
            pos += 1
        self.send(encode(common.ID_MAP, common.MOVE_END))
        self.send(encode(common.ID_ROVER, common.MOVE_STOP))
        
    def move(self, direction):
        """"""
        if direction == common.MOVE_FORDWARD:
            self.motors(0, 0)
        elif direction == common.MOVE_REVERSE:
            self.motors(1, 1)
        elif direction == common.MOVE_LEFT:
            self.motors(0, 1)
        elif direction == common.MOVE_RIGHT:
            self.motors(1, 0)

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
