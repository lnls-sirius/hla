from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QFormLayout, QLabel, QGroupBox
from pydm.widgets import PyDMPushButton
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusDialog, PyDMLed, SiriusLabel, SiriusSpinbox


class DiffCtrlDetails(SiriusDialog):

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super(DiffCtrlDetails, self).__init__(parent)
        self.dev_prefix = _PVName(device).substitute(prefix=prefix)
        self.setObjectName(self.dev_prefix.sec+'App')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>'+self.dev_prefix+' Control Details</h3>', self,
                       alignment=Qt.AlignCenter)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_status = QGroupBox('Status', self)
        gbox_status.setLayout(self._setupDetailedStatusLayout())

        gbox_force = QGroupBox('Commands to Force Positions', self)
        gbox_force.setLayout(self._setupForceCommandsLayout())

        gbox_limits = QGroupBox('Limits', self)
        gbox_limits.setLayout(self._setupLimitsLayout())

        self.setStyleSheet("""
            SiriusSpinbox, SiriusLabel{
                min-width: 5em; max-width: 5em;
            }""")

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(label, 0, 0)
        lay.addWidget(gbox_general, 1, 0)
        lay.addWidget(gbox_status, 2, 0)
        lay.addWidget(gbox_force, 3, 0)
        lay.addWidget(gbox_limits, 4, 0)
        self.setLayout(lay)

    def _setupGeneralInfoLayout(self):
        label_NegMtrCtrlPrefix = QLabel('Negative Motion Control: ', self)
        self.lb_NegMtrCtrlPrefix = SiriusLabel(
            self, self.dev_prefix.substitute(propty='NegativeMotionCtrl-Cte'))
        self.lb_NegMtrCtrlPrefix.setStyleSheet("""
            max-width:14.20em; max-height:1.29em;""")

        label_PosMtrCtrlPrefix = QLabel('Positive Motion Control: ', self)
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
        label_NegDoneMov = QLabel('Negative Edge Motor Finished Move? ', self)
        self.PyDMLed_NegDoneMov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='NegativeDoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_NegDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_PosDoneMov = QLabel('Positive Edge Motor Finished Move? ', self)
        self.PyDMLed_PosDoneMov = PyDMLed(
            parent=self, init_channel=self.dev_prefix.substitute(
                propty='PositiveDoneMov-Mon'),
            color_list=[PyDMLed.Red, PyDMLed.LightGreen])
        self.PyDMLed_PosDoneMov.setStyleSheet("""
            max-width:7.10em; max-height:1.29em;""")

        label_ConvOk = QLabel('Convertion from virtual to measured'
                              '\ncoordanates was succesfully done? ', self)
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

    def _setupForceCommandsLayout(self):
        self.PyDMPushButton_DoHome = PyDMPushButton(
            parent=self, label='Do Homing', pressValue=1,
            init_channel=self.dev_prefix+':Home-Cmd')

        self.PyDMPushButton_NegDoneMov = PyDMPushButton(
            parent=self, label='Force Negative Edge Position', pressValue=1,
            init_channel=self.dev_prefix.substitute(
                propty='ForceNegativeEdgePos-Cmd'))

        self.PyDMPushButton_PosDoneMov = PyDMPushButton(
            parent=self, label='Force Positive Edge Position', pressValue=1,
            init_channel=self.dev_prefix.substitute(
                propty='ForcePositiveEdgePos-Cmd'))

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
        self.sb_PosEdgeInnerLim.showStepExponent = False
        self.lb_PosEdgeInnerLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='PosEdgeInnerLim-RB'))
        self.sb_NegEdgeInnerLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='NegEdgeInnerLim-SP'))
        self.sb_NegEdgeInnerLim.showStepExponent = False
        self.lb_NegEdgeInnerLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='NegEdgeInnerLim-RB'))
        self.sb_LowOuterLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='LowOuterLim-SP'))
        self.sb_LowOuterLim.showStepExponent = False
        self.lb_LowOuterLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='LowOuterLim-RB'))
        self.sb_HighOuterLim = SiriusSpinbox(
            self, self.dev_prefix.substitute(propty='HighOuterLim-SP'))
        self.sb_HighOuterLim.showStepExponent = False
        self.lb_HighOuterLim = SiriusLabel(
            self, self.dev_prefix.substitute(propty='HighOuterLim-RB'))

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel('Positive Edge Inner Limit:', self), 0, 0)
        lay.addWidget(self.sb_PosEdgeInnerLim, 0, 1)
        lay.addWidget(self.lb_PosEdgeInnerLim, 0, 2)
        lay.addWidget(QLabel('Negative Edge Inner Limit:', self), 1, 0)
        lay.addWidget(self.sb_NegEdgeInnerLim, 1, 1)
        lay.addWidget(self.lb_NegEdgeInnerLim, 1, 2)
        lay.addWidget(QLabel('Low Outer Limit:', self), 2, 0)
        lay.addWidget(self.sb_LowOuterLim, 2, 1)
        lay.addWidget(self.lb_LowOuterLim, 2, 2)
        lay.addWidget(QLabel('High Outer Limit:', self), 3, 0)
        lay.addWidget(self.sb_HighOuterLim, 3, 1)
        lay.addWidget(self.lb_HighOuterLim, 3, 2)
        return lay
