
import web
import optparse
from amsn2.core import aMSNCore


urls = (
  '/signin', 'signin'
)


app = web.application(urls, globals())

class signin:
    def POST(self):
        i = web.input()
        try:
            u = i.u
            p = i.p
        except Exception:
            return web.badrequest("")




if __name__ == "__main__":
    app.run()

