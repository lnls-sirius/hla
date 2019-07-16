import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QMenuBar
from pydm.widgets.label import PyDMLabel
from siriuspy.search import LLTimeSearch
from siriushla.util import connect_window
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import create_window_from_widget
from siriushla import as_ti_control as _ti_ctrl
from .base import BaseWidget


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

        downs = LLTimeSearch.get_fout2trigsrc_mapping()[prefix.device_name]
        downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
        for out, dwn in downs:
            dev, down = dwn.dev, dwn.device_name
            if dev == 'EVR':
                devt = _ti_ctrl.EVR
            elif dev == 'EVE':
                devt = _ti_ctrl.EVE
            else:
                devt = _ti_ctrl.AFC
            action = menu.addAction(out + ' --> ' + down)
            Win = create_window_from_widget(devt, title=down)
            connect_window(action, Win, None, prefix=down + ':')

        menu = main_menu.addMenu('&Uplink')
        link = list(LLTimeSearch.In2OutMap[prefix.dev])[0]
        evg = LLTimeSearch.get_evg_channel(
            prefix.device_name.substitute(propty=link))
        action = menu.addAction(evg)
        Win = create_window_from_widget(_ti_ctrl.EVG, title=evg.device_name)
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


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow
    app = SiriusApplication()
    win = SiriusMainWindow()
    fout_ctrl = FOUT(prefix='TEST-FAC:TI-Fout:')
    win.setCentralWidget(fout_ctrl)
    win.show()
    sys.exit(app.exec_())
