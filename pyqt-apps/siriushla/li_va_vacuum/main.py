"""Main module of the Application Interface."""

import os as _os
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel
from pydm.widgets.display_format import DisplayFormat
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND
from .widgets import SquareLed


class VacuumMain(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.setObjectName('LIApp')
        self.setWindowTitle('LI Vacuum')
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "vacuum.png"))
        self._setupui()

    def legendText(self, text):
        text = QLabel(text)
        text.setMaximumHeight(30)
        return text

    def showLegend(self, legend):
        """ Show one of the legends present in the LEGEND variable in util"""
        leg_glay = QGridLayout()
        leg_glay.addWidget(
            self.legendText('<b>'+legend+'</b>'),
            0, 0, 1, 2, Qt.AlignCenter)
        row = 1
        for item in LEGEND[legend]:
            column = 0
            if 'color' in item:
                leg_glay.addWidget(
                    SquareLed(self,
                        item['color'], False),
                    row, column, 1, 1, Qt.AlignCenter)
                column = 1

            leg_glay.addWidget(
                self.legendText(item['text']),
                row, column, 1, 1, Qt.AlignLeft)
            row += 1
        return leg_glay

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        # self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(950, 0)
        return self.image_container

    def _setupui(self):
        """ . """
        lay1 = QGridLayout()
        self.setLayout(lay1)

        # lay1.addWidget(self.imageViewer(), 0, 0)
        lay1.addLayout(self.showLegend('Gauge Status'), 0, 0)
        lay1.addLayout(self.showLegend('CCG'), 0, 1)
        lay1.addLayout(self.showLegend('IPS Control'), 0, 2)
