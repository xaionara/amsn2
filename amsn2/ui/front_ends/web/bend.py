import cherrypy
import thread
import os
import logging
import threading
import Queue

class Backend(object):
    """
    This is the main comunication module,
    all comunication to the JS frontend will be issued from here
    """
    def __init__(self):
        self.listeners = {}
        self._outq = Queue.Queue(0)
        self._inq = Queue.Queue(0)


        def worker(inq, outq):
            class Root(object):
                def __init__(self, inq, outq):
                    self._inq = inq
                    self._outq = outq

                @cherrypy.expose
                def index(self):
                    raise cherrypy.HTTPRedirect("static/amsn2.html")

                @cherrypy.expose
                def signin(self, u=None, p=None):
                    self._inq.put_nowait(["signin", u, p])

                @cherrypy.expose
                def out(self):
                    l = []
                    while True:
                        try:
                            l.append(self._outq.get_nowait())
                        except Queue.Empty:
                            break;
                    logging.error("OOOOOO")
                    return l

            current_dir = os.path.dirname(os.path.abspath(__file__))
            cherrypy.config.update({'log.error_file': 'amsn2-web-error.log',
                                   'log.access_file': 'amsn2-web-access.log',
                                   'log.screen': False})

            conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static')},
                   }
            cherrypy.quickstart(Root(inq, outq), '/', config=conf)
        t = threading.Thread(target=worker, args=[self._inq, self._outq])
        t.daemon = True
        t.start()

    def add_listener(self, event, listener):
        if not self.listeners.has_key(event):
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def del_listener(self, event, listener):
        #TODO
        pass

    def check_event(self):
        # This function is called to check for events
        while True:
            try:
                e = self._inq.get_nowait()
                self.emit_event(e[0], e[1:])
            except Queue.Empty:
                break;
        # Return true to continue checking events
        return True

    def emit_event(self, event, *args, **kwargs):
        if event in self.listeners.keys():
            for func in self.listeners[event]:
                try:
                    func(*args, **kwargs)
                except:
                    pass

    def send(self, event, *args, **kwargs):
        # The backend sent a message to the JS client
        # select the JS function to call depending on the type of event
        call = event + "(["
        for value in args:
            call += "'" + str(value).encode('string_escape') + "',"
        call = call.rstrip(",") + "]);"
        self._outq.put_nowait(call)
        print call
