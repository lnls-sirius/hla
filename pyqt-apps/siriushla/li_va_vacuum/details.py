from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QLabel
from siriushla.widgets.label import SiriusLabel
from .functions import buildIdName, showUnitView
from .util import IPS_DETAILS, PVS_CONFIG
from ..widgets import SiriusMainWindow, SiriusLineEdit, \
    PyDMLed, SiriusEnumComboBox

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

    def getWidget(self, name, wid_type='button'):
        pv_name = self.devpref + name
        if wid_type == 'led':
            widget = PyDMLed(
                init_channel=pv_name)
        elif wid_type == 'edit':
            widget = SiriusLineEdit(
                init_channel=pv_name)
            widget.setAlignment(Qt.AlignCenter)   
        elif wid_type == 'enum':
            widget = SiriusEnumComboBox(
                self, init_channel=pv_name)
        else:
            widget = SiriusLabel(
                init_channel=pv_name)
            widget.setAlignment(Qt.AlignCenter)
        widget._keep_unit = True
        widget.setStyleSheet("min-width:3em;")
        return widget

    def SPRBWidget(self, title, control, readback, wid_type):
        wid = QWidget()
        lay = QHBoxLayout()
        wid.setLayout(lay)
        label = QLabel(title, alignment=Qt.AlignCenter)
        label.setStyleSheet("min-width:5em;")
        lay.addWidget(label)
        lay.addWidget(
            self.getWidget(control, wid_type), 
            alignment=Qt.AlignRight)
        lay.addWidget(
            self.getWidget(readback, 'label'), 
            alignment=Qt.AlignLeft)
        return wid

    def buildIPSInfo(self):
        wid = QGroupBox()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)
        for info_type in ['voltage', 'current', 'pressure']:
            info = self.config[info_type]
            name = self.devpref + info['text']
            widget = showUnitView(
                name, info['color'], 6)
            lay.addWidget(widget, alignment=Qt.AlignCenter)
        return wid
            
    def buildGroup(self, info, title):
        group = QGroupBox()
        lay = QVBoxLayout()
        group.setTitle(title)
        group.setLayout(lay)
        for item in info:
            if 'title' in item:
                lay.addWidget(
                    self.SPRBWidget(
                        item['title'], item['control'], 
                        item['status'], item['widget']))
        return group

    def buildDetails(self):
        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)
        for title, info in IPS_DETAILS.items():
            group = self.buildGroup(info, title)
            hlay.addWidget(group)
        return wid

    def _setupUi(self):
        """."""
        lay = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(lay)
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 0, 10, 0)
         
        lay.addWidget(self.buildIPSInfo())
        lay.addWidget(self.buildDetails())
