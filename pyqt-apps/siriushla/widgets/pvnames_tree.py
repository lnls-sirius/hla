"""PVName selection tree view."""
import re
import uuid
from copy import deepcopy as _dcopy
from qtpy.QtCore import Qt, QSize, Signal, QThread, Slot
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem, QProgressDialog, \
    QAction, QMenu, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, \
    QHeaderView

from siriuspy.namesys import SiriusPVName


class QTreeItem(QTreeWidgetItem):
    """Tree Item."""

    def __init__(self, string_list, parent=None):
        """Init."""
        super().__init__(parent, string_list)
        self._shown = set()
        self._status = {
            Qt.Checked: set(), Qt.Unchecked: set(), Qt.PartiallyChecked: set()}
        self._myhash = uuid.uuid4()

    @property
    def myhash(self):
        return self._myhash

    def isLeaf(self):
        """Return if is Leaf."""
        if self.childCount() > 0:
            return False
        return True

    def setHidden(self, status):
        """Overhide setHidden method."""
        super().setHidden(status)
        if isinstance(self.parent(), QTreeItem):
            self.parent().childHidden(self, status)

    def childHidden(self, child, status):
        """Set child hidden."""
        getattr(self._shown, 'discard' if status else 'add')(child.myhash)
        status = not self._shown
        super().setHidden(status)
        if isinstance(self.parent(), QTreeItem):
            self.parent().childHidden(self, status)

    def setData(self, column, role, value):
        """Set data."""
        if column == 0 and role == Qt.CheckStateRole:
            if self.checkState(0) == Qt.PartiallyChecked:
                value = Qt.Unchecked
            # Trigger parent check
            if isinstance(self.parent(), QTreeItem):
                self.parent().childChecked(self, column, value)
            # Trigger children check
            if value in (Qt.Checked, Qt.Unchecked):
                if self.childCount() == 0:
                    if self.checkState(column) != value:
                        self.treeWidget().parent().itemChecked.emit(
                            self, column, value)
                    super().setData(column, role, value)
                else:
                    for chil in range(self.childCount()):
                        if not self.child(chil).isHidden():
                            self.child(chil).setData(
                                column, Qt.CheckStateRole, value)
        else:
            super().setData(column, role, value)

    def _check_children(self):
        """Child was checked."""
        check = self._status
        if check[Qt.PartiallyChecked]:
            return Qt.PartiallyChecked
        elif check[Qt.Checked] and check[Qt.Unchecked]:
            return Qt.PartiallyChecked
        elif check[Qt.Checked]:
            return Qt.Checked
        return Qt.Unchecked

    def childChecked(self, child, column, status):
        """Child was checked."""
        self._status[status].add(child.myhash)
        left = self._status.keys() - {status, }
        for sts in left:
            self._status[sts].discard(child.myhash)

        mystate = self.checkState(column)
        if status == Qt.PartiallyChecked:
            status = Qt.PartiallyChecked
        elif status != mystate:
            status = self._check_children()
        else:
            status = mystate

        super().setData(column, Qt.CheckStateRole, status)
        if isinstance(self.parent(), QTreeItem):
            self.parent().childChecked(self, column, status)


class BuildTree(QThread):
    """QThread to build tree."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, obj):
        """Init."""
        super().__init__(obj)
        self.obj = obj
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self.obj.items)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Build tree."""
        for item in self.obj.items:
            if self._quit_task:
                break
            name = item
            if not isinstance(name, str):
                name = item[0]
            self.currentItem.emit(name)
            self.obj._add_item(item)
            self.itemDone.emit()
        self.completed.emit()


class Tree(QTreeWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.header().setSectionsMovable(False)

    def resizeEvent(self, event):
        # self.setColumnWidth(0, self.width()*3/6)
        self.setColumnWidth(1, self.width()*1.3/6)
        # self.setColumnWidth(2, self.width()*0.4/6)
        if not self.header().isHidden():
            self.header().setSectionResizeMode(0, QHeaderView.Stretch)
            self.header().setSectionResizeMode(1, QHeaderView.Fixed)
            self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.header().setStretchLastSection(False)
        super().resizeEvent(event)


class PVNameTree(QWidget):
    """Build a tree with SiriusPVNames."""

    itemChecked = Signal(QTreeItem, int, int)

    def __init__(self, items=tuple(), tree_levels=tuple(),
                 checked_levels=tuple(), parent=None):
        """Constructor."""
        super().__init__(parent)

        self._item_map = dict()

        self._pnames = tree_levels
        self._leafs = list()
        self._nr_checked_items = 0

        self._setup_ui()
        self._create_actions()

        self.check_children = True
        self.check_parent = True

        self.check_requested_levels(checked_levels)

        self.items = _dcopy(items)
        self.tree.expanded.connect(
            lambda idx: self.tree.resizeColumnToContents(idx.column()))

    def _setup_ui(self):
        self._msg = QLabel(self)

        # Add Selection Tree
        self._check_count = QLabel(self)
        self.tree = Tree(self)
        self.tree.setColumnCount(3)
        self.tree.setHeaderHidden(False)
        self.tree.setHeaderLabels(['Name', 'Value', 'Delay'])

        self.itemChecked.connect(self._item_checked)

        # Add filter for tree
        self._filter_le = QLineEdit(self)
        self._filter_le.setPlaceholderText("Filter Items...")
        self._filter_le.textChanged.connect(self._filter_items)

        self.setLayout(QVBoxLayout())
        hl = QHBoxLayout()
        hl.addWidget(self._msg)
        hl.addWidget(self._check_count)
        self.layout().addWidget(self._filter_le)
        self.layout().addLayout(hl)
        self.layout().addWidget(self.tree)

    def _create_actions(self):
        self._act_check_all = QAction("Check All", self)
        self._act_check_all.triggered.connect(self.check_all)
        self._act_uncheck_all = QAction("Uncheck All", self)
        self._act_uncheck_all.triggered.connect(self.uncheck_all)
        self._act_expand_all = QAction("Expand All", self)
        self._act_expand_all.triggered.connect(self.expand_all)
        self._act_collapse_all = QAction("Collapse All", self)
        self._act_collapse_all.triggered.connect(self.collapse_all)

    def clear(self):
        """Clear tree."""
        self._items = tuple()
        self._leafs = list()
        self._item_map = dict()
        self.tree.clear()
        self._nr_checked_items = 0

    @property
    def message(self):
        return self._msg.text()

    @message.setter
    def message(self, text):
        return self._msg.setText(text)

    @property
    def items(self):
        """Items."""
        return self._items

    @items.setter
    def items(self, value):
        self.tree.clear()
        self._items = _dcopy(value)
        self._add_items()
        self._filter_items(self._filter_le.text())

    def check_all(self):
        """Check all items."""
        for item in self._leafs:
            if not item.isHidden():
                item.setCheckState(0, Qt.Checked)

    def uncheck_all(self):
        """Uncheck all items."""
        for item in self._leafs:
            if not item.isHidden():
                item.setCheckState(0, Qt.Unchecked)

    def expand_all(self):
        """Expand all items."""
        for item in self._item_map.values():
            if item.childCount() > 0:
                item.setExpanded(True)

    def collapse_all(self):
        self.tree.collapseAll()

    @staticmethod
    def mag_group(name):
        """Return magnet group."""
        if re.match('^B\w*(-[0-9])?$', name.dev):
            return 'Dipole'
        elif re.match('^Q[A-RT-Z0-9]\w*(-[0-9])?$', name.dev):
            if re.match('Fam', name.sub):
                return 'Quadrupole'
            elif re.match('SI', name.sec):
                return 'Trim'
            else:
                return 'Quadrupole'
        elif re.match('^QS.*$', name.dev):
            return 'Quadrupole Skew'
        elif re.match('^Spect.*$', name.dev):
            return 'Spetrometer'
        elif re.match('^Slnd.*$', name.dev):
            return 'Solenoid'
        elif re.match('^S\w*(-[0-9])?$', name.dev):
            return 'Sextupole'
        elif re.match('^C(H|V)(-[0-9])?$', name.dev):
            return 'Corrector'
        elif re.match('^FC\w*(-[0-9])?$', name.dev):
            return 'Fast Corrector'
        elif re.match('.*Kckr.*$', name.dev):
            return 'Kicker'
        elif re.match('.*Sept.*$', name.dev):
            return 'Septum'
        elif re.match('Ping.*$', name.dev):
            return 'Pinger'
        elif re.match('^Lens.*$', name.dev):
            return 'Lens'
        else:
            return 'Other'

    def check_requested_levels(self, levels):
        """Set requested levels checked."""
        for level in levels:
            self._item_map[level].setCheckState(0, Qt.Checked)

    def _add_item(self, item):

        if isinstance(item, str):
            pvname = item
            row = [item, ]
        else:
            if not isinstance(item[0], str):
                raise ValueError
            pvname = item[0]
            row = [item[0], ]
            row.extend([str(i) for i in item[1:]])
        # pvals = []
        parent = self.tree.invisibleRootItem()
        parent_key = ''
        # if pvname.count(':') == 2 and pvname.count('-') == 3:
        try:
            pvname = SiriusPVName(pvname)
        except (IndexError, ValueError):
            pass
        # Deal with LI LLRF PVs:
        if pvname.startswith('LA'):
            dic_ = {'sec': 'LI', 'dis': 'RF', 'dev': 'LLRF'}
            for p in self._pnames:
                key = dic_.get(p, 'DLLRF')
                if key:
                    item_key = parent_key + key
                    # item = self._item_map.symbol(item_key)
                    item = self._item_map[item_key] \
                        if item_key in self._item_map else None
                    if item is not None:
                        parent = item
                    else:
                        new_item = QTreeItem([key], parent)
                        new_item.setCheckState(0, Qt.Unchecked)
                        # self._item_map.add_symbol(item_key, new_item)
                        self._item_map[item_key] = new_item
                        # parent.addChild(new_item)
                        parent = new_item
                    parent_key = item_key
        # Deal with BO LLRF PVs:
        elif pvname.startswith('BR'):
            dic_ = {'sec': 'BO', 'dis': 'RF', 'dev': 'DLLRF'}
            for p in self._pnames:
                key = dic_.get(p, 'DLLRF')
                if key:
                    item_key = parent_key + key
                    # item = self._item_map.symbol(item_key)
                    item = self._item_map[item_key] \
                        if item_key in self._item_map else None
                    if item is not None:
                        parent = item
                    else:
                        new_item = QTreeItem([key], parent)
                        new_item.setCheckState(0, Qt.Unchecked)
                        # self._item_map.add_symbol(item_key, new_item)
                        self._item_map[item_key] = new_item
                        # parent.addChild(new_item)
                        parent = new_item
                    parent_key = item_key
        elif pvname.startswith('SR'):
            dic_ = {'sec': 'SI', 'dis': 'RF', 'dev': 'DLLRF'}
            for p in self._pnames:
                key = dic_.get(p, 'DLLRF')
                if key:
                    item_key = parent_key + key
                    # item = self._item_map.symbol(item_key)
                    item = self._item_map[item_key] \
                        if item_key in self._item_map else None
                    if item is not None:
                        parent = item
                    else:
                        new_item = QTreeItem([key], parent)
                        new_item.setCheckState(0, Qt.Unchecked)
                        # self._item_map.add_symbol(item_key, new_item)
                        self._item_map[item_key] = new_item
                        # parent.addChild(new_item)
                        parent = new_item
                    parent_key = item_key
        elif pvname.startswith('RF'):
            dic_ = {'sec': 'AS', 'dis': 'RF', 'dev': 'RFGen'}
            for p in self._pnames:
                key = dic_.get(p, 'RFGen')
                if key:
                    item_key = parent_key + key
                    # item = self._item_map.symbol(item_key)
                    item = self._item_map[item_key] \
                        if item_key in self._item_map else None
                    if item is not None:
                        parent = item
                    else:
                        new_item = QTreeItem([key], parent)
                        new_item.setCheckState(0, Qt.Unchecked)
                        # self._item_map.add_symbol(item_key, new_item)
                        self._item_map[item_key] = new_item
                        # parent.addChild(new_item)
                        parent = new_item
                    parent_key = item_key
        elif isinstance(pvname, SiriusPVName):
            # Parse it with SiriusPVName
            pvname = SiriusPVName(pvname)
            # Parse PVName
            for p in self._pnames:
                try:
                    key = getattr(pvname, p)
                except AttributeError:
                    key = getattr(PVNameTree, p)(pvname)
                if key:
                    item_key = parent_key + key
                    # item = self._item_map.symbol(item_key)
                    item = self._item_map[item_key] \
                        if item_key in self._item_map else None
                    if item is not None:
                        parent = item
                    else:
                        new_item = QTreeItem([key], parent)
                        new_item.setCheckState(0, Qt.Unchecked)
                        # self._item_map.add_symbol(item_key, new_item)
                        self._item_map[item_key] = new_item
                        # parent.addChild(new_item)
                        parent = new_item
                    parent_key = item_key
        else:
            key = pvname[:2]
            item_key = parent_key + key
            item = self._item_map[item_key] \
                if item_key in self._item_map else None
            if item is None:
                new_item = QTreeItem([key], parent)
                new_item.setCheckState(0, Qt.Unchecked)
                self._item_map[item_key] = new_item
                parent = new_item
            else:
                parent = item
        # Insert leaf node pvname
        new_item = QTreeItem(row, parent)
        new_item.setCheckState(0, Qt.Unchecked)
        self._item_map[pvname] = new_item
        self._leafs.append(new_item)

    def _add_items(self):
        # Connect signals
        t = BuildTree(self)
        t.finished.connect(t.deleteLater)
        dlg = None
        if len(self.items) > 1500:
            dlg = QProgressDialog(
                labelText='Building Tree',
                minimum=0, maximum=len(self._items), parent=self)
            t.itemDone.connect(lambda: dlg.setValue(dlg.value() + 1))
            t.finished.connect(dlg.close)
        # Start
        t.start()
        if dlg:
            dlg.exec_()
        t.wait()

    def checked_items(self):
        """Return checked items."""
        return [item.data(0, Qt.DisplayRole) for item in self._leafs
                if item.checkState(0) == Qt.Checked]

    def sizeHint(self):
        """Override sizehint."""
        return QSize(600, 600)

    def contextMenuEvent(self, event):
        """Show context menu."""
        menu = QMenu(self)
        menu.addAction(self._act_check_all)
        menu.addAction(self._act_uncheck_all)
        menu.addSeparator()
        menu.addAction(self._act_expand_all)
        menu.addAction(self._act_collapse_all)
        menu.popup(event.globalPos())

    @Slot(str)
    def _filter_items(self, text):
        """Filter pvnames based on text inserted at line edit."""
        selected_pvs = 0
        try:
            pattern = re.compile(text, re.I)
        except Exception:
            return

        for node in self._leafs:
            if pattern.search(node.data(0, 0)):
                node.setHidden(False)
                selected_pvs += 1
            else:
                # node.setCheckState(0, Qt.Unchecked)
                node.setHidden(True)
        self._msg.setText('Showing {} Items.'.format(selected_pvs))

    @Slot(QTreeItem, int, int)
    def _item_checked(self, item, column, value):
        if item.childCount() == 0:
            if value == Qt.Checked:
                self._nr_checked_items += 1
            elif value == Qt.Unchecked:
                self._nr_checked_items -= 1
        self._check_count.setText(
            '{} Items checked.'.format(self._nr_checked_items))


if __name__ == "__main__":
    # import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()

    items = []
    for i in range(800):
        items.extend([('SI-Fam:PS-B1B1{}:PwrState-Sel'.format(i), 1, 0.0),
                      ('BO-Fam:PS-QD{}:Current-SP'.format(i), 1, 0.0),
                      ('BO-Fam:PS-B-{}:PwrState-Sel'.format(i), 1, 0.0)])
    w = PVNameTree(
        items=items, tree_levels=('sec', 'mag_group'),
        checked_levels=('BOQuadrupole', ))
    w.show()
    # w.items = items
    # w.check_requested_levels(('BOQuadrupole', ))

    # sys.exit(app.exec_())
    app.exec_()
