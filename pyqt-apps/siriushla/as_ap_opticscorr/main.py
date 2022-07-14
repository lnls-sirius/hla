"""OpticsCorr main module."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, \
    QPushButton, QVBoxLayout, QSpacerItem, QSizePolicy as QSzPly, \
    QHBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMPushButton, PyDMEnumComboBox, \
    PyDMSpinbox, PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.opticscorr.csdev import Const as _Const

from siriushla import util as _hlautil
from siriushla.widgets import SiriusMainWindow, PyDMLogLabel, PyDMStateButton
from siriushla.as_ps_control import PSDetailWindow as _PSDetailWindow
from .details import CorrParamsDetailWindow as _CorrParamsDetailWindow
from .custom_widgets import StatusLed as _StatusLed, \
    ConfigLineEdit as _ConfigLineEdit


class OpticsCorrWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(OpticsCorrWindow, self).__init__(parent)
        self.prefix = prefix
        self.acc = acc.upper()
        self.param = opticsparam
        self.ioc_prefix = _PVName(
            self.acc+'-Glob:AP-'+self.param.title()+'Corr')
        self.ioc_prefix = self.ioc_prefix.substitute(prefix=self.prefix)
        self.title = self.acc + ' ' + self.param.title() + ' Correction'

        if self.param == 'tune':
            self.param_pv = 'DeltaTune{0}-{1}'
            self.intstrength = 'KL'
            self.intstrength_calcdesc = 'DeltaKL-Mon'
            self.intstrength_calcpv = 'DeltaKL{}-Mon'
            self.fams = list(_Const.SI_QFAMS_TUNECORR) if self.acc == 'SI' \
                else list(_Const.BO_QFAMS_TUNECORR)
        elif self.param == 'chrom':
            self.param_pv = 'Chrom{0}-{1}'
            self.intstrength = 'SL'
            self.intstrength_calcdesc = 'CalcSL-Mon'
            self.intstrength_calcpv = 'SL{}-Mon'
            self.fams = list(_Const.SI_SFAMS_CHROMCORR) if self.acc == 'SI' \
                else list(_Const.BO_SFAMS_CHROMCORR)

        self.setWindowTitle(self.title)
        self.setObjectName(self.acc+'App')
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        label = QLabel('<h3>'+self.title+'</h3>', self)
        label.setStyleSheet("""
            min-height:1.55em; max-height: 1.55em;
            qproperty-alignment: 'AlignVCenter | AlignRight';
            background-color: qlineargradient(spread:pad, x1:1, y1:0.0227273,
                              x2:0, y2:0, stop:0 rgba(173, 190, 207, 255),
                              stop:1 rgba(213, 213, 213, 255));""")

        self.gb_status = QGroupBox('Status', self)
        self.gb_status.setLayout(self._setupStatusLayout())

        self.wid_optics = QWidget()
        lay_optics = QGridLayout(self.wid_optics)
        lay_optics.setContentsMargins(0, 0, 0, 0)
        self.gb_optprm = QGroupBox(
            'ΔTune' if self.param == 'tune' else 'Chromaticity', self)
        self.gb_optprm.setLayout(self._setupOpticsParamLayout())
        if self.param == 'tune':
            self.pb_updref = PyDMPushButton(
                self, label='Update Reference', pressValue=1,
                init_channel=self.ioc_prefix.substitute(propty='SetNewRefKL-Cmd'))
            self.pb_updref.setStyleSheet('min-height:2.4em; max-height:2.4em;')
            lay_optics.addWidget(self.pb_updref, 0, 0, 1, 2)
            lay_optics.addWidget(self.gb_optprm, 1, 0)

            if self.acc == 'SI':
                self.gb_digmon = QGroupBox('Tune Monitor', self)
                self.gb_digmon.setLayout(self._setupDigMonLayout())
                lay_optics.addWidget(self.gb_digmon, 1, 1)
                lay_optics.setColumnStretch(0, 3)
                lay_optics.setColumnStretch(1, 1)
        else:
            lay_optics.addWidget(self.gb_optprm, 0, 0)

        self.gb_fams = QGroupBox('Families', self)
        self.gb_fams.setLayout(self._setupFamiliesLayout())
        self.gb_fams.setSizePolicy(QSzPly.Preferred, QSzPly.Expanding)

        self.gb_iocctrl = QGroupBox('IOC Control', self)
        self.gb_iocctrl.setLayout(self._setupIOCControlLayout())

        cwt = QWidget()
        self.setCentralWidget(cwt)
        if self.acc == 'SI':
            vlay1 = QVBoxLayout()
            vlay1.setAlignment(Qt.AlignTop)
            vlay1.addWidget(self.wid_optics)
            vlay1.addWidget(self.gb_fams)
            lay = QGridLayout(cwt)
            lay.addWidget(label, 0, 0, 1, 2)
            lay.addLayout(vlay1, 1, 0, alignment=Qt.AlignTop)
            lay.addWidget(self.gb_iocctrl, 1, 1)
            lay.addWidget(self.gb_status, 2, 0, 1, 2)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
            lay.setRowStretch(0, 1)
            lay.setRowStretch(1, 15)
            lay.setRowStretch(2, 5)
        else:
            lay = QVBoxLayout(cwt)
            lay.addWidget(label)
            lay.addWidget(self.wid_optics)
            lay.addWidget(self.gb_fams)
            lay.addWidget(self.gb_iocctrl)
            lay.addWidget(self.gb_status)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignCenter;
            }""")

    def _setupStatusLayout(self):
        self.log_label = PyDMLogLabel(
            self, self.ioc_prefix.substitute(propty='Log-Mon'))

        lay = QVBoxLayout()
        lay.addWidget(self.log_label)
        return lay

    def _setupOpticsParamLayout(self):
        self.lb_x = QLabel('<h4>X</h4>', self, alignment=Qt.AlignCenter)
        self.lb_y = QLabel('<h4>Y</h4>', self, alignment=Qt.AlignCenter)
        self.lb_sp = QLabel('<h4>SP</h4>', self, alignment=Qt.AlignCenter)
        self.lb_rb = QLabel('<h4>RB</h4>', self, alignment=Qt.AlignCenter)
        self.lb_mon = QLabel(
            '<h4>Estimative</h4>', self, alignment=Qt.AlignCenter)

        self.sb_paramx = PyDMSpinbox(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('X', 'SP')))
        self.sb_paramx.showStepExponent = False
        self.sb_paramy = PyDMSpinbox(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('Y', 'SP')))
        self.sb_paramy.showStepExponent = False

        self.lb_paramx = PyDMLabel(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('X', 'RB')))
        self.lb_paramy = PyDMLabel(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('Y', 'RB')))

        self.lb_prmmonx = PyDMLabel(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('X', 'Mon')))
        self.lb_prmmony = PyDMLabel(self, self.ioc_prefix.substitute(
            propty=self.param_pv.format('Y', 'Mon')))

        self.bt_apply = PyDMPushButton(
            self, label='Apply', pressValue=1,
            init_channel=self.ioc_prefix.substitute(
                propty='ApplyDelta-Cmd'))

        lay = QGridLayout()
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

        if self.acc == 'SI' and self.param == 'chrom':
            self._icon_absval = qta.icon(
                'mdi.alpha-a', 'mdi.alpha-b', 'mdi.alpha-s', options=[
                    dict(scale_factor=1.5, offset=(-0.4, 0.0)),
                    dict(scale_factor=1.5, offset=(0.0, 0.0)),
                    dict(scale_factor=1.5, offset=(+0.4, 0.0))])
            self._icon_delta = qta.icon('mdi.delta')
            self._is_setting = 'absolut'
            self.pb_change_sp = QPushButton(self._icon_absval, '', self)
            self.pb_change_sp.clicked.connect(self._change_chrom_sp)

            self.sb_paramx_delta = PyDMSpinbox(
                self, self.ioc_prefix.substitute(propty='DeltaChromX-SP'))
            self.sb_paramx_delta.showStepExponent = False
            self.sb_paramx_delta.setVisible(False)

            self.sb_paramy_delta = PyDMSpinbox(
                self, self.ioc_prefix.substitute(propty='DeltaChromY-SP'))
            self.sb_paramy_delta.showStepExponent = False
            self.sb_paramy_delta.setVisible(False)

            self.lb_paramx_delta = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='DeltaChromX-RB'))
            self.lb_paramx_delta.setVisible(False)
            self.lb_paramy_delta = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='DeltaChromY-RB'))
            self.lb_paramy_delta.setVisible(False)

            self.lb_mon.setText('Implem.\nEstimative')
            self.lb_mon.setStyleSheet('font-weight: bold;')
            self.lb_calcmon = QLabel(
                'Calcd.\nEstimative', self, alignment=Qt.AlignCenter)
            self.lb_calcmon.setStyleSheet('font-weight: bold;')

            self.lb_prmcalcmonx = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='CalcChromX-Mon'))
            self.lb_prmcalcmony = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='CalcChromY-Mon'))

            lay.addWidget(self.pb_change_sp, 0, 0)
            lay.addWidget(self.sb_paramx_delta, 1, 1)
            lay.addWidget(self.sb_paramy_delta, 2, 1)
            lay.addWidget(self.lb_paramx_delta, 1, 2)
            lay.addWidget(self.lb_paramy_delta, 2, 2)
            lay.addWidget(self.lb_calcmon, 0, 4)
            lay.addWidget(self.lb_prmcalcmonx, 1, 4)
            lay.addWidget(self.lb_prmcalcmony, 2, 4)
        return lay

    def _setupDigMonLayout(self):
        lb_x = QLabel('<h4>X</h4>', self, alignment=Qt.AlignCenter)
        lb_y = QLabel('<h4>Y</h4>', self, alignment=Qt.AlignCenter)
        self.lb_tunex = PyDMLabel(self, 'SI-Glob:DI-Tune-H:TuneFrac-Mon')
        self.lb_tuney = PyDMLabel(self, 'SI-Glob:DI-Tune-V:TuneFrac-Mon')

        lay = QGridLayout()
        lay.addWidget(lb_x, 0, 0)
        lay.addWidget(self.lb_tunex, 0, 1)
        lay.addWidget(lb_y, 1, 0)
        lay.addWidget(self.lb_tuney, 1, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 5)
        return lay

    def _setupFamiliesLayout(self):
        lay = QGridLayout()

        lb_family = QLabel('<h4>Family</h4>', self, alignment=Qt.AlignCenter)
        lb_family.setStyleSheet('max-height:1.29em;')
        lay.addWidget(lb_family, 0, 1)

        lb_rbdesc = QLabel('<h4>'+self.intstrength+'-RB</h4>', self,
                           alignment=Qt.AlignCenter)
        lb_rbdesc.setStyleSheet('max-height:1.29em;')
        lay.addWidget(lb_rbdesc, 0, 2)

        if self.param == 'tune':
            lb_refdesc = QLabel('<h4>RefKL-Mon</h4>', self,
                                alignment=Qt.AlignCenter)
            lb_refdesc.setStyleSheet('max-height:1.29em;')
            lay.addWidget(lb_refdesc, 0, 3)

        lb_lastddesc = QLabel('<h4>'+self.intstrength_calcdesc+'</h4>', self,
                              alignment=Qt.AlignCenter)
        lb_lastddesc.setStyleSheet('max-height:1.29em;')
        lay.addWidget(lb_lastddesc, 0, 4)

        row = 1
        for fam in self.fams:
            dev_name = _PVName(self.acc+'-Fam:PS-'+fam)
            pref_name = dev_name.substitute(prefix=self.prefix)

            pbt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            pbt.setObjectName('pbt')
            pbt.setStyleSheet("""
                #pbt{
                    min-width:25px; max-width:25px;
                    min-height:25px; max-height:25px;
                    icon-size:20px;}""")
            _hlautil.connect_window(
                pbt, _PSDetailWindow, parent=self, psname=dev_name)
            lay.addWidget(pbt, row, 0)

            lb_name = QLabel(fam, self, alignment=Qt.AlignCenter)
            lay.addWidget(lb_name, row, 1)

            lb_rb = PyDMLabel(self, pref_name.substitute(
                propty=self.intstrength+'-RB'))
            lay.addWidget(lb_rb, row, 2)

            if self.param == 'tune':
                lb_ref = PyDMLabel(self, self.ioc_prefix.substitute(
                    propty='RefKL'+fam+'-Mon'))
                lay.addWidget(lb_ref, row, 3)

            lb_calc = PyDMLabel(self, self.ioc_prefix.substitute(
                propty=self.intstrength_calcpv.format(fam)))
            lay.addWidget(lb_calc, row, 4)
            row += 1
        return lay

    def _setupIOCControlLayout(self):
        lay = QGridLayout()

        lb_sts = QLabel('<h4>Status</h4>', self)
        self.led_sts = _StatusLed(self, self.ioc_prefix.substitute(
            propty='Status-Mon'))
        lay.addWidget(lb_sts, 0, 0)
        lay.addWidget(self.led_sts, 0, 1, alignment=Qt.AlignLeft)

        lb_conf = QLabel('<h4>Configuration</h4>')
        self.bt_dtls = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        _hlautil.connect_window(
            self.bt_dtls, _CorrParamsDetailWindow, parent=self,
            acc=self.acc, opticsparam=self.param,
            prefix=self.prefix, fams=self.fams)
        lay.addWidget(lb_conf, 2, 0, 1, 2)
        lay.addWidget(self.bt_dtls, 2, 2, alignment=Qt.AlignRight)

        lb_cname = QLabel('Name', self)
        self.le_cname = _ConfigLineEdit(
            self, self.ioc_prefix.substitute(
                propty='ConfigName-SP'))
        self.lb_cname = PyDMLabel(self, self.ioc_prefix.substitute(
            propty='ConfigName-RB'))
        lay.addWidget(lb_cname, 3, 0)
        lay.addWidget(self.le_cname, 3, 1, 1, 2)
        lay.addWidget(self.lb_cname, 4, 1, 1, 2)

        row = 5
        if self.acc == 'SI':
            lay.addItem(
                QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 5, 0)
            row = 6

            if self.param == 'chrom':
                lb_meas_chrom = QLabel('<h4>Chrom. Measurement</h4>')
                lay.addWidget(lb_meas_chrom, 6, 0, 1, 3)

                lb_meas_chrom_dfRF = QLabel('ΔFreq RF [Hz]', self)
                self.sb_meas_chrom_dfRF = PyDMSpinbox(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromDeltaFreqRF-SP'))
                self.sb_meas_chrom_dfRF.showStepExponent = False
                self.lb_meas_chrom_dfRF = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromDeltaFreqRF-RB'))
                lay.addWidget(lb_meas_chrom_dfRF, 7, 0)
                lay.addWidget(self.sb_meas_chrom_dfRF, 7, 1)
                lay.addWidget(self.lb_meas_chrom_dfRF, 7, 2)

                lb_meas_chrom_wait = QLabel('Wait Tune [s]', self)
                self.sb_meas_chrom_wait = PyDMSpinbox(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromWaitTune-SP'))
                self.sb_meas_chrom_wait.showStepExponent = False
                self.lb_meas_chrom_wait = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromWaitTune-RB'))
                lay.addWidget(lb_meas_chrom_wait, 8, 0)
                lay.addWidget(self.sb_meas_chrom_wait, 8, 1)
                lay.addWidget(self.lb_meas_chrom_wait, 8, 2)

                lb_meas_chrom_nrsteps = QLabel('Nr Steps', self)
                self.sb_meas_chrom_nrsteps = PyDMSpinbox(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromNrSteps-SP'))
                self.sb_meas_chrom_nrsteps.showStepExponent = False
                self.lb_meas_chrom_nrsteps = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromNrSteps-RB'))
                lay.addWidget(lb_meas_chrom_nrsteps, 9, 0)
                lay.addWidget(self.sb_meas_chrom_nrsteps, 9, 1)
                lay.addWidget(self.lb_meas_chrom_nrsteps, 9, 2)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 10, 0)

                lb_meas_chrom_x = QLabel('Meas. Chrom X', self)
                self.lb_meas_chrom_x = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromX-Mon'))
                lay.addWidget(lb_meas_chrom_x, 11, 0)
                lay.addWidget(self.lb_meas_chrom_x, 11, 1)

                lb_meas_chrom_y = QLabel('Meas. Chrom Y', self)
                self.lb_meas_chrom_y = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromY-Mon'))
                lay.addWidget(lb_meas_chrom_y, 12, 0)
                lay.addWidget(self.lb_meas_chrom_y, 12, 1)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 13, 0)

                self.lb_meas_chrom_sts = PyDMLabel(
                    self, self.ioc_prefix.substitute(
                        propty='MeasChromStatus-Mon'))
                self.bt_meas_chrom_start = PyDMPushButton(
                    self, icon=qta.icon('fa5s.play'), label='',
                    init_channel=self.ioc_prefix.substitute(
                        propty='MeasChrom-Cmd'),
                    pressValue=_Const.MeasCmd.Start)
                self.bt_meas_chrom_start.setObjectName('start')
                self.bt_meas_chrom_start.setStyleSheet(
                    '#start{min-width:25px; max-width:25px; icon-size:20px;}')
                self.bt_meas_chrom_stop = PyDMPushButton(
                    self, icon=qta.icon('fa5s.stop'), label='',
                    init_channel=self.ioc_prefix.substitute(
                        propty='MeasChrom-Cmd'),
                    pressValue=_Const.MeasCmd.Stop)
                self.bt_meas_chrom_stop.setObjectName('stop')
                self.bt_meas_chrom_stop.setStyleSheet(
                    '#stop{min-width:25px; max-width:25px; icon-size:20px;}')
                self.bt_meas_chrom_rst = PyDMPushButton(
                    self, icon=qta.icon('fa5s.sync'), label='',
                    init_channel=self.ioc_prefix.substitute(
                        propty='MeasChrom-Cmd'),
                    pressValue=_Const.MeasCmd.Reset)
                self.bt_meas_chrom_rst.setObjectName('rst')
                self.bt_meas_chrom_rst.setStyleSheet(
                    '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
                hbox_cmd = QHBoxLayout()
                hbox_cmd.addWidget(self.bt_meas_chrom_start)
                hbox_cmd.addWidget(self.bt_meas_chrom_stop)
                hbox_cmd.addWidget(self.bt_meas_chrom_rst)
                lay.addWidget(self.lb_meas_chrom_sts, 14, 0, 1, 2)
                lay.addLayout(hbox_cmd, 14, 2)

                lay.addItem(
                    QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), 15, 0)
                row = 15

            # configuration measurement
            lb_meas_conf = QLabel('<h4>Config. Measurement</h4>')
            lay.addWidget(lb_meas_conf, row+1, 0, 1, 3)

            mag_type = 'Q' if self.param == 'tune' else 'S'
            unit = '[1/m]' if self.param == 'tune' else '[1/m2]'

            pvn = self.ioc_prefix.substitute(
                propty='MeasConfigDelta'+self.intstrength+'Fam'+mag_type+'F')
            lb_meas_conf_dfamF = QLabel(
                'Fam. Δ'+self.intstrength+' '+mag_type+'F '+unit, self)
            self.sb_meas_conf_dfamF = PyDMSpinbox(
                self, pvn.substitute(propty_suffix='SP'))
            self.sb_meas_conf_dfamF.showStepExponent = False
            self.lb_meas_conf_dfamF = PyDMLabel(
                self, pvn.substitute(propty_suffix='RB'))
            lay.addWidget(lb_meas_conf_dfamF, row+2, 0)
            lay.addWidget(self.sb_meas_conf_dfamF, row+2, 1)
            lay.addWidget(self.lb_meas_conf_dfamF, row+2, 2)

            pvn = self.ioc_prefix.substitute(
                propty='MeasConfigDelta'+self.intstrength+'Fam'+mag_type+'D')
            lb_meas_conf_dfamD = QLabel(
                'Fam. Δ'+self.intstrength+' '+mag_type+'D '+unit, self)
            self.sb_meas_conf_dfamD = PyDMSpinbox(
                self, pvn.substitute(propty_suffix='SP'))
            self.sb_meas_conf_dfamD.showStepExponent = False
            self.lb_meas_conf_dfamD = PyDMLabel(
                self, pvn.substitute(propty_suffix='RB'))
            lay.addWidget(lb_meas_conf_dfamD, row+3, 0)
            lay.addWidget(self.sb_meas_conf_dfamD, row+3, 1)
            lay.addWidget(self.lb_meas_conf_dfamD, row+3, 2)

            lb_meas_conf_wait = QLabel('Wait [s]', self)
            self.sb_meas_conf_wait = PyDMSpinbox(
                self, self.ioc_prefix.substitute(propty='MeasConfigWait-SP'))
            self.sb_meas_conf_wait.showStepExponent = False
            self.lb_meas_conf_wait = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='MeasConfigWait-RB'))
            lay.addWidget(lb_meas_conf_wait, row+4, 0)
            lay.addWidget(self.sb_meas_conf_wait, row+4, 1)
            lay.addWidget(self.lb_meas_conf_wait, row+4, 2)

            lb_meas_conf_cname = QLabel('Name to save', self)
            self.le_meas_conf_name = PyDMLineEdit(
                self, self.ioc_prefix.substitute(propty='MeasConfigName-SP'))
            self.lb_meas_conf_name = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='MeasConfigName-RB'))
            lay.addWidget(lb_meas_conf_cname, row+5, 0)
            lay.addWidget(self.le_meas_conf_name, row+5, 1, 1, 2)
            lay.addWidget(self.lb_meas_conf_name, row+6, 1, 1, 2)

            lb_meas_conf_save = QLabel('Force Save', self)
            self.bt_meas_conf_save = PyDMPushButton(
                self, icon=qta.icon('mdi.content-save'), label='',
                init_channel=self.ioc_prefix.substitute(
                    propty='MeasConfigSave-Cmd'),
                pressValue=1)
            self.bt_meas_conf_save.setObjectName('save')
            self.bt_meas_conf_save.setStyleSheet(
                '#save{min-width:25px; max-width:25px; icon-size:20px;}')
            lay.addWidget(lb_meas_conf_save, row+7, 0)
            lay.addWidget(
                self.bt_meas_conf_save, row+7, 1, alignment=Qt.AlignLeft)

            lay.addItem(
                QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), row+8, 0)

            self.lb_meas_conf_sts = PyDMLabel(
                self, self.ioc_prefix.substitute(
                    propty='MeasConfigStatus-Mon'))
            self.bt_meas_conf_start = PyDMPushButton(
                self, icon=qta.icon('fa5s.play'), label='',
                init_channel=self.ioc_prefix.substitute(
                    propty='MeasConfig-Cmd'),
                pressValue=_Const.MeasCmd.Start)
            self.bt_meas_conf_start.setObjectName('start')
            self.bt_meas_conf_start.setStyleSheet(
                '#start{min-width:25px; max-width:25px; icon-size:20px;}')
            self.bt_meas_conf_stop = PyDMPushButton(
                self, icon=qta.icon('fa5s.stop'), label='',
                init_channel=self.ioc_prefix.substitute(
                    propty='MeasConfig-Cmd'),
                pressValue=_Const.MeasCmd.Stop)
            self.bt_meas_conf_stop.setObjectName('stop')
            self.bt_meas_conf_stop.setStyleSheet(
                '#stop{min-width:25px; max-width:25px; icon-size:20px;}')
            self.bt_meas_conf_rst = PyDMPushButton(
                self, icon=qta.icon('fa5s.sync'), label='',
                init_channel=self.ioc_prefix.substitute(
                    propty='MeasConfig-Cmd'),
                pressValue=_Const.MeasCmd.Reset)
            self.bt_meas_conf_rst.setObjectName('rst')
            self.bt_meas_conf_rst.setStyleSheet(
                '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
            hbox_cmd = QHBoxLayout()
            hbox_cmd.addWidget(self.bt_meas_conf_start)
            hbox_cmd.addWidget(self.bt_meas_conf_stop)
            hbox_cmd.addWidget(self.bt_meas_conf_rst)
            lay.addWidget(self.lb_meas_conf_sts, row+9, 0, 1, 2)
            lay.addLayout(hbox_cmd, row+9, 2)

            lay.addItem(
                QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Fixed), row+10, 0)

            # correction settings
            lb_corr = QLabel('<h4>Settings</h4>')
            lay.addWidget(lb_corr, row+11, 0, 1, 3)

            lb_meth = QLabel('Method', self)
            self.cb_method = PyDMEnumComboBox(
                self, self.ioc_prefix.substitute(propty='CorrMeth-Sel'))
            self.lb_method = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='CorrMeth-Sts'))
            lay.addWidget(lb_meth, row+12, 0)
            lay.addWidget(self.cb_method, row+12, 1)
            lay.addWidget(self.lb_method, row+12, 2)

            lb_grp = QLabel('Grouping', self)
            self.cb_group = PyDMEnumComboBox(
                self, self.ioc_prefix.substitute(propty='CorrGroup-Sel'))
            self.lb_group = PyDMLabel(
                self, self.ioc_prefix.substitute(propty='CorrGroup-Sts'))
            lay.addWidget(lb_grp, row+13, 0)
            lay.addWidget(self.cb_group, row+13, 1)
            lay.addWidget(self.lb_group, row+13, 2)

            if self.param == 'tune':
                lb_sync = QLabel('Sync', self)
                self.bt_sync = PyDMStateButton(
                    self, self.ioc_prefix.substitute(propty='SyncCorr-Sel'))
                self.bt_sync.shape = 1
                self.lb_sync = PyDMLabel(
                    self, self.ioc_prefix.substitute(propty='SyncCorr-Sts'))
                lay.addWidget(lb_sync, row+14, 0)
                lay.addWidget(self.bt_sync, row+14, 1)
                lay.addWidget(self.lb_sync, row+14, 2)
            row = row + 15

        lay.addItem(
            QSpacerItem(1, 20, QSzPly.Ignored, QSzPly.Expanding), row, 0)
        return lay

    def _change_chrom_sp(self):
        cond = self._is_setting == 'absolut'
        self._is_setting = 'delta' if cond else 'absolut'
        icon = self._icon_delta if cond else self._icon_absval
        textX = '<h4>Δ-SP</h4>' if cond else '<h4>SP</h4>'
        textY = '<h4>Δ-RB</h4>' if cond else '<h4>RB</h4>'
        self.sb_paramx.setVisible(not cond)
        self.lb_paramx.setVisible(not cond)
        self.sb_paramy.setVisible(not cond)
        self.lb_paramy.setVisible(not cond)
        self.sb_paramx_delta.setVisible(cond)
        self.lb_paramx_delta.setVisible(cond)
        self.sb_paramy_delta.setVisible(cond)
        self.lb_paramy_delta.setVisible(cond)
        self.pb_change_sp.setIcon(icon)
        self.lb_sp.setText(textX)
        self.lb_rb.setText(textY)
