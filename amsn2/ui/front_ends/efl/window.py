
from constants import *
import evas
import ecore
import ecore.evas
import ecore.x
import elementary

from amsn2.ui import base
from amsn2.core.views import MenuView, MenuItemView

class aMSNWindow(elementary.Window, base.aMSNWindow):
    def __init__(self, amsn_core):
        self._amsn_core = amsn_core
        elementary.Window.__init__(self, "aMSN", elementary.ELM_WIN_BASIC)
        self.resize(WIDTH, HEIGHT)
        self.on_key_down_add(self._on_key_down)
        self.fullscreen = False
        self.name_class_set = (WM_NAME, WM_CLASS)
        #self._has_menu = False
        self._child = None

        self._bg = elementary.Background(self)
        self.resize_object_add(self._bg)
        self._bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                                      evas.EVAS_HINT_EXPAND)
        self._bg.show()

        self._bx = elementary.Box(self)
        self.resize_object_add(self._bx)
        self._bx.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                                      evas.EVAS_HINT_EXPAND)
        self._bx.size_hint_align_set(evas.EVAS_HINT_FILL,
                                     evas.EVAS_HINT_FILL)
        self._bx.show()

        self._tb = None


    def set_child(self, child):
        if self._child:
            self._bx.unpack(self._child)
        self._child = child
        self._bx.pack_end(child)

    @property
    def _evas(self):
        return self.evas_get()

    def hide(self):
        pass

    def setTitle(self, text):
        self.title_set(text)

    def setMenu(self, mv):
        pass

    def toggleMenu(self):
        if self._tb:
            #TODO
            if True:
                self._tb.hide()
            else:
                self._tb.show()

    def _on_key_down(self, obj, event):
        pass

