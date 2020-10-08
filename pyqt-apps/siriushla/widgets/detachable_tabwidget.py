"""."""
from qtpy.QtWidgets import QTabBar, QTabWidget, qApp, QMessageBox
from qtpy.QtCore import Signal, Slot, QPoint, Qt
from qtpy.QtGui import QCursor

from ..widgets import SiriusMainWindow


class DetachableTabWidget(QTabWidget):
    """
    The DetachableTabWidget adds additional functionality to Qt's
    QTabWidget that allows it to detach and re-attach tabs.

    Detach tabs by double clicking the tab

    Adapted from https://stackoverflow.com/questions/47267195/in-pyqt-is-it-possible-to-detach-tabs-from-a-qtabwidget

    Original by Stack Overflow user: Blackwood, 13/11/2017
    """

    def __init__(self, parent=None):
        """."""

        super().__init__(parent=parent)

        self.tabBar = TabBar(self)
        self.tabBar.onDetachTabSignal.connect(self.detachTab)
        self.setTabBar(self.tabBar)

        # Used to keep a reference to detached tabs since their QMainWindow
        # does not have a parent
        self.detachedTabs = dict()

        # Close all detached tabs if the application is closed explicitly
        qApp.aboutToQuit.connect(self.closeDetachedTabs)  # @UndefinedVariable

    @Slot(int, QPoint)
    def detachTab(self, index, point):
        """Detach tab from TabWidget."""
        # Get the tab content
        name = self.objectName()
        text = self.tabText(index)
        icon = self.tabIcon(index)
        if icon.isNull():
            icon = self.window().windowIcon()
        contentWidget = self.widget(index)

        try:
            contentWidgetRect = contentWidget.frameGeometry()
        except AttributeError:
            return

        # Create a new detached tab window
        detachedTab = DetachedTab(name, text, contentWidget, parent=self)
        detachedTab.setWindowModality(Qt.NonModal)
        detachedTab.setWindowIcon(icon)
        detachedTab.setGeometry(contentWidgetRect)
        detachedTab.onAttachSignal.connect(self.attachTabSlot)
        detachedTab.move(point)
        detachedTab.show()

        # Create a reference to maintain access to the detached tab
        self.detachedTabs[text] = (detachedTab, index)

    def attachTab(self, contentWidget, name, icon, index):
        """Attach tab to QTabWidget."""
        # Create an image from the given icon (for comparison)
        if not icon.isNull():
            try:
                tabIconPixmap = icon.pixmap(icon.availableSizes()[0])
                tabIconImage = tabIconPixmap.toImage()
            except IndexError:
                tabIconImage = None
        else:
            tabIconImage = None

        # Create an image of the main window icon (for comparison)
        if not icon.isNull():
            try:
                windowIconPixmap = self.window().windowIcon().pixmap(
                    icon.availableSizes()[0])
                windowIconImage = windowIconPixmap.toImage()
            except IndexError:
                windowIconImage = None
        else:
            windowIconImage = None

        # Determine if the given image and the main window icon are the same.
        # If they are, then do not add the icon to the tab
        if tabIconImage == windowIconImage:
            index = self.insertTab(index, contentWidget, name)
        else:
            index = self.insertTab(index, contentWidget, icon, name)
        # Make this tab the current tab
        if index > -1:
            self.setCurrentIndex(index)

    @Slot(str)
    def attachTabSlot(self, name):
        """Slot responsible for attaching tab to QTabWidget."""
        wind, index = self.detachedTabs[name]

        # Create references to the detached tab's content and icon
        indcs = sorted(idx for _, idx in self.detachedTabs.values())
        index -= indcs.index(index)
        contentWidget = wind.contentWidget
        icon = wind.windowIcon()

        # Make the content widget a child of this widget
        contentWidget.setParent(self)
        wind.onAttachSignal.disconnect()
        wind.do_close()
        del self.detachedTabs[name]

        self.attachTab(contentWidget, name, icon, index)

    def closeDetachedTabs(self):
        """Slot responsible for clsing detached tabs."""
        for dettab, _ in self.detachedTabs.values():
            dettab.do_close()


class DetachedTab(SiriusMainWindow):
    """Reimplement SiriusMainWindow to accomodated detached tabs."""
    onAttachSignal = Signal(str)

    def __init__(self, name, text, contentWidget, parent=None):
        """."""
        SiriusMainWindow.__init__(self, parent)
        self._do_close = False
        self.setObjectName(name[:2] + 'App')
        self.setWindowTitle(text)

        self.menuBar().addAction('Attach Tab', self._retach_tab)
        self.contentWidget = contentWidget
        self.setCentralWidget(self.contentWidget)
        self.contentWidget.show()

    def do_close(self):
        """."""
        self._do_close = True
        self.close()

    def closeEvent(self, event):
        """."""
        if self._do_close:
            event.accept()
        else:
            event.ignore()
            # self._retach_tab()
            QMessageBox.information(
                self, 'Operation not Permitted',
                'It is not possible to close this window.\n' +
                'Please click in the MenuBar option "Attach Tab" '+
                'to re-attach it to the original TabWidget.')

    @Slot()
    def _retach_tab(self):
        self.onAttachSignal.emit(self.windowTitle())


class TabBar(QTabBar):
    """Reimplement QTabBar to add DoubleClickEvent handling."""
    onDetachTabSignal = Signal(int, QPoint)

    def __init__(self, parent=None):
        """."""
        QTabBar.__init__(self, parent)

        self.setAcceptDrops(True)
        self.setToolTip('Double click to detach Tab.')
        self.setElideMode(Qt.ElideRight)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectLeftTab)

        self.mouseCursor = QCursor()

    def mouseDoubleClickEvent(self, event):
        """."""
        event.accept()
        self.onDetachTabSignal.emit(
            self.tabAt(event.pos()), self.mouseCursor.pos())
