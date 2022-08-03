"""."""
import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, \
    QScrollArea, QGroupBox, QLabel, QSizePolicy as QSzPol, QFrame, QMenu, \
    QLineEdit, QPushButton
import qtawesome as qta
from pydm.widgets.base import PyDMPrimitiveWidget

from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusLabel, SiriusSpinbox, SiriusEnumComboBox


class BaseWidget(QWidget):

    def __init__(self, parent=None, device='', prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)

    def channels(self):
        return self._chans

    def get_pvname(self, propty, field=''):
        return self.device.substitute(
            prefix=self.prefix, propty=propty, field=field)

    def _create_propty_layout(self, propty, width=6.0, show_unit=True):
        """Return layout that handles a property according to 'propty_type'."""
        layout = QHBoxLayout()
        not_enum = propty.endswith('-SP')
        pv2 = propty.replace('-SP', '-RB').replace('-Sel', '-Sts')

        style = 'min-width:{0}em; max-width:{0}em;\
            min-height:1.29em;'.format(str(width))

        if pv2 != propty:
            chan1 = self.get_pvname(propty)
            if not_enum:
                wid = SiriusSpinbox(self, init_channel=chan1)
                wid.showStepExponent = False
                wid.setAlignment(Qt.AlignCenter)
            else:
                wid = SiriusEnumComboBox(self, init_channel=chan1)
            wid.setStyleSheet(style)
            layout.addWidget(wid)

        label = SiriusLabel(
            parent=self, init_channel=self.get_pvname(pv2))
        label.setStyleSheet(style)
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName(pv2.replace('-', ''))
        label.showUnits = show_unit
        layout.addWidget(label)

        layout.setAlignment(Qt.AlignVCenter)
        return layout

    def _create_small_group(
            self, name, parent, wids, align_ver=True, no_marg=False):
        group = QGroupBox(name, parent) if name else QWidget(parent)
        lay = QVBoxLayout(group) if align_ver else QHBoxLayout(group)
        if align_ver:
            lay.setAlignment(Qt.AlignCenter)
        for wid in wids:
            lay.addWidget(wid)
            lay.setAlignment(wid, Qt.AlignCenter)
        if no_marg:
            lay.setContentsMargins(0, 0, 0, 0)
        return group


class CustomGroupBox(QGroupBox, PyDMPrimitiveWidget):

    def __init__(self, title, parent=None):
        QGroupBox.__init__(self, title, parent)
        PyDMPrimitiveWidget.__init__(self)


class BaseList(CustomGroupBox):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {}
    _LABELS = {}
    _ALL_PROPS = tuple()

    def __init__(self, name=None, parent=None, prefix='', props=set(),
                 obj_names=list(), has_search=True, props2search=set()):
        """Initialize object."""
        super().__init__(name, parent)
        self.prefix = prefix
        self.props = props or set(self._ALL_PROPS)
        self.has_search = has_search
        self.props2search = set(props2search) or set()
        self.obj_names = obj_names
        self.setupUi()

    def setupUi(self):
        self.my_layout = QVBoxLayout(self)
        self.my_layout.setContentsMargins(6, 10, 6, 0)

        if self.has_search:
            hbl = QHBoxLayout()
            hbl.setSpacing(0)
            self.my_layout.addLayout(hbl)
            # Create search bar
            self.search_lineedit = QLineEdit(parent=self)
            hbl.addWidget(self.search_lineedit)
            self.search_lineedit.setPlaceholderText("Search...")
            self.search_lineedit.textEdited.connect(self.filter_lines)
            # Create search menu
            pbt = QPushButton('  ', self)
            pbt.setToolTip('Choose which columns to show')
            pbt.setObjectName('but')
            pbt.setIcon(qta.icon('mdi.view-column'))
            pbt.setStyleSheet("""
                #but{
                    min-width:35px; max-width:35px;
                    min-height:25px; max-height:25px;
                    icon-size:25px;
                }""")
            hbl.addWidget(pbt)
            self.search_menu = QMenu(pbt)
            self.search_menu.triggered.connect(self.filter_lines)
            pbt.setMenu(self.search_menu)
            for prop in self._ALL_PROPS:
                act = self.search_menu.addAction(prop)
                act.setCheckable(True)
                act.setChecked(prop in self.props)
                act.toggled.connect(self.filter_columns)

        # Create header
        header = QWidget()
        headerlay = QHBoxLayout(header)
        headerlay.setContentsMargins(0, 0, 0, 0)
        self.my_layout.addWidget(header, alignment=Qt.AlignLeft)
        objs = self.getLine(header=True)
        for prop, obj in objs:
            name = obj.objectName()
            obj.setStyleSheet("""
                #{0:s}{{
                    min-width:{1:.1f}em; max-width: {1:.1f}em;
                    min-height:1.8em; max-height:1.8em;
                }}""".format(name, self._MIN_WIDs[prop]))
            headerlay.addWidget(obj)

        # Create scrollarea
        sc_area = QScrollArea()
        sc_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sc_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sc_area.setWidgetResizable(True)
        sc_area.setFrameShape(QFrame.NoFrame)
        self.my_layout.addWidget(sc_area)

        # ScrollArea Widget
        wid = QWidget()
        wid.setObjectName('wid')
        wid.setStyleSheet('#wid {background-color: transparent;}')
        lay = QVBoxLayout(wid)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignTop)
        sc_area.setWidget(wid)

        self.lines = dict()
        self.filtered_lines = set()
        for obj_name in self.obj_names:
            pref = _PVName(obj_name).substitute(prefix=self.prefix)
            objs = self.getLine(pref)
            self.lines[pref] = objs
            self.filtered_lines.add(pref)
            lwid = QWidget()
            hlay = QHBoxLayout(lwid)
            hlay.setContentsMargins(0, 0, 0, 0)
            for prop, obj in objs:
                name = obj.objectName()
                obj.setStyleSheet("""
                    #{0:s}{{
                        min-width:{1:.1f}em; max-width: {1:.1f}em;
                    }}""".format(name, self._MIN_WIDs[prop]))
                hlay.addWidget(obj)
            lay.addWidget(lwid, alignment=Qt.AlignLeft)

    def getLine(self, device=None, header=False):
        objects = list()
        for prop in self._ALL_PROPS:
            widget = self.getColumn(device, prop, header)
            if widget is not None:
                objects.append([prop, widget])
        return objects

    def getColumn(self, device, prop, header):
        widget = QWidget(self)
        widget.setObjectName(prop)
        widget.setVisible(prop in self.props)
        widget.setSizePolicy(QSzPol.Fixed, QSzPol.Fixed)
        lay = QVBoxLayout(widget)
        lay.setSpacing(6)
        lay.setContentsMargins(0, 6, 0, 6)
        lay.setAlignment(Qt.AlignCenter)
        fun = self._createObjs if not header else self._headerLabel
        for obj in fun(device, prop):
            lay.addWidget(obj)
            obj.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        return widget

    def filter_columns(self):
        txt = self.sender().text()
        visi = self.sender().isChecked()
        objs = self.findChildren(QWidget, txt)
        for obj in objs:
            objname = obj.objectName()
            if objname.startswith(txt):
                obj.setVisible(visi)

    def filter_lines(self, text):
        """Filter lines according to the regexp filter."""
        text = self.search_lineedit.text()
        try:
            pattern = re.compile(text, re.I)
        except Exception:
            return

        self.filtered_lines.clear()
        for line, objs in self.lines.items():
            keep = False
            for prop, obj in objs:
                if keep:
                    self.filtered_lines.add(line)
                    break
                if prop not in self.props2search:
                    continue
                cnt = obj.layout().count()
                wid = obj.layout().itemAt(cnt-1).widget()
                if hasattr(wid, 'text'):
                    keep |= bool(pattern.search(wid.text()))
                    continue
                elif hasattr(wid, 'enum_strings') and hasattr(wid, 'value'):
                    conds = wid.enum_strings is not None
                    if conds:
                        conds &= isinstance(wid.value, int)
                        conds &= wid.value < len(wid.enum_strings)
                    if conds:
                        enum = wid.enum_strings[wid.value]
                        keep |= bool(pattern.search(enum))
                        continue
        self._set_lines_visibility()

    def _set_lines_visibility(self):
        props = {
            a.text() for a in self.search_menu.actions() if a.isChecked()}
        for key, objs in self.lines.items():
            if key in self.filtered_lines:
                for _, wid in objs:
                    wid.setVisible(wid.objectName() in props)
            else:
                for _, wid in objs:
                    wid.setVisible(False)

    def _headerLabel(self, device, prop):
        lbl = QLabel('<h4>' + self._LABELS[prop] + '</h4>', self)
        lbl.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        return (lbl, )

    def _createObjs(self, device, prop):
        return tuple()  # return tuple of widgets
