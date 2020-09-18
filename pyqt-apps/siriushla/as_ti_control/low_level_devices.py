"""."""
import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import QLabel, QPushButton, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QMenuBar, QSplitter, QTabWidget, QWidget, \
    QSizePolicy as QSzPol, QDialog, QLineEdit
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMPushButton, PyDMLineEdit

from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys import csdev as _cstime

from ..widgets import PyDMLed, PyDMStateButton, SiriusLedState, \
    SiriusEnumComboBox as _MyComboBox, SiriusLedAlert, SiriusLabel
from ..widgets.windows import create_window_from_widget
from ..util import connect_window, get_appropriate_color

from .base import BaseList, MySpinBox as _MySpinBox, BaseWidget


# ###################### Event Generator ######################
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
            Win = create_window_from_widget(FOUT, title=down, icon=icon)
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

        tm = 'min-width:{0:d}em; max-width:{0:d}em; max-height:1.15em;'
        sp = BucketListLineEdit(wid, init_channel=prefix + "BucketList-SP")
        self.bucket_ledit = sp
        sp.setStyleSheet(tm.format(self._min_size-1))
        sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('SP : ', wid)
        pushbtn = QPushButton(wid)
        pushbtn.setIcon(qta.icon('mdi.basket-fill'))
        pushbtn.clicked.connect(self._set_bucket_list)
        lay_sp = QHBoxLayout()
        lay_sp.addWidget(lab)
        lay_sp.addWidget(sp)
        lay_sp.addWidget(pushbtn)

        rb = BucketListLabel(wid, init_channel=prefix + "BucketList-RB")
        rb.setStyleSheet(tm.format(self._min_size))
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('RB : ', wid)
        lay_rb = QHBoxLayout()
        lay_rb.addWidget(lab)
        lay_rb.addWidget(rb)
        mn = BucketListLabel(wid, init_channel=prefix + "BucketList-Mon")
        mn.setStyleSheet(tm.format(self._min_size))
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

    def _set_bucket_list(self):

        wid = QDialog(self)
        wid.setObjectName('ASApp')
        lay = QGridLayout()
        wid.setLayout(lay)

        row = 0
        lay.addWidget(QLabel('Start', wid), row, 0)
        start = QLineEdit(wid)
        val = QIntValidator()
        val.setRange(1, 864)
        start.setValidator(val)
        start.setText('1')
        start.setAlignment(Qt.AlignCenter)
        start.setStyleSheet('max-width:5em;')
        lay.addWidget(start, row, 1)

        row += 1
        lay.addWidget(QLabel('Stop', wid), row, 0)
        stop = QLineEdit(wid)
        val = QIntValidator()
        val.setRange(1, 864)
        stop.setValidator(val)
        stop.setText('864')
        stop.setAlignment(Qt.AlignCenter)
        stop.setStyleSheet('max-width:5em;')
        lay.addWidget(stop, row, 1)

        row += 1
        lay.addWidget(QLabel('Step', wid), row, 0)
        step = QLineEdit(wid)
        val = QIntValidator()
        val.setRange(1, 863)
        step.setValidator(val)
        step.setText('50')
        step.setAlignment(Qt.AlignCenter)
        step.setStyleSheet('max-width:5em;')
        lay.addWidget(step, row, 1)

        row += 1
        hlay = QHBoxLayout()
        cancel = QPushButton('Cancel', wid)
        confirm = QPushButton('Ok', wid)
        confirm.setDefault(True)
        cancel.clicked.connect(wid.reject)
        confirm.clicked.connect(wid.accept)
        hlay.addStretch()
        hlay.addWidget(cancel)
        hlay.addStretch()
        hlay.addWidget(confirm)
        hlay.addStretch()
        wid.layout().addItem(hlay, row, 0, 1, 2)
        res = wid.exec_()
        if res != QDialog.Accepted:
            return

        start_ = int(start.text())
        stop_ = int(stop.text())
        step_ = int(step.text())
        lst = list(range(start_, stop_, step_))
        if lst:
            txt = ' '.join(str(i) for i in lst)
            self.bucket_ledit.setText(txt)
            self.bucket_ledit.returnPressed.emit()


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


# ###################### Event Distributors ######################
class FOUT(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix)
        self._setupUi()
        self.setObjectName('ASApp')

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0)
        self._setup_status_wid()

    def _setupmenus(self):
        prefix = self.prefix
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Downlinks')

        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        downs = LLTimeSearch.get_fout2trigsrc_mapping()[prefix.device_name]
        downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
        for out, dwn in downs:
            dev, down = dwn.dev, dwn.device_name
            if dev == 'EVR':
                devt = EVR
            elif dev == 'EVE':
                devt = EVE
            else:
                devt = AFC
            action = menu.addAction(out + ' --> ' + down)
            Win = create_window_from_widget(devt, title=down, icon=icon)
            connect_window(action, Win, None, prefix=down + ':')

        menu = main_menu.addMenu('&Uplink')
        link = list(LLTimeSearch.In2OutMap[prefix.dev])[0]
        evg = LLTimeSearch.get_evg_channel(
            prefix.device_name.substitute(propty=link))
        action = menu.addAction(evg)
        Win = create_window_from_widget(EVG, title=evg.device_name, icon=icon)
        connect_window(action, Win, None, prefix=evg.device_name + ':')
        return main_menu

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False
            )
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Network-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "LinkStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

        wids = list()
        for i in range(8):
            rb = SiriusLedAlert(self, init_channel=prefix + "Los-Mon", bit=i)
            wids.append(rb)
        gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 1, 0, 1, 4)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


# ###################### Event Receivers ######################
class AFC(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix=prefix)
        self.prefix = _PVName(prefix)
        self._setupUi()
        self.setObjectName('ASApp')

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0)
        self._setup_status_wid()

        tab = QTabWidget(self)
        self.my_layout.addWidget(tab, 3, 0)

        props = {
            'name', 'state', 'event', 'source', 'width', 'polarity', 'pulses',
            'delay', 'timestamp'}
        set_ = LLTimeSearch.In2OutMap['AMCFPGAEVR']['SFP8']
        obj_names = sorted([out for out in set_ if out.startswith('FMC')])
        self.fmcs_wid = AFCOUTList(
            name='', parent=self, props=props,
            prefix=self.prefix, obj_names=obj_names)
        self.fmcs_wid.setObjectName('fmcs_wid')
        self.fmcs_wid.setStyleSheet("""#fmcs_wid{min-width:60em;}""")
        tab.addTab(self.fmcs_wid, 'FMC Outputs')

        obj_names = sorted([out for out in set_ if out.startswith('CRT')])
        self.crts_wid = AFCOUTList(
            name='', parent=self, props=props,
            prefix=self.prefix, obj_names=obj_names)
        self.crts_wid.setObjectName('crts_wid')
        self.crts_wid.setStyleSheet("""#crts_wid{min-width:60em;}""")
        tab.addTab(self.crts_wid, 'CRT Outputs')

    def _setupmenus(self):
        prefix = self.prefix
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Uplink')

        fout = LLTimeSearch.get_fout_channel(prefix + 'CRT0')
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(action, Win, None, prefix=fout.device_name+':')
        return main_menu

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False)
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Locked</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "RefClkLocked-Mon")
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "LinkStatus-Mon")
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(Qt.AlignCenter)
        return gb


class _EVR_EVE(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix='', device='EVR'):
        """Initialize object."""
        super().__init__(parent, prefix)
        self.device_type = device
        self.setupui()
        self.setObjectName('ASApp')

    def setupui(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self.setupmenus(), 0, 0, 1, 2)

        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0, 1, 2)
        self._setup_status_wid()

        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        self.my_layout.addWidget(splitter, 3, 0, 1, 2)

        props = {
            'name', 'state', 'event', 'widthraw', 'polarity', 'pulses',
            'delayraw', 'timestamp'}
        self.otps_wid = OTPList(
            name='Internal Trigger (OTP)', parent=self, prefix=self.prefix,
            props=props, obj_names=['OTP{0:02d}'.format(i) for i in range(24)])
        self.otps_wid.setObjectName('otps_wid')
        self.otps_wid.setStyleSheet("""#otps_wid{min-width:60em;}""")
        splitter.addWidget(self.otps_wid)

        props = {
            'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay_type',
            'fine_delayraw'}
        self.outs_wid = OUTList(
            name='OUT', parent=self, prefix=self.prefix, props=props,
            obj_names=['OUT{0:d}'.format(i) for i in range(8)])
        self.outs_wid.setObjectName('outs_wid')
        self.outs_wid.setStyleSheet("""#outs_wid{min-width:44em;}""")
        splitter.addWidget(self.outs_wid)

    def setupmenus(self):
        prefix = self.prefix
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Uplink')

        fout = LLTimeSearch.get_fout_channel(prefix + 'OTP0')
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(action, Win, None, prefix=fout.device_name+':')
        return main_menu

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False)
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Network-Mon")
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "LinkStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

        lb = QLabel("<b>Interlock Status</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "IntlkStatus-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 4)

        lb = QLabel("<b>Interlock Enabled</b>")
        rb = SiriusLedState(self, init_channel=prefix + "IntlkEnbl-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 5)

        if self.device_type == 'EVR':
            wids = list()
            for i in range(8):
                rb = SiriusLedAlert(
                    parent=self, init_channel=prefix + "Los-Mon", bit=i)
                wids.append(rb)
            gb = self._create_small_GB(
                    'Down Connection', self.status_wid, wids, align_ver=False)
        else:
            sp = _MyComboBox(self, init_channel=prefix + "RFOut-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "RFOut-Sts")
            gb = self._create_small_GB('RF Output', self.status_wid, (sp, rb))
        status_layout.addWidget(gb, 0, 6)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


class EVR(_EVR_EVE):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent, prefix, device='EVR')


class EVE(_EVR_EVE):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent, prefix, device='EVE')


# ###################### Triggers ######################
class LLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'name': 3.2,
        'device': 12,
        'state': 5.8,
        'event': 4.8,
        'widthraw': 4.8,
        'width': 4.8,
        'polarity': 5,
        'pulses': 4.8,
        'delayraw': 4.8,
        'delay': 4.8,
        'timestamp': 3.2,
        'source': 6.5,
        'trigger': 4,
        'rf_delayraw': 4.8,
        'rf_delay': 6.5,
        'fine_delayraw': 4.8,
        'fine_delay': 6.5,
        'rf_delay_type': 6.5,
        'hl_trigger': 10,
        'dir': 4,
        'evtcnt': 5,
        'evtcntrst': 4,
        }
    _LABELS = {
        'name': 'Name',
        'device': 'Device',
        'state': 'State',
        'event': 'Event',
        'widthraw': 'Width',
        'width': 'Width [us]',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delayraw': 'Delay',
        'delay': 'Delay [us]',
        'timestamp': 'Log',
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delayraw': 'RF Delay',
        'rf_delay': 'RF Delay [ns]',
        'fine_delayraw': 'Fine Delay',
        'fine_delay': 'Fine Delay [ps]',
        'rf_delay_type': 'RF Delay Type',
        'hl_trigger': 'HL Trigger',
        'dir': 'Direction',
        'evtcnt': 'Evt. Cnt.',
        'evtcntrst': 'Rst. Cnt.',
        }
    _ALL_PROPS = (
        'device', 'name', 'state', 'event', 'widthraw', 'width',
        'polarity', 'pulses', 'delayraw', 'delay', 'timestamp', 'source',
        'trigger', 'rf_delayraw', 'rf_delay', 'rf_delay_type', 'fine_delayraw',
        'fine_delay', 'hl_trigger', 'dir', 'evtcnt', 'evtcntrst')

    def __init__(self, **kwargs):
        srch = set(('device', 'name', 'polarity', 'source', 'dir'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)

    def _createObjs(self, prefix, prop):
        intlb = LLTimeSearch.get_channel_internal_trigger_pvname(prefix)
        outlb = LLTimeSearch.get_channel_output_port_pvname(prefix)
        sp = rb = None
        if prop == 'device':
            devt = outlb.dev
            if devt == 'EVR':
                devt = EVR
            elif devt == 'EVE':
                devt = EVE
            else:
                devt = AFC
            sp = QPushButton(outlb.device_name, self)
            sp.setAutoDefault(False)
            sp.setDefault(False)
            icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
            Win = create_window_from_widget(
                devt, title=outlb.device_name, icon=icon)
            connect_window(sp, Win, None, prefix=outlb.device_name + ':')
        elif prop == 'name':
            sp = QLabel(outlb.propty, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'hl_trigger':
            trig = HLTimeSearch.get_hl_from_ll_triggers(prefix)
            sp = QLabel(trig, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'state':
            pvname = intlb.substitute(propty=intlb.propty+"State-Sel")
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"State-Sts")
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'event':
            pvname = intlb.substitute(propty=intlb.propty+'Evt-SP')
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'Evt-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'widthraw':
            pvname = intlb.substitute(propty=intlb.propty+"WidthRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"WidthRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'width':
            pvname = intlb.substitute(propty=intlb.propty+"Width-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"Width-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'polarity':
            pvname = intlb.substitute(propty=intlb.propty+"Polarity-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"Polarity-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'pulses':
            pvname = intlb.substitute(propty=intlb.propty+"NrPulses-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"NrPulses-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delayraw':
            pvname = intlb.substitute(propty=intlb.propty+"DelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"DelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delay':
            pvname = intlb.substitute(propty=intlb.propty+"Delay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"Delay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'timestamp':
            pvname = intlb.substitute(propty=intlb.propty+"Log-Sel")
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"Log-Sts")
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'source':
            pvname = outlb.substitute(propty=outlb.propty+"Src-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+"Src-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'trigger':
            pvname = outlb.substitute(propty=outlb.propty+"SrcTrig-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"SrcTrig-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"RFDelay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay_type':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayType-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayType-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+"FineDelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"FineDelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delay':
            pvname = outlb.substitute(propty=outlb.propty+"FineDelay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"FineDelay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'dir':
            pvname = intlb.substitute(propty=intlb.propty+"Dir-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"Dir-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'evtcnt':
            pvname = intlb.substitute(propty=intlb.propty+'EvtCnt-Mon')
            sp = PyDMLabel(self, init_channel=pvname)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'evtcntrst':
            pvname = intlb.substitute(propty=intlb.propty+'EvtCntRst-Cmd')
            sp = PyDMPushButton(
                self, icon=qta.icon('fa5s.sync'), label='',
                init_channel=pvname, pressValue=1)
            sp.setObjectName('rst')
            sp.setStyleSheet(
                '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
        if rb is None:
            return (sp, )
        return sp, rb


class OTPList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'widthraw', 'width', 'polarity', 'pulses',
        'delayraw', 'delay', 'evtcnt', 'evtcntrst', 'timestamp', 'hl_trigger')


class OUTList(LLTriggerList):
    """Template for control of Timing Devices Output Channels."""

    _ALL_PROPS = (
        'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay',
        'rf_delay_type', 'fine_delayraw', 'fine_delay', 'hl_trigger')


class AFCOUTList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'source', 'widthraw', 'width', 'polarity',
        'pulses', 'delayraw', 'delay', 'dir', 'evtcnt', 'evtcntrst',
        'timestamp', 'hl_trigger')
    _MIN_WIDs = LLTriggerList._MIN_WIDs
    _MIN_WIDs['name'] = 3.7
