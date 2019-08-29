"""Define a window with detailed controls for a given magnet."""

from qtpy.QtWidgets import QPushButton
import qtawesome as qta
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch, MASearch
from siriushla.util import connect_window, get_appropriate_color
from siriushla.widgets import SiriusMainWindow
from .detail_widget.DetailWidgetFactory import DetailWidgetFactory


class PSDetailWindow(SiriusMainWindow):
    """Window to control a detailed widget."""

    def __init__(self, psname, parent=None):
        """Init UI."""
        super(PSDetailWindow, self).__init__(parent)
        if isinstance(psname, str):
            self._psname = [_PVName(psname), ]
        else:
            self._psname = [_PVName(psn) for psn in psname]
        name = self._psname[0]
        dis = name.dis
        self._is_dclink = (dis == 'PS') and \
            ('dclink' in PSSearch.conv_psname_2_pstype(name))
        secs = {'AS', 'TB', 'BO', 'TS', 'SI', 'LI'}
        if name.sec in secs:
            sec = name.sec
        elif name.idx[:2] in secs:
            sec = name.idx[:2]
        else:
            sec = 'AS'
        self.setObjectName(sec+'App')
        if name.dis.lower().startswith('ma'):
            icon = qta.icon(
                'mdi.magnet', color=get_appropriate_color(sec))
        else:
            icon = qta.icon(
                'mdi.car-battery', color=get_appropriate_color(sec))
        self.setWindowIcon(icon)
        self._setup_ui()

    def _setup_ui(self):
        if self._is_dclink:
            self.setWindowTitle('DCLinks Window')
        else:
            self.setWindowTitle(self._psname[0])
        # Set window layout
        self.widget = DetailWidgetFactory.factory(self._psname, self)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        if self._psname[0] in ['BO-Fam:MA-B', 'SI-Fam:MA-B1B2']:
            w1 = widget.findChild(QPushButton, 'dclink1_button')
            w2 = widget.findChild(QPushButton, 'dclink2_button')
            psnames = MASearch.conv_maname_2_psnames(self._psname[0])
            for psname, w in zip(psnames, (w1, w2)):
                dclinks = PSSearch.conv_psname_2_dclink(psname)
                connect_window(w, PSDetailWindow, self, psname=dclinks)
        else:
            w = widget.findChild(QPushButton, 'dclink_button')
            if w:
                psname = self._psname[0].replace(':MA-', ':PS-')
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
