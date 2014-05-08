from gi.repository import GObject
from gi.repository import Vte, GLib
from gi.repository import Gst, GstVideo
from gi.repository import Gtk, Gdk, GdkPixbuf, GdkX11

from common import Video, encode, decode
from common import LOG_FORMAT, HOST, COM_PORT, GST_PORT
from common import ID_BUMPER, ID_ROVER, ID_WLAN, ID_RANGE

import socket
import threading
import logging
logger = logging.getLogger()

IMG_ICON = "media/icon.png"
IMG_TERMINAL = "media/icon_terminal.png"
IMG_VIDEO = "media/icon_video.png"
IMG_LOG = "media/icon_log.png"
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
        self.buffer = textview.get_buffer()
        
    def write(self, text):
        """"""
        iter = self.buffer.get_end_iter()
        self.buffer.insert(iter, text)
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
    #(("autovideosink", None), [("sync", False)])]
    (("autovideosink", None), [])]
    
    def __init__(self, xid):
        """"""
        Video.__init__(self)
        self.xid = xid
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

class Communications(GObject.GObject):
    """"""
    reception = GObject.property(type=str, default="")
    
    def __init__(self):
        """"""
        GObject.GObject.__init__(self)
        self.socket = None
        self.thread = None
        
    def new_connection(self, host, port):
        """"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)
            self.socket.connect((host, port))
            self.thread = threading.Thread(target=self.receive)
            self.thread.start()
        except Exception, e:
            logger.error(e)
        else:
            logger.info("Connected with %s:%i" % (host, port))
        
    def send(self, msg):
        """"""
        try:
            self.socket.send(msg)
        except Exception, e:
            logger.error(e)
            self.disconnect()
        else:
            logger.debug(msg)
            
    def receive(self):
        """"""
        msg = True
        while msg and self.socket:
            try:
                msg = self.socket.recv(1024)
                self.set_property("reception", msg)
            except socket.timeout:
                continue
            else:
                logger.debug(msg)

    def disconnect(self):
        """"""
        if self.socket:
            self.socket.close()
            self.socket = None

class ControlPanel(Gtk.Window):
    """"""
    CONTROL_KEYS = ["", "w", "s", "a", "d"]
    
    PIXBUF_ICON = GdkPixbuf.Pixbuf.new_from_file(IMG_ICON)
    
    PIXBUF_TERMINAL = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_TERMINAL, 64, 64)
    PIXBUF_VIDEO = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_VIDEO, 64, 64)
    PIXBUF_LOG = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_LOG, 64, 64)
    
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
    PIXBUF_ROVER,
    PIXBUF_ROVER_FORWARD,
    PIXBUF_ROVER_REVERSE,
    PIXBUF_ROVER_LEFT,
    PIXBUF_ROVER_RIGHT]    

    def __init__(self):
        """"""        
        Gtk.Window.__init__(self, title=self.__class__.__name__)
        self.set_icon(self.PIXBUF_ICON)
        self.connect("delete-event", self.on_close)
        
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
        
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        hbox.pack_start(notebook, True, True, 5)

        vte = Vte.Terminal()
        vte.set_scrollback_lines(-1)
        vte.connect("child-exited", self.on_close)
        vte.fork_command_full(Vte.PtyFlags.DEFAULT, None, ["/bin/bash"], 
        None, GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None)
        notebook.append_page(vte, Gtk.Image.new_from_pixbuf(self.PIXBUF_TERMINAL))

        drawing_area = Gtk.DrawingArea()
        notebook.append_page(drawing_area, Gtk.Image.new_from_pixbuf(self.PIXBUF_VIDEO))
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(-1, 150)
        notebook.append_page(scroll, Gtk.Image.new_from_pixbuf(self.PIXBUF_LOG))
        
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(2)
        scroll.add(textview)

        log_stream = LogStream(textview)
        logging.basicConfig(format=LOG_FORMAT, stream=log_stream, level="DEBUG")

        vbox = Gtk.VBox()
        hbox.pack_start(vbox, False, False, 5)

        self.rover_img = Gtk.Image.new_from_pixbuf(self.PIXBUF_ROVER)
        self.bumper_img = Gtk.Image.new_from_pixbuf(self.PIXBUF_BUMPER)
        vbox.pack_start(self.bumper_img, False, False, 5)
        
        button = Gtk.ToggleButton()
        button.set_image(self.rover_img)
        button.connect("focus-out-event", self.on_control)
        button.connect("key-press-event", self.on_control)
        button.connect("key-release-event", self.on_control)
        vbox.pack_start(button, False, False, 5)

        self.telemetry_store = Gtk.ListStore(str, str, str)
        self.telemetry_store.append(["wlan0", "", "%"])
        self.telemetry_store.append(["Range", "", "cm"])
        
        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 5)
        
        tree = Gtk.TreeView(self.telemetry_store)
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

        self.maximize()
        self.show_all()
        
        notebook.set_current_page(1)
        self.video = VideoSink(drawing_area.get_property("window").get_xid())
        notebook.set_current_page(0)
        
        self.coms = Communications()
        self.coms.connect("notify::reception", self.on_reception)
        
    def on_connect(self, widget, gparam):
        """"""
        if widget.get_active():
            host = self.host_ip.get_text()
            self.video.new_connection(host, int(self.gst_port.get_value()))
            self.coms.new_connection(host, int(self.com_port.get_value()))
        else:
            self.video.pause()
            self.coms.disconnect()
            
    def on_reception(self, obj, params):
        """"""
        for msg in decode(obj.get_property(params.name)):
            id = msg[0]
            if id == ID_BUMPER:
                if msg[1] == "0":
                    self.bumper_img.set_from_pixbuf(self.PIXBUF_BUMPER_BOTH)
                elif msg[1] == "1":
                    self.bumper_img.set_from_pixbuf(self.PIXBUF_BUMPER_RIGHT)
                elif msg[1] == "2":
                    self.bumper_img.set_from_pixbuf(self.PIXBUF_BUMPER_LEFT)
                elif msg[1] == "3":
                    self.bumper_img.set_from_pixbuf(self.PIXBUF_BUMPER)
            elif id == ID_ROVER:
                if msg[1] == "0":
                    self.rover_img.set_from_pixbuf(self.PIXBUF_ROVER)
                elif msg[1] == "1":
                    self.rover_img.set_from_pixbuf(self.PIXBUF_ROVER_FORWARD)
                elif msg[1] == "2":
                    self.rover_img.set_from_pixbuf(self.PIXBUF_ROVER_REVERSE)
                elif msg[1] == "3":
                    self.rover_img.set_from_pixbuf(self.PIXBUF_ROVER_LEFT)
                elif msg[1] == "4":
                    self.rover_img.set_from_pixbuf(self.PIXBUF_ROVER_RIGHT)
            elif id == ID_WLAN:
                iter = self.telemetry_store.get_iter_first()
                self.telemetry_store.set_value(iter, 1, msg[1])
            else:
                logger.info(msg)
        
    def on_control(self, widget, event):
        """"""
        if widget.get_active():
            if event.type == Gdk.EventType.FOCUS_CHANGE:
                widget.set_active(False)
            elif event.type == Gdk.EventType.KEY_PRESS:
                key = event.string
                if key in self.CONTROL_KEYS:
                    i = self.CONTROL_KEYS.index(key)
                    self.coms.send(encode(ID_ROVER, i))
                    self.rover_img.set_from_pixbuf(self.PIXBUFS[i])
            elif event.type == Gdk.EventType.KEY_RELEASE:
                key = event.string
                if key in self.CONTROL_KEYS:
                    self.rover_img.set_from_pixbuf(self.PIXBUFS[0])

    def on_close(self, widget, event=None):
        """"""
        self.video.quit()
        self.coms.disconnect()
        Gtk.main_quit()

if __name__ == "__main__":
    GObject.threads_init()
    c = ControlPanel()
    logger.info("System ready")
    Gtk.main()
    