"""Base class for controlling a magnet."""
import re

# from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QPushButton, \
    QGroupBox, QGridLayout, QLabel, QHBoxLayout, \
    QScrollArea
from pydm.widgets.label import PyDMLabel
from pydm.widgets.led import PyDMLed
from pydm.widgets.state_button import PyDMStateButton
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla.FloatSetPointWidget import FloatSetPointWidget


class BaseMagnetControlWidget(QWidget):
    """Base widget class to control magnet."""

    SQUARE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    STYLESHEET = """
        #header_widget QLabel {
            font-weight: bold;
        }
        #h_state,
        #state_widget {
            min-width: 150px;
            max-width: 150px;
        }
        #h_magnet_name,
        QPushButton {
            min-width: 300px;
            max-width: 300px;
        }
        #h_current_sp,
        #h_current_mon,
        #h_str_sp,
        #h_str_mon,
        FloatSetPointWidget,
        PyDMLabel {
            min-width: 250px;
            max-width: 250px;
        }
        #h_trim,
        QPushButton[text='>'] {
            min-width: 80px;
            max-width: 80px;
            padding-left: 0;
        }
        QGroupBox {
            min-width: 1600px;
        }
    """

    def __init__(self, magnet_list, orientation=0, parent=None):
        """Class constructor."""
        super(BaseMagnetControlWidget, self).__init__(parent)
        self._orientation = orientation
        self._magnet_list = magnet_list

        self._setupUi()
        self.setStyleSheet(self.STYLESHEET)

    def _setupUi(self):
        self.layout = self._getLayout()

        groups = self._getGroups()
        last_section = 0

        # Create group boxes and pop. layout
        for idx, group in enumerate(groups):

            # group[0] = name; group[1] = name pattern
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
                # Add section label widget for individual magnets
                if self._divideBySection():
                    section = self._getSection(ma)
                    if section != last_section:
                        last_section = section
                        section_label = QLabel(
                            "Section {:02d}:".format(section))
                        # Create a new line with a QLabel only
                        group_widgets.append(section_label)
                # Add magnet widgets
                group_widgets.append(self._createGroupWidgets(ma))

            # Create group and scroll area
            group_box = self._createGroupBox(
                group[0], self._getHeader(), group_widgets)
            if self._hasScrollArea():
                widget = QScrollArea()
                widget.setWidget(group_box)
                # widget.setMinimumWidth(800)
            else:
                widget = group_box

            # Add group box or scroll area to grid layout
            if self._orientation == self.SQUARE:
                if idx % 2 == 0:
                    self.layout.addWidget(widget, int(idx), 0)
                else:
                    self.layout.addWidget(widget, int(idx/2), 1)
            else:
                self.layout.addWidget(widget)

        self.setLayout(self.layout)

    def _createGroupWidgets(self, ma):

        prefixed_ma = _VACA_PREFIX + ma

        magnet_widget = QWidget()
        magnet_widget.layout = QHBoxLayout()
        magnet_widget.setLayout(magnet_widget.layout)

        # Create magnet widgets
        state_widget = QWidget(self)
        state_widget.setObjectName("state_widget")
        state_widget.layout = QHBoxLayout()
        state_widget.setLayout(state_widget.layout)
        state_button = PyDMStateButton(
            parent=self, init_channel="ca://" + prefixed_ma + ":PwrState-Sel")
        state_led = PyDMLed(
            parent=self, init_channel="ca://" + prefixed_ma + ":PwrState-Sts")
        state_widget.layout.addWidget(state_button)
        state_widget.layout.addWidget(state_led)
        name_label = QPushButton(ma, parent=self)
        name_label.setObjectName("label_" + ma)
        current_widget = FloatSetPointWidget(
            parent=self, channel="ca://" + prefixed_ma + ":Current-SP")
        current_rb = PyDMLabel(
            parent=self, init_channel="ca://" + prefixed_ma + ":Current-Mon")
        strength_name = self._getStrength()
        strength_widget = FloatSetPointWidget(
            parent=self,
            channel="ca://" + prefixed_ma + ":" + strength_name + "-SP")
        strength_rb = PyDMLabel(
            parent=self,
            init_channel="ca://" + prefixed_ma + ":" + strength_name + "-SP")

        # Setting
        current_widget.set_limits_from_pv(True)
        current_rb.precFromPV = True
        strength_widget.set_limits_from_pv(True)
        strength_rb.precFromPV = True

        magnet_widget.layout.addWidget(state_widget)
        magnet_widget.layout.addWidget(name_label)
        magnet_widget.layout.addWidget(current_widget)
        magnet_widget.layout.addWidget(current_rb)
        magnet_widget.layout.addWidget(strength_widget)
        magnet_widget.layout.addWidget(strength_rb)
        if self._hasTrimButton():
            trim_btn = QPushButton(">", self)
            trim_btn.setObjectName("trim_" + ma)
            magnet_widget.layout.addWidget(trim_btn)
        magnet_widget.layout.addStretch()

        return magnet_widget

    def _createGroupBox(self, title, headers, widget_group):
        group_box = QGroupBox(title)
        group_box.layout = QVBoxLayout()
        # Build header
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.layout = QHBoxLayout()

        header_ids = ["h_state", "h_magnet_name", "h_current_sp",
                      "h_current_mon", "h_str_sp", "h_str_mon", "h_trim"]

        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setObjectName(header_ids[col])
            header_widget.layout.addWidget(label)
        header_widget.layout.addStretch()
        header_widget.setLayout(header_widget.layout)
        # Set groupbox layout
        group_box.layout.addWidget(header_widget)
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
