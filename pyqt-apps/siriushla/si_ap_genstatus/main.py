"""Sirius General Status Window."""

import numpy as _np

from qtpy.QtCore import Qt, Slot, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, \
    QVBoxLayout, QGroupBox, QHBoxLayout, QApplication
from qtpy.QtGui import QColor, QFont, QBrush, QGradient

import qtawesome as qta

from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.clientarch.time import Time
from siriuspy.devices import InjSysStandbyHandler

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
        self.app_color = get_appropriate_color('SI')
        self.setObjectName('SIApp')
        self.setWindowTitle('Sirius General Status')
        self.setWindowIcon(
            qta.icon('mdi.view-split-vertical', color=self.app_color))
        self._setupUi()

    def _setupUi(self):
        # controls
        self.ld_machsht = QLabel(
            '<h3>Shift: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_machsht = PyDMLabel(
            self, self.prefix+'AS-Glob:AP-MachShift:Mode-Sts')
        self.lb_machsht.setAlignment(Qt.AlignCenter)
        self.lb_machsht.setStyleSheet('QLabel{font-size: 45pt;}')
        color_list = [
            SiriusFrame.Yellow,  # Users
            SiriusFrame.LightBlue,  # Commissioning
            SiriusFrame.DarkCyan,  # Conditioning
            SiriusFrame.LightSalmon,  # Injection
            SiriusFrame.LightBlue,  # MachineStudy
            SiriusFrame.LightGreen,  # Maintenance
            SiriusFrame.Salmon,  # Standby
            SiriusFrame.Lavender,  # Shutdown
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
            self, self.prefix+'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon')
        self._led_siriusintlk.setStyleSheet(
            'min-width:3em;min-height:3em;max-width:3em;max-height:3em;')
        self._gbox_siriusintlk = self._create_groupbox(
            'Sirius Interlock', self._led_siriusintlk)

        self._led_injsyssts = InjSysStandbyStatusLed(
            InjSysStandbyHandler(), self)
        self._led_injsyssts.setStyleSheet(
            'min-width:3em;min-height:3em;max-width:3em;max-height:3em;')
        self._gbox_injsyssts = self._create_groupbox(
            'Injection System', self._led_injsyssts)

        self._led_sofbloop = SiriusLedState(
            self, self.prefix+'SI-Glob:AP-SOFB:LoopState-Sts')
        self._led_sofbloop.setStyleSheet(
            'min-width:3em;min-height:3em;max-width:3em;max-height:3em;')
        self._led_sofbloop.offColor = SiriusLedState.Red
        self._gbox_sofbloop = self._create_groupbox(
            'SOFB Loop', self._led_sofbloop)

        bbbdev_pref = 'SI-Glob:DI-BbBProc-L'
        self._led_bbbloop = SiriusLedState(
            self, self.prefix+bbbdev_pref+':FBCTRL')
        self._led_bbbloop.setStyleSheet(
            'min-width:3em;min-height:3em;max-width:3em;max-height:3em;')
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
            'min-width:3em;min-height:3em;max-width:3em;max-height:3em;')
        self._led_bbbsts.offColor = SiriusLedState.Red
        self._gbox_bbbloop = self._create_groupbox(
            'BbB Loop', [self._led_bbbloop, self._led_bbbsts], orientation='H')

        # current
        self.ld_curr = QLabel(
            '<h3>Current [mA]</h3>', self, alignment=Qt.AlignCenter)
        self.ld_curr.setStyleSheet('max-height: 2em;')
        self.lb_curr = PyDMLabel(
            self, self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon')
        self.lb_curr.setAlignment(Qt.AlignCenter)
        self.lb_curr.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';font-size: 45pt;}')
        self.frm_curr = SiriusFrame(
            self, self.prefix+'SI-Glob:AP-CurrInfo:StoredEBeam-Mon',
            color_list=[SiriusFrame.DarkGreen, SiriusFrame.LightGreen],
            is_float=False)
        self.frm_curr.borderWidth = 5
        self.frm_curr.add_widget(self.lb_curr)
        box_curr = QWidget()
        lay_curr = QVBoxLayout(box_curr)
        lay_curr.setAlignment(Qt.AlignVCenter)
        lay_curr.addWidget(self.ld_curr)
        lay_curr.addWidget(self.frm_curr)

        self.ld_lifetime = QLabel(
            '<h3>Lifetime</h3>', self, alignment=Qt.AlignCenter)
        self.ld_lifetime.setStyleSheet('max-height: 2em;')
        self.lb_lifetime = QLabel('0:00:00', self, alignment=Qt.AlignCenter)
        self.lb_lifetime.setStyleSheet('QLabel{font-size: 45pt;}')
        self.ch_lifetime = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon')
        self.ch_lifetime.new_value_signal[float].connect(
            self.formatLifetimeLabel)
        box_lt = QWidget()
        lay_lt = QVBoxLayout(box_lt)
        lay_lt.setAlignment(Qt.AlignVCenter)
        lay_lt.addWidget(self.ld_lifetime)
        lay_lt.addWidget(self.lb_lifetime)

        self.tune_mon = SITuneMonitor(self, self.prefix, description='short',
                                      use_color_labels=False)
        self.tune_mon.lb_tunefrach.setStyleSheet('QLabel{font-size: 45pt;}')
        self.tune_mon.lb_tunefracv.setStyleSheet('QLabel{font-size: 45pt;}')
        self.curr_graph = SiriusTimePlot(self)
        self.curr_graph.setObjectName('curr_graph')
        self.curr_graph.setStyleSheet(
            '#curr_graph{min-width: 20em; min-height: 14em;}')
        self.curr_graph.showXGrid = True
        self.curr_graph.showYGrid = True
        self.curr_graph.backgroundColor = QColor(255, 255, 255)
        self.curr_graph.setYLabels(['Current [mA]'])
        for ax in self.curr_graph.getPlotItem().axes.values():
            sty = ax['item'].labelStyle
            sty['font-size'] = '18pt'
            ax['item'].setLabel(text=None, **sty)
        font = QFont()
        font.setPointSize(18)
        self.curr_graph.plotItem.getAxis('bottom').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=50, tickFont=font)
        self.curr_graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=50, tickFont=font)
        curr_pvname = self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon'
        self.curr_graph.addYChannel(
            y_channel=curr_pvname, name='Current',
            color='blue', lineStyle=Qt.SolidLine, lineWidth=2)
        self.curve = self.curr_graph.curveAtIndex(0)
        self.curve.setFillLevel(0)
        self.curve.setBrush(QBrush(QGradient(QGradient.ColdEvening)))

        timespan = 12*60*60
        self.curr_graph.timeSpan = timespan
        self.curr_graph.bufferSize = timespan*10
        self.curr_graph.maxRedrawRate = 2
        t_end = Time.now()
        t_init = t_end - timespan
        self.curr_graph.fill_curve_with_archdata(
            self.curve, curr_pvname,
            t_init=t_init.get_iso8601(), t_end=t_end.get_iso8601(),
            process_type='mean', process_bin_intvl=10)

        cw = QWidget()
        hlay1 = QHBoxLayout()
        hlay1.setSpacing(30)
        hlay1.setAlignment(Qt.AlignVCenter)
        hlay1.addWidget(box_curr)
        hlay1.addWidget(box_lt)
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
        gbox.setStyleSheet(
            'QGroupBox{font-size: 12pt; font-weight: bold;}')

        lay = QVBoxLayout(gbox) if orientation == 'V' else QHBoxLayout(gbox)
        lay.setAlignment(Qt.AlignCenter)
        lay.addStretch()
        for wid in widgets:
            lay.addWidget(wid)
        lay.addStretch()
        return gbox

    def changeEvent(self, event):
        if event.type() == QEvent.FontChange:
            fontsize = self.app.font().pointSize()

            # labels
            self.lb_machsht.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+35)+'pt;}')
            self.lb_curr.setStyleSheet(
                'QLabel{background-color: '+self.app_color+';'
                'font-size: '+str(fontsize+35)+'pt;}')
            self.lb_lifetime.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+35)+'pt;}')
            self.tune_mon.lb_tunefrach.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+35)+'pt;}')
            self.tune_mon.lb_tunefracv.setStyleSheet(
                'QLabel{font-size: '+str(fontsize+35)+'pt;}')

            self._gbox_siriusintlk.setStyleSheet(
                'QGroupBox{font-size: '+str(fontsize+2)+'pt;'
                'font-weight: bold;}')
            self._gbox_injsyssts.setStyleSheet(
                'QGroupBox{font-size: '+str(fontsize+2)+'pt;'
                'font-weight: bold;}')
            self._gbox_sofbloop.setStyleSheet(
                'QGroupBox{font-size: '+str(fontsize+2)+'pt;'
                'font-weight: bold;}')
            self._gbox_bbbloop.setStyleSheet(
                'QGroupBox{font-size: '+str(fontsize+2)+'pt;'
                'font-weight: bold;}')

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
