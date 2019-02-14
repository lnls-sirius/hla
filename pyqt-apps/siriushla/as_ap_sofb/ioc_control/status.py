"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QFormLayout
from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusLedAlert
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class StatusWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI', is_orb=False):
        super().__init__(parent, prefix, acc)
        self.is_orb = is_orb
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = 'Config. Acquisition' if self.is_orb else 'Config. Correctors'
        pv = 'OrbitTrigAcqConfig-Cmd' if self.is_orb else 'ConfigCorrs-Cmd'
        pdm_btn = PyDMPushButton(
            self, label=lab, init_channel=self.prefix + pv, pressValue=1)
        vbl.addWidget(pdm_btn)
        vbl.addSpacing(20)

        grpbx = self.creategroupbox('Orbit' if self.is_orb else 'Corr')
        vbl.addWidget(grpbx)

    def creategroupbox(self, name):
        if name == 'Corr':
            labels = self._csorb.StatusLabelsCorrs
            title = 'Correctors'
        else:
            labels = self._csorb.StatusLabelsOrb
            title = 'Orbit'
        wid = QGroupBox(title + ' Status', self)

        fbl = QFormLayout(wid)
        fbl.setHorizontalSpacing(20)
        fbl.setVerticalSpacing(20)
        channel = self.prefix + name + 'Status-Mon'
        for bit, label in enumerate(labels._fields):
            led = SiriusLedAlert(self, channel, bit)
            lab = QLabel(label, self)
            fbl.addRow(led, lab)
        return wid


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    vbl = QVBoxLayout(win)
    acc = 'BO'
    prefix = pref+acc+'-Glob:AP-SOFB:'
    wid = StatusWidget(win, prefix, acc, True)
    vbl.addWidget(wid)
    vbl.addSpacing(40)
    wid = StatusWidget(win, prefix, acc, False)
    vbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
