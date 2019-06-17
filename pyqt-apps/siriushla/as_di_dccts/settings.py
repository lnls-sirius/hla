"""DCCT settings module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, QGroupBox, \
    QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout
import epics
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMPushButton
from siriuspy.csdevice.dccts import Const as _DCCTc
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import PyDMStateButton, SiriusConnectionSignal, \
    SiriusLedAlert, PyDMLedMultiChannel
from siriushla import util as _hlautil
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed


class DCCTSettings(QWidget):
    """DCCT Settings Main Widget."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.dcct_prefix = prefix + device + ':'
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout()
        lay.addWidget(QLabel('<h3>Settings</h3>', self,
                             alignment=Qt.AlignCenter))
        lay.setStretch(0, 1)

        # Measure
        l_reliablemeas = QLabel('Reliability: ')
        self.led_ReliableMeas = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon')

        l_measmode = QLabel('Mode: ', self)
        self.pydmenumcombobox_MeasMode = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sel')
        self.pydmlabel_MeasMode = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sts')
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
            self.dcct_prefix+'MeasMode-Sel')
        self.mode_channel.new_value_signal.connect(self._showMeasModeSettings)

        l_meastrig = QLabel('Trigger\nSource:', self)
        self.pydmenumcombobox_MeasTrg = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sel')
        self.pydmlabel_MeasTrg = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sts')
        hlay_meastrig = QHBoxLayout()
        hlay_meastrig.addWidget(self.pydmenumcombobox_MeasTrg)
        hlay_meastrig.addWidget(self.pydmlabel_MeasTrg)

        l_trgdelay = QLabel('Delay After\nTrigger [s]:', self)
        self.pydmspinbox_TrgDelay = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-SP')
        self.pydmspinbox_TrgDelay.showStepExponent = False
        self.pydmlabel_TrgDelay = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-RB')
        hlay_trgdelay = QHBoxLayout()
        hlay_trgdelay.addWidget(self.pydmspinbox_TrgDelay)
        hlay_trgdelay.addWidget(self.pydmlabel_TrgDelay)
        hlay_trgdelay.setContentsMargins(0, 0, 0, 0)

        gbox_gen = QGroupBox('Measure')
        glay_gen = QGridLayout(gbox_gen)
        glay_gen.setVerticalSpacing(10)
        glay_gen.setHorizontalSpacing(10)
        glay_gen.addWidget(l_reliablemeas, 0, 0)
        glay_gen.addWidget(self.led_ReliableMeas, 0, 1, alignment=Qt.AlignLeft)
        glay_gen.addWidget(l_measmode, 1, 0)
        glay_gen.addLayout(hlay_measmode, 1, 1)
        glay_gen.addLayout(glay_mode, 2, 0, 1, 2)
        glay_gen.addWidget(l_meastrig, 3, 0)
        glay_gen.addLayout(hlay_meastrig, 3, 1)
        glay_gen.addWidget(l_trgdelay, 4, 0)
        glay_gen.addLayout(hlay_trgdelay, 4, 1)
        gbox_gen.setStyleSheet("""
            .QLabel{
                qproperty-alignment: 'AlignVCenter | AlignRight';
                min-width: 6em;}""")
        lay.addWidget(gbox_gen)
        lay.setStretch(1, 7)

        # Trigger
        self.trigger_widget = QGroupBox('Trigger')
        self.trigger_widget.setLayout(_create_trigger_layout(
            self, self.prefix, self.device))
        lay.addWidget(self.trigger_widget)
        lay.setStretch(2, 3)

        # Details
        self.pb_opendetails = QPushButton('More settings', self)
        detail_window = create_window_from_widget(
            DCCTSettingsDetails, title=self.device+' Settings Details')
        _hlautil.connect_window(
            self.pb_opendetails, detail_window,
            self, prefix=self.prefix, device=self.device)
        lay.addWidget(self.pb_opendetails, alignment=Qt.AlignRight)
        lay.setStretch(3, 1)
        lay

        self.setLayout(lay)
        self.setStyleSheet("""
            QSpinBox, QComboBox, QPushButton,
            PyDMSpinbox, PyDMEnumComboBox, PyDMLabel{
                min-width:6em; max-width:6em;}
            .QLabel{max-height:1.5em;}""")

    def _setupMeasSettingsWidget(self, mode):
        if mode == 'Normal':
            prefix = self.dcct_prefix
            visible = True
        elif mode == 'Fast':
            prefix = self.dcct_prefix + mode
            visible = False

        l_smpcnt = QLabel('Sample Count: ', self)
        spinbox_SampleCnt = PyDMSpinbox(
            parent=self, init_channel=prefix+'SampleCnt-SP')
        spinbox_SampleCnt.showStepExponent = False
        label_SampleCnt = PyDMLabel(
            parent=self, init_channel=prefix+'SampleCnt-RB')
        hlay_smpcnt = QHBoxLayout()
        hlay_smpcnt.addWidget(spinbox_SampleCnt)
        hlay_smpcnt.addWidget(label_SampleCnt)

        l_measperiod = QLabel('Period [s]: ', self)
        spinbox_MeasPeriod = PyDMSpinbox(
            parent=self, init_channel=prefix+'MeasPeriod-SP')
        spinbox_MeasPeriod.showStepExponent = False
        label_MeasPeriod = PyDMLabel(
            parent=self, init_channel=prefix+'MeasPeriod-RB')
        hlay_measperiod = QHBoxLayout()
        hlay_measperiod.addWidget(spinbox_MeasPeriod)
        hlay_measperiod.addWidget(label_MeasPeriod)

        glay_modesettings = QGridLayout()
        glay_modesettings.addWidget(l_smpcnt, 0, 0)
        glay_modesettings.addLayout(hlay_smpcnt, 0, 1)
        glay_modesettings.addWidget(l_measperiod, 1, 0)
        glay_modesettings.addLayout(hlay_measperiod, 1, 1)
        glay_modesettings.setContentsMargins(0, 0, 0, 0)
        modesettings = QWidget(self)
        modesettings.setLayout(glay_modesettings)
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
        self.device = device
        self.dcct_prefix = self.prefix + device + ':'
        self._setupUi()

    def _setupUi(self):
        self.gbox_reliablemeas = self._setupReliableMeasWidget()

        self.gbox_generalsettings = self._setupGeneralSettingsWidget()

        self.gbox_normalmode = self._setupMeasSettingsWidget('Normal')
        self.gbox_fastmode = self._setupMeasSettingsWidget('Fast')
        lay_mode = QGridLayout()
        lay_mode.addWidget(self.gbox_normalmode, 0, 0)
        lay_mode.addWidget(self.gbox_fastmode, 0, 0)
        self.mode_channel = SiriusConnectionSignal(
            self.dcct_prefix+'MeasMode-Sel')
        self.mode_channel.new_value_signal.connect(self._showMeasModeSettings)

        self.gbox_trigger = self._setupTriggerWidget()

        lay = QGridLayout()
        lay.addWidget(
            QLabel('<h3>'+self.device+' Settings Details</h3>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self.gbox_reliablemeas, 1, 0)
        lay.addWidget(self.gbox_generalsettings, 2, 0)
        lay.addWidget(self.gbox_trigger, 3, 0)
        lay.addLayout(lay_mode, 1, 1, 3, 1)
        lay.setVerticalSpacing(15)
        lay.setHorizontalSpacing(15)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 3)
        lay.setRowStretch(1, 7)
        lay.setRowStretch(2, 2)
        self.setLayout(lay)

        self.setStyleSheet("""
            PyDMSpinbox, PyDMLabel{
                min-width:6em; max-width:6em;
                qproperty-alignment: AlignCenter;}
            PyDMLedMultiChannel, PyDMStateButton, PyDMEnumComboBox{
                min-width:6em; max-width:6em;}""")

    def _setupReliableMeasWidget(self):
        self.label_reliablemeas0 = QLabel('', self)
        self.led_ReliableMeas0 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=0)
        self.label_reliablemeas1 = QLabel('', self)
        self.led_ReliableMeas1 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=1)
        self.label_reliablemeas2 = QLabel('', self)
        self.led_ReliableMeas2 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=2)

        self.reliablemeas_channel = epics.PV(
            self.dcct_prefix+'ReliableMeasLabels-Cte',
            callback=self._updateReliableMeasLabels)

        gbox_reliablemeas = QGroupBox('Measure Reliability Status', self)
        lay_reliablemeas = QGridLayout()
        lay_reliablemeas.setColumnStretch(0, 1)
        lay_reliablemeas.setColumnStretch(1, 10)
        lay_reliablemeas.addWidget(self.led_ReliableMeas0, 0, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas0, 0, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas1, 1, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas1, 1, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas2, 2, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas2, 2, 1)
        gbox_reliablemeas.setLayout(lay_reliablemeas)
        gbox_reliablemeas.setStyleSheet("""
            .QLabel{min-height:1.29em; max-height:1.29em;}
        """)
        return gbox_reliablemeas

    def _setupGeneralSettingsWidget(self):
        gbox_generalsettings = QGroupBox('General Measurement Settings', self)

        l_measmode = QLabel('Mode: ', self)
        self.pydmenumcombobox_MeasMode = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sel')
        self.pydmlabel_MeasMode = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sts')
        hlay_measmode = QHBoxLayout()
        hlay_measmode.addWidget(self.pydmenumcombobox_MeasMode)
        hlay_measmode.addWidget(self.pydmlabel_MeasMode)

        l_range = QLabel('Range: ', self)
        self.pydmenumcombobox_Range = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'Range-Sel')
        self.pydmlabel_Range = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'Range-Sts')
        hlay_range = QHBoxLayout()
        hlay_range.addWidget(self.pydmenumcombobox_Range)
        hlay_range.addWidget(self.pydmlabel_Range)

        l_currthold = QLabel('Current Threshold [mA]: ', self)
        self.pydmspinbox_CurrThold = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'CurrThold-SP')
        self.pydmspinbox_CurrThold.showStepExponent = False
        self.pydmlabel_CurrThold = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'CurrThold-RB')
        hlay_currthold = QHBoxLayout()
        hlay_currthold.addWidget(self.pydmspinbox_CurrThold)
        hlay_currthold.addWidget(self.pydmlabel_CurrThold)

        l_hfreject = QLabel('High Frequency Rejection: ', self)
        self.pydmstatebutton_HFReject = PyDMStateButton(
            parent=self, init_channel=self.dcct_prefix+'HFReject-Sel')
        self.pydmstatebutton_HFReject.shape = 1
        self.pydmlabel_HFReject = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'HFReject-Sts')
        hlay_hfreject = QHBoxLayout()
        hlay_hfreject.addWidget(self.pydmstatebutton_HFReject)
        hlay_hfreject.addWidget(self.pydmlabel_HFReject)

        l_lowlimenbl = QLabel('Low Beam Current Detection: ', self)
        self.pydmstatebutton_LowLimEnbl = PyDMStateButton(
            parent=self, init_channel=self.dcct_prefix+'LowLimEnbl-Sel')
        self.pydmstatebutton_LowLimEnbl.shape = 1
        self.pydmlabel_LowLimEnbl = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'LowLimEnbl-Sts')
        hlay_lowlimenbl = QHBoxLayout()
        hlay_lowlimenbl.addWidget(self.pydmstatebutton_LowLimEnbl)
        hlay_lowlimenbl.addWidget(self.pydmlabel_LowLimEnbl)

        l_meastrig = QLabel('Trigger Source: ', self)
        self.pydmenumcombobox_MeasTrg = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sel')
        self.pydmlabel_MeasTrg = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sts')
        hlay_meastrig = QHBoxLayout()
        hlay_meastrig.addWidget(self.pydmenumcombobox_MeasTrg)
        hlay_meastrig.addWidget(self.pydmlabel_MeasTrg)

        l_trgdelay = QLabel('Delay After Trigger [s]: ', self)
        self.pydmspinbox_TrgDelay = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-SP')
        self.pydmspinbox_TrgDelay.showStepExponent = False
        self.pydmlabel_TrgDelay = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-RB')
        hlay_trgdelay = QHBoxLayout()
        hlay_trgdelay.addWidget(self.pydmspinbox_TrgDelay)
        hlay_trgdelay.addWidget(self.pydmlabel_TrgDelay)

        flay_generalsettings = QFormLayout()
        flay_generalsettings.setLabelAlignment(Qt.AlignRight)
        flay_generalsettings.setFormAlignment(Qt.AlignCenter)
        flay_generalsettings.addRow(l_measmode, hlay_measmode)
        flay_generalsettings.addRow(l_range, hlay_range)
        flay_generalsettings.addRow(l_currthold, hlay_currthold)
        flay_generalsettings.addRow(l_hfreject, hlay_hfreject)
        flay_generalsettings.addRow(l_lowlimenbl, hlay_lowlimenbl)
        flay_generalsettings.addRow(l_meastrig, hlay_meastrig)
        flay_generalsettings.addRow(l_trgdelay, hlay_trgdelay)
        gbox_generalsettings.setLayout(flay_generalsettings)
        return gbox_generalsettings

    def _setupMeasSettingsWidget(self, mode):
        if mode == 'Normal':
            prefix = self.dcct_prefix
            visible = True
        elif mode == 'Fast':
            prefix = self.dcct_prefix + mode
            visible = False

        gbox_modesettings = QGroupBox(mode+' Measurement Mode Settings', self)

        l_smpcnt = QLabel('Sample Count: ', self)
        spinbox_SampleCnt = PyDMSpinbox(
            parent=self, init_channel=prefix+'SampleCnt-SP')
        spinbox_SampleCnt.showStepExponent = False
        label_SampleCnt = PyDMLabel(
            parent=self, init_channel=prefix+'SampleCnt-RB')
        hlay_smpcnt = QHBoxLayout()
        hlay_smpcnt.addWidget(spinbox_SampleCnt)
        hlay_smpcnt.addWidget(label_SampleCnt)

        l_measperiod = QLabel('Period [s]: ', self)
        spinbox_MeasPeriod = PyDMSpinbox(
            parent=self, init_channel=prefix+'MeasPeriod-SP')
        spinbox_MeasPeriod.showStepExponent = False
        label_MeasPeriod = PyDMLabel(
            parent=self, init_channel=prefix+'MeasPeriod-RB')
        hlay_measperiod = QHBoxLayout()
        hlay_measperiod.addWidget(spinbox_MeasPeriod)
        hlay_measperiod.addWidget(label_MeasPeriod)

        l_offset = QLabel('Relative Offset Enable: ', self)
        statebutton_RelEnbl = PyDMStateButton(
            parent=self, init_channel=prefix+'RelEnbl-Sel')
        statebutton_RelEnbl.shape = 1
        statebutton_RelEnbl.setStyleSheet('min-width:6em; max-width:6em;')
        label_RelEnbl = PyDMLabel(
            parent=self, init_channel=prefix+'RelEnbl-Sts')
        hlay_offset = QHBoxLayout()
        hlay_offset.addWidget(statebutton_RelEnbl)
        hlay_offset.addWidget(label_RelEnbl)

        l_rellvl = QLabel('Relative Offset Level [V]: ', self)
        spinbox_RelLvl = PyDMSpinbox(
            parent=self, init_channel=prefix+'RelLvl-SP')
        spinbox_RelLvl.showStepExponent = False
        label_RelLvl = PyDMLabel(
            parent=self, init_channel=prefix+'RelLvl-RB')
        pushbutton_RelAcq = PyDMPushButton(
            parent=self, label='Acquire Offset', pressValue=1,
            init_channel=prefix+'RelAcq-Cmd')
        hlay_rellvl = QHBoxLayout()
        hlay_rellvl.addWidget(spinbox_RelLvl)
        hlay_rellvl.addWidget(label_RelLvl)
        hlay_rellvl.addWidget(pushbutton_RelAcq)

        l_imped = QLabel('Impedance: ', self)
        enumcombobox_Imped = PyDMEnumComboBox(
            parent=self, init_channel=prefix+'Imped-Sel')
        label_Imped = PyDMLabel(
            parent=self, init_channel=prefix+'Imped-Sts')
        hlay_imped = QHBoxLayout()
        hlay_imped.addWidget(enumcombobox_Imped)
        hlay_imped.addWidget(label_Imped)

        flay_modesettings = QFormLayout()
        flay_modesettings.setLabelAlignment(Qt.AlignRight)
        flay_modesettings.setFormAlignment(Qt.AlignHCenter)
        flay_modesettings.addRow(l_smpcnt, hlay_smpcnt)
        flay_modesettings.addRow(l_measperiod, hlay_measperiod)
        flay_modesettings.addRow(l_offset, hlay_offset)
        flay_modesettings.addRow(l_rellvl, hlay_rellvl)
        flay_modesettings.addRow(l_imped, hlay_imped)

        if mode == 'Normal':
            l_linesync = QLabel('Line Synchronization: ', self)
            statebutton_LineSync = PyDMStateButton(
                parent=self, init_channel=prefix+'LineSync-Sel')
            statebutton_LineSync.shape = 1
            statebutton_LineSync.setStyleSheet('min-width:6em; max-width:6em;')
            label_LineSync = PyDMLabel(
                parent=self, init_channel=prefix+'LineSync-Sts')
            hlay_linesync = QHBoxLayout()
            hlay_linesync.addWidget(statebutton_LineSync)
            hlay_linesync.addWidget(label_LineSync)

            label_avg = QLabel('<h4>Average Filter</h4>', self)
            l_avgenbl = QLabel('Enable: ', self)
            statebutton_AvgFilterEnbl = PyDMStateButton(
                parent=self, init_channel=prefix+'AvgFilterEnbl-Sel')
            statebutton_AvgFilterEnbl.shape = 1
            label_AvgFilterEnbl = PyDMLabel(
                parent=self, init_channel=prefix+'AvgFilterEnbl-Sts')
            hlay_avgenbl = QHBoxLayout()
            hlay_avgenbl.addWidget(statebutton_AvgFilterEnbl)
            hlay_avgenbl.addWidget(label_AvgFilterEnbl)

            l_avgcnt = QLabel('Samples : ', self)
            spinbox_AvgFilterCount = PyDMSpinbox(
                parent=self, init_channel=prefix+'AvgFilterCnt-SP')
            spinbox_AvgFilterCount.showStepExponent = False
            label_AvgFilterCount = PyDMLabel(
                parent=self, init_channel=prefix+'AvgFilterCnt-RB')
            hlay_avgcnt = QHBoxLayout()
            hlay_avgcnt.addWidget(spinbox_AvgFilterCount)
            hlay_avgcnt.addWidget(label_AvgFilterCount)

            l_avgtyp = QLabel('Type: ', self)
            enumcombobox_AvgFilterTyp = PyDMEnumComboBox(
                parent=self, init_channel=self.dcct_prefix+'AvgFilterTyp-Sel')
            label_AvgFilterTyp = PyDMLabel(
                parent=self, init_channel=self.dcct_prefix+'AvgFilterTyp-Sts')
            hlay_avgtyp = QHBoxLayout()
            hlay_avgtyp.addWidget(enumcombobox_AvgFilterTyp)
            hlay_avgtyp.addWidget(label_AvgFilterTyp)

            l_avgwin = QLabel('Noise window size [%]: ', self)
            spinbox_AvgFilterWind = PyDMSpinbox(
                parent=self, init_channel=prefix+'AvgFilterWind-SP')
            spinbox_AvgFilterWind.showStepExponent = False
            label_AvgFilterWind = PyDMLabel(
                parent=self, init_channel=prefix+'AvgFilterWind-RB')
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
            PyDMSpinbox, PyDMLabel{
                min-width:6em; max-width:6em;
                qproperty-alignment: AlignCenter;}
            PyDMLedMultiChannel, PyDMStateButton, PyDMEnumComboBox{
                min-width:6em; max-width:6em;}""")
        return gbox_modesettings

    def _setupTriggerWidget(self):
        gbox_trigger = QGroupBox('Trigger', self)
        lay = _create_trigger_layout(
            gbox_trigger, self.prefix, self.device, label_align=Qt.AlignRight)
        lay.setAlignment(Qt.AlignCenter)
        gbox_trigger.setLayout(lay)
        return gbox_trigger

    def _updateReliableMeasLabels(self, pvname, value,  **kwargs):
        if value:
            self.label_reliablemeas0.setText(value[0])
            self.label_reliablemeas1.setText(value[1])
            self.label_reliablemeas2.setText(value[2])

    def _showMeasModeSettings(self, value):
        if value == _DCCTc.MeasModeSel.Normal:
            self.gbox_normalmode.setVisible(True)
            self.gbox_fastmode.setVisible(False)
        elif value == _DCCTc.MeasModeSel.Fast:
            self.gbox_normalmode.setVisible(False)
            self.gbox_fastmode.setVisible(True)


def _create_trigger_layout(parent, prefix, device, label_align=Qt.AlignRight):
    trg_prefix = prefix + device.replace('DI', 'TI')

    l_TIstatus = QLabel('Status: ', parent)
    ledmulti_TIStatus = PyDMLedMultiChannel(
        parent=parent, channels2values={trg_prefix+':State-Sts': 1,
                                        trg_prefix+':Status-Mon': 0})
    pb_trgdetails = QPushButton('Open details', parent)
    trg_w = create_window_from_widget(
        HLTriggerDetailed, title=trg_prefix+' Detailed Settings',
        is_main=True)
    _hlautil.connect_window(pb_trgdetails, trg_w, parent=None,
                            prefix=trg_prefix)
    hlay_TIstatus = QHBoxLayout()
    hlay_TIstatus.addWidget(ledmulti_TIStatus, alignment=Qt.AlignLeft)
    hlay_TIstatus.addWidget(pb_trgdetails)

    l_TIdelay = QLabel('Delay [us]: ', parent)
    spinbox_TIDelay = PyDMSpinbox(
        parent=parent, init_channel=trg_prefix+':Delay-SP')
    spinbox_TIDelay.showStepExponent = False
    label_TIDelay = PyDMLabel(
        parent=parent, init_channel=trg_prefix+':Delay-RB')
    hlay_TIdelay = QHBoxLayout()
    hlay_TIdelay.addWidget(spinbox_TIDelay)
    hlay_TIdelay.addWidget(label_TIDelay)

    lay = QGridLayout()
    lay.addWidget(l_TIstatus, 0, 0, alignment=label_align)
    lay.addLayout(hlay_TIstatus, 0, 1)
    lay.addWidget(l_TIdelay, 1, 0, alignment=label_align)
    lay.addLayout(hlay_TIdelay, 1, 1)
    return lay


if __name__ == '__main__':
    """Run test."""
    import sys
    from siriuspy.envars import vaca_prefix as _vaca_prefix
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()

    device = 'BO-35D:DI-DCCT'
    DCCTSettingsWindow = create_window_from_widget(
        DCCTSettings, device+' Settings', is_main=True)
    window = DCCTSettingsWindow(
        None, prefix=_vaca_prefix, device=device, show_smooth_settings=False)
    window.show()
    sys.exit(app.exec_())
