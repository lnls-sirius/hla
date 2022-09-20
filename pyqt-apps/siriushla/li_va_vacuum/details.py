from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout
from .functions import buildIdName, showUnitView
from .util import PVS_CONFIG
from ..widgets import SiriusMainWindow, SiriusLabel

class IpsDetailWindow(SiriusMainWindow):
    """Show the Chart Window."""

    def __init__(self, parent=None, prefix='', id_ips=''):
        """Init."""
        super().__init__(parent)
        self.config = PVS_CONFIG["Pump"]
        self.prefix = prefix
        self.main_dev = self.config["prefix"]
        self.devpref = buildIdName(self.prefix + self.main_dev, id_ips)
        self.setObjectName('LIApp')
        self.setWindowTitle("IPS "+str(id_ips)+" Details")
        self._setupUi()

    def SPRBWidget(self, wid_type=0):
        lay = QHBoxLayout()
        lay.addWidget(SiriusLabel())

    def buildIPSInfo(self):
        wid = QGroupBox()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)
        for info_type in ['voltage', 'current', 'pressure']:
            info = self.config[info_type]
            name = self.devpref + info['text']
            widget = showUnitView(
                name, info['color'], 5)
            lay.addWidget(widget, alignment=Qt.AlignCenter)
        return wid
            

    def _setupUi(self):
        """."""
        lay = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(lay)
        self.setCentralWidget(wid)
        lay.setContentsMargins(0, 0, 0, 0)
         
        lay.addWidget(self.buildIPSInfo())
