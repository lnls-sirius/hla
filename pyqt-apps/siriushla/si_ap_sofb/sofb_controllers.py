"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QWidget, QLabel, QGroupBox, QPushButton, \
                            QGridLayout, QVBoxLayout, QHBoxLayout, \
                            QSpacerItem, QSizePolicy, QFormLayout
from qtpy.QtCore import Qt, QSize
from pydm.widgets import PyDMCheckbox, PyDMSpinbox, PyDMLabel, \
                            PyDMPushButton, PyDMEnumComboBox
from siriushla.widgets import SiriusConnectionSignal, PyDMStateButton, \
            SiriusDialog, SiriusLedAlert, SiriusLedState
import siriuspy.csdevice.orbitcorr as _csorb
from siriushla.widgets.windows import create_window_from_widget
import siriushla.util as _util

from siriushla.si_ap_sofb.selection_matrix import SelectionMatrix
from siriushla.si_ap_sofb.orbit_controllers import CorrectionOrbitController, \
    ReferenceController

CONST = _csorb.get_consts('SI')


class _BaseWidget(QWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.prefix = prefix

    def create_pair(self, parent, pvname):
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(9, 0, 0, 0)
        pdm_spbx = PyDMSpinbox(
            wid, init_channel=self.prefix+pvname+'-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(
            wid, init_channel=self.prefix+pvname+'-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_spbx)
        hbl.addWidget(pdm_lbl)
        return wid

    def create_pair_sel(self, parent, pvname):
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(9, 0, 0, 9)
        pdm_cbbx = PyDMEnumComboBox(
            wid, init_channel=self.prefix+pvname+'-Sel')
        pdm_lbl = PyDMLabel(
            wid, init_channel=self.prefix+pvname+'-Sts')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_cbbx)
        hbl.addWidget(pdm_lbl)
        return wid


class ControlSOFB(_BaseWidget):

    def __init__(self, parent, prefix, ctrls, acc='SI'):
        super().__init__(parent, prefix)
        self.ctrls = ctrls
        self.acc = acc
        self.setup_ui()

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        grp_bx = QGroupBox(self)
        hbl.addWidget(grp_bx)
        grp_bx.setTitle(self.acc + ' SOFB Control')

        vbl = QVBoxLayout(grp_bx)
        vbl.setContentsMargins(9, -1, -1, 9)

        # ####################################################################
        # ########################### STATUS #################################
        # ####################################################################
        btn = QPushButton('Open Status', grp_bx)
        Window = create_window_from_widget(
            StatusWidget, name='StatusWindow')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix)
        pdm_led = SiriusLedAlert(grp_bx, init_channel=self.prefix+'Status-Mon')
        pdm_led.setMinimumHeight(20)
        pdm_led.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        vbl.addItem(hbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ########################## Orbit PVs ###############################
        # ####################################################################
        fbl = QFormLayout()
        fbl.setSpacing(9)
        vbl.addItem(fbl)

        lbl = QLabel('Orbit Mode', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        wid = self.create_pair_sel(grp_bx, 'OrbitMode')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Correct:', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        combo = CorrectionOrbitController(
            self, self.prefix, self.ctrls, self.acc)
        combo.rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'OrbitMode-Sts'+'", "trigger": true}]}]')
        fbl.addRow(lbl, combo)

        lbl = QLabel('as diff to:', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        combo = ReferenceController(
            self, self.prefix, self.ctrls, self.acc)
        fbl.addRow(lbl, combo)

        Window = create_window_from_widget(
            AcqControlWidget, name='AcqControlWindow')
        btn = QPushButton('Acquisition Configuration Details', grp_bx)
        _util.connect_window(btn, Window, grp_bx, prefix=self.prefix)
        fbl.addRow(btn)

        vbl.addSpacing(40)
        # ####################################################################
        # ####################### Synchronization ############################
        # ####################################################################
        lbl = QLabel('Synchronize Kicks', grp_bx)
        pdm_btn = PyDMStateButton(
            grp_bx, init_channel=self.prefix+'SyncKicks-Sel')
        pdm_btn.setMinimumHeight(20)
        pdm_btn.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_btn)
        vbl.addItem(hbl)
        # ####################################################################
        # ####################### Selection Lists ############################
        # ####################################################################
        vbl.addSpacing(40)
        btns = dict()
        lbl = QLabel('Corrs and BPMs selection', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        Window = create_window_from_widget(
            SelectionMatrix, name='SelectionWindow')
        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            btns[dev] = QPushButton(dev, grp_bx)
            _util.connect_window(
                btns[dev], Window, self,
                dev=dev, prefix=self.prefix, acc=self.acc)
        gbl = QGridLayout()
        gbl.setSpacing(9)
        gbl.addWidget(lbl, 0, 0, 1, 2)
        gbl.addWidget(btns['BPMX'], 1, 0)
        gbl.addWidget(btns['BPMY'], 2, 0)
        gbl.addWidget(btns['CH'], 1, 1)
        gbl.addWidget(btns['CV'], 2, 1)

        pdm_chbx = PyDMCheckbox(grp_bx, init_channel=self.prefix+'RFEnbl-Sel')
        pdm_chbx.setText('Enable RF')
        pdm_led = SiriusLedState(grp_bx, init_channel=self.prefix+'RFEnbl-Sts')
        pdm_led.setMinimumHeight(20)
        pdm_led.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        hbl.addWidget(pdm_chbx)
        hbl.addWidget(pdm_led)
        gbl.addItem(hbl, 3, 1)
        vbl.addItem(gbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################## Configurations ############################
        # ####################################################################
        pdm_btn = PyDMPushButton(
            grp_bx, label='Configure Correctors',
            init_channel=self.prefix+'ConfigCorrs-Cmd', pressValue=1)
        pdm_btn2 = PyDMPushButton(
            grp_bx, label='Configure Orbit Acquisition',
            init_channel=self.prefix+'OrbitTrigAcqConfig-Cmd', pressValue=1)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pdm_btn)
        hbl.addWidget(pdm_btn2)
        vbl.addItem(hbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ####################### Auto Correction ############################
        # ####################################################################
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[0] in (1, 3)", "channels": [{"channel": "' +
            self.prefix+'OrbitMode-Sts'+'", "trigger": true}]}]')
        lbl = QLabel('Enable Auto Correction', grp_bx)
        pdm_btn = PyDMStateButton(
            grp_bx, init_channel=self.prefix+'AutoCorr-Sel')
        pdm_btn.rules = rules
        pdm_btn.setMinimumHeight(20)
        pdm_btn.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_btn)
        vbl.addItem(hbl)

        lbl = QLabel('Frequency [Hz]', grp_bx)
        wid = self.create_pair(grp_bx, 'AutoCorrFreq')
        fbl = QFormLayout()
        fbl.setHorizontalSpacing(9)
        fbl.addRow(lbl, wid)
        vbl.addItem(fbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################## Kicks Configs. ############################
        # ####################################################################
        wid = KicksConfigWidget(grp_bx, self.prefix, False)
        vbl.addWidget(wid)
        vbl.addSpacing(40)
        # ####################################################################
        # ###################### Manual Correction ###########################
        # ####################################################################
        lbl = QLabel('Manual Correction')
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lbl)

        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'AutoCorr-Sts'+'", "trigger": true}]}]')
        pdm_pbtn = PyDMPushButton(
            grp_bx, 'Calculate Kicks', pressValue=1,
            init_channel=self.prefix+'CalcCorr-Cmd')
        pdm_pbtn.rules = rules
        vbl.addWidget(pdm_pbtn)
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "(ch[1] in (1, 3)) and not ch[0]", ' +
            '"channels": [' +
            '{"channel": "'+self.prefix+'AutoCorr-Sts'+'", "trigger": true},' +
            '{"channel": "'+self.prefix+'OrbitMode-Sel'+'", "trigger": true}' +
            ']}]')
        pdm_pbtn2 = PyDMPushButton(
            grp_bx, 'Apply All',
            pressValue=_csorb.ApplyCorr.All,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn2.rules = rules
        vbl2 = QVBoxLayout()
        vbl2.addWidget(pdm_pbtn)
        vbl2.addWidget(pdm_pbtn2)

        pdm_pbtn = PyDMPushButton(
            grp_bx, 'Apply CH',
            pressValue=_csorb.ApplyCorr.CH,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn.rules = rules
        pdm_pbtn2 = PyDMPushButton(
            grp_bx, 'Apply CV',
            pressValue=_csorb.ApplyCorr.CV,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn2.rules = rules
        pdm_pbtn3 = PyDMPushButton(
            grp_bx, 'Apply RF',
            pressValue=_csorb.ApplyCorr.RF,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn3.rules = rules
        vbl3 = QVBoxLayout()
        vbl3.setSpacing(9)
        vbl3.addWidget(pdm_pbtn)
        vbl3.addWidget(pdm_pbtn2)
        vbl3.addWidget(pdm_pbtn3)

        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addItem(vbl2)
        hbl.addItem(vbl3)
        vbl.addItem(hbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ################## Response Matrix Configurations ##################
        # ####################################################################
        Window = create_window_from_widget(
            RespMatWidget, name='RespMatWindow')
        btn = QPushButton('RespMat Configurations', grp_bx)
        vbl.addWidget(btn)
        _util.connect_window(btn, Window, self, prefix=self.prefix)

    def create_pair(self, parent, pvname):
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(0, 0, 0, 0)
        pdm_spbx = PyDMSpinbox(
            wid, init_channel=self.prefix+pvname+'-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(
            wid, init_channel=self.prefix+pvname+'-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_spbx)
        hbl.addWidget(pdm_lbl)
        return wid

    def create_pair_sel(self, parent, pvname):
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(0, 0, 0, 9)
        pdm_cbbx = PyDMEnumComboBox(
            wid, init_channel=self.prefix+pvname+'-Sel')
        pdm_lbl = PyDMLabel(
            wid, init_channel=self.prefix+pvname+'-Sts')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_cbbx)
        hbl.addWidget(pdm_lbl)
        return wid


class AcqControlWidget(_BaseWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent, prefix)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        gdl.setHorizontalSpacing(40)
        gdl.setVerticalSpacing(20)

        lbl = QLabel('General Configurations', self)
        lbl.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lbl, 0, 0, 1, 2)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 1, 0)

        grp_bx = QGroupBox('Orbit Mode', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair_sel(grp_bx, 'OrbitMode')
        fbl.addRow(wid)

        grp_bx = QGroupBox('Acquisition Rates', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Orbit [Hz]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitAcqRate')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Kicks [Hz]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'KickAcqRate')
        fbl.addRow(lbl, wid)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 1, 1)

        grp_bx = QGroupBox('Number of Orbits for Smoothing', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair(grp_bx, 'OrbitSmoothNPnts')
        fbl.addWidget(wid)
        pdm_btn = PyDMPushButton(
            init_channel=self.prefix+'OrbitSmoothReset-Cmd',
            pressValue=1,
            label='Reset Buffer')
        fbl.addWidget(pdm_btn)

        grp_bx = QGroupBox('MultiTurn Acquisition', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Index', grp_bx)
        wid = self.create_pair(grp_bx, 'OrbitMultiTurnIdx')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Time [ms]', grp_bx)
        pdm_lbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'OrbitMultiTurnIdxTime-Mon')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        fbl.addRow(lbl, pdm_lbl)

        lbl = QLabel('Triggered Acquisition Configurations', self)
        lbl.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lbl, 2, 0, 1, 2)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 3, 0)

        grp_bx = QGroupBox('Common Parameters', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Acquistion Channel', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigAcqChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Acquistion Trigger', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigAcqTrigger')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Number of Shots', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigNrShots')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Number of Samples', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigNrSamples')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Downsampling', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigDownSample')
        fbl.addRow(lbl, wid)

        fbl.addItem(QSpacerItem(20, 20))
        lbl = QLabel('Control Acquisition:', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        fbl.addRow(lbl)
        gdl2 = QGridLayout()
        fbl.addRow(gdl2)
        pdm_btn1 = PyDMPushButton(
            grp_bx, label='Start',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=_csorb.OrbitAcqCtrl.Start)
        pdm_btn2 = PyDMPushButton(
            grp_bx, label='Stop',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=_csorb.OrbitAcqCtrl.Stop)
        pdm_btn3 = PyDMPushButton(
            grp_bx, label='Abort',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=_csorb.OrbitAcqCtrl.Abort)
        pdmlbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'OrbitTrigAcqCtrl-Sts')
        pdmlbl.setAlignment(Qt.AlignCenter)
        gdl2.addWidget(pdm_btn1, 0, 0)
        gdl2.addWidget(pdm_btn2, 0, 1)
        gdl2.addWidget(pdm_btn3, 1, 0)
        gdl2.addWidget(pdmlbl, 1, 1)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 3, 1)

        grp_bx = QGroupBox('Data-Driven Trigger Parameters', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Channel', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Selection', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataSel')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Threshold', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigDataThres')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Hysteresis', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigDataHyst')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Polarity', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataPol')
        fbl.addRow(lbl, wid)

        grp_bx = QGroupBox('External Trigger Parameter', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Duration [ms]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigExtDuration')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Initial Delay [us]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigExtDelay')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Event Source', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigExtEvtSrc')
        fbl.addRow(lbl, wid)


class StatusWidget(_BaseWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent, prefix)
        self.setupui()

    def setupui(self):
        fml = QFormLayout(self)
        lab = QLabel('General Status', self)
        led = SiriusLedAlert(self, init_channel=self.prefix+'Status-Mon')
        led.setMinimumHeight(20)
        led.setMaximumHeight(40)
        fml.addRow(lab, led)
        grpbx = self.creategroupbox('Corr')
        fml.addRow(grpbx)
        grpbx = self.creategroupbox('Orbit')
        fml.addRow(grpbx)

    def creategroupbox(self, name):
        if name == 'Corr':
            labels = _csorb.StatusLabels.Corrs
            title = 'Correctors'
        else:
            labels = _csorb.StatusLabels.Orbit
            title = 'Orbit'
        wid = QGroupBox(title + ' Status', self)

        fbl = QFormLayout(wid)
        fbl.setHorizontalSpacing(20)
        fbl.setVerticalSpacing(20)
        channel = self.prefix + name + 'Status-Mon'
        for bit, label in enumerate(labels):
            led = SiriusLedAlert(self, channel, bit)
            led.setMinimumHeight(20)
            led.setMaximumHeight(40)
            lab = QLabel(label, self)
            fbl.addRow(led, lab)
        return wid


class KicksConfigWidget(_BaseWidget):

    def __init__(self, parent, prefix, show_details):
        super().__init__(parent, prefix)
        self.show_details = show_details
        self.setupui()

    def setupui(self):
        names = ('Correction Factors', 'Maximum Kicks', 'Maximum Delta Kicks')
        pvnames = ('CorrFactor', 'MaxKick', 'MaxDeltaKick')
        unitss = (
            ('[%]', '[%]', '[%]'),
            ('[urad]', '[urad]', '[Hz]'),
            ('[urad]', '[urad]', '[Hz]'), )
        if not self.show_details:
            names = names[:1]
            pvnames = pvnames[:1]
            unitss = unitss[:1]

        vbl = QVBoxLayout(self)
        for name, pvname, units in zip(names, pvnames, unitss):
            fbl = QFormLayout()
            fbl.setSpacing(9)
            lbl = QLabel(name, self)
            lbl.setAlignment(Qt.AlignCenter)
            fbl.addRow(lbl)
            for unit, pln in zip(units, ('CH', 'CV', 'RF')):
                lbl = QLabel(pln+' '+unit+'  ', self)
                fbl.addRow(
                    lbl, self.create_pair(self, pvname+pln))
            vbl.addItem(fbl)
            if self.show_details:
                vbl.addSpacing(40)
        if not self.show_details:
            Window = create_window_from_widget(
                KicksConfigWidget, name='KicksConfigWindow')
            btn = QPushButton('Show Details', self)
            vbl.addWidget(btn)
            _util.connect_window(
                btn, Window, self, prefix=self.prefix, show_details=True)


class RespMatWidget(_BaseWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent, prefix)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        grpbx = QGroupBox('RespMat Measurement', self)
        vbl.addWidget(grpbx)
        pdm_pbtn = PyDMPushButton(
            self, label="Start",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Start)
        pdm_pbtn.setEnabled(True)
        pdm_pbtn2 = PyDMPushButton(
            self, label="Stop",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Stop)
        pdm_pbtn2.setEnabled(True)
        pdm_pbtn3 = PyDMPushButton(
            self, label="Reset",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Reset)
        pdm_pbtn3.setEnabled(True)
        pdm_lbl = PyDMLabel(self, init_channel=self.prefix+'MeasRespMat-Mon')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        gdl = QGridLayout(grpbx)
        gdl.setSpacing(9)
        gdl.addWidget(pdm_pbtn, 0, 0)
        gdl.addWidget(pdm_pbtn2, 0, 1)
        gdl.addWidget(pdm_pbtn3, 1, 0)
        gdl.addWidget(pdm_lbl, 1, 1)
        gdl.addItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding),
            2, 0, 1, 2)

        fml = QFormLayout()
        fml.setSpacing(9)
        gdl.addItem(fml, 3, 0, 1, 2)
        lbl = QLabel('Meas. CH kick [urad]', self)
        wid = self.create_pair(self, 'MeasRespMatKickCH')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. CV kick [urad]', self)
        wid = self.create_pair(self, 'MeasRespMatKickCV')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. RF kick [Hz]', self)
        wid = self.create_pair(self, 'MeasRespMatKickRF')
        fml.addRow(lbl, wid)
        fml.addItem(QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        lbl = QLabel('Wait between kicks [s]', self)
        wid = self.create_pair(self, 'MeasRespMatWait')
        fml.addRow(lbl, wid)

        vbl.addSpacing(20)

        lbl = QLabel('Number of Sing. Vals.', self)
        pdm_spbx = PyDMSpinbox(
            self, init_channel=self.prefix+'NumSingValues-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(
            self, init_channel=self.prefix+'NumSingValues-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        fml = QFormLayout()
        fml.setSpacing(9)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pdm_spbx)
        hbl.addWidget(pdm_lbl)
        fml.addRow(lbl, hbl)
        vbl.addItem(fml)

        vbl.addSpacing(20)

        lbl = QLabel('Load RespMat', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lbl)
        pbtn = QPushButton('from File', self)
        pbtn2 = QPushButton('from ServConf', self)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pbtn)
        hbl.addWidget(pbtn2)
        vbl.addItem(hbl)
        # pdm_wplt = PyDMWaveformPlot(self.ResponseMatrix)
        # pdm_wplt.setShowXGrid(True)
        # pdm_wplt.setShowYGrid(True)
        # pdm_wplt.setBackgroundColor(QColor(255, 255, 255))
        # pdm_wplt.setCurves([
        #   '{"y_channel": "${PREFIX}SingValues-Mon", "x_channel": null, "name": "", "color": "black", "lineStyle": 0, "lineWidth": 1, "symbol": "o", "symbolSize": 10, "redraw_mode": 2}'])


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    pvs = [
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
        'OrbitRefX-RB', 'OrbitRefY-RB']
    chans = []
    for pv in pvs:
        chans.append(SiriusConnectionSignal(prefix+pv))
    win._channels = chans
    ctrls = {
        'Online Orbit': {
            'x': {
                'signal': chans[0].new_value_signal,
                'getvalue': chans[0].getvalue},
            'y': {
                'signal': chans[1].new_value_signal,
                'getvalue': chans[1].getvalue}},
        'Offline Orbit': {
            'x': {
                'signal': chans[2].new_value_signal,
                'getvalue': chans[2].getvalue},
            'y': {
                'signal': chans[3].new_value_signal,
                'getvalue': chans[3].getvalue}},
        'Reference Orbit': {
            'x': {
                'signal': chans[4].new_value_signal,
                'getvalue': chans[4].getvalue},
            'y': {
                'signal': chans[5].new_value_signal,
                'getvalue': chans[5].getvalue}}}
    wid = ControlSOFB(win, prefix, ctrls)
    hbl.addWidget(wid)
    win.resize(QSize(200, 1200))
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
