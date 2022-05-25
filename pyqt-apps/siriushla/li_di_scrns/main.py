''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
from qtpy.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets  import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QLabel, QGridLayout
from pydm.widgets import PyDMEnumComboBox, PyDMLabel
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, PyDMLed
from .util import DEVICES, MOTORS_PV

class LiBeamProfile(SiriusMainWindow):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = get_appropriate_color('LI')

        self.selected_device = DEVICES[0]
        self.device_name = 'LA-BI:'

        self.setWindowIcon(qta.icon('mdi.camera-metering-center', color=color))
        self.setWindowTitle(self.device_name)
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
                _os.path.abspath(_os.path.dirname(__file__)), "linac.png"))

        self._setupUi()

    def getPvName(self, device, pv_name):
        if device is not False:
            return self.device_name + device + ":" + pv_name
        else:
            return self.device_name + self.selected_device + ":" + pv_name

    def resizeEvent(self, event):
        self.image_container.setMinimumSize(1, 1)
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height())
        )
        SiriusMainWindow.resizeEvent(self, event)

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

    def setWidgetType(self, widType, device, pv_name):
        if widType == 0:
            widget = PyDMLabel(self,
                init_channel=self.getPvName(device, pv_name))
            widget.setAlignment(Qt.AlignCenter)
        elif widType == 1:
            widget = PyDMLed(self,
                init_channel=self.getPvName(device, pv_name))
        else:
            widget = QLabel("Error: Unknown device")
        return widget

    def motorHeader(self, device):
        mi_hlay = QHBoxLayout()
        for text in MOTORS_PV.get('labels'):
            label = QLabel('<h4>'+text+'</h4>')
            label.setAlignment(Qt.AlignCenter)
            mi_hlay.addWidget(label)
        return mi_hlay

    def motorInfo(self, device):
        mi_hlay = QHBoxLayout()
        pvList = MOTORS_PV.get('content')
        pv_name = 'MOTOR'+":"

        label = QLabel(device)
        label.setAlignment(Qt.AlignCenter)
        mi_hlay.addWidget(label)

        for item in range(0, len(pvList)):
            mi_hlay.addWidget(
                self.setWidgetType(item, device, pv_name+pvList[item]))
        return mi_hlay

    def allMotors(self):
        group = QGroupBox()
        am_vlay = QVBoxLayout()
        am_vlay.addLayout(self.motorHeader(MOTORS_PV.get('title')))
        for device in DEVICES:
            am_vlay.addLayout(self.motorInfo(device))


        group.setTitle(MOTORS_PV.get('title'))
        group.setLayout(am_vlay)
        return group

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0)
        if_glay.addLayout(self.imageViewer(), 1, 0)
        if_glay.addWidget(self.allMotors(), 2, 0)

        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
