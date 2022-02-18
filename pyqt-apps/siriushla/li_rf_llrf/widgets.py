"""LILLRF Custom Widgets."""

import numpy as np

from qtpy.QtCore import QSize
from qtpy.QtWidgets import QPushButton

import qtawesome as _qta

from ..widgets import SiriusConnectionSignal as _ConnSignal


class DeltaIQPhaseCorrButton(QPushButton):

    def __init__(self, parent=None, device=None, prefix='', delta=0,
                 show_label=True):
        label = str(abs(delta))+'°' if show_label else ''
        icon_name = 'mdi.plus' if np.sign(delta) == 1 else 'mdi.minus'
        icon = _qta.icon(icon_name)
        super().__init__(icon, label, parent)
        self.setIconSize(QSize(20, 20))

        self.prefix = prefix
        self.dev = device
        self.devpref = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname
        self.delta = delta

        self.setToolTip(f'Do {delta:.1f}° delta')
        self.setEnabled(False)
        self.ch_loop_enable = _ConnSignal(
            self.devpref+':SET_FB_MODE')
        self.ch_loop_enable.new_value_signal[int].connect(
            self._handle_enable_state)
        self.ch_loop_enable.connection_state_signal.connect(
            self._handle_enable_state)

        self.ch_iqcorr_phase_ch1 = _ConnSignal(
            self.devpref+':SET_CH1_PHASE_CORR')

        self.clicked.connect(self._do_delta)

    def _do_delta(self):
        if not self.isEnabled():
            return
        if not self.ch_iqcorr_phase_ch1.connected:
            return
        curr_value = self.ch_iqcorr_phase_ch1.value
        new_value = curr_value + self.delta
        new_value = (new_value + 180) % 360 - 180
        self.ch_iqcorr_phase_ch1.send_value_signal[float].emit(new_value)

    def _handle_enable_state(self):
        state = (
            self.ch_loop_enable.connected and  # is connected
            self.ch_loop_enable.value == 0)    # is disabled
        self.setEnabled(state)
