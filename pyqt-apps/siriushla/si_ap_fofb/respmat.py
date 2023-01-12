"""RespMat."""

from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QHBoxLayout, QWidget, QGridLayout, \
    QTabWidget, QAction, QMenu, QGroupBox, QVBoxLayout
import qtawesome as qta

from pydm.widgets.base import PyDMWidget
from pydm.widgets import PyDMCheckbox

from siriuspy.clientconfigdb import ConfigDBClient

from ..util import connect_window, connect_newprocess
from ..widgets.windows import create_window_from_widget
from ..widgets import SiriusConnectionSignal as _ConnSignal, \
    SiriusLedState, SiriusEnumComboBox, SiriusLabel, \
    SelectionMatrixWidget as SelectionWidget

from ..as_ap_sofb.ioc_control.respmat import RespMatWidget as _RespMatWidget
from ..as_ap_sofb.ioc_control.respmat_enbllist import \
    SingleSelMatrix as _SingleSelMatrix
from ..as_ap_sofb.ioc_control.base import CAPushButton

from .base import BaseObject, BaseWidget, get_fofb_icon
from .graphics import CorrGainWidget


class RespMatWidget(_RespMatWidget, BaseWidget):
    """FOFB RespMat widget."""

    def __init__(self, parent, device, prefix=''):
        BaseWidget.__init__(self, parent, device, prefix=prefix)
        self.setWindowTitle('SI - FOFB')
        self._enblrule = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.devpref.substitute(propty='LoopState-Sts') +
            '", "trigger": true}]}]')
        self.setupui()
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._config_type = 'si_fastorbcorr_respm'
        self._client = ConfigDBClient(config_type=self._config_type)
        self.EXT = self._csorb.respmat_fname.split('.')[1]
        self.EXT_FLT = 'RespMat Files (*.{})'.format(self.EXT)
        self.last_dir = self.DEFAULT_DIR

        self._respmat_sp = _ConnSignal(
            self.devpref.substitute(propty='RespMat-SP'))
        self._respmat_rb = _ConnSignal(
            self.devpref.substitute(propty='RespMat-RB'))

    def get_main_widget(self, parent):
        main_wid = QWidget(parent)
        main_lay = QVBoxLayout(main_wid)

        sel_gp = QGroupBox('Sel.')
        sel_gp.setLayout(QHBoxLayout())
        sel_gp.layout().setContentsMargins(0, 0, 0, 0)
        sel_wid = self.get_selection_lists_widget(sel_gp)
        sel_gp.layout().addWidget(sel_wid)
        main_lay.addWidget(sel_gp)

        norm_gp = QGroupBox('Norm.Mode')
        pdm_cbb = SiriusEnumComboBox(
            self, self.devpref.substitute(propty='InvRespMatNormMode-Sel'))
        pdm_cbb.rules = self._enblrule
        pdm_lbl = SiriusLabel(
            self, self.devpref.substitute(propty='InvRespMatNormMode-Sts'))
        nlay = QHBoxLayout(norm_gp)
        nlay.setAlignment(Qt.AlignCenter)
        nlay.addWidget(pdm_cbb)
        nlay.addWidget(pdm_lbl)
        main_lay.addWidget(norm_gp)

        svld_gp = QGroupBox('Load and Save')
        svld_gp.setLayout(QHBoxLayout())
        svld_gp.layout().setContentsMargins(0, 0, 0, 0)
        svld_wid = self.get_saveload_widget(svld_gp)
        svld_gp.layout().addWidget(svld_wid)
        main_lay.addWidget(svld_gp)

        return main_wid

    def get_selection_lists_widget(self, parent):
        """Selection lists."""
        sel_wid = QWidget(parent)
        sel_lay = QGridLayout(sel_wid)
        sel_lay.setVerticalSpacing(15)

        icon = get_fofb_icon()
        window = create_window_from_widget(
            SelectionMatrix,
            title=self.acc + ' - FOFB - Corrs and BPMs selection',
            icon=icon)
        btn = CAPushButton('', sel_wid)
        btn.rules = self._enblrule
        btn.setObjectName('btn')
        btn.setIcon(qta.icon('fa5s.tasks'))
        btn.setToolTip('Open window to select BPMs and correctors')
        btn.setStyleSheet(
            '#btn{min-width:3.8em; max-width:3.8em;\
            min-height:2em; max-height:2em; icon-size:25px;}')
        connect_window(
            btn, window, None, device=self.device, prefix=self.prefix)
        sel_lay.addWidget(btn, 0, 0)

        pdm_chbx = PyDMCheckbox(
            sel_wid, self.devpref.substitute(propty='UseRF-Sel'))
        pdm_chbx.rules = self._enblrule
        pdm_chbx.setText('use RF')
        pdm_led = SiriusLedState(
            sel_wid, self.devpref.substitute(propty='UseRF-Sts'))
        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(pdm_chbx)
        hlay.addWidget(pdm_led)
        hlay.addStretch()
        sel_lay.addLayout(hlay, 0, 1)

        btn = QPushButton('', sel_wid)
        btn.setToolTip('Visualize Response Matrices')
        btn.setIcon(qta.icon('mdi.chart-line'))
        btn.setObjectName('btn')
        btn.setStyleSheet('#btn{max-width:40px; icon-size:40px;}')
        btnmenu = QMenu(btn)
        cmd = ['sirius-hla-si-ap-fofb.py', '--matrix', '--property']
        act_respm = QAction('RespMat - Physiscs Units', self)
        connect_newprocess(act_respm, cmd + ['RespMat-Mon', ])
        btnmenu.addAction(act_respm)
        act_invrespm = QAction('InvRespMat - Physiscs Units', self)
        connect_newprocess(act_invrespm, cmd + ['InvRespMat-Mon', ])
        btnmenu.addAction(act_invrespm)
        act_respmhw = QAction('RespMat - Hardware Units', self)
        connect_newprocess(act_respmhw, cmd + ['RespMatHw-Mon', ])
        btnmenu.addAction(act_respmhw)
        act_invrespmhw = QAction('InvRespMat - Hardware Units', self)
        connect_newprocess(act_invrespmhw, cmd + ['InvRespMatHw-Mon', ])
        btnmenu.addAction(act_invrespmhw)
        act_coeffs = QAction('Corrector Coefficients', self)
        connect_newprocess(act_coeffs, cmd + ['CorrCoeffs-Mon', ])
        btnmenu.addAction(act_coeffs)
        act_gains = QAction('Corrector Gains', self)
        window = create_window_from_widget(
            CorrGainWidget, title='Corrector Gains', icon=icon)
        connect_window(
            act_gains, window, None, device=self.device, prefix=self.prefix)
        btnmenu.addAction(act_gains)
        btn.setMenu(btnmenu)
        sel_lay.addWidget(btn, 0, 2)

        return sel_wid


class SingleSelMatrix(_SingleSelMatrix, BaseObject):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, device, prefix=''):
        """Initialize the matrix data of the specified dev."""

        # initialize BaseObject
        BaseObject.__init__(self, device, prefix=prefix)
        self.dev = dev
        self.devpos = {
            'BPMX': self._csorb.bpm_pos,
            'BPMY': self._csorb.bpm_pos,
            'CH': self._csorb.ch_pos,
            'CV': self._csorb.cv_pos}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (self._csorb.bpm_names, self._csorb.bpm_nicknames),
            'BPMY': (self._csorb.bpm_names, self._csorb.bpm_nicknames),
            'CH': (self._csorb.ch_names, self._csorb.ch_nicknames),
            'CV': (self._csorb.cv_names, self._csorb.cv_nicknames)}

        # initialize SelectionWidget
        SelectionWidget.__init__(
            self, parent=parent, title=dev + "List",
            has_bothplanes=dev.lower().startswith('bpm'))

        # initialize PyDMWidget
        init_channel = self.devpref.substitute(propty=self.dev+'EnblList-RB')
        PyDMWidget.__init__(self, init_channel=init_channel)

        self.pv_sp = _ConnSignal(init_channel.replace('-RB', '-SP'))
        self.pv_otpl = _ConnSignal(self.devpref.substitute(
            propty=self.devotpl[self.dev]+'EnblList-SP'))

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)
        self.applyBothPlanesClicked.connect(_part(self.send_value, other=True))

    def get_headers(self):
        _, nicks = self.devnames[self.dev]
        top_headers = sorted({nick[2:] for nick in nicks})
        top_headers = top_headers[-2:] + top_headers[:-2]
        side_headers = sorted({nick[:2] for nick in nicks})
        side_headers.append(side_headers[0])
        return top_headers, side_headers

    def get_positions(self):
        top_headers, side_headers = self.headers
        positions = list()
        for idx in range(len(self.devnames[self.dev][0])):
            _, nicks = self.devnames[self.dev]
            rsize, hsize, i = len(nicks), len(side_headers), 0
            j = top_headers.index(nicks[idx][2:])
            if not (idx+1) % rsize:
                i += hsize-1
            else:
                i += ((idx % rsize) + 1) // len(top_headers)
            positions.append((i, j))
        return positions


class SelectionMatrix(BaseWidget):

    def __init__(self, parent, device, prefix=''):
        super().__init__(parent, device, prefix=prefix)
        tab = QTabWidget(self)
        tab.setObjectName('SITab')
        hbl = QHBoxLayout(self)
        hbl.addWidget(tab)
        hbl.setContentsMargins(0, 0, 0, 0)

        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            wid = SingleSelMatrix(tab, dev, self.device, prefix=self.prefix)
            tab.addTab(wid, dev)
