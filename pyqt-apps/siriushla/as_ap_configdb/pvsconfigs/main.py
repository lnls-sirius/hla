"""PVs Config Main Module."""

from qtpy.QtWidgets import QWidget, QPushButton, QHBoxLayout

from siriuspy.clientconfigdb import ConfigDBClient

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.util import connect_window
from .load_and_apply import LoadAndApplyConfig2MachineWindow
from .read_and_save import ReadAndSaveConfig2ServerWindow


class PVsConfigManager(SiriusMainWindow):
    """Window to manage configuration."""

    def __init__(self, parent=None, url=None):
        """Setup UI."""
        super().__init__(parent)
        self._client = ConfigDBClient(url)
        self._setup_ui()
        self.setWindowTitle("PVs Configuration Manager")

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.layout = QHBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)

        self.save_btn = QPushButton('Save', self)
        self.load_btn = QPushButton('Load', self)
        self.save_btn.setObjectName('SaveBtn')
        self.load_btn.setObjectName('LoadBtn')

        self.central_widget.layout.addWidget(self.save_btn)
        self.central_widget.layout.addWidget(self.load_btn)

        self.central_widget.setStyleSheet("""
        #SaveBtn, #LoadBtn {
            background: qlineargradient(x1:0 y1:0, x2:0 y2:1,
                                        stop:0 white, stop:1 lightgrey);
            height: 100%;
            border: 1px solid grey;
            padding: 0 5px 0 5px;
        }
        #SaveBtn:hover, #LoadBtn:hover {
            background: qlineargradient(x1:0 y1:0, x2:0 y2:1,
                                        stop:0 lightgrey, stop:1 white);
        }""")

        connect_window(
            self.save_btn, ReadAndSaveConfig2ServerWindow,
            self, client=self._client)
        connect_window(
            self.load_btn, LoadAndApplyConfig2MachineWindow,
            self, client=self._client)
