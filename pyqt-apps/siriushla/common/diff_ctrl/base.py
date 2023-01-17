#!/usr/bin/env python-sirius
"""Scraper and Slit Monitor Base class."""

import os as _os
from qtpy.uic import loadUi
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, \
    QLabel, QGridLayout, QScrollArea, QSizePolicy
import qtawesome as qta
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from pydm.widgets import PyDMPushButton
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import PyDMLedMultiChannel, SiriusLabel, SiriusSpinbox
from siriushla import util
from .details import DiffCtrlDetails as _DiffCtrlDetails


class DiffCtrlDevMonitor(QWidget):
    """Diff Ctrl Dev Monitor Widget."""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super(DiffCtrlDevMonitor, self).__init__(parent)
        if not prefix:
            self.prefix = _VACA_PREFIX
        else:
            self.prefix = prefix
        self.device = _PVName(device)
        self.device = self.device.substitute(prefix=self.prefix)
        self.section = self.device.sec
        self.orientation = self.device.dev[-1]
        self.setObjectName(self.section+'App')
        self._setupUi()
        self._createConnectors()
        self._setupControlWidgets()
        self.updateDevWidget()

        self.setStyleSheet("""
            SiriusSpinbox, SiriusLabel{
                min-width:5em; max-width: 5em;
            }""")

    def _setupUi(self):
        # status
        label_status = QLabel(
            'Status: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        channels2values = {
            self.device.substitute(propty='ForceComplete-Mon'): 1,
            self.device.substitute(propty='NegativeDoneMov-Mon'): 1,
            self.device.substitute(propty='PositiveDoneMov-Mon'): 1}
        self.multiled_status = PyDMLedMultiChannel(self, channels2values)
        self.multiled_status.setStyleSheet('max-width: 1.29em;')

        self.pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.pb_details.setToolTip('Open details')
        self.pb_details.setObjectName('detail')
        self.pb_details.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        util.connect_window(self.pb_details, _DiffCtrlDetails, parent=self,
                            prefix=self.prefix, device=self.device)

        self.lb_descCtrl1 = QLabel(
            '', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_Ctrl1 = SiriusSpinbox(self)
        self.lb_Ctrl1 = SiriusLabel(self)
        self.lb_descCtrl2 = QLabel(
            '', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_Ctrl2 = SiriusSpinbox(self)
        self.lb_Ctrl2 = SiriusLabel(self)

        self.pb_open = PyDMPushButton(
            parent=self, label='Open', pressValue=1,
            init_channel=self.device.substitute(propty='Home-Cmd'))

        tmp_file = _substitute_in_file(
            _os.path.abspath(_os.path.dirname(__file__))+'/ui_as_ap_dev' +
            self.orientation.lower()+'mon.ui', {'PREFIX': self.prefix})
        self.dev_widget = loadUi(tmp_file)
        self.dev_widget.setObjectName('dev')
        self.dev_widget_scrarea = QScrollArea()
        self.dev_widget_scrarea.setObjectName('scrarea')
        self.dev_widget_scrarea.setStyleSheet(
            '#scrarea{background-color: transparent; max-width: 15em;}'
            '#dev{background-color:transparent;}')
        self.dev_widget_scrarea.setWidget(self.dev_widget)
        self.dev_widget_scrarea.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(label_status, 0, 0)
        lay.addWidget(self.multiled_status, 0, 1)
        lay.addWidget(self.pb_details, 0, 2, alignment=Qt.AlignRight)
        lay.addWidget(self.lb_descCtrl1, 1, 0)
        lay.addWidget(self.sb_Ctrl1, 1, 1)
        lay.addWidget(self.lb_Ctrl1, 1, 2)
        lay.addWidget(self.lb_descCtrl2, 2, 0)
        lay.addWidget(self.sb_Ctrl2, 2, 1)
        lay.addWidget(self.lb_Ctrl2, 2, 2)
        lay.addWidget(self.pb_open, 3, 1, 1, 2)
        lay.addWidget(self.dev_widget_scrarea, 0, 3, 4, 1)

    def _createConnectors(self):
        """Create connectors to monitor device positions."""
        raise NotImplementedError

    def _setDevPos(self, new_value):
        """Set device widget positions."""
        raise NotImplementedError

    def _setupControlWidgets(self):
        """Setup control widgets channels/labels."""
        raise NotImplementedError

    def updateDevWidget(self):
        """Update device illustration."""
        raise NotImplementedError

    def channels(self):
        """Return channels."""
        raise NotImplementedError


class DiffCtrlView(QWidget):
    """Diff Ctrl View Widget."""

    DEVICE_PREFIX = ''
    DEVICE_CLASS = None

    def __init__(self, parent=None, prefix=''):
        """Init."""
        self.dev_type = 'Slits' if 'Slit' in self.DEVICE_PREFIX else 'Scrapers'
        self.sec = _PVName(self.DEVICE_PREFIX).sec
        super(DiffCtrlView, self).__init__(parent)
        self.setObjectName(self.sec+'App')

        devname = 'Slits' if 'Slit' in self.DEVICE_PREFIX else 'Scrapers'
        title = QLabel(
            '<h3>' + self.sec + ' ' + devname + ' View</h3>',
            alignment=Qt.AlignCenter)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        gbox_h = QGroupBox(self.DEVICE_PREFIX + 'H')
        self.dev_h = self.DEVICE_CLASS(self, prefix, self.DEVICE_PREFIX+'H')
        lay_h = QVBoxLayout()
        lay_h.addWidget(self.dev_h)
        gbox_h.setLayout(lay_h)

        gbox_v = QGroupBox(self.DEVICE_PREFIX + 'V')
        self.dev_v = self.DEVICE_CLASS(self, prefix, self.DEVICE_PREFIX+'V')
        lay_v = QVBoxLayout()
        lay_v.addWidget(self.dev_v)
        gbox_v.setLayout(lay_v)

        lay = QVBoxLayout()
        lay.setSpacing(20)
        lay.addWidget(title)
        lay.addWidget(gbox_h)
        lay.addWidget(gbox_v)
        self.setLayout(lay)

    def changeEvent(self, event):
        """Reimplement changeEvent."""
        if event.type() == QEvent.FontChange:
            self.dev_h.updateDevWidget()
            self.dev_v.updateDevWidget()
        super().changeEvent(event)
