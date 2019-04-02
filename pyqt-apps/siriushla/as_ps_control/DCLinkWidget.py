"""Widget with general functions of DCLink Widgets."""


from qtpy.QtWidgets import QHBoxLayout, QWidget, QPushButton, QStyle, \
    QStyleOption, QLabel
from qtpy.QtGui import QPainter
from pydm.widgets import PyDMPushButton, PyDMLabel

from siriuspy.pwrsupply.data import PSData
from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriushla.widgets import PyDMStateButton, SiriusLedState, \
    SiriusLedAlert, PyDMLinEditScrollbar


class DCLinkWidget(QWidget):
    """General widget for controlling a DCLink."""

    Stylesheet = """
        PyDMStateButton {
            min-width: 2.5em;
            max-width: 2.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
        PyDMLed {
            min-width: 1.5em;
            max-width: 1.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
        #DetailButton {
            min-width: 12em;
            max-width: 12em;
            margin-right: 0.5em;
        }
        #OpModeLabel {
            min-width: 8em;
            max-width: 8em;
            qproperty-alignment: AlignCenter;
        }
        #StateWidget {
            min-width: 8em;
            max-width: 8em;
        }
        #ControlWidget {
            min-width: 8em;
            max-width: 8em;
        }
        #IntlkWidget {
            min-width: 5em;
            max-width: 5em;
        }
        #SetpointWidget {
            min-width: 10em;
            max-width: 10em;
        }
        #ReadbackLabel {
            min-width: 10em;
            max-width: 10em;
            qproperty-alignment: AlignCenter;
        }
        #ResetIntlkButton {
            min-width: 4em;
            max-width: 4em;
        }
    """

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def __init__(self, name, parent=None):
        """Build UI with dclink name."""
        super().__init__(parent)
        self._name = name
        self._prefixed_name = VACA_PREFIX + name
        self._setup_ui()
        self.setStyleSheet(self.Stylesheet)

    def _create_pvs(self):
        self._pwrstate_sts = self._prefixed_name + ':PwrState-Sts'
        self._pwrstate_sel = self._prefixed_name + ':PwrState-Sel'
        self._ctrlloop_sts = self._prefixed_name + ':CtrlLoop-Sts'
        self._ctrlloop_sel = self._prefixed_name + ':CtrlLoop-Sel'
        self._opmode_sts = self._prefixed_name + ':OpMode-Sts'
        self._opmode_sel = self._prefixed_name + ':OpMode-Sel'
        self._soft_intlk = self._prefixed_name + ':IntlkSoft-Mon'
        self._hard_intlk = self._prefixed_name + ':IntlkHard-Mon'
        self._reset_intlk = self._prefixed_name + ':Reset-Cmd'

        sp = self._get_setpoint_name()
        self._analog_sp = self._prefixed_name + ':{}-SP'.format(sp)
        self._analog_mon = self._prefixed_name + ':{}-Mon'.format(sp)

    def _get_setpoint_name(self):
        model = PSData(self._name).psmodel
        if model == 'FBP_DCLink':
            return 'Voltage'
        elif model in ('FAC_ACDC', 'FAC_2S_ACDC', 'FAC_2P4S_ACDC'):
            return 'CapacitorBankVoltage'
        else:
            raise RuntimeError(
                'Undefined PS model {}setpoint PV name'.format(model))

    def _setup_ui(self):
        """Setups widget UI."""
        self._create_pvs()
        self._layout = QHBoxLayout()
        # self._layout.setSpacing(0)
        # self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        # Widgets
        self.detail_btn = QPushButton(self._name, self)
        self.detail_btn.setObjectName('DetailButton')
        self.opmode_label = PyDMLabel(self, self._opmode_sts)
        self.opmode_label.setObjectName('OpModeLabel')
        self.state_btn = PyDMStateButton(self, self._pwrstate_sel)
        self.state_led = SiriusLedState(self, self._pwrstate_sts)
        self.state_widget = self._build_horizontal_widget(
            [self.state_btn, self.state_led])
        self.control_btn = PyDMStateButton(
            self, self._ctrlloop_sel, invert=True)
        self.control_label = PyDMLabel(self, self._ctrlloop_sts)
        self.control_widget = self._build_horizontal_widget(
            [self.control_btn, self.control_label])
        self.control_widget.setObjectName('ControlWidget')
        self.state_widget.setObjectName('StateWidget')
        self.soft_intlk_led = SiriusLedAlert(self, self._soft_intlk)
        self.hard_intlk_led = SiriusLedAlert(self, self._hard_intlk)
        self.intlk_widget = self._build_horizontal_widget(
            [self.soft_intlk_led, self.hard_intlk_led])
        self.intlk_widget.setObjectName('IntlkWidget')
        self.setpoint = PyDMLinEditScrollbar(self._analog_sp, self)
        self.setpoint.setObjectName('SetpointWidget')
        self.setpoint.sp_scrollbar.setTracking(False)
        self.readback = PyDMLabel(self, self._analog_mon)
        self.readback.setObjectName('ReadbackLabel')
        self.reset = PyDMPushButton(
            self, 'Reset', init_channel=self._reset_intlk)
        self.reset.setObjectName('ResetIntlkButton')

        self._layout.addWidget(self.detail_btn)
        self._layout.addWidget(self.opmode_label)
        self._layout.addWidget(self.state_widget)
        self._layout.addWidget(self.control_widget)
        self._layout.addWidget(self.intlk_widget)
        self._layout.addWidget(self.setpoint)
        self._layout.addWidget(self.readback)
        self._layout.addWidget(self.reset)
        self._layout.addStretch()

    def _build_horizontal_widget(self, widgets):
        widget = QWidget(self)
        widget.setLayout(QHBoxLayout())
        for w in widgets:
            widget.layout().addWidget(w)
        return widget


class DCLinkWidgetHeader(QWidget):

    DETAIL_COL_WIDTH = '12'
    OPMODE_COL_WIDTH = '8'
    STATE_COL_WIDTH = '8'
    CONTROL_COL_WIDTH = '8'
    INTLK_COL_WIDTH = '5'
    SETPOINT_COL_WIDTH = '10'
    RESET_COL_WIDTH = '4'

    Labels = [
        'DCLink Name',
        'OpMode',
        'State',
        'Control Loop',
        'Interlocks',
        'Setpoint',
        'Readback',
        'Reset'
    ]

    Stylesheet = """
        #DCLinkNameHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + DETAIL_COL_WIDTH + """em;
            max-width: """ + DETAIL_COL_WIDTH + """em;
            margin-right: 0.5em;
        }
        #OpModeHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + OPMODE_COL_WIDTH + """em;
            max-width: """ + OPMODE_COL_WIDTH + """em;
        }
        #StateHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + STATE_COL_WIDTH + """em;
            max-width: """ + STATE_COL_WIDTH + """em;
        }
        #ControlLoopHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + CONTROL_COL_WIDTH + """em;
            max-width: """ + CONTROL_COL_WIDTH + """em;
        }
        #InterlocksHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + INTLK_COL_WIDTH + """em;
            max-width: """ + INTLK_COL_WIDTH + """em;
        }
        #SetpointHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + SETPOINT_COL_WIDTH + """em;
            max-width: """ + SETPOINT_COL_WIDTH + """em;
        }
        #ReadbackHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + SETPOINT_COL_WIDTH + """em;
            max-width: """ + SETPOINT_COL_WIDTH + """em;
        }
        #ResetHeader {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            min-width: """ + RESET_COL_WIDTH + """em;
            max-width: """ + RESET_COL_WIDTH + """em;
        }
    """

    def __init__(self, parent=None):
        """Build UI."""
        super().__init__(parent)
        self._setup_ui()
        self.setStyleSheet(self.Stylesheet)

    def _setup_ui(self):
        self.setLayout(QHBoxLayout())
        for label in DCLinkWidgetHeader.Labels:
            widget = QLabel(label, self)
            widget.setObjectName(label.replace(' ', '') + 'Header')
            self.layout().addWidget(widget)
        self.layout().addStretch()

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()

    w = DCLinkWidget('PA-RaPSF01:PS-DCLink-BO')
    w.show()
    sys.exit(app.exec_())
