#!/usr/bin/env python-sirius
"""HLA TB and TS ICT monitoring Window."""

import sys
from qtpy.uic import loadUi
from qtpy.QtCore import QPoint
from qtpy.QtWidgets import QWidget, QVBoxLayout
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusConnectionSignal
from siriushla import util


class SlitMonitoring(QWidget):
    """Class to create Slits Monitor Widget."""

    def __init__(self, slit_orientation, parent=None, prefix=''):
        """Init."""
        super(SlitMonitoring, self).__init__(parent)
        if not prefix:
            prefix = _vaca_prefix
        self.slit_orientation = slit_orientation
        self._slit_center = 0
        self._slit_width = 0

        tmp_file = _substitute_in_file(
            '/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/tl_ap_control'
            '/ui_tb_ap_slit'+slit_orientation.lower()+'mon.ui',
            {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.centralwidget)

        slit_prefix = prefix+'TB-01:DI-Slit'+slit_orientation.upper()
        self.conn_slitcenter = SiriusConnectionSignal(
            slit_prefix+':Center-RB')
        self.conn_slitcenter.new_value_signal[float].connect(self._setSlitPos)
        self.conn_slitwidth = SiriusConnectionSignal(
            slit_prefix+':Width-RB')
        self.conn_slitwidth.new_value_signal[float].connect(self._setSlitPos)

    def _setSlitPos(self, new_value):
        """Set Slits Widget positions."""
        if 'Center' in self.sender().address:
            self._slit_center = new_value  # considering mm
        elif 'Width' in self.sender().address:
            self._slit_width = new_value

        rect_width = 110
        circle_diameter = 100
        widget_width = 300
        vacuum_chamber_diameter = 36  # mm

        xc = (circle_diameter*self._slit_center/vacuum_chamber_diameter
              + widget_width/2)
        xw = circle_diameter*self._slit_width/vacuum_chamber_diameter

        if self.slit_orientation == 'H':
            left = round(xc - rect_width - xw/2)
            right = round(xc + xw/2)
            self.centralwidget.PyDMDrawingRectangle_SlitHLeft.move(
                QPoint(left, (widget_width/2 - rect_width)))
            self.centralwidget.PyDMDrawingRectangle_SlitHRight.move(
                QPoint(right, (widget_width/2 - rect_width)))
        elif self.slit_orientation == 'V':
            up = round(xc - rect_width - xw/2)
            down = round(xc + xw/2)
            self.centralwidget.PyDMDrawingRectangle_SlitVUp.move(
                QPoint((widget_width/2 - rect_width), up))
            self.centralwidget.PyDMDrawingRectangle_SlitVDown.move(
                QPoint((widget_width/2 - rect_width), down))

    def channels(self):
        """Return channels."""
        return [self.conn_slitcenter, self.conn_slitwidth]


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    util.set_style(app)
    w = SlitMonitoring(slit_orientation='H', prefix=_vaca_prefix)
    window = SiriusMainWindow()
    window.setCentralWidget(w)
    window.setWindowTitle('SlitV Monitor')
    window.show()
    sys.exit(app.exec_())
