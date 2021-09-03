"""Auxiliary dialogs."""

from datetime import datetime as _datetime, timedelta as _timedelta

from qtpy.QtCore import Qt, Signal, QThread
from qtpy.QtWidgets import QGridLayout, QVBoxLayout, QLabel, QPushButton, \
    QDateTimeEdit, QLineEdit, QWidget, QFormLayout, QSizePolicy as QSzPlcy, \
    QMessageBox

from siriuspy.clientarch.client import ClientArchiver
from siriuspy.clientarch.pvarch import PVData, PVDetails
from siriuspy.clientarch.time import Time as _Time

from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.dialog import WaitDialog, WaitThread


# ---------- get plot data thread and window ----------

class GetPlotDataWindow(SiriusMainWindow):
    """Window to get data to add new graph."""

    plotDataSignal = Signal(list)

    def __init__(self, conn=None, show_intvl_sel=True,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle('Plot Data')
        self.conn = conn
        if not conn:
            self.conn = ClientArchiver()
        self.show_intvl_sel = show_intvl_sel
        self.t_now = _datetime.now()
        self.duration = _timedelta(minutes=10)
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h4>Plot Data</h4>',
            alignment=Qt.AlignCenter)

        self.ld_search = QLabel('Enter PV name/filter: ', self)
        self.le_search = PVListLineEdit(self.conn, self)

        self.tree = PVNameTree(
            tree_levels=('sec', 'dis', 'dev', 'device_name'),
            parent=self)
        self.tree.tree.setHeaderHidden(True)
        self.tree.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Preferred)
        self.tree.tree.setColumnCount(1)
        self.tree._filter_le.setVisible(False)

        self.pb_send = QPushButton('Choose', self)
        self.pb_send.setObjectName('send')
        self.pb_send.clicked.connect(self._send_plot_data)
        self.pb_send.setStyleSheet(
            "#send{max-width: 6em;}")

        lay1 = QGridLayout()
        lay1.addWidget(self.ld_search, 0, 0)
        lay1.addWidget(self.le_search, 0, 1)
        lay1.addWidget(self.tree, 1, 0, 1, 2)

        if self.show_intvl_sel:
            self.ld_intvlsel = QLabel('<h4>Select interval: </h4>', self)

            self.t_init = self.t_now - self.duration
            self.ld_init = QLabel('Start time: ', self)
            self.dt_init = QDateTimeEdit(self)
            self.dt_init.setDateTime(self.t_init)

            self.t_end = self.t_now
            self.ld_end = QLabel('Stop time: ', self)
            self.dt_end = QDateTimeEdit(self)
            self.dt_end.setDateTime(self.t_end)

            lay_intvl = QFormLayout()
            lay_intvl.setContentsMargins(0, 0, 0, 0)
            lay_intvl.addRow(self.ld_intvlsel)
            lay_intvl.addRow(self.ld_init, self.dt_init)
            lay_intvl.addRow(self.ld_end, self.dt_end)

        self.ld_intvlsel = QLabel('<h4>Apply pre-processing: </h4>', self)

        lay_process = QFormLayout()
        lay_process.setContentsMargins(0, 0, 0, 0)

        lay2 = QVBoxLayout()
        if self.show_intvl_sel:
            lay2.addLayout(lay_intvl)
        lay2.addLayout(lay_process)

        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addLayout(lay1, 1, 0)
        lay.addLayout(lay2, 1, 1)
        lay.addWidget(self.pb_send, 2, 0, 1, 2, alignment=Qt.AlignCenter)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)

        self.le_search.pvListSignal.connect(self._fill_tree)

    def _fill_tree(self, pvnames):
        self.tree.clear()
        self.tree.items = pvnames

    def _send_plot_data(self):
        plot_data = [None]*3

        pvs = self.tree.checked_items()
        plot_data[0] = pvs

        process = self.list_prcss.items_data()
        plot_data[1] = process

        if self.show_intvl_sel:
            t_init = self.dt_init.dateTime().toSecsSinceEpoch()
            plot_data[2] = t_init

            t_end = self.dt_end.dateTime().toSecsSinceEpoch()
            plot_data[3] = t_end

        self.plotDataSignal.emit(plot_data)
        self.close()


class GetPlotDataThread(QThread):
    """Thread to get plot data."""

    errorSignal = Signal(str)
    dataSignal = Signal(str, dict)

    def __init__(self, pvname, t_init, t_end, parent=None):
        super().__init__(parent)
        self.pvname = pvname
        self.t_init = _Time(timestamp=float(t_init))
        self.t_end = _Time(timestamp=float(t_end))

    def run(self):
        data = dict()

        try:
            pvdetails = PVDetails(self.pvname)
            pvdetails.update()
            data['unit'] = pvdetails.units

            pvdata = PVData(self.pvname)
            pvdata.timestamp_start = self.t_init
            pvdata.timestamp_stop = self.t_end
            pvdata.update()
            data['timestamp'] = pvdata.timestamp
            data['value'] = pvdata.value

            if len(data['value']) == 1:
                val = pvdata.value[0]
                data['timestamp'] = [self.t_init.get_timestamp(),
                                     self.t_end.get_timestamp()]
                data['value'] = [val, val]
        except ConnectionError as msg:
            self.errorSignal.emit(str(msg))
        else:
            self.dataSignal.emit(self.pvname, data)


# ---------- get pv list line edit ----------

class PVListLineEdit(QLineEdit):
    """Line Edit To Get PV List From Archiver."""

    pvListSignal = Signal(list)

    def __init__(self, conn=set(), parent=None):
        super().__init__(parent)
        self._conn = conn

        self.returnPressed.connect(self._get_pvnames)

    def _get_pvnames(self):
        self.wait_dlg = WaitDialog(self)
        self.wait_th = WaitThread(self)
        self.wait_th.opendiag.connect(self.wait_dlg.show)
        self.wait_th.closediag.connect(self.wait_dlg.close)
        self.wait_th.start()

        self.getpv_th = GetPVNamesThread(self._conn, self.text())
        self.getpv_th.errorSignal.connect(self._show_error_msg)
        self.getpv_th.pvnamesSignal.connect(self._emit_pvlist)
        self.getpv_th.start()

    def _show_error_msg(self, msg):
        self.wait_th.exit_task()
        QMessageBox.critical(
            self,
            'Could not get PV Data in Archiver',
            'Error on querry:\n{}'.format(msg))

    def _emit_pvlist(self, pvnames):
        self.wait_th.exit_task()
        self.pvListSignal.emit(pvnames)


class GetPVNamesThread(QThread):
    """Thread to get pvnames."""

    errorSignal = Signal(str)
    pvnamesSignal = Signal(list)

    def __init__(self, conn, filters, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.filters = filters

    def run(self):
        try:
            pvnames = self.conn.getAllPVs(self.filters)
        except ConnectionError as err:
            self.errorSignal.emit(str(err))
        else:
            self.pvnamesSignal.emit(pvnames)


# ---------- processing data widget ----------

class ProcessDataWidget(QWidget):
    """Widget to Get Process Data for Selected PVs."""

    def __init__(self, parent=None):
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('<h4>TO DO</h4>'))

    def add_items(self, items):
        self.wait_dlg = WaitDialog(self)
        self.wait_th = WaitThread(self)
        self.wait_th.opendiag.connect(self.wait_dlg.show)
        self.wait_th.closediag.connect(self.wait_dlg.close)
        self.wait_th.start()

        for item in items:
            self.add_new_row()

        self.wait_th.exit_task()
