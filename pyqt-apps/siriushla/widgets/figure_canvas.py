"""Derive matplotlib FigureCanvas to resize labels in ZoomIn/ZoomOut."""
from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QApplication
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)


class SiriusFigureCanvas(FigureCanvas):
    """SiriusFigureCanvas class."""

    def changeEvent(self, event):
        """Reimplement changeEvent to handle labels resizing."""
        if event.type() == QEvent.FontChange:
            self.app = QApplication.instance()
            fontsize = self.app.font().pointSize()

            axes = self.figure.get_axes()
            handles = []
            labels = []
            for axis in axes:
                axis.tick_params(labelsize=fontsize)
                xl = axis.get_xlabel()
                axis.set_xlabel(xl, {'size': fontsize})
                yl = axis.get_ylabel()
                axis.set_ylabel(yl, {'size': fontsize})
                title = axis.get_title()
                axis.set_title(title, {'size': fontsize})
                legh, legl = axis.get_legend_handles_labels()
                if legl:
                    handles.extend(legh)
                    labels.extend(legl)
            if labels:
                axes[0].legend(handles, labels, fontsize=fontsize)

            self.figure.canvas.draw()
