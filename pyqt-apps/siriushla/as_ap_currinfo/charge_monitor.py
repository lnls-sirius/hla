"""Charge Monitor."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, \
    QVBoxLayout, QGridLayout, QApplication

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientarch.time import Time
from siriushla.widgets import SiriusMainWindow, SiriusConnectionSignal, \
    SiriusTimePlot, QDoubleSpinBoxPlus


class BOMonitor(SiriusMainWindow):
    """BO charges monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        super().__init__(parent)
        self.setObjectName('BOApp')
        self.setWindowTitle('BO Charge Monitor')

        self._prefix = prefix
        self._ioc_prefix = _PVName('BO-Glob:AP-CurrInfo').substitute(
            prefix=prefix)
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
        self.timeplot = SiriusTimePlot(parent=self, background='w')
        timespan = 60*60*6
        colors = ['blue', 'red', 'green', 'magenta']
        self.timeplot.timeSpan = timespan  # [s]
        self.timeplot.bufferSize = 2*timespan  # [2 samples/s]
        self.timeplot.addAxis(
            plot_data_item=None, name='left', orientation='left')
        self.timeplot.autoRangeY = True
        self.timeplot.showXGrid = True
        self.timeplot.showYGrid = True
        self.timeplot.setLabel('left', text='Charge', units='C', color='gray')
        self.timeplot.setObjectName('timeplot')
        self.timeplot.setStyleSheet(
            '#timeplot{min-width:28em; min-height: 18em;}')
        t_end = Time.now()
        t_init = t_end - timespan

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
            pvname = self._ioc_prefix.substitute(propty='Charge'+e+'-Mon')
            self._channels[e] = SiriusConnectionSignal(address=pvname)
            self._channels[e].new_value_signal[float].connect(
                self._update_charges)

            self.timeplot.addYChannel('Charge'+e, color=colors[i], lineWidth=2)
            curve = self.timeplot.curveAtIndex(-1)
            self._curves[e] = curve
            self.timeplot.fill_curve_with_archdata(
                self._curves[e], pvname, factor=1e9,
                t_init=t_init.get_iso8601(), t_end=t_end.get_iso8601())

            cb = QCheckBox(e)
            cb.setChecked(True)
            cb.setStyleSheet('color:'+colors[i]+';')
            cb.stateChanged.connect(curve.setVisible)
            self._cb_show[e] = cb

            lb = QLabel('', self, alignment=Qt.AlignCenter)
            self._pvs_labels[e] = lb

            sb = QDoubleSpinBoxPlus(self)
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

        self.pb_offset = QPushButton('Update offset', self)
        self.pb_offset.clicked.connect(self._set_current_values_2_offset)
        self.pb_offset.setToolTip('Set offsets to current charge values.')
        glay_aux.addWidget(self.pb_offset, 1, 0)

        lay = QVBoxLayout(cw)
        lay.addWidget(label)
        lay.addWidget(self.timeplot)
        lay.addLayout(glay_aux)

    def _update_charges(self, value):
        if self.sender() is None:
            return
        address = self.sender().address
        energy = address.strip(self._ioc_prefix).strip('Charge').strip('-Mon')
        self._latest_charges[energy] = value
        # update widgets
        curve = self._curves[energy]
        latest_offset = self._latest_offsets[energy]
        new_value = value - latest_offset
        curve.receiveNewValue(1e-9*new_value)
        curve.redrawCurve()
        lb = self._pvs_labels[energy]
        lb.setText('{:.4e} nC'.format(new_value))

    def _update_offset(self):
        sender = self.sender()
        energy = sender.energy
        value = sender.value()
        if value == self._latest_offsets[energy]:
            return
        self._update_curve_and_label(energy, value)

    def _set_current_values_2_offset(self):
        for e in self._energies:
            charge = self._latest_charges[e]
            if charge == self._latest_offsets[e]:
                continue
            sb = self._cb_offsets[e]
            sb.setValue(charge)
            self._update_curve_and_label(e, charge)

    def _update_curve_and_label(self, energy, value):
        self._curves[energy].blockSignals(True)
        self._curves[energy].data_buffer[1] += \
            self._latest_offsets[energy]*1e-9
        self._curves[energy].data_buffer[1] -= value*1e-9
        self._latest_offsets[energy] = value
        self._curves[energy].redrawCurve()
        self._curves[energy].blockSignals(False)
        lb = self._pvs_labels[energy]
        charge = self._latest_charges[energy]
        lb.setText('{:.4f} nC'.format(charge - value))
