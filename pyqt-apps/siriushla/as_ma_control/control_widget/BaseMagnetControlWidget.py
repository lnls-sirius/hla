"""Base class for controlling a magnet."""
import re

from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from pydm.PyQt.QtCore import Qt, QPoint, pyqtSlot,QLocale
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QGroupBox, \
    QGridLayout, QLabel, QHBoxLayout, QScrollArea, QLineEdit, QAction, \
    QMenu, QInputDialog


class BaseMagnetControlWidget(QWidget):
    """Base widget class to control magnet."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    StyleSheet = """
    """

    def __init__(self, magnet_list, orientation=0, parent=None):
        """Class constructor.

        Parameters:
        magnet list - a list of magnets, will be filtered based on patterns
                      defined in the subclass;
        orientation - how the different groups(defined in subclasses) will be
                      laid out.
        """
        super(BaseMagnetControlWidget, self).__init__(parent)
        self._orientation = orientation
        self._magnet_list = magnet_list
        # Data structures used to filter the widgets
        self.widgets_list = dict()
        self.filtered_widgets = set()  # Set with key of visible widgets
        # Setup the UI and apply css
        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)
        # Set custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    @pyqtSlot(str)
    def filter_magnets(self, text):
        """Filter magnet widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception as e:  # Ignore malformed patterns?
            pattern = re.compile("malformed")
        # Clear filtered widgets and add the ones that match the new pattern
        self.filtered_widgets.clear()
        for widget in self.widgets_list:
            if pattern.search(widget):
                self.filtered_widgets.add(widget)
        # Set widgets visibility and the number of widgets matched
        self.set_widgets_visibility()
        self.count_label.setText(
            "Showing {} magnets".format(len(self.filtered_widgets)))
        # Sroll to top
        for scroll_area in self.findChildren(QScrollArea):
            scroll_area.verticalScrollBar().setValue(0)

    def set_widgets_visibility(self):
        """Set visibility of the widgets."""
        for key, widget in self.widgets_list.items():
            if key in self.filtered_widgets:
                widget.setVisible(True)
            else:
                widget.setVisible(False)

    @pyqtSlot(bool)
    def pwrstate_action(self, state):
        """Execute actions from context menu."""
        for key, widget in self.widgets_list.items():
            if key in self.filtered_widgets:
                widget.pwrstate_button.sendValue(state)

    @pyqtSlot()
    def set_current_sp_action(self):
        """Set current setpoint for every visible widget."""
        dlg = QInputDialog(self)
        dlg.setLocale(QLocale(QLocale.English))
        new_value, ok = dlg.getDouble(
            self, "Insert current setpoint", "Value")
        if ok:
            for key, widget in self.widgets_list.items():
                if key in self.filtered_widgets:
                    widget.analog_widget.sp_lineedit.setText(str(new_value))
                    widget.analog_widget.sp_lineedit.sendValue()

    @pyqtSlot(QPoint)
    def show_context_menu(self, point):
        """Show a custom context menu."""
        menu = QMenu("Actions", self)

        turn_on = QAction("Turn On", self)
        turn_on.triggered.connect(lambda: self.pwrstate_action(True))
        turn_off = QAction("Turn Off", self)
        turn_off.triggered.connect(lambda: self.pwrstate_action(False))
        set_current_sp = QAction("Set Current SP", self)
        set_current_sp.triggered.connect(self.set_current_sp_action)
        menu.addAction(turn_on)
        menu.addAction(turn_off)
        menu.addAction(set_current_sp)

        menu.popup(self.mapToGlobal(point))

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.magnets_layout = self._getLayout()

        self.search_lineedit = QLineEdit(parent=self)
        self.search_lineedit.setObjectName("search_lineedit")
        self.search_lineedit.setPlaceholderText("Search for a magnet...")
        self.search_lineedit.textEdited.connect(self.filter_magnets)

        self.count_label = QLabel(parent=self)

        self.layout.addWidget(self.search_lineedit)
        self.layout.addWidget(self.count_label)
        self.layout.addLayout(self.magnets_layout)

        # Build Magnet Layout
        groups = self._getGroups()

        # Create group boxes and pop. layout
        for idx, group in enumerate(groups):

            # Get magnets that belong to group
            magnets = list()
            element_list = self._getElementList()
            pattern = re.compile(group[1])
            for el in element_list:
                if pattern.search(el):
                    magnets.append(el)

            # Loop magnets to create all the widgets of a groupbox
            group_widgets = list()
            for n, ma in enumerate(magnets):
                magnet_widget = MagnetWidget(maname=ma, parent=self)
                group_widgets.append(magnet_widget)
                self.widgets_list[ma] = magnet_widget
                self.filtered_widgets.add(ma)

            # Create group and scroll area
            group_box = self._createGroupBox(group[0], group_widgets)
            if self._hasScrollArea():
                widget = QScrollArea()
                widget.setWidget(group_box)
            else:
                widget = group_box

            # Add group box or scroll area to grid layout
            if self._orientation == self.SQUARE:
                if idx % 2 == 0:
                    self.magnets_layout.addWidget(widget, int(idx), 0)
                else:
                    self.magnets_layout.addWidget(widget, int(idx/2), 1)
            else:
                self.magnets_layout.addWidget(widget)

        self.count_label.setText(
            "Showing {} magnets.".format(len(self.widgets_list)))

        self.setLayout(self.layout)

    def _createGroupBox(self, title, widget_group):
        group_box = QGroupBox(title)
        group_box.layout = QVBoxLayout()
        for line, widget in enumerate(widget_group):
            group_box.layout.addWidget(widget)
        group_box.layout.addStretch()
        group_box.setLayout(group_box.layout)

        return group_box

    def _getElementList(self):
        return filter(lambda magnet: re.match(
            self._getPattern(), magnet), self._magnet_list)

    def _getSection(self, name):
        section = name.split(":")[0].split("-")[1][:2]
        try:
            int(section)
        except Exception:
            return 0

        return int(section)

    def _getLayout(self):
        if self._orientation == self.SQUARE:
            return QGridLayout()
        elif self._orientation == self.HORIZONTAL:
            return QHBoxLayout()
        else:
            return QVBoxLayout()
