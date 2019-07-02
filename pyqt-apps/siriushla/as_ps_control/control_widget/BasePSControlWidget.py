"""Base class for controlling a power supply."""
import re

from epics import caput

from siriuspy.search import PSSearch, MASearch
from siriushla.as_ps_control.PSWidget import BasePSWidget, PSWidget, MAWidget
from qtpy.QtCore import Qt, QPoint, Slot, QLocale
from qtpy.QtWidgets import QWidget, QVBoxLayout, QGroupBox, \
    QGridLayout, QLabel, QHBoxLayout, QScrollArea, QLineEdit, QAction, \
    QMenu, QInputDialog, QFrame, QSplitter, QPushButton
from siriushla.as_ps_control.DCLinkWidget import \
    DCLinkWidget, DCLinkWidgetHeader


class PSContainer(QWidget):

    def __init__(self, widget, parent=None):
        super().__init__(parent)
        # Works for PS or MA
        self._widget = widget
        self._name = widget.psname

        if widget.psname in ['BO-Fam:MA-B', 'SI-Fam:MA-B1B2']:
            psname = self._name.replace(':MA-', ':PS-')
            psname = [psname + '-1', psname + '-2']
            self._dclinks = list()
            for name in psname:
                self._dclinks.extend(PSSearch.conv_psname_2_dclink(name))
        else:
            psname = self._name.replace(':MA-', ':PS-')
            self._dclinks = PSSearch.conv_psname_2_dclink(psname)

        self._setup_ui()
        self._create_actions()
        self.setStyleSheet("""
            #HideButton {
                min-width: 10px;
                max-width: 10px;
            }
            #DCLinkContainer {
                background-color: lightgrey;
            }
        """)

    def _setup_ui(self):
        """Setup widget UI."""
        self._layout = QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        # self._splitter = QSplitter(Qt.Vertical, self)

        self._dclink_container = QWidget(self)
        self._dclink_container.setObjectName('DCLinkContainer')
        self._dclink_container.setLayout(QVBoxLayout())
        if self._dclinks:
            self._dclink_container.layout().addWidget(DCLinkWidgetHeader(self))
            for dclink_name in self._dclinks:
                w = DCLinkWidget(dclink_name, self)
                self._dclink_container.layout().addWidget(w)

        # self._splitter.addWidget(self._widget)
        # self._splitter.addWidget(self._dclink_container)

        if self._dclinks:
            self._hide = QPushButton('+', self)
        else:
            self._hide = QPushButton('', self)
            self._hide.setEnabled(False)
        self._hide.setObjectName('HideButton')
        self._hide.setFlat(True)

        self._layout.addWidget(self._hide, 0, 0, Qt.AlignCenter)
        self._layout.addWidget(self._widget, 0, 1)
        self._layout.addWidget(self._dclink_container, 1, 1)

        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 99)

        # Configure
        self._dclink_container.setHidden(True)
        self._hide.clicked.connect(self._toggle_dclink)

    def _toggle_dclink(self):
        if self._dclink_container.isHidden():
            self._hide.setText('-')
            self._dclink_container.setHidden(False)
        else:
            self._hide.setText('+')
            self._dclink_container.setHidden(True)

    def _create_actions(self):
        self._turn_on_action = QAction('Turn DCLinks On', self)
        self._turn_on_action.triggered.connect(
            lambda: self._set_dclink_pwrstate(True))
        self._turn_off_action = QAction('Turn DCLinks Off', self)
        self._turn_off_action.triggered.connect(
            lambda: self._set_dclink_pwrstate(False))
        self._open_loop_action = QAction('Open DCLinks Control Loop', self)
        self._open_loop_action.triggered.connect(
            lambda: self._set_dclink_control_loop(False))
        self._close_loop_action = QAction('Close DCLinks Control Loop', self)
        self._close_loop_action.triggered.connect(
            lambda: self._set_dclink_control_loop(True))
        self._set_setpoint_action = QAction('Set DCLinks voltage', self)
        self._set_setpoint_action.triggered.connect(self._set_setpoint)
        self._reset_intlk_action = QAction('Reset DCLinks Interlocks', self)

    # Action methods
    def _set_dclink_pwrstate(self, value):
        for dclink in self.dclink_widgets():
            btn = dclink.state_btn
            if value:
                if not btn._bit_val:
                    btn.send_value()
            else:
                if btn._bit_val:
                    btn.send_value()

    def _set_dclink_control_loop(self, value):
        for dclink in self.dclink_widgets():
            btn = dclink.control_btn
            if value:
                if btn._bit_val:
                    btn.send_value()
            else:
                if not btn._bit_val:
                    btn.send_value()

    def _set_setpoint(self):
        """Set current setpoint for every visible widget."""
        dlg = QInputDialog(self)
        dlg.setLocale(QLocale(QLocale.English))
        new_value, ok = dlg.getDouble(
            self, "New setpoint", "Value")
        if ok:
            for dclink in self.dclink_widgets():
                sp = dclink.setpoint.sp_lineedit
                sp.setText(str(new_value))
                try:
                    sp.send_value()
                except TypeError:
                    pass

    def _reset_intlk(self):
        for dclink in self.dclink_widgets():
            dclink.reset.click()

    # Overloaded method
    def contextMenuEvent(self, event):
        """Overload to create a custom context menu."""
        widget = self.childAt(event.pos())
        parent = widget.parent()
        grand_parent = parent.parent()
        if widget.objectName() == 'DCLinkContainer' or \
                parent.objectName() == 'DCLinkContainer' or \
                grand_parent.objectName() == 'DCLinkContainer':
            menu = QMenu(self)
            menu.addAction(self._turn_on_action)
            menu.addAction(self._turn_off_action)
            menu.addSeparator()
            menu.addAction(self._close_loop_action)
            menu.addAction(self._open_loop_action)
            menu.addSeparator()
            menu.addAction(self._set_setpoint_action)
            menu.addSeparator()
            menu.addAction(self._reset_intlk_action)
            menu.popup(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def dclink_widgets(self):
        return self._dclink_container.findChildren(DCLinkWidget)


class BasePSControlWidget(QWidget):
    """Base widget class to control power supply."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

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
        if dev_type == 'PS':
            self._dev_list = PSSearch.get_psnames(self._getFilter())
            self._widget_class = PSWidget
        elif dev_type == 'MA':
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
                try:
                    if state:
                        widget.turn_on()
                    else:
                        widget.turn_off()
                except TypeError:
                    pass

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

    @Slot()
    def reset_interlocks(self):
        """Reset interlocks."""
        for key, widget in self.widgets_list.items():
            if key in self.filtered_widgets:
                try:
                    caput(widget.psname + ":Reset-Cmd", 1, timeout=100e-3)
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
        reset = QAction("Reset Interlocks", self)
        reset.triggered.connect(self.reset_interlocks)
        menu.addAction(turn_on)
        menu.addAction(turn_off)
        menu.addAction(set_current_sp)
        menu.addAction(reset)

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
                pscontainer = PSContainer(ps_widget, self)
                group_widgets.append(pscontainer)
                self.widgets_list[psname] = ps_widget
                self.filtered_widgets.add(psname)

            # Create group and scroll area
            main_widget = self._createGroupBox(group[0], group_widgets)
            main_widget.layout.setContentsMargins(0, 0, 0, 0)
            # main_widget.setAutoFillBackground(False)
            # if self._hasScrollArea():
            widget = QScrollArea(self)
            # widget.viewport().setAutoFillBackground(False)
            widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            widget.setWidgetResizable(True)
            widget.setFrameShape(QFrame.NoFrame)
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
        w.setObjectName('groupbox')
        w.setStyleSheet('#groupbox {background-color: transparent;}')
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
