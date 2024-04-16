"""Custom widgets."""

from pydm.widgets import PyDMLineEdit

from ..widgets import SiriusDialog
from ..as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class ConfigLineEdit(PyDMLineEdit):
    """Configuration line edit."""

    def mouseReleaseEvent(self, _):
        """Reimplement mouseReleaseEvent."""
        config_type = 'si_idff'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)


class ConfigFFView(SiriusDialog):
    pass
