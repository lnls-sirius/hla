import sys
import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, QMenuBar, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy as QSzPol, \
    QSplitter
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMLineEdit, PyDMPushButton
from siriuspy.search import LLTimeSearch
from siriuspy.timesys import csdev as _cstime
from siriushla.util import connect_window, get_appropriate_color
from siriushla.widgets import PyDMLed, SiriusLedAlert, PyDMStateButton, \
    SiriusLabel, SiriusEnumComboBox as _MyComboBox
from siriushla.widgets.windows import create_window_from_widget
from siriushla import as_ti_control as _ti_ctrl
from .base import BaseList, BaseWidget, MySpinBox as _MySpinBox


class BucketListLineEdit(PyDMLineEdit):

    def value_changed(self, value):
        super().value_changed(value)
        self.channeltype = _np.ndarray
        self.subtype = int


class BucketListLabel(SiriusLabel):

    def value_changed(self, value):
        maxele = 20
        if isinstance(value, _np.ndarray):
            zeros = _np.where(value == 0)[0]
            if zeros.size > 0:
                value = value[:zeros[0]]
            txt = '[ ' + ' '.join([str(i) for i in value[:maxele]])
            txt += ' ...]' if value.size > maxele else ']'
            self.setText(txt)
        else:
            super().value_changed(value)


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

        bucketlist_wid = BucketList(self, self.prefix)
        mylayout.addWidget(bucketlist_wid, 3, 0)

        self.status_wid = QGroupBox('Status', self)
        mylayout.addWidget(self.status_wid, 2, 1, 2, 1)
        self._setup_status_wid()

        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        mylayout.addWidget(splitter, 4, 0, 1, 2)

        self.events_wid = EventList(
            name='Events', parent=self, prefix=self.prefix,
            obj_names=sorted(_cstime.Const.EvtLL._fields[1:]))
        self.events_wid.setObjectName('events_wid')
        self.events_wid.setStyleSheet("events_wid{min-width:40em;}")
        splitter.addWidget(self.events_wid)

        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            props={'name', 'mux_enbl', 'frequency'},
            obj_names=sorted(_cstime.Const.ClkLL._fields),
            has_search=True,
            )
        splitter.addWidget(self.clocks_wid)

    def _setupmenus(self):
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
            icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
            Win = create_window_from_widget(
                _ti_ctrl.FOUT, title=down, icon=icon)
            connect_window(action, Win, None, prefix=down + ':')
        return main_menu

    def _setup_configs_wid(self):
        prefix = self.prefix

        suplay = QVBoxLayout(self.configs_wid)
        configlayout = QHBoxLayout()
        suplay.addItem(configlayout)
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
            self, init_channel=prefix+"RFReset-Cmd", pressValue=1)
        sp.setIcon(qta.icon('fa5s.sync'))
        sp.setToolTip('Reset RF Status')
        sp.setObjectName('but')
        sp.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
        rb = PyDMLed(self, init_channel=prefix + "RFStatus-Mon")
        layrow.addWidget(self._create_prop_widget(
                        'RF Status', self.configs_wid, (sp, rb)))

        sp = PyDMPushButton(
            self, init_channel=prefix+"UpdateEvt-Cmd", pressValue=1)
        sp.setIcon(qta.icon('fa5s.sync'))
        sp.setToolTip('Update Events Table')
        sp.setObjectName('but')
        sp.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
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

        sp = PyDMStateButton(self, init_channel=prefix + "ContinuousEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "ContinuousEvt-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'Continuous', self.configs_wid, (sp, rb)))

        sp = PyDMStateButton(self, init_channel=prefix + "InjectionEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "InjectionEvt-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'Injection', self.configs_wid, (sp, rb)))

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(5)

        rb1 = PyDMLabel(self.status_wid, init_channel=prefix + 'STATEMACHINE')
        rb2 = PyDMLabel(self.status_wid, init_channel=prefix + 'DevStatus-Mon')
        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(rb1)
        hlay.addStretch()
        hlay.addWidget(rb2)
        hlay.addStretch()
        status_layout.addItem(hlay, 0, 0, 1, 3)
        status_layout.setAlignment(hlay, Qt.AlignCenter)

        hlay = QHBoxLayout()
        wid = QWidget(self.status_wid)
        wid.setLayout(QHBoxLayout())
        wid.layout().setContentsMargins(0, 0, 0, 0)
        pydmlab1 = PyDMLabel(
            self.status_wid, init_channel=prefix+'TotalInjCount-Mon')
        pydmlab1.setStyleSheet('min-width:5em;')
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pydmlab2 = PyDMLabel(
            self.status_wid, init_channel=prefix+'InjCount-Mon')
        pydmlab2.setAlignment(Qt.AlignCenter)
        lab1 = QLabel(
            '(', self.status_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab2 = QLabel(
            ')', self.status_wid, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        wid.layout().addStretch()
        wid.layout().addWidget(pydmlab1)
        wid.layout().addWidget(lab1)
        wid.layout().addWidget(pydmlab2)
        wid.layout().addWidget(lab2)
        wid.layout().addStretch()
        hlay.addWidget(self._create_prop_widget(
            '<b>Inj Count: All (Now)</b>', self.status_wid, (wid, )))

        wid = QWidget(self.status_wid)
        wid.setLayout(QHBoxLayout())
        wid.layout().setContentsMargins(0, 0, 0, 0)
        pydmlab1 = PyDMLabel(
            self.status_wid, init_channel=prefix+'SeqStatus-Mon')
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pydmlab2 = PyDMLabel(
            self.status_wid, init_channel=prefix+'SeqCount-SP')
        lab1 = QLabel(
            '(', self.status_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab2 = QLabel(
            ')', self.status_wid, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        wid.layout().addStretch()
        wid.layout().addWidget(pydmlab1)
        wid.layout().addWidget(lab1)
        wid.layout().addWidget(pydmlab2)
        wid.layout().addWidget(lab2)
        wid.layout().addStretch()
        hlay.addWidget(self._create_prop_widget(
            '<b>Sequence: Table (Count)</b>', self.status_wid, (wid, )))
        status_layout.addItem(hlay, 1, 0, 1, 3)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 0)

        lb = QLabel("<b>Network</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Network-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 1)

        lb = QLabel("<b>RF Sts</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "RFStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 2)

        wids = list()
        for i in range(8):
            rb = SiriusLedAlert(self, init_channel=prefix + "Los-Mon", bit=i)
            wids.append(rb)
        gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 3, 0, 1, 3)

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


class BucketList(BaseWidget):

    def __init__(self, parent=None, prefix='', min_size=38):
        super().__init__(parent, prefix=prefix)
        self.setObjectName('ASApp')
        self._min_size = min_size
        self.setupui()

    def setupui(self):
        self.setLayout(QHBoxLayout(self))
        wid = QGroupBox('Bucket List', self)
        self.layout().addWidget(wid)
        self.layout().setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout(wid)
        prefix = self.prefix

        tm = 'min-width:{0:d}em; max-width:{0:d}em; max-height:1.15em;'.format(
            self._min_size)
        sp = BucketListLineEdit(wid, init_channel=prefix + "BucketList-SP")
        sp.setStyleSheet(tm)
        sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('SP : ', wid)
        lay_sp = QHBoxLayout()
        lay_sp.addWidget(lab)
        lay_sp.addWidget(sp)
        rb = BucketListLabel(wid, init_channel=prefix + "BucketList-RB")
        rb.setStyleSheet(tm)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('RB : ', wid)
        lay_rb = QHBoxLayout()
        lay_rb.addWidget(lab)
        lay_rb.addWidget(rb)
        mn = BucketListLabel(wid, init_channel=prefix + "BucketList-Mon")
        mn.setStyleSheet(tm)
        mn.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('Mon: ', wid)
        lay_mn = QHBoxLayout()
        lay_mn.addWidget(lab)
        lay_mn.addWidget(mn)
        vlay = QVBoxLayout()
        lay.addItem(vlay)
        vlay.addItem(lay_sp)
        vlay.addItem(lay_rb)
        vlay.addItem(lay_mn)

        rb = PyDMLed(wid, init_channel=prefix + "BucketListSyncStatus-Mon")
        rb.setOffColor(rb.Red)
        rb.setOnColor(rb.LightGreen)
        lab = QLabel('Sync', wid)
        lab.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab.setAlignment(Qt.AlignCenter)
        vlay = QVBoxLayout()
        lay.addItem(vlay)
        vlay.addWidget(lab)
        vlay.addWidget(rb)

        rb = PyDMLabel(wid, init_channel=prefix + "BucketListLen-Mon")
        rb.setStyleSheet("min-width:4em; max-height:1.15em;")
        rb.setAlignment(Qt.AlignCenter)
        lab = QLabel('Size', wid)
        lab.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab.setAlignment(Qt.AlignCenter)
        vlay = QVBoxLayout()
        lay.addItem(vlay)
        vlay.addWidget(lab)
        vlay.addWidget(rb)

        sp = _MySpinBox(wid, init_channel=prefix + "RepeatBucketList-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(wid, init_channel=prefix + "RepeatBucketList-RB")
        rb.setStyleSheet("min-width:2.5em; max-height:1.15em;")
        rb.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab = QLabel('Repeat', wid, alignment=Qt.AlignCenter)
        vlay = QVBoxLayout()
        hlay = QHBoxLayout()
        lay.addItem(vlay)
        vlay.addWidget(lab)
        vlay.addItem(hlay)
        hlay.addWidget(sp)
        hlay.addWidget(rb)


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 3, 'mode': 6.6, 'delay_type': 4.2, 'delay': 5.2,
        'delayraw': 5.2, 'description': 9.7, 'code': 3.2, 'name': 4.8,
        }
    _LABELS = {
        'ext_trig': 'Trig.', 'mode': 'Mode', 'description': 'Description',
        'delay_type': 'Type', 'delay': 'Delay [us]', 'delayraw': 'Raw Delay',
        'code': 'Code', 'name': 'Name'}
    _ALL_PROPS = (
        'ext_trig', 'name', 'mode', 'delay_type', 'delay', 'delayraw',
        'description', 'code')

    def __init__(self, **kwargs):
        kwargs['props2search'] = set(
            ('name', 'mode', 'delay_type'))
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if prop == 'ext_trig':
            sp = QWidget(self)
            but = PyDMPushButton(
                sp, init_channel=prefix+'ExtTrig-Cmd', pressValue=1)
            but.setIcon(qta.icon('fa5s.step-forward'))
            but.setObjectName('but')
            but.setStyleSheet(
                '#but{min-width:40px; min-height:30px; icon-size:20px;}')
            but.setToolTip('Run event asynchronously')
            hbl = QHBoxLayout(sp)
            hbl.addWidget(but)
        elif prop == 'name':
            sp = QLabel(prefix.propty, self, alignment=Qt.AlignCenter)
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
        elif prop == 'delayraw':
            sp = _MySpinBox(self, init_channel=prefix + "DelayRaw-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "DelayRaw-RB")
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
        'name': 'Name',
        'frequency': 'Freq. [Hz]',
        'mux_div': 'Mux Divisor',
        'mux_enbl': 'Enabled',
        }
    _ALL_PROPS = ('name', 'mux_enbl', 'frequency', 'mux_div')

    def __init__(self, name=None, parent=None, prefix='',
                 props=set(), obj_names=list(), has_search=False):
        """Initialize object."""
        super().__init__(
            name=name, parent=parent, prefix=prefix, props=props,
            obj_names=obj_names, has_search=has_search,
            props2search={'name', 'mux_enbl'})
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
