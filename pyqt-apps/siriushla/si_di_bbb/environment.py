"""BbB Environment Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout

from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from .custom_widgets import TimeGraph


class BbBEnvironmMonWidget(QWidget):
    """BbB Environment Monitor Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._graph_fpgatemp = TimeGraph(background='w')
        self._graph_fpgatemp.timeSpan = 300
        self._graph_fpgatemp.addYChannel(
            self.dev_pref+':TEMP_FPGA', color=QColor('blue'))
        self._graph_fpgatemp.setPlotTitle('FPGA temperature')

        self._graph_pcbtemp = TimeGraph(background='w')
        self._graph_pcbtemp.timeSpan = 300
        self._graph_pcbtemp.addYChannel(
            self.dev_pref+':TEMP_AMB', color=QColor('blue'))
        self._graph_pcbtemp.setPlotTitle('PCB temperature')

        self._graph_exttemp = TimeGraph(background='w')
        self._graph_exttemp.timeSpan = 300
        self._graph_exttemp.setPlotTitle('Ext.1 (blue) and Ext.2(red)')
        self._graph_exttemp.addYChannel(
            self.dev_pref+':TEMP_EXT1', color=QColor('blue'))
        self._graph_exttemp.addYChannel(
            self.dev_pref+':TEMP_EXT2', color=QColor('red'))

        self._graph_bulkvolt = TimeGraph(background='w')
        self._graph_bulkvolt.timeSpan = 300
        self._graph_bulkvolt.addYChannel(
            self.dev_pref+':VBULK', color=QColor('red'))
        self._graph_bulkvolt.setPlotTitle('Bulk Supply voltage')

        self._graph_digivolt = TimeGraph(background='w')
        self._graph_digivolt.timeSpan = 300
        self._graph_digivolt.addYChannel(
            self.dev_pref+':VCC', color=QColor('red'))
        self._graph_digivolt.setPlotTitle('Digital 3.3V')

        self._graph_fpgavolt = TimeGraph(background='w')
        self._graph_fpgavolt.timeSpan = 300
        self._graph_fpgavolt.addYChannel(
            self.dev_pref+':VINT', color=QColor('red'))
        self._graph_fpgavolt.setPlotTitle('FPGA core supply voltage')

        lay_graphs = QGridLayout()
        lay_graphs.setContentsMargins(0, 0, 0, 0)
        lay_graphs.addWidget(self._graph_exttemp, 0, 0, 1, 2)
        lay_graphs.addWidget(self._graph_fpgatemp, 0, 2, 1, 2)
        lay_graphs.addWidget(self._graph_pcbtemp, 0, 4, 1, 2)
        lay_graphs.addWidget(self._graph_bulkvolt, 1, 0, 1, 2)
        lay_graphs.addWidget(self._graph_digivolt, 1, 2, 1, 2)
        lay_graphs.addWidget(self._graph_fpgavolt, 1, 4, 1, 2)

        self._ld_fpgatemp = QLabel(
            '<h4>FPGA temp</h4>', self, alignment=Qt.AlignRight)
        self._lb_fpgatemp = PyDMLabel(self, self.dev_pref+':TEMP_FPGA')
        self._lb_fpgatemp.showUnits = True

        self._ld_pcbtemp = QLabel(
            '<h4>PCB temp</h4>', self, alignment=Qt.AlignRight)
        self._lb_pcbtemp = PyDMLabel(self, self.dev_pref+':TEMP_AMB')
        self._lb_pcbtemp.showUnits = True

        self._ld_exttemp1 = QLabel(
            '<h4>External temp 1</h4>', self, alignment=Qt.AlignRight)
        self._lb_exttemp1 = PyDMLabel(self, self.dev_pref+':TEMP_EXT1')
        self._lb_exttemp1.showUnits = True

        self._ld_exttemp2 = QLabel(
            '<h4>External temp 2</h4>', self, alignment=Qt.AlignRight)
        self._lb_exttemp2 = PyDMLabel(self, self.dev_pref+':TEMP_EXT2')
        self._lb_exttemp2.showUnits = True

        self._ld_bulkvolt = QLabel(
            '<h4>Bulk Supply</h4>', self, alignment=Qt.AlignRight)
        self._lb_bulkvolt = PyDMLabel(self, self.dev_pref+':VBULK')
        self._lb_bulkvolt.showUnits = True

        self._ld_digivolt = QLabel(
            '<h4>Digital 3.3V</h4>', self, alignment=Qt.AlignRight)
        self._lb_digivolt = PyDMLabel(self, self.dev_pref+':VCC')
        self._lb_digivolt.showUnits = True

        self._ld_fpgavolt = QLabel(
            '<h4>FPGA core supply</h4>', self, alignment=Qt.AlignRight)
        self._lb_fpgavolt = PyDMLabel(self, self.dev_pref+':VINT')
        self._lb_fpgavolt.showUnits = True

        self._ld_anal3p3volt = QLabel(
            '<h4>Analog 3.3V</h4>', self, alignment=Qt.AlignRight)
        self._lb_anal3p3volt = PyDMLabel(self, self.dev_pref+':VMON33')
        self._lb_anal3p3volt.showUnits = True

        self._ld_cputemp = QLabel(
            '<h4>CPU temp</h4>', self, alignment=Qt.AlignRight)
        self._lb_cputemp = PyDMLabel(self, self.dev_pref+':HWMON_CPU_TEMP')
        self._lb_cputemp.showUnits = True

        self._ld_cpufan = QLabel(
            '<h4>CPU fan</h4>', self, alignment=Qt.AlignRight)
        self._lb_cpufan = PyDMLabel(self, self.dev_pref+':HWMON_CPU_FAN')
        self._lb_cpufan.showUnits = True

        self._ld_chassisfan = QLabel(
            '<h4>Chassis fan</h4>', self, alignment=Qt.AlignRight)
        self._lb_chassisfan = PyDMLabel(

            self, self.dev_pref+':HWMON_CHASSIS_FAN')
        self._lb_chassisfan.showUnits = True

        self._ld_anal5volt = QLabel(
            '<h4>Analog 5V</h4>', self, alignment=Qt.AlignRight)
        self._lb_anal5volt = PyDMLabel(self, self.dev_pref+':VMON5')
        self._lb_anal5volt.showUnits = True

        lay_labels = QGridLayout()
        lay_labels.setContentsMargins(0, 0, 0, 0)
        lay_labels.addWidget(self._ld_fpgatemp, 0, 0)
        lay_labels.addWidget(self._lb_fpgatemp, 0, 1)
        lay_labels.addWidget(self._ld_pcbtemp, 0, 2)
        lay_labels.addWidget(self._lb_pcbtemp, 0, 3)
        lay_labels.addWidget(self._ld_exttemp1, 0, 4)
        lay_labels.addWidget(self._lb_exttemp1, 0, 5)
        lay_labels.addWidget(self._ld_exttemp2, 0, 6)
        lay_labels.addWidget(self._lb_exttemp2, 0, 7)
        lay_labels.addWidget(self._ld_bulkvolt, 1, 0)
        lay_labels.addWidget(self._lb_bulkvolt, 1, 1)
        lay_labels.addWidget(self._ld_digivolt, 1, 2)
        lay_labels.addWidget(self._lb_digivolt, 1, 3)
        lay_labels.addWidget(self._ld_fpgavolt, 1, 4)
        lay_labels.addWidget(self._lb_fpgavolt, 1, 5)
        lay_labels.addWidget(self._ld_anal3p3volt, 1, 6)
        lay_labels.addWidget(self._lb_anal3p3volt, 1, 7)
        lay_labels.addWidget(self._ld_cputemp, 2, 0)
        lay_labels.addWidget(self._lb_cputemp, 2, 1)
        lay_labels.addWidget(self._ld_cpufan, 2, 2)
        lay_labels.addWidget(self._lb_cpufan, 2, 3)
        lay_labels.addWidget(self._ld_chassisfan, 2, 4)
        lay_labels.addWidget(self._lb_chassisfan, 2, 5)
        lay_labels.addWidget(self._ld_anal5volt, 2, 6)
        lay_labels.addWidget(self._lb_anal5volt, 2, 7)

        lay = QGridLayout(self)
        lay.addLayout(lay_graphs, 0, 0)
        lay.addLayout(lay_labels, 1, 0)


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBEnvironmMonWidget(
        prefix=_vaca_prefix, device='SI-Glob:DI-BbBProc-H')
    w.show()
    sys.exit(app.exec_())
