import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QMenuBar
from pydm.widgets.label import PyDMLabel
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import LLTimeSearch as _LLTimeSearch
from siriushla.util import connect_window
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import create_window_from_widget
from siriushla import as_ti_control as _ti_ctrl
from .ll_trigger import AFCOUTList
from .base import BaseWidget


class AFC(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix=prefix)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self._setupmenus(), 0, 0, 1, 2)

        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0, 1, 2)
        self._setup_status_wid()

        set_ = _LLTimeSearch.In2OutMap['AMCFPGAEVR']['SFP8']
        obj_names = sorted([out for out in set_ if out.startswith('FMC')])
        self.fmcs_wid = AFCOUTList(name='FMC Outputs', parent=self,
                                   prefix=self.prefix, obj_names=obj_names)
        self.fmcs_wid.setObjectName('fmcs_wid')
        self.fmcs_wid.setStyleSheet("""#fmcs_wid{min-width:60em;}""")
        self.my_layout.addWidget(self.fmcs_wid, 3, 0)

        obj_names = sorted([out for out in set_ if out.startswith('CRT')])
        self.crts_wid = AFCOUTList(name='CRT Outputs', parent=self,
                                   prefix=self.prefix, obj_names=obj_names)
        self.crts_wid.setObjectName('crts_wid')
        self.crts_wid.setStyleSheet("""#crts_wid{min-width:60em;}""")
        self.my_layout.addWidget(self.crts_wid, 3, 1)

    def _setupmenus(self):
        prefix = self.prefix
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Uplink')

        fout = _LLTimeSearch.get_fout_channel(prefix + 'CRT0')
        action = menu.addAction(fout)
        Win = create_window_from_widget(_ti_ctrl.FOUT, title=fout.device_name)
        connect_window(action, Win, self, prefix=fout.device_name+':')
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


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow
    app = SiriusApplication()
    win = SiriusMainWindow()
    afc_ctrl = AFC(prefix='TEST-FAC:TI-AMCFPGAEVR:')
    win.setCentralWidget(afc_ctrl)
    win.show()
    sys.exit(app.exec_())
