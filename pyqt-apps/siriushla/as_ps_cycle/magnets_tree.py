"""Magnet selection tree view."""
import re

from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QTreeWidget, QTreeWidgetItem

from siriuspy.search.ma_search import MASearch


class MagnetTree(QTreeWidget):

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.ma_items = list()
        self._setup_ui()
        self.setHeaderHidden(True)
        self.itemChanged.connect(self._check_children)
        self.setGeometry(100, 100, 600, 1024)

        self.dontemit = False

    def _setup_ui(self):
        sections = set()
        sections_items = dict()
        dev_by_sec = dict()
        dev_by_sec_items = dict()

        for maname in MASearch.get_manames():

            if maname.dis != 'MA':
                continue

            section = maname[:2]
            device = self._get_device_type(maname)

            if section not in sections:
                sections.add(section)
                sec_item = QTreeWidgetItem([section])
                sec_item.setCheckState(0, Qt.Unchecked)
                sections_items[section] = sec_item

            if section not in dev_by_sec:
                dev_by_sec[section] = set()
                dev_by_sec_items[section] = dict()

            if device not in dev_by_sec[section]:
                sec_item = sections_items[section]
                dev_item = QTreeWidgetItem(sec_item, [device])
                dev_item.setCheckState(0, Qt.Unchecked)
                sec_item.addChild(dev_item)
                dev_by_sec[section].add(device)
                dev_by_sec_items[section][device] = dev_item

            dev_item = dev_by_sec_items[section][device]
            ma_item = QTreeWidgetItem(dev_item, [maname])
            ma_item.setCheckState(0, Qt.Unchecked)
            dev_item.addChild(ma_item)
            self.ma_items.append(ma_item)

        for sec_item in sections_items.values():
            self.addTopLevelItem(sec_item)

    def _get_device_type(self, maname):
        if re.match('^B\w*(-[0-9])?$', maname.dev):
            return 'Dipole'
        elif re.match('^Q[A-RT-Z0-9]\w*(-[0-9])?$', maname.dev):
            return 'Quadrupole'
        elif re.match('^QS.*$', maname.dev):
            return 'Quadrupole Skew'
        elif re.match('^S\w*(-[0-9])?$', maname.dev):
            return 'Sextupole'
        elif re.match('^C(H|V)(-[0-9])?$', maname.dev):
            return 'Corrector'
        elif re.match('^FC\w*(-[0-9])?$', maname.dev):
            return 'Fast Corrector'

    def _check_children(self, item, column):
        if self.dontemit:
            return

        if column == 0:
            check_state = item.checkState(0)
            child_count = item.childCount()
            for i in range(child_count):
                item.child(i).setCheckState(0, check_state)

            if item.parent():
                parent = item.parent()
                self.dontemit = True
                self._check_parent(parent)
                self.dontemit = False

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

        if item.parent():
            self._check_parent(item.parent())

    def checked_items(self):
        return [item.data(0, Qt.DisplayRole) for item in self.ma_items
                if item.checkState(0) == Qt.Checked]
