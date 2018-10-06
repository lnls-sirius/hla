"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout

from pydm.widgets import PyDMPushButton
from siriushla.widgets import PyDMStateButton

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class KicksConfigWidget(BaseWidget):

    def __init__(self, parent, prefix, show_details):
        super().__init__(parent, prefix)
        self.show_details = show_details
        self.setupui()

    def setupui(self):
        names = ('Correction Factors', 'Maximum Kicks', 'Maximum Delta Kicks')
        pvnames = ('CorrFactor', 'MaxKick', 'MaxDeltaKick')
        unitss = (
            ('[%]', '[%]', '[%]'),
            ('[urad]', '[urad]', '[Hz]'),
            ('[urad]', '[urad]', '[Hz]'), )
        if not self.show_details:
            names = names[:1]
            pvnames = pvnames[:1]
            unitss = unitss[:1]

        vbl = QVBoxLayout(self)
        for name, pvname, units in zip(names, pvnames, unitss):
            fbl = QFormLayout()
            fbl.setSpacing(9)
            lbl = QLabel(name, self)
            lbl.setAlignment(Qt.AlignCenter)
            fbl.addRow(lbl)
            for unit, pln in zip(units, ('CH', 'CV', 'RF')):
                lbl = QLabel(pln+' '+unit+'  ', self)
                fbl.addRow(
                    lbl, self.create_pair(self, pvname+pln))
            vbl.addItem(fbl)
            if self.show_details:
                vbl.addSpacing(40)
        if self.show_details:
            lbl = QLabel('Synchronize Kicks', self)
            pdm_btn = PyDMStateButton(
                self, init_channel=self.prefix+'SyncKicks-Sel')
            pdm_btn.setMinimumHeight(20)
            pdm_btn.setMaximumHeight(40)
            hbl = QHBoxLayout()
            hbl.addWidget(lbl)
            hbl.addWidget(pdm_btn)
            vbl.addItem(hbl)
            pdm_btn = PyDMPushButton(
                self, label='Configure Correctors',
                init_channel=self.prefix+'ConfigCorrs-Cmd', pressValue=1)
            vbl.addSpacing(20)
            vbl.addWidget(pdm_btn)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    wid = KicksConfigWidget(win, prefix, True)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
