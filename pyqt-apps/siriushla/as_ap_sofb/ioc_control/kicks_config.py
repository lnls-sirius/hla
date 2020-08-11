"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, \
    QGroupBox, QPushButton, QWidget, QTabWidget, QGridLayout
from qtpy.QtCore import Qt
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from ...util import connect_window
from ...widgets import SiriusLedAlert
from ...widgets.windows import create_window_from_widget
from ...as_ti_control import HLTriggerDetailed

from .base import BaseWidget
from .status import StatusWidget


class KicksConfigWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc=acc)
        self.setupui()

    def setupui(self):
        self.setLayout(QVBoxLayout())

        names = ('Maximum Kicks', 'Maximum Delta Kicks')
        tabs = ('Max \u03b8', 'Max \u0394\u03b8')
        pvnames = ('MaxKick', 'MaxDeltaKick')
        unitss = (('[urad]', '[urad]'), ('[urad]', '[urad]'))
        planes = ('CH', 'CV')
        if self.acc == 'SI':
            unitss = (
                ('[urad]', '[urad]', None),
                ('[urad]', '[urad]', '[Hz]'), )
            planes = ('CH', 'CV', 'RF')

        tabw = QTabWidget(self)
        self.layout().addWidget(tabw)
        for tab, pvname, units in zip(tabs, pvnames, unitss):
            grpbx = QWidget(tabw)
            grpbx.setObjectName('gbx')
            fbl = QFormLayout(grpbx)
            for unit, pln in zip(units, planes):
                if unit is None:
                    continue
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
        if self.acc == 'SI':
            det_wid = self.get_details_widget(tabw)
            tabw.addTab(det_wid, 'Details')

    def get_details_widget(self, parent):
        """."""
        det_wid = QWidget(parent)
        det_wid.setObjectName('gbx')
        det_lay = QGridLayout(det_wid)

        # syn_lbl = QLabel('Synchronize', det_wid)
        syn_wid = self.create_pair_sel(det_wid, 'CorrSync', is_vert=True)
        syn_wid.layout().setContentsMargins(0, 1, 0, 1)

        del_lbl = QLabel('Delay', det_wid)
        del_wid = self.create_pair(
            det_wid, 'Delay', prefix='SI-Glob:TI-Mags-Corrs:', is_vert=False)
        del_det = QPushButton(qta.icon('fa5s.ellipsis-h'), '', det_wid)
        del_det.setToolTip('Open details')
        del_det.setObjectName('detail')
        del_det.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        trg_w = create_window_from_widget(
            HLTriggerDetailed,
            title='SI-Glob:TI-Mags-Corrs Detailed Settings', is_main=True)
        connect_window(
            del_det, trg_w, parent=None,
            prefix='SI-Glob:TI-Mags-Corrs:')

        enbl_lbl = QLabel('Enable:', det_wid)
        enbl_wid = self.create_pair_butled(det_wid, 'CorrPSSOFBEnbl')
        enbl_wid.layout().setContentsMargins(0, 0, 0, 0)
        wait_lbl = QLabel('Wait:', det_wid)
        wait_wid = self.create_pair_butled(det_wid, 'CorrPSSOFBWait')
        wait_wid.layout().setContentsMargins(0, 0, 0, 0)

        pssofb_grp = QGroupBox('PSSOFB', det_wid)
        gdl = QGridLayout(pssofb_grp)
        # gdl.setContentsMargins(1, 0, 0, 0)
        gdl.setSpacing(1)
        gdl.addWidget(enbl_lbl, 0, 0)
        gdl.addWidget(wait_lbl, 1, 0)
        gdl.addWidget(enbl_wid, 0, 1)
        gdl.addWidget(wait_wid, 1, 1)

        det_lay.addWidget(pssofb_grp, 0, 0)

        syn_grp = QGroupBox('Sync.', det_wid)
        gdl = QGridLayout(syn_grp)
        gdl.addWidget(syn_wid, 0, 0)
        det_lay.addWidget(syn_grp, 0, 2)

        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        hbl.addStretch()
        hbl.addWidget(del_lbl)
        hbl.addWidget(del_wid)
        hbl.addWidget(del_det)
        hbl.addStretch()
        det_lay.addLayout(hbl, 2, 0, 1, 3)
        det_lay.setColumnStretch(1, 10)
        det_lay.setRowStretch(1, 10)

        return det_wid

    def get_status_widget(self, parent):
        """."""
        conf = PyDMPushButton(
            parent,
            init_channel=self.prefix+'CorrConfig-Cmd', pressValue=1)
        conf.setToolTip('Refresh Configurations')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        sts = QPushButton('', parent)
        sts.setIcon(qta.icon('fa5s.list-ul'))
        sts.setToolTip('Open Detailed Status View')
        sts.setObjectName('sts')
        sts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        Window = create_window_from_widget(
            StatusWidget, title='Correctors Status')
        connect_window(
            sts, Window, self, prefix=self.prefix, acc=self.acc, is_orb=False)

        pdm_led = SiriusLedAlert(
            parent, init_channel=self.prefix+'CorrStatus-Mon')

        lbl = QLabel('Correctors Status:', parent)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(lbl)
        hbl.addStretch()
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        return hbl


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
