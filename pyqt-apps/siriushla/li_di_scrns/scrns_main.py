''' Diagnostic Interface of the LINAC's BPM'''
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QLabel, QGridLayout
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow


class LiBeamProfile(SiriusMainWindow):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = get_appropriate_color('LI')

        self.device_name = "LA-BI:"
        self.setWindowIcon(qta.icon('mdi.safe-square', color=color))
        self.setWindowTitle(self.device_name)

        self._setupUi()

    def header(self):
        hd_hlay = QHBoxLayout()
        title = QLabel("<h2>" + self.device_name + " - Screen View</h2>")
        title.setAlignment(Qt.AlignCenter)
        hd_hlay.addWidget(title)
        return hd_hlay

    def imageViewer(self):
        pixmap = QPixmap('./linac.jpg')
        image_container = QLabel()
        image_container.setPixmap(pixmap)
        return image_container

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 1)
        if_glay.addWidget(self.imageViewer(), 1, 0, 1, 1)
        if_glay.setAlignment(Qt.AlignTop)
        wid.setLayout(if_glay)
        self.setCentralWidget(wid)

# mdi-circle-double
#mdi-record-circle-outline
#mdi-cash
#mdi-safe-square-outline
#mdi-safe-square
