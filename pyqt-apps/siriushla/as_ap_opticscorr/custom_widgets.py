from pydm.widgets import PyDMLineEdit

from siriuspy.opticscorr.csdev import Const as _Const
from siriushla.widgets import SiriusLedAlert
from siriushla.widgets.dialog import StatusDetailDialog
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class ConfigLineEdit(PyDMLineEdit):

    def mouseReleaseEvent(self, _):
        """Reimplement mouse release event."""
        if 'SI' in self.channel and 'Tune' in self.channel:
            config_type = 'si_tunecorr_params'
        elif 'BO' in self.channel and 'Tune' in self.channel:
            config_type = 'bo_tunecorr_params'
        elif 'SI' in self.channel and 'Chrom' in self.channel:
            config_type = 'si_chromcorr_params'
        elif 'BO' in self.channel and 'Chrom' in self.channel:
            config_type = 'bo_chromcorr_params'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)


class StatusLed(SiriusLedAlert):

    def __init__(self, parent=None, init_channel='', labels=list()):
        super().__init__(parent, init_channel=init_channel)
        self.parent = parent
        self.labels = labels

    def mouseDoubleClickEvent(self, event):
        msg = StatusDetailDialog(
            parent=self.parent, pvname=self.channel,
            labels=_Const.STATUS_LABELS)
        msg.exec_()
        super().mouseDoubleClickEvent(event)
