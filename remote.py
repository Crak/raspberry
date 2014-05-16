from gi.repository import GObject
from gi.repository import Vte, GLib
from gi.repository import Gst, GstVideo
from gi.repository import Gtk, Gdk, GdkPixbuf, GdkX11

import common

from common import Video, encode, decode
from common import LOG_FORMAT, HOST, COM_PORT, GST_PORT

import socket
import threading
import logging
logger = logging.getLogger()

IMG_ICON = "media/icon.png"
IMG_TERMINAL = "media/icon_terminal.png"
IMG_VIDEO = "media/icon_video.png"
IMG_MAP = "media/icon_map.png"
IMG_LOG = "media/icon_log.png"
IMG_LIGHTS = "media/lights.png"
IMG_MOVE = "media/move.png"
IMG_WLAN = "media/wlan.png"
IMG_WLAN_25 = "media/wlan_25.png"
IMG_WLAN_50 = "media/wlan_50.png"
IMG_WLAN_75 = "media/wlan_75.png"
IMG_WLAN_100 = "media/wlan_100.png"
IMG_MAP_START = "media/map_start.png"
IMG_MAP_UP = "media/map_up.png"
IMG_MAP_DOWN = "media/map_down.png"
IMG_MAP_LEFT = "media/map_left.png"
IMG_MAP_RIGHT = "media/map_right.png"
IMG_BUMPER = "media/bumper.png"
IMG_BUMPER_LEFT = "media/bumper_left.png"
IMG_BUMPER_RIGHT = "media/bumper_right.png"
IMG_BUMPER_BOTH = "media/bumper_both.png"
IMG_BUMPER_BACK = "media/bumper_back.png"
IMG_BUMPER_BACK_ON = "media/bumper_back_on.png"
IMG_ROVER = "media/rover.png"
IMG_ROVER_FORWARD = "media/rover_forward.png"
IMG_ROVER_REVERSE = "media/rover_reverse.png"
IMG_ROVER_LEFT = "media/rover_left.png"
IMG_ROVER_RIGHT = "media/rover_right.png"

PIXBUF_ICON = GdkPixbuf.Pixbuf.new_from_file(IMG_ICON)

PIXBUF_TERMINAL = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_TERMINAL, 64, 64)
PIXBUF_VIDEO = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_VIDEO, 64, 64)
PIXBUF_MAP = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP, 64, 64)
PIXBUF_LOG = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_LOG, 64, 64)

PIXBUF_LIGHTS = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_LIGHTS, 32, 32)

PIXBUF_WLAN = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_WLAN, 32, 32)
PIXBUF_WLAN_25 = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_WLAN_25, 32, 32)
PIXBUF_WLAN_50 = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_WLAN_50, 32, 32)
PIXBUF_WLAN_75 = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_WLAN_75, 32, 32)
PIXBUF_WLAN_100 = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_WLAN_100, 32, 32)

PIXBUF_MAP_START = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP_START, 32, 32)
PIXBUF_MAP_UP = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP_UP, 32, 32)
PIXBUF_MAP_DOWN = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP_DOWN, 32, 32)
PIXBUF_MAP_LEFT = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP_LEFT, 32, 32)
PIXBUF_MAP_RIGHT = GdkPixbuf.Pixbuf.new_from_file_at_size(IMG_MAP_RIGHT, 32, 32)

PIXBUF_MOVE = GdkPixbuf.Pixbuf.new_from_file(IMG_MOVE)

PIXBUF_BUMPER = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER)
PIXBUF_BUMPER_LEFT = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_LEFT)
PIXBUF_BUMPER_RIGHT = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_RIGHT)
PIXBUF_BUMPER_BOTH = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_BOTH)
PIXBUF_BUMPER_BACK = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_BACK)
PIXBUF_BUMPER_BACK_ON = GdkPixbuf.Pixbuf.new_from_file(IMG_BUMPER_BACK_ON)

PIXBUF_ROVER = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER)
PIXBUF_ROVER_FORWARD = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_FORWARD)
PIXBUF_ROVER_REVERSE = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_REVERSE)
PIXBUF_ROVER_LEFT = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_LEFT)
PIXBUF_ROVER_RIGHT = GdkPixbuf.Pixbuf.new_from_file(IMG_ROVER_RIGHT)

WLAN_PIXBUFS = [
PIXBUF_WLAN,
PIXBUF_WLAN_25,
PIXBUF_WLAN_50,
PIXBUF_WLAN_75,
PIXBUF_WLAN_100]

MAP_PIXBUFS = [
PIXBUF_MAP_START,
PIXBUF_MAP_UP,
PIXBUF_MAP_DOWN,
PIXBUF_MAP_LEFT,
PIXBUF_MAP_RIGHT]

BUMPER_PIXBUFS = [
PIXBUF_BUMPER_BOTH,
PIXBUF_BUMPER_RIGHT,
PIXBUF_BUMPER_LEFT,
PIXBUF_BUMPER]

ROVER_PIXBUFS = [
PIXBUF_ROVER,
PIXBUF_ROVER_FORWARD,
PIXBUF_ROVER_REVERSE,
PIXBUF_ROVER_LEFT,
PIXBUF_ROVER_RIGHT]

COLOR_BLACK = Gdk.Color(0, 0, 0)
COLOR_WHITE = Gdk.Color(65535, 65535, 65535)

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
        
    def disconnect(self):
        """"""
        self.pause()
        self.quit()

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
        if self.socket:
            try:
                self.socket.send(msg)
            except Exception, e:
                logger.error(e)
                self.disconnect()
            else:
                #logger.debug(msg)
                pass
            
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
                #logger.debug(decode(msg))
                pass

    def disconnect(self):
        """"""
        if self.socket:
            self.socket.close()
            self.socket = None
            
class Map(Gtk.Table):
    """"""
    def __init__(self, size):
        """"""
        Gtk.Table.__init__(self, size, size, True)
        
        self.size = size
        self.new_map()
        
    def new_map(self):
        """"""
        self.map = []
        self.x = self.size/2
        self.y = self.size/2
        self.add(PIXBUF_MAP_START, 0)
        
    def add(self, pixbuf, direction):
        """"""
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.set_state_flags(Gtk.StateFlags.SELECTED, True)
        self.map.append((image, direction))
        self.attach(image, self.x, self.x+1, self.y, self.y+1)
        image.show()
        
    def get_map(self):
        """"""
        return [direction for image, direction in self.map]
        
    def move(self, pos):
        """"""
        if len(self.map) > pos:
            self.map[pos][0].set_state_flags(Gtk.StateFlags.NORMAL, True)
            self.map[pos-1][0].set_state_flags(Gtk.StateFlags.SELECTED, True)
        
    def on_clear(self, widget):
        """"""
        for image, direction in self.map:
            self.remove(image)
        self.new_map()

    def on_move(self, widget, pixbuf):
        """"""
        if pixbuf == PIXBUF_MAP_UP and self.y > 0:
            self.y -= 1
            self.add(pixbuf, common.MOVE_FORDWARD)
        elif pixbuf == PIXBUF_MAP_DOWN and self.y < self.size-1:
            self.y += 1
            self.add(pixbuf, common.MOVE_REVERSE)
        elif pixbuf == PIXBUF_MAP_LEFT and self.x > 0:
            self.x -= 1
            self.add(pixbuf, common.MOVE_LEFT)
        elif pixbuf == PIXBUF_MAP_RIGHT and self.x < self.size-1:
            self.x += 1
            self.add(pixbuf, common.MOVE_RIGHT)

class ControlPanel(Gtk.Window):
    """"""
    CONTROL_KEYS = {
    "": common.MOVE_STOP,
    "w": common.MOVE_FORDWARD,
    "s": common.MOVE_REVERSE,
    "a": common.MOVE_LEFT,
    "d": common.MOVE_RIGHT}

    def __init__(self):
        """"""        
        Gtk.Window.__init__(self, title=self.__class__.__name__)
        self.set_icon(PIXBUF_ICON)
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
        notebook.append_page(vte, Gtk.Image.new_from_pixbuf(PIXBUF_TERMINAL))
        
        drawing_area = Gtk.DrawingArea()
        drawing_area.modify_bg(Gtk.StateType.NORMAL, COLOR_BLACK)
        notebook.append_page(drawing_area, Gtk.Image.new_from_pixbuf(PIXBUF_VIDEO))
        
        hbox2 = Gtk.HBox()
        notebook.append_page(hbox2, Gtk.Image.new_from_pixbuf(PIXBUF_MAP))
        
        frame = Gtk.Frame()
        hbox2.pack_start(frame, True, True, 0)

        ebox = Gtk.EventBox()
        ebox.modify_bg(Gtk.StateType.NORMAL, COLOR_WHITE)
        frame.add(ebox)
        
        self.map = Map(17)
        ebox.add(self.map)
        
        vbox2 = Gtk.VBox()
        hbox2.pack_start(vbox2, False, False, 5)
        
        self.pad = Gtk.Table(3, 3)
        vbox2.pack_start(self.pad , False, False, 5)
        
        button = Gtk.Button(image=Gtk.Image.new_from_pixbuf(PIXBUF_MAP_UP))
        button.connect("clicked", self.map.on_move, PIXBUF_MAP_UP)
        self.pad .attach(button, 1, 2, 0, 1)
        button = Gtk.Button(image=Gtk.Image.new_from_pixbuf(PIXBUF_MAP_LEFT))
        button.connect("clicked", self.map.on_move, PIXBUF_MAP_LEFT)
        self.pad .attach(button, 0, 1, 1, 2)
        button = Gtk.Button(image=Gtk.Image.new_from_pixbuf(PIXBUF_MAP_START))
        button.connect("clicked", self.map.on_clear)
        self.pad .attach(button, 1, 2, 1, 2)
        button = Gtk.Button(image=Gtk.Image.new_from_pixbuf(PIXBUF_MAP_RIGHT))
        button.connect("clicked", self.map.on_move, PIXBUF_MAP_RIGHT)
        self.pad .attach(button, 2, 3, 1, 2)
        button = Gtk.Button(image=Gtk.Image.new_from_pixbuf(PIXBUF_MAP_DOWN))
        button.connect("clicked", self.map.on_move, PIXBUF_MAP_DOWN)
        self.pad .attach(button, 1, 2, 2, 3)
        
        vbox2.pack_start(Gtk.VSeparator(), True, True, 5)        

        self.play_button = Gtk.ToggleButton()
        self.play_button.set_image(Gtk.Image.new_from_pixbuf(PIXBUF_MOVE))
        self.play_button.connect("clicked", self.on_play)
        vbox2.pack_start(self.play_button, False, False, 5)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(-1, 150)
        notebook.append_page(scroll, Gtk.Image.new_from_pixbuf(PIXBUF_LOG))
        
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(2)
        scroll.add(textview)

        log_stream = LogStream(textview)
        logging.basicConfig(format=LOG_FORMAT, stream=log_stream, level="DEBUG")

        vbox = Gtk.VBox()
        hbox.pack_start(vbox, False, False, 5)
        
        frame = Gtk.Frame()
        vbox.pack_start(frame, False, False, 0)
        
        vbox2 = Gtk.VBox()
        frame.add(vbox2)
        
        self.bumper_img = Gtk.Image.new_from_pixbuf(PIXBUF_BUMPER)
        vbox2.pack_start(self.bumper_img, False, False, 0)
        
        self.rover_img = Gtk.Image.new_from_pixbuf(PIXBUF_ROVER)
        
        self.control = Gtk.ToggleButton()
        self.control.set_image(self.rover_img)
        self.control.set_border_width(15)
        self.control.connect("focus-out-event", self.on_control)
        self.control.connect("key-press-event", self.on_control)
        self.control.connect("key-release-event", self.on_control)
        vbox2.pack_start(self.control, False, False, 0)
        
        self.bumper_back_img = Gtk.Image.new_from_pixbuf(PIXBUF_BUMPER_BACK)
        vbox2.pack_start(self.bumper_back_img, False, False, 0)
        
        hbox  = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 5)

        button = Gtk.ToggleButton()
        button.set_image(Gtk.Image.new_from_pixbuf(PIXBUF_LIGHTS))
        button.connect("clicked", self.on_lights)
        hbox.pack_start(button, True, True, 0)
        
        self.wlan_img = Gtk.Image.new_from_pixbuf(PIXBUF_WLAN)
        hbox.pack_start(self.wlan_img, True, True, 0)

        self.store = Gtk.ListStore(str, str, str)
        self.store.append(["Battery", "", "V"])
        self.store.append(["Range Finder", "", "cm"])

        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 0)
        
        tree = Gtk.TreeView(self.store)
        tree.set_headers_visible(False)
        tree.set_enable_search(False)
        frame.add(tree)        

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("name", renderer, text=0)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        renderer.set_alignment(1, 0)
        column = Gtk.TreeViewColumn("data", renderer, text=1)
        column.set_expand(True)
        tree.append_column(column)
        
        renderer = Gtk.CellRendererText()
        renderer.set_alignment(1, 0)
        column = Gtk.TreeViewColumn("unit", renderer, text=2)
        tree.append_column(column)

        self.maximize()
        self.show_all()
        
        notebook.set_current_page(1)
        self.video = VideoSink(drawing_area.get_property("window").get_xid())
        notebook.set_current_page(0)
        
        self.coms = Communications()
        self.coms.connect("notify::reception", self.on_reception)
        logger.info("System ready")
        
    def on_play(self, widget):
        """"""
        if widget.get_active():
            map = self.map.get_map()
            self.coms.send(encode(common.ID_MAP, map))
            self.control.set_sensitive(False)
            self.pad.set_sensitive(False)
        else:
            self.control.set_sensitive(True)
            self.pad.set_sensitive(True)

    def on_connect(self, widget, gparam):
        """"""
        if widget.get_active():
            host = self.host_ip.get_text()
            self.video.new_connection(host, int(self.gst_port.get_value()))
            self.coms.new_connection(host, int(self.com_port.get_value()))
        else:
            self.video.disconnect()
            self.coms.disconnect()
            self.wlan_img.set_from_pixbuf(WLAN_PIXBUFS[0])
            
    def on_reception(self, obj, params):
        """"""
        id, value = decode(obj.get_property(params.name))
        if id == common.ID_BUMPER:
            self.bumper_img.set_from_pixbuf(BUMPER_PIXBUFS[value])
        elif id == common.ID_ROVER:
            self.rover_img.set_from_pixbuf(ROVER_PIXBUFS[value])
        elif id == common.ID_MAP:
            if value == common.MOVE_END:
                self.play_button.set_active(False)
            else:
                self.map.move(value)
        elif id == common.ID_WLAN:
            self.wlan_img.set_from_pixbuf(WLAN_PIXBUFS[(int(value)/26)+1])
        elif id == common.ID_TELEMETRY:
            iter = self.store.get_iter_first()
            for i in value:
                self.store.set_value(iter, 1, i)
                iter = self.store.iter_next(iter)
        else:
            logger.warning(id, value)
        
    def on_control(self, widget, event):
        """"""
        if widget.get_active():
            if event.type == Gdk.EventType.FOCUS_CHANGE:
                widget.set_active(False)
            elif event.type == Gdk.EventType.KEY_PRESS:
                key = event.string
                if key in self.CONTROL_KEYS.keys():
                    i = self.CONTROL_KEYS[key]
                    self.coms.send(encode(common.ID_ROVER, i))
                    self.rover_img.set_from_pixbuf(ROVER_PIXBUFS[i])
            elif event.type == Gdk.EventType.KEY_RELEASE:
                key = event.string
                if key in self.CONTROL_KEYS.keys():
                    self.rover_img.set_from_pixbuf(ROVER_PIXBUFS[0])
                    
    def on_lights(self, widget):
        """"""
        if widget.get_active():
            self.coms.send(encode(common.ID_LIGHTS, 1))
        else:
            self.coms.send(encode(common.ID_LIGHTS, 0))

    def on_close(self, widget, event=None):
        """"""
        self.video.disconnect()
        self.coms.disconnect()
        Gtk.main_quit()

if __name__ == "__main__":
    GObject.threads_init()
    c = ControlPanel()
    Gtk.main()
    