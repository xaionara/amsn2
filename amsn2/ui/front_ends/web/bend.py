import cherrypy
import thread
import os
import logging

class Backend(object):
    """
    This is the main comunication module,
    all comunication to the JS frontend will be issued from here
    """
    def __init__(self):
        self.listeners = {}
        self.out_stack = []

        class Root(object):
            def __init__(self, backend):
                self._backend = backend
            @cherrypy.expose
            def index(self):
                raise cherrypy.HTTPRedirect("static/amsn2.html")

            @cherrypy.expose
            def signin(self, u=None, p=None):
                self._backend.emit_event("signin", u, p)
                print self._backend.listeners

            @cherrypy.expose
            def out(self):
                l = self._backend.out_stack
                self._backend.out_stack = []
                return l

        current_dir = os.path.dirname(os.path.abspath(__file__))
        cherrypy.config.update({'log.error_file': 'amsn2-web-error.log',
                               'log.access_file': 'amsn2-web-access.log',
                               'log.screen': False})

        conf = {'/static': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir, 'static')},
               }

        self._web = thread.start_new_thread(
            cherrypy.quickstart(Root(self), '/', config=conf))

    def set_listener(self, event, listener):
        if not self.listeners.has_key(event):
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def del_listener(self, event, listener):
        #TODO
        pass

    def checkEvent(self):
        # This function is called to check for events in the file
        try:
            # one event per line, divided by columns divided by tab
            # the first column is the event, the next columns are the arguments
            eventDesc = self._in.readline()
            while len(eventDesc) > 0:
                try:
                    eventDesc = eventDesc.strip().split("\t")
                    eventName = eventDesc.pop(0)
                    realValues = []
                    for value in eventDesc:
                        realValues.append(str(value).decode('string_escape'))
                    if eventName is not "":
                        self.event(eventName, realValues)
                except:
                     # event problem.. probably a badly encoded string
                     break
                eventDesc = self._in.readline()
        except:
            # problem with lines (maybe empty file)
            pass
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
        self.out_stack.append(call)
        print call
