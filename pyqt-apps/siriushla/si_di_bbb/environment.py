"""BbB Environment Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout
from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from .custom_widgets import TimeGraph
from .util import set_bbb_color


class BbBEnvironmMonWidget(QWidget):
    """BbB Environment Monitor Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        graph_fpgatemp = TimeGraph(background='w')
        graph_fpgatemp.timeSpan = 300
        graph_fpgatemp.addYChannel(
            self.dev_pref+':TEMP_FPGA', color=QColor('blue'))
        graph_fpgatemp.setPlotTitle('FPGA temperature')
        graph_fpgatemp.setLabel('left', 'Temp. [°C]', color='gray')

        graph_pcbtemp = TimeGraph(background='w')
        graph_pcbtemp.timeSpan = 300
        graph_pcbtemp.addYChannel(
            self.dev_pref+':TEMP_AMB', color=QColor('blue'))
        graph_pcbtemp.setPlotTitle('PCB temperature')
        graph_pcbtemp.setLabel('left', 'Temp. [°C]', color='gray')

        graph_exttemp = TimeGraph(background='w')
        graph_exttemp.timeSpan = 300
        graph_exttemp.setPlotTitle('Ext.1 (blue) and Ext.2(red)')
        graph_exttemp.addYChannel(
            self.dev_pref+':TEMP_EXT1', color=QColor('blue'))
        graph_exttemp.addYChannel(
            self.dev_pref+':TEMP_EXT2', color=QColor('red'))
        graph_exttemp.setLabel('left', 'Temp. [°C]', color='gray')

        graph_bulkvolt = TimeGraph(background='w')
        graph_bulkvolt.timeSpan = 300
        graph_bulkvolt.addYChannel(
            self.dev_pref+':VBULK', color=QColor('red'))
        graph_bulkvolt.setPlotTitle('Bulk Supply voltage')
        graph_bulkvolt.setLabel('left', 'Voltage [V]', color='gray')

        graph_digivolt = TimeGraph(background='w')
        graph_digivolt.timeSpan = 300
        graph_digivolt.addYChannel(
            self.dev_pref+':VCC', color=QColor('red'))
        graph_digivolt.setPlotTitle('Digital 3.3V')
        graph_digivolt.setLabel('left', 'Voltage [V]', color='gray')

        graph_fpgavolt = TimeGraph(background='w')
        graph_fpgavolt.timeSpan = 300
        graph_fpgavolt.addYChannel(
            self.dev_pref+':VINT', color=QColor('red'))
        graph_fpgavolt.setPlotTitle('FPGA core supply voltage')
        graph_fpgavolt.setLabel('left', 'Voltage [V]', color='gray')

        lay_graphs = QGridLayout()
        lay_graphs.setContentsMargins(0, 0, 0, 0)
        lay_graphs.addWidget(graph_exttemp, 0, 0, 1, 2)
        lay_graphs.addWidget(graph_fpgatemp, 0, 2, 1, 2)
        lay_graphs.addWidget(graph_pcbtemp, 0, 4, 1, 2)
        lay_graphs.addWidget(graph_bulkvolt, 1, 0, 1, 2)
        lay_graphs.addWidget(graph_digivolt, 1, 2, 1, 2)
        lay_graphs.addWidget(graph_fpgavolt, 1, 4, 1, 2)

        ld_fpgatemp = QLabel(
            '<h4>FPGA temp</h4>', self, alignment=Qt.AlignRight)
        lb_fpgatemp = PyDMLabel(self, self.dev_pref+':TEMP_FPGA')
        lb_fpgatemp.showUnits = True

        ld_pcbtemp = QLabel(
            '<h4>PCB temp</h4>', self, alignment=Qt.AlignRight)
        lb_pcbtemp = PyDMLabel(self, self.dev_pref+':TEMP_AMB')
        lb_pcbtemp.showUnits = True

        ld_exttemp1 = QLabel(
            '<h4>External temp 1</h4>', self, alignment=Qt.AlignRight)
        lb_exttemp1 = PyDMLabel(self, self.dev_pref+':TEMP_EXT1')
        lb_exttemp1.showUnits = True

        ld_exttemp2 = QLabel(
            '<h4>External temp 2</h4>', self, alignment=Qt.AlignRight)
        lb_exttemp2 = PyDMLabel(self, self.dev_pref+':TEMP_EXT2')
        lb_exttemp2.showUnits = True

        ld_bulkvolt = QLabel(
            '<h4>Bulk Supply</h4>', self, alignment=Qt.AlignRight)
        lb_bulkvolt = PyDMLabel(self, self.dev_pref+':VBULK')
        lb_bulkvolt.showUnits = True

        ld_digivolt = QLabel(
            '<h4>Digital 3.3V</h4>', self, alignment=Qt.AlignRight)
        lb_digivolt = PyDMLabel(self, self.dev_pref+':VCC')
        lb_digivolt.showUnits = True

        ld_fpgavolt = QLabel(
            '<h4>FPGA core supply</h4>', self, alignment=Qt.AlignRight)
        lb_fpgavolt = PyDMLabel(self, self.dev_pref+':VINT')
        lb_fpgavolt.showUnits = True

        ld_anal3p3volt = QLabel(
            '<h4>Analog 3.3V</h4>', self, alignment=Qt.AlignRight)
        lb_anal3p3volt = PyDMLabel(self, self.dev_pref+':VMON33')
        lb_anal3p3volt.showUnits = True

        ld_cputemp = QLabel(
            '<h4>CPU temp</h4>', self, alignment=Qt.AlignRight)
        lb_cputemp = PyDMLabel(self, self.dev_pref+':HWMON_CPU_TEMP')
        lb_cputemp.showUnits = True

        ld_cpufan = QLabel(
            '<h4>CPU fan</h4>', self, alignment=Qt.AlignRight)
        lb_cpufan = PyDMLabel(self, self.dev_pref+':HWMON_CPU_FAN')
        lb_cpufan.showUnits = True

        ld_chassisfan = QLabel(
            '<h4>Chassis fan</h4>', self, alignment=Qt.AlignRight)
        lb_chassisfan = PyDMLabel(self, self.dev_pref+':HWMON_CHASSIS_FAN')
        lb_chassisfan.showUnits = True

        ld_anal5volt = QLabel(
            '<h4>Analog 5V</h4>', self, alignment=Qt.AlignRight)
        lb_anal5volt = PyDMLabel(self, self.dev_pref+':VMON5')
        lb_anal5volt.showUnits = True

        lay_labels = QGridLayout()
        lay_labels.setContentsMargins(0, 0, 0, 0)
        lay_labels.addWidget(ld_fpgatemp, 0, 0)
        lay_labels.addWidget(lb_fpgatemp, 0, 1)
        lay_labels.addWidget(ld_pcbtemp, 0, 2)
        lay_labels.addWidget(lb_pcbtemp, 0, 3)
        lay_labels.addWidget(ld_exttemp1, 0, 4)
        lay_labels.addWidget(lb_exttemp1, 0, 5)
        lay_labels.addWidget(ld_exttemp2, 0, 6)
        lay_labels.addWidget(lb_exttemp2, 0, 7)
        lay_labels.addWidget(ld_bulkvolt, 1, 0)
        lay_labels.addWidget(lb_bulkvolt, 1, 1)
        lay_labels.addWidget(ld_digivolt, 1, 2)
        lay_labels.addWidget(lb_digivolt, 1, 3)
        lay_labels.addWidget(ld_fpgavolt, 1, 4)
        lay_labels.addWidget(lb_fpgavolt, 1, 5)
        lay_labels.addWidget(ld_anal3p3volt, 1, 6)
        lay_labels.addWidget(lb_anal3p3volt, 1, 7)
        lay_labels.addWidget(ld_cputemp, 2, 0)
        lay_labels.addWidget(lb_cputemp, 2, 1)
        lay_labels.addWidget(ld_cpufan, 2, 2)
        lay_labels.addWidget(lb_cpufan, 2, 3)
        lay_labels.addWidget(ld_chassisfan, 2, 4)
        lay_labels.addWidget(lb_chassisfan, 2, 5)
        lay_labels.addWidget(ld_anal5volt, 2, 6)
        lay_labels.addWidget(lb_anal5volt, 2, 7)

        lay = QGridLayout(self)
        lay.addLayout(lay_graphs, 0, 0)
        lay.addLayout(lay_labels, 1, 0)
