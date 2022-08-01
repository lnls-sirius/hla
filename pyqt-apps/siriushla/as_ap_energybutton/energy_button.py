"""Interface to set dipole energies with constant normalization."""

from qtpy.QtCore import Slot, QVariant
from qtpy.QtWidgets import QVBoxLayout, QWidget, QPushButton, \
    QHBoxLayout, QLabel
from qtpy.QtGui import QPalette, QColor
from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.common.epics.task import EpicsConnector, EpicsSetter, \
    EpicsChecker, EpicsGetter, EpicsWait
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from siriushla.widgets import PVNameTree, QDoubleSpinBoxPlus
from siriushla.util import get_appropriate_color

from .set_energy import init_section


class EnergyButton(QWidget):
    """Set dipole energy."""

    def __init__(self, section, parent=None):
        """Setups widget interface."""
        super().__init__(parent)
        self._section = section
        self.dips, self.mags = init_section(section.upper())
        self._items_fail = []
        self._items_success = []
        self._setup_ui()
        color = QColor(get_appropriate_color(section.upper()))
        pal = self.palette()
        pal.setColor(QPalette.Background, color)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())

        self.energy_value = QDoubleSpinBoxPlus(self)
        self.energy_value.setSingleStep(0.01)
        self.energy_value.setMinimum(self.lower_limit)
        self.energy_value.setMaximum(self.upper_limit)
        self.energy_value.setDecimals(4)

        if self.section == 'tb':
            sp_channel = 'TB-Fam:PS-B:Energy-RB'
        elif self.section == 'bo':
            sp_channel = 'BO-Fam:PS-B-1:Energy-RB'
        elif self.section == 'ts':
            sp_channel = 'TS-Fam:PS-B:Energy-RB'
        elif self.section == 'si':
            sp_channel = 'SI-Fam:PS-B1B2-1:Energy-RB'
        else:
            raise RuntimeError
        sp_channel = _PVName(sp_channel).substitute(prefix=_VACA_PREFIX)
        self.energy_sp = PyDMLabel(self)
        self.energy_sp.channel = sp_channel
        self.energy_sp.showUnits = True

        self._tree = PVNameTree(
            items=self.mags, tree_levels=('dis', 'mag_group'), parent=self)
        self._tree.tree.setHeaderHidden(True)
        self._tree.tree.setColumnCount(1)
        self._tree.check_all()
        self._tree.collapse_all()

        self.set_energy = QPushButton('Set', self)
        self.set_energy.clicked.connect(self._process)

        # forml = Q
        hbl = QHBoxLayout()
        # hbl.addStretch()
        hbl.addWidget(QLabel('<h4>New Energy:</h4> ', self))
        hbl.addWidget(self.energy_value)
        self.layout().addLayout(hbl)
        hbl = QHBoxLayout()
        # hbl.addStretch()
        hbl.addWidget(QLabel('Current Energy: ', self))
        hbl.addWidget(self.energy_sp)
        self.layout().addLayout(hbl)
        self.layout().addWidget(self._tree)
        self.layout().addWidget(self.set_energy)

    @property
    def section(self):
        return self._section

    @property
    def upper_limit(self):
        if self.section == 'tb':
            return 0.155
        elif self.section == 'bo':
            return 0.160
        elif self.section == 'ts':
            return 3.2
        elif self.section == 'si':
            return 3.014
        else:
            raise RuntimeError

    @property
    def lower_limit(self):
        if self.section == 'tb':
            return 0.0
        elif self.section == 'bo':
            return 0.0
        elif self.section == 'ts':
            return 0.0
        elif self.section == 'si':
            return 0.0
        else:
            raise RuntimeError

    def _process(self):
        self._items_success = []
        self._items_fail = []

        # Get selected PVs
        selected_pvs = set(self._tree.checked_items())
        mags = [mag for mag in self.mags if mag in selected_pvs]
        if not mags:
            report = ReportDialog(['Select at least one PS!'], self)
            report.exec_()
            return

        pvs = self.dips + mags

        conn = EpicsConnector(pvs, parent=self)
        get_task = EpicsGetter(pvs, parent=self)
        get_task.itemRead.connect(self._read_success)
        get_task.itemNotRead.connect(self._read_fail)
        dlg = ProgressDialog(
            ['Connecting', 'Reading'], [conn, get_task], parent=self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        if self._items_fail:
            failed = ['Failed to read some PVs', ]
            failed += self._items_fail + ['Aborting!', ]
            report = ReportDialog(failed, self)
            report.exec_()
            return

        energy = self.energy_value.value()
        # remove dipole
        pvs, values = zip(*self._items_success[len(self.dips):])
        delays = [0.0, ] * len(pvs)
        self._items_success = []

        energies = [energy, ] * len(self.dips)
        dly_dips = [0.0, ] * len(self.dips)
        conn = EpicsConnector(self.dips, parent=self)
        set_dip = EpicsSetter(self.dips, energies, dly_dips, parent=self)
        sleep_task = EpicsWait([None, ]*10, wait_time=2.0, parent=self)
        check_dip = EpicsChecker(self.dips, energies, dly_dips, parent=self)
        check_dip.itemChecked.connect(self._check_status)

        dlg = ProgressDialog(
            ['Connecting', 'Setting Dipole', 'Waiting Dipole',
             'Checking Dipole'],
            [conn, set_dip, sleep_task, check_dip], parent=self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        if self._items_fail:
            failed = ['Failed to set Dipole. Aborting!']
            report = ReportDialog(failed, self)
            report.exec_()
            return

        conn = EpicsConnector(pvs, parent=self)
        set_mags = EpicsSetter(pvs, values, delays, parent=self)
        sleep_task = EpicsWait([None, ]*10, wait_time=2.0, parent=self)
        check_mags = EpicsChecker(pvs, values, delays, parent=self)
        check_mags.itemChecked.connect(self._check_status)

        dlg = ProgressDialog(
            ['Connecting to Magnets', 'Setting Magnets', 'Waiting Magnets',
             'Checking Magnets'],
            [conn, set_mags, sleep_task, check_mags], parent=self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return

        failed = []
        if self._items_fail:
            failed = ['Failed to set magnets:', ] + self._items_fail
        report = ReportDialog(failed, self)
        report.exec_()

    @Slot(str)
    def _read_fail(self, item):
        self._items_fail.append(item)

    @Slot(str, QVariant)
    def _read_success(self, item, value):
        self._items_success.append((item, value))

    @Slot(str, bool)
    def _check_status(self, item, status):
        if status:
            self._items_success.append((item, True))
        else:
            self._items_fail.append(item)
