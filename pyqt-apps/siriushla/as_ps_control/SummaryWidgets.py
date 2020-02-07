"""Widget with general functions of DCLink Widgets."""

import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton, \
    QLabel, QSizePolicy as QSzPlcy
import qtawesome as qta
from pydm.widgets import PyDMPushButton, PyDMLabel, PyDMEnumComboBox

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import PSSearch
from siriushla.widgets import PyDMStateButton, SiriusLedState, \
    SiriusLedAlert, PyDMLinEditScrollbar, PyDMLedMultiChannel


Dipole = re.compile("^.*:PS-B.*$")
Quadrupole = re.compile("^.*:PS-Q.*$")
QuadrupoleSkew = re.compile("^.*:PS-QS.*$")
Sextupole = re.compile("^.*:PS-S.*$")
Corrector = re.compile("^.*:PS-(CH|CV|FCH|FCV).*$")
IsPulsed = re.compile("^.*:PU-.*$")
IsDCLink = re.compile("^.*:PS-DCLink.*$")

HasTrim = re.compile("^.*SI-Fam:PS-Q.*$")
HasSoftHardIntlk = re.compile("^.*:PS-.*$")


def get_analog_name(psname):
    psname = PVName(psname)
    psmodel = PSSearch.conv_psname_2_psmodel(psname)
    try:
        pstype = PSSearch.conv_psname_2_pstype(psname)
    except KeyError:
        pstype = ''

    if 'dclink' in pstype:
        if psmodel == 'FBP_DCLink':
            return 'Voltage'
        elif psmodel in {'FAC_ACDC', 'FAC_2S_ACDC', 'FAC_2P4S_ACDC'}:
            return 'CapacitorBankVoltage'
        else:
            raise RuntimeError(
                'Undefined PS model {} setpoint PV name'.format(psmodel))
    elif psmodel == 'REGATRON_DCLink':
        return 'Voltage'
    else:
        if psname.dis == 'PS':
            return 'Current'
        elif psname.dis == 'PU':
            return 'Voltage'
        else:
            raise RuntimeError(
                'Undefined PS model {} setpoint PV name'.format(psmodel))


def get_strength_name(psname):
    if Dipole.match(psname):
        return "Energy"
    elif Quadrupole.match(psname):
        return "KL"
    elif Sextupole.match(psname):
        return "SL"
    elif Corrector.match(psname):
        return "Kick"
    elif IsPulsed.match(psname):
        return "Kick"
    else:
        return


def get_prop2width(psname):
    detail_wid = '8.5' if psname.dev != 'DCLink' else '3'
    dic = {
        'detail': detail_wid,
        'state': '6',
        'intlk':  '5',
        'setpoint': '6',
        'readback': '6',
        'monitor': '6',
    }
    if psname.sec != 'LI':
        dic.update({
            'bbb': 10,
            'udc': 10,
            'opmode': '8',
            'ctrlmode': '6',
            'reset': '4',
            'ctrlloop': '8',
        })
    else:
        dic['conn'] = '5'
    if get_strength_name(psname):
        dic.update({
            'strength_sp': '6',
            'strength_rb': '6',
            'strength_mon': '8'
        })
    if psname.dis == 'PU':
        dic.update({'pulse': '8'})
    if HasTrim.match(psname):
        dic.update({'trim': '2'})
    return sort_propties(dic)


def get_prop2label(psname):
    analog = get_analog_name(psname)
    if 'CapacitorBank' in analog:
        analog = 'Voltage'
    dic = {
        'detail': 'Detail',
        'state': 'PwrState',
        'intlk': 'Interlocks',
        'setpoint': analog + '-SP',
        'readback': analog + '-RB',
        'monitor': analog + '-Mon',
    }
    if psname.sec != 'LI':
        dic.update({
            'bbb': 'Beagle Bone',
            'udc': 'UDC',
            'opmode': 'OpMode',
            'ctrlmode': 'Control Mode',
            'reset': 'Reset',
            'ctrlloop': 'Control Loop',
        })
    else:
        dic['conn'] = 'Connected'
    strength = get_strength_name(psname)
    if strength:
        dic.update({
            'strength_sp': strength + '-SP',
            'strength_rb': strength + '-RB',
            'strength_mon': strength + '-Mon'})
    if psname.dis == 'PU':
        dic.update({'pulse': 'Pulse'})
    if HasTrim.match(psname):
        dic.update({'trim': 'Trim'})
    return sort_propties(dic)


def sort_propties(labels):
    default_order = (
        'detail', 'bbb', 'udc', 'opmode', 'ctrlmode', 'state', 'pulse',
        'conn', 'intlk', 'reset', 'ctrlloop', 'setpoint',
        'readback', 'monitor', 'strength_sp', 'strength_rb', 'strength_mon',
        'trim')
    idcs = list()
    for lbl in labels:
        idcs.append(default_order.index(lbl))
    if isinstance(labels, list):
        return [x for _, x in sorted(zip(idcs, labels))]
    elif isinstance(labels, dict):
        return {x: labels[x] for _, x in sorted(zip(idcs, labels.keys()))}


class SummaryWidget(QWidget):
    """General widget for controlling a power supply."""

    def __init__(self, name, visible_props, parent=None):
        """Build UI with dclink name."""
        super().__init__(parent)
        self._name = PVName(name)
        self.visible_props = sort_propties(visible_props)
        self.filled_widgets = set()
        self._prefixed_name = VACA_PREFIX + name
        self._is_pulsed = self._name.dis == 'PU'
        self._analog_name = get_analog_name(self._name)
        self._strength_name = get_strength_name(self._name)
        self._has_softhard_intlk = HasSoftHardIntlk.match(self._name)
        self._has_trim = HasTrim.match(self._name)
        self._is_dclink = IsDCLink.match(self._name)
        self._bbb_name = ''
        self._udc_name = ''
        if not self._is_pulsed:
            self._bbb_name = PSSearch.conv_psname_2_bbbname(self._name)
            self._udc_name = PSSearch.conv_psname_2_udc(self._name)

        self._create_pvs()
        self._setup_ui()

    @property
    def devname(self):
        """PS name."""
        return self._name

    @property
    def bbbname(self):
        """BBB name."""
        return self._bbb_name

    @property
    def udcname(self):
        """UDC name."""
        return self._udc_name

    def _setup_ui(self):
        """Setups widget UI."""
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        self._widgets_dict = dict()

        self.detail_wid = self._build_widget(name='detail', orientation='v')
        self._widgets_dict['detail'] = self.detail_wid
        lay.addWidget(self.detail_wid)

        self.bbb_wid = self._build_widget(name='bbb', orientation='v')
        self._widgets_dict['bbb'] = self.bbb_wid
        lay.addWidget(self.bbb_wid)

        self.udc_wid = self._build_widget(name='udc', orientation='v')
        self._widgets_dict['udc'] = self.udc_wid
        lay.addWidget(self.udc_wid)

        self.opmode_wid = self._build_widget(name='opmode', orientation='v')
        self._widgets_dict['opmode'] = self.opmode_wid
        lay.addWidget(self.opmode_wid)

        self.ctrlmode_wid = self._build_widget(
            name='ctrlmode', orientation='v')
        self._widgets_dict['ctrlmode'] = self.ctrlmode_wid
        lay.addWidget(self.ctrlmode_wid)

        self.state_wid = self._build_widget(name='state')
        self._widgets_dict['state'] = self.state_wid
        lay.addWidget(self.state_wid)

        if self._is_pulsed:
            self.pulse_wid = self._build_widget(name='pulse')
            self._widgets_dict['pulse'] = self.pulse_wid
            lay.addWidget(self.pulse_wid)

        self.intlk_wid = self._build_widget(name='intlk')
        self._widgets_dict['intlk'] = self.intlk_wid
        lay.addWidget(self.intlk_wid)

        self.reset_wid = self._build_widget(name='reset')
        self._widgets_dict['reset'] = self.reset_wid
        lay.addWidget(self.reset_wid)

        self.ctrlloop_wid = self._build_widget(name='ctrlloop')
        self._widgets_dict['ctrlloop'] = self.ctrlloop_wid
        lay.addWidget(self.ctrlloop_wid)

        self.setpoint_wid = self._build_widget(
            name='setpoint', orientation='v')
        self._widgets_dict['setpoint'] = self.setpoint_wid
        lay.addWidget(self.setpoint_wid)

        self.readback_wid = self._build_widget(
            name='readback', orientation='v')
        self._widgets_dict['readback'] = self.readback_wid
        lay.addWidget(self.readback_wid)

        self.monitor_wid = self._build_widget(
            name='monitor', orientation='v')
        self._widgets_dict['monitor'] = self.monitor_wid
        lay.addWidget(self.monitor_wid)

        if not self._is_dclink:
            self.strength_sp_wid = self._build_widget(
                name='strength_sp', orientation='v')
            self._widgets_dict['strength_sp'] = self.strength_sp_wid
            lay.addWidget(self.strength_sp_wid)

            self.strength_rb_wid = self._build_widget(
                name='strength_rb', orientation='v')
            self._widgets_dict['strength_rb'] = self.strength_rb_wid
            lay.addWidget(self.strength_rb_wid)

            self.strength_mon_wid = self._build_widget(
                name='strength_mon', orientation='v')
            self._widgets_dict['strength_mon'] = self.strength_mon_wid
            lay.addWidget(self.strength_mon_wid)

        # Add trim button
        if self._has_trim:
            self.trim_wid = self._build_widget(name='trim', orientation='v')
            self._widgets_dict['trim'] = self.trim_wid
            lay.addWidget(self.trim_wid)

        _widths = get_prop2width(self._name)
        for name, widget in self._widgets_dict.items():
            width = _widths[name]
            widget.setStyleSheet(
                '#'+name+'{min-width:'+str(width)+'em;'
                'max-width:'+str(width)+'em;}')
            widget.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
            widget.setVisible(name in self.visible_props)

        self.setStyleSheet("""
            PyDMStateButton{
                min-width: 2.5em; max-width: 2.5em;
                min-height: 1.5em; max-height: 1.5em;
            }
            QLed{
                min-width: 1.5em; max-width: 1.5em;
                min-height: 1.5em; max-height: 1.5em;
            }
            QLabel{
                min-height: 1.5em; max-height: 1.5em;
                qproperty-alignment: AlignCenter;
            }
        """)

        lay.addStretch()
        self.setLayout(lay)

        for prop in self.visible_props:
            self.fillWidget(prop)

    def _create_pvs(self):
        self._opmode_sel = self._prefixed_name + ':OpMode-Sel'
        self._opmode_sts = self._prefixed_name + ':OpMode-Sts'
        self._ctrlmode_sts = self._prefixed_name + ':CtrlMode-Mon'
        self._pwrstate_sel = self._prefixed_name + ':PwrState-Sel'
        self._pwrstate_sts = self._prefixed_name + ':PwrState-Sts'
        self._ctrlloop_sel = self._prefixed_name + ':CtrlLoop-Sel'
        self._ctrlloop_sts = self._prefixed_name + ':CtrlLoop-Sts'

        if self._has_softhard_intlk:
            self._soft_intlk = self._prefixed_name + ':IntlkSoft-Mon'
            self._hard_intlk = self._prefixed_name + ':IntlkHard-Mon'
        else:
            self._intlk = list()
            for i in range(1, 8):
                self._intlk.append(self._prefixed_name+":Intlk"+str(i)+"-Mon")
            if 'Sept' not in self._name.dev:
                self._intlk.append(self._prefixed_name+":Intlk8-Mon")
        self._reset_intlk = self._prefixed_name + ':Reset-Cmd'

        sp = self._analog_name
        self._analog_sp = self._prefixed_name + ':{}-SP'.format(sp)
        self._analog_rb = self._prefixed_name + ':{}-RB'.format(sp)
        self._analog_mon = self._prefixed_name + ':{}-Mon'.format(sp)

        st = self._strength_name
        self._strength_sp = self._prefixed_name + ':{}-SP'.format(st)
        self._strength_rb = self._prefixed_name + ':{}-RB'.format(st)
        self._strength_mon = self._prefixed_name + ':{}-Mon'.format(st)

        if self._is_pulsed:
            self._pulse_sel = self._prefixed_name + ':Pulse-Sel'
            self._pulse_sts = self._prefixed_name + ':Pulse-Sts'

    def _build_widget(self, name='', orientation='h'):
        widget = QWidget(self)
        widget.setObjectName(name)
        if orientation == 'h':
            lay = QHBoxLayout(widget)
        else:
            lay = QVBoxLayout(widget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        return widget

    def fillWidget(self, name):
        if name in self.filled_widgets:
            return
        if name == 'detail':
            if self._name.dev != 'DCLink':
                self.detail_bt = QPushButton(self._name, self)
            else:
                self.detail_bt = QPushButton(
                    qta.icon('fa5s.list-ul'), '', self)
                self.detail_bt.setToolTip(self._name)
            self.detail_wid.layout().addWidget(self.detail_bt)
        elif name == 'bbb':
            self.bbb_lb = QLabel(self._bbb_name, self)
            self.bbb_wid.layout().addWidget(self.bbb_lb)
        elif name == 'udc':
            self.udc_lb = QLabel(self._udc_name, self)
            self.udc_wid.layout().addWidget(self.udc_lb)
        elif name == 'opmode':
            opmode_list = list()
            if 'Voltage' not in self._analog_name:
                self.opmode_cb = MyComboBox(self, self._opmode_sel)
                opmode_list.append(self.opmode_cb)
            self.opmode_lb = PyDMLabel(self, self._opmode_sts)
            opmode_list.append(self.opmode_lb)
            for wid in opmode_list:
                self.opmode_wid.layout().addWidget(wid)
        elif name == 'ctrlmode':
            self.ctrlmode_lb = PyDMLabel(self, self._ctrlmode_sts)
            self.ctrlmode_wid.layout().addWidget(self.ctrlmode_lb)
        elif name == 'state':
            self.state_bt = PyDMStateButton(self, self._pwrstate_sel)
            self.state_led = SiriusLedState(self, self._pwrstate_sts)
            self.state_wid.layout().addWidget(self.state_bt)
            self.state_wid.layout().addWidget(self.state_led)
        elif name == 'pulse' and self._is_pulsed:
            self.pulse_bt = PyDMStateButton(self, self._pulse_sel)
            self.pulse_led = SiriusLedState(self, self._pulse_sts)
            self.pulse_wid.layout().addWidget(self.pulse_bt)
            self.pulse_wid.layout().addWidget(self.pulse_led)
        elif name == 'intlk':
            if self._has_softhard_intlk:
                self.soft_intlk_led = SiriusLedAlert(self, self._soft_intlk)
                self.hard_intlk_led = SiriusLedAlert(self, self._hard_intlk)
                self.intlk_wid.layout().addWidget(self.soft_intlk_led)
                self.intlk_wid.layout().addWidget(self.hard_intlk_led)
            else:
                self.intlk_led = PyDMLedMultiChannel(
                    self, channels2values={ch: 1 for ch in self._intlk})
                self.intlk_wid.layout().addWidget(self.intlk_led)
        elif name == 'reset':
            self.reset_bt = PyDMPushButton(
                parent=self, init_channel=self._reset_intlk, pressValue=1)
            self.reset_bt.setIcon(qta.icon('fa5s.sync'))
            self.reset_bt.setObjectName('reset_bt')
            self.reset_bt.setStyleSheet(
                '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')
            self.reset_wid.layout().addWidget(self.reset_bt)
        elif name == 'ctrlloop':
            self.ctrlloop_bt = PyDMStateButton(
                self, self._ctrlloop_sel, invert=True)
            self.ctrlloop_lb = PyDMLabel(self, self._ctrlloop_sts)
            self.ctrlloop_wid.layout().addWidget(self.ctrlloop_bt)
            self.ctrlloop_wid.layout().addWidget(self.ctrlloop_lb)
        elif name == 'setpoint':
            self.setpoint = PyDMLinEditScrollbar(self._analog_sp, self)
            self.setpoint.sp_scrollbar.setTracking(False)
            self.setpoint_wid.layout().addWidget(self.setpoint)
        elif name == 'readback':
            self.readback = PyDMLabel(self, self._analog_rb)
            self.readback_wid.layout().addWidget(self.readback)
        elif name == 'monitor':
            self.monitor = PyDMLabel(self, self._analog_mon)
            self.monitor_wid.layout().addWidget(self.monitor)
        elif name == 'strength_sp' and not self._is_dclink:
            self.strength_sp_le = PyDMLinEditScrollbar(
                parent=self, channel=self._strength_sp)
            self.strength_sp_le.sp_scrollbar.setTracking(False)
            self.strength_sp_wid.layout().addWidget(self.strength_sp_le)
        elif name == 'strength_rb' and not self._is_dclink:
            self.strength_rb_lb = PyDMLabel(
                parent=self, init_channel=self._strength_rb)
            self.strength_rb_lb.showUnits = True
            self.strength_rb_wid.layout().addWidget(self.strength_rb_lb)
        elif name == 'strength_mon' and not self._is_dclink:
            self.strength_mon_lb = PyDMLabel(
                parent=self, init_channel=self._strength_mon)
            self.strength_mon_lb.showUnits = True
            self.strength_mon_wid.layout().addWidget(self.strength_mon_lb)
        elif name == 'trim' and self._has_trim:
            self.trim_bt = QPushButton(qta.icon('fa5s.angle-right'), '', self)
            self.trim_wid.layout().addWidget(self.trim_bt)
        self.filled_widgets.add(name)

    def get_detail_button(self):
        """Return psname button."""
        return self.detail_bt

    def get_trim_button(self):
        """Return trim button."""
        if self._has_trim:
            return self.trim_bt
        return None

    def set_opmode_slowref(self):
        """Set power supply OpMode to SlowRef."""
        if self.opmode_cb.isEnabled():
            index = self.opmode_cb.findText('SlowRef')
            self.opmode_cb.internal_combo_box_activated_int(index)

    def turn_on(self):
        """Turn power supply on."""
        if self.state_bt.isEnabled():
            if not self.state_bt.value:
                self.state_bt.send_value()

    def turn_off(self):
        """Turn power supply off."""
        if self.state_bt.isEnabled():
            if self.state_bt.value:
                self.state_bt.send_value()

    def pulse_on(self):
        """Turn power supply on."""
        if self.pulse_bt.isEnabled():
            if not self.pulse_bt.value:
                self.pulse_bt.send_value()

    def pulse_off(self):
        """Turn power supply off."""
        if self.pulse_bt.isEnabled():
            if self.pulse_bt.value:
                self.pulse_bt.send_value()

    def reset(self):
        """Reset power supply."""
        if self.reset_bt.isEnabled():
            self.reset_bt.sendValue()


class SummaryHeader(QWidget):

    def __init__(self, name, visible_props, parent=None):
        """Build UI."""
        super().__init__(parent)
        self._name = PVName(name)
        self.all_props = get_prop2label(self._name)
        self.visible_props = sort_propties(visible_props)
        self._setup_ui()

    def _setup_ui(self):
        _widths = get_prop2width(self._name)

        lay = QHBoxLayout()
        lay.setSpacing(10)
        lay.setContentsMargins(0, 0, 0, 0)

        if self._name.dis == 'PS' and 'DCLink' not in self._name.dev:
            hidden = QLabel(' ')
            hidden.setObjectName('HiddenButton')
            hidden.setStyleSheet('min-width: 10px; max-width: 10px;')
            lay.addWidget(hidden)
        for idt, label in self.all_props.items():
            widget = QLabel(label, self)
            widget.setObjectName(idt)
            width = _widths[idt]
            widget.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Preferred)
            widget.setStyleSheet(
                'font-weight: bold; qproperty-alignment: AlignCenter;'
                'min-width: {0}em; max-width: {0}em;'.format(width))
            widget.setVisible(idt in self.visible_props)
            lay.addWidget(widget)
        lay.addStretch()
        self.setLayout(lay)

    def update_visible_props(self, new_value):
        self.visible_props = sort_propties(new_value)


class MyComboBox(PyDMEnumComboBox):
    """Subclass PyDMEnumComboBox to reimplement whellEvent."""

    def __init__(self, parent, init_channel=None):
        """Initialize object."""
        super().__init__(parent=parent, init_channel=init_channel)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()

    # name = 'PA-RaPSF01:PS-DCLink-BO'
    # name = 'BO-Fam:MA-B'
    name = 'BO-Fam:PS-B-1'
    visible_props = sort_propties(
        ['detail', 'opmode', 'state', 'intlk', 'reset',
         'setpoint', 'monitor'])

    w = QWidget()
    lay = QVBoxLayout(w)
    lay.addWidget(SummaryHeader(name, visible_props))
    lay.addWidget(SummaryWidget(name, visible_props))
    w.show()
    sys.exit(app.exec_())
