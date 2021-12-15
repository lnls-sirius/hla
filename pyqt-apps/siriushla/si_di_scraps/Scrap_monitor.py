#!/usr/bin/env python-sirius
"""HLA SI Scrapers monitoring Window."""

from qtpy.QtCore import QPoint
from siriushla.widgets import SiriusConnectionSignal
from siriushla.common.diff_ctrl import DiffCtrlDevMonitor, DiffCtrlView


class ScraperMonitoring(DiffCtrlDevMonitor):
    """Scraper Monitor Widget."""

    def _createConnectors(self):
        """Create connectors to monitor device positions."""
        self._scrap_pospos = 0
        self.conn_scrap_pospos = SiriusConnectionSignal(
            self.device.substitute(propty='PositiveEdgePos-RB'))
        self.conn_scrap_pospos.new_value_signal[float].connect(self._setDevPos)
        self._scrap_negpos = 0
        self.conn_scrap_negpos = SiriusConnectionSignal(
            self.device.substitute(propty='NegativeEdgePos-RB'))
        self.conn_scrap_negpos.new_value_signal[float].connect(self._setDevPos)

    def _setDevPos(self, new_value):
        """Set Scraper Widget positions."""
        if 'Positive' in self.sender().address:
            self._scrap_pospos = new_value
        elif 'Negative' in self.sender().address:
            self._scrap_negpos = new_value
        self.updateDevWidget()

    def _setupControlWidgets(self):
        """Setup control widgets channels/labels."""
        self.lb_descCtrl1.setText('Positive Edge Pos.[mm]:')
        self.lb_descCtrl1.setStyleSheet(
            'min-width: 10.5em; max-width: 10.5em;')
        self.sb_Ctrl1.channel = \
            self.device+':PositiveEdgePos-SP'
        self.lb_Ctrl1.channel = \
            self.device+':PositiveEdgePos-RB'
        self.lb_descCtrl2.setText('Negative Edge Pos.[mm]:')
        self.lb_descCtrl2.setStyleSheet(
            'min-width: 10.5em; max-width: 10.5em;')
        self.sb_Ctrl2.channel = \
            self.device+':NegativeEdgePos-SP'
        self.lb_Ctrl2.channel = \
            self.device+':NegativeEdgePos-RB'

    def updateDevWidget(self):
        """Update Scraper illustration."""
        self.style().unpolish(self.dev_widget.widget_draw)
        self.style().polish(self.dev_widget.widget_draw)
        widget_w = self.dev_widget.widget_draw.width()
        widget_h = self.dev_widget.widget_draw.height()
        vacuum_chamber_d = 24  # mm

        if self.orientation == 'H':
            rect_h = widget_h*3/5
            rect_w = rect_h/2
            circle_d = rect_w
            factor = circle_d/vacuum_chamber_d
            xpos = widget_h/2 - self._scrap_pospos*factor
            xneg = widget_h/2 - self._scrap_negpos*factor
            left = round(xpos - rect_w)
            right = round(xneg)

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
            xpos = widget_h/2 - self._scrap_pospos*factor
            xneg = widget_h/2 - self._scrap_negpos*factor
            up = round(xpos - rect_h)
            down = round(xneg)

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
        self.dev_widget.axis.move(QPoint((widget_w-axis_w), (widget_h-axis_h)))

    def channels(self):
        """Return channels."""
        return [self.conn_scrap_pospos, self.conn_scrap_negpos]


class ScrapersView(DiffCtrlView):
    """Scrapers View Widget."""

    DEVICE_PREFIX = 'SI-01SA:DI-Scrap'
    DEVICE_CLASS = ScraperMonitoring
