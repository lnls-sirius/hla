"""Define a window with detailed controls for a given magnet."""
from pydm import PyDMApplication
from qtpy.QtWidgets import QPushButton
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.detail_widget.DetailWidgetFactory \
    import DetailWidgetFactory
from siriuspy.search.ps_search import PSSearch
from ..util import connect_window


class PSDetailWindow(SiriusMainWindow):
    """Window to control a detailed widget."""

    def __init__(self, psname, parent=None):
        """Init UI."""
        super(PSDetailWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()

        self._ma = psname

        self._setup_ui()
        # self.setStyleSheet(self.STYLESHEET)
        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set window layout
        self.setWindowTitle("PS Detail Window")
        self.widget = DetailWidgetFactory.factory(self._ma, self)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        w = widget.findChild(QPushButton, 'dclink_button')
        if w:
            dclinks = PSSearch.conv_psname_2_dclink(self._ma)
            if dclinks:
                connect_window(w, PSDetailWindow, self, psname=dclinks)
