from amsn2.ui import base
import image
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class aMSNFileChooserWindow(base.aMSNFileChooserWindow, QFileDialog):
    def __init__(self, filters, directory, callback):
        QFileDialog.__init__(self, "aMSN2 -Choose a file", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        

        #if filters:
        #    for name in filters.keys():
        #        filefilter = gtk.FileFilter()
        #        filefilter.set_name(name)
        #        for ext in filters[name]:
        #            filefilter.add_pattern(ext)
        #        self.add_filter(filefilter)


        self.callback = callback

        QObject.connect(self, SIGNAL("fileSelected(QString)"), self.onReponse)

        self.show()


    def onResponse(self, file):
        if file ==""
        	pass
        else
        	self.callback(file)
        	
        self.destroy()



class aMSNDPChooserWindow(base.aMSNDPChooserWindow, QWidget):
    def __init__(self, callback, backend_manager):
        
        self.resize(550, 450)
        self.setWindowTitle("aMSN - Choose a Display Picture")
        self.callback = callback
        self.view = None
        self.child = None
        
        self.iconview= QListWidget()
        self.iconview.setViewMode(1)
        self.buttonOk= QPushButton("Ok")
        self.buttonCancel = QPushButton("Cancel")
        self.buttonOpen = QPushButton("Open File")
        QObject.connect(self.buttonOpen, SIGNAL("clicked()"), self._open_file)
        self.vboxlayout = QVBoxLayout()
        self.hboxlayout = QHBoxLayout()
        self.vbox = QWidget()
        
        vboxlayout.addWidget(self.buttonOk)
        vboxlayout.addWidget(self.buttonCancel)
        vboxlayout.addWidget(self.buttonOpen)
        
        self.vbox.setLayout(self.hboxlayout)
        
        self.hboxlayout.addWidget(iconview)
        self.hboxlayout.addWidget(vbox)
        
        self.setLayout(hboxlayout)
        

        default_dps = []
        for dp in default_dps:
            self._update_dp_list(default_dps)

        self.show()

    def _open_file(self):
        filters = {'Image files':("*.png", "*.jpeg", "*.jpg", "*.gif", "*.bmp"),
                   'All files':('*.*')}
        aMSNFileChooserWindow(filters, None, self._update_dp_list)


    def _dp_chosen(self):
        self.callback(self.view)
        self.destroy()

    def __on_dp_dblclick(self, widget, path):
        if path:
            iter = self._model.get_iter(path)
            self.view = self._model.get_value(iter, 1)
            self._dp_chosen(None)
            return True

        else:
            return False

    def _update_dp_list(self, dp_path):
        im = QIcon(dp_path)
        self.iconview.addItem(im, dp_path)
