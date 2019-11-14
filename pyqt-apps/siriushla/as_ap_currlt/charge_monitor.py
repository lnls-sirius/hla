from datetime import datetime as _datetime, timedelta as _timedelta
import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, \
    QVBoxLayout, QGridLayout, QDoubleSpinBox, QApplication
from pydm.widgets import PyDMTimePlot, PyDMLabel
from siriuspy.envars import vaca_prefix
from siriuspy.clientarch import ClientArchiver
from siriushla.widgets import SiriusMainWindow, SiriusConnectionSignal


class BOMonitor(SiriusMainWindow):
    """BO charges monitor."""

    def __init__(self, parent=None, prefix=vaca_prefix):
        super().__init__(parent)
        self.setObjectName('BOApp')
        self.setWindowTitle('BO Charge Monitor')

        self._prefix = prefix
        self._ioc_prefix = self._prefix + 'BO-Glob:AP-CurrInfo'
        self._energies = ['150MeV', '1GeV', '2GeV', '3GeV']
        self._latest_offsets = {e: 0.0 for e in self._energies}  # in nC
        self._latest_charges = {e: 0.0 for e in self._energies}  # in nC

        self._app = QApplication.instance()
        font = self._app.font()
        font.setPointSize(20)
        self._app.setFont(font)
        self._setupUi()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.setFocusPolicy(Qt.StrongFocus)

        label = QLabel('<h4>Booster Charge</h4>',
                       self, alignment=Qt.AlignCenter)

        # timeplot
        self.timeplot = PyDMTimePlot(parent=self, background='w')
        timespan = 3600*6
        colors = ['blue', 'red', 'green', 'magenta']
        self.timeplot.timeSpan = timespan  # [s]
        self.timeplot.bufferSize = 2*timespan  # [2 samples/s]
        self.timeplot.autoRangeY = True
        self.timeplot.showXGrid = True
        self.timeplot.showYGrid = True
        self.timeplot.setLabel('left', text='Charge', units='nC')
        self.timeplot.setObjectName('timeplot')
        self.timeplot.setStyleSheet(
            '#timeplot{min-width:28em; min-height: 18em;}')

        self._channels = dict()
        self._curves = dict()
        self._cb_show = dict()
        self._pvs_labels = dict()
        self._cb_offsets = dict()
        glay_aux = QGridLayout()
        glay_aux.setHorizontalSpacing(20)
        glay_aux.setVerticalSpacing(10)
        glay_aux.addWidget(
            QLabel('Show curves: ', self), 0, 0, alignment=Qt.AlignCenter)
        glay_aux.addWidget(
            QLabel('Offset [nC]: ', self), 2, 0, alignment=Qt.AlignCenter)
        for i, e in enumerate(self._energies):
            pvname = self._ioc_prefix+':Charge'+e+'-Mon'
            self._channels[e] = SiriusConnectionSignal(address=pvname)
            self._channels[e].new_value_signal[float].connect(
                self._update_charges)

            self.timeplot.addYChannel('Charge'+e, color=colors[i], lineWidth=2)

            data = self._get_value_from_arch(pvname)
            buff = np.zeros((2, 2*timespan), order='f', dtype=float)
            buff[0, (2*timespan-len(data[0])):] = data[0]
            buff[1, (2*timespan-len(data[0])):] = data[1]
            nrpts = len(data[0])
            curve = self.timeplot.curveAtIndex(-1)
            curve.data_buffer = buff
            curve.points_accumulated = nrpts
            curve._min_y_value = min(data[1])
            curve._max_y_value = max(data[1])
            curve.latest_value = data[1][-1]
            self._curves[e] = curve

            cb = QCheckBox(e)
            cb.setChecked(True)
            cb.setStyleSheet('color:'+colors[i]+';')
            cb.stateChanged.connect(curve.setVisible)
            self._cb_show[e] = cb

            lb = QLabel('', self, alignment=Qt.AlignCenter)
            self._pvs_labels[e] = lb

            sb = QDoubleSpinBox(self)
            sb.energy = e
            sb.setMinimum(0)
            sb.setMaximum(1e6)
            sb.setDecimals(4)
            sb.setStyleSheet('max-width: 5em;')
            sb.setValue(self._latest_offsets[e])
            sb.editingFinished.connect(self._update_offset)
            self._cb_offsets[e] = sb

            glay_aux.addWidget(cb, 0, i+1, alignment=Qt.AlignCenter)
            glay_aux.addWidget(lb, 1, i+1, alignment=Qt.AlignCenter)
            glay_aux.addWidget(sb, 2, i+1, alignment=Qt.AlignCenter)

        lay = QVBoxLayout(cw)
        lay.addWidget(label)
        lay.addWidget(self.timeplot)
        lay.addLayout(glay_aux)

    def _get_value_from_arch(self, pvname):
        carch = ClientArchiver()
        t1 = _datetime.now()
        t0 = t1 - _timedelta(hours=6)
        t0_str = t0.isoformat() + '-03:00'
        t1_str = t1.isoformat() + '-03:00'
        timestamp, value, _, _ = carch.getData(pvname, t0_str, t1_str)
        # ignore first sample
        timestamp[0] = t0.timestamp()
        value[0] = value[1]
        return timestamp, value

    def _update_charges(self, value):
        if self.sender() is None:
            return
        address = self.sender().address
        energy = address.strip(self._ioc_prefix).strip('Charge').strip('-Mon')
        self._latest_charges[energy] = value
        # update widgets
        curve = self._curves[energy]
        latest_offset = self._latest_offsets[energy]
        curve.receiveNewValue(value - latest_offset)
        curve.redrawCurve()
        lb = self._pvs_labels[energy]
        lb.setText('{:.4f} nC'.format(value - latest_offset))

    def _update_offset(self):
        sender = self.sender()
        energy = sender.energy
        value = sender.value()
        if value == self._latest_offsets[energy]:
            return
        self._curves[energy].blockSignals(True)
        self._curves[energy].data_buffer[1] += \
            self._latest_offsets[energy]
        self._curves[energy].data_buffer[1] -= value
        self._latest_offsets[energy] = value
        self._curves[energy].redrawCurve()
        self._curves[energy].blockSignals(False)
        lb = self._pvs_labels[energy]
        charge = self._latest_charges[energy]
        lb.setText('{:.4f} nC'.format(charge - value))
