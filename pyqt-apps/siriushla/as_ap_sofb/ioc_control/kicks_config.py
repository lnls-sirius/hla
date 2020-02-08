"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, \
    QGroupBox, QPushButton, QWidget, QTabWidget
import qtawesome as qta

from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusLedAlert

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget
from siriushla.widgets.windows import create_window_from_widget
import siriushla.util as _util

from .status import StatusWidget


class KicksConfigWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc=acc)
        self.setupui()

    def setupui(self):
        gbox = QGroupBox('Correctors', self)
        gbox.setObjectName('grbx')
        gbox.setStyleSheet('#grbx{min-height:13.0em; max-height:13.0em;}')
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(gbox)
        vbl = QVBoxLayout(gbox)

        conf = PyDMPushButton(
            gbox,
            init_channel=self.prefix+'CorrConfig-Cmd', pressValue=1)
        conf.setToolTip('Refresh Configurations')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        sts = QPushButton('', gbox)
        sts.setIcon(qta.icon('fa5s.list-ul'))
        sts.setToolTip('Open Detailed Status View')
        sts.setObjectName('sts')
        sts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        Window = create_window_from_widget(
            StatusWidget, title='Correctors Status')
        _util.connect_window(
            sts, Window, self, prefix=self.prefix, acc=self.acc, is_orb=False)

        pdm_led = SiriusLedAlert(
            gbox, init_channel=self.prefix+'CorrStatus-Mon')

        lbl = QLabel('Status:', gbox)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        vbl.addItem(hbl)

        names = ('Correction Factors', 'Maximum Kicks', 'Maximum Delta Kicks')
        tabs = ('%', 'Max \u03b8', 'Max \u0394\u03b8')
        pvnames = ('DeltaFactor', 'MaxKick', 'MaxDeltaKick')
        unitss = (('[%]', '[%]'), ('[urad]', '[urad]'), ('[urad]', '[urad]'))
        planes = ('CH', 'CV')
        if self.acc == 'SI':
            unitss = (
                ('[%]', '[%]', '[%]'),
                ('[urad]', '[urad]', '[Hz]'),
                ('[urad]', '[urad]', '[Hz]'), )
            planes = ('CH', 'CV', 'RF')

        tabw = QTabWidget(self)
        vbl.addWidget(tabw)
        for tab, pvname, units in zip(tabs, pvnames, unitss):
            grpbx = QWidget(tabw)
            grpbx.setObjectName('gbx')
            grpbx.setStyleSheet('#gbx{min-height:5.5em; max-height:5.5em;}')
            # grpbx.setVisible(pvname.startswith('Delta'))
            fbl = QFormLayout(grpbx)
            for unit, pln in zip(units, planes):
                lbl = QLabel(pln+' '+unit+'  ', grpbx)
                lbl.setObjectName('lbl')
                lbl.setStyleSheet('#lbl{min-height:1em;}')
                wid = self.create_pair(grpbx, pvname+pln)
                wid.setObjectName('wid')
                wid.setStyleSheet('#wid{min-height:1.2em;}')
                fbl.addRow(lbl, wid)
            tabw.addTab(grpbx, tab)
        for i, name in enumerate(names):
            tabw.setTabToolTip(i, name)
        if self.isring:
            lbl = QLabel('Synchronize', gbox)
            wid = self.create_pair_sel(gbox, 'CorrSync')
            hbl = QHBoxLayout()
            hbl.addWidget(lbl)
            hbl.addWidget(wid)
            vbl.addItem(hbl)


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
    from siriuspy.envars import VACA_PREFIX as pref
    import sys
    _main()
