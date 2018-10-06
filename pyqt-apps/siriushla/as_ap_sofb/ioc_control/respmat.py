"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QWidget
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel, PyDMPushButton, \
                    PyDMWaveformPlot, PyDMCheckbox
import siriuspy.csdevice.orbitcorr as _csorb
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusLedState
from siriushla.util import connect_window
# from siriushla.si_ap_sofb.graphics.base import Graph

from siriushla.as_ap_sofb.ioc_control.respmat_enbllist import SelectionMatrix
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class RespMatWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc=acc)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        # ####################################################################
        # ####################### Selection Lists ############################
        # ####################################################################
        btns = dict()
        grpbx = QGroupBox('Corrs and BPMs selection', self)
        vbl.addWidget(grpbx)
        Window = create_window_from_widget(
            SelectionMatrix, name='SelectionWindow', size=(1000, 1800))
        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            btns[dev] = QPushButton(dev, grpbx)
            connect_window(
                btns[dev], Window, self,
                dev=dev, prefix=self.prefix, acc=self.acc)
        gdl = QGridLayout(grpbx)
        gdl.setSpacing(9)
        gdl.addWidget(btns['BPMX'], 0, 0)
        gdl.addWidget(btns['BPMY'], 1, 0)
        gdl.addWidget(btns['CH'], 0, 1)
        gdl.addWidget(btns['CV'], 1, 1)

        pdm_chbx = PyDMCheckbox(grpbx, init_channel=self.prefix+'RFEnbl-Sel')
        pdm_chbx.setText('Enable RF')
        pdm_led = SiriusLedState(grpbx, init_channel=self.prefix+'RFEnbl-Sts')
        pdm_led.setMinimumHeight(20)
        pdm_led.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        hbl.addWidget(pdm_chbx)
        hbl.addWidget(pdm_led)
        gdl.addItem(hbl, 2, 1)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################### Measurement ##############################
        # ####################################################################
        grpbx = QGroupBox('RespMat Measurement', self)
        vbl.addWidget(grpbx)
        pdm_pbtn = PyDMPushButton(
            grpbx, label="Start",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Start)
        pdm_pbtn.setEnabled(True)
        pdm_pbtn2 = PyDMPushButton(
            grpbx, label="Stop",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Stop)
        pdm_pbtn2.setEnabled(True)
        pdm_pbtn3 = PyDMPushButton(
            grpbx, label="Reset",
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=_csorb.MeasRespMatCmd.Reset)
        pdm_pbtn3.setEnabled(True)
        pdm_lbl = PyDMLabel(grpbx, init_channel=self.prefix+'MeasRespMat-Mon')
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
        lbl = QLabel('Meas. CH kick [urad]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatKickCH')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. CV kick [urad]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatKickCV')
        fml.addRow(lbl, wid)
        lbl = QLabel('Meas. RF kick [Hz]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatKickRF')
        fml.addRow(lbl, wid)
        fml.addItem(QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        lbl = QLabel('Wait between kicks [s]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatWait')
        fml.addRow(lbl, wid)

        vbl.addSpacing(40)
        # ####################################################################
        # ####################### Singular Values ############################
        # ####################################################################
        grpbx = QGroupBox('Singular Values', self)
        vbl.addWidget(grpbx)
        fml = QFormLayout(grpbx)
        lab = QLabel('Number used')
        wid = self.create_pair(grpbx, 'NumSingValues')
        fml.addRow(lab, wid)
        btn = QPushButton('Check Singular Values', grpbx)
        fml.addWidget(btn)
        Window = create_window_from_widget(
            SingularValues, name='SingularValues', size=(1000, 700))
        connect_window(btn, Window, grpbx, prefix=self.prefix)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################## Load/Save/Set #############################
        # ####################################################################
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


class SingularValues(QWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('Singular Values')
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        graph = PyDMWaveformPlot()
        graph.plotItem.showButtons()
        vbl.addWidget(graph)
        opts = dict(
            y_channel=self.prefix+'SingValues-Mon',
            color='white',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        cur = graph.curveAtIndex(0)
        cur.setSymbolBrush(255, 255, 255)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    wid = RespMatWidget(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
