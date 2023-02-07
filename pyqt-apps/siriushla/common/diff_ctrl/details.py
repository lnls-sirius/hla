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
        self.pos_label = pos_label
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
        label_NegMtrCtrlPrefix = QLabel(
            self.neg_label + ' Motion Control: ', self)
        self.lb_NegMtrCtrlPrefix = SiriusLabel(
            self, self.dev_prefix.substitute(propty='NegativeMotionCtrl-Cte'))
        self.lb_NegMtrCtrlPrefix.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        label_PosMtrCtrlPrefix = QLabel(
            self.pos_label + ' Motion Control: ', self)
        self.lb_PosMtrCtrlPrefix = SiriusLabel(
            self, self.dev_prefix.substitute(propty='PositiveMotionCtrl-Cte'))
        self.lb_PosMtrCtrlPrefix.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_NegMtrCtrlPrefix, self.lb_NegMtrCtrlPrefix)
        flay.addRow(label_PosMtrCtrlPrefix, self.lb_PosMtrCtrlPrefix)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupDetailedStatusLayout(self):
        label_NegDoneMov = QLabel(
            self.neg_label + ' Motor Finished Move? ', self)
        self.PyDMLed_NegDoneMov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='NegativeDoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_NegDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_PosDoneMov = QLabel(
            self.pos_label + ' Motor Finished Move? ', self)
        self.PyDMLed_PosDoneMov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='PositiveDoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_PosDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_ConvOk = QLabel('Convertion from virtual to measured'
                              '\ncoordinates was succesfully done? ', self)
        self.PyDMLed_ConvOk = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='CoordConvErr-Mon'),
            color_list=[PyDMLed.LightGreen, PyDMLed.Red])
        self.PyDMLed_ConvOk.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_NegDoneMov, self.PyDMLed_NegDoneMov)
        flay.addRow(label_PosDoneMov, self.PyDMLed_PosDoneMov)
        flay.addRow(label_ConvOk, self.PyDMLed_ConvOk)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupPositionsLayout(self):
        self.PyDMPushButton_DoHome = PyDMPushButton(
            parent=self, label='Do Homing', pressValue=1,
            init_channel=self.dev_prefix.substitute(propty='Home-Cmd'))

        self.PyDMPushButton_NegDoneMov = PyDMPushButton(
            parent=self, label='Force ' + self.neg_label + ' Position',
            pressValue=1, init_channel=self.dev_prefix.substitute(
                propty='ForceNegativeEdgePos-Cmd'))

        self.PyDMPushButton_PosDoneMov = PyDMPushButton(
            parent=self, label='Force ' + self.pos_label + ' Position',
            pressValue=1, init_channel=self.dev_prefix.substitute(
                propty='ForcePositiveEdgePos-Cmd'))

        for btn in [self.PyDMPushButton_DoHome,
                    self.PyDMPushButton_NegDoneMov,
                    self.PyDMPushButton_PosDoneMov]:
            btn.setDefault(False)
            btn.setAutoDefault(False)

        label_ForceComplete = QLabel('Force Commands Completed? ', self)
        self.PyDMLed_ForceComplete = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='ForceComplete-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_ForceComplete.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(self.PyDMPushButton_DoHome)
        flay.addRow(self.PyDMPushButton_NegDoneMov)
        flay.addRow(self.PyDMPushButton_PosDoneMov)
        flay.addRow(label_ForceComplete, self.PyDMLed_ForceComplete)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupLimitsLayout(self):
        self.sb_PosEdgeInnerLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='PosEdgeInnerLim-SP'))
        self.lb_PosEdgeInnerLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='PosEdgeInnerLim-RB'),
            keep_unit=True)
        self.lb_PosEdgeInnerLim.showUnits = True
        self.sb_NegEdgeInnerLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='NegEdgeInnerLim-SP'))
        self.lb_NegEdgeInnerLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='NegEdgeInnerLim-RB'),
            keep_unit=True)
        self.lb_NegEdgeInnerLim.showUnits = True
        self.sb_LowOuterLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='LowOuterLim-SP'))
        self.lb_LowOuterLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='LowOuterLim-RB'),
            keep_unit=True)
        self.lb_LowOuterLim.showUnits = True
        self.sb_HighOuterLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='HighOuterLim-SP'))
        self.lb_HighOuterLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='HighOuterLim-RB'),
            keep_unit=True)
        self.lb_HighOuterLim.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel(self.pos_label+' Inner Limit:', self), 0, 0)
        lay.addWidget(self.sb_PosEdgeInnerLim, 0, 1)
        lay.addWidget(self.lb_PosEdgeInnerLim, 0, 2)
        lay.addWidget(QLabel(self.pos_label+' Outer Limit:', self), 1, 0)
        lay.addWidget(self.sb_HighOuterLim, 1, 1)
        lay.addWidget(self.lb_HighOuterLim, 1, 2)
        lay.addWidget(QLabel(self.neg_label+' Inner Limit:', self), 2, 0)
        lay.addWidget(self.sb_NegEdgeInnerLim, 2, 1)
        lay.addWidget(self.lb_NegEdgeInnerLim, 2, 2)
        lay.addWidget(QLabel(self.neg_label+' Outer Limit:', self), 3, 0)
        lay.addWidget(self.sb_LowOuterLim, 3, 1)
        lay.addWidget(self.lb_LowOuterLim, 3, 2)
        return lay

    def _setupBacklashCompLayout(self):
        self.sb_EnblBacklashComp = PyDMStateButton(
            self, self.dev_prefix.substitute(
                propty='EnblBacklashComp-Sel'))
        self.led_EnblBacklashComp = SiriusLedState(
            self, self.dev_prefix.substitute(
                propty='EnblBacklashComp-Sts'))
        self.sb_PosEdgeBacklashDist = SiriusSpinbox(
            self, self.dev_prefix.substitute(
                propty='PositiveEdgeBacklashDist-SP'))
        self.lb_PosEdgeBacklashDist = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty='PositiveEdgeBacklashDist-RB'), keep_unit=True)
        self.lb_PosEdgeBacklashDist.showUnits = True
        self.sb_NegEdgeBacklashDist = SiriusSpinbox(
            self, self.dev_prefix.substitute(
                propty='NegativeEdgeBacklashDist-SP'))
        self.lb_NegEdgeBacklashDist = SiriusLabel(
            self, self.dev_prefix.substitute(
                propty='NegativeEdgeBacklashDist-RB'), keep_unit=True)
        self.lb_NegEdgeBacklashDist.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel('Enable Backlash Compensation:', self), 0, 0)
        lay.addWidget(self.sb_EnblBacklashComp, 0, 1)
        lay.addWidget(self.led_EnblBacklashComp, 0, 2)
        lay.addWidget(QLabel(self.pos_label+' Backlash Distance:', self), 1, 0)
        lay.addWidget(self.sb_PosEdgeBacklashDist, 1, 1)
        lay.addWidget(self.lb_PosEdgeBacklashDist, 1, 2)
        lay.addWidget(QLabel(self.neg_label+' Backlash Distance:', self), 2, 0)
        lay.addWidget(self.sb_NegEdgeBacklashDist, 2, 1)
        lay.addWidget(self.lb_NegEdgeBacklashDist, 2, 2)
        return lay
