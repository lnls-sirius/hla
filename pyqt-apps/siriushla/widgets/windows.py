"""Sirius Windows module."""
from qtpy.QtGui import QKeySequence
from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QMainWindow, QDialog, QHBoxLayout, QApplication
import pyqtgraph as pg


def _create_siriuswindow(qt_type):
    """Create a _SiriusWindow that inherits from qt_type."""
    class _SiriusWindow(qt_type):
        """Auxiliar _SiriusWindow class.

        Parameters
        ----------
        parent : QWidget
            The parent widget for the SiriusMainWindow
        """

        Stylesheet = ""
        FontSizeSS = "* {{font-size: {}pt;}}"

        def __init__(self, *args, **kwargs):
            """Init."""
            super().__init__(*args, **kwargs)
            self.setFocus(True)
            self.app = QApplication.instance()

        def keyPressEvent(self, event):
            """Override keyPressEvent."""
            font = self.app.font()
            if event.matches(QKeySequence.ZoomIn):
                font.setPointSize(font.pointSize() + 1)
                self.app.setFont(font)
            elif event.matches(QKeySequence.ZoomOut) and font.pointSize() > 9:
                font.setPointSize(font.pointSize() - 1)
                self.app.setFont(font)
            super().keyPressEvent(event)

        def changeEvent(self, event):
            if event.type() == QEvent.FontChange:
                fontsize = self.app.font().pointSize()
                self.ensurePolished()
                self.setStyleSheet(
                    self.Stylesheet + self.FontSizeSS.format(fontsize))
                self.setFixedSize(self.sizeHint())

                # handle resizing of pyqtgraph plots labels
                fontsize_str = str(fontsize)+'pt'
                for w in self.findChildren(pg.PlotWidget):
                    # axes labels
                    for ax in w.getPlotItem().axes.values():
                        sty = ax['item'].labelStyle
                        sty['font-size'] = fontsize_str
                        ax['item'].setLabel(text=None, **sty)
                    # legend
                    if w.plotItem.legend:
                        legw = 0
                        for item in w.plotItem.legend.items:
                            item[1].opts['size'] = fontsize_str
                            item[1].setText(text=item[1].text, **item[1].opts)
                            legw = max(legw, 20+item[1].width())
                        w.plotItem.legend.updateSize()
                        w.plotItem.legend.setFixedWidth(legw)
                    # title
                    wtitle = w.plotItem.titleLabel
                    wtitle.opts['size'] = fontsize_str
                    wtitle.setText(text=wtitle.text, **wtitle.opts)
                for w in self.findChildren(pg.GraphicsLayoutWidget):
                    sty = w.xaxis.labelStyle
                    sty['font-size'] = fontsize_str
                    w.xaxis.setLabel(text=None, **sty)
                    sty = w.yaxis.labelStyle
                    sty['font-size'] = fontsize_str
                    w.yaxis.setLabel(text=None, **sty)
            super().changeEvent(event)

    return _SiriusWindow


SiriusMainWindow = _create_siriuswindow(QMainWindow)
SiriusDialog = _create_siriuswindow(QDialog)


def create_window_from_widget(
                WidgetClass, name=None, size=None, is_main=False):

    if is_main:
        class MyWindow(SiriusMainWindow):

            def __init__(self, parent, *args, **kwargs):
                super().__init__(parent)
                wid = WidgetClass(self, *args, **kwargs)
                self.setCentralWidget(wid)
                if size:
                    wid.setObjectName('celtralwidget')
                    wid.setStyleSheet("""
                        #celtralwidget{{
                            min-width:{0}em; max-width:{0}em;
                            min-height:{1}em; max-height:{1}em;
                        }}""".format(size[0], size[1]))
    else:
        class MyWindow(SiriusDialog):

            def __init__(self, parent, *args, **kwargs):
                super().__init__(parent)
                hbl = QHBoxLayout(self)
                wid = WidgetClass(self, *args, **kwargs)
                hbl.addWidget(wid)
                if size:
                    wid.setObjectName('celtralwidget')
                    wid.setStyleSheet("""
                        #celtralwidget{{
                            min-width:{0}em; max-width:{0}em;
                            min-height:{1}em; max-height:{1}em;
                        }}""".format(size[0], size[1]))

    if name:
        MyWindow.__name__ = name
    return MyWindow
