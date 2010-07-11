class aMSNLoginWindow(object):
    def __init__(self, core, main):
        self._main = main
        self._core = core

    def __del__(self):
        self._main.login_window = None

    def show(self):
        self._main.login_window = self

    def hide(self):
        self._main.login_window = None

    def set_accounts(self, accountviews):
        #TODO
        pass

    def signin(self, u, p, *args, **kwargs):
        accv = self._core._ui_manager.get_accountview_from_email(u)
        accv.password = password

        accv.presence = self.presence_key

        accv.save = False
        accv.save_password = False
        accv.autologin = False

        logging.error("signing in")
        self._core.signin_to_account(self, accv)

    def on_connecting(self, progress, msg):
        self._main.send("onConnecting", msg)
