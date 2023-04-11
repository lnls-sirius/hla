"""DiffCtrl Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QFormLayout, QLabel, QGroupBox
from pydm.widgets import PyDMPushButton
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusDialog, PyDMLed, SiriusLabel, \
    SiriusSpinbox, PyDMStateButton, SiriusLedState


class DiffCtrlDetails(SiriusDialog):
    """DiffCtrl Details."""

    def __init__(
            self, parent=None, prefix='', device='',
            pos_label='', neg_label=''):
        """Init."""
        super(DiffCtrlDetails, self).__init__(parent)
        self.dev_prefix = _PVName(device).substitute(prefix=prefix)
        self.setObjectName(self.dev_prefix.sec+'App')
        self.neg_label = neg_label
        self.neg_name = self.neg_label.split(' ')[0]
        self.pos_label = pos_label
        self.pos_name = self.pos_label.split(' ')[0]
        self.slit_name = self.pos_label.split(' ')[1]
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout()
        lay.setVerticalSpacing(15)

        label = QLabel(
            '<h3>'+self.dev_prefix+' Control Details</h3>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(label, 0, 0)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_status = QGroupBox('Status', self)
        gbox_status.setLayout(self._setupDetailedStatusLayout())

        gbox_force = QGroupBox('Positions', self)
        gbox_force.setLayout(self._setupPositionsLayout())

        gbox_limits = QGroupBox('Limits', self)
        gbox_limits.setLayout(self._setupLimitsLayout())

        lay.addWidget(gbox_general, 1, 0)
        lay.addWidget(gbox_status, 2, 0)
        lay.addWidget(gbox_force, 3, 0)
        lay.addWidget(gbox_limits, 4, 0)

        if 'Scrap' in self.dev_prefix:
            gbox_backlash = QGroupBox('Backlash Compensation', self)
            gbox_backlash.setLayout(self._setupBacklashCompLayout())
            lay.addWidget(gbox_backlash, 5, 0)

        self.setStyleSheet("""
            SiriusSpinbox, SiriusLabel{
                min-width: 7em; max-width: 7em;
            }""")
        self.setLayout(lay)

    def _setupGeneralInfoLayout(self):
        label_negmtrctrlpref = QLabel(
            self.neg_label + ' Motion Control: ', self)
        self.lb_negmtrctrlpref = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty=self.neg_name+'MotionCtrl-Cte'))
        self.lb_negmtrctrlpref.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        label_posmtrctrlpref = QLabel(
            self.pos_label + ' Motion Control: ', self)
        self.lb_posmtrctrlpref = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty=self.pos_name+'MotionCtrl-Cte'))
        self.lb_posmtrctrlpref.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_negmtrctrlpref, self.lb_negmtrctrlpref)
        flay.addRow(label_posmtrctrlpref, self.lb_posmtrctrlpref)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupDetailedStatusLayout(self):
        label_negdonemov = QLabel(
            self.neg_label + ' Motor Finished Move? ', self)
        self.led_negdonemov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty=self.neg_name+'DoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.led_negdonemov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_posdonemov = QLabel(
            self.pos_label + ' Motor Finished Move? ', self)
        self.led_posdonemov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty=self.pos_name+'DoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.led_posdonemov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_convok = QLabel('Convertion from virtual to measured'
                              '\ncoordinates was succesfully done? ', self)
        self.led_convok = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='CoordConvErr-Mon'),
            color_list=[PyDMLed.LightGreen, PyDMLed.Red])
        self.led_convok.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_negdonemov, self.led_negdonemov)
        flay.addRow(label_posdonemov, self.led_posdonemov)
        flay.addRow(label_convok, self.led_convok)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupPositionsLayout(self):
        self.pb_home = PyDMPushButton(
            parent=self, label='Do Homing', pressValue=1,
            init_channel=self.dev_prefix.substitute(propty='Home-Cmd'))

        self.pb_negdonemov = PyDMPushButton(
            parent=self, label='Force ' + self.neg_label + ' Position',
            pressValue=1, init_channel=self.dev_prefix.substitute(
                propty='Force'+self.neg_name+self.slit_name+'Pos-Cmd'))

        self.pb_posdonemov = PyDMPushButton(
            parent=self, label='Force ' + self.pos_label + ' Position',
            pressValue=1, init_channel=self.dev_prefix.substitute(
                propty='Force'+self.pos_name+self.slit_name+'Pos-Cmd'))

        for btn in [self.pb_home,
                    self.pb_negdonemov,
                    self.pb_posdonemov]:
            btn.setDefault(False)
            btn.setAutoDefault(False)

        label_forcecomplete = QLabel('Force Commands Completed? ', self)
        self.led_forcecomplete = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='ForceComplete-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.led_forcecomplete.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(self.pb_home)
        flay.addRow(self.pb_negdonemov)
        flay.addRow(self.pb_posdonemov)
        flay.addRow(label_forcecomplete, self.led_forcecomplete)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupLimitsLayout(self):
        prefposi = self.pos_name if 'Scrap' in self.dev_prefix else 'Pos'
        prefposi += self.slit_name
        prefposo = self.pos_name if 'Scrap' in self.dev_prefix else 'High'
        prefposo += self.slit_name if 'Scrap' in self.dev_prefix else ''
        prefnegi = self.neg_name if 'Scrap' in self.dev_prefix else 'Neg'
        prefnegi += self.slit_name
        prefnego = self.neg_name if 'Scrap' in self.dev_prefix else 'Low'
        prefnego += self.slit_name if 'Scrap' in self.dev_prefix else ''

        self.sb_posinnerlim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty=prefposi+'InnerLim-SP'))
        self.lb_posinnerlim = SiriusLabel(
            self, self.dev_prefix.substitute(propty=prefposi+'InnerLim-RB'),
            keep_unit=True)
        self.lb_posinnerlim.showUnits = True
        self.sb_posouterlim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty=prefposo+'OuterLim-SP'))
        self.lb_posouterlim = SiriusLabel(
            self, self.dev_prefix.substitute(propty=prefposo+'OuterLim-RB'),
            keep_unit=True)
        self.lb_posouterlim.showUnits = True
        self.sb_neginnerlim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty=prefnegi+'InnerLim-SP'))
        self.lb_neginnerlim = SiriusLabel(
            self, self.dev_prefix.substitute(propty=prefnegi+'InnerLim-RB'),
            keep_unit=True)
        self.lb_neginnerlim.showUnits = True
        self.sb_negouterlim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty=prefnego+'OuterLim-SP'))
        self.lb_negouterlim = SiriusLabel(
            self, self.dev_prefix.substitute(propty=prefnego+'OuterLim-RB'),
            keep_unit=True)
        self.lb_negouterlim.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel(self.pos_label+' Inner Limit:', self), 0, 0)
        lay.addWidget(self.sb_posinnerlim, 0, 1)
        lay.addWidget(self.lb_posinnerlim, 0, 2)
        lay.addWidget(QLabel(self.pos_label+' Outer Limit:', self), 1, 0)
        lay.addWidget(self.sb_posouterlim, 1, 1)
        lay.addWidget(self.lb_posouterlim, 1, 2)
        lay.addWidget(QLabel(self.neg_label+' Inner Limit:', self), 2, 0)
        lay.addWidget(self.sb_neginnerlim, 2, 1)
        lay.addWidget(self.lb_neginnerlim, 2, 2)
        lay.addWidget(QLabel(self.neg_label+' Outer Limit:', self), 3, 0)
        lay.addWidget(self.sb_negouterlim, 3, 1)
        lay.addWidget(self.lb_negouterlim, 3, 2)
        return lay

    def _setupBacklashCompLayout(self):
        self.sb_enblbacklashcomp = PyDMStateButton(
            self, self.dev_prefix.substitute(
                propty='EnblBacklashComp-Sel'))
        self.led_enblbacklashcomp = SiriusLedState(
            self, self.dev_prefix.substitute(
                propty='EnblBacklashComp-Sts'))
        self.sb_posbacklashdist = SiriusSpinbox(
            self, self.dev_prefix.substitute(
                propty=self.pos_name+self.slit_name+'BacklashDist-SP'))
        self.lb_posbacklashdist = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty=self.pos_name+self.slit_name+'BacklashDist-RB'),
            keep_unit=True)
        self.lb_posbacklashdist.showUnits = True
        self.sb_negbacklashdist = SiriusSpinbox(
            self, self.dev_prefix.substitute(
                propty=self.neg_name+self.slit_name+'BacklashDist-SP'))
        self.lb_negbacklashdist = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty=self.neg_name+self.slit_name+'BacklashDist-RB'),
            keep_unit=True)
        self.lb_negbacklashdist.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel('Enable Backlash Compensation:', self), 0, 0)
        lay.addWidget(self.sb_enblbacklashcomp, 0, 1)
        lay.addWidget(self.led_enblbacklashcomp, 0, 2)
        lay.addWidget(QLabel(self.pos_label+' Backlash Distance:', self), 1, 0)
        lay.addWidget(self.sb_posbacklashdist, 1, 1)
        lay.addWidget(self.lb_posbacklashdist, 1, 2)
        lay.addWidget(QLabel(self.neg_label+' Backlash Distance:', self), 2, 0)
        lay.addWidget(self.sb_negbacklashdist, 2, 1)
        lay.addWidget(self.lb_negbacklashdist, 2, 2)
        return lay
