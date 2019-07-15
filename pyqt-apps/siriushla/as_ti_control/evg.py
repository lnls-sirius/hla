import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, QMenuBar, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy as QSzPol
from pydm.widgets import PyDMLabel, PyDMLineEdit, PyDMPushButton
from siriuspy.search import LLTimeSearch
from siriuspy.csdevice import timesys as _cstime
from siriushla.util import connect_window
from siriushla.widgets import PyDMLed, SiriusLedAlert, PyDMStateButton
from siriushla.widgets.windows import create_window_from_widget
from siriushla import as_ti_control as _ti_ctrl
from .base import BaseList, BaseWidget, \
    MySpinBox as _MySpinBox, MyComboBox as _MyComboBox


class EVG(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix=prefix)
        self.setupui()
        self.setObjectName('ASApp')

    def setupui(self):
        mylayout = QGridLayout(self)
        mylayout.setHorizontalSpacing(20)
        mylayout.setVerticalSpacing(20)

        mylayout.addWidget(self._setupmenus(), 0, 0, 1, 2)

        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        mylayout.addWidget(lab, 1, 0, 1, 2)
        mylayout.setAlignment(lab, Qt.AlignCenter)

        self.configs_wid = QGroupBox('Configurations', self)
        mylayout.addWidget(self.configs_wid, 2, 0)
        self._setup_configs_wid()

        self.status_wid = QGroupBox('Status', self)
        mylayout.addWidget(self.status_wid, 2, 1)
        self._setup_status_wid()

        self.events_wid = EventList(
            name='Events', parent=self, prefix=self.prefix,
            obj_names=sorted(_cstime.Const.EvtLL._fields[1:]))
        self.events_wid.setObjectName('events_wid')
        self.events_wid.setStyleSheet("""#events_wid{min-width:40em;}""")
        mylayout.addWidget(self.events_wid, 3, 0)

        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            props={'name', 'mux_enbl', 'frequency'},
            obj_names=sorted(_cstime.Const.ClkLL._fields)
            )
        mylayout.addWidget(self.clocks_wid, 3, 1)

        # grpbx = self._create_formlayout_groupbox('Configurations', (
        #     ('DevEnbl-Sel', 'Enabled'),
        #     ('ContinuousEvt-Sel', 'Continuous'),
        #     ('InjectionEvt-Sel', 'Injection'),
        #     ('ACDiv-SP', 'AC Divisor'),
        #     ('RFDiv-SP', 'RF Divisor'),
        #     # ('BucketList-SP', 'Bucket List'),
        #     ('RepeatBucketList-SP', 'Repeat Bucket List'),
        #     ))
        # mylayout.addWidget(grpbx, 1, 0)

    def _setupmenus(self):
        prefix = self.prefix
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Downlinks')

        downs = LLTimeSearch.get_device_names({'dev': 'Fout'})
        link = list(LLTimeSearch.In2OutMap[downs[0].dev])[0]
        downs2 = list()
        for down in downs:
            out = LLTimeSearch.get_evg_channel(down.substitute(propty=link))
            downs2.append((out.propty, down.device_name))

        for out, down in sorted(downs2):
            action = menu.addAction(out + ' --> ' + down)
            Win = create_window_from_widget(_ti_ctrl.FOUT, title=down)
            connect_window(action, Win, self, prefix=down + ':')
        return main_menu

    def _setup_configs_wid(self):
        prefix = self.prefix

        configlayout = QHBoxLayout(self.configs_wid)
        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addStretch()
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'Dev Enable', self.configs_wid, (sp, rb)))

        sp = _MySpinBox(self, init_channel=prefix + "RFDiv-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "RFDiv-RB")
        layrow.addWidget(self._create_prop_widget(
                        'RF Divisor', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMPushButton(
            self, init_channel=prefix+"RFReset-Cmd", pressValue=1,
            label='Reset')
        rb = PyDMLed(self, init_channel=prefix + "RFStatus-Mon")
        layrow.addWidget(self._create_prop_widget(
                        'RF Status', self.configs_wid, (sp, rb)))

        sp = PyDMPushButton(
            self, init_channel=prefix+"UpdateEvt-Cmd", pressValue=1,
            label='Update')
        rb = PyDMLed(self, init_channel=prefix + "EvtSyncStatus-Mon")
        layrow.addWidget(self._create_prop_widget(
                        'Update Evts', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMStateButton(self, init_channel=prefix + "ACEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "ACEnbl-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'AC Enable', self.configs_wid, (sp, rb)))

        mon = PyDMLed(self, init_channel=prefix + "ACStatus-Mon")
        layrow.addWidget(self._create_prop_widget(
                        'AC Status', self.configs_wid, (mon,)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = _MySpinBox(self, init_channel=prefix + "InjRate-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "InjRate-RB")
        layrow.addWidget(self._create_prop_widget(
                        'Pulse Rate [Hz]', self.configs_wid, (sp, rb)))

        sp = _MyComboBox(self, init_channel=prefix + "ACSrc-Sel")
        rb = PyDMLabel(self, init_channel=prefix + "ACSrc-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'AC Source', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = _MySpinBox(self, init_channel=prefix + "RepeatBucketList-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "RepeatBucketList-RB")
        layrow.addWidget(self._create_prop_widget(
                        'Repeat BL', self.configs_wid, (sp, rb)))

        rb = PyDMLabel(self, init_channel=prefix + "BucketListLen-Mon")
        layrow.addWidget(self._create_prop_widget(
                        'Bucket List Size', self.configs_wid, (rb, )))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMStateButton(self, init_channel=prefix + "ContinuousEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "ContinuousEvt-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'Continuous', self.configs_wid, (sp, rb)))

        sp = PyDMStateButton(self, init_channel=prefix + "InjectionEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "InjectionEvt-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'Injection', self.configs_wid, (sp, rb)))

        # sp = PyDMLineEdit(self, init_channel=prefix + "BucketList-SP")
        # sp.setStyleSheet("""min-width:9.7em; max-height:1.15em;""")
        # sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        # rb = PyDMLabel(self, init_channel=prefix + "BucketList-RB")
        # rb.setStyleSheet(
        #    """min-width:9.7em; max-width:16em; max-height:1.15em;""")
        # rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        # # gb = self._create_small_GB('Bucket List', self.configs_wid, (sp, rb))
        # # configs_layout.addWidget(gb, 2, 0, 1, 2)

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        rb = PyDMLabel(self, init_channel=prefix + "STATEMACHINE")
        status_layout.addWidget(rb, 0, 0, 1, 3)
        status_layout.setAlignment(rb, Qt.AlignCenter)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 0)

        lb = QLabel("<b>Network</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Network-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 1)

        lb = QLabel("<b>RF Sts</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "RFStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 2)

        wids = list()
        for i in range(8):
            rb = SiriusLedAlert(self, init_channel=prefix + "Los-Mon", bit=i)
            wids.append(rb)
        gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 2, 0, 1, 3)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb

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

    # def _create_prop_widget(self, name, parent, wids, align_ver=True):
    #     pwid = QWidget(parent)
    #     lay = QGridLayout(pwid)
    #     lab = QLabel(name)
    #     lab.setAlignment(Qt.AlignCenter)
    #     lay.addWidget(lab, 0, 0, 1, len(wids))
    #     for i, wid in enumerate(wids):
    #         wid.setParent(pwid)
    #         lay.addWidget(wid, 1, i)
    #     return pwid


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 4.8, 'mode': 6.6, 'delay_type': 4.2, 'delay': 4.8,
        'description': 9.7, 'code': 3.2,
        }
    _LABELS = {
        'ext_trig': 'Ext. Trig.', 'mode': 'Mode', 'description': 'Description',
        'delay_type': 'Type', 'delay': 'Delay [us]', 'code': 'Code',
        }
    _ALL_PROPS = (
        'ext_trig', 'mode', 'delay_type', 'delay', 'description', 'code')

    def __init__(self, **kwargs):
        kwargs['props2search'] = set(('mode', 'ext_trig', 'delay_type'))
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if prop == 'ext_trig':
            sp = PyDMPushButton(
                self, init_channel=prefix+'ExtTrig-Cmd', pressValue=1)
            sp.setText(prefix.propty)
        elif prop == 'mode':
            sp = _MyComboBox(self, init_channel=prefix + "Mode-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "Mode-Sts")
        elif prop == 'delay_type':
            sp = _MyComboBox(self, init_channel=prefix+"DelayType-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"DelayType-Sts")
        elif prop == 'delay':
            sp = _MySpinBox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        elif prop == 'description':
            sp = PyDMLineEdit(self, init_channel=prefix + 'Desc-SP')
            rb = PyDMLabel(self, init_channel=prefix + 'Desc-RB')
        elif prop == 'code':
            sp = PyDMLabel(self, init_channel=prefix+'Code-Mon')
            sp.setAlignment(Qt.AlignCenter)
        if rb is None:
            return (sp, )
        return (sp, rb)


class ClockList(BaseList):
    """Template for control of Low Level Clocks."""

    _MIN_WIDs = {
        'name': 3.8,
        'frequency': 4.8,
        'mux_div': 4.8,
        'mux_enbl': 4.8,
        }
    _LABELS = {
        'name': 'Clock Name',
        'frequency': 'Freq. [Hz]',
        'mux_div': 'Mux Divisor',
        'mux_enbl': 'Enabled',
        }
    _ALL_PROPS = ('name', 'mux_enbl', 'frequency', 'mux_div')

    def __init__(self, name=None, parent=None, prefix='',
                 props=set(), obj_names=list(), has_search=False):
        """Initialize object."""
        super().__init__(name=name, parent=parent, prefix=prefix, props=props,
                         obj_names=obj_names, has_search=has_search)
        self.setObjectName('ASApp')

    def _createObjs(self, prefix, prop):
        if prop == 'frequency':
            sp = _MySpinBox(self, init_channel=prefix + "Freq-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Freq-RB")
        elif prop == 'name':
            rb = QLabel(prefix.propty, self)
            rb.setAlignment(Qt.AlignCenter)
            return (rb, )
        elif prop == 'mux_enbl':
            sp = PyDMStateButton(self, init_channel=prefix + "MuxEnbl-Sel")
            rb = PyDMLed(self, init_channel=prefix + "MuxEnbl-Sts")
        elif prop == 'mux_div':
            sp = _MySpinBox(self, init_channel=prefix + "MuxDiv-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "MuxDiv-RB")
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow
    app = SiriusApplication()
    win = SiriusMainWindow()
    evg_ctrl = EVG(prefix='TEST-FAC:TI-EVG:')
    win.setCentralWidget(evg_ctrl)
    win.show()
    sys.exit(app.exec_())
