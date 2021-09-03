"""Sirius Data View Window."""

import time as _time

# from functools import partial as _part
# import numpy as _np

# from threading import Thread


from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QVBoxLayout,\
    QHBoxLayout, QPushButton,  QSpacerItem, QSizePolicy as QSzPlcy

import qtawesome as qta

import pydm

from siriuspy.clientarch import ClientArchiver

from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ap_dataview.auxiliary_dialogs import \
    WaitDialog, WaitThread, \
    GetPlotDataWindow, GetPlotDataThread
from siriushla.as_ap_dataview.custom_widgets import GraphItem

pydm.utilities.colors.default_colors.remove('white')


class SiriusDataViewWindow(SiriusMainWindow):
    """Sirius Data View Window."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Sirius Data View')
        color = get_appropriate_color('SI')
        self.setWindowIcon(qta.icon('fa.book', color=color))

        self.archiver_client = ClientArchiver()

        self.pvname2data = dict()
        self._layout_first_empty_line = 0
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h3>Sirius Data View</h3>', self, alignment=Qt.AlignCenter)

        self.graphs_lay = QVBoxLayout()

        self.pb_additem = QPushButton(qta.icon('fa5s.plus'), '', self)
        self.pb_additem.clicked.connect(self.get_plot_data)
        lay_but = QHBoxLayout()
        lay_but.addWidget(self.pb_additem)

        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(self.title, 0, 0)
        lay.addLayout(lay_but, 1, 0, alignment=Qt.AlignRight)
        lay.addLayout(self.graphs_lay, 2, 0)
        lay.addItem(QSpacerItem(1, 1, QSzPlcy.Fixed, QSzPlcy.Expanding))

    def get_plot_data(self):
        wind = GetPlotDataWindow(conn=self.archiver_client, parent=self)
        wind.plotDataSignal.connect(self.query_arch)
        wind.show()

    def query_arch(self, plot_data):
        pvnames = plot_data[0]
        time_init = plot_data[1]
        time_end = plot_data[2]

        self.wait_dlg = WaitDialog(self)
        self.wait_th = WaitThread(self)
        self.wait_th.opendiag.connect(self.wait_dlg.show)
        self.wait_th.closediag.connect(self.wait_dlg.close)
        self.wait_th.start()

        self.pvname2data = dict()
        self.pvnames2querry = pvnames
        self.querry_errs = list()
        for pvname in pvnames:
            data_thread = GetPlotDataThread(pvname, time_init, time_end, self)
            data_thread.errorSignal.connect(self._get_errors)
            data_thread.dataSignal.connect(self._get_pvname2data)
            data_thread.start()
        self._t0_getplotdata = _time.time()

    def _get_pvname2data(self, pvname, data):
        self.pvname2data[pvname] = data

        if set(self.pvname2data.keys()) == set(self.pvnames2querry):
            self.wait_th.exit_task()
            self.add_item(pvname2data=self.pvname2data)
        elif self.querry_errs:
            self.wait_th.exit_task()

    def _get_errors(self, msg):
        self.querry_errs.append(msg)

    def add_item(self, index=None, pvname2data=dict()):
        if index is None:
            index = self._layout_first_empty_line
        new_graph = GraphItem(
            self, delete_slot=self.delete_item, index=index,
            pvname2data=pvname2data)
        self.graphs_lay.insertWidget(self._layout_first_empty_line, new_graph)
        self._layout_first_empty_line += 1

    def delete_item(self, index=None):
        if index is None:
            index = self._layout_first_empty_line-1
        item = self.graphs_lay.takeAt(index).widget()
        item.deleteLater()
        del item
        self._layout_first_empty_line -= 1


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    app.open_window(SiriusDataViewWindow, parent=None)
    sys.exit(app.exec_())
