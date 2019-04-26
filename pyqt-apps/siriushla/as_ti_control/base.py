import re
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, \
    QScrollArea, QGroupBox, QLabel, QGridLayout, QSizePolicy as QSzPol, \
    QFrame, QLineEdit
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
        wid = QWidget()
        glay = QGridLayout()
        glay.setVerticalSpacing(30)
        glay.setHorizontalSpacing(30)
        glay.setContentsMargins(0, 0, 0, 0)
        glay.setAlignment(Qt.AlignTop)
        wid.setLayout(glay)

        self.lines = dict()
        self.filtered_lines = set()
        for i, obj_name in enumerate(self.obj_names, 1):
            pref = _PVName(self.prefix + obj_name)
            objs = self.getLine(pref)
            self.lines[pref] = objs
            self.filtered_lines.add(pref)
            for j, obj in enumerate(objs):
                glay.setColumnStretch(j, 10*self._MIN_WIDs[obj[0]])
                glay.addLayout(obj[1], i, j)

        self.my_layout = QVBoxLayout(self)
        self.my_layout.setContentsMargins(6, 10, 6, 0)
        self.my_layout.setSpacing(15)

        if self.has_search:
            # Create search bar
            search_lineedit = QLineEdit(parent=self)
            search_lineedit.setPlaceholderText("Search...")
            search_lineedit.textEdited.connect(self.filter_lines)
            self.my_layout.addWidget(search_lineedit)

        # Create header
        headerlay = QGridLayout()
        headerlay.setVerticalSpacing(30)
        headerlay.setHorizontalSpacing(30)
        headerlay.setContentsMargins(0, 0, 0, 0)
        objs = self.getLine(header=True)
        for j, obj in enumerate(objs):
            headerlay.setColumnStretch(j, 10*self._MIN_WIDs[obj[0]])
            headerlay.addLayout(obj[1], 0, j)
        self.my_layout.addLayout(headerlay)

        # Create scrollarea
        sc_area = QScrollArea()
        sc_area.setWidgetResizable(True)
        sc_area.setFrameShape(QFrame.NoFrame)
        sc_area.setWidget(wid)
        self.my_layout.addWidget(sc_area)

    def getLine(self, prefix=None, header=False):
        objects = list()
        for prop in self._ALL_PROPS:
            item = self.getColumn(prefix, prop, header)
            if item is not None:
                objects.append([prop, item])
        return objects

    def getColumn(self, prefix, prop, header):
        if prop not in self.props:
            return
        lv = QVBoxLayout()
        lv.setSpacing(6)
        lv.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        fun = self._createObjs if not header else self._headerLabel
        objs = fun(prefix, prop)
        for ob in objs:
            lv.addWidget(ob)
            ob.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        return lv

    def filter_lines(self, text):
        """Filter lines according to the regexp filter."""
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
                    conds &= isinstance(wid.value, int)
                    conds &= wid.value < len(wid.enum_strings)
                    if conds:
                        enum = wid.enum_strings[wid.value]
                        keep |= bool(pattern.search(enum))
                        continue

        self._set_lines_visibility()

    def _set_lines_visibility(self):
        for key, objs in self.lines.items():
            if key in self.filtered_lines:
                for _, layout in objs:
                    for idx in range(layout.count()):
                        layout.itemAt(idx).widget().setVisible(True)
            else:
                for _, layout in objs:
                    for idx in range(layout.count()):
                        layout.itemAt(idx).widget().setVisible(False)

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
