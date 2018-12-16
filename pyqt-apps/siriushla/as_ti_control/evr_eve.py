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
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util
from siriushla.as_ti_control.base import BaseList, BaseWidget


class _EVR_EVE(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix='', device='EVR'):
        """Initialize object."""
        super().__init__(parent, prefix)
        self.device_type = device
        self.setupui()

    def setupui(self):
        # self.resize(2000, 2000)
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        scr_ar = QScrollArea(self)
        # scr_ar.setSizePolicy(QSzPol.)
        self.otps_wid = OTPList(
            name='Internal Trigger (OTP)', parent=scr_ar, prefix=self.prefix,
            obj_names=['OTP{0:02d}'.format(i) for i in range(24)]
            )
        scr_ar.setWidget(self.otps_wid)
        scr_ar.setMinimumWidth(1440)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Expanding)
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
        'pulses': 150,
        'delay': 150,
        'interlock': 200,
        }
    _LABELS = {
        'state': 'State',
        'event': 'Event',
        'width': 'Width',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delay': 'Delay',
        'interlock': 'ByPass Intlk',
        }
    _ALL_PROPS = (
        'state', 'event', 'width', 'polarity', 'pulses', 'delay', 'interlock',
        )

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if 'state' == prop:
            sp = PyDMStateButton(self, init_channel=prefix + "State-Sel")
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + 'Evt-RB')
            rb.setAlignment(Qt.AlignCenter)
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix+"Width-RB")
            rb.setAlignment(Qt.AlignCenter)
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
            rb.setAlignment(Qt.AlignCenter)
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "NrPulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "NrPulses-RB")
            rb.setAlignment(Qt.AlignCenter)
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
            rb.setAlignment(Qt.AlignCenter)
        elif 'interlock' == prop:
            sp = PyDMStateButton(self, init_channel=prefix + "ByPassIntlk-Sel")
            rb = PyDMLed(self, init_channel=prefix + "ByPassIntlk-Sts")
        if rb is not None:
            return sp, rb
        return (sp, )


class OUTList(BaseList):
    """Template for control of Timing Devices Output Channels."""

    _MIN_WIDs = {
        'source': 200,
        'trigger': 100,
        'rf_delay': 150,
        'fine_delay': 150,
        }
    _LABELS = {
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delay': 'RF Delay',
        'fine_delay': 'Fine Delay',
        }
    _ALL_PROPS = ('source', 'trigger', 'rf_delay', 'fine_delay')

    def _createObjs(self, prefix, prop):
        if 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix+"Src-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "Src-Sts")
            rb.setAlignment(Qt.AlignCenter)
        elif 'trigger' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "SrcTrig-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "SrcTrig-RB")
            rb.setAlignment(Qt.AlignCenter)
        elif 'rf_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "RFDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "RFDelay-RB")
            rb.setAlignment(Qt.AlignCenter)
        elif 'fine_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "FineDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "FineDelay-RB")
            rb.setAlignment(Qt.AlignCenter)
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    _util.set_style(app)
    evr_ctrl = EVR(prefix='TEST-FAC:TI-EVR:')
    evr_ctrl.show()
    # eve_ctrl = EVE(prefix='TEST-FAC:TI-EVE:')
    # eve_ctrl.show()
    sys.exit(app.exec_())
