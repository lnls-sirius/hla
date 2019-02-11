import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QScrollArea, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy as QSzPol
from pydm.widgets import PyDMLabel,  PyDMEnumComboBox as PyDMECB
from siriushla.widgets import PyDMLed, SiriusLedAlert, PyDMStateButton
from siriushla.as_ti_control.base import BaseWidget
from siriushla.as_ti_control.ll_trigger import OTPList, OUTList


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
        scr_ar.setMinimumWidth(1570)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Expanding)
        self.my_layout.addWidget(scr_ar, 2, 0, 2, 1)

        self.outs_wid = OUTList(
            name='OUT', parent=self, prefix=self.prefix,
            obj_names=['OUT{0:d}'.format(i) for i in range(8)]
            )
        self.my_layout.addWidget(self.outs_wid, 2, 1)
        self.my_layout.addItem(QSpacerItem(
                0, 0, QSzPol.Minimum, QSzPol.Expanding))

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


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow
    app = SiriusApplication()
    win = SiriusMainWindow()
    evr_ctrl = EVR(prefix='TEST-FAC:TI-EVR:')
    # eve_ctrl = EVE(prefix='TEST-FAC:TI-EVE:')
    win.setCentralWidget(evr_ctrl)
    # win.setCentralWidget(eve_ctrl)
    win.show()
    sys.exit(app.exec_())
