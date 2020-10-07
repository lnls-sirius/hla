"""Sirius General Status Window."""

import numpy as _np

from qtpy.QtCore import Qt, Slot, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, \
    QVBoxLayout, QGroupBox, QHBoxLayout, QApplication
from qtpy.QtGui import QColor, QFont

import qtawesome as qta
# from pyqtgraph import mkBrush

from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX

from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow, SiriusTimePlot, SiriusFrame, \
    SiriusLedState, SiriusLedAlert, SiriusConnectionSignal, PyDMLedMultiChannel
from siriushla.as_di_tune.controls import SITuneMonitor
from siriushla.as_ap_launcher.standby_widgets import InjSysStandbyStatusLed


class SIGenStatusWindow(SiriusMainWindow):
    """Sirius General Status Window."""

    def __init__(self, prefix=VACA_PREFIX, parent=None):
        super().__init__(parent)
        self.prefix = prefix
        self.app = QApplication.instance()
        self.setObjectName('ASApp')
        self.setWindowTitle('Sirius General Status')
        self.setWindowIcon(
            qta.icon('mdi.view-split-vertical',
                     color=get_appropriate_color('AS')))
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel('<h2>Sirius Status</h2>',
                            alignment=Qt.AlignCenter)

        # controls
        self.ld_machsht = QLabel(
            '<h4>Shift: </h4>', self, alignment=Qt.AlignCenter)
        self.lb_machsht = PyDMLabel(
            self, self.prefix+'AS-Glob:AP-MachShift:Mode-Sts')
        self.lb_machsht.setAlignment(Qt.AlignCenter)
        self.lb_machsht.setStyleSheet('QLabel{font-size: 13.5pt;}')
        color_list = [
            SiriusFrame.Yellow,  # Users
            SiriusFrame.LightGreen,  # Commissioning
            SiriusFrame.LightBlue,  # Conditioning
            SiriusFrame.Red,  # Injection
            SiriusFrame.LightGreen,  # MachineStudy
            SiriusFrame.LightSalmon,  # Maintenance
        ]
        self.frm_machsht = SiriusFrame(
            self, self.prefix+'AS-Glob:AP-MachShift:Mode-Sts',
            color_list=color_list, is_float=False)
        self.frm_machsht.add_widget(self.lb_machsht)
        box_mach = QHBoxLayout()
        box_mach.addWidget(self.ld_machsht)
        box_mach.addWidget(self.frm_machsht)
        box_mach.setStretch(0, 1)
        box_mach.setStretch(1, 4)

        self._led_siriusintlk = SiriusLedAlert(
            self, self.prefix+'SI-02SB:RF-Intlk:SIA-Mon')
        self._led_siriusintlk.setStyleSheet(
            'min-width:2em; min-height:2em;')
        self._gbox_siriusintlk = self._create_groupbox(
            'Sirius Interlock', self._led_siriusintlk)

        self._led_injsyssts = InjSysStandbyStatusLed()
        self._led_injsyssts.setStyleSheet(
            'min-width:2em; min-height:2em;')
        self._gbox_injsyssts = self._create_groupbox(
            'Injection System', self._led_injsyssts)

        self._led_sofbloop = SiriusLedState(
            self, self.prefix+'SI-Glob:AP-SOFB:LoopState-Sts')
        self._led_sofbloop.setStyleSheet(
            'min-width:2em; min-height:2em;')
        self._led_sofbloop.offColor = SiriusLedState.Red
        self._gbox_sofbloop = self._create_groupbox(
            'SOFB Loop', self._led_sofbloop)

        bbbdev_pref = 'SI-Glob:DI-BbBProc-L'
        self._led_bbbloop = SiriusLedState(
            self, self.prefix+bbbdev_pref+':FBCTRL')
        self._led_bbbloop.setStyleSheet(
            'min-width:2em; min-height:2em;')
        self._led_bbbloop.offColor = SiriusLedState.Red
        chs2vals = {
            bbbdev_pref+':CLKMISS': 0,
            bbbdev_pref+':PLL_UNLOCK': 0,
            bbbdev_pref+':DCM_UNLOCK': 0,
            bbbdev_pref+':ADC_OVR': 0,
            bbbdev_pref+':SAT': 0,
            bbbdev_pref+':FID_ERR': 0}
        self._led_bbbsts = PyDMLedMultiChannel(self, chs2vals)
        self._led_bbbsts.setStyleSheet(
            'min-width:2em; min-height:2em;')
        self._led_bbbsts.offColor = SiriusLedState.Red
        self._gbox_bbbloop = self._create_groupbox(
            'BbB Loop', [self._led_bbbloop, self._led_bbbsts], orientation='H')

        # current
        self.ld_curr = QLabel(
            '<h4>Current</h4>', self, alignment=Qt.AlignCenter)
        self.ld_curr.setStyleSheet('max-height: 2em;')
        self.lb_curr = PyDMLabel(
            self, self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon')
        self.lb_curr.setAlignment(Qt.AlignCenter)
        self.lb_curr.setStyleSheet(
            'QLabel{background-color: #d7ccc8;font-size: 30pt;}')
        self.lb_curr.showUnits = True
        self.frm_curr = SiriusFrame(
            self, self.prefix+'SI-Glob:AP-CurrInfo:StoredEBeam-Mon',
            color_list=[SiriusFrame.DarkGreen, SiriusFrame.LightGreen],
            is_float=False)
        self.frm_curr.borderWidth = 5
        self.frm_curr.add_widget(self.lb_curr)
        box_curr = QGridLayout()
        box_curr.setAlignment(Qt.AlignCenter)
        box_curr.addWidget(self.ld_curr, 0, 0)
        box_curr.addWidget(self.frm_curr, 1, 0)
        box_curr.setColumnStretch(0, 5)
        box_curr.setColumnStretch(1, 1)

        self.ld_lifetime = QLabel(
            '<h4>Lifetime</h4>', self, alignment=Qt.AlignCenter)
        self.ld_lifetime.setStyleSheet('max-height: 2em;')
        self.lb_lifetime = QLabel('0:00:00', self, alignment=Qt.AlignCenter)
        self.lb_lifetime.setStyleSheet('QLabel{font-size: 30pt;}')
        self.ch_lifetime = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon')
        self.ch_lifetime.new_value_signal[float].connect(
            self.formatLifetimeLabel)
        box_lt = QGridLayout()
        box_lt.setAlignment(Qt.AlignCenter)
        box_lt.addWidget(self.ld_lifetime, 0, 0)
        box_lt.addWidget(self.lb_lifetime, 1, 0)

        self.tune_mon = SITuneMonitor(self, self.prefix, description='short')

        self.curr_graph = SiriusTimePlot(self)
        self.curr_graph.setObjectName('curr_graph')
        self.curr_graph.setStyleSheet(
            '#curr_graph{min-width: 20em; min-height: 20em;}')
        self.curr_graph.showXGrid = True
        self.curr_graph.showYGrid = True
        self.curr_graph.backgroundColor = QColor(255, 255, 255)
        self.curr_graph.timeSpan = 30*60
        self.curr_graph.setYLabels(['Current [mA]'])
        for ax in self.curr_graph.getPlotItem().axes.values():
            sty = ax['item'].labelStyle
            sty['font-size'] = '12pt'
            ax['item'].setLabel(text=None, **sty)
        font = QFont()
        font.setPointSize(12)
        self.curr_graph.plotItem.getAxis('bottom').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=80, tickFont=font)
        self.curr_graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=80, tickFont=font)
        self.curr_graph.addYChannel(
            y_channel=self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon',
            name='Current', color='blue', lineStyle=Qt.SolidLine, lineWidth=1)
        self.curve = self.curr_graph.curveAtIndex(0)
        # self.curve.setFillLevel(0)
        # self.curve.setBrush(mkBrush(color='b'))

        cw = QWidget()
        hlay1 = QHBoxLayout()
        hlay1.setSpacing(14)
        hlay1.setAlignment(Qt.AlignVCenter)
        hlay1.addLayout(box_curr)
        hlay1.addLayout(box_lt)
        hlay1.addWidget(self.tune_mon)

        hlay2 = QHBoxLayout()
        hlay2.setSpacing(14)
        hlay2.addWidget(self._gbox_siriusintlk)
        hlay2.addWidget(self._gbox_injsyssts)
        hlay2.addWidget(self._gbox_sofbloop)
        hlay2.addWidget(self._gbox_bbbloop)
        hlay2.setStretch(0, 1)
        hlay2.setStretch(1, 1)
        hlay2.setStretch(2, 1)
        hlay2.setStretch(3, 1)

        lay = QGridLayout(cw)
        lay.setVerticalSpacing(16)
        lay.setHorizontalSpacing(14)
        lay.addLayout(box_mach, 0, 1)
        lay.addLayout(hlay1, 1, 0, 1, 3)
        lay.addWidget(self.curr_graph, 2, 0, 1, 3)
        lay.addLayout(hlay2, 3, 0, 1, 3)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 10)
        lay.setRowStretch(3, 2)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 1)
        self.setCentralWidget(cw)

    @Slot(float)
    def formatLifetimeLabel(self, value):
        lt = 0 if _np.isnan(value) else value
        H = int(lt // 3600)
        m = int((lt % 3600) // 60)
        s = int((lt % 3600) % 60)
        lt_str = '{:d}:{:02d}:{:02d}'.format(H, m, s)
        self.lb_lifetime.setText(lt_str)

    def _create_groupbox(self, title, widgets, orientation='V'):
        if not isinstance(widgets, list):
            widgets = [widgets, ]
        gbox = QGroupBox(title, self)

        lay = QVBoxLayout(gbox) if orientation == 'V' else QHBoxLayout(gbox)
        lay.addStretch()
        for wid in widgets:
            lay.addWidget(wid)
        lay.addStretch()
        return gbox

    def changeEvent(self, event):
        if event.type() == QEvent.FontChange:
            fontsize = self.app.font().pointSize()

            # labels
            self._lb_machsht.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+3.5)+'pt;}')
            self.lb_curr.setStyleSheet(
                'QLabel{background-color: #d7ccc8;'
                'font-size: '+str(fontsize+20)+'pt;}')
            self.lb_lifetime.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+20)+'pt;}')

            # graph
            graph_fontsize = fontsize + 2
            for ax in self.curr_graph.getPlotItem().axes.values():
                sty = ax['item'].labelStyle
                sty['font-size'] = str(graph_fontsize) + 'pt'
                ax['item'].setLabel(text=None, **sty)

            font = QFont()
            font.setPointSize(graph_fontsize)
            self.curr_graph.plotItem.getAxis('bottom').setStyle(
                tickTextOffset=5, autoExpandTextSpace=False,
                tickTextWidth=80, tickFont=font)
            self.curr_graph.plotItem.getAxis('left').setStyle(
                tickTextOffset=5, autoExpandTextSpace=False,
                tickTextWidth=80, tickFont=font)

            self.ensurePolished()
