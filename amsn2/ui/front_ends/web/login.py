class aMSNLoginWindow(object):
    def __init__(self, amsn_core, main):
        self._main = main
        self._amsn_core = amsn_core

    def __del__(self):
        self._main.del_listener("signin", self.signin)

    def show(self):
        self._main.set_listener("signin", self.signin)

    def hide(self):
        self._main.send("hideLogin");
        self._main.del_listener("signin", self.signin)

    def setUsername(self, listU):
        self._username = listU.pop()

    def setPassword(self, listP):
        self._password = listP.pop()

    def set_accounts(self, accountviews):
        pass

    def signin(self, u, p, *args, **kwargs):
        accv = self._amsn_core._ui_manager.get_accountview_from_email(u)
        accv.password = password

        accv.presence = self.presence_key

        accv.save = False
        accv.save_password = False
        accv.autologin = False

        print "signing in"
        self._amsn_core.signin_to_account(self, accv)

    def on_connecting(self, progress, msg):
        self._main.send("onConnecting", msg)
