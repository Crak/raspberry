from gi.repository import Gst

import pickle
import logging
logger = logging.getLogger()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"

HOST = "192.168.1.21"
COM_PORT = 9000
GST_PORT = 5000

ID_BUMPER = 1
ID_ROVER = 2
ID_WLAN = 3
ID_BATTERY = 4
ID_TELEMETRY = 5

def encode(id, value):
    """"""
    return pickle.dumps((id, value))
    
def decode(msg):
    """"""
    return pickle.loads(msg)
    
class Video(object):
    """"""
    ELEMENTS = []
    
    def __init__(self):
        """"""
        Gst.init(None)        
        self.pipeline = Gst.Pipeline()

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::error", self.on_gst_error)
        
        prev = None
        for element, properties in self.ELEMENTS:
            e = Gst.ElementFactory.make(element[0], element[1])
            self.pipeline.add(e)
            for property, value in properties:
                e.set_property(property, value)
            if prev:
                prev.link(e)
            prev = e
            
    def play(self):
        """"""
        self.pipeline.set_state(Gst.State.PLAYING)
        
    def pause(self):
        """"""
        self.pipeline.set_state(Gst.State.PAUSED)

    def on_gst_error(self, bus, msg):
        """"""
        logger.error(msg.parse_error())
        
    def quit(self):
        """"""
        self.pipeline.set_state(Gst.State.NULL)
        
if __name__ == "__main__":
    v = Video()
