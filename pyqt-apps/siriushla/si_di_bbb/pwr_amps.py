"""BbB Devices Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem
import qtawesome as qta
from pydm.widgets import PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import PyDMStateButton, SiriusLedState, SiriusSpinbox, \
    SiriusLabel, PyDMLed, SiriusPushButton

from .custom_widgets import MyScaleIndicator
from .util import set_bbb_color


class BbBPwrAmpsWidget(QWidget):
    """BbB Power Amplifiers Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        lay_mc = QGridLayout(self)
        lay_mc.setContentsMargins(0, 0, 0, 0)
        if self._device.endswith('-L'):
            lay_mc.addWidget(self._setupMiniCircWidget(0), 0, 0)
            lay_mc.addWidget(self._setupMiniCircWidget(1), 0, 1)
        else:
            lay_mc.addWidget(self._setupTransverse(), 0, 0)

    def _setupSerialAmpWidget(self):
        ld_serial = QLabel(
            '<h3>Serial/USB amplifier</h3>', self, alignment=Qt.AlignCenter)

        ld_lctrl = QLabel('Line Control', self)
        bt_lctrl = PyDMStateButton(self, self.dev_pref+':SERIAL_CTRL_LINE')

        ld_rfctrl = QLabel('RF Control', self)
        bt_rfctrl = PyDMStateButton(self, self.dev_pref+':SERIAL_CTRL_RF')

        ld_pwrfreq = QLabel(
            'Power Meter Calibration Frequency',
            self, alignment=Qt.AlignCenter)
        le_pwrfreq = PyDMLineEdit(self, self.dev_pref+':SERIAL_CALFREQ')
        le_pwrfreq.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(ld_lctrl, 0, 0, alignment=Qt.AlignRight)
        lay_ctrl.addWidget(bt_lctrl, 0, 1, alignment=Qt.AlignLeft)
        lay_ctrl.addWidget(ld_rfctrl, 0, 2, alignment=Qt.AlignRight)
        lay_ctrl.addWidget(bt_rfctrl, 0, 3, alignment=Qt.AlignLeft)
        lay_ctrl.addWidget(ld_pwrfreq, 1, 0, 1, 2, alignment=Qt.AlignRight)
        lay_ctrl.addWidget(le_pwrfreq, 1, 2, 1, 2, alignment=Qt.AlignLeft)
        lay_ctrl.setColumnStretch(0, 1)
        lay_ctrl.setColumnStretch(1, 1)
        lay_ctrl.setColumnStretch(2, 1)
        lay_ctrl.setColumnStretch(3, 1)

        ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        si_fwrpwr = MyScaleIndicator(self, self.dev_pref+':SERIAL_FWD')
        si_fwrpwr.indicatorColor = QColor('blue')
        si_fwrpwr.barIndicator = True
        si_fwrpwr.showUnits = True
        si_fwrpwr.setObjectName('fwrpwr')
        si_fwrpwr.setStyleSheet('#fwrpwr{min-height:6em; min-width:8em;}')

        ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        si_revpwr = MyScaleIndicator(self, self.dev_pref+':SERIAL_REV')
        si_revpwr.indicatorColor = QColor('red')
        si_revpwr.barIndicator = True
        si_revpwr.showUnits = True
        si_revpwr.setObjectName('revpwr')
        si_revpwr.setStyleSheet('#revpwr{min-height:6em; min-width:8em;}')

        ld_id = QLabel('ID', self)
        lb_id = SiriusLabel(self, self.dev_pref+':SERIAL_ID')
        lb_id.displayFormat = SiriusLabel.DisplayFormat.String
        hbox_id = QHBoxLayout()
        hbox_id.setContentsMargins(0, 0, 0, 0)
        hbox_id.addWidget(ld_id)
        hbox_id.addWidget(lb_id)
        hbox_id.setStretch(0, 1)
        hbox_id.setStretch(1, 5)

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(ld_fwrpwr, 0, 0)
        lay_mon.addWidget(si_fwrpwr, 1, 0)
        lay_mon.addWidget(ld_revpwr, 0, 1)
        lay_mon.addWidget(si_revpwr, 1, 1)
        lay_mon.addLayout(hbox_id, 2, 0, 1, 2)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addItem(
            QSpacerItem(10, 1, QSzPlcy.MinimumExpanding, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(ld_serial, 0, 1)
        lay.addWidget(gbox_ctrl, 1, 1)
        lay.addWidget(gbox_mon, 2, 1)
        lay.addItem(
            QSpacerItem(10, 10, QSzPlcy.MinimumExpanding,
                        QSzPlcy.MinimumExpanding), 3, 2)
        return wid

    def _setupMilmegaWidget(self, unit):
        unit_label = str(unit)
        ld_mmdb15 = QLabel(
            '<h3>Milmega DB-15 '+unit_label+'</h3>', self,
            alignment=Qt.AlignCenter)
        ld_mmdesc = QLabel(
            'Milmega via DB-15 custom cable\nand '
            '8 channel ADC (unit '+unit_label+')',
            self, alignment=Qt.AlignCenter)

        ld_rfsts = QLabel('RF Status', self)
        led_rfsts = PyDMLed(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_RF')
        led_rfsts.onColor = PyDMLed.LightGreen
        led_rfsts.offColor = PyDMLed.Red
        lb_rfsts = SiriusLabel(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_RF')

        ld_fltlac = QLabel('Fault Latch', self)
        led_fltlac = PyDMLed(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FAULT')
        led_fltlac.onColor = PyDMLed.LightGreen
        led_fltlac.offColor = PyDMLed.Red
        lb_fltlac = SiriusLabel(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FAULT')

        ld_slope = QLabel('Slope', self)
        le_slope = PyDMLineEdit(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_SLOPE')
        le_slope.showUnits = True
        ld_offset = QLabel('Offset', self)
        le_offset = PyDMLineEdit(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_OFFSET')
        le_offset.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(ld_rfsts, 0, 0)
        lay_ctrl.addWidget(led_rfsts, 0, 1)
        lay_ctrl.addWidget(lb_rfsts, 0, 2)
        lay_ctrl.addWidget(ld_fltlac, 1, 0)
        lay_ctrl.addWidget(led_fltlac, 1, 1)
        lay_ctrl.addWidget(lb_fltlac, 1, 2)
        lay_ctrl.addWidget(ld_slope, 2, 0)
        lay_ctrl.addWidget(le_slope, 2, 1, 1, 2)
        lay_ctrl.addWidget(ld_offset, 3, 0)
        lay_ctrl.addWidget(le_offset, 3, 1, 1, 2)

        ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        si_fwrpwr = MyScaleIndicator(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FWD')
        si_fwrpwr.barIndicator = True
        si_fwrpwr.indicatorColor = QColor('blue')
        si_fwrpwr.showUnits = True
        si_fwrpwr.setObjectName('fwrpwr')
        si_fwrpwr.setStyleSheet('#fwrpwr{min-height:6em; min-width:8em;}')

        ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        si_revpwr = MyScaleIndicator(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_REV')
        si_revpwr.barIndicator = True
        si_revpwr.indicatorColor = QColor('red')
        si_revpwr.showUnits = True
        si_revpwr.setObjectName('revpwr')
        si_revpwr.setStyleSheet('#revpwr{min-height:6em; min-width:8em;}')

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(ld_fwrpwr, 0, 0)
        lay_mon.addWidget(si_fwrpwr, 1, 0)
        lay_mon.addWidget(ld_revpwr, 2, 0)
        lay_mon.addWidget(si_revpwr, 3, 0)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_mmdb15)
        lay.addWidget(ld_mmdesc)
        lay.addWidget(gbox_ctrl)
        lay.addWidget(gbox_mon)
        return wid

    def _setupMiniCircWidget(self, unit):
        unit_label = str(unit)
        ld_mczt102 = QLabel(
            '<h3>Mini-Circuits Zt-102 '+unit_label+'</h3>',
            self, alignment=Qt.AlignCenter)
        ld_mcdesc = QLabel(
            'Mini-Circuits ZT-102 DE-9\nmonitoring '
            'interface (unit '+unit_label+')', self,
            alignment=Qt.AlignCenter)

        ld_fault = QLabel('RF Status', self)
        led_fault = PyDMLed(self, self.dev_pref+':MCLRAW_'+unit_label+'_FAULT')
        led_fault.onColor = PyDMLed.LightGreen
        led_fault.offColor = PyDMLed.Red
        lb_fault = SiriusLabel(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FAULT')

        ld_temp = QLabel('Temperature', self)
        lb_temp = SiriusLabel(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_TEMP')
        lb_temp.showUnits = True

        ld_fwrloss = QLabel('Fwd Loss', self)
        le_fwrloss = PyDMLineEdit(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FWDLOSS')
        le_fwrloss.showUnits = True
        ld_revloss = QLabel('Rev Loss', self)
        le_revloss = PyDMLineEdit(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_REVLOSS')
        le_revloss.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(ld_fault, 0, 0)
        lay_ctrl.addWidget(led_fault, 0, 1)
        lay_ctrl.addWidget(lb_fault, 0, 2)
        lay_ctrl.addWidget(ld_temp, 1, 0)
        lay_ctrl.addWidget(lb_temp, 1, 1, 1, 2)
        lay_ctrl.addWidget(ld_fwrloss, 2, 0)
        lay_ctrl.addWidget(le_fwrloss, 2, 1, 1, 2)
        lay_ctrl.addWidget(ld_revloss, 3, 0)
        lay_ctrl.addWidget(le_revloss, 3, 1, 1, 2)

        ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        si_fwrpwr = MyScaleIndicator(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FWD')
        si_fwrpwr.barIndicator = True
        si_fwrpwr.indicatorColor = QColor('blue')
        si_fwrpwr.showUnits = True
        si_fwrpwr.setObjectName('fwrpwr')
        si_fwrpwr.setStyleSheet('#fwrpwr{min-height:6em; min-width:8em;}')

        ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        si_revpwr = MyScaleIndicator(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_REV')
        si_revpwr.barIndicator = True
        si_revpwr.indicatorColor = QColor('red')
        si_revpwr.showUnits = True
        si_revpwr.setObjectName('revpwr')
        si_revpwr.setStyleSheet('#revpwr{min-height:6em; min-width:8em;}')

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(ld_fwrpwr, 0, 0)
        lay_mon.addWidget(si_fwrpwr, 1, 0)
        lay_mon.addWidget(ld_revpwr, 2, 0)
        lay_mon.addWidget(si_revpwr, 3, 0)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_mczt102)
        lay.addWidget(ld_mcdesc)
        lay.addWidget(gbox_ctrl)
        lay.addWidget(gbox_mon)
        return wid

    def _setupTransverse(self):
        pref = self.dev_pref.substitute(dev='BbBAmp'+self._device.idx, idx='')

        ld_main = QLabel(
            '<h3>AR Amplifier</h3>', self, alignment=Qt.AlignCenter)

        conf = SiriusPushButton(
            self, init_channel=pref+':Rst-Cmd', pressValue=1, releaseValue=0)
        conf.setText('Reset')
        conf.setToolTip('Reset State')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf_lay = QHBoxLayout()
        conf_lay.addStretch()
        conf_lay.addWidget(conf)
        conf_lay.addStretch()

        ld_enbl = QLabel('Enable', self)
        led_enbl = SiriusLedState(self, pref+':Enbl-Sts')
        pb_enbl = PyDMStateButton(self, pref+':Enbl-Sel')

        ld_gainauto = QLabel('Gain lock\n(dB to steps)', self)
        led_gainauto = SiriusLedState(self, pref+':GainAuto-Sts')
        pb_gainauto = PyDMStateButton(self, pref+':GainAuto-Sel')

        ld_gain_db = QLabel('Gain [dB]', self)
        sp_gain_db = SiriusSpinbox(self, pref+':Gain-SP')
        sp_gain_db.showStepExponent = False
        lb_gain_db = SiriusLabel(self, init_channel=pref+':Gain-RB')

        ld_gain_st = QLabel('Gain [steps]', self)
        sp_gain_st = SiriusSpinbox(self, pref+':GainStep-SP')
        sp_gain_st.showStepExponent = False
        lb_gain_st = SiriusLabel(self, init_channel=pref+':GainStep-RB')

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_main, 0, 0, 1, 3)
        lay.addLayout(conf_lay, 1, 0, 1, 3)
        lay.addWidget(ld_enbl, 2, 0)
        lay.addWidget(pb_enbl, 2, 1)
        lay.addWidget(led_enbl, 2, 2)
        lay.addWidget(ld_gainauto, 3, 0)
        lay.addWidget(pb_gainauto, 3, 1)
        lay.addWidget(led_gainauto, 3, 2)
        lay.addWidget(ld_gain_db, 4, 0)
        lay.addWidget(sp_gain_db, 4, 1)
        lay.addWidget(lb_gain_db, 4, 2)
        lay.addWidget(ld_gain_st, 5, 0)
        lay.addWidget(sp_gain_st, 5, 1)
        lay.addWidget(lb_gain_st, 5, 2)
        return wid
