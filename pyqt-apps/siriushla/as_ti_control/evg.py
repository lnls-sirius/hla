import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from siriuspy.csdevice import timesys as _cstime
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla import util as _util
from siriushla.as_ti_control.base import BaseList, BaseWidget


class EVG(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix=prefix)
        self.setupui()

    def setupui(self):
        mylayout = QGridLayout(self)
        mylayout.setHorizontalSpacing(20)
        mylayout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        mylayout.addWidget(lab, 0, 0, 1, 2)
        mylayout.setAlignment(lab, Qt.AlignCenter)

        scr_ar = QScrollArea(self)
        self.events_wid = EventList(
            name='Events', parent=scr_ar, prefix=self.prefix,
            obj_names=sorted(_cstime.Const.EvtLL._fields[1:]))
        scr_ar.setWidget(self.events_wid)
        scr_ar.setMinimumWidth(1150)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Preferred)
        mylayout.addWidget(scr_ar, 2, 0)

        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            props={'mux_div', 'mux_enbl'},
            obj_names=sorted(_cstime.Const.ClkLL._fields)
            )
        mylayout.addWidget(self.clocks_wid, 2, 1)

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
        self.configs_wid = QGroupBox('Configurations', self)
        mylayout.addWidget(self.configs_wid, 1, 0)
        self._setup_configs_wid()

        self.status_wid = QGroupBox('Status', self)
        mylayout.addWidget(self.status_wid, 1, 1)
        self._setup_status_wid()

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
        rb.setMinimumHeight(40)
        rb.setSizePolicy(QSzPol.Preferred, QSzPol.Minimum)
        layrow.addWidget(self._create_prop_widget(
                        'Dev Enable', self.configs_wid, (sp, rb)))

        sp = PyDMSpinbox(self, init_channel=prefix + "RFDiv-SP")
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
        rb.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'RF Status', self.configs_wid, (sp, rb)))

        sp = PyDMPushButton(
            self, init_channel=prefix+"UpdateEvt-Cmd", pressValue=1,
            label='Update')
        rb = PyDMLed(self, init_channel=prefix + "EvtSyncStatus-Mon")
        rb.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'Update Evts', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMStateButton(self, init_channel=prefix + "ACEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "ACEnbl-Sts")
        rb.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'AC Enable', self.configs_wid, (sp, rb)))

        mon = PyDMLed(self, init_channel=prefix + "ACStatus-Mon")
        mon.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'AC Status', self.configs_wid, (mon,)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMSpinbox(self, init_channel=prefix + "ACDiv-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "ACDiv-RB")
        layrow.addWidget(self._create_prop_widget(
                        'AC Divisor', self.configs_wid, (sp, rb)))

        sp = PyDMECB(self, init_channel=prefix + "ACSrc-Sel")
        rb = PyDMLabel(self, init_channel=prefix + "ACSrc-Sts")
        layrow.addWidget(self._create_prop_widget(
                        'AC Source', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        sp = PyDMSpinbox(self, init_channel=prefix + "RepeatBucketList-SP")
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
        rb.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'Continuous', self.configs_wid, (sp, rb)))

        sp = PyDMStateButton(self, init_channel=prefix + "InjectionEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "InjectionEvt-Sts")
        rb.setMinimumHeight(40)
        layrow.addWidget(self._create_prop_widget(
                        'Injection', self.configs_wid, (sp, rb)))

        # sp = PyDMLineEdit(self, init_channel=prefix + "BucketList-SP")
        # sp.setMaximumHeight(35)
        # # sp.setMinimumWidth(300)
        # sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        # rb = PyDMLabel(self, init_channel=prefix + "BucketList-RB")
        # rb.setMaximumSize(500, 35)
        # # rb.setMinimumWidth(300)
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
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 1)

        lb = QLabel("<b>RF Sts</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "RFStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 2)

        wids = list()
        for i in range(8):
            rb = SiriusLedAlert(self, init_channel=prefix + "Los-Mon", bit=i)
            rb.setMaximumSize(40, 40)
            rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
            wids.append(rb)
        gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False
                )
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


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 150, 'mode': 205, 'delay_type': 130, 'delay': 150,
        'description': 300, 'code': 100,
        }
    _LABELS = {
        'ext_trig': 'Ext. Trig.', 'mode': 'Mode', 'description': 'Description',
        'delay_type': 'Type', 'delay': 'Delay [us]', 'code': 'Code',
        }
    _ALL_PROPS = (
        'ext_trig', 'mode', 'delay_type', 'delay', 'description', 'code')

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if prop == 'ext_trig':
            sp = PyDMPushButton(
                self, init_channel=prefix+'ExtTrig-Cmd', pressValue=1)
            sp.setText(prefix.propty)
        elif prop == 'mode':
            sp = PyDMECB(self, init_channel=prefix + "Mode-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "Mode-Sts")
        elif prop == 'delay_type':
            sp = PyDMECB(self, init_channel=prefix+"DelayType-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"DelayType-Sts")
        elif prop == 'delay':
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
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
    """Template for control of High and Low Level Clocks."""

    _MIN_WIDs = {
        'state': 150,
        'frequency': 150,
        'mux_div': 150,
        'mux_enbl': 150,
        }
    _LABELS = {
        'state': 'Enabled',
        'frequency': 'Freq. [kHz]',
        'mux_div': 'Mux Divisor',
        'mux_enbl': 'Mux Enabled',
        }
    _ALL_PROPS = ('state', 'frequency', 'mux_div', 'mux_enbl')

    def _createObjs(self, prefix, prop):
        if prop == 'state':
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            sp.setText(prefix.propty)
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif prop == 'frequency':
            sp = PyDMSpinbox(self, init_channel=prefix + "Freq-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Freq-RB")
        if prop == 'mux_enbl':
            sp = PyDMCb(self, init_channel=prefix + "MuxEnbl-Sel")
            sp.setText(prefix.propty)
            rb = PyDMLed(self, init_channel=prefix + "MuxEnbl-Sts")
        elif prop == 'mux_div':
            sp = PyDMSpinbox(self, init_channel=prefix + "MuxDiv-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "MuxDiv-RB")
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow
    app = SiriusApplication()
    win = SiriusMainWindow()
    _util.set_style(app)
    evg_ctrl = EVG(prefix='TEST-FAC:TI-EVG:')
    win.setCentralWidget(evg_ctrl)
    win.show()
    sys.exit(app.exec_())
