"""Define a window with detailed controls for a given magnet."""

from qtpy.QtWidgets import QPushButton, QMenu, QAction
import qtawesome as qta
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch
from siriushla.util import connect_window, connect_newprocess, \
    get_appropriate_color
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
        self._is_dclink = 'dclink' in PSSearch.conv_psname_2_pstype(name)
        secs = {'AS', 'LI', 'TB', 'BO', 'TS', 'SI', 'IT'}
        if name.sub.endswith(('SA', 'SB', 'SP', 'ID')):
            sec = 'ID'
        elif name.sec in secs:
            sec = name.sec
        elif name.idx[:2] in secs:
            sec = name.idx[:2]
        else:
            sec = 'AS'
        self.setObjectName(sec+'App')
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
        w = widget.findChild(QPushButton, 'dclink_button')
        if w:
            psname = self._psname[0]
            dclinks = PSSearch.conv_psname_2_dclink(psname)
            if dclinks:
                dclink_type = PSSearch.conv_psname_2_psmodel(dclinks[0])
                if dclink_type != 'REGATRON_DCLink':
                    connect_window(w, PSDetailWindow, self, psname=dclinks)
                else:
                    if len(dclinks) > 1:
                        menu = QMenu(w)
                        for dcl in dclinks:
                            act = QAction(dcl, menu)
                            connect_newprocess(
                                act,
                                ['sirius-hla-as-ps-regatron-individual',
                                 '-dev', dcl], parent=self, is_pydm=True)
                            menu.addAction(act)
                        w.setMenu(menu)
                    else:
                        connect_newprocess(
                            w, ['sirius-hla-as-ps-regatron-individual',
                                '-dev', dclinks[0]], parent=self, is_pydm=True)
            else:
                w.setHidden(True)
