"""BL AP ImgProc."""

from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QColor
from pyqtgraph import PlotCurveItem, mkPen

import qtawesome as qta
import numpy as _np

from pydm.widgets import PyDMImageView
from ..util import get_appropriate_color
from ..widgets import SiriusConnectionSignal

from .util import PVS_IMGPROC


class SiriusImageView(PyDMImageView):
    """Image Processing Window."""

    def __init__(self, device, pvname, parent=None):
        """."""
        super().__init__(parent=parent)
        self.setObjectName('SIApp')
        self.setWindowIcon(
            qta.icon('mdi.camera-metering-center',
                     color=get_appropriate_color('SI')))

        self.device = device

        self.roi = None
        self.roi_con = {}

        self.fit_mean = None
        self.fit_mean_con = {}

        self.fit_ellipse = None
        self.fit_ellipse_con = {}
        self.angle = 0
        self.sigma = [200, 200]

        self._setupUi(pvname)

    def add_prefixes(self, sufix):
        return self.device + ":" + sufix

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
        self.addItem(self.roi)

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
        pen = mkPen(QColor('white'))
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
        self.addItem(self.fit_mean)

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
        pen = mkPen(QColor('white'))
        x_mean = 200
        y_mean = 200

        theta = _np.linspace(0, 2*_np.pi, 100)
        x_points = self.sigma[0] * _np.cos(theta)
        y_points = self.sigma[1] * _np.sin(theta)

        x_centered = x_points + x_mean
        y_centered = y_points + y_mean

        self.fit_ellipse = PlotCurveItem(x_centered, y_centered)
        self.fit_ellipse.setPen(pen)
        self.addItem(self.fit_ellipse)

    def add_fit_ellipse_connection(self, param):
        fit_pvs = PVS_IMGPROC['Fit'][1]
        fit_ellipse_pv = self.add_prefixes(fit_pvs[param])
        self.fit_ellipse_con[param] = SiriusConnectionSignal(fit_ellipse_pv)
        self.fit_ellipse_con[param].new_value_signal[float].connect(
            lambda value: self.plot_fit_ellipse(value, fit_ellipse_pv))

    def _setupUi(self, pvname):
        self.image_channel = pvname[0]
        self.width_channel = pvname[1]

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

        self.readingOrder = self.ReadingOrder.Clike
        self.getView().getViewBox().setAspectLocked(True)
        self.colorMap = self.Jet
        self.maxRedrawRate = 10  # [Hz]
        self.normalizeData = True
