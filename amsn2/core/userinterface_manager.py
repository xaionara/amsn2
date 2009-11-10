
from amsn2 import gui
from views import *

import logging
logger = logging.getLogger('amsn2.ui_manager')

class aMSNUserInterfaceManager(object):
    def __init__(self, core):
        self._core = core
        self._ui = None
        self._splash = None
        self._login = None
        self._contactlist = None

    def loadUI(self, ui_name):
        guim = gui.GUIManager(self._core, ui_name)
        if guim.gui:
            self._ui = guim.gui

            self._main = self._ui.aMSNMainWindow(self._core)
            self._core._main = self._main
            self._skin_manager = self._ui.SkinManager(self._core)
            self._core._skin_manager = self._skin_manager
        else:
            logger.error('Unable to load UI %s' % ui_name)
            self._core.quit()

    def getLoop(self):
        return self._ui.aMSNMainLoop(self)

    def loadSplash(self):
        self._splash = self._ui.aMSNSplashScreen(self._core, self._main)
        image = ImageView()
        image.load("Filename","/path/to/image/here")

        self._splash.setImage(image)
        self._splash.setText("Loading...")
        self._splash.show()
        self._main.setTitle("aMSN 2 - Loading")
        return self._splash

    def loadLogin(self, accounts):
        self._login = self._ui.aMSNLoginWindow(self._core, self._main)
        self._login.setAccounts(accounts)

        if self._splash:
            self._splash.hide()
            self._splash = None

        if self._contactlist:
            self.unloadContactList()

        self._main.setTitle("aMSN 2 - Login")
        self._login.show()

    def unloadLogin(self):
        self._login.hide()
        self._login = None

    def loadContactList(self):
        self._contactlist = self._ui.aMSNContactListWindow(self._core, self._main)

        em = self._core._event_manager
        em.register(em.events.PERSONALINFO_UPDATED, self._contactlist.myInfoUpdated)

        clwidget = self._contactlist.getContactListWidget()
        em.register(em.events.CLVIEW_UPDATED, clwidget.contactListUpdated)
        em.register(em.events.GROUPVIEW_UPDATED, clwidget.groupUpdated)
        em.register(em.events.CONTACTVIEW_UPDATED, clwidget.contactUpdated)

        if self._login:
            self.unloadLogin()

        self._main.setTitle("aMSN 2")
        self._contactlist.show()

    def unloadContactList(self):
        self._contactlist.hide()

        em = self._core._event_manager
        em.unregister(em.events.PERSONALINFO_UPDATED, self._contactlist.myInfoUpdated)

        clwidget = self._contactlist.getContactListWidget()
        em.unregister(em.events.CLVIEW_UPDATED, clwidget.contactListUpdated)
        em.unregister(em.events.GROUPVIEW_UPDATED, clwidget.groupUpdated)
        em.unregister(em.events.CONTACTVIEW_UPDATED, clwidget.contactUpdated)

        self._contactlist = None

    def showDialog(self, message, buttons):
        self._ui.aMSNDialogWindow(message, buttons)

    def showNotification(self, message):
        self._ui.aMSNNotificationWindow(message)

    def showError(self, message):
        self._ui.aMSNErrorWindow(message)

    def loadChatWindow(self, conv_manager):
        return self._ui.aMSNChatWindow(conv_manager)

    def loadChatWidget(self, conversation, window, cuids):
        return self._ui.aMSNChatWidget(conversation, window, cuids)

    def loadContactInputWindow(self, callback):
        return self._ui.aMSNContactInputWindow(('Contact to add: ', 'Invite message: '),
                                                 callback, ())

    def loadContactDeleteWindow(self, callback):
        return self._ui.aMSNContactDeleteWindow('Contact to remove: ', callback, ())

    def loadDPChooserWindow(self):
        self._ui.aMSNDPChooserWindow(self._core._account.set_dp ,self._core._backend_manager)



