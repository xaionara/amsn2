import os
import socket
import errno
import logging
import urlparse
import re
import gobject

READ_CHUNK_SIZE = 4096
BASEPATH="amsn2/ui/front_ends/web"

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


class TinyHTTPServer(object):
    def __init__(self, backend, socket, peer, rules):
        self._backend = backend
        self._socket = socket
        self._socket.setblocking(0)
        self._peer = peer

        self._rbuf = ""
        self._wbuf = ""
        self._read = 0
        self._written = 0

        self._read_delimiter = "\r\n\r\n"
        self._rcb = self.on_headers

        self._is_alive = True

        self._rules = rules

        self._in_id = gobject.io_add_watch(socket.fileno(),
                             gobject.IO_IN | gobject.IO_PRI,
                             self.on_read)
        self._out_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_OUT,
                             self.on_write)
        self._err_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_ERR,
                             self.on_error)
        self._hup_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_HUP,
                             self.on_hang_up)


    def close(self):
        if self._is_alive:
            self._is_alive = False
            gobject.source_remove(self._in_id)
            gobject.source_remove(self._out_id)
            gobject.source_remove(self._err_id)
            gobject.source_remove(self._hup_id)
            self._socket.close()
            self._socket = None

    def write(self, data):
        if self._is_alive:
            self._wbuf += data
            self.on_write(self._socket, gobject.IO_OUT)

    def on_headers(self, headers):
        eol = headers.find("\r\n")
        start_line = headers[:eol]
        method, uri, version = start_line.split(" ")
        print "method=%s, uri=%s, version=%s" % (method, uri, version)
        if not version.startswith("HTTP/"):
            self.close()
            return
        scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)
        for (r, get_cb, post_cb) in self._rules:
            if r.match(path):
                if method == "GET":
                    try:
                        get_cb(self, scheme, netloc, path, query, fragment)
                    except Exception as e:
                        print e
                        self._backend._500(self, scheme, netloc, path, query, fragment)
                    finally:
                        return
                elif method == "POST":
                    try:
                        post_cb(self, scheme, netloc, path, query, fragment)
                    except Exception as e:
                        print e
                        self._backend._500(self, scheme, netloc, path, query, fragment)
                    finally:
                        return
                else:
                    #TODO: head, put, delete, trace, options, connect, patch
                    self._backend._501(self, scheme, netloc, path, query, fragment)
                    return
        self._backend._404(self, scheme, netloc, path, query, fragment)


    def on_body(self, body):
        #TODO
        pass

    def on_read(self, s, c):
        print "on read"
        try:
            chunk = self._socket.recv(READ_CHUNK_SIZE)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return self._is_alive
            else:
                logging.warning("Read error on %d: %s",
                                self._socket.fileno(), e)
                self.close()
                return self._is_alive
        if not chunk:
            self.close()
            return self._is_alive

        self._rbuf += chunk
        self._read += len(chunk)
        if self._read >= 16777216:
            logging.error("Reached maximum read buffer size")
            self.close()
            return self._is_alive

        pos = self._rbuf.find(self._read_delimiter)
        if pos != -1:
            pos += len(self._read_delimiter)
            r = self._rbuf[:pos]
            self._rbuf = self._rbuf[pos:]
            self._rcb(r)
        return self._is_alive

    def on_write(self, s, c):
        print "on write"
        while self._wbuf:
            try:
                b = self._socket.send(self._wbuf)
                self._wbuf = self._wbuf[b:]
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                else:
                    logging.warning("Write error on %d: %s",
                                    self._socket.fileno(), e)
                    self.close()
                    return self._is_alive
        return self._is_alive

    def on_error(self, s, c):
        print "error"
        self.close()
        return self._is_alive

    def on_hang_up(self, s, c):
        print "hang up"
        self.close()
        return self._is_alive

    def send_file(self, path):
        f = open(BASEPATH + path, "r")
        r = f.read()
        f.close()
        self.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s"
                   % (len(r), r))
        self.close()



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
            (re.compile('/static/(.*)'), self.get_static_file, None)
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

    def _404(self, w, scheme, netloc, path, query, fragment):
        print "404 on %s" % (path,)
        w.write("HTTP/1.1 404\r\n\r\n")
        w.close()

    def _500(self, w, scheme, netloc, path, query, fragment):
        print "500 on %s" % (path,)
        w.write("HTTP/1.1 500\r\n\r\n")
        w.close()

    def _501(self, w, scheme, netloc, path, query, fragment):
        print "501 on %s" % (path,)
        w.write("HTTP/1.1 501\r\n\r\n")
        w.close()

    def get_index(self, w, scheme, netloc, path, query, fragment):
        w.send_file("/static/amsn2.html")

    def get_static_file(self, w, scheme, netloc, path, query, fragment):
        if uri_path_is_safe(path):
            w.send_file(path)
        else:
            self._404(w, scheme, netloc, path, query, fragment)
