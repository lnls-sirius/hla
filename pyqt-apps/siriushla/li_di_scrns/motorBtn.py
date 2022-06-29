from ..widgets import PyDMStateButton
import numpy as np

class MotorBtn(PyDMStateButton):
    """Rederivation to change send values."""

    def value_changed(self, new_val):
        """Value changed rederivation."""
        if isinstance(new_val, np.ndarray):
            return
        super(PyDMStateButton, self).value_changed(new_val)
        self.value = new_val
        self._bit_val = 1 if new_val == 'IL1' else 0
        self.update()

    def send_value(self):
        """Send value rederivation."""
        if not self._connected:
            return None
        if not self.confirm_dialog():
            return None
        if not self.validate_password():
            return None
        checked = not self._bit_val
        val = 'IL1' if checked else 'IH1'
        self.send_value_signal[self.channeltype].emit(self.channeltype(val))
