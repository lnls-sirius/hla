#!/usr/bin/env python-sirius
"""HLA TB Slits monitoring Window."""

from qtpy.QtCore import QPoint
from siriushla.widgets import SiriusConnectionSignal
from siriushla.common.diff_ctrl import DiffCtrlDevMonitor, DiffCtrlView


class SlitMonitoring(DiffCtrlDevMonitor):
    """Class to create Slits Monitor Widget."""

    def _setupControlWidgets(self):
        """Setup control widgets channels/labels."""
        self.lb_descctrl1.setText('Center [mm]:')
        self.sb_ctrl1.channel = self.device.substitute(propty='Center-SP')
        self.lb_ctrl1.channel = self.device.substitute(propty='Center-RB')
        self.lb_descctrl2.setText('Width [mm]:')
        self.sb_ctrl2.channel = self.device.substitute(propty='Width-SP')
        self.lb_ctrl2.channel = self.device.substitute(propty='Width-RB')

    def _createConnectors(self):
        """Create connectors to monitor device positions."""
        self._slit_center = 0
        self._slit_width = 0
        self.conn_slitcenter = SiriusConnectionSignal(
            self.device.substitute(propty='Center-RB'))
        self.conn_slitcenter.new_value_signal[float].connect(self._setDevPos)
        self.conn_slitwidth = SiriusConnectionSignal(
            self.device.substitute(propty='Width-RB'))
        self.conn_slitwidth.new_value_signal[float].connect(self._setDevPos)

    def _setDevPos(self, new_value):
        """Set Slit Widget positions."""
        if 'Center' in self.sender().address:
            self._slit_center = new_value  # considering mm
        elif 'Width' in self.sender().address:
            self._slit_width = new_value
        self.updateDevWidget()

    def updateDevWidget(self):
        """Update Slit illustration."""
        self.style().unpolish(self.dev_widget.widget_draw)
        self.style().polish(self.dev_widget.widget_draw)
        widget_w = self.dev_widget.widget_draw.width()
        widget_h = self.dev_widget.widget_draw.height()
        vacuum_chamber_d = 36  # mm

        if self.orientation == 'H':
            rect_h = widget_h*3/5
            rect_w = rect_h/2
            circle_d = rect_w
            factor = circle_d/vacuum_chamber_d
            xc = (widget_w/2 - self._slit_center*factor)
            xw = self._slit_width*factor
            left = round(xc - rect_w - xw/2)
            right = round(xc + xw/2)

            self.dev_widget.PyDMDrawingRectangle_HLeft.resize(rect_w, rect_h)
            self.dev_widget.PyDMDrawingRectangle_HLeft.move(
                QPoint(left, (widget_h-rect_h)/2))
            self.dev_widget.PyDMDrawingRectangle_HRight.resize(rect_w, rect_h)
            self.dev_widget.PyDMDrawingRectangle_HRight.move(
                QPoint(right, (widget_h-rect_h)/2))

        elif self.orientation == 'V':
            rect_w = widget_h*3/5
            rect_h = rect_w/2
            circle_d = rect_h
            factor = circle_d/vacuum_chamber_d
            xc = (widget_h/2 - self._slit_center*factor)
            xw = self._slit_width*factor
            up = round(xc - rect_h - xw/2)
            down = round(xc + xw/2)

            self.dev_widget.PyDMDrawingRectangle_VUp.resize(rect_w, rect_h)
            self.dev_widget.PyDMDrawingRectangle_VUp.move(
                QPoint((widget_w-rect_w)/2, up))
            self.dev_widget.PyDMDrawingRectangle_VDown.resize(rect_w, rect_h)
            self.dev_widget.PyDMDrawingRectangle_VDown.move(
                QPoint((widget_w-rect_w)/2, down))

        self.dev_widget.PyDMDrawingCircle.resize(circle_d, circle_d)
        self.dev_widget.PyDMDrawingCircle.move(QPoint(
            (widget_w-circle_d)/2, (widget_h-circle_d)/2))

        axis_w = self.dev_widget.axis.width()
        axis_h = self.dev_widget.axis.height()
        self.dev_widget.axis.move(QPoint(
            (widget_w-axis_w), (widget_h-axis_h)))

    def channels(self):
        """Return channels."""
        return [self.conn_slitcenter, self.conn_slitwidth]


class SlitsView(DiffCtrlView):
    """Class to create Slits View Widget."""

    DEVICE_PREFIX = 'TB-01:DI-Slit'
    DEVICE_CLASS = SlitMonitoring
