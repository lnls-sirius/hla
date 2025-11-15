"""Main window."""

from time import strftime, localtime

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QGridLayout, QSizePolicy as QSzPlcy, \
    QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, \
    QRadioButton, QButtonGroup, QStackedWidget
from qtpy.QtGui import QColor

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.devices import IDFF, IDFFCtrl, IDFFCtrlSoft
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import IDSearch
from siriuspy.idff.csdev import ETypes as IDFFEnums

from ..util import connect_window
from ..widgets import SiriusMainWindow, SiriusLabel, SiriusSpinbox, \
    PyDMStateButton, SiriusLedState, PyDMLogLabel, SiriusLedAlert, \
    SiriusConnectionSignal, SiriusWaveformPlot
from ..widgets.dialog import StatusDetailDialog
from ..as_ps_control.control_widget.ControlWidgetFactory import \
    ControlWidgetFactory
from ..as_ps_control import PSDetailWindow
from .custom_widgets import ConfigLineEdit, SectionedWaveformCurveItem
from .util import get_idff_icon


class IDFFWindow(SiriusMainWindow):
    """ID FF main window."""

    # NOTE: in order to simplify this HLA class we could try to either
    # a) implement low level FF for DELTA52 or ...
    # b) change its soft FF IOC
    #    so as to provide the same PVs as the low level ioc (particularly
    #    "IDPos-Mon")

    def __init__(self, parent=None, prefix='', idname=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix or _VACA_PREFIX
        self.idname = _PVName(idname)
        self._is_llidff = self.idname.dev.startswith(("IVU", "VPU"))
        if self._is_llidff and self.idname.dev.startswith("IVU"):
            self._idffname = _PVName(f"SI-{self.idname.sub}:BS-IDFF-CHCV")
        elif self._is_llidff and self.idname.dev.startswith("VPU"):
            self._idffname = _PVName(f"SI-{self.idname.sub}:BS-IDFF-CC")
        else:
            self._idffname = _PVName(f"SI-{self.idname.sub}:AP-IDFF")
        self.dev_pref = _PVName(self._idffname + ':')
        # self._idffname = IDFFConst(idname).idffname
        self._idffdev = self._create_idffdev()
        self._idffdata = IDSearch.conv_idname_2_idff(self.idname)
        self.device = _PVName(self._idffname)
        self.setObjectName('IDApp')
        self.setWindowTitle(self.device)
        self.setWindowIcon(get_idff_icon())
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.title = QLabel(
            '<h2>' + self.idname + ' Feedforward Settings</h2>',
            alignment=Qt.AlignCenter)
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        if self._is_llidff:
            corrs = list()
            corrs += self._idffdev.ctrldev.IDFF_CH_LABELS
            corrs += self._idffdev.ctrldev.IDFF_CV_LABELS
            corrs += self._idffdev.ctrldev.IDFF_CC_LABELS
            lay.addWidget(self._llStatusWidget(), 1, 0, 1, 1)
            lay.addWidget(self._llSettingsWidget(corrs), 2, 0, 3, 1)
        else:
            lay.addWidget(self._idStatusWidget(), 1, 0)
            lay.addWidget(self._corrStatusWidget(), 2, 0)
            lay.addWidget(self._basicSettingsWidget(), 3, 0)
            lay.addWidget(self._logWidget(), 4, 0)
        lay.addWidget(self._corrsMonitorWidget(), 1, 1, 4, 1)
        self.setCentralWidget(wid)

    def _llStatusWidget(self):
        gbox = QGroupBox('ID Status', self)
        hlay = QHBoxLayout(gbox)

        lbl_gap = QLabel(
            'Gap: ', self)
        gap_val = SiriusLabel(
            self, self.dev_pref.substitute(propty='IDPos-Mon'))
        gap_val.showUnits = True

        hlay.addWidget(lbl_gap)
        hlay.addWidget(gap_val)

        return gbox

    def _format_timestamp_label(self, value):
        self.timestamp.setText(strftime(
            '%Y-%m-%d %H:%M:%S', localtime(value/1000)))

    def _llSettingsWidget(self, corrs):
        gbox = QGroupBox('Settings', self)
        lay = QGridLayout(gbox)

        ld_loopstate = QLabel('Loop State: ', self)
        self.sb_loopstate = PyDMStateButton(
            self, self.dev_pref.substitute(propty='LoopState-Sel'))
        self.lb_loopstate = SiriusLedState(
            self, self.dev_pref.substitute(propty='LoopState-Sts'))

        lbl_table_pointer = QLabel('Table Pointer: ', self)
        self.table_pointer = SiriusLabel(
            self, self.dev_pref.substitute(propty='TablePointer-Mon'))

        lbl_alarm = QLabel('Alarm: ', self)
        self.alarm_led = SiriusLedState(
            self, self.dev_pref.substitute(propty='Alarms-Mon'))

        alarm_details = QPushButton('', self)
        alarm_details.setIcon(qta.icon('fa5s.list-ul'))
        alarm_details.setToolTip('Open Detailed Alarms View')
        alarm_details.setObjectName('sts')
        alarm_details.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        connect_window(
            alarm_details, StatusDetailDialog, parent=self,
            pvname=self.dev_pref.substitute(propty='Alarms-Mon'),
            labels=["Mode/Polar. out of range", "Gap/phase out of range",
                "Gap/phase high deviation", "Timeout for serial data"],
            section='ID', title='FeedForward Status')

        self.clear_alarms = PyDMPushButton(
            self, "Clear Alarms", pressValue=1,
            init_channel=self.dev_pref.substitute(propty='ClearFlags-Cmd'))

        lbl_plc_counter = QLabel('PLC Counter: ', self)
        self.plc_counter = SiriusLabel(
            self, self.dev_pref.substitute(propty='PLCCounter-Mon'))

        lbl_timestamp = QLabel('PLC Timestamp: ', self)
        self.timestamp = QLabel('0:00:00', self)
        self.timestamp_mon = SiriusConnectionSignal(
            self.dev_pref.substitute(propty='PLCTimestamp-Mon'))
        self.timestamp_mon.new_value_signal[float].connect(
            self._format_timestamp_label)

        buttonGroupWid = QWidget()
        vlay = QVBoxLayout(buttonGroupWid)
        self.button_group = QButtonGroup(buttonGroupWid)
        self.button_group.buttonClicked.connect(lambda btn: self.stack.setCurrentIndex(self.button_group.id(btn)))

        self.stack = QStackedWidget()
        self.plot_dict = {}
        for idx, name in enumerate(corrs):
            channel_btn = QRadioButton(name)
            vlay.addWidget(channel_btn)
            self.button_group.addButton(channel_btn, idx)

            if idx == 0:
                channel_btn.setChecked(True)

            graph = SiriusWaveformPlot()
            graph.setShowLegend(True)
            graph.autoRangeX = True
            graph.autoRangeY = True
            graph.showXGrid = True
            graph.showYGrid = True
            graph.showLegend = True
            graph.setLabel('bottom', text='Index')
            graph.setLabel('left', text='Current [A]')
            graph.setBackgroundColor(QColor(255, 255, 255))
            self._addNewTableCurve(graph, name, idx)
            self.stack.addWidget(graph)
            self.plot_dict[name] = graph

        self.lb_rampcorr = QLabel('Ramp Corr: ', self)
        self.btn_rampcorr = QPushButton('', self)
        self.btn_rampcorr.clicked.connect(
            lambda: self._ramp_corr())
        self.btn_rampcorr.setIcon(qta.icon(
            'mdi.escalator', scale_factor=1.5
        ))
        self.btn_rampcorr.setToolTip('Ramp correctors to correct values')
        self.btn_rampcorr.setObjectName('rmpbtn')
        self.btn_rampcorr.setStyleSheet(
            '#rmpbtn{min-width:25px; max-width:25px; icon-size:20px;}')

        lay.addWidget(ld_loopstate, 0, 0)
        lay.addWidget(self.sb_loopstate, 0, 1)
        lay.addWidget(self.lb_loopstate, 0, 2)
        lay.addWidget(lbl_table_pointer, 1, 0)
        lay.addWidget(self.table_pointer, 1, 1, 1, 2)
        lay.addWidget(lbl_alarm, 2, 0)
        lay.addWidget(self.alarm_led, 2, 1)
        lay.addWidget(alarm_details, 2, 2)
        lay.addWidget(self.clear_alarms, 3, 0, 1, 3)
        lay.addWidget(lbl_plc_counter, 4, 0)
        lay.addWidget(self.plc_counter, 4, 1, 1, 2)
        lay.addWidget(lbl_timestamp, 5, 0)
        lay.addWidget(self.timestamp, 5, 1, 1, 2)
        lay.addWidget(buttonGroupWid, 6, 0)
        lay.addWidget(self.stack, 6, 1, 1, 2)
        lay.addWidget(self.lb_rampcorr, 7, 0)
        lay.addWidget(self.btn_rampcorr, 7, 1, alignment=Qt.AlignHCenter)

        return gbox

    def _addNewTableCurve(self, plt, name, section):
        if "ch" in name:
            color_sp, color_rb = 'blue', 'darkBlue'
        elif "cv" in name:
            color_sp, color_rb = 'red', 'darkRed'
        else:
            color_sp, color_rb = 'green', 'darkGreen'

        curve_sp = SectionedWaveformCurveItem(
            section=section,
            y_addr=self.dev_pref.substitute(propty='Table-SP'),
            name="SP",
            color=QColor(color_sp),
        )
        plt._needs_redraw = False
        plt.addCurve(curve_sp, curve_color=QColor(color_sp))
        curve_sp.data_changed.connect(plt.set_needs_redraw)

        curve_rb = SectionedWaveformCurveItem(
            section=section,
            y_addr=self.dev_pref.substitute(propty='Table-RB'),
            name="RB",
            color=QColor(color_rb),
        )
        plt._needs_redraw = False
        plt.addCurve(curve_rb, curve_color=QColor(color_rb))
        curve_rb.data_changed.connect(plt.set_needs_redraw)

        return plt

    def _basicSettingsWidget(self):
        ld_configname = QLabel(
            'Config. Name: ', self, alignment=Qt.AlignRight)
        self.le_configname = ConfigLineEdit(
            self, self.dev_pref.substitute(propty='ConfigName-SP'))
        self.le_configname.setStyleSheet('min-width:10em; max-width:10em;')
        self.lb_configname = SiriusLabel(
            self, self.dev_pref.substitute(propty='ConfigName-RB'))

        ld_loopstate = QLabel(
            'Loop State: ', self, alignment=Qt.AlignRight)
        self.sb_loopstate = PyDMStateButton(
            self, self.dev_pref.substitute(propty='LoopState-Sel'))
        self.lb_loopstate = SiriusLedState(
            self, self.dev_pref.substitute(propty='LoopState-Sts'))

        ld_loopfreq = QLabel(
            'Loop Freq.: ', self, alignment=Qt.AlignRight)
        self.sb_loopfreq = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='LoopFreq-SP'))
        self.lb_loopfreq = SiriusLabel(
            self, self.dev_pref.substitute(propty='LoopFreq-RB'))

        self.lb_rampcorr = QLabel('Ramp Corr: ', self)
        self.btn_rampcorr = QPushButton('', self)
        self.btn_rampcorr.clicked.connect(
            lambda: self._ramp_corr())
        self.btn_rampcorr.setIcon(qta.icon(
            'mdi.escalator', scale_factor=1.5
        ))
        self.btn_rampcorr.setToolTip('Ramp correctors to correct values')
        self.btn_rampcorr.setObjectName('rmpbtn')
        self.btn_rampcorr.setStyleSheet(
            '#rmpbtn{min-width:25px; max-width:25px; icon-size:20px;}')

        chnames = IDSearch.conv_idname_2_idff_chnames(self.idname)
        cvnames = IDSearch.conv_idname_2_idff_cvnames(self.idname)
        qsnames = IDSearch.conv_idname_2_idff_qsnames(self.idname)
        lcnames = IDSearch.conv_idname_2_idff_lcnames(self.idname)
        qnnames = IDSearch.conv_idname_2_idff_qnnames(self.idname)
        # ccnames = IDSearch.conv_idname_2_idff_ccnames(self.idname)

        ld_calccorr = QLabel(
            'Calc. values:', self, alignment=Qt.AlignRight)
        glay_calccorr = QGridLayout()
        glay_calccorr.addWidget(ld_calccorr, 0, 0)
        corr_fams = ['CH', 'CV', 'QS', 'LCH', 'QD1', 'QF', 'QD2', 'CC']
        for ridx, corr in enumerate(corr_fams):
            if corr == 'CH' and not chnames:
                continue
            if corr == 'CV' and not cvnames:
                continue
            if corr == 'QS' and not qsnames:
                continue
            if corr == 'LCH' and not lcnames:
                continue
            if corr in ('QD1', 'QF', 'QD2') and not qnnames:
                continue
            if corr == 'CC':
                continue
            # if corr == 'CC' and not ccnames:
            #     continue
            row = ridx + 1
            hheader = QLabel(f'{corr}', alignment=Qt.AlignCenter)
            hheader.setStyleSheet('.QLabel{font-weight: bold;}')
            glay_calccorr.addWidget(hheader, row, 0)
            for cidx in range(2):
                col = cidx + 1
                if ridx == 0:
                    vheader = QLabel(f'{col}', alignment=Qt.AlignCenter)
                    vheader.setStyleSheet('.QLabel{font-weight: bold;}')
                    glay_calccorr.addWidget(vheader, 0, col)
                propty = f'Corr{corr}_{col}Current-Mon'
                pvname = self.dev_pref.substitute(propty=propty)
                lbl = SiriusLabel(self, pvname, keep_unit=True)
                lbl.showUnits = True
                glay_calccorr.addWidget(lbl, row, col)


        gbox = QGroupBox('Settings', self)
        lay = QGridLayout(gbox)
        lay.addWidget(ld_loopstate, 0, 0)
        lay.addWidget(self.sb_loopstate, 0, 1)
        lay.addWidget(self.lb_loopstate, 0, 2)
        lay.addItem(QSpacerItem(0, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(ld_loopfreq, 2, 0)
        lay.addWidget(self.sb_loopfreq, 2, 1)
        lay.addWidget(self.lb_loopfreq, 2, 2, 1, 2)
        lay.addWidget(ld_configname, 3, 0)
        lay.addWidget(self.le_configname, 3, 1, 1, 3)
        lay.addWidget(self.lb_configname, 4, 1, 1, 3)
        lay.addItem(QSpacerItem(0, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 6, 0)

        row = 5

        if chnames:
            ld_controlch = QLabel(
                'Control CH: ', self, alignment=Qt.AlignRight)
            self.sb_controlch = PyDMStateButton(
                self, self.dev_pref.substitute(propty='ControlCH-Sel'))
            self.lb_controlch = SiriusLedState(
                self, self.dev_pref.substitute(propty='ControlCH-Sts'))
            lay.addWidget(ld_controlch, row, 0)
            lay.addWidget(self.sb_controlch, row, 1)
            lay.addWidget(self.lb_controlch, row, 2)
            row += 1

        if cvnames:
            ld_controlcv = QLabel(
                'Control CV: ', self, alignment=Qt.AlignRight)
            self.sb_controlcv = PyDMStateButton(
                self, self.dev_pref.substitute(propty='ControlCV-Sel'))
            self.lb_controlcv = SiriusLedState(
                self, self.dev_pref.substitute(propty='ControlCV-Sts'))
            lay.addWidget(ld_controlcv, row, 0)
            lay.addWidget(self.sb_controlcv, row, 1)
            lay.addWidget(self.lb_controlcv, row, 2)
            row += 1

        if qsnames:
            ld_controlqs = QLabel(
                'Control QS: ', self, alignment=Qt.AlignRight)
            self.sb_controlqs = PyDMStateButton(
                self, self.dev_pref.substitute(propty='ControlQS-Sel'))
            self.lb_controlqs = SiriusLedState(
                self, self.dev_pref.substitute(propty='ControlQS-Sts'))
            lay.addWidget(ld_controlqs, row, 0)
            lay.addWidget(self.sb_controlqs, row, 1)
            lay.addWidget(self.lb_controlqs, row, 2)
            row += 1

        if lcnames:
            ld_controllc = QLabel(
                'Control LC: ', self, alignment=Qt.AlignRight)
            self.sb_controllc = PyDMStateButton(
                self, self.dev_pref.substitute(propty='ControlLC-Sel'))
            self.lb_controllc = SiriusLedState(
                self, self.dev_pref.substitute(propty='ControlLC-Sts'))
            lay.addWidget(ld_controllc, row, 0)
            lay.addWidget(self.sb_controllc, row, 1)
            lay.addWidget(self.lb_controllc, row, 2)
            row += 1

        if qnnames:
            ld_controlqn = QLabel(
                'Control QN: ', self, alignment=Qt.AlignRight)
            self.sb_controlqn = PyDMStateButton(
                self, self.dev_pref.substitute(propty='ControlQN-Sel'))
            self.lb_controlqn = SiriusLedState(
                self, self.dev_pref.substitute(propty='ControlQN-Sts'))
            lay.addWidget(ld_controlqn, row, 0)
            lay.addWidget(self.sb_controlqn, row, 1)
            lay.addWidget(self.lb_controlqn, row, 2)
            row += 1

        # if ccnames:
        #     ld_controlcc = QLabel(
        #         'Control CC: ', self, alignment=Qt.AlignRight)
        #     self.sb_controlcc = PyDMStateButton(
        #         self, self.dev_pref.substitute(propty='ControlCC-Sel'))
        #     self.lb_controlcc = SiriusLedState(
        #         self, self.dev_pref.substitute(propty='ControlCC-Sts'))
        #     lay.addWidget(ld_controlcc, row, 0)
        #     lay.addWidget(self.sb_controlcc, row, 1)
        #     lay.addWidget(self.lb_controlcc, row, 2)
        #     row += 1

        lay.addLayout(glay_calccorr, row, 0, 1, 3)
        row += 1
        lay.addWidget(self.lb_rampcorr, row, 0, alignment=Qt.AlignHCenter)
        lay.addWidget(self.btn_rampcorr, row, 1, alignment=Qt.AlignHCenter)

        return gbox

    def _corrStatusWidget(self):
        ld_corconf = QLabel(
            'Corr. Status: ', self, alignment=Qt.AlignRight)
        self.led_corr = SiriusLedAlert(
            self, self.dev_pref.substitute(propty='CorrStatus-Mon'))
        pb_corsts = QPushButton('', self)
        pb_corsts.setIcon(qta.icon('fa5s.list-ul'))
        pb_corsts.setToolTip('Open Detailed Status View')
        pb_corsts.setObjectName('sts')
        pb_corsts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        connect_window(
            pb_corsts, StatusDetailDialog, parent=self,
            pvname=self.dev_pref.substitute(propty='CorrStatus-Mon'),
            labels=IDFFEnums.STS_LBLS_CORR, section='ID',
            title='Corrector Status')
        self.pb_corconf = PyDMPushButton(
            self, pressValue=1,
            init_channel=self.dev_pref.substitute(propty='CorrConfig-Cmd'))
        self.pb_corconf.setToolTip('Send PwrState and OpMode')
        self.pb_corconf.setIcon(qta.icon('fa5s.sync'))
        self.pb_corconf.setObjectName('conf')
        self.pb_corconf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        gbox = QGroupBox('Corrector Status', self)
        lay = QGridLayout(gbox)
        lay.addWidget(ld_corconf, 0, 0)
        lay.addWidget(self.led_corr, 0, 1)
        lay.addWidget(pb_corsts, 0, 2)
        lay.addWidget(self.pb_corconf, 0, 3)
        return gbox

    def _idStatusWidget(self):
        gbox = QGroupBox('ID Status', self)
        lay = QGridLayout(gbox)

        if self._idffdata['pparameter']:
            pparam = _PVName(self._idffdata['pparameter'])
            ld_pparam = QLabel(
                pparam.propty_name + ': ', self, alignment=Qt.AlignRight)
            self._lb_pparam = SiriusLabel(self, pparam, keep_unit=True)
            self._lb_pparam.showUnits = True
            lay.addWidget(ld_pparam, 0, 0)
            lay.addWidget(self._lb_pparam, 0, 1)

        if self._idffdata['kparameter']:
            kparam = _PVName(self._idffdata['kparameter'])
            ld_kparam = QLabel(
                kparam.propty_name + ': ', self, alignment=Qt.AlignRight)
            self._lb_kparam = SiriusLabel(self, kparam, keep_unit=True)
            self._lb_kparam.showUnits = True
            lay.addWidget(ld_kparam, 1, 0)
            lay.addWidget(self._lb_kparam, 1, 1)

        ld_polar = QLabel(
            'Polarization: ', self, alignment=Qt.AlignRight)
        self.lb_polar = SiriusLabel(
            self, self.dev_pref.substitute(propty='Polarization-Mon'))
        lay.addItem(QSpacerItem(0, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)
        lay.addWidget(ld_polar, 3, 0)
        lay.addWidget(self.lb_polar, 3, 1, 1, 3)

        return gbox

    def _logWidget(self):
        self.log = PyDMLogLabel(
            self, init_channel=self.dev_pref.substitute(propty='Log-Mon'))
        self.log.setSizePolicy(
            QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding)
        self.log.setAlternatingRowColors(True)
        self.log.maxCount = 2000

        gbox = QGroupBox('Log', self)
        lay = QVBoxLayout(gbox)
        lay.addWidget(self.log)
        return gbox

    def _corrsMonitorWidget(self):
        widget = ControlWidgetFactory.factory(
            self, section='SI', device='corrector-idff',
            subsection=self.device.sub, orientation=Qt.Vertical)
        for wid in widget.get_summary_widgets():
            detail_bt = wid.get_detail_button()
            psname = detail_bt.text()
            if not psname:
                psname = detail_bt.toolTip()
            connect_window(detail_bt, PSDetailWindow, self, psname=psname)

        gbox = QGroupBox('Correctors', self)
        lay = QVBoxLayout(gbox)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.addWidget(widget)
        return gbox

    def _create_idffdev(self):
        idffclass = IDFFCtrl.get_idffclass(self._idffname)
        props2init_ctrl = ('LoopState-Sts', )
        # PVNames to initialize depend whether a soft or hard IDFF
        if issubclass(idffclass, IDFFCtrlSoft):
            props2init_ctrl += ('ConfigName-RB',)
        else:
            props2init_ctrl += ('Table-RB',)
        props2init_corrs = ('Current-Mon', 'Current-SP',)
        idffdev = IDFF(
            self._idffname,
            props2init_ctrl=props2init_ctrl,
            props2init_corrs=props2init_corrs
        )
        return idffdev

    def _ramp_corr(self):
        # NOTE:
        # 1 - implement this ramp as a separate thread
        # 2 - add a time icon to indicate when this therad is running
        # 3 - add 'nrpts' and 'time_interval' parameters as edit widgets
        devctrl = self._idffdev.ctrldev
        if not devctrl.loopstate:
            # if softidff first must guarantee a config is loaded
            # from clientconfig
            is_soft = isinstance(devctrl, IDFFCtrlSoft)
            if is_soft:
                configname = devctrl.configname
                if configname != self._idffdev.idffconfig.name:
                    self._idffdev.load_config(configname)
            # run correctors' ramp
            self._idffdev.rampup_corr_currents(
                nrpts=50, time_interval=10, dry_run=False)
        else:
            # NOTE: lauunch a popup warning window...
            pass
