"""Auxiliary dialogs module."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QHBoxLayout, QGridLayout, \
    QSizePolicy as QSzPlcy, QSpacerItem

from pydm.widgets import PyDMLabel

from siriushla.widgets import SiriusDialog, PyDMLed, PyDMLedMultiChannel


class APUAlarmDetails(SiriusDialog):
    """APU Alarm Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(parent)
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self.setObjectName('SIApp')
        self.setWindowTitle(device+' Alarm Details')
        self._setupUi()

    def _setupUi(self):
        self._ld_almaxctrl = QLabel('<h4>Axis Control</h4>', self)

        self._ld_almflag = QLabel('Flag', self)
        self._lb_almflag = PyDMLabel(self, self.dev_pref+':AlrmPhase-Mon')

        self._ld_almeid = QLabel('Error ID Code', self)
        self._lb_almeid = PyDMLabel(self, self.dev_pref+':AlrmPhaseErrID-Mon')

        self._ld_almsttdw = QLabel('State DWord', self)
        self._lb_almsttdw = PyDMLabel(
            self, self.dev_pref+':AlrmPhaseSttDW-Mon')

        self._ld_almsttcode = QLabel('State Code', self)
        self._lb_almsttcode = PyDMLabel(
            self, self.dev_pref+':AlrmPhaseStt-Mon')

        self._ld_almrack = QLabel('<h4>Rack</h4>', self)

        self._ld_almestop = QLabel('E-Stop button pressed', self)
        self._led_almestop = PyDMLed(self, self.dev_pref+':AlrmRackEStop-Mon')
        self._led_almestop.offColor = PyDMLed.LightGreen
        self._led_almestop.onColor = PyDMLed.Red

        self._ld_almkillpres = QLabel('Kill switch pressed', self)
        self._led_almkillpres = PyDMLed(
            self, self.dev_pref+':AlrmRackKill-Mon')
        self._led_almkillpres.offColor = PyDMLed.LightGreen
        self._led_almkillpres.onColor = PyDMLed.Red

        self._ld_almkilldsbl = QLabel('Kill switches disabled', self)
        self._led_almkilldsbl = PyDMLed(
            self, self.dev_pref+':AlrmRackKillDsbld-Mon')
        self._led_almkilldsbl.offColor = PyDMLed.LightGreen
        self._led_almkilldsbl.onColor = PyDMLed.Red

        self._ld_almpwrdsbl = QLabel('Power disabled', self)
        self._led_almpwrdsbl = PyDMLed(
            self, self.dev_pref+':AlrmRackPwrDsbld-Mon')
        self._led_almpwrdsbl.offColor = PyDMLed.LightGreen
        self._led_almpwrdsbl.onColor = PyDMLed.Red

        lay = QGridLayout(self)
        lay.addWidget(
            QLabel('<h4>Alarms</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self._ld_almaxctrl, 1, 0, 1, 2)
        lay.addWidget(self._ld_almflag, 2, 0)
        lay.addWidget(self._lb_almflag, 2, 1)
        lay.addWidget(self._ld_almeid, 3, 0)
        lay.addWidget(self._lb_almeid, 3, 1)
        lay.addWidget(self._ld_almsttdw, 4, 0)
        lay.addWidget(self._lb_almsttdw, 4, 1)
        lay.addWidget(self._ld_almsttcode, 5, 0)
        lay.addWidget(self._lb_almsttcode, 5, 1)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 6, 0)
        lay.addWidget(self._ld_almrack, 7, 0, 1, 2)
        lay.addWidget(self._ld_almestop, 8, 0)
        lay.addWidget(self._led_almestop, 8, 1)
        lay.addWidget(self._ld_almkillpres, 9, 0)
        lay.addWidget(self._led_almkillpres, 9, 1)
        lay.addWidget(self._ld_almkilldsbl, 10, 0)
        lay.addWidget(self._led_almkilldsbl, 10, 1)
        lay.addWidget(self._ld_almpwrdsbl, 11, 0)
        lay.addWidget(self._led_almpwrdsbl, 11, 1)


class APUInterlockDetails(SiriusDialog):
    """APU Interlock Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(parent)
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self.setObjectName('SIApp')
        self.setWindowTitle(device+' Interlock Details')
        self._setupUi()

    def _setupUi(self):
        self._ld_ilkistop = QLabel('Stop\n(Input)', self)
        self._led_ilkistop = PyDMLed(self, self.dev_pref+':IntlkInStop-Mon')
        self._led_ilkistop.offColor = PyDMLed.LightGreen
        self._led_ilkistop.onColor = PyDMLed.Red
        self._lb_ilkistop = PyDMLabel(self, self.dev_pref+':IntlkInStop-Mon')
        hbox_ilkistop = QHBoxLayout()
        hbox_ilkistop.addWidget(self._led_ilkistop)
        hbox_ilkistop.addWidget(self._lb_ilkistop)

        self._ld_ilkieopn = QLabel('Emergency Open Gap\n(Input)', self)
        self._led_ilkieopn = PyDMLed(self, self.dev_pref+':IntlkInEOpnGap-Mon')
        self._led_ilkieopn.offColor = PyDMLed.LightGreen
        self._led_ilkieopn.onColor = PyDMLed.Red
        self._lb_ilkieopn = PyDMLabel(
            self, self.dev_pref+':IntlkInEOpnGap-Mon')
        hbox_eopngap = QHBoxLayout()
        hbox_eopngap.addWidget(self._led_ilkieopn)
        hbox_eopngap.addWidget(self._lb_ilkieopn)

        self._ld_ilkogapopn = QLabel('Gap Opened\n(Output)', self)
        self._lb_ilkogapopn = PyDMLabel(
            self, self.dev_pref+':IntlkOutGapStt-Mon')
        self._lb_ilkogapopn.setAlignment(Qt.AlignCenter)

        self._ld_ilkostsok = QLabel('Status Ok\n(Output)', self)
        self._led_ilkostsok = PyDMLed(self, self.dev_pref+':IntlkOutStsOk-Mon')
        self._led_ilkostsok.offColor = PyDMLed.Red
        self._led_ilkostsok.onColor = PyDMLed.LightGreen

        self._ld_ilkoccps = QLabel('CCPS Enabled\n(Output)', self)
        self._led_ilkoccps = PyDMLed(
            self, self.dev_pref+':IntlkOutCCPSEnbld-Mon')
        self._led_ilkoccps.offColor = PyDMLed.Red
        self._led_ilkoccps.onColor = PyDMLed.LightGreen

        self._ld_ilkopwr = QLabel('Power Enabled\n(Output)', self)
        self._led_ilkopwr = PyDMLed(
            self, self.dev_pref+':IntlkOutPwrEnbld-Mon')
        self._led_ilkopwr.offColor = PyDMLed.Red
        self._led_ilkopwr.onColor = PyDMLed.LightGreen

        lay = QGridLayout(self)
        lay.addWidget(
            QLabel('<h4>Interlock status</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self._ld_ilkistop, 1, 0)
        lay.addLayout(hbox_ilkistop, 1, 1)
        lay.addWidget(self._ld_ilkieopn, 2, 0)
        lay.addLayout(hbox_eopngap, 2, 1)
        lay.addWidget(self._ld_ilkogapopn, 3, 0)
        lay.addWidget(self._lb_ilkogapopn, 3, 1)
        lay.addWidget(self._ld_ilkostsok, 4, 0)
        lay.addWidget(self._led_ilkostsok, 4, 1)
        lay.addWidget(self._ld_ilkoccps, 5, 0)
        lay.addWidget(self._led_ilkoccps, 5, 1)
        lay.addWidget(self._ld_ilkopwr, 6, 0)
        lay.addWidget(self._led_ilkopwr, 6, 1)


class APUHardLLDetails(SiriusDialog):
    """APU Hardware and LowLevel Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(parent)
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self.setObjectName('SIApp')
        self.setWindowTitle(device+' Hardware and LowLevel Details')
        self._setupUi()

    def _setupUi(self):
        self._ld_stthw = QLabel('Hardware state', self)
        self._led_stthw = PyDMLedMultiChannel(
            self, channels2values={
                self.dev_pref+':StateHw-Mon':
                    {'value': [0x4C, 0x3C], 'comp': 'in'}})  # in [Op, Ready]
        self._led_stthw.offColor = PyDMLed.Yellow
        self._led_stthw.onColor = PyDMLed.LightGreen
        self._led_stthw.setStyleSheet('max-width: 1.29em;')
        self._led_stthw.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        self._lb_stthw = PyDMLabel(self, self.dev_pref+':StateHw-Mon')

        self._ld_sttsys = QLabel('System state', self)
        self._led_sttsys = PyDMLedMultiChannel(
            self, channels2values={self.dev_pref+':State-Mon': 1})  # 1: Op
        self._led_sttsys.offColor = PyDMLed.Yellow
        self._led_sttsys.onColor = PyDMLed.LightGreen
        self._led_sttsys.setStyleSheet('max-width: 1.29em;')
        self._led_sttsys.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        self._lb_sttsys = PyDMLabel(self, self.dev_pref+':State-Mon')

        self._ld_isopr = QLabel('Is operational', self)
        self._led_isopr = PyDMLed(self, self.dev_pref+':IsOperational-Mon')
        self._led_isopr.offColor = PyDMLed.Red
        self._led_isopr.onColor = PyDMLed.LightGreen
        self._led_isopr.setStyleSheet('max-width: 1.29em;')
        self._led_isopr.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)

        lay_hwsys = QGridLayout(self)
        lay_hwsys.addWidget(
            QLabel('<h4>Hardware&&LowLevel</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 3)
        lay_hwsys.addWidget(self._ld_stthw, 2, 0)
        lay_hwsys.addWidget(self._led_stthw, 2, 1)
        lay_hwsys.addWidget(self._lb_stthw, 2, 2)
        lay_hwsys.addWidget(self._ld_sttsys, 3, 0)
        lay_hwsys.addWidget(self._led_sttsys, 3, 1)
        lay_hwsys.addWidget(self._lb_sttsys, 3, 2)
        lay_hwsys.addWidget(self._ld_isopr, 4, 0)
        lay_hwsys.addWidget(self._led_isopr, 4, 1)
