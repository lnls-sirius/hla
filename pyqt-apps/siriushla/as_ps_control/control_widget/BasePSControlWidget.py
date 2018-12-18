"""Base class for controlling a power supply."""
import re

from siriuspy.search import PSSearch, MASearch
from siriushla.as_ps_control.PSWidget import BasePSWidget, PSWidget, MAWidget
from qtpy.QtGui import QPainter
from qtpy.QtCore import Qt, QPoint, Slot, QLocale
from qtpy.QtWidgets import QWidget, QVBoxLayout, QGroupBox, \
    QGridLayout, QLabel, QHBoxLayout, QScrollArea, QLineEdit, QAction, \
    QMenu, QInputDialog, QStyleOption, QStyle


class BasePSControlWidget(QWidget):
    """Base widget class to control power supply."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    PS = 0
    MA = 1

    StyleSheet = """
        QScrollArea {
            min-width: 75em;
        }
    """

    def __init__(self, dev_type, orientation=0, parent=None):
        """Class constructor.

        Parameters:
        psname_list - a list of power supplies, will be filtered based on
                      patterns defined in the subclass;
        orientation - how the different groups(defined in subclasses) will be
                      laid out.
        """
        super(BasePSControlWidget, self).__init__(parent)
        self._dev_type = dev_type
        self._orientation = orientation
        if dev_type == self.PS:
            self._dev_list = PSSearch.get_psnames(self._getFilter())
            self._widget_class = PSWidget
        elif dev_type == self.MA:
            self._dev_list = MASearch.get_manames(self._getFilter())
            self._widget_class = MAWidget
        else:
            raise ValueError("Invalid device type, must be either PS or MA.")
        # Data structures used to filter the widgets
        self.widgets_list = dict()
        self.filtered_widgets = set()  # Set with key of visible widgets
        # Setup the UI and apply css
        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)
        # Set custom context menu
        # TODO: maybe no here
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    @Slot(str)
    def filter_pwrsupplies(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
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
            "Showing {} power supplies".format(len(self.filtered_widgets)))
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

    @Slot(bool)
    def pwrstate_action(self, state):
        """Execute actions from context menu."""
        for key, widget in self.widgets_list.items():
            if key in self.filtered_widgets:
                if state:
                    widget.turn_on()
                else:
                    widget.turn_off()

    @Slot()
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
                    try:
                        widget.analog_widget.sp_lineedit.send_value()
                    except TypeError:
                        pass

    @Slot(QPoint)
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

    def get_ps_widgets(self):
        """Return PSWidget and MAWidget widgets."""
        return self.findChildren(BasePSWidget)

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.pwrsupplies_layout = self._getLayout()
        # Create search bar
        self.search_lineedit = QLineEdit(parent=self)
        self.search_lineedit.setObjectName("search_lineedit")
        self.search_lineedit.setPlaceholderText("Search for a power supply...")
        self.search_lineedit.textEdited.connect(self.filter_pwrsupplies)

        self.count_label = QLabel(parent=self)

        self.layout.addWidget(self.search_lineedit)
        self.layout.addWidget(self.count_label)
        self.layout.addLayout(self.pwrsupplies_layout)

        # Build power supply Layout
        groups = self._getGroups()

        # Create group boxes and pop. layout
        for idx, group in enumerate(groups):

            # Get power supplies that belong to group
            pwrsupplies = list()
            # element_list = self._getElementList()
            pattern = re.compile(group[1])
            for el in self._dev_list:
                if pattern.search(el):
                    pwrsupplies.append(el)

            # Loop power supply to create all the widgets of a groupbox
            group_widgets = list()
            for n, psname in enumerate(pwrsupplies):
                if n > 0:
                    ps_widget = self._widget_class(psname=psname,
                                                   parent=self, header=False)
                else:
                    ps_widget = self._widget_class(psname=psname, parent=self)
                group_widgets.append(ps_widget)
                self.widgets_list[psname] = ps_widget
                self.filtered_widgets.add(psname)

            # Create group and scroll area
            main_widget = self._createGroupBox(group[0], group_widgets)
            # main_widget.setAutoFillBackground(False)
            # if self._hasScrollArea():
            widget = QScrollArea(self)
            # widget.viewport().setAutoFillBackground(False)
            widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            widget.setWidgetResizable(True)
            widget.setWidget(main_widget)
            # else:
            #     widget = main_widget

            group_box = QGroupBox(group[0], parent=self)
            group_box.layout = QVBoxLayout()
            group_box.setLayout(group_box.layout)
            group_box.layout.addWidget(widget)

            # Add group box or scroll area to grid layout
            if self._orientation == self.SQUARE:
                if idx % 2 == 0:
                    self.pwrsupplies_layout.addWidget(group_box, int(idx), 0)
                else:
                    self.pwrsupplies_layout.addWidget(group_box, int(idx/2), 1)
            else:
                self.pwrsupplies_layout.addWidget(group_box)

        self.count_label.setText(
            "Showing {} power supplies.".format(len(self.widgets_list)))

        self.setLayout(self.layout)

    def _createGroupBox(self, title, widget_group):
        w = QWidget(self)
        w.layout = QVBoxLayout()
        w.setLayout(w.layout)
        for line, widget in enumerate(widget_group):
            w.layout.addWidget(widget)
        w.layout.addStretch()

        return w

    # def _getElementList(self):
    #     return filter(lambda ps: re.match(
    #         self._getPattern(), ps), self._psname_list)

    # def _getSection(self, name):
    #     section = name.split(":")[0].split("-")[1][:2]
    #     try:
    #         int(section)
    #     except Exception:
    #         return 0
    #
    #     return int(section)

    def _getLayout(self):
        if self._orientation == self.SQUARE:
            return QGridLayout()
        elif self._orientation == self.HORIZONTAL:
            return QHBoxLayout()
        else:
            return QVBoxLayout()
