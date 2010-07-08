import os
import socket
import errno
import logging
import urlparse
import re
import gobject
import cgi

from constants import BASEPATH
from tinyhttpserver import TinyHTTPServer

def uri_path_is_safe(path):
    if not BASEPATH and path[0] == '/':
        return False
    elif path[0:1] == '..':
        return False

    l = path.split('/')
    b = [d for d in l if d == '..']

    if len(b) >= len(l):
        return False

    return True


class Backend(object):
    """
    This is the main comunication module,
    all comunication to the JS frontend will be issued from here
    """
    def __init__(self, core):
        self._core = core
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(0)
        self._socket.bind(("127.0.0.1", 8080))
        self._socket.listen(1)
        self._workers = []
        self._rules = (
            (re.compile('/$'), self.get_index, None),
            (re.compile('/static/(.*)'), self.get_static_file, None),
            (re.compile('/signin'), None, self.post_signin),
        )

        gobject.io_add_watch(self._socket, gobject.IO_IN, self.on_accept)

    def on_accept(self, s, c):
        w = s.accept()
        t = TinyHTTPServer(self, *w, rules = self._rules)
        self._workers.append(t)
        return True

    def emit_event(self, event, *args, **kwargs):
        """
        if event in self.listeners.keys():
            for func in self.listeners[event]:
                try:
                    func(*args, **kwargs)
                except:
                    pass
        """

    def send(self, event, *args, **kwargs):
        # The backend sent a message to the JS client
        # select the JS function to call depending on the type of event
        call = event + "(["
        for value in args:
            call += "'" + str(value).encode('string_escape') + "',"
        call = call.rstrip(",") + "]);"
        #self._outq.put_nowait(call)
        print call

    def _500(self, w, uri, headers, body = None):
        path = uri[2]
        print "500 on %s" % (path,)
        w.write("HTTP/1.1 500\r\n\r\n")
        w.close()

    def _404(self, w, uri, headers, body = None):
        path = uri[2]
        print "404 on %s" % (path,)
        w.write("HTTP/1.1 404\r\n\r\n")
        w.close()

    def _500(self, w, uri, headers, body = None):
        path = uri[2]
        print "500 on %s" % (path,)
        w.write("HTTP/1.1 500\r\n\r\n")
        w.close()

    def _501(self, w, uri, headers, body = None):
        path = uri[2]
        print "501 on %s" % (path,)
        w.write("HTTP/1.1 501\r\n\r\n")
        w.close()

    def get_index(self, w, uri, headers, body = None):
        w.send_file(BASEPATH + "/static/amsn2.html")

    def get_static_file(self, w, uri, headers, body = None):
        path = uri[2]
        if uri_path_is_safe(path):
            w.send_file(path)
        else:
            self._404(w, uri, headers, body = None)


    def post_signin(self, w, uri, headers, body = None):
        print "---------"
        print body
        print "---------"
        if (body and 'Content-Type' in headers
        and headers['Content-Type'] == 'application/x-www-form-urlencoded'):
            args = cgi.parse_qs(body)
            print args
            # TODO
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            return
        self._400(self, w, uri, headers, body)
