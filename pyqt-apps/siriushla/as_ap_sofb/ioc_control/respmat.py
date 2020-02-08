"""Define Controllers for the orbits displayed in the graphic."""

import pathlib as _pathlib
from datetime import datetime as _datetime
import numpy as _np
from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QMessageBox, QFileDialog, QWidget, QTabWidget
from qtpy.QtCore import Qt
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMPushButton, PyDMCheckbox
from siriuspy.csdevice.orbitcorr import ConstTLines
from siriuspy.clientconfigdb import ConfigDBClient, ConfigDBException
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusLedState, SiriusConnectionSignal
from siriushla.util import connect_window, get_appropriate_color
from siriushla.as_ap_configdb import LoadConfigDialog, SaveConfigDialog

from .respmat_enbllist import SelectionMatrix
from .base import BaseWidget
from ..graphics import SingularValues, ShowMatrixWidget


class RespMatWidget(BaseWidget):

    DEFAULT_DIR = _pathlib.Path.home().as_posix()

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc=acc)
        self.setupui()
        self._config_type = acc.lower() + '_orbcorr_respm'
        self._client = ConfigDBClient(config_type=self._config_type)
        self.EXT = self._csorb.RESPMAT_FILENAME.split('.')[1]
        self.EXT_FLT = 'RespMat Files (*.{})'.format(self.EXT)
        self.last_dir = self.DEFAULT_DIR

        self._respmat_sp = SiriusConnectionSignal(prefix+'RespMat-SP')
        self._respmat_rb = SiriusConnectionSignal(prefix+'RespMat-RB')

    def setupui(self):
        gbox = QGroupBox('Matrix', self)
        gbox.setObjectName('grbx')
        gbox.setStyleSheet('#grbx{min-height:13.0em; max-height:13.0em;}')
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(gbox)
        vbl = QVBoxLayout(gbox)
        tabw = QTabWidget(gbox)
        vbl.addWidget(tabw)

        mainwid = QWidget(tabw)
        vbl = QVBoxLayout(mainwid)
        tabw.addTab(mainwid, 'Main')

        # ####################################################################
        # ####################### Selection Lists ############################
        # ####################################################################
        hbl = QHBoxLayout()
        hbl.setSpacing(6)
        vbl.addLayout(hbl)

        grpbx = QGroupBox('Corrs and BPMs selection', mainwid)
        hbl.addWidget(grpbx)
        icon = qta.icon('fa5s.hammer', color=get_appropriate_color(self.acc))
        Window = create_window_from_widget(
            SelectionMatrix, title='Corrs and BPMs selection', icon=icon)
        hbl2 = QHBoxLayout(grpbx)
        btn = QPushButton('', grpbx)
        btn.setObjectName('btn')
        btn.setIcon(qta.icon('fa5s.tasks'))
        btn.setToolTip('Open window to select BPMs and correctors')
        btn.setStyleSheet(
            '#btn{min-width:3.8em; max-width:3.8em;\
            min-height:2em; max-height:2em; icon-size:25px;}')
        connect_window(btn, Window, None, prefix=self.prefix, acc=self.acc)
        hbl2.addWidget(btn)

        if self.acc == 'SI':
            pdm_chbx = PyDMCheckbox(
                grpbx, init_channel=self.prefix+'RFEnbl-Sel')
            pdm_chbx.setText('use RF')
            pdm_led = SiriusLedState(
                grpbx, init_channel=self.prefix+'RFEnbl-Sts')
            hbl2.addStretch()
            hbl2.addWidget(pdm_chbx)
            hbl2.addWidget(pdm_led)

        btn = QPushButton('', mainwid)
        btn.setToolTip('Visualize RespMat')
        btn.setIcon(qta.icon('mdi.chart-line'))
        btn.setObjectName('btn')
        btn.setStyleSheet('#btn{max-width:40px; icon-size:40px;}')
        Window = create_window_from_widget(
            ShowMatrixWidget, title='Check RespMat')
        connect_window(btn, Window, mainwid, prefix=self.prefix, acc=self.acc)
        hbl.addWidget(btn)

        # ####################################################################
        # ####################### Singular Values ############################
        # ####################################################################

        grpbx = QGroupBox('Singular Values', mainwid)
        vbl.addWidget(grpbx)
        fml = QVBoxLayout(grpbx)
        wid = self.create_pair(grpbx, 'NrSingValues')
        btn = QPushButton('', grpbx)
        btn.setToolTip('Check Singular Values')
        btn.setIcon(qta.icon('mdi.chart-line'))
        btn.setObjectName('btn')
        btn.setStyleSheet('#btn{max-width:30px; icon-size:30px;}')
        hbl = QHBoxLayout()
        hbl.addWidget(wid)
        hbl.addWidget(btn)
        fml.addItem(hbl)
        Window = create_window_from_widget(
            SingularValues, title='Check Singular Values')
        connect_window(btn, Window, grpbx, prefix=self.prefix)

        # ####################################################################
        # ######################### Measurement ##############################
        # ####################################################################
        grpbx = QWidget(tabw)
        vbl = QVBoxLayout(grpbx)
        tabw.addTab(grpbx, 'Meas')

        strt = PyDMPushButton(
            grpbx,
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=ConstTLines.MeasRespMatCmd.Start)
        strt.setEnabled(True)
        strt.setToolTip('Start Measurement')
        strt.setIcon(qta.icon('fa5s.play'))
        strt.setObjectName('strt')
        strt.setStyleSheet(
            '#strt{min-width:25px; max-width:25px; icon-size:20px;}')
        stop = PyDMPushButton(
            grpbx,
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=ConstTLines.MeasRespMatCmd.Stop)
        stop.setEnabled(True)
        stop.setToolTip('Stop Measurement')
        stop.setIcon(qta.icon('fa5s.stop'))
        stop.setObjectName('stop')
        stop.setStyleSheet(
            '#stop{min-width:25px; max-width:25px; icon-size:20px;}')
        rst = PyDMPushButton(
            grpbx,
            init_channel=self.prefix+"MeasRespMat-Cmd",
            pressValue=ConstTLines.MeasRespMatCmd.Reset)
        rst.setEnabled(True)
        rst.setToolTip('Reset Measurement Status')
        rst.setIcon(qta.icon('fa5s.sync'))
        rst.setObjectName('conf')
        rst.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')
        lbl = PyDMLabel(grpbx, init_channel=self.prefix+'MeasRespMat-Mon')
        lbl.setAlignment(Qt.AlignCenter)
        hbl = QHBoxLayout()
        hbl.setSpacing(8)
        vbl.addItem(hbl)
        hbl.addWidget(strt)
        hbl.addWidget(stop)
        hbl.addWidget(rst)
        hbl.addStretch()
        hbl.addWidget(lbl)

        fml = QFormLayout()
        vbl.addSpacing(20)
        vbl.addItem(fml)
        lbl = QLabel('CH kick [urad]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatKickCH')
        fml.addRow(lbl, wid)
        lbl = QLabel('CV kick [urad]', grpbx)
        wid = self.create_pair(grpbx, 'MeasRespMatKickCV')
        fml.addRow(lbl, wid)
        if self.acc == 'SI':
            lbl = QLabel('RF kick [Hz]', grpbx)
            wid = self.create_pair(grpbx, 'MeasRespMatKickRF')
            fml.addRow(lbl, wid)
        fml.addItem(QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        lbl = QLabel('Wait [s]', grpbx)
        lbl.setToolTip('Time to wait between kicks')
        wid = self.create_pair(grpbx, 'MeasRespMatWait')
        fml.addRow(lbl, wid)

        # ####################################################################
        # ######################## Load/Save/Set #############################
        # ####################################################################
        grpbx = QWidget(tabw)
        gdl = QGridLayout(grpbx)
        tabw.addTab(grpbx, 'Load/Save')

        # gdl.setVerticalSpacing(15)
        lbl = QLabel('Load from:', grpbx)
        gdl.addWidget(lbl, 0, 0)
        pbtn = QPushButton('File', grpbx)
        pbtn.clicked.connect(self._load_respmat_from_file)
        gdl.addWidget(pbtn, 0, 1)
        pbtn = QPushButton('ServConf', grpbx)
        pbtn.clicked.connect(self._open_load_config_servconf)
        gdl.addWidget(pbtn, 0, 2)

        lbl = QLabel('Save to:', grpbx)
        gdl.addWidget(lbl, 1, 0)
        pbtn = QPushButton('File', grpbx)
        pbtn.clicked.connect(self._save_respmat_to_file)
        gdl.addWidget(pbtn, 1, 1)
        pbtn = QPushButton('ServConf', grpbx)
        pbtn.clicked.connect(self._open_save_config_servconf)
        gdl.addWidget(pbtn, 1, 2)

        gdl.addItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding),
            2, 0, 1, 2)

    def _save_respmat_to_file(self, _):
        header = '# ' + _datetime.now().strftime('%Y/%m/%d-%H:%M:%S') + '\n'
        if self.acc == 'SI':
            header += '# (BPMX, BPMY) [um] x (CH, CV, RF) [urad, Hz]' + '\n'
        else:
            header += '# (BPMX, BPMY) [um] x (CH, CV) [urad]' + '\n'
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save the Response Matrix',
            directory=self.last_dir,
            filter=self.EXT_FLT)
        fname = filename[0]
        if not fname:
            return
        fname += '' if fname.endswith(self.EXT) else ('.' + self.EXT)
        respm = self._respmat_rb.getvalue()
        respm = respm.reshape(-1, self._csorb.NR_CORRS)
        _np.savetxt(fname, respm, header=header)

    def _load_respmat_from_file(self):
        filename = QFileDialog.getOpenFileName(
            caption='Select a Response Matrix File.',
            directory=self.last_dir,
            filter=self.EXT_FLT)
        if not filename[0]:
            return
        respm = _np.loadtxt(filename[0])
        self._respmat_sp.send_value_signal[_np.ndarray].emit(respm.flatten())

    def _open_load_config_servconf(self):
        win = LoadConfigDialog(self._config_type, self)
        win.configname.connect(self._set_respm)
        win.show()

    def _set_respm(self, confname):
        data = self._client.get_config_value(confname)
        self._respmat_sp.send_value_signal[_np.ndarray].emit(
            _np.array(data).flatten())

    def _open_save_config_servconf(self):
        win = SaveConfigDialog(self._config_type, self)
        win.configname.connect(self._save_respm)
        win.show()

    def _save_respm(self, confname):
        val = self._respmat_rb.getvalue()
        val = val.reshape(-1, self._csorb.NR_CORRS)
        try:
            self._client.insert_config(confname, val.tolist())
        except (ConfigDBException, TypeError) as err:
            QMessageBox.warning(self, 'Warning', str(err), QMessageBox.Ok)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    acc = 'BO'
    prefix = pref+acc+'-Glob:AP-SOFB:'
    wid = RespMatWidget(win, prefix, acc)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import VACA_PREFIX as pref
    import sys
    _main()
