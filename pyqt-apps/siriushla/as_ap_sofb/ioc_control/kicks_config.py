"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, \
    QGroupBox

from pydm.widgets import PyDMPushButton
from siriushla.widgets import PyDMStateButton

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget


class KicksConfigWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI', show_details=False):
        super().__init__(parent, prefix, acc=acc)
        self.show_details = show_details
        self.setupui()

    def setupui(self):
        names = ('Correction Factors', 'Maximum Kicks', 'Maximum Delta Kicks')
        pvnames = ('DeltaFactor', 'MaxKick', 'MaxDeltaKick')
        unitss = (('[%]', '[%]'), ('[urad]', '[urad]'), ('[urad]', '[urad]'))
        planes = ('CH', 'CV')
        if self.isring:
            unitss = (
                ('[%]', '[%]', '[%]'),
                ('[urad]', '[urad]', '[Hz]'),
                ('[urad]', '[urad]', '[Hz]'), )
            planes = ('CH', 'CV', 'RF')
        if not self.show_details:
            names = names[:1]
            pvnames = pvnames[:1]
            unitss = unitss[:1]

        vbl = QVBoxLayout(self)
        for name, pvname, units in zip(names, pvnames, unitss):
            grpbx = QGroupBox(name)
            fbl = QFormLayout(grpbx)
            # fbl.setSpacing(9)
            for unit, pln in zip(units, planes):
                lbl = QLabel(pln+' '+unit+'  ', grpbx)
                fbl.addRow(lbl, self.create_pair(grpbx, pvname+pln))
            vbl.addWidget(grpbx)
        if self.show_details:
            # vbl.addSpacing(40)
            if self.isring:
                lbl = QLabel('Synchronize Correctors', self)
                pdm_btn = PyDMStateButton(
                    self, init_channel=self.prefix+'CorrSync-Sel')
                hbl = QHBoxLayout()
                hbl.addWidget(lbl)
                hbl.addWidget(pdm_btn)
                vbl.addItem(hbl)
            pdm_btn = PyDMPushButton(
                self, label='Configure Correctors',
                init_channel=self.prefix+'CorrConfig-Cmd', pressValue=1)
            # vbl.addSpacing(20)
            vbl.addWidget(pdm_btn)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = pref+'SI-Glob:AP-SOFB:'
    wid = KicksConfigWidget(win, prefix, 'SI', True)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
