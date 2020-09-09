"""BbB GPIO Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, \
    QHBoxLayout, QVBoxLayout
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..widgets import PyDMStateButton

from .custom_widgets import MyScaleIndicator


class BbBGPIOWidget(QWidget):
    """BbB GPIO Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        ld_gpio = QLabel(
            '<h3>GPIO Settings</h3>', self, alignment=Qt.AlignCenter)

        vlay1 = QVBoxLayout()
        vlay1.addWidget(self._setupFrontBackEndRegsWidget())
        vlay1.addWidget(self._setupOtherControlsWidget())

        vlay2 = QVBoxLayout()
        vlay2.addWidget(self._setupPhaseServoLoopWidget())
        vlay2.addWidget(self._setupThermoWidget())

        lay = QGridLayout(self)
        lay.addWidget(ld_gpio, 0, 1, 1, 2)
        lay.addLayout(vlay1, 1, 1)
        lay.addLayout(vlay2, 1, 2)
        lay.addWidget(self._setupMonitorsWidget(), 2, 1, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(3, 3)
        lay.setRowStretch(3, 3)

        self.setStyleSheet("""PyDMLabel{qproperty-alignment: AlignCenter;}""")

    def _setupGPIOSelectionWidget(self):
        # # GPIO Selection
        ld_gpiosel = QLabel('<h4>Select GPIO</h4>', self)
        cb_gpiosel = PyDMEnumComboBox(self, self.dev_pref+':GPIO_SEL')

        gbox_gpiosel = QGroupBox(self)
        lay_gpiosel = QHBoxLayout(gbox_gpiosel)
        lay_gpiosel.addWidget(ld_gpiosel)
        lay_gpiosel.addWidget(cb_gpiosel)
        return gbox_gpiosel

    def _setupFrontBackEndRegsWidget(self):
        # # Front/back end registers
        ld_gpiohph = QLabel('Horiz. Phase', self)
        sb_gpiohph = PyDMSpinbox(self, self.dev_pref+':FBELT_X_PHASE_SETPT')
        sb_gpiohph.showStepExponent = False
        ld_gpiohat = QLabel('Horiz. Atten.', self)
        sb_gpiohat = PyDMSpinbox(self, self.dev_pref+':FBE_X_ATT')
        sb_gpiohat.showStepExponent = False
        ld_gpiovph = QLabel('Vert. Phase', self)
        sb_gpiovph = PyDMSpinbox(self, self.dev_pref+':FBELT_Y_PHASE_SETPT')
        sb_gpiovph.showStepExponent = False
        ld_gpiovat = QLabel('Vert. Atten.', self)
        sb_gpiovat = PyDMSpinbox(self, self.dev_pref+':FBE_Y_ATT')
        sb_gpiovat.showStepExponent = False
        ld_gpiolph = QLabel('Long. Phase', self)
        sb_gpiolph = PyDMSpinbox(self, self.dev_pref+':FBELT_SERVO_SETPT')
        sb_gpiolph.showStepExponent = False
        ld_gpiolat = QLabel('Long. Atten.', self)
        sb_gpiolat = PyDMSpinbox(self, self.dev_pref+':FBE_Z_ATT')
        sb_gpiolat.showStepExponent = False
        ld_gpiobeph = QLabel('Back-end Phase', self)
        sb_gpiobeph = PyDMSpinbox(self, self.dev_pref+':FBE_BE_PHASE')
        sb_gpiobeph.showStepExponent = False
        ld_gpiobeat = QLabel('Back-end Atten.', self)
        sb_gpiobeat = PyDMSpinbox(self, self.dev_pref+':FBE_BE_ATT')
        sb_gpiobeat.showStepExponent = False
        # # Phases
        ld_gpiophss = QLabel('<h4>Phases</h4>', self, alignment=Qt.AlignCenter)
        lb_gpiohph = PyDMLabel(self, self.dev_pref+':FBE_X_PHASE')
        lb_gpiovph = PyDMLabel(self, self.dev_pref+':FBE_Y_PHASE')
        lb_gpiolph = PyDMLabel(self, self.dev_pref+':FBE_Z_PHASE')
        lay_phases = QGridLayout()
        lay_phases.addWidget(ld_gpiophss, 0, 0, 1, 10)
        lay_phases.addWidget(QLabel('L:'), 1, 1)
        lay_phases.addWidget(lb_gpiolph, 1, 2)
        lay_phases.addWidget(QLabel('H:'), 1, 4)
        lay_phases.addWidget(lb_gpiohph, 1, 5)
        lay_phases.addWidget(QLabel('V:'), 1, 7)
        lay_phases.addWidget(lb_gpiovph, 1, 8)
        lay_phases.setColumnStretch(0, 2)
        lay_phases.setColumnStretch(3, 2)
        lay_phases.setColumnStretch(6, 2)
        lay_phases.setColumnStretch(9, 2)

        gbox_fbend = QGroupBox('Front/back end registers', self)
        lay_fbend = QGridLayout(gbox_fbend)
        lay_fbend.addWidget(ld_gpiobeat, 0, 0)
        lay_fbend.addWidget(sb_gpiobeat, 0, 1)
        lay_fbend.addWidget(ld_gpiolat, 1, 0)
        lay_fbend.addWidget(sb_gpiolat, 1, 1)
        lay_fbend.addWidget(ld_gpiohat, 2, 0)
        lay_fbend.addWidget(sb_gpiohat, 2, 1)
        lay_fbend.addWidget(ld_gpiovat, 3, 0)
        lay_fbend.addWidget(sb_gpiovat, 3, 1)
        lay_fbend.addWidget(ld_gpiobeph, 4, 0)
        lay_fbend.addWidget(sb_gpiobeph, 4, 1)
        lay_fbend.addWidget(ld_gpiolph, 5, 0)
        lay_fbend.addWidget(sb_gpiolph, 5, 1)
        lay_fbend.addWidget(ld_gpiohph, 6, 0)
        lay_fbend.addWidget(sb_gpiohph, 6, 1)
        lay_fbend.addWidget(ld_gpiovph, 7, 0)
        lay_fbend.addWidget(sb_gpiovph, 7, 1)
        lay_fbend.addLayout(lay_phases, 8, 0, 1, 2)
        return gbox_fbend

    def _setupPhaseServoLoopWidget(self):
        # # Phase Servo Loop
        ld_gpiolctrl = QLabel('Loop Ctrl', self)
        cb_gpiolctrl = PyDMStateButton(self, self.dev_pref+':FBELT_SERVO_MODE')

        ld_gpiolsign = QLabel('Loop Sign', self)
        cb_gpiolsign = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_SERVO_SIGN')

        ld_gpiogain = QLabel('Gain', self)
        sb_gpiogain = PyDMSpinbox(self, self.dev_pref+':FBELT_SERVO_GAIN')
        sb_gpiogain.showStepExponent = False

        ld_gpiooff = QLabel('Offset', self)
        sb_gpiooff = PyDMSpinbox(self, self.dev_pref+':FBELT_SERVO_OFFSET')
        sb_gpiooff.showStepExponent = False

        ld_gpiohtrk = QLabel('Hor. Trk.', self)
        cb_gpiohtrk = PyDMStateButton(
            self, self.dev_pref+':FBELT_SERVO_X_TRACK')

        ld_gpiovtrk = QLabel('Vert. Trk.', self)
        cb_gpiovtrk = PyDMStateButton(
            self, self.dev_pref+':FBELT_SERVO_Y_TRACK')

        gbox_phsloop = QGroupBox('Phase Servo Loop', self)
        lay_phsloop = QGridLayout(gbox_phsloop)
        lay_phsloop.addWidget(ld_gpiolctrl, 0, 0)
        lay_phsloop.addWidget(cb_gpiolctrl, 0, 1)
        lay_phsloop.addWidget(ld_gpiolsign, 1, 0)
        lay_phsloop.addWidget(cb_gpiolsign, 1, 1)
        lay_phsloop.addWidget(ld_gpiogain, 2, 0)
        lay_phsloop.addWidget(sb_gpiogain, 2, 1)
        lay_phsloop.addWidget(ld_gpiooff, 3, 0)
        lay_phsloop.addWidget(sb_gpiooff, 3, 1)
        lay_phsloop.addWidget(ld_gpiohtrk, 4, 0)
        lay_phsloop.addWidget(cb_gpiohtrk, 4, 1)
        lay_phsloop.addWidget(ld_gpiovtrk, 5, 0)
        lay_phsloop.addWidget(cb_gpiovtrk, 5, 1)
        return gbox_phsloop

    def _setupThermoWidget(self):
        # # DS1822 ROM/Thermometer
        ld_gpiosts = QLabel('Status', self)
        lb_gpiosts = PyDMLabel(self, self.dev_pref+':FBE_DS1822_STAT')

        ld_gpiocsum = QLabel('CheckSum', self)
        lb_gpiocsum = PyDMLabel(self, self.dev_pref+':FBE_DS1822_XSUM')

        ld_gpiomod = QLabel('Modification', self)
        lb_gpiomod = PyDMLabel(self, self.dev_pref+':FBE_MOD_SENSE')

        ld_gpiodevid = QLabel('Device ID', self)
        lb_gpiodevid = PyDMLabel(self, self.dev_pref+':FBE_DS1822_DEVID')
        lb_gpiodevid.displayFormat = PyDMLabel.DisplayFormat.Hex

        ld_gpioser = QLabel('Serial', self)
        lb_gpioser = PyDMLabel(self, self.dev_pref+':FBE_DS1822_SERIAL')

        ld_gpiotemp = QLabel('Temperature', self)
        lb_gpiotemp = PyDMLabel(self, self.dev_pref+':FBE_TEMP')
        lb_gpiotemp.showUnits = True

        gbox_thermo = QGroupBox('DS1822 ROM/Thermometer', self)
        lay_thermo = QGridLayout(gbox_thermo)
        lay_thermo.addWidget(ld_gpiosts, 0, 0)
        lay_thermo.addWidget(lb_gpiosts, 0, 1)
        lay_thermo.addWidget(ld_gpiocsum, 1, 0)
        lay_thermo.addWidget(lb_gpiocsum, 1, 1)
        lay_thermo.addWidget(ld_gpiomod, 2, 0)
        lay_thermo.addWidget(lb_gpiomod, 2, 1)
        lay_thermo.addWidget(ld_gpiodevid, 3, 0)
        lay_thermo.addWidget(lb_gpiodevid, 3, 1)
        lay_thermo.addWidget(ld_gpioser, 4, 0)
        lay_thermo.addWidget(lb_gpioser, 4, 1)
        lay_thermo.addWidget(ld_gpiotemp, 5, 0)
        lay_thermo.addWidget(lb_gpiotemp, 5, 1)
        return gbox_thermo

    def _setupOtherControlsWidget(self):
        # # FBE
        ld_gpiomode = QLabel('Mode', self)
        cb_gpiomode = PyDMStateButton(self, self.dev_pref+':FBELT_FAN_MODE')

        ld_gpiofanspd = QLabel('Fan Speed', self)
        lb_gpiofanspd = PyDMLabel(self, self.dev_pref+':FBE_FANMON')
        lb_gpiofanspd.showUnits = True

        ld_gpiotempsp = QLabel('Temperature Setpoint', self)
        sb_gpiotempsp = PyDMSpinbox(self, self.dev_pref+':FBELT_FAN_SETPT')
        sb_gpiotempsp.showStepExponent = False

        gbox_fbe = QGroupBox('Fan Control', self)
        lay_fbe = QGridLayout(gbox_fbe)
        lay_fbe.addWidget(ld_gpiomode, 0, 0)
        lay_fbe.addWidget(cb_gpiomode, 0, 1)
        lay_fbe.addWidget(ld_gpiofanspd, 1, 0)
        lay_fbe.addWidget(lb_gpiofanspd, 1, 1)
        lay_fbe.addWidget(ld_gpiotempsp, 2, 0)
        lay_fbe.addWidget(sb_gpiotempsp, 2, 1)
        return gbox_fbe

    def _setupMonitorsWidget(self):
        # # ADC Average
        si_gpioadcav = MyScaleIndicator(self, self.dev_pref+':CIC_MEAN')
        si_gpioadcav.setObjectName('si')
        si_gpioadcav.setStyleSheet('#si{min-height: 4em;}')

        gbox_adcav = QGroupBox('ADC Average', self)
        lay_adcav = QGridLayout(gbox_adcav)
        lay_adcav.addWidget(si_gpioadcav)

        # # Phase servo output
        si_gpioservodlt = MyScaleIndicator(
            self, self.dev_pref+':FBELT_SERVO_DELTA')
        ld_gpioservomax = QLabel(
            '<h4>Max</h4>', self, alignment=Qt.AlignCenter)
        sb_gpioservomax = PyDMSpinbox(
            self, self.dev_pref+':FBELT_SERVO_MAXDELTA')
        sb_gpioservomax.showStepExponent = False

        gbox_phsout = QGroupBox('Phase Servo Output', self)
        lay_phsout = QGridLayout(gbox_phsout)
        lay_phsout.addWidget(si_gpioservodlt, 0, 0, 2, 1)
        lay_phsout.addWidget(ld_gpioservomax, 0, 1, alignment=Qt.AlignBottom)
        lay_phsout.addWidget(sb_gpioservomax, 1, 1, alignment=Qt.AlignTop)
        lay_phsout.setColumnStretch(0, 4)
        lay_phsout.setColumnStretch(1, 1)

        wid = QWidget()
        lay = QHBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(gbox_adcav)
        lay.addWidget(gbox_phsout)
        lay.setStretch(0, 4)
        lay.setStretch(1, 5)
        return wid
