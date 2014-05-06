from gi.repository import GObject
from gi.repository import Gst, GstVideo
from gi.repository import Gtk, GdkPixbuf, GdkX11

from common import Video, LOG_FORMAT, HOST, COM_PORT, GST_PORT

import socket
import logging
logger = logging.getLogger()

IMG_BUMPER = "media/bumper.png"
IMG_BUMPER_LEFT = "media/bumper_left.png"
IMG_BUMPER_RIGHT = "media/bumper_right.png"
IMG_BUMPER_BOTH = "media/bumper_both.png"
IMG_ROVER = "media/rover.png"
IMG_ROVER_FORWARD = "media/rover_forward.png"
IMG_ROVER_REVERSE = "media/rover_reverse.png"
IMG_ROVER_LEFT = "media/rover_left.png"
IMG_ROVER_RIGHT = "media/rover_right.png"

class LogStream(object):
    """"""
    def __init__(self, textview):
        """"""
        self.view = textview
        
    def write(self, text):
        """"""
        buffer = self.view.get_buffer()
        iter = buffer.get_end_iter()
        buffer.insert(iter, text)
        self.view.scroll_to_iter(iter, 0, False, 0, 0)
        
    def flush(self):
        """"""
        pass
        
class VideoSink(Video):
    """"""
    ELEMENTS = [
    (("tcpclientsrc", "remote"), []),
    (("gdpdepay", None), []),
    (("rtph264depay", None), []),
    (("avdec_h264", None), []),
    (("videoconvert", None), []),
    (("autovideosink", None), [("sync", False)])]
    
    def __init__(self):
        """"""
        Video.__init__(self)
        bus = self.pipeline.get_bus()
        bus.enable_sync_message_emission()
        bus.connect("sync-message::element", self.on_gst_sync)
    
    def new_connection(self, host, port):
        """"""
        self.pipeline.set_state(Gst.State.READY)
        src = self.pipeline.get_by_name("remote")
        src.set_property("host", host)
        src.set_property("port", port)
        self.play()

    def on_gst_sync(self, bus, msg):
        """"""
        if msg.get_structure().get_name() == "prepare-window-handle":
            msg.src.set_property("force-aspect-ratio", True)
            msg.src.set_window_handle(self.xid)
            logger.debug("prepare-window-handle")

class Communications(object):
    """"""
    def __init__(self):
        """"""
        self.socket = None
        
    def new_connection(self, host, port):
        """"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except Exception, e:
            logger.error(e)
        else:
            logger.info("Connected with %s:%i" % (host, port))
            return True
        
    def send(self, char):
        """"""
        try:
            self.socket.send(char)
        except:
            logger.warning("Connection Closed")
        else:
            logger.debug(char)

    def disconnect(self):
        """"""
        if self.socket:
            self.socket.close()
            self.socket = None

class ControlPanel(Gtk.Window, VideoSink, Communications):
    """"""
    CONTROL_KEYS = ["a", "w", "s", "d"]
    
    PIXBUF_BUMPER = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER)
    PIXBUF_BUMPER_LEFT = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_LEFT)
    PIXBUF_BUMPER_RIGHT = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_RIGHT)
    PIXBUF_BUMPER_BOTH = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_BOTH)
    PIXBUF_ROVER = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER)
    PIXBUF_ROVER_FORWARD = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_FORWARD)
    PIXBUF_ROVER_REVERSE = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_REVERSE)
    PIXBUF_ROVER_LEFT = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_LEFT)
    PIXBUF_ROVER_RIGHT = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_RIGHT)
    
    PIXBUFS = [
    PIXBUF_ROVER_LEFT,
    PIXBUF_ROVER_FORWARD,
    PIXBUF_ROVER_REVERSE,
    PIXBUF_ROVER_RIGHT]

    def __init__(self):
        """"""
        VideoSink.__init__(self)
        Communications.__init__(self)
        
        Gtk.Window.__init__(self, title=self.__class__.__name__)
        self.connect("delete-event", self.on_close)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)
        
        vbox = Gtk.VBox()
        self.add(vbox)
        
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 5)
        
        switch = Gtk.Switch()
        switch.connect("notify::active", self.on_connect)
        hbox.pack_start(switch, False, True, 5)
        
        label = Gtk.Label("Rover IP:")
        hbox.pack_start(label, False, False, 5)
        
        self.host_ip = Gtk.Entry()
        self.host_ip.set_text(HOST)
        self.host_ip.set_max_length(15)
        hbox.pack_start(self.host_ip, False, False, 5)
        
        label = Gtk.Label("Video Port:")
        hbox.pack_start(label, False, False, 5)
        
        self.gst_port = Gtk.SpinButton.new_with_range(0, 10000, 1)
        self.gst_port.set_value(GST_PORT)
        hbox.pack_start(self.gst_port, False, False, 5)
        
        label = Gtk.Label("Control Port:")
        hbox.pack_start(label, False, False, 5)
        
        self.com_port = Gtk.SpinButton.new_with_range(0, 10000, 1)
        self.com_port.set_value(COM_PORT)
        hbox.pack_start(self.com_port, False, False, 5)
                
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, True, True, 5)
        
        frame = Gtk.Frame()
        hbox.pack_start(frame, True, True, 5)

        drawing_area = Gtk.DrawingArea()
        frame.add(drawing_area)
        
        vbox2 = Gtk.VBox()
        hbox.pack_start(vbox2, False, False, 5)

        self.bumper = Gtk.Image.new_from_pixbuf(self.PIXBUF_BUMPER)
        vbox2.pack_start(self.bumper, False, False, 5)
        
        self.rover = Gtk.Image.new_from_pixbuf(self.PIXBUF_ROVER)
        vbox2.pack_start(self.rover, False, False, 5)

        self.store = Gtk.ListStore(str, str, str)
        self.store.append(["Range", str(10.7), "cm"])
        
        frame = Gtk.Frame()
        vbox2.pack_start(frame, True, True, 5)
        
        tree = Gtk.TreeView(self.store)
        tree.set_headers_visible(False)
        tree.set_enable_search(False)
        frame.add(tree)        

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("name", renderer, text=0)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("data", renderer, text=1)
        renderer.set_alignment(1, 0)
        column.set_expand(True)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("units", renderer, text=2)
        tree.append_column(column)
        
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 5)
        
        frame = Gtk.Frame()
        hbox.pack_start(frame, True, True, 5)

        scroll = Gtk.ScrolledWindow()
        frame.add(scroll)
        
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(2)
        scroll.add(textview)

        log_stream = LogStream(textview)
        logging.basicConfig(format=LOG_FORMAT, stream=log_stream, level="DEBUG")
        
        self.show_all()
        
        self.xid = drawing_area.get_property("window").get_xid()
        
    def on_connect(self, widget, gparam):
        """"""
        if widget.get_active():
            host = self.host_ip.get_text()
            gst_port = int(self.gst_port.get_value())
            com_port = int(self.com_port.get_value())
            VideoSink.new_connection(self, host, gst_port)
            Communications.new_connection(self, host, com_port)
        else:
            VideoSink.pause(self)
            Communications.disconnect(self)
        
    def on_key_press(self, widget, event):
        """"""
        key = event.string
        if key in self.CONTROL_KEYS:
            Communications.send(self, key)
            i = self.CONTROL_KEYS.index(key)
            self.rover.set_from_pixbuf(self.PIXBUFS[i])

    def on_key_release(self, widget, event):
        """"""
        key = event.string
        if key in self.CONTROL_KEYS:
            self.rover.set_from_pixbuf(self.PIXBUF_ROVER)

    def on_close(self, widget, event=None):
        """"""
        VideoSink.quit(self)
        Communications.disconnect(self)
        Gtk.main_quit()

if __name__ == "__main__":
    GObject.threads_init()
    c = ControlPanel()
    logger.info("System ready")
    Gtk.main()
