"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, \
    QGroupBox, QPushButton, QWidget, QTabWidget, QGridLayout
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from ...util import connect_window
from ...widgets import SiriusLedAlert, SiriusLabel, SiriusLedState
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
            tabw.setCurrentIndex(2)

    def get_details_widget(self, parent):
        """."""
        det_wid = QWidget(parent)
        det_wid.setObjectName('gbx')
        det_lay = QGridLayout(det_wid)

        syn_wid = self.create_pair_butled(det_wid, 'CorrSync', is_vert=False)
        syn_lab = SiriusLabel(det_wid, self.device+':CorrSync-Sts')
        syn_wid.layout().setContentsMargins(0, 1, 0, 1)
        det_lay.addWidget(QLabel('Synchronization', det_wid), 0, 0)
        det_lay.addWidget(syn_wid, 0, 1)
        det_lay.addWidget(syn_lab, 0, 2)

        enbl_wid = self.create_pair_butled(
            det_wid, 'CorrPSSOFBEnbl', is_vert=False)
        enbl_led = SiriusLedState(det_wid, self.device+':CorrPSSOFBEnbl-Mon')
        enbl_wid.layout().setContentsMargins(0, 0, 0, 0)
        det_lay.addWidget(QLabel('PSSOFB Enable:', det_wid), 1, 0)
        det_lay.addWidget(enbl_wid, 1, 1)
        det_lay.addWidget(enbl_led, 1, 2)

        del_wid = self.create_pair(
            det_wid, 'Delay', device='SI-Glob:TI-Mags-Corrs', is_vert=False)
        del_det = QPushButton(qta.icon('fa5s.ellipsis-h'), '', det_wid)
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
        del_lay = QGridLayout()
        del_lay.addWidget(QLabel('Trigger Delay', det_wid), 0, 0)
        del_lay.addWidget(del_wid, 0, 1)
        del_lay.addWidget(del_det, 0, 2)
        det_lay.addLayout(del_lay, 2, 0, 1, 3)

        return det_wid

    def get_status_widget(self, parent):
        """."""
        conf = PyDMPushButton(
            parent, pressValue=1,
            init_channel=self.devpref.substitute(propty='CorrConfig-Cmd'))
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.devpref.substitute(propty='LoopState-Sts') +
            '", "trigger": true}]}]')
        conf.rules = rules
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
