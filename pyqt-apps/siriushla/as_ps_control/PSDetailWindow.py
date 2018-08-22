"""Define a window with detailed controls for a given magnet."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QPushButton
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.detail_widget.DetailWidgetFactory \
    import DetailWidgetFactory
from ..util import connect_window


class PSDetailWindow(SiriusMainWindow):
    """Window to control a detailed widget."""

    STYLESHEET = """
    """

    def __init__(self, psname, parent=None):
        """Init UI."""
        super(PSDetailWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()

        self._ma = psname

        self._setup_ui()
        self.setStyleSheet(self.STYLESHEET)
        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set window layout
        self.setWindowTitle(self._ma)
        self.widget = DetailWidgetFactory.factory(self._ma, self)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        w = widget.findChild(QPushButton, 'dclink_button')
        if w:
            # TODO: dclink name is hardcoded
            connect_window(
                w, PSDetailWindow, self, psname='AS-Glob:PS-DCLinkFBP-2')
