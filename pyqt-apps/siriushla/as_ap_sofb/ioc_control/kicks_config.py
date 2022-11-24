"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, \
    QGroupBox, QPushButton, QWidget, QTabWidget, QGridLayout
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from ...util import connect_window
from ...widgets import SiriusLedAlert
from ...widgets.windows import create_window_from_widget
from ...as_ti_control import HLTriggerDetailed

from .base import BaseWidget
from .status import StatusWidget


class KicksConfigWidget(BaseWidget):

    def __init__(self, parent, device, prefix='', acc='SI'):
        super().__init__(parent, device, prefix=prefix, acc=acc)
        self.setupui()

    def setupui(self):
        self.setLayout(QVBoxLayout())

        names = ('Maximum Kicks', 'Maximum Delta Kicks')
        tabs = ('Max \u03b8', 'Max \u0394\u03b8')
        pvnames = ('MaxKick', 'MaxDeltaKick')
        unitss = (('[urad]', '[urad]'), ('[urad]', '[urad]'))
        planes = ('CH', 'CV')
        if self.acc in {'SI', 'BO'}:
            unitss = (
                ('[urad]', '[urad]', None),
                ('[urad]', '[urad]', '[Hz]'), )
            planes = ('CH', 'CV', 'RF')

        tabw = QTabWidget(self)
        tabw.setObjectName(self.acc+'Tab')
        tabw.setStyleSheet("""
            #{0}Tab::pane {{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }}""".format(self.acc))
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

        syn_grp = QGroupBox('Sync.', det_wid)
        syn_wid = self.create_pair_sel(syn_grp, 'CorrSync', is_vert=True)
        syn_wid.layout().setContentsMargins(0, 1, 0, 1)
        gdl = QGridLayout(syn_grp)
        gdl.addWidget(syn_wid, 0, 0)

        pssofb_grp = QGroupBox('PSSOFB', det_wid)
        enbl_lbl = QLabel('Enable:', pssofb_grp)
        enbl_wid = self.create_pair_butled(pssofb_grp, 'CorrPSSOFBEnbl')
        enbl_wid.layout().setContentsMargins(0, 0, 0, 0)
        wait_lbl = QLabel('Wait:', pssofb_grp)
        wait_wid = self.create_pair_butled(pssofb_grp, 'CorrPSSOFBWait')
        wait_wid.layout().setContentsMargins(0, 0, 0, 0)
        gdl = QGridLayout(pssofb_grp)
        gdl.setSpacing(1)
        gdl.addWidget(enbl_lbl, 0, 0)
        gdl.addWidget(wait_lbl, 1, 0)
        gdl.addWidget(enbl_wid, 0, 1)
        gdl.addWidget(wait_wid, 1, 1)

        del_grp = QGroupBox('Trigger Delay', det_wid)
        del_wid = self.create_pair(
            del_grp, 'Delay', device='SI-Glob:TI-Mags-Corrs', is_vert=False)
        del_det = QPushButton(qta.icon('fa5s.ellipsis-h'), '', del_grp)
        del_det.setToolTip('Open details')
        del_det.setObjectName('detail')
        del_det.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        trg_w = create_window_from_widget(
            HLTriggerDetailed,
            title='SI-Glob:TI-Mags-Corrs Detailed Settings', is_main=True)
        connect_window(
            del_det, trg_w, parent=None, device='SI-Glob:TI-Mags-Corrs',
            prefix=self.prefix)
        del_lay = QHBoxLayout(del_grp)
        del_lay.addStretch()
        del_lay.addWidget(del_wid)
        del_lay.addWidget(del_det)
        del_lay.addStretch()

        det_lay.addWidget(pssofb_grp, 0, 0)
        det_lay.addWidget(syn_grp, 0, 2)
        det_lay.addWidget(del_grp, 2, 0, 1, 3)
        det_lay.setColumnStretch(1, 10)
        det_lay.setRowStretch(1, 10)
        return det_wid

    def get_status_widget(self, parent):
        """."""
        conf = PyDMPushButton(
            parent, pressValue=1,
            init_channel=self.devpref.substitute(propty='CorrConfig-Cmd'))
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
            sts, Window, self, device=self.device,
            prefix=self.prefix, acc=self.acc, is_orb=False)

        pdm_led = SiriusLedAlert(
            parent, self.devpref.substitute(propty='CorrStatus-Mon'))

        lbl = QLabel('Correctors Status:', parent)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(lbl)
        hbl.addStretch()
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        return hbl
