"""BbB GPIO Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QGroupBox, QHBoxLayout, QVBoxLayout

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
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
        self._ld_gpio = QLabel(
            '<h3>GPIO Settings</h3>', self, alignment=Qt.AlignCenter)

        vlay1 = QVBoxLayout()
        vlay1.addWidget(self._setupFrontBackEndRegsWidget())
        vlay1.addWidget(self._setupOtherControlsWidget())

        vlay2 = QVBoxLayout()
        vlay2.addWidget(self._setupPhaseServoLoopWidget())
        vlay2.addWidget(self._setupThermoWidget())

        lay = QGridLayout(self)
        lay.addWidget(self._ld_gpio, 0, 0, 1, 2)
        lay.addWidget(self._setupGPIOSelectionWidget(), 1, 0, 1, 2)
        lay.addLayout(vlay1, 2, 0)
        lay.addLayout(vlay2, 2, 1)
        lay.addWidget(self._setupMonitorsWidget(), 3, 0, 1, 2)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignCenter;
            }
        """)

    def _setupGPIOSelectionWidget(self):
        # # GPIO Selection
        self._ld_gpiosel = QLabel('<h4>Select GPIO</h4>', self)
        self._cb_gpiosel = PyDMEnumComboBox(
            self, self.dev_pref+':GPIO_SEL')

        gbox_gpiosel = QGroupBox(self)
        lay_gpiosel = QHBoxLayout(gbox_gpiosel)
        lay_gpiosel.addWidget(self._ld_gpiosel)
        lay_gpiosel.addWidget(self._cb_gpiosel)
        return gbox_gpiosel

    def _setupFrontBackEndRegsWidget(self):
        # # Front/back end registers
        self._ld_gpiohph = QLabel('Horiz. Phase', self)
        self._sb_gpiohph = PyDMSpinbox(
            self, self.dev_pref+':FBELT_X_PHASE_SETPT')
        self._sb_gpiohph.showStepExponent = False
        self._ld_gpiohat = QLabel('Horiz. Atten.', self)
        self._sb_gpiohat = PyDMSpinbox(self, self.dev_pref+':FBE_X_ATT')
        self._sb_gpiohat.showStepExponent = False
        self._ld_gpiovph = QLabel('Vert. Phase', self)
        self._sb_gpiovph = PyDMSpinbox(
            self, self.dev_pref+':FBELT_Y_PHASE_SETPT')
        self._sb_gpiovph.showStepExponent = False
        self._ld_gpiovat = QLabel('Vert. Atten.', self)
        self._sb_gpiovat = PyDMSpinbox(self, self.dev_pref+':FBE_Y_ATT')
        self._sb_gpiovat.showStepExponent = False
        self._ld_gpiolph = QLabel('Long. Phase', self)
        self._sb_gpiolph = PyDMSpinbox(
            self, self.dev_pref+':FBELT_SERVO_SETPT')
        self._sb_gpiolph.showStepExponent = False
        self._ld_gpiolat = QLabel('Long. Atten.', self)
        self._sb_gpiolat = PyDMSpinbox(self, self.dev_pref+':FBE_Z_ATT')
        self._sb_gpiolat.showStepExponent = False
        self._ld_gpiobeph = QLabel('Back-end Phase', self)
        self._sb_gpiobeph = PyDMSpinbox(self, self.dev_pref+':FBE_BE_PHASE')
        self._sb_gpiobeph.showStepExponent = False
        self._ld_gpiobeat = QLabel('Back-end Atten.', self)
        self._sb_gpiobeat = PyDMSpinbox(self, self.dev_pref+':FBE_BE_ATT')
        self._sb_gpiobeat.showStepExponent = False
        # # Phases
        self._ld_gpiophss = QLabel(
            '<h4>Phases</h4>', self, alignment=Qt.AlignCenter)
        self._lb_gpiohph = PyDMLabel(self, self.dev_pref+':FBE_X_PHASE')
        self._lb_gpiovph = PyDMLabel(self, self.dev_pref+':FBE_Y_PHASE')
        self._lb_gpiolph = PyDMLabel(self, self.dev_pref+':FBE_Z_PHASE')
        lay_phases = QGridLayout()
        lay_phases.addWidget(self._ld_gpiophss, 0, 0, 1, 3)
        lay_phases.addWidget(self._lb_gpiohph, 1, 0)
        lay_phases.addWidget(self._lb_gpiovph, 1, 1)
        lay_phases.addWidget(self._lb_gpiolph, 1, 2)

        gbox_fbend = QGroupBox('Front/back end registers', self)
        lay_fbend = QGridLayout(gbox_fbend)
        lay_fbend.addWidget(self._ld_gpiohph, 0, 0)
        lay_fbend.addWidget(self._sb_gpiohph, 0, 1)
        lay_fbend.addWidget(self._ld_gpiohat, 1, 0)
        lay_fbend.addWidget(self._sb_gpiohat, 1, 1)
        lay_fbend.addWidget(self._ld_gpiovph, 2, 0)
        lay_fbend.addWidget(self._sb_gpiovph, 2, 1)
        lay_fbend.addWidget(self._ld_gpiovat, 3, 0)
        lay_fbend.addWidget(self._sb_gpiovat, 3, 1)
        lay_fbend.addWidget(self._ld_gpiolph, 4, 0)
        lay_fbend.addWidget(self._sb_gpiolph, 4, 1)
        lay_fbend.addWidget(self._ld_gpiolat, 5, 0)
        lay_fbend.addWidget(self._sb_gpiolat, 5, 1)
        lay_fbend.addWidget(self._ld_gpiobeph, 6, 0)
        lay_fbend.addWidget(self._sb_gpiobeph, 6, 1)
        lay_fbend.addWidget(self._ld_gpiobeat, 7, 0)
        lay_fbend.addWidget(self._sb_gpiobeat, 7, 1)
        lay_fbend.addLayout(lay_phases, 8, 0, 1, 2)
        return gbox_fbend

    def _setupPhaseServoLoopWidget(self):
        # # Phase Servo Loop
        self._ld_gpiolctrl = QLabel('Loop Ctrl', self)
        self._cb_gpiolctrl = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_SERVO_MODE')

        self._ld_gpiolsign = QLabel('Loop Sign', self)
        self._cb_gpiolsign = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_SERVO_SIGN')

        self._ld_gpiogain = QLabel('Gain', self)
        self._sb_gpiogain = PyDMSpinbox(
            self, self.dev_pref+':FBELT_SERVO_GAIN')
        self._sb_gpiogain.showStepExponent = False

        self._ld_gpiooff = QLabel('Offset', self)
        self._sb_gpiooff = PyDMSpinbox(
            self, self.dev_pref+':FBELT_SERVO_OFFSET')
        self._sb_gpiooff.showStepExponent = False

        self._ld_gpiohtrk = QLabel('Hor. Trk.', self)
        self._cb_gpiohtrk = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_SERVO_X_TRACK')

        self._ld_gpiovtrk = QLabel('Vert. Trk.', self)
        self._cb_gpiovtrk = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_SERVO_Y_TRACK')

        gbox_phsloop = QGroupBox('Phase Servo Loop', self)
        lay_phsloop = QGridLayout(gbox_phsloop)
        lay_phsloop.addWidget(self._ld_gpiolctrl, 0, 0)
        lay_phsloop.addWidget(self._cb_gpiolctrl, 0, 1)
        lay_phsloop.addWidget(self._ld_gpiolsign, 1, 0)
        lay_phsloop.addWidget(self._cb_gpiolsign, 1, 1)
        lay_phsloop.addWidget(self._ld_gpiogain, 2, 0)
        lay_phsloop.addWidget(self._sb_gpiogain, 2, 1)
        lay_phsloop.addWidget(self._ld_gpiooff, 3, 0)
        lay_phsloop.addWidget(self._sb_gpiooff, 3, 1)
        lay_phsloop.addWidget(self._ld_gpiohtrk, 4, 0)
        lay_phsloop.addWidget(self._cb_gpiohtrk, 4, 1)
        lay_phsloop.addWidget(self._ld_gpiovtrk, 5, 0)
        lay_phsloop.addWidget(self._cb_gpiovtrk, 5, 1)
        return gbox_phsloop

    def _setupThermoWidget(self):
        # # DS1822 ROM/Thermometer
        self._ld_gpiosts = QLabel('Status', self)
        self._lb_gpiosts = PyDMLabel(self, self.dev_pref+':FBE_DS1822_STAT')

        self._ld_gpiocsum = QLabel('CheckSum', self)
        self._lb_gpiocsum = PyDMLabel(self, self.dev_pref+':FBE_DS1822_XSUM')

        self._ld_gpiomod = QLabel('Modification', self)
        self._lb_gpiomod = PyDMLabel(self, self.dev_pref+':FBE_MOD_SENSE')

        self._ld_gpiodevid = QLabel('Device ID', self)
        self._lb_gpiodevid = PyDMLabel(self, self.dev_pref+':FBE_DS1822_DEVID')
        self._lb_gpiodevid.displayFormat = PyDMLabel.DisplayFormat.Hex

        self._ld_gpioser = QLabel('Serial', self)
        self._lb_gpioser = PyDMLabel(self, self.dev_pref+':FBE_DS1822_SERIAL')

        self._ld_gpiotemp = QLabel('Temperature', self)
        self._lb_gpiotemp = PyDMLabel(self, self.dev_pref+':FBE_TEMP')
        self._lb_gpiotemp.showUnits = True

        gbox_thermo = QGroupBox('DS1822 ROM/Thermometer', self)
        lay_thermo = QGridLayout(gbox_thermo)
        lay_thermo.addWidget(self._ld_gpiosts, 0, 0)
        lay_thermo.addWidget(self._lb_gpiosts, 0, 1)
        lay_thermo.addWidget(self._ld_gpiocsum, 1, 0)
        lay_thermo.addWidget(self._lb_gpiocsum, 1, 1)
        lay_thermo.addWidget(self._ld_gpiomod, 2, 0)
        lay_thermo.addWidget(self._lb_gpiomod, 2, 1)
        lay_thermo.addWidget(self._ld_gpiodevid, 3, 0)
        lay_thermo.addWidget(self._lb_gpiodevid, 3, 1)
        lay_thermo.addWidget(self._ld_gpioser, 4, 0)
        lay_thermo.addWidget(self._lb_gpioser, 4, 1)
        lay_thermo.addWidget(self._ld_gpiotemp, 5, 0)
        lay_thermo.addWidget(self._lb_gpiotemp, 5, 1)
        return gbox_thermo

    def _setupOtherControlsWidget(self):
        # # FBE
        self._ld_gpiomode = QLabel('Mode', self)
        self._cb_gpiomode = PyDMEnumComboBox(
            self, self.dev_pref+':FBELT_FAN_MODE')

        self._ld_gpiofanspd = QLabel('Fan Speed', self)
        self._lb_gpiofanspd = PyDMLabel(self, self.dev_pref+':FBE_FANMON')
        self._lb_gpiofanspd.showUnits = True

        self._ld_gpiotempsp = QLabel('Temperature Setpoint', self)
        self._sb_gpiotempsp = PyDMSpinbox(
            self, self.dev_pref+':FBELT_FAN_SETPT')
        self._sb_gpiotempsp.showStepExponent = False

        gbox_fbe = QGroupBox(self)
        lay_fbe = QGridLayout(gbox_fbe)
        lay_fbe.addWidget(self._ld_gpiomode, 0, 0)
        lay_fbe.addWidget(self._cb_gpiomode, 0, 1)
        lay_fbe.addWidget(self._ld_gpiofanspd, 1, 0)
        lay_fbe.addWidget(self._lb_gpiofanspd, 1, 1)
        lay_fbe.addWidget(self._ld_gpiotempsp, 2, 0)
        lay_fbe.addWidget(self._sb_gpiotempsp, 2, 1)
        return gbox_fbe

    def _setupMonitorsWidget(self):
        # # ADC Average
        self._si_gpioadcav = MyScaleIndicator(
            self, self.dev_pref+':CIC_MEAN')
        self._si_gpioadcav.setObjectName('si')
        self._si_gpioadcav.setStyleSheet('#si{min-height: 4em;}')

        gbox_adcav = QGroupBox('ADC Average', self)
        lay_adcav = QGridLayout(gbox_adcav)
        lay_adcav.addWidget(self._si_gpioadcav)

        # # Phase servo output
        self._si_gpioservodlt = MyScaleIndicator(
            self, self.dev_pref+':FBELT_SERVO_DELTA')
        self._ld_gpioservomax = QLabel(
            '<h4>Max</h4>', self, alignment=Qt.AlignCenter)
        self._sb_gpioservomax = PyDMSpinbox(
            self, self.dev_pref+':FBELT_SERVO_MAXDELTA')
        self._sb_gpioservomax.showStepExponent = False

        gbox_phsout = QGroupBox('Phase Servo Output', self)
        lay_phsout = QGridLayout(gbox_phsout)
        lay_phsout.addWidget(self._si_gpioservodlt, 0, 0, 2, 1)
        lay_phsout.addWidget(
            self._ld_gpioservomax, 0, 1, alignment=Qt.AlignBottom)
        lay_phsout.addWidget(
            self._sb_gpioservomax, 1, 1, alignment=Qt.AlignTop)
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
