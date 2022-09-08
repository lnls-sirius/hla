"""Main module of the Application Interface."""

import os as _os
from qtpy.QtCore import Qt, QEvent
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel, \
    QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QTabWidget, \
    QFrame, QSpacerItem
from pydm.widgets.display_format import DisplayFormat

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..widgets import SiriusLabel, RelativeWidget
from .util import BASIC_INFO
from .chart import ChartWindow, ChartMon
from .motor_control import MotorControlWindow
from .controls import ControlBox, DEVICES


class LLRFMain(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.display_format = DisplayFormat
        self.main_dev = 'LA-RF:LLRF:'
        self.setObjectName('LIApp')
        self.setWindowTitle('LI LLRF')
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "llrf.png"))
        self.relative_widgets = []
        self._setupui()

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def buildPvName(self, pv_name, device, pvPrefix='', pvSufix=''):
        """Build the pv name"""
        return (self.prefix + self.main_dev +
            device + ":" + pvPrefix + pv_name + pvSufix)

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_container.setMinimumSize(950, 0)
        return self.image_container

    def formatLabel(self, pv_name='', pv_type='Power'):
        """Get widget type"""
        widget = SiriusLabel(init_channel=pv_name)
        widget.precisionFromPV = False
        widget.precision = 2
        if pv_type == 'Power':
            widget.displayFormat = self.display_format.Exponential
        return widget

    def showChartBtn(self, device, channel, chart_type):
        """Show the Chart Button Widget"""
        widget = QPushButton(chart_type)
        _util.connect_window(
            widget, ChartWindow,
            parent=self, dev=device, chart_type=chart_type, channel=channel)
        widget.setMinimumSize(20, 20)
        return widget

    def baseWidget(
        self, title='', pv_name=''):
            """Show the base widget"""
            """Base Widget: 'title'  'PV information'"""
            bw_hlay = QHBoxLayout()
            bw_hlay.addWidget(
                QLabel(title), alignment=Qt.AlignCenter)

            widget = self.formatLabel(pv_name, title)
            widget.showUnits = True
            bw_hlay.addWidget(
                widget, alignment=Qt.AlignCenter)

            return bw_hlay

    def basicInfoBox(self, device, channel, info):
        """Show the basic information of an element"""
        """
            The basic information of and element consists of:
            -Power and Phase information
            -Chart buttons
        """
        group = QGroupBox()
        bi_vlay = QVBoxLayout()
        bi_vlay.setContentsMargins(2, 2, 2, 2)

        for chart_type in info["Chart"]:
            bi_vlay.addWidget(
                self.showChartBtn(
                    device, channel, chart_type),
                alignment=Qt.AlignCenter)

        for basic_info in ["Power", "Phase"]:
            bi_vlay.addLayout(
                self.baseWidget(
                    basic_info,
                    self.buildPvName(
                        channel, device,
                        "GET_", '_' + basic_info.upper())))
        group.setLayout(bi_vlay)
        group.setStyleSheet('''
            max-width: 160px; max-height: 150px;
        ''')

        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=group,
            relative_pos=info["Position"])
        self.relative_widgets.append(rel_wid)

    def motorControlBtn(self, device, info):
        """Show the motor control button"""
        btn = QPushButton("Motor Control")
        _util.connect_window(
            btn, MotorControlWindow,
            parent=self, motor_type=device)
        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=btn,
            relative_pos=info["Position"])
        self.relative_widgets.append(rel_wid)

    def buildDevicesWidgets(self):
        """Build and arrange the basic information
        and control buttons on the image"""

        for device, channel in BASIC_INFO.items():
            for pv_name, info in channel.items():
                if device != "MOTOR":
                    self.basicInfoBox(device, pv_name, info)
                else:
                    self.motorControlBtn(pv_name, info)

    def buildLine(self):
        """ Build a single horizontal line """
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Raised)
        line.setStyleSheet('color: gray;')
        line.setLineWidth(3)
        return line

    def buildChartMonitor(self):
        """ Build the Control Loop Monitor tab """
        widget = QWidget()
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        for dev in DEVICES:
            lay.addWidget(
                ChartMon(
                    parent=self, dev=dev.pvname, prefix=self.prefix))
            if dev != DEVICES.SHB:
                lay.addWidget(self.buildLine())
        widget.setLayout(lay)
        return widget

    def buildTabs(self):
        """ Build the tab widget """
        tab = QTabWidget()
        tab.setObjectName("LITab")
        tab.setContentsMargins(0, 0, 0, 0)
        tab.addTab(self.imageViewer(), "Complete Footprint")
        tab.addTab(self.buildChartMonitor(), "Control Loop Monitor")

        return tab

    def _setupui(self):
        """ . """
        lay1 = QGridLayout()
        self.setLayout(lay1)

        lay1.addWidget(self.buildTabs(), 0, 1)
        self.buildDevicesWidgets()

        conlay = QGridLayout()
        conlay.addItem(
            QSpacerItem(1, 12, QSizePolicy.Ignored, QSizePolicy.Fixed), 0, 0)
        for dev in DEVICES:
            grbox = QGroupBox(dev.label, self)
            lay = QGridLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            grbox.setLayout(lay)
            lay.addWidget(
                ControlBox(
                    grbox, dev.pvname, main_dev=self.main_dev,
                    device=dev, prefix=self.prefix),
                0, 0)
            conlay.addWidget(grbox, dev.value+1, 0)
        lay1.addLayout(conlay, 0, 0)
