import os
import socket
import errno
import logging
import urlparse
import re
import gobject
from constants import READ_CHUNK_SIZE

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
        self._bytes_to_read = 0
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
            self.on_write(self._socket, gobject.IO_IN)

    def on_headers(self, headers):
        eol = headers.find("\r\n")
        start_line = headers[:eol]
        self._method, uri, self._version = start_line.split(" ")
        print headers
        self._headers = {}
        for line in headers[eol:].splitlines():
            if line:
                name, value = line.split(":", 1)
                self._headers[name] = value.strip()
        print "method=%s, uri=%s, version=%s" % (self._method, uri, self._version)
        if not self._version.startswith("HTTP/"):
            self.close()
            return
        self._uri = (scheme, netloc, path, query, fragment) = urlparse.urlsplit(uri)
        if self._method == "GET":
            for (r, get_cb, _) in self._rules:
                if r.match(path):
                    try:
                        get_cb(self, self._uri, self._headers)
                    except Exception as e:
                        print e
                        self._backend._500(self, self._uri, self._headers)
                    finally:
                        return
            self._backend._404(self, self._uri, self._headers)
        elif self._method == "POST":
            if "Content-Length" in self._headers:
                self._read_delimiter = None
                self._rcb = self.on_body
                self._bytes_to_read = int(self._headers["Content-Length"])
            else:
                self._backend._400(self, self._uri, self._headers)
        else:
            #TODO: head, put, delete, trace, options, connect, patch
            self._backend._501(self, self._uri, self._headers)
            return


    def on_body(self, body):
        print "ON BODY"
        if self._method == "POST":
            path = self._uri[2]
            for (r, _, post_cb) in self._rules:
                if r.match(path):
                    try:
                        post_cb(self, self._uri, self._headers, body)
                    except Exception as e:
                        print e
                        self._backend._500(self, self._uri, self._headers, body)
                    finally:
                        return
            self._backend._404(self, self._uri, self._headers, body)
        else:
            self._backend._501(self, self._uri, self._headers, body)

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

        if self._read_delimiter:
            pos = self._rbuf.find(self._read_delimiter)
            if pos != -1:
                pos += len(self._read_delimiter)
                r = self._rbuf[:pos]
                self._rbuf = self._rbuf[pos:]
                self._rcb(r)
                self._read -= pos
        if self._bytes_to_read > 0 and self._read >= self._bytes_to_read:
            r = self._rbuf[:self._bytes_to_read]
            self._rbuf = self._rbuf[self._bytes_to_read:]
            self._rcb(r)
            self._read -= self._bytes_to_read
            self._bytes_to_read = 0
        return self._is_alive

    def on_write(self, s, c):
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
        self.close()
        return self._is_alive

    def on_hang_up(self, s, c):
        self.close()
        return self._is_alive

    def send_file(self, path):
        f = open(path, "r")
        r = f.read()
        f.close()
        self.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s"
                   % (len(r), r))
        self.close()
