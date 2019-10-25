"""Widget with general functions of DCLink Widgets."""

import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton, \
    QLabel, QSizePolicy as QSzPlcy
import qtawesome as qta
from pydm.widgets import PyDMPushButton, PyDMLabel, PyDMEnumComboBox

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import MASearch, PSSearch
from siriushla.widgets import PyDMStateButton, SiriusLedState, \
    SiriusLedAlert, PyDMLinEditScrollbar, PyDMLedMultiChannel


Dipole = re.compile("^.*:MA-B.*$")
Quadrupole = re.compile("^.*:MA-Q.*$")
QuadrupoleSkew = re.compile("^.*:MA-QS.*$")
Sextupole = re.compile("^.*:MA-S.*$")
Corrector = re.compile("^.*:MA-(CH|CV|FCH|FCV).*$")
IsPulsed = re.compile("^.*:(PU|PM)-.*$")

HasTrim = re.compile("^.*SI-Fam:(PS|MA)-Q.*$")
HasSoftHardIntlk = re.compile("^.*:(PS|MA)-.*$")


def get_analog_name(psname):
    psname = PVName(psname)
    try:
        psmodel = PSSearch.conv_psname_2_psmodel(psname)
        pstype = PSSearch.conv_psname_2_pstype(psname)
    except KeyError:
        pstype = ''
        psmodel = ''

    if 'dclink' in pstype:
        if psmodel == 'FBP_DCLink':
            return 'Voltage'
        elif psmodel in ('FAC_ACDC', 'FAC_2S_ACDC', 'FAC_2P4S_ACDC'):
            return 'CapacitorBankVoltage'
        else:
            raise RuntimeError(
                'Undefined PS model {} setpoint PV name'.format(psmodel))
    else:
        if psname.dis in ['PS', 'MA']:
            return 'Current'
        elif psname.dis in ['PU', 'PM']:
            return 'Voltage'
        else:
            raise RuntimeError(
                'Undefined PS model {} setpoint PV name'.format(psmodel))


def get_strength_name(maname):
    if Dipole.match(maname):
        return "Energy"
    elif Quadrupole.match(maname):
        return "KL"
    elif Sextupole.match(maname):
        return "SL"
    elif Corrector.match(maname):
        return "Kick"
    elif IsPulsed.match(maname):
        return "Kick"
    else:
        raise AttributeError("Magnet name is not defined.")


def get_prop2width(psname):
    detail_wid = '8.5' if psname.dev != 'DCLink' else '3'
    dic = {'detail': detail_wid}
    if psname.dis == 'MA':
        dic.update({'psconn': '4'})
    dic.update({
        'opmode': '8',
        'ctrlmode': '6',
        'state': '6'
    })
    if psname.dis == 'PM':
        dic.update({'pulse': '8'})
    dic.update({
        'intlk':  '5',
        'reset': '4',
        'ctrlloop': '8',
        'setpoint': '6',
        'readback': '6',
        'monitor': '6',
    })
    if psname.dis in ['MA', 'PM']:
        dic.update({
            'strength_sp': '6',
            'strength_rb': '6',
            'strength_mon': '8'
        })
    if HasTrim.match(psname):
        dic.update({'trim': '2'})
    return dic


def get_prop2label(psname):
    dic = {'detail': 'Detail'}
    if psname.dis == 'MA':
        dic.update({'psconn': 'PSConn'})
    dic.update({
        'opmode': 'OpMode',
        'ctrlmode': 'Control Mode',
        'state': 'PwrState'
    })
    if psname.dis == 'PM':
        dic.update({'pulse': 'Pulse'})
    dic.update({
        'intlk':  'Interlocks',
        'reset': 'Reset'
    })
    if psname.dis == 'MA':
        name = MASearch.conv_maname_2_psnames(psname)
        analog = get_analog_name(name[0])
    else:
        analog = get_analog_name(psname)
    if 'CapacitorBank' in analog:
        analog = 'Voltage'
    dic.update({
        'ctrlloop': 'Control Loop',
        'setpoint': analog + '-SP',
        'readback': analog + '-RB',
        'monitor': analog + '-Mon',
    })

    if psname.dis in ['MA', 'PM']:
        strength = get_strength_name(psname)
        dic.update({
            'strength_sp': strength + '-SP',
            'strength_rb': strength + '-RB',
            'strength_mon': strength + '-Mon'
        })
    if HasTrim.match(psname):
        dic.update({'trim': 'Trim'})
    return dic


class SummaryWidget(QWidget):
    """General widget for controlling a power supply."""

    def __init__(self, name, visible_props, parent=None):
        """Build UI with dclink name."""
        super().__init__(parent)
        self._name = PVName(name)
        self.visible_props = visible_props
        self._prefixed_name = VACA_PREFIX + name
        self._is_magnet = True if self._name.dis in ['MA', 'PM'] else False

        if self._is_magnet:
            psnames = MASearch.conv_maname_2_psnames(name)
            self._analog_name = get_analog_name(psnames[0])
            self._strength_name = get_strength_name(self._name)
        else:
            self._analog_name = get_analog_name(self._name)
        self._has_softhard_intlk = HasSoftHardIntlk.match(self._name)
        self._has_trim = HasTrim.match(self._name)

        self._create_pvs()
        self._setup_ui()

    @property
    def devname(self):
        """PS name."""
        return self._name

    def _setup_ui(self):
        """Setups widget UI."""
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        self._widgets_dict = dict()

        if self._name.dev != 'DCLink':
            self.detail_bt = QPushButton(self._name, self)
        else:
            self.detail_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            self.detail_bt.setToolTip(self._name)
        self.detail_wid = self._build_widget(
            [self.detail_bt, ], orientation='v', name='detail')
        self._widgets_dict['detail'] = self.detail_wid
        lay.addWidget(self.detail_wid)

        if self._name.dis == 'MA':
            self.psconn_led = SiriusLedState(self, self._psconn_mon)
            self.psconn_led.setOffColor(SiriusLedAlert.Red)
            self.psconn_wid = self._build_widget(
                [self.psconn_led, ], name='psconn')
            self._widgets_dict['psconn'] = self.psconn_wid
            lay.addWidget(self.psconn_wid)

        opmode_list = list()
        if 'Voltage' not in self._analog_name:
            self.opmode_cb = MyComboBox(self, self._opmode_sel)
            opmode_list.append(self.opmode_cb)
        self.opmode_lb = PyDMLabel(self, self._opmode_sts)
        opmode_list.append(self.opmode_lb)
        self.opmode_wid = self._build_widget(
            opmode_list, orientation='v', name='opmode')
        self._widgets_dict['opmode'] = self.opmode_wid
        lay.addWidget(self.opmode_wid)

        self.ctrlmode_lb = PyDMLabel(self, self._ctrlmode_sts)
        self.ctrlmode_wid = self._build_widget(
            [self.ctrlmode_lb, ], orientation='v', name='ctrlmode')
        self._widgets_dict['ctrlmode'] = self.ctrlmode_wid
        lay.addWidget(self.ctrlmode_wid)

        self.state_bt = PyDMStateButton(self, self._pwrstate_sel)
        self.state_led = SiriusLedState(self, self._pwrstate_sts)
        self.state_wid = self._build_widget(
            [self.state_bt, self.state_led], name='state')
        self._widgets_dict['state'] = self.state_wid
        lay.addWidget(self.state_wid)

        if self._name.dis == 'PM':
            self.pulse_bt = PyDMStateButton(self, self._pulse_sel)
            self.pulse_led = SiriusLedState(self, self._pulse_sts)
            self.pulse_wid = self._build_widget(
                [self.pulse_bt, self.pulse_led], name='pulse')
            self._widgets_dict['pulse'] = self.pulse_wid
            lay.addWidget(self.pulse_wid)

        if self._has_softhard_intlk:
            self.soft_intlk_led = SiriusLedAlert(self, self._soft_intlk)
            self.hard_intlk_led = SiriusLedAlert(self, self._hard_intlk)
            self.intlk_wid = self._build_widget(
                [self.soft_intlk_led, self.hard_intlk_led], name='intlk')
            self._widgets_dict['intlk'] = self.intlk_wid
        else:
            self.intlk_led = PyDMLedMultiChannel(
                self, channels2values={ch: 1 for ch in self._intlk})
            self.intlk_wid = self._build_widget(
                [self.intlk_led, ], name='intlk')
            self._widgets_dict['intlk'] = self.intlk_wid
        lay.addWidget(self.intlk_wid)

        self.reset_bt = PyDMPushButton(
            parent=self, init_channel=self._reset_intlk, pressValue=1)
        self.reset_bt.setIcon(qta.icon('fa5s.sync'))
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        self.reset_wid = self._build_widget([self.reset_bt, ], name='reset')
        self._widgets_dict['reset'] = self.reset_wid
        lay.addWidget(self.reset_wid)

        self.ctrlloop_bt = PyDMStateButton(
            self, self._ctrlloop_sel, invert=True)
        self.ctrlloop_lb = PyDMLabel(self, self._ctrlloop_sts)
        self.ctrlloop_wid = self._build_widget(
            [self.ctrlloop_bt, self.ctrlloop_lb], name='ctrlloop')
        self._widgets_dict['ctrlloop'] = self.ctrlloop_wid
        lay.addWidget(self.ctrlloop_wid)

        self.setpoint = PyDMLinEditScrollbar(self._analog_sp, self)
        self.setpoint.sp_scrollbar.setTracking(False)
        self.setpoint_wid = self._build_widget(
            [self.setpoint, ], orientation='v', name='setpoint')
        self._widgets_dict['setpoint'] = self.setpoint_wid
        lay.addWidget(self.setpoint_wid)

        self.readback = PyDMLabel(self, self._analog_rb)
        self.readback_wid = self._build_widget(
            [self.readback, ], orientation='v', name='readback')
        self._widgets_dict['readback'] = self.readback_wid
        lay.addWidget(self.readback_wid)

        self.monitor = PyDMLabel(self, self._analog_mon)
        self.monitor_wid = self._build_widget(
            [self.monitor, ], orientation='v', name='monitor')
        self._widgets_dict['monitor'] = self.monitor_wid
        lay.addWidget(self.monitor_wid)

        if self._is_magnet:
            self.strength_sp_le = PyDMLinEditScrollbar(
                parent=self, channel=self._strength_sp)
            self.strength_sp_le.sp_scrollbar.setTracking(False)
            self.strength_sp_wid = self._build_widget(
                [self.strength_sp_le, ], orientation='v', name='strength_sp')
            self._widgets_dict['strength_sp'] = self.strength_sp_wid
            lay.addWidget(self.strength_sp_wid)

            self.strength_rb_lb = PyDMLabel(
                parent=self, init_channel=self._strength_rb)
            self.strength_rb_lb.showUnits = True
            self.strength_rb_wid = self._build_widget(
                [self.strength_rb_lb, ], orientation='v', name='strength_rb')
            self._widgets_dict['strength_rb'] = self.strength_rb_wid
            lay.addWidget(self.strength_rb_wid)

            self.strength_mon_lb = PyDMLabel(
                parent=self, init_channel=self._strength_mon)
            self.strength_mon_lb.showUnits = True
            self.strength_mon_wid = self._build_widget(
                [self.strength_mon_lb, ], orientation='v', name='strength_mon')
            self._widgets_dict['strength_mon'] = self.strength_mon_wid
            lay.addWidget(self.strength_mon_wid)

        # Add trim button
        if self._has_trim:
            self.trim_bt = QPushButton(qta.icon('fa5s.angle-right'), '', self)
            self.trim_wid = self._build_widget(
                [self.trim_bt, ], orientation='v', name='trim')
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

        if self._is_magnet:
            st = self._strength_name
            self._strength_sp = self._prefixed_name + ':{}-SP'.format(st)
            self._strength_rb = self._prefixed_name + ':{}-RB'.format(st)
            self._strength_mon = self._prefixed_name + ':{}-Mon'.format(st)
            if self._name.dis == 'MA':
                self._psconn_mon = self._prefixed_name + ':PSConnStatus-Mon'
            elif self._name.dis == 'PM':
                self._pulse_sel = self._prefixed_name + ':Pulse-Sel'
                self._pulse_sts = self._prefixed_name + ':Pulse-Sts'

    def _build_widget(self, widgets, orientation='h', name=''):
        widget = QWidget(self)
        widget.setObjectName(name)
        if orientation == 'h':
            lay = QHBoxLayout(widget)
        else:
            lay = QVBoxLayout(widget)
        for w in widgets:
            lay.addWidget(w)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        return widget

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
        index = self.opmode_cb.findText('SlowRef')
        self.opmode_cb.internal_combo_box_activated_int(index)

    def turn_on(self):
        """Turn power supply on."""
        if not self.state_bt.value:
            self.state_bt.send_value()

    def turn_off(self):
        """Turn power supply off."""
        if self.state_bt.value:
            self.state_bt.send_value()

    def reset(self):
        """Reset power supply."""
        self.reset_bt.sendValue()


class SummaryHeader(QWidget):

    def __init__(self, name, visible_props, parent=None):
        """Build UI."""
        super().__init__(parent)
        self._name = PVName(name)
        self.visible_props = visible_props
        self._setup_ui()

    def _setup_ui(self):
        _widths = get_prop2width(self._name)
        _labels = get_prop2label(self._name)

        lay = QHBoxLayout()
        lay.setSpacing(10)
        lay.setContentsMargins(0, 0, 0, 0)

        if self._name.dis in ['PS', 'MA'] and 'DCLink' not in self._name.dev:
            hidden = QLabel(' ')
            hidden.setObjectName('HiddenButton')
            hidden.setStyleSheet('min-width: 10px; max-width: 10px;')
            lay.addWidget(hidden)
        for idt, label in _labels.items():
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
    visible_props = {'detail', 'opmode', 'state', 'intlk', 'reset',
                     'setpoint', 'monitor'}

    w = QWidget()
    lay = QVBoxLayout(w)
    lay.addWidget(SummaryHeader(name, visible_props))
    lay.addWidget(SummaryWidget(name, visible_props))
    w.show()
    sys.exit(app.exec_())
