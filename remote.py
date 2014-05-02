import pygtk
pygtk.require('2.0')
import gtk

import socket

HOST = "192.168.2.3"
PORT = 9000

"""
gst-launch-1.0 -v tcpclientsrc host=192.168.1.21 port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
raspivid -t 0 -h 600 -w 800 -fps 25 -vs -vf -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.21 port=5000
"""

class Remote(gtk.Window):
    """"""
    def __init__(self):
        """"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST,PORT))
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.connect("delete_event", self.quit)
        self.connect("key-press-event", self.key_handler)
        self.show()
        
        gtk.main()
        
    def key_handler(self, widget, event):
        """"""
        try:
            self.socket.send(event.string)
        except:
            print "Connection Closed"
            self.quit()

    def quit(self, widget=None, data=None):
        """"""
        gtk.main_quit()

if __name__ == "__main__":
    r = Remote()
