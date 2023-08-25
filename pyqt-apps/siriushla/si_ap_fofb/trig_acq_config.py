"""System identification module."""

from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, \
    QGroupBox, QCheckBox, QSizePolicy as QSzPlcy, QVBoxLayout, \
    QSpacerItem, QHBoxLayout, QPushButton, QTabWidget

from pydm.widgets import PyDMPushButton, PyDMLineEdit

from siriuspy.namesys import SiriusPVName as _PVName, join_name

from ..util import connect_window, get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusLabel, \
    SiriusEnumComboBox, SiriusSpinbox, PyDMStateButton, \
    SiriusLedState, SiriusWaveformPlot, SiriusAlarmFrame
from ..widgets.windows import create_window_from_widget
from ..as_di_bpms.base import GraphWave
from ..common.afc_acq_core import LogicalTriggers, PhysicalTriggers
from .base import get_fofb_icon


class _AcqBaseWindow(SiriusMainWindow):
    """Acquisition base window"""

    CONV_IDX2BPM = {
        0: 'M1',
        1: 'M2',
        2: 'C1-1',
        3: 'C1-2',
        4: 'C2',
        5: 'C3-1',
        6: 'C3-2',
        7: 'C4',
    }

    DEFAULT_COLORS = [
        QColor(0, 0, 0),  # Black
        QColor(100, 100, 100),  # DarkGray
        QColor(0, 0, 255),  # Blue
        QColor(15, 105, 0),  # Green
        QColor(255, 69, 0),  # Orangered
        QColor(210, 210, 0),  # Yellow
        QColor(88, 57, 39),  # Brown
        QColor(255, 0, 255)  # Magenta
    ]

    ACQCORE = ''

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.corrs = [
            join_name(
                sec='SI', sub=self.device.sub[:2]+sub,
                dis='PS', dev='FC'+plane)
            for sub in ['M1', 'M2', 'C2', 'C3'] for plane in ['H', 'V']]
        self.setWindowTitle('SI - FOFB Acquisitions - ' + self.ACQCORE)
        self.sec = 'SI' if self.device.sec == 'IA' else self.device.sec
        self.app_color = get_appropriate_color(self.sec)
        self.setObjectName(self.sec+'App')
        self.setWindowIcon(get_fofb_icon(color=self.app_color))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _get_pvname(self, propty):
        propty = self.ACQCORE + propty
        return self.devpref.substitute(propty=propty)

    def _create_graph(self, title, channels2names, add_scale=None):
        graph = GraphWave()
        graph.graph.setTitle(title)
        graph.graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False, tickTextWidth=50)
        graph.graph.setStyleSheet('PlotWidget{min-width: 30em;}')
        for i, chn in enumerate(channels2names):
            opts = dict(
                y_channel=chn,
                name=channels2names[chn],
                color=self.DEFAULT_COLORS[i],
                lineStyle=1,
                lineWidth=1,
                add_scale=add_scale)
            graph.addChannel(**opts)
        if len(channels2names) == 1:
            cbx = graph.findChild(QCheckBox)
            cbx.setVisible(False)
            lbl = QLabel('XX-XXX', self)
            lbl.setStyleSheet(
                'QLabel{color:transparent; min-width:3.5em; max-width:3.5em;}')
            graph.vbl.addWidget(lbl)
        else:
            cbxs = graph.findChildren(QCheckBox)
            for cbx in cbxs:
                cbx.setStyleSheet(
                    'QCheckBox{min-width:3.5em;max-width:3.5em;}')
        return graph

    def _basicSettingsWidget(self):
        ld_chan = QLabel('Channel', self)
        self.ec_chan = SiriusEnumComboBox(
            self, self._get_pvname('Channel-Sel'))
        self.lb_chan = SiriusLabel(self, self._get_pvname('Channel-Sts'))

        ld_dtype = QLabel('DataType', self)
        self.ec_dtype = SiriusEnumComboBox(self, self._get_pvname('DataType'))

        ld_rep = QLabel('Repeat Acquisitions', self)
        self.ec_rep = SiriusEnumComboBox(
            self, self._get_pvname('TriggerRep-Sel'))
        self.lb_rep = SiriusLabel(self, self._get_pvname('TriggerRep-Sts'))

        ld_nrpre = QLabel('Pre-Trigger Nr.Samples', self)
        self.sb_nrpre = SiriusSpinbox(self, self._get_pvname('SamplesPre-SP'))
        self.lb_nrpre = SiriusLabel(
            self, self._get_pvname('SamplesPre-RB'), keep_unit=True)
        self.lb_nrpre.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';}')
        self.fr_nrpre = SiriusAlarmFrame(
            self, self._get_pvname('SamplesTotal-Mon'))
        self.fr_nrpre.add_widget(self.lb_nrpre)

        ld_nrpos = QLabel('Post-Trigger Nr.Samples', self)
        self.sb_nrpos = SiriusSpinbox(self, self._get_pvname('SamplesPost-SP'))
        self.lb_nrpos = SiriusLabel(
            self, self._get_pvname('SamplesPost-RB'), keep_unit=True)
        self.lb_nrpos.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';}')
        self.fr_nrpos = SiriusAlarmFrame(
            self, self._get_pvname('SamplesTotal-Mon'))
        self.fr_nrpos.add_widget(self.lb_nrpos)

        ld_trig = QLabel('Trigger Type', self)
        self.ec_trig = SiriusEnumComboBox(
            self, self._get_pvname('Trigger-Sel'))
        self.lb_trig = SiriusLabel(self, self._get_pvname('Trigger-Sts'))

        ld_nrshots = QLabel('Number of Shots', self)
        self.sb_nrshots = SiriusSpinbox(self, self._get_pvname('Shots-SP'))
        self.lb_nrshots = SiriusLabel(
            self, self._get_pvname('Shots-RB'), keep_unit=True)

        ld_uptime = QLabel('Update Interval', self)
        self.sb_uptime = SiriusSpinbox(self, self._get_pvname('UpdateTime-SP'))
        self.lb_uptime = SiriusLabel(
            self, self._get_pvname('UpdateTime-RB'), keep_unit=True)

        self.pb_start = PyDMPushButton(
            self, init_channel=self._get_pvname('TriggerEvent-Cmd'),
            label='Start', pressValue=0)
        self.pb_stop = PyDMPushButton(
            self, init_channel=self._get_pvname('TriggerEvent-Cmd'),
            label='Stop', pressValue=1)
        self.lb_status = SiriusLabel(
            self, self._get_pvname('Status-Mon'), keep_unit=True)
        self.lb_status.setAlignment(Qt.AlignCenter)
        self.lb_status.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self.lb_count = SiriusLabel(
            self, self._get_pvname('Count-Mon'), keep_unit=True)
        self.lb_count.setAlignment(Qt.AlignCenter)
        self.lb_count.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        dlay_cmd = QGridLayout()
        dlay_cmd.setContentsMargins(0, 0, 0, 0)
        dlay_cmd.addWidget(self.pb_start, 0, 0)
        dlay_cmd.addWidget(self.pb_stop, 0, 1)
        dlay_cmd.addWidget(self.lb_status, 1, 0)
        dlay_cmd.addWidget(self.lb_count, 1, 1)

        wid = QGroupBox('Basic Settings', self)
        lay = QGridLayout(wid)
        lay.addWidget(ld_chan, 0, 0)
        lay.addWidget(self.ec_chan, 0, 1)
        lay.addWidget(self.lb_chan, 0, 2)
        lay.addWidget(ld_dtype, 1, 0)
        lay.addWidget(self.ec_dtype, 1, 1)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Preferred, QSzPlcy.Fixed), 2, 0)
        lay.addWidget(ld_rep, 3, 0)
        lay.addWidget(self.ec_rep, 3, 1)
        lay.addWidget(self.lb_rep, 3, 2)
        lay.addWidget(ld_nrpre, 4, 0)
        lay.addWidget(self.sb_nrpre, 4, 1)
        lay.addWidget(self.fr_nrpre, 4, 2)
        lay.addWidget(ld_nrpos, 5, 0)
        lay.addWidget(self.sb_nrpos, 5, 1)
        lay.addWidget(self.fr_nrpos, 5, 2)
        lay.addWidget(ld_trig, 6, 0)
        lay.addWidget(self.ec_trig, 6, 1)
        lay.addWidget(self.lb_trig, 6, 2)
        lay.addWidget(ld_nrshots, 7, 0)
        lay.addWidget(self.sb_nrshots, 7, 1)
        lay.addWidget(self.lb_nrshots, 7, 2)
        lay.addWidget(ld_uptime, 8, 0)
        lay.addWidget(self.sb_uptime, 8, 1)
        lay.addWidget(self.lb_uptime, 8, 2)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Preferred, QSzPlcy.Fixed), 9, 0)
        lay.addLayout(dlay_cmd, 10, 0, 1, 3)
        return wid

    def _triggersWidget(self):
        group = QGroupBox('Triggers Configuration', self)
        bt_phy = QPushButton('Physical Triggers')
        wind_phy = create_window_from_widget(
            PhysicalTriggers, title=self.device+' Physical Triggers')
        connect_window(
            bt_phy, wind_phy, parent=group, prefix=self.prefix,
            device=self.device)

        bt_log = QPushButton('Logical Triggers')
        wind_log = create_window_from_widget(
            LogicalTriggers, title=self.device+' Logical Triggers')
        connect_window(
            bt_log, wind_log, parent=group, prefix=self.prefix,
            device=self.device, trig_tp='_'+self.ACQCORE)

        hbl = QHBoxLayout(group)
        hbl.addStretch()
        hbl.addWidget(bt_phy)
        hbl.addStretch()
        hbl.addWidget(bt_log)
        hbl.addStretch()
        return group

    def _handle_graph_xaxis_link(self, graphref, graphs, link):
        view2link = graphref.graph.plotItem.getViewBox() \
            if link else None
        for graph in graphs:
            graph.graph.setXLink(view2link)

    def _setupUi(self):
        raise NotImplementedError


class FOFBAcqSYSIDWindow(_AcqBaseWindow):
    """FOFB system identification acquisition window."""

    ACQCORE = 'SYSID'

    def _setupUi(self):
        self.title = QLabel(
            '<h2>'+self.device.substitute(propty_name='SYSID') +
            ' Acquisitions < /h2 >', alignment=Qt.AlignCenter)
        self.title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        self.wid_basic = self._basicSettingsWidget()
        self.wid_prbs = self._PRBSSettingsWidget()
        self.wid_trig = self._triggersWidget()
        self.wid_graph = self._graphsWidget()

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.wid_graph, 1, 0, 3, 1)
        lay.addWidget(self.wid_basic, 1, 1)
        lay.addWidget(self.wid_prbs, 2, 1)
        lay.addWidget(self.wid_trig, 3, 1)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 1)
        lay.setRowStretch(0, 3)
        lay.setRowStretch(1, 3)
        lay.setRowStretch(2, 1)
        self.setCentralWidget(wid)

    def _PRBSSettingsWidget(self):
        tabs = QTabWidget()
        tabs.setObjectName(self.sec+'Tab')
        tabs.addTab(self._PRBSGeneralSettingsWidget(), 'General')
        tabs.addTab(self._PRBSFOFBAccSettingsWidget(), 'FOFBAcc Levels')
        tabs.addTab(self._PRBSBPMsSettingsWidget(), 'BPM Levels')

        wid = QGroupBox('PRBS Settings', self)
        lay = QHBoxLayout(wid)
        lay.setContentsMargins(0, 9, 0, 9)
        lay.addWidget(tabs)
        return wid

    def _PRBSGeneralSettingsWidget(self):
        ld_syncenb = QLabel('Sync Enable', self)
        self.sb_syncenb = PyDMStateButton(
            self, self._get_pvname('PRBSSyncEn-Sel'))
        self.led_syncenb = SiriusLedState(
            self, self._get_pvname('PRBSSyncEn-Sts'))

        ld_stepdur = QLabel('Step Duration', self)
        self.sb_stepdur = PyDMLineEdit(
            self, self._get_pvname('PRBSStepDuration-SP'))
        self.lb_stepdur = SiriusLabel(
            self, self._get_pvname('PRBSStepDuration-RB'))

        ld_lfsrlen = QLabel('LFSR Length', self)
        self.sb_lfsrlen = PyDMLineEdit(
            self, self._get_pvname('PRBSLFSRLength-SP'))
        self.lb_lfsrlen = SiriusLabel(
            self, self._get_pvname('PRBSLFSRLength-RB'))

        ld_correnb = QLabel('Enable Corrs.', self)
        self.sb_correnb = PyDMStateButton(
            self, self._get_pvname('PRBSFOFBAccEn-Sel'))
        self.led_correnb = SiriusLedState(
            self, self._get_pvname('PRBSFOFBAccEn-Sts'))

        ld_bpmenbl = QLabel('Enable BPMs', self)
        self.sb_bpmenbl = PyDMStateButton(
            self, self._get_pvname('PRBSBPMPosEn-Sel'))
        self.led_bpmenbl = SiriusLedState(
            self, self._get_pvname('PRBSBPMPosEn-Sts'))

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.addWidget(ld_syncenb, 0, 0)
        lay.addWidget(self.sb_syncenb, 0, 1)
        lay.addWidget(self.led_syncenb, 0, 2, alignment=Qt.AlignLeft)
        lay.addWidget(ld_stepdur, 1, 0)
        lay.addWidget(self.sb_stepdur, 1, 1)
        lay.addWidget(self.lb_stepdur, 1, 2)
        lay.addWidget(ld_lfsrlen, 2, 0)
        lay.addWidget(self.sb_lfsrlen, 2, 1)
        lay.addWidget(self.lb_lfsrlen, 2, 2)
        lay.addWidget(ld_correnb, 3, 0)
        lay.addWidget(self.sb_correnb, 3, 1)
        lay.addWidget(self.led_correnb, 3, 2, alignment=Qt.AlignLeft)
        lay.addWidget(ld_bpmenbl, 4, 0)
        lay.addWidget(self.sb_bpmenbl, 4, 1)
        lay.addWidget(self.led_bpmenbl, 4, 2, alignment=Qt.AlignLeft)
        return wid

    def _PRBSFOFBAccSettingsWidget(self):
        wid = QWidget()
        lay = QGridLayout(wid)

        for ridx, sub in enumerate(['M1', 'M2', 'C2', 'C3']):
            row = ridx + 1

            # row header
            lblr = QLabel(
                '<h4>'+sub+'</h4>', self,
                alignment=Qt.AlignRight | Qt.AlignVCenter)
            lblr.setObjectName('rowhead')
            lay.addWidget(lblr, row, 0)

            for cidx, plan in enumerate(['H', 'V']):
                col = cidx + 1
                if ridx == 0:
                    # column header
                    lblp = QLabel(
                        '<h4>FC'+plan+'</h4>', self, alignment=Qt.AlignCenter)
                    lbl0 = QLabel(
                        '<h4>Level 0</h4>', self, alignment=Qt.AlignCenter)
                    lbl1 = QLabel(
                        '<h4>Level 1</h4>', self, alignment=Qt.AlignCenter)
                    gridhead = QGridLayout()
                    gridhead.setContentsMargins(0, 0, 0, 0)
                    gridhead.addWidget(lblp, 0, 0, 1, 2)
                    gridhead.addWidget(lbl0, 1, 0)
                    gridhead.addWidget(lbl1, 1, 1)
                    lay.addLayout(gridhead, 0, col)

                # levels grid
                gridlvls = QGridLayout()
                gridlvls.setContentsMargins(6, 0, 6, 0)
                gridlvls.setHorizontalSpacing(12)
                gridlvls.setVerticalSpacing(6)
                for lvl in range(2):
                    pvsp = join_name(
                        sec='SI', sub=self.device.sub[:2]+sub,
                        dis='PS', dev='FC'+plan,
                        propty_name=f'SYSIDPRBSFOFBAccLvl{lvl}',
                        propty_suffix='SP')
                    wsp = PyDMLineEdit(self, pvsp)
                    pvrb = pvsp.substitute(propty_suffix='RB')
                    wrb = SiriusLabel(self, pvrb)
                    gridlvls.addWidget(wsp, 0, lvl)
                    gridlvls.addWidget(wrb, 1, lvl)
                lay.addLayout(gridlvls, row, col)

        wid.setStyleSheet(
            'QLineEdit{max-width: 5em;}'
            '#rowhead{max-width:3.5em;}')

        return wid

    def _PRBSBPMsSettingsWidget(self):
        graph = SiriusWaveformPlot()
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 15em; min-width: 25em;}')
        graph.maxRedrawRate = 2
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        graph.plotItem.getAxis('left').setStyle(tickTextOffset=5)

        for plidx, plan in enumerate(['X', 'Y']):
            for lvl in range(2):
                for pvidx, suf in enumerate(['SP', 'RB']):
                    pvn = self._get_pvname(f'PRBSBPMPos{plan}Lvl{lvl}-{suf}')
                    color = self.DEFAULT_COLORS[pvidx + 2*lvl + 4*plidx]
                    opts = dict(
                        y_channel=pvn,
                        name=f'{plan} - Level {lvl} ({suf})',
                        color=color,
                        redraw_mode=2,
                        lineStyle=1,
                        lineWidth=1,
                        symbol=None,
                        symbolSize=None)
                    graph.addChannel(**opts)
        return graph

    def _graphsWidget(self):
        # PRBSData
        gp_prbs = self._create_graph(
            'PRBS', {self._get_pvname('PRBSData'): 'PRBS'})

        # TimeFrameData
        gp_tframe = self._create_graph(
            'TimeFrame', {self._get_pvname('TimeFrameData'): 'TimeFrame'})

        # PosXData
        gp_posx = self._create_graph(
            'Pos X [nm]',
            {self._get_pvname(f'BPM{i}PosXData'): self.CONV_IDX2BPM[i]
             for i in range(8)}, add_scale=1e-9)

        # PosYData
        gp_posy = self._create_graph(
            'Pos Y [nm]',
            {self._get_pvname(f'BPM{i}PosYData'): self.CONV_IDX2BPM[i]
             for i in range(8)}, add_scale=1e-9)

        # FOFBAccData
        gp_fofbacc = self._create_graph(
            'FOFBAcc [A]',
            {c.substitute(propty_name='SYSIDFOFBAccData'):
             c.sub[2:]+'-'+c.dev[-1] for c in self.corrs})

        cb_linkxaxis = QCheckBox('Link X axis', self)
        cb_linkxaxis.stateChanged.connect(_part(
            self._handle_graph_xaxis_link, gp_prbs,
            [gp_tframe, gp_posx, gp_posy, gp_fofbacc]))
        cb_linkxaxis.setChecked(True)

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.addWidget(gp_prbs)
        lay.addWidget(gp_tframe)
        lay.addWidget(gp_posx)
        lay.addWidget(gp_posy)
        lay.addWidget(gp_fofbacc)
        lay.addWidget(cb_linkxaxis, alignment=Qt.AlignLeft)
        return wid


class FOFBAcqLAMPWindow(_AcqBaseWindow):
    """FOFB lamp acquisition window."""

    ACQCORE = 'LAMP'

    def _setupUi(self):
        self.title = QLabel(
            '<h2>'+self.device.substitute(propty_name='LAMP') +
            ' Acquisitions < /h2 >', alignment=Qt.AlignCenter)
        self.title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        self.wid_basic = self._basicSettingsWidget()
        self.wid_trig = self._triggersWidget()
        self.tab_graphs = QTabWidget(self)
        self.tab_graphs.setObjectName(self.sec+'Tab')
        self.wid_graphphy = self._graphsWidget(is_raw=False)
        self.tab_graphs.addTab(self.wid_graphphy, 'Conv. Data')
        self.wid_graphraw = self._graphsWidget(is_raw=True)
        self.tab_graphs.addTab(self.wid_graphraw, 'Raw Data')
        self.tab_graphs.setCurrentIndex(0)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.tab_graphs, 1, 0, 2, 1)
        lay.addWidget(self.wid_basic, 1, 1)
        lay.addWidget(self.wid_trig, 2, 1)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 1)
        lay.setRowStretch(0, 3)
        lay.setRowStretch(1, 1)
        self.setCentralWidget(wid)

    def _graphsWidget(self, is_raw):
        pvname = 'LAMP{}' + ('Raw' if is_raw else '') + 'Data'
        # Current
        gp_curr = self._create_graph(
            'Current' + ('' if is_raw else ' [A]'),
            {c.substitute(propty_name=pvname.format('Current')):
             c.sub[2:]+'-'+c.dev[-1] for c in self.corrs})

        # CurrentRef
        gp_currref = self._create_graph(
            'CurrentRef' + ('' if is_raw else ' [A]'),
            {c.substitute(propty_name=pvname.format('CurrentRef')):
             c.sub[2:]+'-'+c.dev[-1] for c in self.corrs})

        # Voltage
        gp_volt = self._create_graph(
            'Voltage' + ('' if is_raw else ' [V]'),
            {c.substitute(propty_name=pvname.format('Voltage')):
             c.sub[2:]+'-'+c.dev[-1] for c in self.corrs})

        cb_linkxaxis = QCheckBox('Link X axis', self)
        cb_linkxaxis.stateChanged.connect(_part(
            self._handle_graph_xaxis_link, gp_curr, [gp_volt, ]))
        cb_linkxaxis.setChecked(True)

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.addWidget(gp_curr)
        lay.addWidget(gp_currref)
        lay.addWidget(gp_volt)
        lay.addWidget(cb_linkxaxis, alignment=Qt.AlignLeft)
        return wid
