"""DCCT settings module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, QGroupBox, \
    QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QSpacerItem, \
    QSizePolicy as QSzPly
import qtawesome as qta

from pydm.widgets import PyDMEnumComboBox, PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.diagbeam.dcct.csdev import Const as _DCCTc, get_dcct_database
from siriuspy.epics import PV as _PV

from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import PyDMStateButton, SiriusConnectionSignal, \
    SiriusLedState, SiriusLedAlert, SiriusLabel, SiriusSpinbox
from siriushla import util as _hlautil
from siriushla.as_ti_control.hl_trigger import HLTriggerSimple


class DCCTSettings(QWidget):
    """DCCT Settings Main Widget."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.dcct_prefix = device.substitute(prefix=self.prefix)
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout()
        lay.addWidget(QLabel('<h3>Settings</h3>', self,
                             alignment=Qt.AlignHCenter | Qt.AlignBottom))
        lay.setStretch(0, 1)

        # Measure
        l_reliablemeas = QLabel('Reliability: ')
        self.led_ReliableMeas = SiriusLedAlert(
            self, self.dcct_prefix.substitute(propty='ReliableMeas-Mon'))

        l_curr = QLabel('Current [mA]: ', self, alignment=Qt.AlignRight)
        self.label_current = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='Current-Mon'))
        self.led_StoredEBeam = SiriusLedState(
            self, self.dcct_prefix.substitute(propty='StoredEBeam-Mon'))
        hlay_current = QHBoxLayout()
        hlay_current.addWidget(self.label_current)
        hlay_current.addWidget(self.led_StoredEBeam)

        l_enbl = QLabel('Enable:', self)
        self.pydmstatebutton_Enbl = PyDMStateButton(
            self, self.dcct_prefix.substitute(propty='Enbl-Sel'))
        self.pydmstatebutton_Enbl.shape = 1
        self.led_Enbl = SiriusLedState(
            self, self.dcct_prefix.substitute(propty='Enbl-Sts'))
        hlay_enbl = QHBoxLayout()
        hlay_enbl.addWidget(self.pydmstatebutton_Enbl)
        hlay_enbl.addWidget(self.led_Enbl)

        l_meastrig = QLabel('Trigger Source:', self)
        self.pydmenumcombobox_MeasTrg = PyDMEnumComboBox(
            self, self.dcct_prefix.substitute(propty='MeasTrg-Sel'))
        self.pydmlabel_MeasTrg = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='MeasTrg-Sts'))
        hlay_meastrig = QHBoxLayout()
        hlay_meastrig.addWidget(self.pydmenumcombobox_MeasTrg)
        hlay_meastrig.addWidget(self.pydmlabel_MeasTrg)

        if 'SI' in self.device:
            l_range = QLabel('Range: ', self)
            self.pydmenumcombobox_Range = PyDMEnumComboBox(
                self, self.dcct_prefix.substitute(propty='Range-Sel'))
            self.pydmlabel_Range = SiriusLabel(
                self, self.dcct_prefix.substitute(propty='Range-Sts'))
            hlay_range = QHBoxLayout()
            hlay_range.addWidget(self.pydmenumcombobox_Range)
            hlay_range.addWidget(self.pydmlabel_Range)
            hlay_range.setContentsMargins(0, 0, 0, 0)

        l_measmode = QLabel('Mode: ', self)
        self.pydmenumcombobox_MeasMode = PyDMEnumComboBox(
            self, self.dcct_prefix.substitute(propty='MeasMode-Sel'))
        self.pydmlabel_MeasMode = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='MeasMode-Sts'))
        hlay_measmode = QHBoxLayout()
        hlay_measmode.addWidget(self.pydmenumcombobox_MeasMode)
        hlay_measmode.addWidget(self.pydmlabel_MeasMode)
        hlay_measmode.setContentsMargins(0, 0, 0, 0)

        glay_mode = QGridLayout()
        self.normalmode_widget = self._setupMeasSettingsWidget('Normal')
        self.fastmode_widget = self._setupMeasSettingsWidget('Fast')
        glay_mode.addWidget(self.normalmode_widget, 0, 0)
        glay_mode.addWidget(self.fastmode_widget, 0, 0)
        glay_mode.setContentsMargins(0, 0, 0, 0)
        self.mode_channel = SiriusConnectionSignal(
            self.dcct_prefix.substitute(propty='MeasMode-Sel'))
        self.mode_channel.new_value_signal.connect(self._showMeasModeSettings)

        # Details
        self.pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.pb_details.setToolTip('Open details')
        self.pb_details.setObjectName('detail')
        self.pb_details.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        detail_window = create_window_from_widget(
            DCCTSettingsDetails, title=self.device+' Settings Details')
        _hlautil.connect_window(
            self.pb_details, detail_window,
            self, prefix=self.prefix, device=self.device)

        gbox_gen = QGroupBox('Measure')
        glay_gen = QGridLayout(gbox_gen)
        glay_gen.setAlignment(Qt.AlignVCenter)
        glay_gen.addWidget(l_curr, 0, 0)
        glay_gen.addLayout(hlay_current, 0, 1)
        glay_gen.addWidget(l_reliablemeas, 1, 0)
        glay_gen.addWidget(self.led_ReliableMeas, 1, 1, alignment=Qt.AlignLeft)
        glay_gen.addWidget(l_enbl, 2, 0)
        glay_gen.addLayout(hlay_enbl, 2, 1)
        glay_gen.addWidget(l_meastrig, 3, 0)
        glay_gen.addLayout(hlay_meastrig, 3, 1)
        if 'SI' in self.device:
            glay_gen.addWidget(l_range, 4, 0)
            glay_gen.addLayout(hlay_range, 4, 1)
        glay_gen.addWidget(l_measmode, 5, 0)
        glay_gen.addLayout(hlay_measmode, 5, 1)
        glay_gen.addLayout(glay_mode, 6, 0, 1, 2)
        glay_gen.addWidget(self.pb_details, 7, 0, 1, 2,
                           alignment=Qt.AlignRight)
        gbox_gen.setStyleSheet("""
            .QLabel{
                qproperty-alignment: 'AlignVCenter | AlignRight';
                min-width: 6em;}
            PyDMLed{
                min-width: 6em;}""")
        lay.addWidget(gbox_gen)
        lay.setStretch(1, 7)

        # Trigger
        self.trigger_widget = QGroupBox('Trigger')
        hbl = QHBoxLayout(self.trigger_widget)
        hbl.addWidget(HLTriggerSimple(
            self.trigger_widget, device=self.device.substitute(dis='TI'),
            prefix=self.prefix))
        lay.addWidget(self.trigger_widget)
        lay.setStretch(2, 3)

        self.setLayout(lay)
        self.setStyleSheet("""
            QSpinBox, QComboBox, QPushButton,
            SiriusSpinbox, PyDMEnumComboBox, SiriusLabel{
                min-width:6em; max-width:6em;}
            .QLabel{max-height:1.5em;}""")

    def _setupMeasSettingsWidget(self, mode):
        if mode == 'Normal':
            prefix = self.dcct_prefix
            visible = True
        elif mode == 'Fast':
            prefix = self.dcct_prefix.substitute(propty_name=mode)
            visible = False

        l_smpcnt = QLabel('Sample Count: ', self)
        spinbox_SampleCnt = SiriusSpinbox(
            self, prefix.substitute(propty=prefix.propty_name+'SampleCnt-SP'))
        label_SampleCnt = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'SampleCnt-RB'))
        hlay_smpcnt = QHBoxLayout()
        hlay_smpcnt.addWidget(spinbox_SampleCnt)
        hlay_smpcnt.addWidget(label_SampleCnt)

        l_measperiod = QLabel('Period [s]: ', self)
        spinbox_MeasPeriod = SiriusSpinbox(
            self, prefix.substitute(propty=prefix.propty_name+'MeasPeriod-SP'))
        label_MeasPeriod = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'MeasPeriod-RB'))
        hlay_measperiod = QHBoxLayout()
        hlay_measperiod.addWidget(spinbox_MeasPeriod)
        hlay_measperiod.addWidget(label_MeasPeriod)

        flay_modesettings = QFormLayout()
        flay_modesettings.addRow(l_smpcnt, hlay_smpcnt)
        flay_modesettings.addRow(l_measperiod, hlay_measperiod)
        flay_modesettings.setContentsMargins(0, 0, 0, 0)
        modesettings = QWidget(self)
        modesettings.setLayout(flay_modesettings)
        modesettings.setVisible(visible)
        return modesettings

    def _showMeasModeSettings(self, value):
        if value == _DCCTc.MeasModeSel.Normal:
            self.normalmode_widget.setVisible(True)
            self.fastmode_widget.setVisible(False)
        elif value == _DCCTc.MeasModeSel.Fast:
            self.normalmode_widget.setVisible(False)
            self.fastmode_widget.setVisible(True)


class DCCTSettingsDetails(QWidget):
    """DCCT Settings Details Widget."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        if 'BO' in device:
            self.setObjectName('BOApp')
        else:
            self.setObjectName('SIApp')
        self.dcct_prefix = device.substitute(prefix=self.prefix)
        self._db = get_dcct_database()
        self._setupUi()

    def _setupUi(self):
        self.gbox_reliablemeas = self._setupReliableMeasWidget()

        self.gbox_generalsettings = self._setupGeneralSettingsWidget()

        self.gbox_trigger = self._setupTriggerWidget()

        self.gbox_config = self._setupConfigurationWidget()

        self.gbox_normalmode = self._setupMeasSettingsWidget('Normal')
        self.gbox_fastmode = self._setupMeasSettingsWidget('Fast')
        lay_mode = QGridLayout()
        lay_mode.addWidget(self.gbox_normalmode, 0, 0)
        lay_mode.addWidget(self.gbox_fastmode, 0, 0)
        self.mode_channel = SiriusConnectionSignal(
            self.dcct_prefix.substitute(propty='MeasMode-Sel'))
        self.mode_channel.new_value_signal.connect(self._showMeasModeSettings)

        lay = QGridLayout()
        lay.addWidget(
            QLabel('<h3>'+self.device+' Settings Details</h3>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self.gbox_reliablemeas, 1, 0)
        lay.addWidget(self.gbox_generalsettings, 2, 0)
        lay.addWidget(self.gbox_config, 3, 0)
        lay.addWidget(self.gbox_trigger, 3, 1)
        lay.addLayout(lay_mode, 1, 1, 2, 1)
        lay.setVerticalSpacing(15)
        lay.setHorizontalSpacing(15)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 3)
        lay.setRowStretch(2, 7)
        lay.setRowStretch(3, 2)
        self.setLayout(lay)

        self.setStyleSheet("""
            SiriusSpinbox, SiriusLabel{
                min-width:6em; max-width:6em;
                qproperty-alignment: AlignCenter;}
            PyDMLedMultiChannel, PyDMStateButton, PyDMEnumComboBox{
                min-width:6em; max-width:6em;}""")

    def _setupReliableMeasWidget(self):
        gbox_reliablemeas = QGroupBox('Measure Reliability Status', self)
        gbox_reliablemeas.setStyleSheet("""
            .QLabel{min-height:1.29em; max-height:1.29em;}
        """)

        lay_reliablemeas = QGridLayout(gbox_reliablemeas)
        relmeas_count = self._db['ReliableMeasLabels-Cte']['count']
        self.relmeas_labels = list()
        for idx in range(relmeas_count):
            led = SiriusLedAlert(
                parent=self, init_channel=self.dcct_prefix.substitute(
                    propty='ReliableMeas-Mon'), bit=idx)
            lay_reliablemeas.addWidget(led, idx, 0)
            lbl = QLabel('', self)
            self.relmeas_labels.append(lbl)
            lay_reliablemeas.addWidget(lbl, idx, 1)
        lay_reliablemeas.setColumnStretch(0, 1)
        lay_reliablemeas.setColumnStretch(1, 10)

        self.reliablemeas_channel = _PV(
            self.dcct_prefix.substitute(propty='ReliableMeasLabels-Cte'),
            callback=self._updateReliableMeasLabels)

        return gbox_reliablemeas

    def _setupGeneralSettingsWidget(self):
        gbox_generalsettings = QGroupBox('General Measurement Settings', self)

        l_enbl = QLabel('Enable:', self)
        self.pydmstatebutton_Enbl = PyDMStateButton(
            self, self.dcct_prefix.substitute(propty='Enbl-Sel'))
        self.pydmstatebutton_Enbl.shape = 1
        self.led_Enbl = SiriusLedState(
            self, self.dcct_prefix.substitute(propty='Enbl-Sts'))
        hlay_enbl = QHBoxLayout()
        hlay_enbl.addWidget(self.pydmstatebutton_Enbl)
        hlay_enbl.addWidget(self.led_Enbl)

        l_meastrig = QLabel('Trigger Source: ', self)
        self.pydmenumcombobox_MeasTrg = PyDMEnumComboBox(
            self, self.dcct_prefix.substitute(propty='MeasTrg-Sel'))
        self.pydmlabel_MeasTrg = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='MeasTrg-Sts'))
        hlay_meastrig = QHBoxLayout()
        hlay_meastrig.addWidget(self.pydmenumcombobox_MeasTrg)
        hlay_meastrig.addWidget(self.pydmlabel_MeasTrg)

        l_trigmiss = QLabel('Trigger Is Missing?', self)
        self.led_TrgMiss = SiriusLedAlert(
            self, self.dcct_prefix.substitute(propty='TrgIsMissing-Mon'))
        hlay_trigmiss = QHBoxLayout()
        hlay_trigmiss.addWidget(self.led_TrgMiss)
        hlay_trigmiss.setAlignment(Qt.AlignLeft)

        l_range = QLabel('Range: ', self)
        self.pydmenumcombobox_Range = PyDMEnumComboBox(
            self, self.dcct_prefix.substitute(propty='Range-Sel'))
        self.pydmlabel_Range = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='Range-Sts'))
        hlay_range = QHBoxLayout()
        hlay_range.addWidget(self.pydmenumcombobox_Range)
        hlay_range.addWidget(self.pydmlabel_Range)

        l_lowlimenbl = QLabel('Low Beam Current Detection: ', self)
        self.pydmstatebutton_LowLimEnbl = PyDMStateButton(
            self, self.dcct_prefix.substitute(propty='LowLimEnbl-Sel'))
        self.pydmstatebutton_LowLimEnbl.shape = 1
        self.pydmlabel_LowLimEnbl = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='LowLimEnbl-Sts'))
        hlay_lowlimenbl = QHBoxLayout()
        hlay_lowlimenbl.addWidget(self.pydmstatebutton_LowLimEnbl)
        hlay_lowlimenbl.addWidget(self.pydmlabel_LowLimEnbl)

        l_currthold = QLabel('Current Threshold [mA]: ', self)
        self.pydmspinbox_CurrThold = SiriusSpinbox(
            self, self.dcct_prefix.substitute(propty='CurrThold-SP'))
        self.pydmlabel_CurrThold = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='CurrThold-RB'))
        hlay_currthold = QHBoxLayout()
        hlay_currthold.addWidget(self.pydmspinbox_CurrThold)
        hlay_currthold.addWidget(self.pydmlabel_CurrThold)

        l_hfreject = QLabel('High Frequency Rejection: ', self)
        self.pydmstatebutton_HFReject = PyDMStateButton(
            self, self.dcct_prefix.substitute(propty='HFReject-Sel'))
        self.pydmstatebutton_HFReject.shape = 1
        self.pydmlabel_HFReject = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='HFReject-Sts'))
        hlay_hfreject = QHBoxLayout()
        hlay_hfreject.addWidget(self.pydmstatebutton_HFReject)
        hlay_hfreject.addWidget(self.pydmlabel_HFReject)

        l_measmode = QLabel('Mode: ', self)
        self.pydmenumcombobox_MeasMode = PyDMEnumComboBox(
            self, self.dcct_prefix.substitute(propty='MeasMode-Sel'))
        self.pydmlabel_MeasMode = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='MeasMode-Sts'))
        hlay_measmode = QHBoxLayout()
        hlay_measmode.addWidget(self.pydmenumcombobox_MeasMode)
        hlay_measmode.addWidget(self.pydmlabel_MeasMode)

        flay_generalsettings = QFormLayout()
        flay_generalsettings.setLabelAlignment(Qt.AlignRight)
        flay_generalsettings.setFormAlignment(Qt.AlignCenter)
        flay_generalsettings.addRow(l_enbl, hlay_enbl)
        flay_generalsettings.addRow(l_meastrig, hlay_meastrig)
        flay_generalsettings.addRow(l_trigmiss, hlay_trigmiss)
        flay_generalsettings.addRow(l_range, hlay_range)
        flay_generalsettings.addItem(
            QSpacerItem(1, 10, QSzPly.Ignored, QSzPly.Preferred))
        flay_generalsettings.addRow(l_lowlimenbl, hlay_lowlimenbl)
        flay_generalsettings.addRow(l_currthold, hlay_currthold)
        flay_generalsettings.addRow(l_hfreject, hlay_hfreject)
        flay_generalsettings.addItem(
            QSpacerItem(1, 10, QSzPly.Ignored, QSzPly.Preferred))
        flay_generalsettings.addRow(l_measmode, hlay_measmode)
        gbox_generalsettings.setLayout(flay_generalsettings)
        return gbox_generalsettings

    def _setupMeasSettingsWidget(self, mode):
        if mode == 'Normal':
            prefix = self.dcct_prefix
            visible = True
        elif mode == 'Fast':
            prefix = self.dcct_prefix.substitute(propty_name=mode)
            visible = False

        gbox_modesettings = QGroupBox(mode+' Measurement Mode Settings', self)

        l_smpcnt = QLabel('Sample Count: ', self)
        spinbox_SampleCnt = SiriusSpinbox(
            self, prefix.substitute(propty=prefix.propty_name+'SampleCnt-SP'))
        label_SampleCnt = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'SampleCnt-RB'))
        hlay_smpcnt = QHBoxLayout()
        hlay_smpcnt.addWidget(spinbox_SampleCnt)
        hlay_smpcnt.addWidget(label_SampleCnt)

        l_measperiod = QLabel('Period [s]: ', self)
        spinbox_MeasPeriod = SiriusSpinbox(
            self, prefix.substitute(propty=prefix.propty_name+'MeasPeriod-SP'))
        label_MeasPeriod = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'MeasPeriod-RB'))
        hlay_measperiod = QHBoxLayout()
        hlay_measperiod.addWidget(spinbox_MeasPeriod)
        hlay_measperiod.addWidget(label_MeasPeriod)

        l_measupdateperiod = QLabel('Measured Period [s]: ', self)
        label_MeasUpdatePeriod = SiriusLabel(
            self, self.dcct_prefix.substitute(propty='MeasUpdatePeriod-Mon'))

        l_imped = QLabel('Impedance: ', self)
        enumcombobox_Imped = PyDMEnumComboBox(
            self, prefix.substitute(propty=prefix.propty_name+'Imped-Sel'))
        label_Imped = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'Imped-Sts'))
        hlay_imped = QHBoxLayout()
        hlay_imped.addWidget(enumcombobox_Imped)
        hlay_imped.addWidget(label_Imped)

        l_offset = QLabel('Relative Offset Enable: ', self)
        statebutton_RelEnbl = PyDMStateButton(
            self, prefix.substitute(propty=prefix.propty_name+'RelEnbl-Sel'))
        statebutton_RelEnbl.shape = 1
        statebutton_RelEnbl.setStyleSheet('min-width:6em; max-width:6em;')
        label_RelEnbl = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'RelEnbl-Sts'))
        hlay_offset = QHBoxLayout()
        hlay_offset.addWidget(statebutton_RelEnbl)
        hlay_offset.addWidget(label_RelEnbl)

        l_rellvl = QLabel('Relative Offset Level [V]: ', self)
        spinbox_RelLvl = SiriusSpinbox(
            self, prefix.substitute(propty=prefix.propty_name+'RelLvl-SP'))
        label_RelLvl = SiriusLabel(
            self, prefix.substitute(propty=prefix.propty_name+'RelLvl-RB'))
        label_RelLvl.precisionFromPV = False
        label_RelLvl.precision = 9
        pushbutton_RelAcq = PyDMPushButton(
            parent=self, label='Acquire Offset', pressValue=1,
            init_channel=prefix.substitute(
                propty=prefix.propty_name+'RelAcq-Cmd'))
        pushbutton_RelAcq.setAutoDefault(False)
        pushbutton_RelAcq.setDefault(False)
        hlay_rellvl = QHBoxLayout()
        hlay_rellvl.addWidget(spinbox_RelLvl)
        hlay_rellvl.addWidget(label_RelLvl)
        hlay_rellvl.addWidget(pushbutton_RelAcq)

        flay_modesettings = QFormLayout()
        flay_modesettings.setLabelAlignment(Qt.AlignRight)
        flay_modesettings.setFormAlignment(Qt.AlignHCenter)
        flay_modesettings.addRow(l_smpcnt, hlay_smpcnt)
        flay_modesettings.addRow(l_measperiod, hlay_measperiod)
        flay_modesettings.addRow(l_measupdateperiod, label_MeasUpdatePeriod)
        flay_modesettings.addRow(l_imped, hlay_imped)
        flay_modesettings.addRow(l_offset, hlay_offset)
        flay_modesettings.addRow(l_rellvl, hlay_rellvl)

        if mode == 'Normal':
            l_linesync = QLabel('Line Synchronization: ', self)
            statebutton_LineSync = PyDMStateButton(self, prefix.substitute(
                propty=prefix.propty_name+'LineSync-Sel'))
            statebutton_LineSync.shape = 1
            statebutton_LineSync.setStyleSheet('min-width:6em; max-width:6em;')
            label_LineSync = SiriusLabel(self, prefix.substitute(
                propty=prefix.propty_name+'LineSync-Sts'))
            hlay_linesync = QHBoxLayout()
            hlay_linesync.addWidget(statebutton_LineSync)
            hlay_linesync.addWidget(label_LineSync)

            label_avg = QLabel('<h4>Average Filter</h4>', self)
            l_avgenbl = QLabel('Enable: ', self)
            statebutton_AvgFilterEnbl = PyDMStateButton(
                self, prefix.substitute(
                    propty=prefix.propty_name+'AvgFilterEnbl-Sel'))
            statebutton_AvgFilterEnbl.shape = 1
            label_AvgFilterEnbl = SiriusLabel(self, prefix.substitute(
                propty=prefix.propty_name+'AvgFilterEnbl-Sts'))
            hlay_avgenbl = QHBoxLayout()
            hlay_avgenbl.addWidget(statebutton_AvgFilterEnbl)
            hlay_avgenbl.addWidget(label_AvgFilterEnbl)

            l_avgcnt = QLabel('Samples: ', self)
            spinbox_AvgFilterCount = SiriusSpinbox(self, prefix.substitute(
                propty=prefix.propty_name+'AvgFilterCnt-SP'))
            label_AvgFilterCount = SiriusLabel(self, prefix.substitute(
                propty=prefix.propty_name+'AvgFilterCnt-RB'))
            hlay_avgcnt = QHBoxLayout()
            hlay_avgcnt.addWidget(spinbox_AvgFilterCount)
            hlay_avgcnt.addWidget(label_AvgFilterCount)

            l_avgtyp = QLabel('Type: ', self)
            enumcombobox_AvgFilterTyp = PyDMEnumComboBox(
                self, self.dcct_prefix.substitute(propty='AvgFilterTyp-Sel'))
            label_AvgFilterTyp = SiriusLabel(
                self, self.dcct_prefix.substitute(propty='AvgFilterTyp-Sts'))
            hlay_avgtyp = QHBoxLayout()
            hlay_avgtyp.addWidget(enumcombobox_AvgFilterTyp)
            hlay_avgtyp.addWidget(label_AvgFilterTyp)

            l_avgwin = QLabel('Noise window size [%]: ', self)
            spinbox_AvgFilterWind = SiriusSpinbox(self, prefix.substitute(
                propty=prefix.propty_name+'AvgFilterWind-SP'))
            label_AvgFilterWind = SiriusLabel(self, prefix.substitute(
                propty=prefix.propty_name+'AvgFilterWind-RB'))
            hlay_avgwin = QHBoxLayout()
            hlay_avgwin.addWidget(spinbox_AvgFilterWind)
            hlay_avgwin.addWidget(label_AvgFilterWind)

            flay_modesettings.addRow(l_linesync, hlay_linesync)
            flay_modesettings.addRow(QLabel(''))
            flay_modesettings.addRow(label_avg)
            flay_modesettings.addRow(l_avgenbl, hlay_avgenbl)
            flay_modesettings.addRow(l_avgcnt, hlay_avgcnt)
            flay_modesettings.addRow(l_avgtyp, hlay_avgtyp)
            flay_modesettings.addRow(l_avgwin, hlay_avgwin)

        gbox_modesettings.setLayout(flay_modesettings)
        gbox_modesettings.setVisible(visible)
        gbox_modesettings.setStyleSheet("""
            SiriusLabel{
                min-width:6em; max-width:6em;
                qproperty-alignment: AlignCenter;}
            PyDMLedMultiChannel, PyDMStateButton, PyDMEnumComboBox{
                min-width:6em; max-width:6em;}""")
        return gbox_modesettings

    def _setupConfigurationWidget(self):
        statebutton_Test = PyDMStateButton(
            self, self.dcct_prefix.substitute(propty='Test-Sel'))
        statebutton_Test.shape = 1
        statebutton_Test.setStyleSheet('min-width:6em; max-width:6em;')
        label_Test = SiriusLabel(self, self.dcct_prefix.substitute(
            propty='Test-Sts'))
        hlay_test = QHBoxLayout()
        hlay_test.addWidget(statebutton_Test)
        hlay_test.addWidget(label_Test)

        self.bt_dl = PyDMPushButton(
            parent=self, pressValue=1, icon=qta.icon('fa5s.sync'),
            init_channel=self.dcct_prefix.substitute(propty='Download-Cmd'))
        self.bt_dl.setObjectName('bt_dl')
        self.bt_dl.setStyleSheet(
            '#bt_dl{min-width:25px; max-width:25px; icon-size:20px;}')

        gbox_test = QGroupBox('Configurations')
        lay = QFormLayout(gbox_test)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow('Enable test current: ', hlay_test)
        lay.addRow('Download Configurations: ', self.bt_dl)
        return gbox_test

    def _setupTriggerWidget(self):
        gbox_trigger = QGroupBox('Trigger', self)
        hbl = QHBoxLayout(gbox_trigger)
        hbl.addWidget(HLTriggerSimple(
            gbox_trigger, device=self.device.substitute(dis='TI'),
            prefix=self.prefix))
        return gbox_trigger

    def _updateReliableMeasLabels(self, pvname, value,  **kwargs):
        if value:
            for idx, lbl in enumerate(self.relmeas_labels):
                lbl.setText(value[idx])

    def _showMeasModeSettings(self, value):
        if value == _DCCTc.MeasModeSel.Normal:
            self.gbox_normalmode.setVisible(True)
            self.gbox_fastmode.setVisible(False)
        elif value == _DCCTc.MeasModeSel.Fast:
            self.gbox_normalmode.setVisible(False)
            self.gbox_fastmode.setVisible(True)
