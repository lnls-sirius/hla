#!/usr/bin/env python-sirius
"""HLA TB and TS ICT monitoring Window."""

import sys
import os as _os
from qtpy.uic import loadUi
from qtpy.QtCore import QPoint, Qt, QEvent
from qtpy.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFormLayout, \
    QSpacerItem,  QSizePolicy as QSzPlcy, QLabel, QGroupBox, QPushButton
import qtawesome as qta
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from pydm.widgets import PyDMLabel, PyDMPushButton
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusDialog, PyDMLed, \
                              SiriusConnectionSignal, PyDMLedMultiChannel
from siriushla import util


class SlitsView(QWidget):
    """Class to create Slits View Widget."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super(SlitsView, self).__init__(parent)
        self.setObjectName('TBApp')
        gbox_slith = QGroupBox('TB-01:DI-SlitH')
        self.slith = SlitMonitoring('H', self, prefix)
        lay_slith = QVBoxLayout()
        lay_slith.addWidget(self.slith)
        gbox_slith.setLayout(lay_slith)

        gbox_slitv = QGroupBox('TB-01:DI-SlitV')
        self.slitv = SlitMonitoring('V', self, prefix)
        lay_slitv = QVBoxLayout()
        lay_slitv.addWidget(self.slitv)
        gbox_slitv.setLayout(lay_slitv)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('<h3>TB Slits View</h3>',
                             alignment=Qt.AlignCenter))
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addWidget(gbox_slith)
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addWidget(gbox_slitv)
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        self.setLayout(lay)

    def changeEvent(self, event):
        """Override keyPressEvent."""
        if event.type() == QEvent.FontChange:
            self.slith.updateSlitWidget()
            self.slitv.updateSlitWidget()
        super().changeEvent(event)


class SlitMonitoring(QWidget):
    """Class to create Slits Monitor Widget."""

    def __init__(self, slit_orientation, parent=None, prefix=''):
        """Init."""
        super(SlitMonitoring, self).__init__(parent)
        if not prefix:
            self.prefix = _VACA_PREFIX
        else:
            self.prefix = prefix
        self.slit_orientation = slit_orientation.upper()
        self._slit_center = 0
        self._slit_width = 0

        tmp_file = _substitute_in_file(
            _os.path.abspath(_os.path.dirname(__file__))+'/ui_tb_ap_slit' +
            slit_orientation.lower()+'mon.ui', {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setObjectName('TBApp')
        self.centralwidget.setObjectName('TBApp')
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.centralwidget)

        self.updateSlitWidget()

        slit_prefix = prefix+'TB-01:DI-Slit'+self.slit_orientation
        self.conn_slitcenter = SiriusConnectionSignal(slit_prefix+':Center-RB')
        self.conn_slitcenter.new_value_signal[float].connect(self._setSlitPos)
        self.conn_slitwidth = SiriusConnectionSignal(slit_prefix+':Width-RB')
        self.conn_slitwidth.new_value_signal[float].connect(self._setSlitPos)

        channels2values = {slit_prefix+':ForceComplete-Mon': 1,
                           slit_prefix+':NegativeDoneMov-Mon': 1,
                           slit_prefix+':PositiveDoneMov-Mon': 1}
        multiled_status = PyDMLedMultiChannel(self, channels2values)
        multiled_status.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self.centralwidget.lay_status.addWidget(multiled_status)

        pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        pb_details.setToolTip('Open details')
        pb_details.setObjectName('detail')
        pb_details.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        util.connect_window(pb_details, _SlitDetails, parent=self,
                            slit_prefix=slit_prefix)
        self.centralwidget.lay_status.addWidget(pb_details)

    def _setSlitPos(self, new_value):
        """Set Slits Widget positions."""
        if 'Center' in self.sender().address:
            self._slit_center = new_value  # considering mm
        elif 'Width' in self.sender().address:
            self._slit_width = new_value
        self.updateSlitWidget()

    def updateSlitWidget(self):
        """Update slit illustration."""
        widget_w = self.centralwidget.widget_draw.width()
        widget_h = self.centralwidget.widget_draw.height()
        vacuum_chamber_d = 36  # mm

        if self.slit_orientation == 'H':
            rect_h = widget_h*3/5
            rect_w = rect_h/2
            circle_d = rect_w
            xc = (circle_d*self._slit_center/vacuum_chamber_d + widget_w/2)
            xw = circle_d*self._slit_width/vacuum_chamber_d

            self.centralwidget.PyDMDrawingRectangle_SlitHLeft.resize(
                rect_w, rect_h)
            self.centralwidget.PyDMDrawingRectangle_SlitHRight.resize(
                rect_w, rect_h)
            left = round(xc - rect_w - xw/2)
            right = round(xc + xw/2)
            self.centralwidget.PyDMDrawingRectangle_SlitHLeft.move(
                QPoint(left, (widget_h-rect_h)/2))
            self.centralwidget.PyDMDrawingRectangle_SlitHRight.move(
                QPoint(right, (widget_h-rect_h)/2))

        elif self.slit_orientation == 'V':
            rect_w = widget_h*3/5
            rect_h = rect_w/2
            circle_d = rect_h
            xc = (circle_d*self._slit_center/vacuum_chamber_d + widget_h/2)
            xw = circle_d*self._slit_width/vacuum_chamber_d

            self.centralwidget.PyDMDrawingRectangle_SlitVUp.resize(
                rect_w, rect_h)
            self.centralwidget.PyDMDrawingRectangle_SlitVDown.resize(
                rect_w, rect_h)
            up = round(xc - rect_h - xw/2)
            down = round(xc + xw/2)
            self.centralwidget.PyDMDrawingRectangle_SlitVUp.move(
                QPoint((widget_w-rect_w)/2, up))
            self.centralwidget.PyDMDrawingRectangle_SlitVDown.move(
                QPoint((widget_w-rect_w)/2, down))

        self.centralwidget.PyDMDrawingCircle.resize(circle_d, circle_d)
        self.centralwidget.PyDMDrawingCircle.move(QPoint(
            (widget_w-circle_d)/2, (widget_h-circle_d)/2))

    def channels(self):
        """Return channels."""
        return [self.conn_slitcenter, self.conn_slitwidth]


class _SlitDetails(SiriusDialog):

    def __init__(self, slit_prefix, parent=None):
        """Init."""
        super(_SlitDetails, self).__init__(parent)
        self.slit_prefix = _PVName(slit_prefix)
        self.setObjectName(self.slit_prefix.sec+'App')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>'+self.slit_prefix+' Control Details</h3>', self,
                       alignment=Qt.AlignCenter)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_status = QGroupBox('Status', self)
        gbox_status.setLayout(self._setupDetailedStatusLayout())

        gbox_force = QGroupBox('Commands to Force Positions', self)
        gbox_force.setLayout(self._setupForceCommandsLayout())

        lay = QGridLayout()
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 1, 0)
        lay.addWidget(gbox_general, 2, 0, 1, 2)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 3, 0)
        lay.addWidget(gbox_status, 4, 0, 1, 2)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 5, 0)
        lay.addWidget(gbox_force, 6, 0, 1, 2)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 7, 0)
        self.setLayout(lay)

    def _setupGeneralInfoLayout(self):
        label_NegMtrCtrlPrefix = QLabel('Negative Motion Control: ', self)
        self.PyDMLabel_NegMtrCtrlPrefix = PyDMLabel(
            parent=self,
            init_channel=self.slit_prefix+':NegativeMotionCtrl-Cte')
        self.PyDMLabel_NegMtrCtrlPrefix.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        label_PosMtrCtrlPrefix = QLabel('Positive Motion Control: ', self)
        self.PyDMLabel_PosMtrCtrlPrefix = PyDMLabel(
            parent=self,
            init_channel=self.slit_prefix+':PositiveMotionCtrl-Cte')
        self.PyDMLabel_PosMtrCtrlPrefix.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_NegMtrCtrlPrefix, self.PyDMLabel_NegMtrCtrlPrefix)
        flay.addRow(label_PosMtrCtrlPrefix, self.PyDMLabel_PosMtrCtrlPrefix)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupDetailedStatusLayout(self):
        label_NegDoneMov = QLabel('Negative Edge Motor Finished Move? ', self)
        self.PyDMLed_NegDoneMov = PyDMLed(
            parent=self, init_channel=self.slit_prefix+':NegativeDoneMov-Mon',
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_NegDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_PosDoneMov = QLabel('Positive Edge Motor Finished Move? ', self)
        self.PyDMLed_PosDoneMov = PyDMLed(
            parent=self, init_channel=self.slit_prefix+':PositiveDoneMov-Mon',
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_PosDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_NegDoneMov, self.PyDMLed_NegDoneMov)
        flay.addRow(label_PosDoneMov, self.PyDMLed_PosDoneMov)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupForceCommandsLayout(self):
        self.PyDMPushButton_DoHome = PyDMPushButton(
            parent=self, label='Do Homing', pressValue=1,
            init_channel=self.slit_prefix+':Home-Cmd')

        self.PyDMPushButton_NegDoneMov = PyDMPushButton(
            parent=self, label='Force Negative Edge Position', pressValue=1,
            init_channel=self.slit_prefix+':ForceNegativeEdgePos-Cmd')

        self.PyDMPushButton_PosDoneMov = PyDMPushButton(
            parent=self, label='Force Positive Edge Position', pressValue=1,
            init_channel=self.slit_prefix+':ForcePositiveEdgePos-Cmd')

        label_ForceComplete = QLabel('Force Commands Completed? ', self)
        self.PyDMLed_ForceComplete = PyDMLed(
            parent=self, init_channel=self.slit_prefix+':ForceComplete-Mon',
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_ForceComplete.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(self.PyDMPushButton_DoHome)
        flay.addRow(self.PyDMPushButton_NegDoneMov)
        flay.addRow(self.PyDMPushButton_PosDoneMov)
        flay.addRow(label_ForceComplete, self.PyDMLed_ForceComplete)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    w = SlitMonitoring(slit_orientation='H', prefix=_VACA_PREFIX)
    window = SiriusMainWindow()
    window.setCentralWidget(w)
    window.setWindowTitle('SlitH Monitor')
    window.show()
    sys.exit(app.exec_())
