import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm.widgets.label import PyDMLabel
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.spinbox import PyDMSpinbox
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import LLTimeSearch as _LLTimeSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import SiriusMainWindow
from siriushla import util as _util
from base_list import BaseList


class AFC(SiriusMainWindow):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(70)
        self.my_layout.setVerticalSpacing(40)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        scr_ar = QScrollArea(cw)
        set_ = _LLTimeSearch.i2o_map['AFC']['SFP']
        obj_names = sorted([out for out in set_ if out.startswith('FMC')])
        self.fmcs_wid = AFCOUTList(
            name='FMC Outputs', parent=scr_ar,
            prefix=self.prefix, obj_names=obj_names,
            )
        scr_ar.setWidget(self.fmcs_wid)
        scr_ar.setMinimumWidth(1440)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Preferred)
        self.my_layout.addWidget(scr_ar, 2, 0)

        obj_names = sorted([out for out in set_ if out.startswith('CRT')])
        self.crts_wid = AFCOUTList(
            name='CRT Outputs', parent=self, prefix=self.prefix,
            obj_names=obj_names
            )
        self.my_layout.addWidget(self.crts_wid, 2, 1)

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
        status_layout.addWidget(gb, 0, 5)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


class AFCOUTList(BaseList):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'state': 200,
        'event': 100,
        'source': 150,
        'width': 150,
        'polarity': 170,
        'pulses': 120,
        'delay': 150,
        }
    _LABELS = {
        'state': 'State',
        'event': 'Event',
        'source': 'Source',
        'width': 'Width',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delay': 'Delay',
        }
    _ALL_PROPS = (
        'state', 'event', 'source', 'width', 'polarity', 'pulses', 'delay',
        )

    def _createObjs(self, prefix, prop):
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + 'Evt-RB')
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix + 'Src-Sel')
            rb = PyDMLabel(self, init_channel=prefix + 'Src-Sts')
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


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    afc_ctrl = AFC(
        prefix='ca://fernando-lnls452-linux-AS-02:TI-AFC:')
    afc_ctrl.show()
    sys.exit(app.exec_())
