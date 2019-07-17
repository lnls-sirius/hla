import re
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, \
    QScrollArea, QGroupBox, QLabel, QGridLayout, QSizePolicy as QSzPol, \
    QFrame, QLineEdit, QPushButton, QMenu
from pydm.widgets import PyDMEnumComboBox
from pydm.widgets.base import PyDMPrimitiveWidget
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusLabel, SiriusSpinbox


class BaseWidget(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        try:
            self.prefix = _PVName(prefix)
        except Exception:
            self.prefix = prefix

    def channels(self):
        return self._chans

    def get_pvname(self, propty):
        return self.prefix + ':' + propty

    def _create_formlayout_groupbox(self, title, props):
        grpbx = CustomGroupBox(title, self)
        fbl = QFormLayout(grpbx)
        grpbx.layoutf = fbl
        fbl.setLabelAlignment(Qt.AlignVCenter)
        for pv1, txt in props:
            hbl = QHBoxLayout()
            not_enum = pv1.endswith('-SP')
            pv2 = pv1.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if pv2 != pv1:
                if not_enum:
                    chan1 = self.get_pvname(pv1)
                    wid = MySpinBox(self, init_channel=chan1)
                    wid.showStepExponent = False
                    wid.limitsFromChannel = False
                else:
                    wid = MyComboBox(self, init_channel=self.get_pvname(pv1))
                    wid.setStyleSheet("""min-width:4.8em;""")
                wid.setObjectName(pv1.replace('-', ''))
                hbl.addWidget(wid)

            lab = SiriusLabel(self, init_channel=self.get_pvname(pv2))
            lab.setObjectName(pv2.replace('-', ''))
            lab.showUnits = True
            lab.setStyleSheet("""min-width:5.5em;""")
            hbl.addWidget(lab)
            lab = QLabel(txt)
            lab.setObjectName(pv1.split('-')[0])
            lab.setStyleSheet("""min-width:7em;""")
            fbl.addRow(lab, hbl)
        return grpbx


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
        try:
            self.prefix = _PVName(prefix)
        except Exception:
            self.prefix = prefix
        self.props = props or set(self._ALL_PROPS)
        self.has_search = has_search
        self.props2search = set(props2search) or set()
        self.obj_names = obj_names
        self.setupUi()

    def setupUi(self):
        self.my_layout = QVBoxLayout(self)
        self.my_layout.setContentsMargins(6, 10, 6, 0)
        self.my_layout.setSpacing(15)

        if self.has_search:
            hbl = QHBoxLayout()
            self.my_layout.addItem(hbl)
            # Create search bar
            self.search_lineedit = QLineEdit(parent=self)
            hbl.addWidget(self.search_lineedit)
            self.search_lineedit.setPlaceholderText("Search...")
            self.search_lineedit.textEdited.connect(self.filter_lines)
            # Create search menu
            pbt = QPushButton('Show Columns', self)
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
        headerlay = QHBoxLayout()
        headerlay.setContentsMargins(0, 0, 0, 0)
        self.my_layout.addLayout(headerlay)
        objs = self.getLine(header=True)
        for prop, obj in objs:
            headerlay.addLayout(obj)
            for idx in range(obj.count()):
                wid = obj.itemAt(idx).widget()
                wid.setStyleSheet(
                    'min-width: {0:.1f}em; max-width: {0:.1f}em;'.format(
                        self._MIN_WIDs[prop]))

        # Create scrollarea
        sc_area = QScrollArea()
        sc_area.setWidgetResizable(True)
        sc_area.setFrameShape(QFrame.NoFrame)
        self.my_layout.addWidget(sc_area)

        # ScrollArea Widget
        wid = QWidget()
        sc_area.setWidget(wid)
        wid.setObjectName('wid')
        wid.setStyleSheet('#wid {background-color: transparent;}')
        lay = QVBoxLayout()
        lay.setSpacing(15)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignTop)
        wid.setLayout(lay)

        self.lines = dict()
        self.filtered_lines = set()
        for obj_name in self.obj_names:
            pref = _PVName(self.prefix + obj_name)
            objs = self.getLine(pref)
            self.lines[pref] = objs
            self.filtered_lines.add(pref)
            hlay = QHBoxLayout()
            lay.addLayout(hlay)
            for prop, obj in objs:
                hlay.addLayout(obj)
                for idx in range(obj.count()):
                    wid = obj.itemAt(idx).widget()
                    wid.setStyleSheet(
                        'min-width: {0:.1f}em; max-width: {0:.1f}em;'.format(
                            self._MIN_WIDs[prop]))

    def getLine(self, prefix=None, header=False):
        objects = list()
        for prop in self._ALL_PROPS:
            item = self.getColumn(prefix, prop, header)
            if item is not None:
                objects.append([prop, item])
        return objects

    def getColumn(self, prefix, prop, header):
        lv = QVBoxLayout()
        lv.setSpacing(6)
        lv.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        fun = self._createObjs if not header else self._headerLabel
        objs = fun(prefix, prop)
        visi = prop in self.props
        for i, ob in enumerate(objs):
            lv.addWidget(ob)
            ob.setVisible(visi)
            ob.setObjectName(prop)
            ob.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        return lv

    def filter_columns(self):
        txt = self.sender().text()
        visi = self.sender().isChecked()
        objs = self.findChildren(QWidget, txt, Qt.FindDirectChildrenOnly)
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
            for prop, lay in objs:
                if keep:
                    self.filtered_lines.add(line)
                    break
                if prop not in self.props2search:
                    continue
                cnt = lay.count()
                wid = lay.itemAt(cnt-1).widget()
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
        props = {act.text() for act in self.search_menu.actions() if act.isChecked()}
        for key, objs in self.lines.items():
            if key in self.filtered_lines:
                for _, layout in objs:
                    for idx in range(layout.count()):
                        wid = layout.itemAt(idx).widget()
                        wid.setVisible(wid.objectName() in props)
            else:
                for _, layout in objs:
                    for idx in range(layout.count()):
                        wid = layout.itemAt(idx).widget()
                        wid.setVisible(False)
        # self.adjustSize()

    def _headerLabel(self, prefix, prop):
        lb = QLabel('<h4>' + self._LABELS[prop] + '</h4>', self)
        lb.setStyleSheet("""min-height:1.55em; max-height:1.55em;""")
        lb.setAlignment(Qt.AlignHCenter)
        return (lb, )

    def _createObjs(self, prefix, prop):
        return tuple()  # return tuple of widgets


class MySpinBox(SiriusSpinbox):
    """Subclass QDoubleSpinBox to reimplement whellEvent."""

    def __init__(self, parent, init_channel=None):
        """Initialize object."""
        super().__init__(parent=parent, init_channel=init_channel)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


class MyComboBox(PyDMEnumComboBox):
    """Subclass PyDMEnumComboBox to reimplement whellEvent."""

    def __init__(self, parent, init_channel=None):
        """Initialize object."""
        super().__init__(parent=parent, init_channel=init_channel)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)
