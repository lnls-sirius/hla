"""Base class for controlling a magnet."""
import re

# from pydm.PyQt.QtCore import Qt
from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QGroupBox, \
    QGridLayout, QLabel, QHBoxLayout, QScrollArea, QLineEdit


class BaseMagnetControlWidget(QWidget):
    """Base widget class to control magnet."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    StyleSheet = """
    """

    def __init__(self, magnet_list, orientation=0, parent=None):
        """Class constructor."""
        super(BaseMagnetControlWidget, self).__init__(parent)
        self._orientation = orientation
        self._magnet_list = magnet_list
        self.widgets_list = dict()

        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)

    @pyqtSlot(str)
    def filter_magnets(self, text):
        """Filter magnet widgets based on text inserted at line edit."""
        count = 0
        try:
            pattern = re.compile(text, re.I)
        except Exception as e:
            print("{}".format(e))
            pattern = re.compile(re.escape(text), re.I)
        for key, widget in self.widgets_list.items():
            # if text.lower() in key.lower():
            if pattern.match(key):
                widget.setVisible(True)
                count += 1
            else:
                widget.setVisible(False)
        self.count_label.setText("Showing {} magnets".format(count))

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
