''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
from qtpy.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets  import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QLabel, QGridLayout
from pydm.widgets import PyDMEnumComboBox, PyDMLabel
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow

#mdi-safe-square
#mdi-camera-metering-center

class LiBeamProfile(SiriusMainWindow):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = get_appropriate_color('LI')

        self.device = 'PRF2:'
        self.device_name = 'LA-BI:' + self.device

        self.setWindowIcon(qta.icon('mdi.safe-square', color=color))
        self.setWindowTitle(self.device_name)
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
                _os.path.abspath(_os.path.dirname(__file__)), "linac.jpg"))


        self._setupUi()

    def resizeEvent(self, event):
        self.image_container.setMinimumSize(1, 1)
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height())
        )
        SiriusMainWindow.resizeEvent(self, event)

    def getPvName(self, pv_name):
        return self.device_name + "MOTOR:" + pv_name

    def header(self):
        hd_hlay = QHBoxLayout()
        title = QLabel("<h2>" + self.device_name + " - Screen View</h2>")
        title.setAlignment(Qt.AlignCenter)
        hd_hlay.addWidget(title)
        return hd_hlay

    def imageViewer(self):
        img_hlay = QHBoxLayout()
        self.image_container.resize(650, 250)
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height())
        )
        img_hlay.addWidget(self.image_container)
        return img_hlay

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 1)
        if_glay.addLayout(self.imageViewer(), 1, 0, 50, 1)
        # if_glay.addWidget(PyDMEnumComboBox(self, init_channel=self.getPvName('POS_R')), 0, 1, 1, 1)
        # if_glay.addWidget(PyDMLabel(self, init_channel=self.getPvName('BUSY')), 1, 1, 1, 1)
        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
