import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy as QSzPol
from pydm.widgets.label import PyDMLabel
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.spinbox import PyDMSpinbox
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util
from siriushla.as_ti_control.base_list import BaseList


class _EVR_EVE(SiriusMainWindow):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix='', device='EVR'):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.device_type = device
        self._setupUi()

    def _setupUi(self):
        # self.resize(2000, 2000)
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        NUM_OTP = 24 if self.device_type == 'EVR' else 16
        scr_ar = QScrollArea(cw)
        # scr_ar.setSizePolicy(QSzPol.)
        self.otps_wid = OTPList(
            name='Internal Trigger (OTP)', parent=scr_ar, prefix=self.prefix,
            obj_names=['OTP{0:02d}'.format(i) for i in range(NUM_OTP)]
            )
        scr_ar.setWidget(self.otps_wid)
        scr_ar.setMinimumWidth(1240)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Preferred)
        self.my_layout.addWidget(scr_ar, 2, 0)

        self.outs_wid = OUTList(
            name='OUT', parent=self, prefix=self.prefix,
            obj_names=['OUT{0:d}'.format(i) for i in range(8)]
            )
        self.my_layout.addWidget(self.outs_wid, 2, 1)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 1, 0, 1, 2)
        self._setup_status_wid()

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        rb.setMinimumHeight(40)
        rb.setSizePolicy(QSzPol.Preferred, QSzPol.Minimum)
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
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Link-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

        lb = QLabel("<b>Interlock</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Intlk-Mon")
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 4)

        if self.device_type == 'EVR':
            wids = list()
            for i in range(8):
                rb = SiriusLedAlert(
                    self, init_channel=prefix + "Los-Mon", bit=i
                    )
                rb.setMaximumSize(40, 40)
                rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
                wids.append(rb)
            gb = self._create_small_GB(
                    'Down Connection', self.status_wid, wids, align_ver=False
                    )
        else:
            sp = PyDMECB(self, init_channel=prefix + "RFOut-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "RFOut-Sts")
            gb = self._create_small_GB('RF Output', self.status_wid, (sp, rb))
        status_layout.addWidget(gb, 0, 5)

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


class OTPList(BaseList):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'state': 200,
        'event': 100,
        'width': 150,
        'polarity': 70,
        'pulses': 70,
        'delay': 150,
        }
    _LABELS = {
        'state': 'State',
        'event': 'Event',
        'width': 'Width',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delay': 'Delay',
        }
    _ALL_PROPS = (
        'state', 'event', 'width', 'polarity', 'pulses', 'delay',
        )

    def _createObjs(self, prefix, prop):
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + 'Evt-RB')
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        return sp, rb


class OUTList(BaseList):
    """Template for control of Timing Devices Output Channels."""

    _MIN_WIDs = {
        'interlock': 200,
        'source': 200,
        'trigger': 200,
        'rf_delay': 150,
        'fine_delay': 150,
        }
    _LABELS = {
        'interlock': 'Interlock',
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delay': 'RF Delay',
        'fine_delay': 'Fine Delay',
        }
    _ALL_PROPS = (
        'interlock', 'source', 'trigger', 'rf_delay', 'fine_delay',
        )

    def _createObjs(self, prefix, prop):
        if 'interlock' == prop:
            sp = PyDMCb(self, init_channel=prefix + "Intlk-Sel")
            rb = PyDMLed(self, init_channel=prefix + "Intlk-Sts")
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix+"Src-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "Src-Sts")
        elif 'trigger' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "SrcTrig-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "SrcTrig-RB")
        elif 'rf_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "RFDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "RFDelay-RB")
        elif 'fine_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "FineDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "FineDelay-RB")
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.envars import vaca_prefix
    app = SiriusApplication()
    _util.set_style(app)
    evr_ctrl = EVR(prefix=vaca_prefix+'AS-Glob:TI-EVR-1:')
    evr_ctrl.show()
    eve_ctrl = EVE(prefix=vaca_prefix+'AS-Glob:TI-EVE-1:')
    eve_ctrl.show()
    sys.exit(app.exec_())
