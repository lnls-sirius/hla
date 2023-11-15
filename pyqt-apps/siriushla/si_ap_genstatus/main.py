"""Sirius General Status Window."""

import numpy as _np

from qtpy.QtCore import Qt, Slot, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, \
    QVBoxLayout, QGroupBox, QHBoxLayout, QApplication
from qtpy.QtGui import QColor, QFont, QBrush, QGradient

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientarch.time import Time
from siriuspy.injctrl.csdev import Const as _InjConst

from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusTimePlot, SiriusFrame, \
    SiriusLedState, SiriusLedAlert, SiriusConnectionSignal, \
    PyDMLedMultiChannel, SiriusLabel
from ..as_di_tune.controls import SITuneMonitor
from ..as_ap_injection import InjSysStbyLed
from ..as_ap_machshift import MachShiftLabel


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
        # machine shift
        self.ld_machsht = QLabel(
            '<h3>Shift: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_machsht = MachShiftLabel(self, prefix=self.prefix)
        self.lb_machsht.label.setStyleSheet('QLabel{font-size: 45pt;}')

        # injection mode
        self.ld_injmode = QLabel(
            '<h3>Inj.Mode: </h3>', self, alignment=Qt.AlignCenter)
        injctrl_dev = _PVName('AS-Glob:AP-InjCtrl')
        injctrl_dev = injctrl_dev.substitute(prefix=self.prefix)
        pvname = injctrl_dev.substitute(propty='Mode-Sts')
        self.lb_injmode = SiriusLabel(self, pvname, alignment=Qt.AlignCenter)
        self.lb_injmode.setStyleSheet('QLabel{font-size: 45pt;}')
        topupwids = list()

        self.ld_tunxt = QLabel(
            '<h3>Next Inj.: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_tunxt = SiriusLabel(
            self, injctrl_dev.substitute(propty='TopUpNextInj-Mon'))
        self.lb_tunxt.displayFormat = SiriusLabel.DisplayFormat.Time
        self.lb_tunxt.setAlignment(Qt.AlignCenter)
        self.lb_tunxt.setStyleSheet('QLabel{font-size: 45pt;}')
        box_tunxt = QWidget()
        lay_tunxt = QVBoxLayout(box_tunxt)
        lay_tunxt.setContentsMargins(0, 0, 0, 0)
        lay_tunxt.addWidget(self.ld_tunxt)
        lay_tunxt.addWidget(self.lb_tunxt)
        topupwids.append(box_tunxt)

        self.ld_tusts = QLabel(
            '<h3>Status: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_tusts = SiriusLabel(
            self, injctrl_dev.substitute(propty='TopUpState-Sts'))
        self.lb_tusts.setAlignment(Qt.AlignCenter)
        self.lb_tusts.setStyleSheet('QLabel{font-size: 45pt;}')
        box_tusts = QWidget()
        lay_tusts = QVBoxLayout(box_tusts)
        lay_tusts.setContentsMargins(0, 0, 0, 0)
        lay_tusts.addWidget(self.ld_tusts)
        lay_tusts.addWidget(self.lb_tusts)
        topupwids.append(box_tusts)

        self.ld_tuperd = QLabel(
            '<h3>Period: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_tuperd = SiriusLabel(
            self, injctrl_dev.substitute(propty='TopUpPeriod-RB'),
            keep_unit=True, alignment=Qt.AlignCenter)
        self.lb_tuperd.showUnits = True
        self.lb_tuperd.setStyleSheet('QLabel{font-size: 45pt;}')
        box_tuperd = QWidget()
        lay_tuperd = QVBoxLayout(box_tuperd)
        lay_tuperd.setContentsMargins(0, 0, 0, 0)
        lay_tuperd.addWidget(self.ld_tuperd)
        lay_tuperd.addWidget(self.lb_tuperd)
        topupwids.append(box_tuperd)

        self.ld_tunrpu = QLabel(
            '<h3>Nr.Pulses: </h3>', self, alignment=Qt.AlignCenter)
        self.lb_tunrpu = SiriusLabel(
            self, injctrl_dev.substitute(propty='TopUpNrPulses-RB'),
            alignment=Qt.AlignCenter)
        self.lb_tunrpu.showUnits = True
        self.lb_tunrpu.setStyleSheet('QLabel{font-size: 45pt;}')
        box_tunrpu = QWidget()
        lay_tunrpu = QVBoxLayout(box_tunrpu)
        lay_tunrpu.setContentsMargins(0, 0, 0, 0)
        lay_tunrpu.addWidget(self.ld_tunrpu)
        lay_tunrpu.addWidget(self.lb_tunrpu)
        topupwids.append(box_tunrpu)

        self._gbox_topup = self._create_groupbox(
            'Top-up status', topupwids, orientation='H')
        self._gbox_topup.setVisible(False)
        self.ch_injmode = SiriusConnectionSignal(pvname)
        self.ch_injmode.new_value_signal[int].connect(
            self._handle_injmode_settings_vis)

        box_macsts = QGridLayout()
        box_macsts.addWidget(self.ld_machsht, 0, 0)
        box_macsts.addWidget(self.lb_machsht, 1, 0)
        box_macsts.addWidget(self.ld_injmode, 0, 1)
        box_macsts.addWidget(self.lb_injmode, 1, 1)

        # interlock
        pvname = _PVName('RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon')
        pvname = pvname.substitute(prefix=self.prefix)
        self._led_siriusintlk = SiriusLedAlert(self, pvname)
        self._led_siriusintlk.setStyleSheet(
            'QLed{min-width:3em;min-height:3em;max-width:3em;max-height:3em;}')
        self._gbox_siriusintlk = self._create_groupbox(
            'Sirius Interlock', self._led_siriusintlk)

        # injection system
        self._led_injsyssts = InjSysStbyLed(self)
        self._led_injsyssts.setStyleSheet(
            'QLed{min-width:3em;min-height:3em;max-width:3em;max-height:3em;}')
        self._gbox_injsyssts = self._create_groupbox(
            'Injection System', self._led_injsyssts)

        # SI SOFB
        pvname = _PVName('SI-Glob:AP-SOFB:LoopState-Sts')
        pvname = pvname.substitute(prefix=self.prefix)
        self._led_sofbloop = SiriusLedState(self, pvname)
        self._led_sofbloop.setStyleSheet(
            'QLed{min-width:3em;min-height:3em;max-width:3em;max-height:3em;}')
        self._led_sofbloop.offColor = SiriusLedState.Red
        self._gbox_sofbloop = self._create_groupbox(
            'SOFB', self._led_sofbloop)

        # FOFB
        pvname = _PVName('SI-Glob:AP-FOFB:LoopState-Sts')
        pvname = pvname.substitute(prefix=self.prefix)
        self._led_fofbloop = SiriusLedState(self, pvname)
        self._led_fofbloop.setStyleSheet(
            'QLed{min-width:3em;min-height:3em;max-width:3em;max-height:3em;}')
        self._led_fofbloop.offColor = SiriusLedState.Red
        self._gbox_fofbloop = self._create_groupbox(
            'FOFB', self._led_fofbloop)

        # BbB
        ledsbbb = list()
        for axis in ['H', 'V', 'L']:
            bbb_pref = _PVName('SI-Glob:DI-BbBProc-'+axis)
            bbb_pref = bbb_pref.substitute(prefix=self.prefix)
            stab_pref = _PVName('SI-Glob:AP-StabilityInfo')
            chs2vals = {
                bbb_pref.substitute(propty_name='FBCTRL'): 1,
                bbb_pref.substitute(propty_name='CLKMISS'): 0,
                bbb_pref.substitute(propty_name='PLL_UNLOCK'): 0,
                bbb_pref.substitute(propty_name='DCM_UNLOCK'): 0,
                bbb_pref.substitute(propty_name='ADC_OVR'): 0,
                bbb_pref.substitute(propty_name='SAT'): 0,
                bbb_pref.substitute(propty_name='FID_ERR'): 0,
                stab_pref.substitute(propty='BbB'+axis+'Status-Mon'): 0,
            }
            led = PyDMLedMultiChannel(self, chs2vals)
            led.setStyleSheet(
                'QLed{min-width:3em;min-height:3em;'
                'max-width:3em;max-height:3em;}')
            led.offColor = SiriusLedState.Red
            ledsbbb.append(led)
        self._gbox_bbbloop = self._create_groupbox(
            'BbB', ledsbbb, orientation='H')

        # current
        self.ld_curr = QLabel(
            '<h3>Current [mA]</h3>', self, alignment=Qt.AlignCenter)
        self.ld_curr.setStyleSheet('max-height: 2em;')
        pvname = _PVName('SI-Glob:AP-CurrInfo:Current-Mon')
        pvname = pvname.substitute(prefix=self.prefix)
        self.lb_curr = SiriusLabel(self, pvname)
        self.lb_curr.setAlignment(Qt.AlignCenter)
        self.lb_curr.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';font-size: 45pt;}')
        pvname = _PVName('SI-Glob:AP-CurrInfo:StoredEBeam-Mon')
        pvname = pvname.substitute(prefix=self.prefix)
        self.frm_curr = SiriusFrame(
            self, pvname,
            color_list=[SiriusFrame.DarkGreen, SiriusFrame.LightGreen],
            is_float=False)
        self.frm_curr.borderWidth = 5
        self.frm_curr.add_widget(self.lb_curr)
        box_curr = QWidget()
        lay_curr = QVBoxLayout(box_curr)
        lay_curr.setAlignment(Qt.AlignVCenter)
        lay_curr.addWidget(self.ld_curr)
        lay_curr.addWidget(self.frm_curr)

        # lifetime
        self.ld_lifetime = QLabel(
            '<h3>Lifetime</h3>', self, alignment=Qt.AlignCenter)
        self.ld_lifetime.setStyleSheet('max-height: 2em;')
        self.lb_lifetime = QLabel('0:00:00', self, alignment=Qt.AlignCenter)
        self.lb_lifetime.setStyleSheet('QLabel{font-size: 45pt;}')
        pvname = _PVName('SI-Glob:AP-CurrInfo:Lifetime-Mon')
        pvname = pvname.substitute(prefix=self.prefix)
        self.ch_lifetime = SiriusConnectionSignal(pvname)
        self.ch_lifetime.new_value_signal[float].connect(
            self.formatLifetimeLabel)
        box_lt = QWidget()
        lay_lt = QVBoxLayout(box_lt)
        lay_lt.setAlignment(Qt.AlignVCenter)
        lay_lt.addWidget(self.ld_lifetime)
        lay_lt.addWidget(self.lb_lifetime)

        # tune
        self.tune_mon = SITuneMonitor(self, self.prefix, description='short',
                                      use_color_labels=False)
        self.tune_mon.lb_tunefrach.setStyleSheet('QLabel{font-size: 45pt;}')
        self.tune_mon.lb_tunefracv.setStyleSheet('QLabel{font-size: 45pt;}')

        # current history
        self.curr_graph = SiriusTimePlot(self)
        self.curr_graph.setObjectName('curr_graph')
        self.curr_graph.setStyleSheet(
            '#curr_graph{min-width: 20em; min-height: 14em;}')
        self.curr_graph.showXGrid = True
        self.curr_graph.showYGrid = True
        self.curr_graph.backgroundColor = QColor(255, 255, 255)
        for axis in self.curr_graph.getPlotItem().axes.values():
            sty = axis['item'].labelStyle
            sty['font-size'] = '18pt'
            axis['item'].setLabel(text=None, **sty)
        self.curr_graph.setLabel('left', text='Current [mA]')
        font = QFont()
        font.setPointSize(18)
        self.curr_graph.plotItem.getAxis('bottom').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=50, tickFont=font)
        self.curr_graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False,
            tickTextWidth=50, tickFont=font)
        curr_pvname = _PVName('SI-Glob:AP-CurrInfo:Current-Mon')
        curr_pvname = curr_pvname.substitute(prefix=self.prefix)
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
        hlay2.addWidget(self._gbox_fofbloop)
        hlay2.addWidget(self._gbox_bbbloop)
        hlay2.setStretch(0, 1)
        hlay2.setStretch(1, 1)
        hlay2.setStretch(2, 1)
        hlay2.setStretch(3, 1)
        hlay2.setStretch(4, 1)

        cwid = QWidget()
        lay = QGridLayout(cwid)
        lay.setVerticalSpacing(16)
        lay.setHorizontalSpacing(14)
        lay.addLayout(box_macsts, 0, 0, 1, 3)
        lay.addLayout(hlay1, 1, 0, 1, 3)
        lay.addWidget(self.curr_graph, 2, 0, 1, 3)
        lay.addLayout(hlay2, 3, 0, 1, 3)
        lay.addWidget(self._gbox_topup, 4, 0, 1, 3)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 1)
        lay.setRowStretch(2, 5)
        lay.setRowStretch(3, 1)
        lay.setRowStretch(4, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 1)
        self.setCentralWidget(cwid)

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
        for idx, wid in enumerate(widgets):
            lay.addWidget(wid)
            lay.setStretch(idx, 1)
        return gbox

    def _handle_injmode_settings_vis(self, value):
        self._gbox_topup.setVisible(value == _InjConst.InjMode.TopUp)

    def changeEvent(self, event):
        """Change event handler."""
        if event.type() == QEvent.FontChange:
            fontsize = self.app.font().pointSize()

            # labels
            sty = 'QLabel{font-size: '+str(fontsize+35)+'pt;}'
            self.lb_machsht.label.setStyleSheet(sty)
            self.lb_injmode.setStyleSheet(sty)
            self.lb_curr.setStyleSheet(
                'QLabel{background-color: '+self.app_color+';'
                'font-size: '+str(fontsize+35)+'pt;}')
            self.lb_lifetime.setStyleSheet(sty)
            self.tune_mon.lb_tunefrach.setStyleSheet(sty)
            self.tune_mon.lb_tunefracv.setStyleSheet(sty)
            self.lb_tunxt.setStyleSheet(sty)
            self.lb_tusts.setStyleSheet(sty)
            self.lb_tuperd.setStyleSheet(sty)
            self.lb_tunrpu.setStyleSheet(sty)

            sty = 'QGroupBox{font-size: '+str(fontsize+2)+'pt;'+\
                'font-weight: bold;}'
            self._gbox_siriusintlk.setStyleSheet(sty)
            self._gbox_injsyssts.setStyleSheet(sty)
            self._gbox_sofbloop.setStyleSheet(sty)
            self._gbox_fofbloop.setStyleSheet(sty)
            self._gbox_bbbloop.setStyleSheet(sty)
            self._gbox_topup.setStyleSheet(sty)

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
