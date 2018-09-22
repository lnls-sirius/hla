"""Define Controllers for the orbits displayed in the graphic."""

from functools import partial as _part
from qtpy.QtWidgets import QWidget, QLabel, QGroupBox, QPushButton, \
                            QGridLayout, QVBoxLayout, QHBoxLayout, \
                            QSpacerItem, QSizePolicy, QFormLayout
from qtpy.QtCore import Qt, QSize
from pydm.widgets import PyDMCheckbox, PyDMSpinbox, PyDMLabel, \
                            PyDMPushButton, PyDMEnumComboBox
from siriushla.widgets import SiriusConnectionSignal, PyDMStateButton, \
            SiriusDialog, SiriusLedAlert, SiriusLedState
import siriuspy.csdevice.orbitcorr as _csorb
import siriushla.util as _util
from siriushla.si_ap_sofb.selection_matrix import SelectionMatrix

CONST = _csorb.get_consts('SI')


class ControlSOFB(QWidget):

    def __init__(self, parent, prefix):
        super(ControlSOFB, self).__init__(parent)
        self.prefix = prefix
        self.setup_ui()

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        grp_bx = QGroupBox(self)
        hbl.addWidget(grp_bx)
        grp_bx.setTitle('Correction Parameters')

        vbl = QVBoxLayout(grp_bx)
        vbl.setContentsMargins(9, -1, -1, 9)

        lbl = QLabel('Correction Mode', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        combo = PyDMEnumComboBox(
            grp_bx, init_channel=self.prefix+'CorrMode-Sel')
        fbl = QFormLayout()
        fbl.setSpacing(9)
        fbl.addRow(lbl, combo)
        vbl.addItem(fbl)

        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ####################################################################
        # ######################## Kicks Configs. ############################
        # ####################################################################
        names = ('Correction Factors', 'Maximum Kicks', 'Maximum Delta Kicks')
        pvnames = ('CorrFactor', 'MaxKick', 'MaxDeltaKick')
        unitss = (
            ('[%]', '[%]', '[%]'),
            ('[urad]', '[urad]', '[Hz]'),
            ('[urad]', '[urad]', '[Hz]'), )
        for name, pvname, units in zip(names, pvnames, unitss):
            fbl = QFormLayout()
            fbl.setSpacing(9)
            lbl = QLabel(name, grp_bx)
            lbl.setAlignment(Qt.AlignCenter)
            fbl.addRow(lbl)
            for unit, pln in zip(units, ('CH', 'CV', 'RF')):
                lbl = QLabel(pln+' '+unit+'  ', grp_bx)
                fbl.addRow(
                    lbl, self.create_pair(grp_bx, pvname+pln))
            vbl.addItem(fbl)
            vbl.addItem(QSpacerItem(
                20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ####################################################################
        # ####################### Synchronization ############################
        # ####################################################################
        lbl = QLabel('Synchronize Kicks', grp_bx)
        pdm_btn = PyDMStateButton(
            grp_bx, init_channel=self.prefix+'SyncKicks-Sel')
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_btn)
        vbl.addItem(hbl)
        # ####################################################################
        # ####################### Selection Lists ############################
        # ####################################################################
        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        btns = dict()
        lbl = QLabel('Corrs and BPMs selection', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            btns[dev] = QPushButton(dev, grp_bx)
            _util.connect_window(
                btns[dev], MySelectionWindow, self,
                dev=dev, prefix=self.prefix)
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
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        hbl.addWidget(pdm_chbx)
        hbl.addWidget(pdm_led)
        gbl.addItem(hbl, 3, 1)
        vbl.addItem(gbl)

        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ####################################################################
        # ######################## Configurations ############################
        # ####################################################################
        pdm_btn = PyDMPushButton(
            grp_bx, label='Configure Correctors',
            init_channel=self.prefix+'ConfigCorrs-Cmd', pressValue=1)
        pdm_btn2 = PyDMPushButton(
            grp_bx, label='Configure Timing',
            init_channel=self.prefix+'ConfigTiming-Cmd', pressValue=1)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pdm_btn)
        hbl.addWidget(pdm_btn2)
        vbl.addItem(hbl)

        btn = QPushButton('Status', grp_bx)
        _util.connect_window(
            btn, StatusWindow, self, prefix=self.prefix)
        pdm_led = SiriusLedAlert(grp_bx, init_channel=self.prefix+'Status-Mon')
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        vbl.addItem(hbl)

        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ####################################################################
        # ####################### Auto Correction ############################
        # ####################################################################
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[0]", "channels": [{"channel": "' +
            self.prefix+'CorrMode-Sts'+'", "trigger": true}]}]')
        lbl = QLabel('Enable Auto Correction', grp_bx)
        pdm_btn = PyDMStateButton(
            grp_bx, init_channel=self.prefix+'AutoCorr-Sel')
        pdm_btn.rules = rules
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

        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
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
            '"expression": "(not ch[0]) and ch[1]", ' +
            '"channels": [' +
            '{"channel": "'+self.prefix+'AutoCorr-Sts'+'", "trigger": true},' +
            '{"channel": "'+self.prefix+'CorrMode-Sel'+'", "trigger": true}' +
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

        vbl.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ####################################################################
        # ################## Response Matrix Configurations ##################
        # ####################################################################
        lbl = QLabel('RespMat Measurement', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lbl)
        pdm_pbtn = PyDMPushButton(
            grp_bx, label="Start",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Start)
        pdm_pbtn.setEnabled(True)
        pdm_pbtn2 = PyDMPushButton(
            grp_bx, label="Stop",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Stop)
        pdm_pbtn2.setEnabled(True)
        pdm_pbtn3 = PyDMPushButton(
            grp_bx, label="Reset",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Reset)
        pdm_pbtn3.setEnabled(True)
        pdm_lbl = PyDMLabel(grp_bx, init_channel=self.prefix+'MeasRespMat-Mon')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        gdl = QGridLayout()
        gdl.setSpacing(9)
        gdl.addWidget(pdm_pbtn, 0, 0)
        gdl.addWidget(pdm_pbtn2, 0, 1)
        gdl.addWidget(pdm_pbtn3, 1, 0)
        gdl.addWidget(pdm_lbl, 1, 1)
        vbl.addItem(gdl)

        fml = QFormLayout()
        fml.setSpacing(9)
        vbl.addItem(fml)
        lbl = QLabel('Meas. CH kick [urad]', grp_bx)
        wid = self.create_pair(grp_bx, 'MeasRespMatKickCH')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. CV kick [urad]', grp_bx)
        wid = self.create_pair(grp_bx, 'MeasRespMatKickCV')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. RF kick [Hz]', grp_bx)
        wid = self.create_pair(grp_bx, 'MeasRespMatKickRF')
        fml.addRow(lbl, wid)
        lbl = QLabel('Wait between kicks [s]', grp_bx)
        wid = self.create_pair(grp_bx, 'MeasRespMatWait')
        fml.addRow(lbl, wid)

        lbl = QLabel('Number of Sing. Vals.', grp_bx)
        pdm_spbx = PyDMSpinbox(
            grp_bx, init_channel=self.prefix+'NumSingValues-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'NumSingValues-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        fml = QFormLayout()
        fml.setSpacing(9)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pdm_spbx)
        hbl.addWidget(pdm_lbl)
        fml.addRow(lbl, hbl)
        vbl.addItem(fml)

        lbl = QLabel('Load RespMat', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lbl)
        pbtn = QPushButton('from File', grp_bx)
        pbtn2 = QPushButton('from ServConf', grp_bx)
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


class StatusWindow(SiriusDialog):

    def __init__(self, parent, prefix):
        super(StatusWindow, self).__init__(parent)
        self.prefix = prefix
        lab_cor = SiriusConnectionSignal(prefix+'CorrStatusLabels-Cte')
        lab_orb = SiriusConnectionSignal(prefix+'OrbitStatusLabels-Cte')
        lab_cor.new_value_signal[list].connect(
            _part(self.creategroupbox, 'Correctors', 'Corr'))
        lab_orb.new_value_signal[list].connect(
            _part(self.creategroupbox, 'Orbit', 'Orbit'))
        self._channels = [lab_cor, lab_orb]
        self._created = {'Corr': False, 'Orbit': False}

        self.setupui()

    def setupui(self):
        self.setWindowTitle('SOFB Status')
        self.fml = QFormLayout(self)
        lab = QLabel('General Status', self)
        led = SiriusLedAlert(self, init_channel=self.prefix+'Status-Mon')
        self.fml.addRow(lab, led)

    def creategroupbox(self, label, name, labels):
        if self._created[name]:
            return
        wid = QGroupBox(label + ' Status', self)
        self.fml.addRow(wid)

        fbl = QFormLayout(wid)
        fbl.setHorizontalSpacing(20)
        fbl.setVerticalSpacing(20)
        channel = self.prefix + name + 'Status-Mon'
        for bit, label in enumerate(labels):
            led = SiriusLedAlert(self, channel, bit)
            lab = QLabel(label, self)
            fbl.addRow(led, lab)
            self._app.establish_widget_connections(led)
        self._created[name] = True


class MySelectionWindow(SiriusDialog):

    def __init__(self, parent, dev, prefix):
        super().__init__(parent)
        hbl = QHBoxLayout(self)
        wid = SelectionMatrix(self, dev, prefix)
        hbl.addWidget(wid)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    wid = ControlSOFB(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
