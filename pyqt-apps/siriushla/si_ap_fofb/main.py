"""High level FOFB main module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QHBoxLayout, QWidget, QGridLayout, \
    QLabel
import qtawesome as qta

from pydm.widgets import PyDMCheckbox

from siriuspy.clientconfigdb import ConfigDBClient

from ..util import connect_window, get_appropriate_color, \
    connect_newprocess
from ..widgets.windows import create_window_from_widget
from ..widgets import SiriusLedState, SiriusConnectionSignal as _ConnSig, \
    SiriusEnumComboBox, SiriusLabel, SiriusSpinbox
from ..as_ap_sofb.ioc_control.respmat import RespMatWidget as _RespMatWidget

from .base import BaseWidget
from .respmat_enbllist import SelectionMatrix


class MainWindow(_RespMatWidget, BaseWidget):
    """FOFB RespMat widget."""

    def __init__(self, parent, device, prefix=''):
        BaseWidget.__init__(self, parent, device, prefix=prefix)
        self.setWindowTitle('SI - FOFB')
        self.setupui()
        self._config_type = 'si_fastorbcorr_respm'
        self._client = ConfigDBClient(config_type=self._config_type)
        self.EXT = self._csorb.respmat_fname.split('.')[1]
        self.EXT_FLT = 'RespMat Files (*.{})'.format(self.EXT)
        self.last_dir = self.DEFAULT_DIR

        self._respmat_sp = _ConnSig(
            self.devpref.substitute(propty='RespMat-SP'))
        self._respmat_rb = _ConnSig(
            self.devpref.substitute(propty='RespMat-RB'))

    def get_selection_lists_widget(self, parent):
        """Selection lists."""
        sel_wid = QWidget(parent)
        sel_lay = QGridLayout(sel_wid)
        sel_lay.setVerticalSpacing(15)

        icon = qta.icon('fa5s.hammer', color=get_appropriate_color('SI'))
        Window = create_window_from_widget(
            SelectionMatrix, title='Corrs and BPMs selection', icon=icon)
        btn = QPushButton('', sel_wid)
        btn.setObjectName('btn')
        btn.setIcon(qta.icon('fa5s.tasks'))
        btn.setToolTip('Open window to select BPMs and correctors')
        btn.setStyleSheet(
            '#btn{min-width:3.8em; max-width:3.8em;\
            min-height:2em; max-height:2em; icon-size:25px;}')
        connect_window(
            btn, Window, None, device=self.device, prefix=self.prefix)
        sel_lay.addWidget(btn, 0, 0)

        hlay = QHBoxLayout()
        pdm_chbx = PyDMCheckbox(
            sel_wid, self.devpref.substitute(propty='UseRF-Sel'))
        pdm_chbx.setText('Use RF')
        pdm_led = SiriusLedState(
            sel_wid, self.devpref.substitute(propty='UseRF-Sts'))
        hlay.addWidget(pdm_chbx)
        hlay.addWidget(pdm_led)
        sel_lay.addLayout(hlay, 0, 1)

        btn = QPushButton('', sel_wid)
        btn.setToolTip('Visualize RespMat')
        btn.setIcon(qta.icon('mdi.chart-line'))
        btn.setObjectName('btn')
        btn.setStyleSheet('#btn{max-width:40px; icon-size:40px;}')
        connect_newprocess(
            btn, [f'sirius-hla-si-ap-fofb.py', '--matrix'])
        sel_lay.addWidget(btn, 0, 2)

        hlay = QHBoxLayout()
        hlay.setAlignment(Qt.AlignCenter)
        lbl = QLabel('Norm.Mode: ', self, alignment=Qt.AlignRight)
        pdm_cbb = SiriusEnumComboBox(
            sel_wid, self.devpref.substitute(propty='InvRespMatNormMode-Sel'))
        pdm_lbl = SiriusLabel(
            sel_wid, self.devpref.substitute(propty='InvRespMatNormMode-Sts'))
        hlay.addWidget(lbl)
        hlay.addWidget(pdm_cbb)
        hlay.addWidget(pdm_lbl)
        sel_lay.addLayout(hlay, 1, 0, 1, 3)

        hlay = QHBoxLayout()
        hlay.setAlignment(Qt.AlignCenter)
        lbl = QLabel('Loop Gain: ', self, alignment=Qt.AlignRight)
        pdm_sbx = SiriusSpinbox(
            sel_wid, self.devpref.substitute(propty='LoopGain-SP'))
        pdm_sbx.showStepExponent = False
        pdm_lbl = SiriusLabel(
            sel_wid, self.devpref.substitute(propty='LoopGain-RB'))
        hlay.addWidget(lbl)
        hlay.addWidget(pdm_sbx)
        hlay.addWidget(pdm_lbl)
        sel_lay.addLayout(hlay, 2, 0, 1, 3)

        return sel_wid
