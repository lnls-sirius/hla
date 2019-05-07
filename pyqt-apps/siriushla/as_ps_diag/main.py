"""Interface to handle power supply diagnostic."""

import re as _re
from datetime import datetime as _datetime
from functools import partial as _partial

from pcaspy import Severity as _Severity

import numpy as _np

from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QSpacerItem, QSizePolicy as QSzPlcy, QLineEdit, \
    QTreeView, QItemDelegate, QHeaderView, QAbstractItemView, \
    QStackedLayout, QRadioButton

from pydm.widgets.channel import PyDMChannel
from pydm.widgets.base import PyDMWidget

from siriuspy.envars import vaca_prefix
from siriuspy.csdevice.pwrsupply import Const as _PSConst, \
    ETypes as _PSEnums
from siriuspy.search.ps_search import PSSearch
from siriuspy.search.ma_search import MASearch
from siriuspy.namesys import SiriusPVName, Filter

from siriushla.util import run_newprocess as _run_newprocess
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiChannel, PyDMLed, PyDMLedMultiConnection, QLed

from siriushla.as_ps_diag.util import LINAC_PS, sec2label, \
                                      asps2labels, lips2labels


class PSDiag(SiriusMainWindow):
    """Power Supply Diagnostic."""

    def __init__(self, parent=None, prefix=vaca_prefix):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('Power Supplies Diagnostics')
        self._setupUi()
        self._initialized = False

    def _setupUi(self):
        # Leds Panel
        cw = QWidget(self)
        panel = QWidget(cw)
        panel_lay = QGridLayout()
        panel_lay.setVerticalSpacing(0)
        panel_lay.setHorizontalSpacing(5)
        panel.setLayout(panel_lay)

        # # Leds Header
        for i, lab in enumerate(
                ['', 'PS\nConn?', 'MA\nConn?',
                 'Power\nState', 'Interlock',
                 'OpMode\nSlowRef?', 'Current\nDiff']):
            label = QLabel(lab, panel, alignment=Qt.AlignCenter)
            if i > 0:
                label.setStyleSheet("min-width:4em; max-width:4em;")
            panel_lay.addWidget(label, 0, i)

        # # Leds panel
        _on = _PSConst.PwrStateSts.On
        _slowref = _PSConst.States.SlowRef
        i = 2
        for sec in sec2label.keys():
            seclabel = QLabel('<h3>'+sec2label[sec]+'</h3>', panel)
            panel_lay.addWidget(seclabel, i, 0)
            i += 1
            if sec == 'LI':
                for ps in lips2labels.keys():
                    ps_label = QLabel(
                        lips2labels[ps], panel,
                        alignment=Qt.AlignRight | Qt.AlignVCenter)
                    ps_ch2vals = dict()
                    intlk_ch2vals = dict()
                    conn_chs = list()
                    psnames = Filter.process_filters(
                        LINAC_PS, filters={'dis': ps})
                    for name in psnames:
                        pname = self._prefix + name
                        conn_chs.append(pname+':setpwm')
                        ps_ch2vals[pname + ':setpwm'] = 1
                        intlk_ch2vals[pname + ':interlock'] = \
                            {'value': 55, 'comp': 'lt'}

                    f = 'LA-.*:'+ps
                    conn_led = MyLedMultiConnection(
                        filter=f, parent=panel, channels=conn_chs)
                    ps_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=ps_ch2vals)
                    intlk_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=intlk_ch2vals)

                    suf = ps.strip('.*')+'_led'
                    conn_led.setObjectName('conn' + suf)
                    ps_led.setObjectName('ps' + suf)
                    intlk_led.setObjectName('intlk' + suf)

                    panel_lay.addWidget(ps_label, i, 0)
                    panel_lay.addWidget(conn_led, i, 1)
                    panel_lay.addWidget(ps_led, i, 3)
                    panel_lay.addWidget(intlk_led, i, 4)
                    i += 1
            else:
                for ps in asps2labels.keys():
                    psnames = PSSearch.get_psnames(
                        filters={'sec': sec, 'dev': ps})
                    if not psnames:
                        continue
                    maconn_chs = list()
                    psconn_chs = list()
                    ps_ch2vals = dict()
                    intlk_ch2vals = dict()
                    opm_ch2vals = dict()
                    diff_ch2vlas = dict()
                    for name in psnames:
                        pname = self._prefix + name
                        maname = MASearch.conv_psname_2_psmaname(name)
                        if maname:
                            maconn_chs.append(
                                self._prefix+maname+':Version-Cte')
                        psconn_chs.append(pname+':Version-Cte')
                        ps_ch2vals[pname+':PwrState-Sts'] = _on
                        intlk_ch2vals[pname+':IntlkSoft-Mon'] = 0
                        intlk_ch2vals[pname+':IntlkHard-Mon'] = 0
                        opm_ch2vals[pname+':OpMode-Sts'] = _slowref
                        diff_ch2vlas[pname+':DiagStatus-Mon'] = \
                            {'value': 0, 'bit': 2}

                    f = sec+'-.*PS-'+ps
                    ps_label = QLabel(
                        asps2labels[ps], panel,
                        alignment=Qt.AlignRight | Qt.AlignVCenter)
                    psconn_led = MyLedMultiConnection(
                        filter=f, parent=panel, channels=psconn_chs)
                    maconn_led = MyLedMultiConnection(
                        filter=f.replace('PS', 'MA'),
                        parent=panel, channels=maconn_chs)
                    ps_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=ps_ch2vals)
                    intlk_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=intlk_ch2vals)
                    opm_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=opm_ch2vals)
                    opm_led.setOnColor(PyDMLed.LightGreen)
                    opm_led.setOffColor(PyDMLed.Yellow)
                    diff_led = MyLedMultiChannel(
                        filter=f, parent=panel, channels2values=diff_ch2vlas)

                    suf = ps.strip('.*')+'_led'
                    psconn_led.setObjectName('psconn' + suf)
                    maconn_led.setObjectName('maconn' + suf)
                    ps_led.setObjectName('ps' + suf)
                    intlk_led.setObjectName('intlk' + suf)
                    opm_led.setObjectName('opm' + suf)
                    diff_led.setObjectName('diff' + suf)

                    panel_lay.addWidget(ps_label, i, 0)
                    panel_lay.addWidget(psconn_led, i, 1)
                    panel_lay.addWidget(maconn_led, i, 2)
                    panel_lay.addWidget(ps_led, i, 3)
                    panel_lay.addWidget(intlk_led, i, 4)
                    panel_lay.addWidget(opm_led, i, 5)
                    panel_lay.addWidget(diff_led, i, 6)
                    i += 1
            panel_lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored,
                              QSzPlcy.MinimumExpanding), i, 0)
            i += 1

        # Current State and Log Tables
        channels = list()
        for ps in PSSearch.get_psnames():
            channels.append(self._prefix+ps+':DiagCurrentDiff-Mon')
        self._status = LogTable(cw, channels, is_status=True)
        self._status.setObjectName('status_table')
        self._status.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._status.updated.connect(self._filter_table)
        self._log = LogTable(cw, channels)
        self._log.setObjectName('log_table')
        self._log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._tables_stack = QStackedLayout()
        self._tables_stack.addWidget(self._status)
        self._tables_stack.addWidget(self._log)

        self._rb_status = QRadioButton('Status', self)
        self._rb_status.setObjectName('rb_status')
        self._rb_status.setChecked(True)
        self._visible_table = self._status
        self._rb_status.toggled.connect(_partial(self._toggle_table, 0))
        self._rb_log = QRadioButton('Log', self)
        self._rb_log.setObjectName('rb_log')
        self._rb_log.toggled.connect(_partial(self._toggle_table, 1))

        for name in ['Date', 'Time', 'Log Type',
                     'PS Name', 'Property', 'Value']:
            setattr(self, '_search_'+name.replace(' ', '').lower(),
                    QLineEdit())
            le = getattr(self, '_search_'+name.replace(' ', '').lower())
            le.setPlaceholderText(name + '...')
            le.editingFinished.connect(self._filter_table)

        self._scrollup_pb = QPushButton('↟', cw)
        self._scrollup_pb.setObjectName('scrollup_pb')
        self._scrollup_pb.clicked.connect(self._arrange_table)

        self._scrolldown_pb = QPushButton('↡', cw)
        self._scrolldown_pb.setObjectName('scrolldown_pb')
        self._scrolldown_pb.clicked.connect(self._arrange_table)

        tables_lay = QGridLayout()
        tables_lay.setVerticalSpacing(2)
        tables_lay.setHorizontalSpacing(1)
        tables_lay.addWidget(self._search_date, 0, 0)
        tables_lay.addWidget(self._search_time, 0, 1)
        tables_lay.addWidget(self._search_logtype, 0, 2)
        tables_lay.addWidget(self._search_psname, 0, 3)
        tables_lay.addWidget(self._search_property, 0, 4)
        tables_lay.addWidget(self._search_value, 0, 5)
        tables_lay.addWidget(self._scrollup_pb, 0, 6, alignment=Qt.AlignRight)
        tables_lay.addLayout(self._tables_stack, 1, 0, 1, 7)
        tables_lay.addWidget(self._rb_status, 2, 0, alignment=Qt.AlignLeft)
        tables_lay.addWidget(self._rb_log, 2, 1, alignment=Qt.AlignLeft)
        tables_lay.addWidget(self._scrolldown_pb, 2, 6,
                             alignment=Qt.AlignRight)
        tables = QWidget(cw)
        tables.setObjectName('tables')
        tables.setLayout(tables_lay)

        # Connect signals
        for led in self.findChildren(QLed):
            led.shape = PyDMLed.ShapeMap.Round
            led.filterlog.connect(self._filter_table)
            led.warning.connect(self._log.add_log_slot)
            led.warning.connect(self._status.add_log_slot)
            led.normal.connect(self._status.remove_log_slot)

        # Layout
        window_title = QLabel('<h2>Power Supplies Diagnostics</h2>', cw,
                              alignment=Qt.AlignCenter)
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)
        layout.addWidget(window_title, 0, 0, 1, 2)
        layout.addWidget(panel, 1, 0)
        layout.addWidget(tables, 1, 1)

        cw.setStyleSheet("""
            #scrollup_pb, #scrolldown_pb{
                max-height: 1em;
                max-width: 0.7em;
                color: #464646;
            }
            QLineEdit{
                max-height: 1em;
            }
            #status_table, #log_table{
                border: 1px solid #bebebe;
            }
            #tables{
                min-width: 45em;
            }
            #rb_status, #rb_log{
                min-width: 5em;
                max-width: 5em;
                max-height: 1em;
            }""")
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _arrange_table(self):
        text = self.sender().text()
        if '↟' in text:
            self._visible_table.scrollToTop()
        elif '↡' in text:
            self._visible_table.scrollToBottom()

    def _filter_table(self, text=''):
        # identify first user interaction
        if isinstance(self.sender(), (QLineEdit, QLed)):
            self._initialized = True
        # ignore initializing
        if not self._initialized:
            return
        # set led's filter
        if isinstance(self.sender(), QLed):
            self.blockSignals(True)
            self._search_psname.setText(text)
            self.blockSignals(False)

        # get search filters
        pats = list()
        date_txt = self._search_date.text()
        time_txt = self._search_time.text()
        logtype_txt = self._search_logtype.text()
        psname_txt = self._search_psname.text()
        property_txt = self._search_property.text()
        value_txt = self._search_value.text()
        try:
            if date_txt:
                pats.append([_re.compile(date_txt, _re.I), 0])
            if time_txt:
                pats.append([_re.compile(time_txt, _re.I), 1])
            if logtype_txt:
                pats.append([_re.compile(logtype_txt, _re.I), 2])
            if psname_txt:
                pats.append([_re.compile(psname_txt, _re.I), 3])
            if property_txt:
                pats.append([_re.compile(property_txt, _re.I), 4])
            if value_txt:
                pats.append([_re.compile(value_txt, _re.I), 5])
        except Exception:
            return

        m = self._visible_table.model()
        for row in range(m.rowCount()):
            for pat, col in pats:
                if not pat.search(m.data(m.index(row, col))):
                    self._visible_table.setRowHidden(
                        row, self._visible_table.rootIndex(), True)
                    break
            else:
                self._visible_table.setRowHidden(
                    row, self._visible_table.rootIndex(), False)

    def _toggle_table(self, i, toggle):
        if not toggle:
            return

        self._tables_stack.setCurrentIndex(i)
        if i == 0:
            self._log.updated.disconnect(self._filter_table)
            self._status.updated.connect(self._filter_table)
            self._visible_table = self._status
        else:
            self._status.updated.disconnect(self._filter_table)
            self._log.updated.connect(self._filter_table)
            self._visible_table = self._log
        self._filter_table()


class LogTable(QTreeView, PyDMWidget):
    """Log Table."""

    updated = Signal()

    def __init__(self, parent=None, channels=list(), is_status=False):
        # QTableView.__init__(self, parent)
        QTreeView.__init__(self, parent)
        PyDMWidget.__init__(self)

        # setup table
        self._is_status = is_status
        self._date_fmt = '%Y/%m/%d'
        self._time_fmt = '%H:%M:%S'
        self.headerLabels = ['Date', 'Time', 'Log Type',
                             'PS Name', 'Property', 'Value']
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(self.headerLabels)
        self.setModel(self._model)
        self.setUniformRowHeights(True)
        self._hheader = QHeaderView(Qt.Horizontal)
        self._hheader.setResizeMode(QHeaderView.Stretch)
        self.setHeader(self._hheader)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setItemDelegateForColumn(2, LogItemDelegate(self))
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setStyleSheet("gridline-color: #ffffff;")

        # set channels
        self.channels2conn = dict()
        for address in channels:
            self.channels2conn[address] = False
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_slot=self.value_changed,
                severity_slot=self.alarm_severity_changed)
            channel.connect()
            self._channels.append(channel)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        address = self.sender().address
        self.channels2conn[address] = conn
        allconn = True
        for conn in self.channels2conn.values():
            allconn &= conn
        self.setState(allconn)
        self._connected = allconn

    def add_log_slot(self, updated):
        new_value = self._get_newitem_data(updated)
        self.add_log(new_value)

    def add_log(self, new_value):
        if self._is_status:
            self.remove_log(new_value)

        datetime_now = _datetime.now()
        item_data = [QStandardItem(text) for text in (
            datetime_now.date().strftime(self._date_fmt),
            datetime_now.time().strftime(self._time_fmt),
            new_value['logtype'], new_value['psname'],
            new_value['propty'], new_value['value'])]
        for item in item_data:
            item.setTextAlignment(Qt.AlignCenter)

        self._model.insertRow(0, item_data)
        if self._model.rowCount() > 10000:
            self._model.removeRow(self._model.rowCount()-1)
        self.updated.emit()

    def remove_log_slot(self, updated):
        new_value = self._get_newitem_data(updated)
        self.remove_log(new_value)

    def remove_log(self, new_value):
        for row in range(self._model.rowCount()):
            logtype = self._model.data(self._model.index(row, 2))
            if logtype != new_value['logtype']:
                continue
            psname = self._model.data(self._model.index(row, 3))
            if psname != new_value['psname']:
                continue
            propty = self._model.data(self._model.index(row, 4))
            if propty != new_value['propty']:
                continue
            self._model.removeRow(row)
        self.updated.emit()

    def alarm_severity_changed(self, new_alarm_severity):
        """Reimplement alarm_severity_changed."""
        if self.sender():
            address = self.sender().address
            pv = SiriusPVName(address)
            value = self.sender()._value
            new_value = {'logtype': 'WARN', 'psname': pv.device_name,
                         'propty': pv.propty_name, 'value': str(value)}
            if new_alarm_severity in [_Severity.MINOR_ALARM,
                                      _Severity.MAJOR_ALARM]:
                self.add_log(new_value)
            elif self._is_status:
                self.remove_log(new_value)

            super().alarm_severity_changed(new_alarm_severity)

    def _get_newitem_data(self, updated):
        pv, value = updated
        pv = SiriusPVName(pv)

        if value is None:
            return
        if 'conn' in self.sender().objectName():
            str_value = 'disconnected'
            logtype = 'DISCONNECT'
        elif pv.propty_name == 'PwrState':
            # TODO: remove the folowing step when the bug in PS is solved
            val = value[0] if isinstance(value, _np.ndarray) else value
            str_value = _PSEnums.PWRSTATE_STS[val]
            logtype = 'ERR'
        elif pv.propty_name == 'OpMode':
            # TODO: remove the folowing step when the bug in PS is solved
            val = value[0] if isinstance(value, _np.ndarray) else value
            str_value = _PSEnums.STATES[val]
            logtype = 'WARN'
        else:
            str_value = str(value)
            logtype = 'ERR'

        return {'logtype': logtype,
                'psname': pv.device_name,
                'propty': '' if logtype == 'DISCONNECT' else pv.propty_name,
                'value': str_value}

    def mouseDoubleClickEvent(self, ev):
        """Trigger open PS detail window."""
        idx = self.selectedIndexes()
        text = self._model.data(self._model.index(idx[0].row(), 3))
        if SiriusPVName(text).dis == 'MA':
            _run_newprocess(['sirius-hla-as-ps-detail.py', text])
        else:
            try:
                PSSearch.conv_psname_2_dclink(text)
            except KeyError:
                pass
            else:
                _run_newprocess(['sirius-hla-as-ps-detail.py', text])
        super().mouseDoubleClickEvent(ev)


class LogItemDelegate(QItemDelegate):
    """Log Item Delegate."""

    def paint(self, painter, option, index):
        """Paint."""
        logtype = self.parent().model().data(
            index.sibling(index.row(), 2))
        if logtype.upper() == 'WARN':
            painter.fillRect(option.rect, PyDMLed.Yellow)
        elif logtype.upper() == 'ERR':
            painter.fillRect(option.rect, PyDMLed.Red)
        elif logtype.upper() == 'DISCONNECT':
            painter.fillRect(option.rect, PyDMLed.Gray)

        QItemDelegate.paint(self, painter, option, index)


def create_led_class(type='multichannel'):
    if type == 'multichannel':
        led_class = PyDMLedMultiChannel
    else:
        led_class = PyDMLedMultiConnection

    class MyLed(led_class):

        filterlog = Signal(str)

        def __init__(self, filter, **kwargs):
            super().__init__(**kwargs)
            self.filter = filter

        def mouseDoubleClickEvent(self, ev):
            self.filterlog.emit(self.filter)
            super().mouseDoubleClickEvent(ev)

    return MyLed


MyLedMultiChannel = create_led_class('multichannel')
MyLedMultiConnection = create_led_class('multiconn')


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSDiag()
    window.show()
    sys.exit(app.exec_())
