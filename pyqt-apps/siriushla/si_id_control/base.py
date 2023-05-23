"""ID Common classes module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QPushButton, QVBoxLayout

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import IDSearch

from siriushla.util import connect_newprocess
from siriushla.widgets import SiriusMainWindow, SiriusLedState, \
    PyDMStateButton, SiriusDialog

from .util import get_id_icon


class IDCommonControlWindow(SiriusMainWindow):
    """ID Common Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._device = _PVName(device)
        self._beamline = IDSearch.conv_idname_2_beamline(self._device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self.setWindowTitle(device+' Control Window - '+self._beamline)
        self.setObjectName('IDApp')
        self.setWindowIcon(get_id_icon())
        self._setupUi()

    def _setupUi(self):
        self._label_title = QLabel(
            '<h3>'+self._device+' Control - '+self._beamline+'</h3 >', self,
            alignment=Qt.AlignCenter)
        self._label_title.setStyleSheet('max-height:1.29em;')

        vlay1 = QVBoxLayout()
        vlay1.addWidget(self._mainControlsWidget())
        try:
            aux_cmds = self._auxCommandsWidget()
            vlay1.addWidget(aux_cmds)
        except NotImplementedError:
            pass

        vlay2 = QVBoxLayout()
        try:
            ctrl_mode = self._ctrlModeWidget()
            vlay2.addWidget(ctrl_mode)
        except NotImplementedError:
            pass
        vlay2.addWidget(self._beamLinesCtrlWidget())
        try:
            status = self._statusWidget()
            vlay2.addWidget(status)
        except NotImplementedError:
            pass

        cwid = QWidget()
        self.setCentralWidget(cwid)
        lay = QGridLayout(cwid)
        lay.addWidget(self._label_title, 0, 0, 1, 2)
        lay.addLayout(vlay1, 1, 0)
        lay.addLayout(vlay2, 1, 1)

        try:
            ffsett = self._ffSettingsWidget()
            lay.addWidget(ffsett, 2, 0, 1, 2)
        except NotImplementedError:
            pass

    def _mainControlsWidget(self):
        raise NotImplementedError

    def _statusWidget(self):
        raise NotImplementedError

    def _ctrlModeWidget(self):
        raise NotImplementedError

    def _beamLinesCtrlWidget(self):
        self._ld_blinesenbl = QLabel('Enable', self)
        self._sb_blinesenbl = PyDMStateButton(
            self, self.dev_pref.substitute(propty='BeamLineCtrlEnbl-Sel'))
        self._led_blinesenbl = SiriusLedState(
            self, self.dev_pref.substitute(propty='BeamLineCtrlEnbl-Sts'))
        self._ld_blinesmon = QLabel('Status', self)
        self._led_blinesmon = SiriusLedState(
            self, self.dev_pref.substitute(propty='BeamLineCtrl-Mon'))

        gbox_blines = QGroupBox('Beam Lines Control', self)
        lay_blines = QGridLayout(gbox_blines)
        lay_blines.addWidget(self._ld_blinesenbl, 0, 0)
        lay_blines.addWidget(self._sb_blinesenbl, 0, 1)
        lay_blines.addWidget(self._led_blinesenbl, 0, 2)
        lay_blines.addWidget(self._ld_blinesmon, 1, 0)
        lay_blines.addWidget(self._led_blinesmon, 1, 1, 1, 2)
        return gbox_blines

    def _auxCommandsWidget(self):
        raise NotImplementedError

    def _ffSettingsWidget(self):
        raise NotImplementedError


class IDCommonDialog(SiriusDialog):
    """ID Common Auxiliary Dialog."""

    def __init__(self, parent=None, prefix='', device='', title=''):
        super().__init__(parent)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self.setObjectName('IDApp')
        self.setWindowTitle(title)
        self._setupUi()

    def _setupUi(self):
        raise NotImplementedError


class IDCommonSummaryBase(QWidget):
    """ID Common Summary Widget."""

    MODEL_WIDTHS = ()

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.setObjectName('IDApp')
        self.prop2width = (
            ('Beamline', 8),
            ('Device', 8),
        ) + self.MODEL_WIDTHS + (
            ('Moving', 4),
            ('BeamLine Enable', 6),
            ('Beamline Control', 4),
        )


class IDCommonSummaryHeader(IDCommonSummaryBase):
    """ID Common Summary Header."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._setupUi()

    def _setupUi(self):
        layout = QHBoxLayout(self)
        for name, size in self.prop2width:
            text = name.replace(' ', '\n')
            label = QLabel(text, self, alignment=Qt.AlignCenter)
            label.setStyleSheet(
                'min-width:{0}em; max-width:{0}em;'
                'font-weight:bold;'.format(str(size)))
            label.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Preferred)
            layout.addWidget(label)


class IDCommonSummaryWidget(IDCommonSummaryBase):
    """ID Common Summary Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._device = _PVName(device)
        self._beamline = IDSearch.conv_idname_2_beamline(self._device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _get_widgets(self, prop):
        wids = list()
        orientation = 'v'
        if prop == 'Beamline':
            lbl = QLabel(
                '<h4>'+self._beamline+'</h4>', self, alignment=Qt.AlignCenter)
            wids.append(lbl)
        elif prop == 'Device':
            btn = QPushButton(self._device, self)
            connect_newprocess(
                btn, ['sirius-hla-si-id-control.py', '-dev', self._device])
            wids.append(btn)
        elif prop == 'Moving':
            led = SiriusLedState(
                self, self.dev_pref.substitute(propty='Moving-Mon'))
            wids.append(led)
        elif prop == 'BeamLine Enable':
            self._sb_blenbl = PyDMStateButton(
                self, self.dev_pref.substitute(propty='BeamLineCtrlEnbl-Sel'))
            wids.append(self._sb_blenbl)
            led = SiriusLedState(
                self, self.dev_pref.substitute(propty='BeamLineCtrlEnbl-Sts'))
            wids.append(led)
            orientation = 'h'
        elif prop == 'Beamline Control':
            led = SiriusLedState(
                self, self.dev_pref.substitute(propty='BeamLineCtrl-Mon'))
            wids.append(led)
        return wids, orientation

    def _setupUi(self):
        layout = QHBoxLayout(self)
        for prop, width in self.prop2width:
            objname = prop.replace(' ', '')
            items, orientation = self._get_widgets(prop)

            widget = QWidget(self)
            lay = QVBoxLayout() if orientation == 'v' else QHBoxLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setAlignment(Qt.AlignCenter)
            lay.setSpacing(0)
            widget.setLayout(lay)

            for item in items:
                lay.addWidget(item)

            widget.setObjectName(objname)
            widget.setStyleSheet(
                '#{0}{{min-width:{1}em; max-width:{1}em;}}'.format(
                    objname, str(width)))
            layout.addWidget(widget)

    def enable_beamline_control(self):
        """Enable beamline control."""
        if self._sb_blenbl.isEnabled():
            if not self._sb_blenbl.value:
                self._sb_blenbl.send_value()

    def disable_beamline_control(self):
        """Disable beamline control."""
        if self._sb_blenbl.isEnabled():
            if self._sb_blenbl.value:
                self._sb_blenbl.send_value()
