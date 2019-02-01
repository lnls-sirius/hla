"""Control of EVG Timing Device."""

import sys as _sys
import os as _os
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, \
    QSizePolicy as QSzPol, QWidget, QGridLayout, QGroupBox, QLabel
from pydm.widgets import PyDMLabel, PyDMLineEdit, PyDMSpinbox, \
    PyDMPushButton, PyDMEnumComboBox as PyDMECB, PyDMCheckbox as PyDMCb
from siriuspy.csdevice import timesys as _cstime
from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriushla import util as _util
from siriushla.widgets import SiriusMainWindow, PyDMLed, SiriusLedAlert, \
    PyDMStateButton
from siriushla.as_ti_control.evg import EventList as _EventList
from siriushla.as_ti_control.evg import EVG as _EVG
from siriushla.as_ti_control.evr_eve import EVR as _EVR
from siriushla.as_ti_control.evr_eve import EVE as _EVE
from siriushla.as_ti_control.afc import AFC as _AFC
from siriushla.as_ti_control.fout import FOUT as _FOUT
from siriushla.as_ti_control.hl_trigger import HLTriggerList as _HLTriggerList


class TimingMain(SiriusMainWindow):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()

    def setupui(self):
        self.setupmenus()

        mainwid = QWidget(self)
        self.setCentralWidget(mainwid)
        gridlayout = QGridLayout(mainwid)

        globpars = self.setglobalparameters()
        gridlayout.addWidget(globpars, 0, 0, 1, 2)

        events = self.setevents()
        gridlayout.addWidget(events, 1, 0)

        triggers = self.settriggers()
        gridlayout.addWidget(triggers, 1, 1)

    def setglobalparameters(self):
        wid = QGroupBox(self.centralWidget())
        hbl = QHBoxLayout(wid)

        evg_pref = LLTimeSearch.get_device_names({'dev': 'EVG'})[0]
        evg_pref = self.prefix + evg_pref + ':'
        sp = PyDMPushButton(
            self, init_channel=evg_pref+"UpdateEvt-Cmd", pressValue=1,
            label='Update')
        rb = PyDMLed(self, init_channel=evg_pref + "EvtSyncStatus-Mon")
        rb.setMinimumHeight(40)
        hbl.addWidget(self._create_prop_widget('Update Evts', wid, (sp, rb)))

        sp = PyDMStateButton(self, init_channel=evg_pref + "ContinuousEvt-Sel")
        rb = PyDMLed(self, init_channel=evg_pref + "ContinuousEvt-Sts")
        rb.setMinimumHeight(40)
        hbl.addWidget(self._create_prop_widget('Continuous', wid, (sp, rb)))

        sp = PyDMStateButton(self, init_channel=evg_pref + "InjectionEvt-Sel")
        rb = PyDMLed(self, init_channel=evg_pref + "InjectionEvt-Sts")
        rb.setMinimumHeight(40)
        hbl.addWidget(self._create_prop_widget('Injection', wid, (sp, rb)))
        return wid

    def setevents(self):
        wid = QGroupBox(self.centralWidget())
        hbl = QHBoxLayout(wid)
        props = {'ext_trig', 'mode', 'delay_type', 'delay'}
        evg_pref = LLTimeSearch.get_device_names({'dev': 'EVG'})[0] + ':'
        names = list(map(
            lambda x: evg_pref + x[1],
            sorted(_cstime.Const.EvtLL2HLMap.items())))
        evts = _EventList(
            name='High Level Events', parent=wid, prefix=self.prefix,
            props=props, obj_names=names)
        hbl.addWidget(evts)
        return wid

    def settriggers(self):
        wid = QGroupBox(self.centralWidget())
        hbl = QHBoxLayout(wid)
        props = {
            'detailed', 'status', 'state', 'source',
            'pulses', 'duration', 'delay'}
        names = HLTimeSearch.get_hl_triggers()
        trigs = _HLTriggerList(
            name='High Level Triggers', parent=wid, prefix=self.prefix,
            props=props, obj_names=names)
        hbl.addWidget(trigs)
        return wid

    def setupmenus(self):
        prefix = self.prefix
        main_menu = self.menuBar()
        menu = main_menu.addMenu('&Devices')
        action = menu.addAction('EVG')
        evg = LLTimeSearch.get_device_names(filters={'dev': 'EVG'})[0]
        _util.connect_window(action, _EVG, self, prefix=prefix + evg + ':')

        menu_evr = menu.addMenu('EVRs')
        for evr in LLTimeSearch.get_device_names(filters={'dev': 'EVR'}):
            action = menu_evr.addAction(evr)
            _util.connect_window(action, _EVR, self, prefix=prefix+evr+':')

        menu_eve = menu.addMenu('EVEs')
        for eve in LLTimeSearch.get_device_names(filters={'dev': 'EVE'}):
            action = menu_eve.addAction(eve)
            _util.connect_window(action, _EVE, self, prefix=prefix + eve + ':')

        menu_afc = menu.addMenu('AFCs')
        for afc in LLTimeSearch.get_device_names(
                                    filters={'dev': 'AMCFPGAEVR'}):
            action = menu_afc.addAction(afc)
            _util.connect_window(action, _AFC, self, prefix=prefix+afc+':')

        menu_fout = menu.addMenu('FOUTs')
        for fout in LLTimeSearch.get_device_names(filters={'dev': 'FOUT'}):
            action = menu_fout.addAction(fout)
            _util.connect_window(action, _FOUT, self, prefix=prefix+fout+':')

    def _create_prop_widget(self, name, parent, wids, align_ver=True):
        pwid = QWidget(parent)
        vbl = QVBoxLayout(pwid)
        lab = QLabel(name)
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        hbl = QHBoxLayout()
        vbl.addItem(hbl)
        for wid in wids:
            wid.setParent(pwid)
            hbl.addWidget(wid)
            hbl.setAlignment(wid, Qt.AlignCenter)
        return pwid


if __name__ == '__main__':
    """Run Example."""
    from siriuspy.envars import vaca_prefix as PREFIX
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    HLTiming = TimingMain(prefix=PREFIX)
    HLTiming.show()
    _sys.exit(app.exec_())
