"""Define a window with detailed controls for a given magnet."""
from pydm import PyDMApplication
from qtpy.QtWidgets import QPushButton
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.detail_widget.DetailWidgetFactory \
    import DetailWidgetFactory
from siriuspy.search import PSSearch
from siriuspy.search import MASearch
from siriushla.util import connect_window


class PSDetailWindow(SiriusMainWindow):
    """Window to control a detailed widget."""

    def __init__(self, psname, parent=None):
        """Init UI."""
        super(PSDetailWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        if isinstance(psname, str):
            self._psname = _PVName(psname)
            name = self._psname
        else:
            self._psname = [_PVName(psn) for psn in psname]
            name = self._psname[0]
        secs = {'AS', 'TB', 'BO', 'TS', 'SI', 'LI'}
        if name.sec in secs:
            self.setObjectName(name.sec+'App')
        elif name.idx[:2] in secs:
            self.setObjectName(name.idx[:2]+'App')
        else:
            self.setObjectName('ASApp')
        self._setup_ui()

    def _setup_ui(self):
        if isinstance(self._psname, list):
            self.setWindowTitle('DCLinks Window')
        else:
            self.setWindowTitle(self._psname)
        # Set window layout
        self.widget = DetailWidgetFactory.factory(self._psname, self)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        if self._psname in ['BO-Fam:MA-B', 'SI-Fam:MA-B1B2']:
            w1 = widget.findChild(QPushButton, 'dclink1_button')
            w2 = widget.findChild(QPushButton, 'dclink2_button')
            psnames = MASearch.conv_maname_2_psnames(self._psname)
            for psname, w in zip(psnames, (w1, w2)):
                dclinks = PSSearch.conv_psname_2_dclink(psname)
                connect_window(w, PSDetailWindow, self, psname=dclinks)
        else:
            w = widget.findChild(QPushButton, 'dclink_button')
            if w:
                psname = self._psname.replace(':MA-', ':PS-')
                dclinks = PSSearch.conv_psname_2_dclink(psname)
                if dclinks:
                    connect_window(w, PSDetailWindow, self, psname=dclinks)
                else:
                    w.setHidden(True)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    ps = PSDetailWindow('BO-Fam:MA-B')
    ps.show()
    sys.exit(app.exec_())
