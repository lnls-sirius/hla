"""OpticsCorr main module."""

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QLabel,
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy as QSzPly,
    QHBoxLayout,
    QTabWidget,
    QDockWidget,
    QMenuBar,
    QMenu,
    QAction,
)
from pyqtgraph import InfiniteLine as _InfLine, mkPen as _Pen
import qtawesome as qta
from pydm.widgets import PyDMPushButton, PyDMEnumComboBox, PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.opticscorr.csdev import Const as _Const
from siriuspy.epics import PV as _PV

from siriushla import util as _hlautil
from siriushla.widgets import (
    SiriusMainWindow,
    PyDMLogLabel,
    SiriusSpinbox,
    PyDMStateButton,
    SiriusLabel,
    SiriusLedState,
    SiriusConnectionSignal,
    SiriusWaveformPlot,
)
from siriushla.as_ps_control import PSDetailWindow as _PSDetailWindow
from .details import CorrParamsDetailWindow as _CorrParamsDetailWindow
from .custom_widgets import (
    StatusLed as _StatusLed,
    ConfigLineEdit as _ConfigLineEdit,
)

from siriushla.as_di_tune import Tune as _TuneWindow
from siriushla.si_di_bbb import BbBControlWindow as _BbBWindow


class OpticsCorrWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(OpticsCorrWindow, self).__init__(parent)
        self.prefix = prefix
        self.acc = acc.upper()
        self.param = opticsparam
        self.ioc_prefix = _PVName(
            self.acc + "-Glob:AP-" + self.param.title() + "Corr"
        )
        self.ioc_prefix = self.ioc_prefix.substitute(prefix=self.prefix)
        self.title = self.acc + " " + self.param.title() + " Correction"

        if self.param == "tune":
            self.param_pv = "DeltaTune{0}-{1}"
            self.intstrength = "KL"
            self.intstrength_calcdesc = "DeltaKL-Mon"
            self.intstrength_calcpv = "DeltaKL{}-Mon"
            self.fams = (
                list(_Const.SI_QFAMS_TUNECORR)
                if self.acc == "SI"
                else list(_Const.BO_QFAMS_TUNECORR)
            )
        elif self.param == "chrom":
            self.param_pv = "Chrom{0}-{1}"
            self.intstrength = "SL"
            self.intstrength_calcdesc = "CalcSL-Mon"
            self.intstrength_calcpv = "SL{}-Mon"
            self.fams = (
                list(_Const.SI_SFAMS_CHROMCORR)
                if self.acc == "SI"
                else list(_Const.BO_SFAMS_CHROMCORR)
            )

        self.setWindowTitle(self.title)
        self.setObjectName(self.acc + "App")
        self._setupui()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupui(self):
        label = QLabel("<h3>" + self.title + "</h3>", self)
        label.setStyleSheet("""
            min-height:1.55em; max-height: 1.55em;
            qproperty-alignment: 'AlignVCenter | AlignRight';
            background-color: qlineargradient(spread:pad, x1:1, y1:0.0227273,
                              x2:0, y2:0, stop:0 rgba(173, 190, 207, 255),
                              stop:1 rgba(213, 213, 213, 255));""")

        self.gb_status = QGroupBox("Status", self)
        self.gb_status.setLayout(self._setup_status_layout())

        self.wid_optics = QWidget()
        lay_optics = QGridLayout(self.wid_optics)
        lay_optics.setContentsMargins(0, 0, 0, 0)
        self.gb_optprm = QGroupBox(
            "ΔTune" if self.param == "tune" else "Chromaticity", self
        )
        self.gb_optprm.setLayout(self._setup_optics_param_layout())
        if self.param == "tune":
            self.pb_updref = PyDMPushButton(
                self,
                label="Update Reference",
                pressValue=1,
                init_channel=self.ioc_prefix.substitute(
                    propty="SetNewRefKL-Cmd"
                ),
            )
            if self.acc == "SI":
                self.pb_updref.setStyleSheet(
                    "min-height:2.4em; max-height:2.4em; margin-top:1em;"
                )
                self.gb_digmon = QGroupBox("Tune Monitor", self)
                self.gb_digmon.setLayout(self._setup_digmon_layout())
                self.gb_corr = QGroupBox("Correction", self)
                self.gb_corr.setLayout(self._setup_correction_layout())
            else:
                self.pb_updref.setStyleSheet(
                    "min-height:2.4em; max-height:2.4em;"
                )
                lay_optics.addWidget(self.pb_updref, 0, 0, 1, 2)
                lay_optics.addWidget(self.gb_optprm, 1, 0)
        else:
            lay_optics.addWidget(self.gb_optprm, 0, 0)

        self.gb_fams = QGroupBox("Families", self)
        self.gb_fams.setLayout(self._setup_families_layout())
        self.gb_fams.setSizePolicy(QSzPly.Preferred, QSzPly.Expanding)

        self.gb_iocctrl = QGroupBox("IOC Control", self)
        self.gb_iocctrl.setLayout(self._setup_ioc_control_layout())

        cwt = QWidget()
        self.setCentralWidget(cwt)
        if self.acc == "SI":

            def vbox(*ws):
                _lay = QVBoxLayout()
                _lay.setAlignment(Qt.AlignTop)
                for w in ws:
                    _lay.addWidget(w)
                return _lay

            lay = QGridLayout(cwt)
            if self.param == "tune":
                lay.addWidget(label, 0, 0, 1, 3)
                lay.addLayout(vbox(self.gb_status, self.gb_fams), 1, 0)
                lay.addWidget(self.gb_iocctrl, 1, 1)
                lay.addLayout(vbox(self.gb_digmon, self.gb_corr), 1, 2)
                lay.setColumnStretch(2, 1)
            else:
                lay.addWidget(label, 0, 0, 1, 2)
                lay.addLayout(vbox(self.wid_optics, self.gb_fams), 1, 0)
                lay.addWidget(self.gb_iocctrl, 1, 1)
                lay.addWidget(self.gb_status, 2, 0, 1, 2)
                lay.setRowStretch(2, 5)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
            lay.setRowStretch(0, 1)
            lay.setRowStretch(1, 15)
        else:
            lay = QVBoxLayout(cwt)
            lay.addWidget(label)
            lay.addWidget(self.wid_optics)
            lay.addWidget(self.gb_fams)
            lay.addWidget(self.gb_iocctrl)
            lay.addWidget(self.gb_status)

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignCenter;
            }""")

    def _setup_status_layout(self):
        self.log_label = PyDMLogLabel(
            self, self.ioc_prefix.substitute(propty="Log-Mon")
        )

        lay = QVBoxLayout()
        lay.addWidget(self.log_label)
        return lay

    def _setup_optics_param_layout(self):
        self.lb_x = QLabel("<h4>X</h4>", self, alignment=Qt.AlignCenter)
        self.lb_y = QLabel("<h4>Y</h4>", self, alignment=Qt.AlignCenter)
        self.lb_sp = QLabel("<h4>SP</h4>", self, alignment=Qt.AlignCenter)
        self.lb_rb = QLabel("<h4>RB</h4>", self, alignment=Qt.AlignCenter)
        self.lb_mon = QLabel(
            "<h4>Estimative</h4>", self, alignment=Qt.AlignCenter
        )

        self.sb_paramx = SiriusSpinbox(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("X", "SP")),
        )
        self.sb_paramx.setSingleStep(0.001)
        self.sb_paramy = SiriusSpinbox(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("Y", "SP")),
        )
        self.sb_paramy.setSingleStep(0.001)

        self.lb_paramx = SiriusLabel(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("X", "RB")),
        )
        self.lb_paramy = SiriusLabel(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("Y", "RB")),
        )

        self.lb_prmmonx = SiriusLabel(
            self,
            self.ioc_prefix.substitute(
                propty=self.param_pv.format("X", "Mon")
            ),
        )
        self.lb_prmmony = SiriusLabel(
            self,
            self.ioc_prefix.substitute(
                propty=self.param_pv.format("Y", "Mon")
            ),
        )

        self.bt_apply = PyDMPushButton(
            self,
            label="Apply",
            pressValue=1,
            init_channel=self.ioc_prefix.substitute(propty="ApplyDelta-Cmd"),
        )

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.lb_sp, 0, 1)
        lay.addWidget(self.lb_rb, 0, 2)
        lay.addWidget(self.lb_x, 1, 0)
        lay.addWidget(self.sb_paramx, 1, 1)
        lay.addWidget(self.lb_paramx, 1, 2)
        lay.addWidget(self.lb_y, 2, 0)
        lay.addWidget(self.sb_paramy, 2, 1)
        lay.addWidget(self.lb_paramy, 2, 2)
        lay.addWidget(self.lb_mon, 0, 3)
        lay.addWidget(self.lb_prmmonx, 1, 3)
        lay.addWidget(self.lb_prmmony, 2, 3)
        lay.addWidget(self.bt_apply, 3, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 5)
        lay.setColumnStretch(2, 5)
        lay.setColumnStretch(3, 5)

        if self.acc == "SI" and self.param == "chrom":
            self._icon_absval = qta.icon(
                "mdi.alpha-a",
                "mdi.alpha-b",
                "mdi.alpha-s",
                options=[
                    dict(scale_factor=1.5, offset=(-0.4, 0.0)),
                    dict(scale_factor=1.5, offset=(0.0, 0.0)),
                    dict(scale_factor=1.5, offset=(+0.4, 0.0)),
                ],
            )
            self._icon_delta = qta.icon("mdi.delta")
            self._is_setting = "absolut"
            self.pb_change_sp = QPushButton(self._icon_absval, "", self)
            self.pb_change_sp.clicked.connect(self._change_chrom_sp)

            self.sb_paramx_delta = SiriusSpinbox(
                self, self.ioc_prefix.substitute(propty="DeltaChromX-SP")
            )
            self.sb_paramx_delta.setVisible(False)

            self.sb_paramy_delta = SiriusSpinbox(
                self, self.ioc_prefix.substitute(propty="DeltaChromY-SP")
            )
            self.sb_paramy_delta.setVisible(False)

            self.lb_paramx_delta = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="DeltaChromX-RB")
            )
            self.lb_paramx_delta.setVisible(False)
            self.lb_paramy_delta = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="DeltaChromY-RB")
            )
            self.lb_paramy_delta.setVisible(False)

            self.lb_mon.setText("Implem.\nEstimative")
            self.lb_mon.setStyleSheet("font-weight: bold;")
            self.lb_calcmon = QLabel(
                "Calcd.\nEstimative", self, alignment=Qt.AlignCenter
            )
            self.lb_calcmon.setStyleSheet("font-weight: bold;")

            self.lb_prmcalcmonx = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="CalcChromX-Mon")
            )
            self.lb_prmcalcmony = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="CalcChromY-Mon")
            )

            lay.addWidget(self.pb_change_sp, 0, 0)
            lay.addWidget(self.sb_paramx_delta, 1, 1)
            lay.addWidget(self.sb_paramy_delta, 2, 1)
            lay.addWidget(self.lb_paramx_delta, 1, 2)
            lay.addWidget(self.lb_paramy_delta, 2, 2)
            lay.addWidget(self.lb_calcmon, 0, 4)
            lay.addWidget(self.lb_prmcalcmonx, 1, 4)
            lay.addWidget(self.lb_prmcalcmony, 2, 4)
        return lay

    def _setup_digmon_layout(self):
        lay_tune = QGridLayout()

        prec = 5
        # val = self.tunesourcepvlist_pv.value
        # tunex_pv, tuney_pv = val if val else ['None', 'None']
        # tunex_pv = _PVName(tunex_pv).substitute(prefix=self.prefix)
        # tuney_pv = _PVName(tuney_pv).substitute(prefix=self.prefix)

        tunex_pv = self.ioc_prefix.substitute(propty="TuneX-Mon")
        tuney_pv = self.ioc_prefix.substitute(propty="TuneY-Mon")

        self.ld_tunefrach = QLabel(
            "<h4>Tune X</h4>", self, alignment=Qt.AlignHCenter
        )
        self.lb_tunefrach = SiriusLabel(self, tunex_pv)
        self.lb_tunefrach.precisionFromPV = False
        self.lb_tunefrach.precision = prec
        self.lb_tunefrach.setAlignment(Qt.AlignHCenter)
        self.lb_tunefrach.setStyleSheet("QLabel{font-size: 16pt;}")
        wid_tuneh = QWidget()
        wid_tuneh.setObjectName("wid_tuneh")
        wid_tuneh.setStyleSheet("background-color:#B3E5FF;")
        vbox_tuneh = QVBoxLayout(wid_tuneh)
        vbox_tuneh.addWidget(self.ld_tunefrach)
        vbox_tuneh.addWidget(self.lb_tunefrach)
        lay_tune.addWidget(wid_tuneh, 0, 0)

        self.ld_tunefracv = QLabel(
            "<h4>Tune Y</h4>", self, alignment=Qt.AlignHCenter
        )
        self.lb_tunefracv = SiriusLabel(self, tuney_pv)
        self.lb_tunefracv.precisionFromPV = False
        self.lb_tunefracv.precision = prec
        self.lb_tunefracv.setAlignment(Qt.AlignHCenter)
        self.lb_tunefracv.setStyleSheet("QLabel{font-size: 16pt;}")
        wid_tunev = QWidget()
        wid_tunev.setObjectName("wid_tunev")
        wid_tunev.setStyleSheet("background-color:#FFB3B3;")
        vbox_tunev = QVBoxLayout(wid_tunev)
        vbox_tunev.setAlignment(Qt.AlignHCenter)
        vbox_tunev.addWidget(self.ld_tunefracv)
        vbox_tunev.addWidget(self.lb_tunefracv)
        lay_tune.addWidget(wid_tunev, 0, 1)

        # self.tunesourcepvlist_pv.add_callback(self._update_tune_digmon)
        return lay_tune

    def _setup_correction_layout(self):

        lay = QVBoxLayout()

        hbl = QHBoxLayout()
        lbl = QLabel("Auto Correction State:", self.gb_corr)

        wid = QWidget(self.gb_corr)

        widlay = QHBoxLayout(wid)
        spsw = PyDMStateButton(
            wid, self.ioc_prefix.substitute(propty="LoopState-Sel")
        )
        rdbl = SiriusLedState(
            wid, self.ioc_prefix.substitute(propty="LoopState-Sts")
        )
        widlay.addWidget(spsw)
        widlay.addWidget(rdbl)

        hbl.addWidget(lbl)
        hbl.addWidget(wid)
        lay.addLayout(hbl)

        corr_tab = QTabWidget()
        corr_tab.setObjectName(self.acc + "Tab")
        lay.addWidget(corr_tab)

        # Loop ################################################################
        self.wid_atcr = QWidget()
        lay_atcr = QVBoxLayout(self.wid_atcr)
        lay_atcr.setAlignment(Qt.AlignTop)

        lay_atcr.addWidget(QLabel("<h4>General</h4>", self.wid_atcr))

        # Tune Source
        self.tunesrc_wid = QWidget(self.wid_atcr)
        lay_tunesrc = QHBoxLayout(self.tunesrc_wid)
        lay_tunesrc.setContentsMargins(0, 0, 0, 0)
        tunesrcpvn = "TuneSrc-{}"
        tunesrc_lbl = QLabel("Tune Source", self.wid_atcr)
        tunesrc_cbbx = PyDMEnumComboBox(
            self.tunesrc_wid,
            self.ioc_prefix.substitute(propty=tunesrcpvn.format("Sel")),
        )
        tunesrc_rb = SiriusLabel(
            self.tunesrc_wid,
            self.ioc_prefix.substitute(propty=tunesrcpvn.format("Sts")),
        )
        lay_tunesrc.addWidget(tunesrc_lbl, 2, alignment=Qt.AlignLeft)
        lay_tunesrc.addWidget(tunesrc_cbbx, alignment=Qt.AlignRight)
        lay_tunesrc.addWidget(tunesrc_rb, alignment=Qt.AlignLeft)
        lay_atcr.addWidget(self.tunesrc_wid)

        # Loop Frequency
        freqbar = QHBoxLayout()
        freqbar.setContentsMargins(0, 0, 0, 0)
        freqbar_lbl = QLabel("Loop Freq. [Hz]", self.wid_atcr)
        freqpvn = "LoopFreq-{}"
        freqspinbox = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=freqpvn.format("SP")),
        )
        freqspinbox.setSingleStep(0.5)
        freqrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=freqpvn.format("RB")),
        )
        freqbar.addWidget(freqbar_lbl, 2, alignment=Qt.AlignLeft)
        freqbar.addWidget(freqspinbox, alignment=Qt.AlignRight)
        freqbar.addWidget(freqrb, alignment=Qt.AlignLeft)
        lay_atcr.addLayout(freqbar)

        # RefTuneX
        reftunexbar = QHBoxLayout()
        reftunexbar.setContentsMargins(0, 0, 0, 0)
        tunexpvn = "RefTuneX-{}"
        reftunex_lbl = QLabel("Ref. Tune X", self.wid_atcr)
        reftunex_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tunexpvn.format("SP")),
        )
        reftunex_wid.setSingleStep(0.001)
        reftunexrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tunexpvn.format("RB")),
        )
        reftunexbar.addWidget(reftunex_lbl, 2, alignment=Qt.AlignLeft)
        reftunexbar.addWidget(reftunex_wid, alignment=Qt.AlignRight)
        reftunexbar.addWidget(reftunexrb, alignment=Qt.AlignLeft)
        lay_atcr.addLayout(reftunexbar)

        # RefTuneY
        reftuneybar = QHBoxLayout()
        reftuneybar.setContentsMargins(0, 0, 0, 0)
        tuneypvn = "RefTuneY-{}"
        reftuney_lbl = QLabel("Ref. Tune Y", self.wid_atcr)
        reftuney_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tuneypvn.format("SP")),
        )
        reftuney_wid.setSingleStep(0.001)
        reftuneyrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tuneypvn.format("RB")),
        )

        reftuneybar.addWidget(reftuney_lbl, 2, alignment=Qt.AlignLeft)
        reftuneybar.addWidget(reftuney_wid, alignment=Qt.AlignRight)
        reftuneybar.addWidget(reftuneyrb, alignment=Qt.AlignLeft)
        lay_atcr.addLayout(reftuneybar)

        # MaxTuneErr
        maxtuneerrbar = QHBoxLayout()
        maxtuneerrbar.setContentsMargins(0, 0, 0, 0)
        maxtuneerrpvn = "MaxTuneErr-{}"
        maxtuneerr_lbl = QLabel("Max. Tune Err.", self.wid_atcr)
        maxtuneerr_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtuneerrpvn.format("SP")),
        )
        maxtuneerr_wid.setSingleStep(0.005)
        maxtuneerrrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtuneerrpvn.format("RB")),
        )
        maxtuneerrbar.addWidget(maxtuneerr_lbl, 2, alignment=Qt.AlignLeft)
        maxtuneerrbar.addWidget(maxtuneerr_wid, alignment=Qt.AlignCenter)
        maxtuneerrbar.addWidget(maxtuneerrrb, alignment=Qt.AlignLeft)
        lay_atcr.addLayout(maxtuneerrbar)

        lay_atcr.addWidget(QLabel("<h4>PID</h4>", self.wid_atcr))

        hpl = QGridLayout()
        _qtal = Qt.AlignCenter
        hpl.addWidget(
            QLabel("<h4>Kp</h4>", self.wid_atcr, alignment=_qtal), 0, 1
        )
        hpl.addWidget(
            QLabel("<h4>Ki</h4>", self.wid_atcr, alignment=_qtal), 0, 2
        )
        hpl.addWidget(
            QLabel("<h4>Kd</h4>", self.wid_atcr, alignment=_qtal), 0, 3
        )

        # PID
        self.tunepid_pvs = [
            self.ioc_prefix.substitute(propty="LoopPID" + _k + _pvt)
            for _k in ["Kp", "Ki", "Kd"]
            for _pvt in ["-SP", "-RB"]
        ]
        self.tunepid_widgets = dict(
            (
                _pv,
                SiriusSpinbox(self.wid_atcr, _pv)
                if _pv.endswith("SP")
                else SiriusLabel(self.wid_atcr, _pv),
            )
            for _pv in self.tunepid_pvs
        )
        for _pv, wid in self.tunepid_widgets.items():
            i = 1 if _pv.split("PID")[-1][2] == "X" else 3
            if _pv.endswith("RB"):
                i += 1
            else:
                wid.setSingleStep(0.05)
            j = ("Kp", "Ki", "Kd").index(_pv.split("PID")[-1][:2]) + 1
            hpl.addWidget(wid, i, j)
        lay_atcr.addLayout(hpl)
        corr_tab.addTab(self.wid_atcr, "Loop")

        # Manual ##############################################################
        self.wid_optics = QWidget()
        lay_optics = QGridLayout(self.wid_optics)
        lay_optics.setContentsMargins(0, 0, 0, 0)
        lay_optics.addWidget(self.pb_updref, 0, 0, 1, 2)
        lay_optics.addWidget(self.gb_optprm, 1, 0)
        corr_tab.addTab(self.wid_optics, "Manual")

        return lay

    def _setup_families_layout(self):
        lay = QGridLayout()

        lb_family = QLabel("<h4>Family</h4>", self, alignment=Qt.AlignCenter)
        lb_family.setStyleSheet("max-height:1.29em;")
        lay.addWidget(lb_family, 0, 1)

        lb_rbdesc = QLabel(
            "<h4>" + self.intstrength + "-RB</h4>",
            self,
            alignment=Qt.AlignCenter,
        )
        lb_rbdesc.setStyleSheet("max-height:1.29em;")
        lay.addWidget(lb_rbdesc, 0, 2)

        if self.param == "tune":
            lb_refdesc = QLabel(
                "<h4>RefKL-Mon</h4>", self, alignment=Qt.AlignCenter
            )
            lb_refdesc.setStyleSheet("max-height:1.29em;")
            lay.addWidget(lb_refdesc, 0, 3)

        lb_lastddesc = QLabel(
            "<h4>" + self.intstrength_calcdesc + "</h4>",
            self,
            alignment=Qt.AlignCenter,
        )
        lb_lastddesc.setStyleSheet("max-height:1.29em;")
        lay.addWidget(lb_lastddesc, 0, 4)

        row = 1
        for fam in self.fams:
            dev_name = _PVName(self.acc + "-Fam:PS-" + fam)
            pref_name = dev_name.substitute(prefix=self.prefix)

            pbt = QPushButton(qta.icon("fa5s.list-ul"), "", self)
            pbt.setObjectName("pbt")
            pbt.setStyleSheet(
                """#pbt{
                    min-width:25px; max-width:25px;
                    min-height:25px; max-height:25px;
                    icon-size:20px;}"""
            )
            _hlautil.connect_window(
                pbt, _PSDetailWindow, parent=self, psname=dev_name
            )
            lay.addWidget(pbt, row, 0)

            lb_name = QLabel(fam, self, alignment=Qt.AlignCenter)
            lay.addWidget(lb_name, row, 1)

            lb_rb = SiriusLabel(
                self, pref_name.substitute(propty=self.intstrength + "-RB")
            )
            lay.addWidget(lb_rb, row, 2)

            if self.param == "tune":
                lb_ref = SiriusLabel(
                    self,
                    self.ioc_prefix.substitute(propty="RefKL" + fam + "-Mon"),
                )
                lay.addWidget(lb_ref, row, 3)

            lb_calc = SiriusLabel(
                self,
                self.ioc_prefix.substitute(
                    propty=self.intstrength_calcpv.format(fam)
                ),
            )
            lay.addWidget(lb_calc, row, 4)
            row += 1
        return lay

    def _setup_ioc_control_layout(self):
        lay = QGridLayout()

        lb_sts = QLabel("<h4>Status</h4>", self)
        self.led_sts = _StatusLed(
            self, self.ioc_prefix.substitute(propty="Status-Mon")
        )
        lay.addWidget(lb_sts, 0, 0)
        lay.addWidget(self.led_sts, 0, 1, alignment=Qt.AlignLeft)

        lb_conf = QLabel("<h4>Configuration</h4>")
        self.bt_dtls = QPushButton(qta.icon("fa5s.list-ul"), "", self)
        _hlautil.connect_window(
            self.bt_dtls,
            _CorrParamsDetailWindow,
            parent=self,
            acc=self.acc,
            opticsparam=self.param,
            prefix=self.prefix,
            fams=self.fams,
        )
        lay.addWidget(lb_conf, 2, 0, 1, 2)
        lay.addWidget(self.bt_dtls, 2, 2, alignment=Qt.AlignRight)

        lb_cname = QLabel("Name", self)
        self.le_cname = _ConfigLineEdit(
            self, self.ioc_prefix.substitute(propty="ConfigName-SP")
        )
        self.lb_cname = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="ConfigName-RB")
        )
        lay.addWidget(lb_cname, 3, 0)
        lay.addWidget(self.le_cname, 3, 1, 1, 2)
        lay.addWidget(self.lb_cname, 4, 1, 1, 2)

        row = 5
        if self.acc == "SI":
            lay.addItem(QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 5, 0)
            row = 6

            if self.param == "chrom":
                lb_meas_chrom = QLabel("<h4>Chrom. Measurement</h4>")
                lay.addWidget(lb_meas_chrom, 6, 0, 1, 3)

                lb_meas_chrom_dfreq = QLabel("ΔFreq RF [Hz]", self)
                self.sb_meas_chrom_dfRF = SiriusSpinbox(
                    self,
                    self.ioc_prefix.substitute(
                        propty="MeasChromDeltaFreqRF-SP"
                    ),
                )
                self.lb_meas_chrom_dfreq = SiriusLabel(
                    self,
                    self.ioc_prefix.substitute(
                        propty="MeasChromDeltaFreqRF-RB"
                    ),
                )
                lay.addWidget(lb_meas_chrom_dfreq, 7, 0)
                lay.addWidget(self.sb_meas_chrom_dfRF, 7, 1)
                lay.addWidget(self.lb_meas_chrom_dfreq, 7, 2)

                lb_meas_chrom_wait = QLabel("Wait Tune [s]", self)
                self.sb_meas_chrom_wait = SiriusSpinbox(
                    self,
                    self.ioc_prefix.substitute(propty="MeasChromWaitTune-SP"),
                )
                self.lb_meas_chrom_wait = SiriusLabel(
                    self,
                    self.ioc_prefix.substitute(propty="MeasChromWaitTune-RB"),
                )
                lay.addWidget(lb_meas_chrom_wait, 8, 0)
                lay.addWidget(self.sb_meas_chrom_wait, 8, 1)
                lay.addWidget(self.lb_meas_chrom_wait, 8, 2)

                lb_meas_chrom_nrsteps = QLabel("Nr Steps", self)
                self.sb_meas_chrom_nrsteps = SiriusSpinbox(
                    self,
                    self.ioc_prefix.substitute(propty="MeasChromNrSteps-SP"),
                )
                self.lb_meas_chrom_nrsteps = SiriusLabel(
                    self,
                    self.ioc_prefix.substitute(propty="MeasChromNrSteps-RB"),
                )
                lay.addWidget(lb_meas_chrom_nrsteps, 9, 0)
                lay.addWidget(self.sb_meas_chrom_nrsteps, 9, 1)
                lay.addWidget(self.lb_meas_chrom_nrsteps, 9, 2)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 10, 0
                )

                lb_meas_chrom_x = QLabel("Meas. Chrom X", self)
                self.lb_meas_chrom_x = SiriusLabel(
                    self, self.ioc_prefix.substitute(propty="MeasChromX-Mon")
                )
                lay.addWidget(lb_meas_chrom_x, 11, 0)
                lay.addWidget(self.lb_meas_chrom_x, 11, 1)

                lb_meas_chrom_y = QLabel("Meas. Chrom Y", self)
                self.lb_meas_chrom_y = SiriusLabel(
                    self, self.ioc_prefix.substitute(propty="MeasChromY-Mon")
                )
                lay.addWidget(lb_meas_chrom_y, 12, 0)
                lay.addWidget(self.lb_meas_chrom_y, 12, 1)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 13, 0
                )

                self.lb_meas_chrom_sts = SiriusLabel(
                    self,
                    self.ioc_prefix.substitute(propty="MeasChromStatus-Mon"),
                )
                self.bt_meas_chrom_start = PyDMPushButton(
                    self,
                    icon=qta.icon("fa5s.play"),
                    label="",
                    init_channel=self.ioc_prefix.substitute(
                        propty="MeasChrom-Cmd"
                    ),
                    pressValue=_Const.MeasCmd.Start,
                )
                self.bt_meas_chrom_start.setObjectName("start")
                self.bt_meas_chrom_start.setStyleSheet(
                    "#start{min-width:25px; max-width:25px; icon-size:20px;}"
                )
                self.bt_meas_chrom_stop = PyDMPushButton(
                    self,
                    icon=qta.icon("fa5s.stop"),
                    label="",
                    init_channel=self.ioc_prefix.substitute(
                        propty="MeasChrom-Cmd"
                    ),
                    pressValue=_Const.MeasCmd.Stop,
                )
                self.bt_meas_chrom_stop.setObjectName("stop")
                self.bt_meas_chrom_stop.setStyleSheet(
                    "#stop{min-width:25px; max-width:25px; icon-size:20px;}"
                )
                self.bt_meas_chrom_rst = PyDMPushButton(
                    self,
                    icon=qta.icon("fa5s.sync"),
                    label="",
                    init_channel=self.ioc_prefix.substitute(
                        propty="MeasChrom-Cmd"
                    ),
                    pressValue=_Const.MeasCmd.Reset,
                )
                self.bt_meas_chrom_rst.setObjectName("rst")
                self.bt_meas_chrom_rst.setStyleSheet(
                    "#rst{min-width:25px; max-width:25px; icon-size:20px;}"
                )
                hbox_cmd = QHBoxLayout()
                hbox_cmd.addWidget(self.bt_meas_chrom_start)
                hbox_cmd.addWidget(self.bt_meas_chrom_stop)
                hbox_cmd.addWidget(self.bt_meas_chrom_rst)
                lay.addWidget(self.lb_meas_chrom_sts, 14, 0, 1, 2)
                lay.addLayout(hbox_cmd, 14, 2)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 15, 0
                )
                row = 15

            # configuration measurement
            lb_meas_conf = QLabel("<h4>Config. Measurement</h4>")
            lay.addWidget(lb_meas_conf, row + 1, 0, 1, 3)

            mag_type = "Q" if self.param == "tune" else "S"
            unit = "[1/m]" if self.param == "tune" else "[1/m2]"

            pvn = self.ioc_prefix.substitute(
                propty="MeasConfigDelta"
                + self.intstrength
                + "Fam"
                + mag_type
                + "F"
            )
            lb_meas_conf_dfam_foc = QLabel(
                "Fam. Δ" + self.intstrength + " " + mag_type + "F " + unit,
                self,
            )
            self.sb_meas_conf_dfamF = SiriusSpinbox(
                self, pvn.substitute(propty_suffix="SP")
            )
            self.lb_meas_conf_dfam_foc = SiriusLabel(
                self, pvn.substitute(propty_suffix="RB")
            )
            lay.addWidget(lb_meas_conf_dfam_foc, row + 2, 0)
            lay.addWidget(self.sb_meas_conf_dfamF, row + 2, 1)
            lay.addWidget(self.lb_meas_conf_dfam_foc, row + 2, 2)

            pvn = self.ioc_prefix.substitute(
                propty="MeasConfigDelta"
                + self.intstrength
                + "Fam"
                + mag_type
                + "D"
            )
            lb_meas_conf_dfam_defoc = QLabel(
                "Fam. Δ" + self.intstrength + " " + mag_type + "D " + unit,
                self,
            )
            self.sb_meas_conf_dfamD = SiriusSpinbox(
                self, pvn.substitute(propty_suffix="SP")
            )
            self.lb_meas_conf_dfam_defoc = SiriusLabel(
                self, pvn.substitute(propty_suffix="RB")
            )
            lay.addWidget(lb_meas_conf_dfam_defoc, row + 3, 0)
            lay.addWidget(self.sb_meas_conf_dfamD, row + 3, 1)
            lay.addWidget(self.lb_meas_conf_dfam_defoc, row + 3, 2)

            lb_meas_conf_wait = QLabel("Wait [s]", self)
            self.sb_meas_conf_wait = SiriusSpinbox(
                self, self.ioc_prefix.substitute(propty="MeasConfigWait-SP")
            )
            self.lb_meas_conf_wait = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="MeasConfigWait-RB")
            )
            lay.addWidget(lb_meas_conf_wait, row + 4, 0)
            lay.addWidget(self.sb_meas_conf_wait, row + 4, 1)
            lay.addWidget(self.lb_meas_conf_wait, row + 4, 2)

            lb_meas_conf_cname = QLabel("Name to save", self)
            self.le_meas_conf_name = PyDMLineEdit(
                self, self.ioc_prefix.substitute(propty="MeasConfigName-SP")
            )
            self.lb_meas_conf_name = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="MeasConfigName-RB")
            )
            lay.addWidget(lb_meas_conf_cname, row + 5, 0)
            lay.addWidget(self.le_meas_conf_name, row + 5, 1, 1, 2)
            lay.addWidget(self.lb_meas_conf_name, row + 6, 1, 1, 2)

            lb_meas_conf_save = QLabel("Force Save", self)
            self.bt_meas_conf_save = PyDMPushButton(
                self,
                icon=qta.icon("mdi.content-save"),
                label="",
                init_channel=self.ioc_prefix.substitute(
                    propty="MeasConfigSave-Cmd"
                ),
                pressValue=1,
            )
            self.bt_meas_conf_save.setObjectName("save")
            self.bt_meas_conf_save.setStyleSheet(
                "#save{min-width:25px; max-width:25px; icon-size:20px;}"
            )
            lay.addWidget(lb_meas_conf_save, row + 7, 0)
            lay.addWidget(
                self.bt_meas_conf_save, row + 7, 1, alignment=Qt.AlignLeft
            )

            lay.addItem(
                QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), row + 8, 0
            )

            self.lb_meas_conf_sts = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="MeasConfigStatus-Mon")
            )
            self.bt_meas_conf_start = PyDMPushButton(
                self,
                icon=qta.icon("fa5s.play"),
                label="",
                init_channel=self.ioc_prefix.substitute(
                    propty="MeasConfig-Cmd"
                ),
                pressValue=_Const.MeasCmd.Start,
            )
            self.bt_meas_conf_start.setObjectName("start")
            self.bt_meas_conf_start.setStyleSheet(
                "#start{min-width:25px; max-width:25px; icon-size:20px;}"
            )
            self.bt_meas_conf_stop = PyDMPushButton(
                self,
                icon=qta.icon("fa5s.stop"),
                label="",
                init_channel=self.ioc_prefix.substitute(
                    propty="MeasConfig-Cmd"
                ),
                pressValue=_Const.MeasCmd.Stop,
            )
            self.bt_meas_conf_stop.setObjectName("stop")
            self.bt_meas_conf_stop.setStyleSheet(
                "#stop{min-width:25px; max-width:25px; icon-size:20px;}"
            )
            self.bt_meas_conf_rst = PyDMPushButton(
                self,
                icon=qta.icon("fa5s.sync"),
                label="",
                init_channel=self.ioc_prefix.substitute(
                    propty="MeasConfig-Cmd"
                ),
                pressValue=_Const.MeasCmd.Reset,
            )
            self.bt_meas_conf_rst.setObjectName("rst")
            self.bt_meas_conf_rst.setStyleSheet(
                "#rst{min-width:25px; max-width:25px; icon-size:20px;}"
            )
            hbox_cmd = QHBoxLayout()
            hbox_cmd.addWidget(self.bt_meas_conf_start)
            hbox_cmd.addWidget(self.bt_meas_conf_stop)
            hbox_cmd.addWidget(self.bt_meas_conf_rst)
            lay.addWidget(self.lb_meas_conf_sts, row + 9, 0, 1, 2)
            lay.addLayout(hbox_cmd, row + 9, 2)

            lay.addItem(
                QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), row + 10, 0
            )

            # correction settings
            lb_corr = QLabel("<h4>Settings</h4>")
            lay.addWidget(lb_corr, row + 11, 0, 1, 3)

            lb_meth = QLabel("Method", self)
            self.cb_method = PyDMEnumComboBox(
                self, self.ioc_prefix.substitute(propty="CorrMeth-Sel")
            )
            self.lb_method = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="CorrMeth-Sts")
            )
            lay.addWidget(lb_meth, row + 12, 0)
            lay.addWidget(self.cb_method, row + 12, 1)
            lay.addWidget(self.lb_method, row + 12, 2)

            lb_grp = QLabel("Grouping", self)
            self.cb_group = PyDMEnumComboBox(
                self, self.ioc_prefix.substitute(propty="CorrGroup-Sel")
            )
            self.lb_group = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="CorrGroup-Sts")
            )
            lay.addWidget(lb_grp, row + 13, 0)
            lay.addWidget(self.cb_group, row + 13, 1)
            lay.addWidget(self.lb_group, row + 13, 2)

            if self.param == "tune":
                lb_sync = QLabel("Sync", self)
                self.bt_sync = PyDMStateButton(
                    self, self.ioc_prefix.substitute(propty="SyncCorr-Sel")
                )
                self.bt_sync.shape = 1
                self.lb_sync = SiriusLabel(
                    self, self.ioc_prefix.substitute(propty="SyncCorr-Sts")
                )
                lay.addWidget(lb_sync, row + 14, 0)
                lay.addWidget(self.bt_sync, row + 14, 1)
                lay.addWidget(self.lb_sync, row + 14, 2)
            row = row + 15

        lay.addItem(
            QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Expanding), row, 0
        )
        return lay

    def _change_chrom_sp(self):
        cond = self._is_setting == "absolut"
        self._is_setting = "delta" if cond else "absolut"
        icon = self._icon_delta if cond else self._icon_absval
        text_x = "<h4>Δ-SP</h4>" if cond else "<h4>SP</h4>"
        text_y = "<h4>Δ-RB</h4>" if cond else "<h4>RB</h4>"
        self.sb_paramx.setVisible(not cond)
        self.lb_paramx.setVisible(not cond)
        self.sb_paramy.setVisible(not cond)
        self.lb_paramy.setVisible(not cond)
        self.sb_paramx_delta.setVisible(cond)
        self.lb_paramx_delta.setVisible(cond)
        self.sb_paramy_delta.setVisible(cond)
        self.lb_paramy_delta.setVisible(cond)
        self.pb_change_sp.setIcon(icon)
        self.lb_sp.setText(text_x)
        self.lb_rb.setText(text_y)


class SITuneCorrWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(SITuneCorrWindow, self).__init__(parent)
        self.prefix = prefix
        self.acc = acc.upper()
        self.param = opticsparam
        self.ioc_prefix = _PVName(
            self.acc + "-Glob:AP-" + self.param.title() + "Corr"
        )
        self.ioc_prefix = self.ioc_prefix.substitute(prefix=self.prefix)
        self.title = self.acc + " " + self.param.title() + " Correction"

        self.param_pv = "DeltaTune{0}-{1}"
        self.intstrength = "KL"
        self.intstrength_calcdesc = "DeltaKL-Mon"
        self.intstrength_calcpv = "DeltaKL{}-Mon"
        self.fams = list(_Const.SI_QFAMS_TUNECORR)

        self.setWindowTitle(self.title)
        self.setObjectName(self.acc + "App")
        self._setupui()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupui(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(self.title)
        self.setDocumentMode(False)
        self.setDockNestingEnabled(True)

        self.ioc_log = self._create_log_docwidget()
        self.qfams_kl_table = self._create_families_docwidget()
        self.qfams_kl_table.setSizePolicy(QSzPly.Preferred, QSzPly.Fixed)
        self.tunefb_control = self._create_ioc_control_docwidget()

        self.mwid = self._create_diagmon_centralwidget()
        self.setCentralWidget(self.mwid)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.ioc_log)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tunefb_control)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.qfams_kl_table)

        self._create_menus()
        self.setFocus(True)
        # self.setFocusPolicy(Qt.StrongFocus)

    def _create_diagmon_centralwidget(self):
        digmon = QGroupBox("SI Tune Monitor", self)
        lay = QGridLayout(digmon)
        # lay = QVBoxLayout(digmon)

        tune_frac_wid = QWidget(digmon)
        tune_frac_lay = QHBoxLayout(tune_frac_wid)
        tune_frac_lay.setContentsMargins(0, 5, 0, 5)
        prec = 5
        tunex_pv = self.ioc_prefix.substitute(propty="TuneX-Mon")
        tuney_pv = self.ioc_prefix.substitute(propty="TuneY-Mon")

        self.ld_tunefrach = QLabel(
            "<h4>Tune X</h4>", self, alignment=Qt.AlignHCenter
        )
        self.lb_tunefrach = SiriusLabel(self, tunex_pv)
        self.lb_tunefrach.precisionFromPV = False
        self.lb_tunefrach.precision = prec
        self.lb_tunefrach.setAlignment(Qt.AlignHCenter)
        self.lb_tunefrach.setStyleSheet("QLabel{font-size: 16pt;}")
        wid_tuneh = QWidget()
        wid_tuneh.setObjectName("wid_tuneh")
        wid_tuneh.setStyleSheet("background-color:#B3E5FF;")
        vbox_tuneh = QVBoxLayout(wid_tuneh)
        vbox_tuneh.addWidget(self.ld_tunefrach)
        vbox_tuneh.addWidget(self.lb_tunefrach)
        tune_frac_lay.addWidget(wid_tuneh)

        self.ld_tunefracv = QLabel(
            "<h4>Tune Y</h4>", self, alignment=Qt.AlignHCenter
        )
        self.lb_tunefracv = SiriusLabel(self, tuney_pv)
        self.lb_tunefracv.precisionFromPV = False
        self.lb_tunefracv.precision = prec
        self.lb_tunefracv.setAlignment(Qt.AlignHCenter)
        self.lb_tunefracv.setStyleSheet("QLabel{font-size: 16pt;}")
        wid_tunev = QWidget()
        wid_tunev.setObjectName("wid_tunev")
        wid_tunev.setStyleSheet("background-color:#FFB3B3;")
        vbox_tunev = QVBoxLayout(wid_tunev)
        vbox_tunev.setAlignment(Qt.AlignHCenter)
        vbox_tunev.addWidget(self.ld_tunefracv)
        vbox_tunev.addWidget(self.lb_tunefracv)
        tune_frac_lay.addWidget(wid_tunev)

        spec_wid = QGroupBox("Spectrum", digmon)
        spec_lay = QGridLayout(spec_wid)
        spec_lay.setContentsMargins(0, 10, 0, 5)
        wid_spect_x = TuneSpectrumPlot(
            prefix=self.prefix,
            plane="H",
            ioc_prefix=self.ioc_prefix,
            parent=spec_wid,
        )
        wid_spect_y = TuneSpectrumPlot(
            prefix=self.prefix,
            plane="V",
            ioc_prefix=self.ioc_prefix,
            parent=spec_wid,
        )
        spec_lay.addWidget(wid_spect_x, 0, 0)
        spec_lay.addWidget(wid_spect_y, 0, 1)

        famskl_wid = QGroupBox("\u0394KL Monitor", digmon)
        famskl_lay = QHBoxLayout(famskl_wid)
        famskl_lay.setContentsMargins(0, 10, 0, 5)
        fams_klplot = DeltaKLFamiliesPlot(
            ioc_prefix=self.ioc_prefix,
            fams=self.fams,
            parent=famskl_wid,
            prefix=self.prefix,
            # yrange_lim=-1.5e-5,
        )
        famskl_lay.addWidget(fams_klplot)

        lay.addWidget(tune_frac_wid)
        lay.addWidget(spec_wid)
        lay.addWidget(famskl_wid)

        famskl_wid.setStyleSheet("""
        min-height: 15em;
        max-height: 15em;
        """)

        # tune_h = 50
        # lay.setRowMinimumHeight(0, tune_h)
        # lay.setRowMinimumHeight(1, 10 * tune_h)
        # lay.setRowMinimumHeight(2, 3 * tune_h)
        # lay.setRowMinimumHeight(3, 3 * tune_h)
        lay.setColumnMinimumWidth(0, 20 * 50)

        return digmon

    def _create_log_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("IOC Log")
        sz_pol = QSzPly(QSzPly.Preferred, QSzPly.Preferred)
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setObjectName("doc_IOCLog")
        docwid.setStyleSheet("#doc_IOCLog{min-width:20em; min-height:20em;}")
        wid_cont = QWidget(parent=docwid)
        docwid.setWidget(wid_cont)
        vbl = QVBoxLayout(wid_cont)
        vbl.setContentsMargins(5, 5, 5, 5)
        pdm_log = PyDMLogLabel(
            wid_cont, self.ioc_prefix.substitute(propty="Log-Mon")
        )
        pdm_log.setAlternatingRowColors(True)
        pdm_log.maxCount = 2000
        vbl.addWidget(pdm_log)
        hbl = QHBoxLayout()
        vbl.addLayout(hbl)
        hbl.addStretch()
        pbtn = QPushButton("Clear Log", wid_cont)
        pbtn.clicked.connect(pdm_log.clear)
        hbl.addWidget(pbtn)
        hbl.addStretch()
        return docwid

    def _create_families_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("Strength Monitor")

        wid = QWidget()
        docwid.setWidget(wid)

        lay = QGridLayout(wid)
        lay.setContentsMargins(5, 5, 5, 5)

        lb_family = QLabel("Family", self)
        lb_family.setStyleSheet("max-height:1.29em; font-weight:bold;")
        lay.addWidget(lb_family, 0, 1, alignment=Qt.AlignCenter)

        lb_rbdesc = QLabel("KL-RB", self)
        lb_rbdesc.setStyleSheet("max-height:1.29em; font-weight:bold;")
        lay.addWidget(lb_rbdesc, 0, 2, alignment=Qt.AlignCenter)

        lb_refdesc = QLabel("RefKL-Mon", self)
        lb_refdesc.setStyleSheet("max-height:1.29em; font-weight:bold;")
        lay.addWidget(lb_refdesc, 0, 3, alignment=Qt.AlignCenter)

        lb_lastddesc = QLabel("DeltaKL-Mon", self)
        lb_lastddesc.setStyleSheet("max-height:1.29em; font-weight:bold;")
        lay.addWidget(lb_lastddesc, 0, 4, alignment=Qt.AlignRight)

        row = 1
        for fam in self.fams:
            dev_name = _PVName(self.acc + "-Fam:PS-" + fam)
            pref_name = dev_name.substitute(prefix=self.prefix)

            pbt = QPushButton(qta.icon("fa5s.list-ul"), "", self)
            pbt.setObjectName("pbt")
            pbt.setStyleSheet(
                """#pbt{
                    min-width:25px; max-width:25px;
                    min-height:25px; max-height:25px;
                    icon-size:20px;}"""
            )
            _hlautil.connect_window(
                pbt, _PSDetailWindow, parent=self, psname=dev_name
            )
            lay.addWidget(pbt, row, 0, alignment=Qt.AlignRight)

            lb_name = QLabel(fam, self, alignment=Qt.AlignCenter)
            lay.addWidget(lb_name, row, 1)

            lb_rb = SiriusLabel(
                self, pref_name.substitute(propty=self.intstrength + "-RB")
            )
            lay.addWidget(lb_rb, row, 2, alignment=Qt.AlignCenter)

            lb_ref = SiriusLabel(
                self, self.ioc_prefix.substitute(propty="RefKL" + fam + "-Mon")
            )
            lay.addWidget(lb_ref, row, 3, alignment=Qt.AlignCenter)

            lb_calc = SiriusLabel(
                self,
                self.ioc_prefix.substitute(
                    propty=self.intstrength_calcpv.format(fam)
                ),
            )
            lay.addWidget(lb_calc, row, 4, alignment=Qt.AlignRight)
            row += 1

        return docwid

    def _create_ioc_control_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("IOC Control")
        sz_pol = QSzPly(QSzPly.Preferred, QSzPly.Preferred)
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setObjectName("doc_IOCCtrl")
        docwid.setStyleSheet("#doc_IOCCtrl{min-width:20em; min-height:20em;}")

        wid = QWidget()
        docwid.setWidget(wid)
        lay = QVBoxLayout()

        wid_sts = self._get_general_sts_widget()
        lay.addWidget(wid_sts)

        wid_corr = self._get_correction_widget()
        lay.addWidget(wid_corr)

        wid_matrix = self._get_matrix_widget()
        lay.addWidget(wid_matrix)

        wid.setLayout(lay)
        return docwid

    def _create_menus(self):
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)

        menuopen = QMenu("Open", menubar)
        actions = (
            ("IOC &Log", "IOC Log", "", True, self.ioc_log),
            ("Strength &Monitor", "Strength Monitor", "", True, self.qfams_kl_table),
            ("IOC &Control", "IOC Control", "", True, self.tunefb_control),
        )
        self.setMenuBar(menubar)
        for name, tool, short, check, doc in actions:
            action = QAction(name, self)
            action.setToolTip(tool)
            action.setShortcut(short)
            action.setCheckable(check)
            action.setChecked(check)
            action.setEnabled(True)
            action.setVisible(True)
            action.toggled.connect(doc.setVisible)
            doc.visibilityChanged.connect(action.setChecked)
            menuopen.addAction(action)
        menubar.addAction(menuopen.menuAction())

    def _get_correction_widget(self):
        widcorr = QGroupBox("Correction", self)
        laycorr = QVBoxLayout()
        laycorr.setContentsMargins(0, 0, 0, 0)

        wid = QWidget()
        hbl = QHBoxLayout()
        # hbl.setContentsMargins(0, 0, 0, 0)
        spsw = PyDMStateButton(
            wid, self.ioc_prefix.substitute(propty="LoopState-Sel")
        )
        rdbl = SiriusLedState(
            wid, self.ioc_prefix.substitute(propty="LoopState-Sts")
        )
        hbl.addWidget(
            QLabel("Auto Correction State:", wid), 5, alignment=Qt.AlignLeft
        )
        hbl.addWidget(spsw, alignment=Qt.AlignRight)
        hbl.addWidget(rdbl, alignment=Qt.AlignLeft)
        wid.setLayout(hbl)
        laycorr.addWidget(wid)

        corr_tab = QTabWidget(widcorr)
        corr_tab.setObjectName(self.acc + "Tab")
        laycorr.addWidget(corr_tab)

        # Loop ################################################################
        self.wid_atcr = QWidget()
        lay_atcr = QGridLayout(self.wid_atcr)
        lay_atcr.setAlignment(Qt.AlignTop)

        _qtac = Qt.AlignCenter
        _qtal = Qt.AlignLeft
        _qtar = Qt.AlignRight

        ln = 0
        mainlbl = QLabel("General", self.wid_atcr)
        mainlbl.setStyleSheet(
            "margin-top:0em;margin-bottom:0em;font-weight:bold;"
        )
        lay_atcr.addWidget(mainlbl, ln, 0, 1, 5, alignment=_qtal)

        # Loop Frequency
        ln += 1
        freqbar_lbl = QLabel("Loop Freq. [Hz]", self.wid_atcr)
        freqpvn = "LoopFreq-{}"
        freqspinbox = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=freqpvn.format("SP")),
        )
        freqspinbox.setSingleStep(0.5)
        freqrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=freqpvn.format("RB")),
        )
        lay_atcr.addWidget(freqbar_lbl, ln, 0, alignment=_qtal)
        lay_atcr.addWidget(freqspinbox, ln, 1, alignment=_qtar)
        lay_atcr.addWidget(freqrb, ln, 2, alignment=_qtal)

        # Plane Separation
        ln += 1
        xlbl = QLabel("X", self.wid_atcr)
        ylbl = QLabel("Y", self.wid_atcr)
        xlbl.setStyleSheet("font-weight:bold;")
        ylbl.setStyleSheet("font-weight:bold;")
        lay_atcr.addWidget(xlbl, ln, 1, 1, 2, alignment=_qtac)
        lay_atcr.addWidget(ylbl, ln, 3, 1, 2, alignment=_qtac)

        #######################################################################

        # Reference Tunes
        ln += 1
        reftune_lbl = QLabel("Ref. Tune", self.wid_atcr)
        lay_atcr.addWidget(reftune_lbl, ln, 0, alignment=_qtal)

        tunexpvn = "RefTuneX-{}"
        reftunex_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tunexpvn.format("SP")),
        )
        reftunex_wid.setSingleStep(0.001)
        reftunexrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tunexpvn.format("RB")),
        )

        tuneypvn = "RefTuneY-{}"
        reftuney_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tuneypvn.format("SP")),
        )
        reftuney_wid.setSingleStep(0.001)
        reftuneyrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=tuneypvn.format("RB")),
        )

        lay_atcr.addWidget(reftunex_wid, ln, 1, alignment=_qtar)
        lay_atcr.addWidget(reftunexrb, ln, 2, alignment=_qtal)
        lay_atcr.addWidget(reftuney_wid, ln, 3, alignment=_qtar)
        lay_atcr.addWidget(reftuneyrb, ln, 4, alignment=_qtal)

        # Max Tune Err
        ln += 1
        maxtuneerr_lbl = QLabel("Max. Tune Err.", self.wid_atcr)
        lay_atcr.addWidget(maxtuneerr_lbl, ln, 0, alignment=_qtal)

        maxtunexerrpvn = "MaxTuneXErr-{}"
        maxtunexerr_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtunexerrpvn.format("SP")),
        )
        maxtunexerr_wid.setSingleStep(0.005)
        maxtunexerrrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtunexerrpvn.format("RB")),
        )

        maxtuneyerrpvn = "MaxTuneYErr-{}"
        maxtuneyerr_wid = SiriusSpinbox(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtuneyerrpvn.format("SP")),
        )
        maxtuneyerr_wid.setSingleStep(0.005)
        maxtuneyerrrb = SiriusLabel(
            self.wid_atcr,
            self.ioc_prefix.substitute(propty=maxtuneyerrpvn.format("RB")),
        )
        lay_atcr.addWidget(maxtunexerr_wid, ln, 1, alignment=_qtar)
        lay_atcr.addWidget(maxtunexerrrb, ln, 2, alignment=_qtal)
        lay_atcr.addWidget(maxtuneyerr_wid, ln, 3, alignment=_qtar)
        lay_atcr.addWidget(maxtuneyerrrb, ln, 4, alignment=_qtal)

        # Tune Source
        ln += 1
        tunesrc_lbl = QLabel("Tune Source", self.wid_atcr)
        lay_atcr.addWidget(tunesrc_lbl, ln, 0, alignment=_qtal)

        tunexsrcpvn = "TuneXSrc-{}"
        tunexsrc_cbbx = PyDMEnumComboBox(
            self, self.ioc_prefix.substitute(propty=tunexsrcpvn.format("Sel"))
        )
        self.tunexsrc_rb = SiriusLabel(
            self, self.ioc_prefix.substitute(propty=tunexsrcpvn.format("Sts"))
        )

        tuneysrcpvn = "TuneYSrc-{}"
        tuneysrc_cbbx = PyDMEnumComboBox(
            self, self.ioc_prefix.substitute(propty=tuneysrcpvn.format("Sel"))
        )
        self._tuneysrc_pv = _PV(
            self.ioc_prefix.substitute(propty=tuneysrcpvn.format("Sts")),
            connection_timeout=0.5,
        )
        self.tuneysrc_rb = SiriusLabel(
            self, self.ioc_prefix.substitute(propty=tuneysrcpvn.format("Sts"))
        )

        lay_atcr.addWidget(tunexsrc_cbbx, ln, 1, 1, 2)
        lay_atcr.addWidget(tuneysrc_cbbx, ln, 3, 1, 2)
        ln += 1
        lay_atcr.addWidget(self.tunexsrc_rb, ln, 1, 1, 2, alignment=_qtac)
        lay_atcr.addWidget(self.tuneysrc_rb, ln, 3, 1, 2, alignment=_qtac)

        # PID parameters
        ln += 1
        tempwid = QGroupBox("PID parameters", self.wid_atcr)
        hpl = QGridLayout()

        _qtac = Qt.AlignCenter
        _qtal = Qt.AlignLeft
        hpl.addWidget(
            QLabel("<h4>Kp</h4>", self.wid_atcr, alignment=_qtac), 2, 0
        )
        hpl.addWidget(
            QLabel("<h4>Ki</h4>", self.wid_atcr, alignment=_qtac), 3, 0
        )
        hpl.addWidget(
            QLabel("<h4>Kd</h4>", self.wid_atcr, alignment=_qtac), 4, 0
        )
        hpl.addWidget(
            QLabel("<h4>X</h4>", self.wid_atcr, alignment=_qtac), 1, 1, 1, 2
        )
        hpl.addWidget(
            QLabel("<h4>Y</h4>", self.wid_atcr, alignment=_qtac), 1, 3, 1, 2
        )
        self.tunepid_pvs = [
            self.ioc_prefix.substitute(propty="LoopPID" + _k + _pln + _pvt)
            for _k in ["Kp", "Ki", "Kd"]
            for _pln in ["X", "Y"]
            for _pvt in ["-SP", "-RB"]
        ]
        self.tunepid_widgets = dict(
            (
                _pv,
                SiriusSpinbox(self.wid_atcr, _pv)
                if _pv.endswith("SP")
                else SiriusLabel(self.wid_atcr, _pv),
            )
            for _pv in self.tunepid_pvs
        )
        for _pv, wid in self.tunepid_widgets.items():
            col = 1 if _pv.split("PID")[-1][2] == "X" else 3
            if _pv.endswith("RB"):
                col += 1
                align = _qtal
            else:
                wid.setSingleStep(0.05)
                align = _qtar
            row = ("Kp", "Ki", "Kd").index(_pv.split("PID")[-1][:2]) + 2
            hpl.addWidget(wid, row, col, alignment=align)
        tempwid.setLayout(hpl)
        lay_atcr.addWidget(tempwid, ln, 0, 1, 5)
        corr_tab.addTab(self.wid_atcr, "Loop")

        # Manual ##############################################################
        self.wid_optics = QWidget()
        lay_optics = QGridLayout(self.wid_optics)
        # lay_optics.setContentsMargins(0, 0, 0, 0)

        pb_updref = PyDMPushButton(
            self,
            label="Update Reference",
            pressValue=1,
            init_channel=self.ioc_prefix.substitute(propty="SetNewRefKL-Cmd"),
        )
        pb_updref.setStyleSheet(
            "min-height:2.4em; max-height:2.4em; margin-top:1em;"
        )
        lay_optics.addWidget(pb_updref, 0, 0, 1, 2)

        gb_optprm = QGroupBox("ΔTune", self)
        gb_optprm.setLayout(self._setup_optics_param_layout())
        lay_optics.addWidget(gb_optprm, 1, 0)

        corr_tab.addTab(self.wid_optics, "Manual")

        # Settings ############################################################
        wid_sett = QWidget()
        lay_sett = QGridLayout()
        # lay_sett.setContentsMargins(0, 0, 0, 0)
        lay_sett.setAlignment(Qt.AlignTop)
        _qtal = Qt.AlignLeft

        cb_method = PyDMEnumComboBox(
            self, self.ioc_prefix.substitute(propty="CorrMeth-Sel")
        )
        lb_method = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="CorrMeth-Sts")
        )
        lay_sett.addWidget(
            QLabel("Method", wid_sett), 0, 0, alignment=Qt.AlignLeft
        )
        lay_sett.addWidget(cb_method, 0, 1, Qt.AlignRight)
        lay_sett.addWidget(lb_method, 0, 2, Qt.AlignLeft)

        cb_group = PyDMEnumComboBox(
            self, self.ioc_prefix.substitute(propty="CorrGroup-Sel")
        )
        lb_group = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="CorrGroup-Sts")
        )
        lay_sett.addWidget(
            QLabel("Grouping", wid_sett), 1, 0, alignment=Qt.AlignLeft
        )
        lay_sett.addWidget(cb_group, 1, 1, Qt.AlignRight)
        lay_sett.addWidget(lb_group, 1, 2, Qt.AlignLeft)

        bt_sync = PyDMStateButton(
            self, self.ioc_prefix.substitute(propty="SyncCorr-Sel")
        )
        bt_sync.shape = 1
        lb_sync = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="SyncCorr-Sts")
        )
        lay_sett.addWidget(
            QLabel("Sync", wid_sett), 2, 0, alignment=Qt.AlignLeft
        )
        lay_sett.addWidget(bt_sync, 2, 1, Qt.AlignRight)
        lay_sett.addWidget(lb_sync, 2, 2, Qt.AlignLeft)

        wid_sett.setLayout(lay_sett)
        corr_tab.addTab(wid_sett, "Settings")

        widcorr.setLayout(laycorr)
        return widcorr

    def _setup_optics_param_layout(self):
        self.lb_x = QLabel("<h4>X</h4>", self, alignment=Qt.AlignCenter)
        self.lb_y = QLabel("<h4>Y</h4>", self, alignment=Qt.AlignCenter)
        self.lb_sp = QLabel("<h4>SP</h4>", self, alignment=Qt.AlignCenter)
        self.lb_rb = QLabel("<h4>RB</h4>", self, alignment=Qt.AlignCenter)
        self.lb_mon = QLabel(
            "<h4>Estimative</h4>", self, alignment=Qt.AlignCenter
        )

        self.sb_paramx = SiriusSpinbox(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("X", "SP")),
        )
        self.sb_paramx.setSingleStep(0.001)
        self.sb_paramy = SiriusSpinbox(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("Y", "SP")),
        )
        self.sb_paramy.setSingleStep(0.001)

        self.lb_paramx = SiriusLabel(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("X", "RB")),
        )
        self.lb_paramy = SiriusLabel(
            self,
            self.ioc_prefix.substitute(propty=self.param_pv.format("Y", "RB")),
        )

        self.lb_prmmonx = SiriusLabel(
            self,
            self.ioc_prefix.substitute(
                propty=self.param_pv.format("X", "Mon")
            ),
        )
        self.lb_prmmony = SiriusLabel(
            self,
            self.ioc_prefix.substitute(
                propty=self.param_pv.format("Y", "Mon")
            ),
        )

        self.bt_apply = PyDMPushButton(
            self,
            label="Apply",
            pressValue=1,
            init_channel=self.ioc_prefix.substitute(propty="ApplyDelta-Cmd"),
        )

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.lb_sp, 0, 1)
        lay.addWidget(self.lb_rb, 0, 2)
        lay.addWidget(self.lb_x, 1, 0)
        lay.addWidget(self.sb_paramx, 1, 1)
        lay.addWidget(self.lb_paramx, 1, 2)
        lay.addWidget(self.lb_y, 2, 0)
        lay.addWidget(self.sb_paramy, 2, 1)
        lay.addWidget(self.lb_paramy, 2, 2)
        lay.addWidget(self.lb_mon, 0, 3)
        lay.addWidget(self.lb_prmmonx, 1, 3)
        lay.addWidget(self.lb_prmmony, 2, 3)
        lay.addWidget(self.bt_apply, 3, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 5)
        lay.setColumnStretch(2, 5)
        lay.setColumnStretch(3, 5)

        return lay

    def _get_general_sts_widget(self):
        widsts = QGroupBox("Status", self)
        laysts = QVBoxLayout()
        laysts.setContentsMargins(0, 10, 0, 0)

        wid = QWidget(widsts)
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        led_sts = _StatusLed(
            self, self.ioc_prefix.substitute(propty="Status-Mon")
        )
        stslbl = QLabel("IOC Status:", self)
        stslbl.setStyleSheet("font-weight:bold;")
        lay.addWidget(stslbl, 0, 0, alignment=Qt.AlignLeft)
        lay.addWidget(led_sts, 0, 1, alignment=Qt.AlignLeft)

        conf_bt = QPushButton(qta.icon("fa5s.list-ul"), "", self)
        _hlautil.connect_window(
            conf_bt,
            _CorrParamsDetailWindow,
            parent=self,
            acc=self.acc,
            opticsparam=self.param,
            prefix=self.prefix,
            fams=self.fams,
        )
        le_cname = _ConfigLineEdit(
            self, self.ioc_prefix.substitute(propty="ConfigName-SP")
        )
        ln = 1
        lay.addWidget(QLabel("Config. Name:"), ln, 0)
        lay.addWidget(le_cname, ln, 1)
        lay.addWidget(conf_bt, ln, 2)
        lb_cname = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="ConfigName-RB")
        )
        lay.addWidget(lb_cname, ln + 1, 1)

        laysts.addWidget(wid)
        widsts.setLayout(laysts)
        return widsts

    def _get_matrix_widget(self):
        widmat = QGroupBox("Matrix", self)
        laymat = QVBoxLayout(widmat)
        laymat.setContentsMargins(0, 5, 0, 0)

        wid = self._get_matrix_main_widget(widmat)
        laymat.addWidget(wid)

        # widmat.setLayout(laymat)
        return widmat

    def _get_matrix_main_widget(self, parent):
        wid = QWidget(parent)
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        wid_rns = QGroupBox("Save", wid)
        lay_rns = QGridLayout(wid_rns)

        ln = 0
        lb_meas_name = QLabel("Name to save:", self)
        le_meas_conf_name = PyDMLineEdit(
            self, self.ioc_prefix.substitute(propty="MeasConfigName-SP")
        )
        lb_meas_conf_name = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="MeasConfigName-RB")
        )
        lay_rns.addWidget(lb_meas_name, ln, 0)
        lay_rns.addWidget(le_meas_conf_name, ln, 1)
        bt_meas_conf_save = PyDMPushButton(
            self,
            icon=qta.icon("mdi.content-save"),
            label="",
            init_channel=self.ioc_prefix.substitute(
                propty="MeasConfigSave-Cmd"
            ),
            pressValue=1,
        )
        bt_meas_conf_save.setObjectName("save")
        bt_meas_conf_save.setStyleSheet(
            "#save{min-width:25px; max-width:25px; icon-size:20px;}"
        )
        lay_rns.addWidget(bt_meas_conf_save, ln, 2, alignment=Qt.AlignRight)
        ln += 1
        lay_rns.addWidget(lb_meas_conf_name, ln, 1)

        lay.addWidget(wid_rns)

        wid_run = QGroupBox("Meas.", wid)
        lay_run = QHBoxLayout(wid_run)
        lay_run.setAlignment(Qt.AlignTop)

        lb_meas_conf_sts = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="MeasConfigStatus-Mon")
        )
        bt_meas_conf_start = PyDMPushButton(
            self,
            icon=qta.icon("fa5s.play"),
            label="",
            init_channel=self.ioc_prefix.substitute(propty="MeasConfig-Cmd"),
            pressValue=_Const.MeasCmd.Start,
        )
        bt_meas_conf_start.setObjectName("start")
        bt_meas_conf_start.setStyleSheet(
            "#start{min-width:25px; max-width:25px; icon-size:20px;}"
        )
        bt_meas_conf_stop = PyDMPushButton(
            self,
            icon=qta.icon("fa5s.stop"),
            label="",
            init_channel=self.ioc_prefix.substitute(propty="MeasConfig-Cmd"),
            pressValue=_Const.MeasCmd.Stop,
        )
        bt_meas_conf_stop.setObjectName("stop")
        bt_meas_conf_stop.setStyleSheet(
            "#stop{min-width:25px; max-width:25px; icon-size:20px;}"
        )
        bt_meas_conf_rst = PyDMPushButton(
            self,
            icon=qta.icon("fa5s.sync"),
            label="",
            init_channel=self.ioc_prefix.substitute(propty="MeasConfig-Cmd"),
            pressValue=_Const.MeasCmd.Reset,
        )
        bt_meas_conf_rst.setObjectName("rst")
        bt_meas_conf_rst.setStyleSheet(
            "#rst{min-width:25px; max-width:25px; icon-size:20px;}"
        )
        lay_run.addWidget(QLabel("Status:", wid_run), alignment=Qt.AlignLeft)
        lay_run.addWidget(lb_meas_conf_sts, alignment=Qt.AlignLeft)
        lay_run.addWidget(bt_meas_conf_start, alignment=Qt.AlignRight)
        lay_run.addWidget(bt_meas_conf_stop, alignment=Qt.AlignRight)
        lay_run.addWidget(bt_meas_conf_rst, alignment=Qt.AlignRight)

        lay.addWidget(wid_run)

        lay_rns = QGridLayout()
        wid_measconf = QGroupBox("Config. Meas.", wid)
        lay_measconf = QVBoxLayout(wid_measconf)
        lay_measconf.addWidget(self._get_matrix_measconf_widget(wid_measconf))
        lay.addWidget(wid_measconf)
        # wid.setLayout(lay)
        return wid

    def _get_matrix_measconf_widget(self, parent):
        wid = QWidget(parent)
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        mag_type = "Q"
        unit = "[1/m]"
        pvn = self.ioc_prefix.substitute(
            propty="MeasConfigDelta"
            + self.intstrength
            + "Fam"
            + mag_type
            + "F"
        )
        lb_meas_conf_foc = QLabel(
            "Fam. Δ" + self.intstrength + " " + mag_type + "F " + unit, self
        )
        sb_meas_conf_dfam_foc = SiriusSpinbox(
            self, pvn.substitute(propty_suffix="SP")
        )
        lb_meas_conf_dfam_foc = SiriusLabel(
            self, pvn.substitute(propty_suffix="RB")
        )
        lay.addWidget(lb_meas_conf_foc, 0, 0)
        lay.addWidget(sb_meas_conf_dfam_foc, 0, 1)
        lay.addWidget(lb_meas_conf_dfam_foc, 0, 2)

        pvn = self.ioc_prefix.substitute(
            propty="MeasConfigDelta"
            + self.intstrength
            + "Fam"
            + mag_type
            + "D"
        )
        lb_meas_conf_defoc = QLabel(
            "Fam. Δ" + self.intstrength + " " + mag_type + "D " + unit, self
        )
        sb_meas_conf_dfam_defoc = SiriusSpinbox(
            self, pvn.substitute(propty_suffix="SP")
        )
        lb_meas_conf_dfam_defoc = SiriusLabel(
            self, pvn.substitute(propty_suffix="RB")
        )
        lay.addWidget(lb_meas_conf_defoc, 1, 0)
        lay.addWidget(sb_meas_conf_dfam_defoc, 1, 1)
        lay.addWidget(lb_meas_conf_dfam_defoc, 1, 2)

        lb_meas_wait = QLabel("Wait [s]", self)
        sb_meas_conf_wait = SiriusSpinbox(
            self, self.ioc_prefix.substitute(propty="MeasConfigWait-SP")
        )
        lb_meas_conf_wait = SiriusLabel(
            self, self.ioc_prefix.substitute(propty="MeasConfigWait-RB")
        )
        lay.addWidget(lb_meas_wait, 2, 0)
        lay.addWidget(sb_meas_conf_wait, 2, 1)
        lay.addWidget(lb_meas_conf_wait, 2, 2)

        wid.setLayout(lay)
        return wid

    def _create_famsklplot_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("Families" + r"$\Delta$" + "KL Monitor")
        sz_pol = QSzPly(QSzPly.Preferred, QSzPly.Preferred)
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setObjectName("doc_dKLMon")
        # docwid.setStyleSheet("#doc_dKLMon{min-width:20em; min-height:30em;}")

        wid = QWidget()
        docwid.setWidget(wid)
        lay = QVBoxLayout(wid)

        wid_klplot = DeltaKLFamiliesPlot(
            ioc_prefix=self.ioc_prefix, fams=self.fams, parent=wid
        )
        lay.addWidget(wid_klplot)
        return docwid

    def _open_tunexsource_window(self):
        self._open_tunesource_window(plane="X")

    def _open_tuneysource_window(self):
        self._open_tunesource_window(plane="Y")

    def _open_tunesource_window(self, plane):
        if plane not in ["X", "Y"]:
            return

        src = self._tunexsrc_pv.value if plane == "X" \
            else self._tuneysrc_pv.value

        if src is None:
            return

        if src == 0:
            if not hasattr(self, "_open_tunespec_bt"):
                self._open_tunespec_bt = QPushButton(self)
                _hlautil.connect_window(
                    self._open_tunespec_bt,
                    _TuneWindow,
                    parent=self,
                    prefix=self.prefix,
                    section="SI",
                )
            self._open_tunespec_bt.click()

        elif src in (1, 2, 3):
            plane_bbb = "H" if plane == "X" else "V"

            attr = f"_open_bbb_{plane_bbb.lower()}_bt"
            if not hasattr(self, attr):
                setattr(self, attr, QPushButton(self))
                _hlautil.connect_window(
                    getattr(self, attr),
                    _BbBWindow,
                    parent=self,
                    prefix=self.prefix,
                    device=f"SI-Glob:DI-BbBProc-{plane_bbb}",
                )

            getattr(self, attr).click()


class DeltaKLFamiliesPlot(SiriusWaveformPlot):
    """."""

    def __init__(
        self,
        ioc_prefix,
        fams,
        parent=None,
        diff=False,
        color=None,
        symbol=None,
        yrange_lim=None,
        prefix=_VACA_PREFIX,
    ):
        """."""
        super().__init__(parent=parent)
        self.ioc_prefix = ioc_prefix
        self.prefix = prefix
        self.fams = fams
        self.channels = dict()
        self.diff = bool(diff)

        self.setObjectName("graph")
        self.setStyleSheet("#graph {min-height: 13em; min-width: 20em;}")

        self.autoRangeX = False
        if yrange_lim:
            self.autoRangeY = False
            _lim_dkl = float(yrange_lim)  # -2e-5
            self.setRange(
                xRange=[0, len(fams) - 1], yRange=[-_lim_dkl, +_lim_dkl]
            )
        else:
            self.autoRangeY = True
        self.showXGrid = True
        self.showYGrid = True
        self.axisColor = QColor(0, 0, 0)
        self.backgroundColor = QColor(255, 255, 255)
        self.showLegend = False

        color = color if color else "black"
        symb = symbol if symbol else "o"
        self.addChannel(
            y_channel="FAKE:DeltaKLFamilies",
            name="Delta KL" if not self.diff else "KL-RB - RefKL",
            redraw_mode=2,
            color=color,
            lineStyle=0,
            lineWidth=1,
            symbol=symb,
            symbolSize=7,
        )

        axis = self.getAxis("bottom")
        labels = [(i, f) for i, f in enumerate(fams)]
        axis.setTicks([labels])

        self.curve_dkl = self.curveAtIndex(0)
        self.curve_dkl.setSymbolBrush(QColor(color))
        self.curve_dkl.setVisible(True)

        for fam in self.fams:
            if not self.diff:
                ch = SiriusConnectionSignal(
                    self.ioc_prefix.substitute(propty=f"DeltaKL{fam}-Mon")
                )
                ch.fam = fam
                ch.new_value_signal[float].connect(self._update_curve)
                self.channels[fam] = ch
            else:
                pv_rb = _PVName(f"SI-Fam:PS-{fam}").substitute(
                    propty="KL-RB", prefix=self.prefix
                )
                ch_rb = SiriusConnectionSignal(pv_rb)
                ch_rb.new_value_signal[float].connect(self._update_curve)

                ch_ref = SiriusConnectionSignal(
                    self.ioc_prefix.substitute(propty=f"RefKL{fam}-Mon")
                )
                ch_ref.new_value_signal[float].connect(self._update_curve)

                self.channels[fam] = {"rb": ch_rb, "ref": ch_ref}

        self._update_curve()

        self.setSizePolicy(QSzPly.Expanding, QSzPly.Expanding)

    def _get_value(self, fam):
        if not self.diff:
            ch = self.channels[fam]
            if ch.connected and ch.value is not None:
                return float(ch.value)
            return _np.nan

        ch_rb = self.channels[fam]["rb"]
        ch_ref = self.channels[fam]["ref"]

        if (
            ch_rb.connected
            and ch_rb.value is not None
            and ch_ref.connected
            and ch_ref.value is not None
        ):
            return float(ch_rb.value) - float(ch_ref.value)
        return _np.nan

    def _update_curve(self):
        x = _np.arange(len(self.fams), dtype=float)
        y = _np.array([self._get_value(fam) for fam in self.fams], dtype=float)
        valid = _np.isfinite(y)
        if not valid.any():
            return
        self.curve_dkl.receiveXWaveform(x[valid])
        self.curve_dkl.receiveYWaveform(y[valid])


class TuneSpectrumPlot(SiriusWaveformPlot):
    """."""

    def __init__(self, prefix="", plane="H", ioc_prefix=None, parent=None):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.plane = plane.upper()
        self.ioc_prefix = ioc_prefix

        self.current_source = None
        self.x_signal = None
        self.y_signal = None
        self.shift_signal = None
        self._shift = 0.0
        self.marker_xsignal = None
        self.marker_ysignal = None

        self._x_data_full = None
        self._y_data_full = None
        self.band_khz = 20.0

        self.autoRangeX = True
        self.autoRangeY = True
        self.showXGrid = True
        self.showYGrid = True
        self.axisColor = QColor(0, 0, 0)
        self.backgroundColor = QColor(255, 255, 255)
        self.showLegend = False

        self.addChannel(
            y_channel=f"FAKE:Spectrum{self.plane}",
            name=f"Tune {self.plane}",
            redraw_mode=2,
            color="blue" if self.plane == "H" else "red",
            lineWidth=1,
            lineStyle=Qt.SolidLine,
        )
        self.curve = self.curveAtIndex(0)
        self.curve.setVisible(True)

        self.addChannel(
            x_channel=f"FAKE:MarkerX-{self.plane}",
            y_channel=f"FAKE:MarkerY-{self.plane}",
            name=f"Tune {self.plane}",
            redraw_mode=2,
            # color='black',
            lineStyle=1,
            lineWidth=1,
            symbol='o',
            symbolSize=7,
        )
        self.marker = self.curveAtIndex(1)
        self.marker.setVisible(True)

        self.ref_tune_signal = SiriusConnectionSignal(
            self.ioc_prefix.substitute(
                propty="RefTuneX-RB" if self.plane == "H" else "RefTuneY-RB"
            )
        )
        self.ref_line = _InfLine(
            angle=90,
            movable=False,
            pen=_Pen(color=(0, 0, 0), width=2),
            label=f"RefTune{'X' if self.plane == 'H' else 'Y'}",
            labelOpts={
                "position": 0.10,
                "color": (0, 0, 0),
                "fill": (255, 255, 255, 0),
                "movable": False,
                "anchors": [(0, 0.5), (0, 0.5)],
            },
        )
        self.addItem(self.ref_line)
        self.ref_line.setVisible(False)

        tunesrc_pv = 'Tune{}Src-Sts'.format(
            'X' if self.plane == 'H' else 'Y'
        )
        self.tunesrc_signal = SiriusConnectionSignal(
            self.ioc_prefix.substitute(propty=tunesrc_pv)
        )
        self.tunesrc_signal.new_value_signal[int].connect(
            self._handle_source_change
        )
        self.ref_tune_signal.new_value_signal[float].connect(
            self._update_reftune
        )

        # testing on sirius@lnls451-linux: _Const.TuneSrc does not exist
        try:
            _fields = _Const.TuneSrc._fields
        except Exception as e:
            print(e)
            _fields = ("TuneSpec", "BbB_SRAM_M2", "BbB_SB_M1", "BbB_SRAM_M1")
        self._enum_map = {i: s for i, s in enumerate(_fields)}

        value = self.tunesrc_signal.value
        if value is not None:
            self._handle_source_change(value)
        value = self.ref_tune_signal.value
        if value is not None:
            self._update_reftune(value)

    def _as_array(self, data):
        if data is None:
            return None
        return _np.atleast_1d(_np.asarray(data, dtype=float))

    def _handle_source_change(self, value):
        src = self._enum_map.get(value, str(value))
        self._set_source(src)

    def _set_source(self, src):
        if src == self.current_source:
            return

        self.current_source = src

        if self.x_signal:
            self.x_signal.disconnect()
        if self.y_signal:
            self.y_signal.disconnect()
        if self.shift_signal:
            self.shift_signal.disconnect()
        if self.marker_xsignal:
            self.marker_xsignal.disconnect()
        if self.marker_ysignal:
            self.marker_ysignal.disconnect()

        self.x_signal = None
        self.y_signal = None
        self.shift_signal = None
        self.marker_xsignal = None
        self.marker_ysignal = None

        self._x_data_full = None
        self._y_data_full = None

        prefix = self.prefix
        self.prefix = ''
        if "TuneSpec" in src:
            self._configure_tunespec_source()
        elif "BbB" in src:
            mode = src.split("_")[1]
            self._configure_bbb_source(mode)
        self.prefix = prefix

    def _configure_tunespec_source(self):
        plane = self.plane

        # self.shift_signal = SiriusConnectionSignal(
        #     _PVName(f"SI-Glob:DI-Tune-{plane}:RevN-RB").substitute(
        #         prefix=self.prefix
        #     )
        # )
        # self.x_signal = SiriusConnectionSignal(
        #     _PVName(f"SI-Glob:DI-Tune-{plane}:TuneFracArray-Mon").substitute(
        #         prefix=self.prefix
        #     )
        # )
        # self.y_signal = SiriusConnectionSignal(
        #     _PVName(f"SI-Glob:DI-TuneProc-{plane}:Trace-Mon").substitute(
        #         prefix=self.prefix
        #     )
        # )
        self.marker_xsignal = SiriusConnectionSignal(
            _PVName(f"SI-Glob:DI-Tune-{plane}:TuneFrac-Mon").substitute(
                prefix=self.prefix
            )
        )
        self.marker_ysignal = SiriusConnectionSignal(
            _PVName(f"SI-Glob:DI-Tune-{plane}:MarkY1-Mon").substitute(
                prefix=self.prefix
            )
        )

        # self.x_signal.new_value_signal[_np.ndarray].connect(self._receive_x)
        # self.y_signal.new_value_signal[_np.ndarray].connect(self._receive_y)
        # self.shift_signal.new_value_signal[float].connect(self._receive_shift)
        self.marker_xsignal.new_value_signal[float].connect(
            self._update_marker_chx
        )
        self.marker_ysignal.new_value_signal[float].connect(
            self._update_marker_chy
        )

    def _configure_bbb_source(self, mode):
        plane = self.plane

        self.shift_signal = SiriusConnectionSignal(
            _PVName(f"SI-Glob:DI-BbBProc-{plane}:FREV").substitute(
                prefix=self.prefix
            )
        )

        self.x_signal = SiriusConnectionSignal(
            _PVName(f"SI-Glob:DI-BbBProc-{plane}:{mode}_FREQ").substitute(
                prefix=self.prefix
            )
        )
        spec = "SPEC" if mode == "SRAM" else "MAG"
        self.y_signal = SiriusConnectionSignal(
            _PVName(f"SI-Glob:DI-BbBProc-{plane}:{mode}_{spec}").substitute(
                prefix=self.prefix
            )
        )

        self.x_signal.new_value_signal[_np.ndarray].connect(self._receive_x)
        self.y_signal.new_value_signal[_np.ndarray].connect(self._receive_y)
        self.shift_signal.new_value_signal[float].connect(self._receive_shift)

    def _update_marker_chx(self, value):
        self.marker.receiveXWaveform(value)

    def _update_marker_chy(self, value):
        self.marker.receiveYWaveform(value)

    def _update_reftune(self, value):
        if value is not None:
            self.ref_line.setPos(value)
            self.ref_line.setVisible(True)
        else:
            self.ref_line.setVisible(False)

    def _receive_shift(self, data):
        self._shift = float(data)
        self._update_plot()

    def _receive_x(self, data):
        self._x_data_full = self._as_array(data)
        self._update_plot()

    def _receive_y(self, data):
        self._y_data_full = self._as_array(data)
        self._update_plot()

    def _get_span_hz(self):
        ref_tune = self.ref_tune_signal.value
        if ref_tune is None:
            return None

        rev_freq = self.shift_signal.value
        if rev_freq is None:
            return None

        freq = float(ref_tune) * rev_freq
        return (freq - self.band_khz / 2, freq + self.band_khz / 2)

    def _update_plot(self):
        if self._x_data_full is None or self._y_data_full is None:
            return

        x = self._x_data_full
        y = self._y_data_full

        n = min(len(x), len(y))
        if n == 0:
            return
        x = x[:n]
        y = y[:n]

        if "BbB" in self.current_source:
            span = self._get_span_hz()
            if span is not None:
                fmin, fmax = span
                mask = (x >= fmin) & (x <= fmax)

                if mask.any():
                    x = x[mask]
                    y = y[mask]

            y = y / self._shift
            x = x / self._shift

        else:
            x = x - self._shift
            y = y - self._shift

        self.curve.receiveXWaveform(x)
        self.curve.receiveYWaveform(y)
