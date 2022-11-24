"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QFormLayout, \
    QHBoxLayout
from pydm.widgets import PyDMPushButton
import qtawesome as qta

from siriushla.widgets import SiriusLedAlert
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class StatusWidget(BaseWidget):

    def __init__(self, parent, device, prefix='', acc='SI', is_orb=False):
        super().__init__(parent, device, prefix=prefix, acc=acc)
        self.is_orb = is_orb
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)

        tip = 'Configure ' + ('Acquisition' if self.is_orb else 'Correctors')
        pv = 'TrigAcqConfig-Cmd' if self.is_orb else 'CorrConfig-Cmd'
        conf = PyDMPushButton(
            self, init_channel=self.devpref.substitute(propty=pv),
            pressValue=1)
        conf.setToolTip(tip)
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')
        vbl.addWidget(conf)

        pv = 'Orb' if self.is_orb else 'Corr'
        pdm_led = SiriusLedAlert(
            self, self.devpref.substitute(propty=pv+'Status-Mon'))

        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(pdm_led)
        hbl.addWidget(QLabel('Global Status', self))
        hbl.addStretch()
        hbl.addWidget(conf)
        vbl.addLayout(hbl)

        grpbx = self.creategroupbox()
        vbl.addWidget(grpbx)

    def creategroupbox(self):
        wid = QGroupBox('Detailed Status', self)
        fbl = QFormLayout(wid)
        if self.is_orb:
            items = self._csorb.StsLblsOrb._fields
            name = 'Orb'
        else:
            items = self._csorb.StsLblsCorr._fields
            name = 'Corr'
        channel = self.devpref.substitute(propty=name + 'Status-Mon')
        for bit, label in enumerate(items):
            led = SiriusLedAlert(self, channel, bit)
            lab = QLabel(label, self)
            fbl.addRow(led, lab)
        return wid
