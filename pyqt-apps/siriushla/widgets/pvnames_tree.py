"""PVName selection tree view."""
import re
from collections import namedtuple

from qtpy.QtCore import Qt, QSize, Signal, QThread
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem, QProgressDialog

from siriuspy.namesys import SiriusPVName


class PVNameTree(QTreeWidget):
    """Build a tree with SiriusPVNames."""

    class BuildTree(QThread):
        """QThread to build tree."""

        itemInserted = Signal()

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
                self.obj._add_item(item)
                self.itemInserted.emit()

            for node in self.obj._ptree.children.values():
                self.obj.addTopLevelItem(node.item)

            self.finished.emit()

    _node = namedtuple('_node', 'item, children')

    def __init__(self, items=tuple(), tree_levels=tuple(), parent=None,
                 checked_levels=tuple()):
        """Constructor."""
        super().__init__(parent)

        self._items = items
        self._pnames = tree_levels
        self._ptree = PVNameTree._node(None, dict())
        self._leafs = list()

        self._setup_ui()

        self.setHeaderHidden(False)
        self.setHeaderLabels(['PVName', 'Value', 'Delay'])
        self.itemChanged.connect(self._item_checked)
        # self.setGeometry(100, 100, 600, 1024)

        self.check_children = True
        self.check_parent = True

        self._check_requested_levels(checked_levels)

    def clear(self):
        """Clear tree."""
        self._items = tuple()
        self._ptree = PVNameTree._node(None, dict())
        self._leafs = list()
        super().clear()

    @property
    def items(self):
        """Items."""
        return self._items

    @items.setter
    def items(self, value):
        self.clear()
        self._items = value
        self._add_items()

    def check_all(self):
        """Check all items."""
        for i in range(self.topLevelItemCount()):
            self.topLevelItem(i).setCheckState(0, Qt.Checked)

    def uncheck_all(self):
        """Uncheck all items."""
        for i in range(self.topLevelItemCount()):
            self.topLevelItem(i).setCheckState(0, Qt.Unchecked)

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

        pvals = []
        if re.match('^.*-.*:.*-.*:.*-.*$', pvname):
        # if pvname.count(':') == 2 and pvname.count('-') == 3:
            # Parse it with SiriusPVName
            pvname = SiriusPVName(pvname)
            for p in self._pnames:
                try:
                    val = getattr(pvname, p)
                except AttributeError:
                    val = getattr(PVNameTree, p)(pvname)
                if val:
                    pvals.append(val)
        else:
            pvname = pvname
        pvals.append(pvname)

        # Build the row for the item
        # pvname = ''
        # if isinstance(item, str):
        #     row = (SiriusPVName(item), )
        # else:
        #     row = [item[0], ]
        #     row.extend([str(i) for i in item[1:]])

        # pvals = []
        # key = row[0] if isinstance(row[0], SiriusPVName) \
        #     else SiriusPVName(row[0])


        # Get device properties value
        # for p in self._pnames:
        #     try:
        #         val = getattr(pvname, p)
        #     except AttributeError:
        #         val = getattr(PVNameTree, p)(pvname)
        #     if val:
        #         pvals.append(val)
        # pvals.append(key)

        # Create TreeItems and add to property maps
        parent = self._ptree
        i = 0
        while pvals:
            val = pvals.pop(0)

            if val in parent.children:
                item = parent.children[val].item
            else:
                if not pvals:
                    item = QTreeWidgetItem(row)
                    self._leafs.append(item)
                else:
                    item = QTreeWidgetItem([val])
                item.setCheckState(0, Qt.Unchecked)
                parent.children[val] = PVNameTree._node(item, dict())

            if parent.item is not None:
                parent.item.addChild(item)
            parent = parent.children[val]
            i += 1

        # self.itemInserted.emit()

    def _setup_ui(self):
        self._add_items()
        self.expanded.connect(
            lambda idx: self.resizeColumnToContents(idx.column()))

    def _add_items(self):
        dlg = QProgressDialog(
            labelText='Building Tree',
            minimum=0, maximum=len(self._items), parent=self)
        t = self.BuildTree(self)
        # Connect signals
        t.itemInserted.connect(lambda: dlg.setValue(dlg.value() + 1))
        t.finished.connect(dlg.close)
        t.finished.connect(t.deleteLater)
        # Start
        t.start()
        if len(self._items) > 0:
            dlg.exec_()

    def _item_checked(self, item, column):
        if self.check_children and self.check_parent:
            self.check_parent = False
            self._check_children(item, column)
            self.check_parent = True
            if item.parent():
                self.check_children = False
                self._check_parent(item.parent())
                self.check_children = True
        elif self.check_children and not self.check_parent:
            self._check_children(item, column)
        elif not self.check_children and self.check_parent:
            if item.parent():
                self._check_parent(item.parent())

    def _check_children(self, item, column):
        if column == 0:
            check_state = item.checkState(0)
            child_count = item.childCount()
            for i in range(child_count):
                item.child(i).setCheckState(0, check_state)

    def _check_parent(self, item):
        child_count = item.childCount()
        checked = 0
        unchecked = 0
        for i in range(child_count):
            if item.child(i).checkState(0) == Qt.Checked:
                checked += 1
            elif item.child(i).checkState(0) == Qt.Unchecked:
                unchecked += 1

        if checked == child_count:
            item.setCheckState(0, Qt.Checked)
        elif unchecked == child_count:
            item.setCheckState(0, Qt.Unchecked)
        else:
            item.setCheckState(0, Qt.PartiallyChecked)

    def checked_items(self):
        """Return checked items."""
        return [item.data(0, Qt.DisplayRole) for item in self._leafs
                if item.checkState(0) == Qt.Checked]

    def sizeHint(self):
        """Override sizehint."""
        return QSize(600, 600)

    @staticmethod
    def mag_group(name):
        """Return magnet group."""
        if re.match('^B\w*(-[0-9])?$', name.dev):
            return 'Dipole'
        elif re.match('^Q[A-RT-Z0-9]\w*(-[0-9])?$', name.dev):
            return 'Quadrupole'
        elif re.match('^QS.*$', name.dev):
            return 'Quadrupole Skew'
        elif re.match('^S\w*(-[0-9])?$', name.dev):
            return 'Sextupole'
        elif re.match('^C(H|V)(-[0-9])?$', name.dev):
            return 'Corrector'
        elif re.match('^FC\w*(-[0-9])?$', name.dev):
            return 'Fast Corrector'
        elif re.match('(Inj|Eje).*$', name.dev):
            return 'Pulsed'
        else:
            return 'Other'

    def _check_requested_levels(self, levels):
        """Set requested levels checked."""
        for node in self._ptree.children.values():
            if node.item.text(0) in levels:
                node.item.setCheckState(0, Qt.Checked)


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()

    w = PVNameTree(tree_levels=('sec', 'mag_group'))
    w.show()
    items = []
    for i in range(10000):
        items.extend([('SI-Fam:MA-B1B1{}:PwrState-Sel'.format(i), 1),
                      ('BO-Fam:MA-B-{}:PwrState-Sel'.format(i), 1)])
    w.items = items

    sys.exit(app.exec_())
