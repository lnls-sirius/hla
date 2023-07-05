"""BL AP ImgProc."""

from datetime import datetime

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QLabel, QSizePolicy, QTabWidget, \
    QPushButton, QScrollArea
from qtpy.QtGui import QColor
from pyqtgraph import PlotCurveItem, mkPen

import qtawesome as qta
import numpy as _np

from pydm.widgets import PyDMImageView, PyDMPushButton

from ..widgets import SiriusEnumComboBox
from ..widgets.dialog import StatusDetailDialog

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..util import get_appropriate_color
from ..widgets import SiriusLabel, SiriusLedState, \
    SiriusLineEdit, PyDMLogLabel, PyDMStateButton, \
    SiriusConnectionSignal, SiriusSpinbox, SiriusLedAlert

from .util import PVS_IMGPROC, PVS_DVF, \
    IMG_PVS, LOG_PV, COMBOBOX_PVS, LINEEDIT_PVS, STATEBUT_PVS, \
    LED_ALERT_PVS, LED_STATE_PVS, LED_DETAIL_PVS


class BLImgProc(QWidget):
    """Image Processing Window."""

    def __init__(self, dvf, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.setObjectName('SIApp')
        self.prefix = prefix + ('-' if prefix else '')
        self.dvf = dvf
        self.device = self.prefix + self.dvf
        self.setWindowTitle(self.device + ' Image Processing Window')
        self.setWindowIcon(
            qta.icon('mdi.camera-metering-center',
                     color=get_appropriate_color('SI')))
        self._lbl_timestamp = {}
        self.timestamp = {}
        self.img_view = None

        self.roi = None
        self.roi_con = {}
        self.fit_mean = None
        self.fit_mean_con = {}
        self.fit_ellipse = None
        self.fit_ellipse_con = {}
        self.angle = 0
        self.sigma = [200, 200]

        self._setupUi()

    def add_prefixes(self, sufix):
        return self.device + ":" + sufix

    def generate_pv_name(self, sufix):
        if len(sufix) != 2:
            return self.add_prefixes(sufix)

        pv_list = []
        for sf in sufix:
            try:
                pvname = self.add_prefixes(sf)
                pv_list.append(pvname)
            except:
                pv_list.append(sf)
        return pv_list

    def format_datetime_lbl(self, value, pvname):
        dtval = datetime.fromtimestamp(value)
        datetime_lbl = dtval.strftime("%d/%m/%Y, %H:%M:%S")
        datetime_lbl += '.{:03d}'.format(int(1e3*(value % 1)))
        self._lbl_timestamp[pvname].setText(datetime_lbl)

    def create_time_widget(self, pvname):
        lbl_time = QLabel('0000-00-00 0:00:00.0', self)
        self._lbl_timestamp[pvname] = lbl_time
        self._lbl_timestamp[pvname].channel = pvname
        self.timestamp[pvname] = SiriusConnectionSignal(pvname)
        self.timestamp[pvname].new_value_signal[float].connect(
            lambda value: self.format_datetime_lbl(value, pvname))
        return self._lbl_timestamp[pvname]

    def plot_roi(self, value, pvname):
        point_list = _np.zeros(5)
        if 'ROIX' in pvname:
            id_data = 0
            change_point = [
                [0, 1, 4], [2, 3]]
        else:
            id_data = 1
            change_point = [
                [0, 3, 4], [1, 2]]

        for idx, val in enumerate(value):
            for point in change_point[idx]:
                point_list[point] = val

        cur_data = self.roi.getData()
        x_points = point_list if id_data == 0 else cur_data[0]
        y_points = point_list if id_data == 1 else cur_data[1]
        self.roi.setData(x=x_points, y=y_points)

    def add_plot_curve(self):
        pen = mkPen(QColor('red'))
        x_points = [0, 400, 400, 0, 0]
        y_points = [0, 0, 400, 400, 0]
        self.roi = PlotCurveItem(x_points, y_points)
        self.roi.setPen(pen)
        self.img_view.addItem(self.roi)

    def add_roi_connection(self, axis):
        roi_pvs = PVS_IMGPROC['ROI'][1]
        roi_pv = self.add_prefixes(roi_pvs[axis]['Min Max'][1])
        self.roi_con[axis] = SiriusConnectionSignal(roi_pv)
        self.roi_con[axis].new_value_signal[_np.ndarray].connect(
            lambda value: self.plot_roi(value, roi_pv))

    def plot_fit_mean(self, value, pvname):
        if 'ROIX' in pvname:
            id_data = 0
            point_list = _np.full(7, value)
            change_point = [2, 6]
        else:
            id_data = 1
            point_list = _np.full(7, value)
            change_point = [0, 4]

        dist = 20
        for point in change_point:
            point_list[point] = value - dist
            dist *= -1

        cur_data = self.fit_mean.getData()
        x_points = point_list if id_data == 0 else cur_data[0]
        y_points = point_list if id_data == 1 else cur_data[1]
        self.fit_mean.setData(x=x_points, y=y_points)

    def add_fit_mean(self):
        pen = mkPen(QColor('red'))
        center = 200
        dist = 20
        x_points = _np.full(7, center)
        x_points[2] = center-dist
        x_points[6] = center+dist

        y_points = _np.full(7, center)
        y_points[0] = center-dist
        y_points[4] = center+dist

        self.fit_mean = PlotCurveItem(x_points, y_points)
        self.fit_mean.setPen(pen)
        self.img_view.addItem(self.fit_mean)

    def add_fit_mean_connection(self, axis):
        fit_pvs = PVS_IMGPROC['Fit'][1]
        fit_mean_pv = self.add_prefixes(fit_pvs[axis]['ROI Mean'])
        self.fit_mean_con[axis] = SiriusConnectionSignal(fit_mean_pv)
        self.fit_mean_con[axis].new_value_signal[float].connect(
            lambda value: self.plot_fit_mean(value, fit_mean_pv))

    def plot_fit_ellipse(self, value, pvname):
        theta = _np.linspace(0, 2*_np.pi, 100)
        centroid_raw = self.fit_mean.getData()
        centroid = [centroid_raw[0][3], centroid_raw[1][3]]

        if 'Angle' in pvname:
            self.angle = value
        elif 'Sigma1' in pvname:
            self.sigma[0] = value
        else:
            self.sigma[1] = value

        theta = _np.linspace(0, 2*_np.pi, 100)
        x_points = self.sigma[0] * _np.cos(theta)
        y_points = self.sigma[1] * _np.sin(theta)

        x_rotated = x_points * _np.cos(self.angle) - y_points * _np.sin(self.angle)
        y_rotated = x_points * _np.sin(self.angle) + y_points * _np.cos(self.angle)

        x_centered = x_rotated + centroid[0]
        y_centered = y_rotated + centroid[1]

        self.fit_ellipse.setData(x=x_centered, y=y_centered)

    def add_fit_ellipse(self):
        pen = mkPen(QColor('red'))
        x_mean = 200
        y_mean = 200

        theta = _np.linspace(0, 2*_np.pi, 100)
        x_points = self.sigma[0] * _np.cos(theta)
        y_points = self.sigma[1] * _np.sin(theta)

        x_centered = x_points + x_mean
        y_centered = y_points + y_mean

        self.fit_ellipse = PlotCurveItem(x_centered, y_centered)
        self.fit_ellipse.setPen(pen)
        self.img_view.addItem(self.fit_ellipse)

    def add_fit_ellipse_connection(self, param):
        fit_pvs = PVS_IMGPROC['Fit'][1]
        fit_ellipse_pv = self.add_prefixes(fit_pvs[param])
        self.fit_ellipse_con[param] = SiriusConnectionSignal(fit_ellipse_pv)
        self.fit_ellipse_con[param].new_value_signal[float].connect(
            lambda value: self.plot_fit_ellipse(value, fit_ellipse_pv))

    def get_image_widget(self, pvname):
        self.img_view = PyDMImageView(
            image_channel=pvname[0],
            width_channel=pvname[1])

        self.add_plot_curve()
        self.add_roi_connection('X')
        self.add_roi_connection('Y')

        self.add_fit_mean()
        self.add_fit_mean_connection('X')
        self.add_fit_mean_connection('Y')

        self.add_fit_ellipse()
        self.add_fit_ellipse_connection('Angle')
        self.add_fit_ellipse_connection('Sigma1')
        self.add_fit_ellipse_connection('Sigma2')

        self.img_view.readingOrder = self.img_view.ReadingOrder.Clike
        self.img_view.getView().getViewBox().setAspectLocked(True)
        self.img_view.colorMap = self.img_view.Jet
        self.img_view.maxRedrawRate = 10  # [Hz]
        self.img_view.normalizeData = True
        return self.img_view

    def select_widget(
            self, pv_name, widget_type='label', units=True, labels=None):
        pvname = self.generate_pv_name(pv_name)
        if widget_type == 'label':
            wid = SiriusLabel(init_channel=pvname, keep_unit=True)
            wid.showUnits = units
            wid.setAlignment(Qt.AlignCenter)
            wid.setMaximumHeight(50)
        elif widget_type == 'setpoint_readback_combo':
            sprb_type = ['enumcombo', 'label', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_edit':
            sprb_type = ['edit', 'label', False]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_sbut':
            sprb_type = ['switch', 'led_state', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_spin':
            sprb_type = ['spin', 'label', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'led_state':
            wid = SiriusLedState(init_channel=pvname)
            wid.offColor = wid.Yellow
        elif widget_type == 'led_alert':
            wid = SiriusLedAlert(init_channel=pvname)
            wid.onColor = wid.Yellow
        elif widget_type == 'leddetail':
            led = SiriusLedAlert(init_channel=pvname[0])
            details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
            details.setObjectName('bt')
            details.setStyleSheet(
                '#bt{min-width:25px;max-width:25px;icon-size:20px;}')
            _util.connect_window(
                details, StatusDetailDialog, pvname=pvname[0], parent=self,
                labels=pvname[1], section="SI", title='Status Detailed')
            wid = QWidget()
            hlay = QHBoxLayout(wid)
            hlay.addWidget(led)
            hlay.addWidget(details)
        elif widget_type == 'log':
            wid = PyDMLogLabel(init_channel=pvname)
            wid.setMaximumHeight(175)
        elif widget_type == 'edit':
            wid = SiriusLineEdit(init_channel=pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'switch':
            wid = PyDMStateButton(init_channel=pvname)
        elif widget_type == 'enumcombo':
            wid = SiriusEnumComboBox(self, init_channel=pvname)
        elif widget_type == 'image':
            wid = self.get_image_widget(pvname)
        elif widget_type == 'time':
            wid = self.create_time_widget(pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'spin':
            wid = SiriusSpinbox(init_channel=pvname)
        elif widget_type == 'cmd':
            wid = PyDMPushButton(init_channel=pvname, pressValue=1)
            wid.setIcon(qta.icon('fa5s.sync'))
            wid.setObjectName('bt')
            wid.setStyleSheet(
                '#bt{min-width:25px;max-width:25px;icon-size:20px;}')
        else:
            wid = QLabel("Widget has not been implemented yet!")
        return wid

    def setpoint_readback_widget(self, pv_list, sprb_type):
        wid = QWidget()
        wid.setContentsMargins(0, 0, 0, 0)
        if sprb_type[2]:
            lay = QHBoxLayout()
        else:
            lay = QVBoxLayout()
        wid.setLayout(lay)

        for x in range(0, 2):
            widget = self.select_widget(
                pv_list[x], sprb_type[x], units=False)
            widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            lay.addWidget(widget)
        return wid

    def create_widget(self, title, pv_name):
        if title in LED_ALERT_PVS:
            wid_type = 'led_alert'
        elif title in LED_STATE_PVS:
            wid_type = 'led_state'
        elif title in LED_DETAIL_PVS:
            wid_type = 'leddetail'
        elif 'Time' in pv_name and 'Proc' not in pv_name:
            wid_type = 'time'
        elif '-Cmd' in pv_name:
            wid_type = 'cmd'
        elif title in LOG_PV:
            wid_type = 'log'
        elif title in IMG_PVS:
            wid_type = 'image'
        elif len(pv_name) != 2:
            wid_type = 'label'
        elif title in COMBOBOX_PVS:
            wid_type = 'setpoint_readback_combo'
        elif title in LINEEDIT_PVS:
            wid_type = 'setpoint_readback_edit'
        elif title in STATEBUT_PVS:
            wid_type = 'setpoint_readback_sbut'
        else:
            wid_type = 'setpoint_readback_spin'

        hlay = QHBoxLayout()
        wid = self.select_widget(pv_name, wid_type)
        if wid_type not in ['log', 'image']:
            title_wid = QLabel(title + ': ')
            title_wid.setAlignment(Qt.AlignRight)
            hlay.addWidget(
                title_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
            hlay.addWidget(wid, alignment=Qt.AlignLeft)
        else:
            hlay.addWidget(wid)

        return hlay

    def create_box_group(self, title, pv_info):
        """."""
        wid = QGroupBox(title)
        gbox = QGridLayout(wid)

        count = 0
        for title, pv in pv_info.items():
            if title in ['X', 'Y']:
                widget = self.create_box_group(title, pv)
                hpos = 0 if title == 'X' else 1
                gbox.addWidget(widget, count, hpos, 1, 1)
                if title == 'Y':
                    count += 1
            else:
                pv_lay = self.create_widget(title, pv)
                gbox.addLayout(pv_lay, count, 0, 1, 2)
                count += 1

        return wid

    def _setupTab(self, content, use_scroll=False):
        cont_wid = QWidget()
        cont_wid.setObjectName('wid')
        glay = QGridLayout()

        for title, pv_data in content.items():
            loc = pv_data[0]
            wid = self.create_box_group(title, pv_data[1])
            glay.addWidget(wid, *loc)

        glay.setColumnStretch(0, 3)
        glay.setColumnStretch(1, 1)
        glay.setColumnStretch(2, 1)
        cont_wid.setLayout(glay)

        if use_scroll:
            sc_area = QScrollArea()
            sc_area.setWidgetResizable(True)
            cont_wid.setStyleSheet('#wid{background-color: transparent;}')
            sc_area.setWidget(cont_wid)
            return sc_area
        return cont_wid

    def _setupUi(self):
        main_lay = QVBoxLayout()
        tab = QTabWidget()
        tab.setObjectName('SITab')

        title = QLabel(
            '<h3>'+self.device+' Image Processing<h3>', self,
            alignment=Qt.AlignCenter)
        main_lay.addWidget(title)

        imgproc_wid = self._setupTab(PVS_IMGPROC)
        tab.addTab(imgproc_wid, "DVFImgProc")
        dvf_wid = self._setupTab(PVS_DVF, use_scroll=True)
        tab.addTab(dvf_wid, "DVF")

        main_lay.addWidget(tab)
        self.setLayout(main_lay)
