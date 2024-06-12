"""System identification module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QLabel, \
    QGroupBox, QCheckBox, QSizePolicy as QSzPlcy, \
    QSpacerItem, QHBoxLayout, QPushButton

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName

from ...util import connect_window, get_appropriate_color
from ...widgets import SiriusMainWindow, SiriusLabel, \
    SiriusEnumComboBox, SiriusSpinbox, SiriusAlarmFrame
from ...widgets.windows import create_window_from_widget
from ...as_di_bpms.base import GraphWave
from . import LogicalTriggers, PhysicalTriggers


class AcqBaseWindow(SiriusMainWindow):
    """Acquisition base window"""

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
        self.sec = 'SI' if self.device.sec == 'IA' else self.device.sec
        self.app_color = get_appropriate_color(self.sec)
        self.setObjectName(self.sec+'App')
        self.setFocusPolicy(Qt.StrongFocus)

    def _get_pvname(self, propty):
        propty = self.ACQCORE + propty
        return self.devpref.substitute(propty=propty)

    def _create_graph(self, title, channels2names, add_scale=None):
        graph = GraphWave()
        graph.graph.setTitle(title)
        graph.graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False, tickTextWidth=70)
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

        ld_rep = QLabel('Repeat Acquisitions', self)
        self.ec_rep = SiriusEnumComboBox(
            self, self._get_pvname('TriggerRep-Sel'))
        self.lb_rep = SiriusLabel(self, self._get_pvname('TriggerRep-Sts'))

        ld_nrpre = QLabel('Pre-Trigger Nr.Samples', self)
        self.sb_nrpre = SiriusSpinbox(self, self._get_pvname('SamplesPre-SP'))
        self.lb_nrpre = SiriusLabel(
            self, self._get_pvname('SamplesPre-RB'), keep_unit=True,
            alignment=Qt.AlignTop)
        self.lb_nrpre.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';}')

        ld_nrpos = QLabel('Post-Trigger Nr.Samples', self)
        self.sb_nrpos = SiriusSpinbox(self, self._get_pvname('SamplesPost-SP'))
        self.lb_nrpos = SiriusLabel(
            self, self._get_pvname('SamplesPost-RB'), keep_unit=True,
            alignment=Qt.AlignBottom)
        self.lb_nrpos.setStyleSheet(
            'QLabel{background-color: '+self.app_color+';}')

        self.fr_nrtot = SiriusAlarmFrame(
            self, self._get_pvname('SamplesTotal-Mon'),
            orientation='V')
        self.fr_nrtot.layout().setSpacing(0)
        self.fr_nrtot.add_widget(self.lb_nrpre)
        self.fr_nrtot.add_widget(self.lb_nrpos)
        self.fr_nrtot.stateColors = [
            QColor(self.app_color),
            SiriusAlarmFrame.DarkYellow, SiriusAlarmFrame.Red,
            SiriusAlarmFrame.Magenta, SiriusAlarmFrame.LightGray]

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
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Preferred, QSzPlcy.Fixed), 2, 0)
        lay.addWidget(ld_rep, 3, 0)
        lay.addWidget(self.ec_rep, 3, 1)
        lay.addWidget(self.lb_rep, 3, 2)
        lay.addWidget(ld_nrpre, 4, 0)
        lay.addWidget(self.sb_nrpre, 4, 1)
        lay.addWidget(ld_nrpos, 5, 0)
        lay.addWidget(self.sb_nrpos, 5, 1)
        lay.addWidget(self.fr_nrtot, 4, 2, 2, 1)
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
