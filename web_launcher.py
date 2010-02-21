#!/usr/bin/env python

import web

import sys
import os
import optparse

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.insert(0, "./papyon")

import locale
locale.setlocale(locale.LC_ALL, '')

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

        options = optparse.Option()
        options.front_end = "web"
        options.account = u
        options.password = p
        options.auto_login = True
        aMSNCore(options)




if __name__ == "__main__":
    app.run()

