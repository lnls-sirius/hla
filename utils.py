import os
import sys
import numpy as np
from epics import PV
from PyQt5.QtWidgets import (QPushButton, QLabel, QGridLayout, QGroupBox,
                             QFormLayout, QMessageBox, QApplication,
                             QSizePolicy, QWidget, QComboBox, QSpinBox,
                             QVBoxLayout, QHBoxLayout, QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QSize, Qt, pyqtSlot
from pydm.application import PyDMApplication
from pydm.widgets import PyDMImageView, PyDMLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from matplotlib import rcParams
from pyqtgraph import PlotCurveItem, mkPen
from scipy.optimize import curve_fit
from scipy.stats import norm


def set_environ():
    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '21000000'
    os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
    os.environ['EPICS_CA_ADDR_LIST'] = \
        "10.128.1.11:5064 10.128.1.11:5066 10.128.1.11:5068 10.128.1.11:5070 \
         10.128.1.12:5064 10.128.1.12:5070 10.128.1.13:5064 10.128.1.13:5068 \
         10.128.1.13:5070 10.128.1.14:5064 10.128.1.14:5068 10.128.1.14:5070 \
         10.128.1.15:5064 10.128.1.15:5068 10.128.1.15:5070 10.128.1.18:5064 \
         10.128.1.18:5068 10.128.1.18:5070 10.128.1.19:5064 10.128.1.19:5068 \
         10.128.1.19:5070 10.128.1.20:5064 10.128.1.20:5066 10.128.1.20:5068 \
         10.128.1.20:5070 10.128.1.20:5072 10.128.1.20:5074 10.128.1.20:5076 \
         10.128.1.20:5078 10.128.1.20:5080 10.128.1.20:5082 10.128.1.20:5084 \
         10.128.1.20:5086 10.128.1.20:5088 10.128.1.20:5090 10.128.1.20:5092 \
         10.128.1.20:5094 10.128.1.20:5096 10.128.1.20:5098 10.128.1.20:5100 \
         10.128.1.20:5102 10.128.1.20:5104 10.128.1.20:5106 10.128.1.20:5108 \
         10.128.1.20:5110 10.128.1.20:5112 10.128.1.20:5114 10.128.1.20:5116 \
         10.128.1.20:5118 10.128.1.20:5120 10.128.1.20:5122 10.128.1.20:5124 \
         10.128.1.20:5126 10.128.1.20:5128 10.128.1.20:5130 10.128.1.20:5132 \
         10.128.1.20:5134 10.128.1.20:5136 10.128.1.20:5138 10.128.1.20:5140 \
         10.128.1.20:5142 10.128.1.20:5144 10.128.1.20:5146 10.128.1.20:5148 \
         10.128.1.20:5150 10.128.1.20:5152 10.128.1.20:5154 10.128.1.20:5156 \
         10.128.1.20:5158 10.128.1.20:5160 10.128.1.20:5162 10.128.1.50:5064 \
         10.128.1.50:5067 10.128.1.50:5069 10.128.1.50:5071 10.128.1.51:5064 \
         10.128.1.51:5067 10.128.1.51:5069 10.128.1.51:5071 10.128.1.54:5064"


def gettransmat(type, L, gamma, K1=None, B=None):
    R = np.eye(6)

    if K1 is not None and K1 == 0:
        type = 'drift'
    if type.lower().startswith('dr'):
        R = np.array([
            [1, L, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, L, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, L/gamma**2],
            [0, 0, 0, 0, 0, 1],
            ])
    elif type.lower().startswith('qu') and K1 is not None:
        kq = np.sqrt(abs(K1))
        c = np.cos(kq*L)
        s = np.sin(kq*L)
        ch = np.cosh(kq*L)
        sh = np.sinh(kq*L)
        if K1 >= 0:
            x11, x12, x21 = c,  1/kq*s, -kq*s
            y11, y12, y21 = ch, 1/kq*sh, kq*sh
        else:
            x11, x12, x21 = ch, 1/kq*sh, kq*sh
            y11, y12, y21 = c,  1/kq*s, -kq*s
        R = np.array([
            [x11, x12, 0,   0,   0, 0],
            [x21, x11, 0,   0,   0, 0],
            [0,   0,   y11, y12, 0, 0],
            [0,   0,   y21, y11, 0, 0],
            [0,   0,   0,   0,   1, L/gamma**2],
            [0,   0,   0,   0,   0, 1],
            ])
    elif type.lower().startswith('sol') and B is not None:
        K = -light_speed*B/2.0/electron_rest_en/gamma/1e6
        C = np.cos(K*L)
        S = np.sin(K*L)
        SC = C*S
        C2 = C**2
        S2 = S**2
        R = np.array([
            [C2,    SC/K,  SC,    S2/K, 0., 0.],
            [-K*SC, C2,    -K*S2, SC,   0., 0.],
            [-SC,   -S2/K, C2,    SC/K, 0., 0.],
            [K*S2,  -SC,   -K*SC, C2,   0., 0.],
            [0.,    0.,    0.,    0.,   1., L/(gamma**2)],
            [0.,    0.,    0.,    0.,   0., 1.]
            ])
    return R


def _calc_moments(axis, proj):
    dx = axis[1]-axis[0]
    Norm = np.trapz(proj, dx=dx)
    cen = np.trapz(proj*axis, dx=dx)/Norm
    sec = np.trapz(proj*axis*axis, dx=dx)/Norm
    std = np.sqrt(sec - cen*cen)
    return cen, std


def _gaussian(x, amp, mu, sigma, y0):
    return amp*np.exp(-(x-mu)**2.0/(2.0*sigma**2.0))+y0


def _fit_gaussian(x, y, amp=None, mu=None, sigma=None, y0=None):
    amp = amp or np.amax(y)
    par = _calc_moments(x, y)
    mu = mu or par[0]
    sigma = sigma or par[1]
    y0 = y0 or np.mean(y)
    try:
        p_opt, p_cov = curve_fit(_gaussian, x, y, (amp, mu, sigma, y0))
    except Exception:
        p_opt = (amp, mu, sigma, y0)
        print('Fitting Problem')
    return p_opt


class MatplotlibWidget(Canvas):
    """
    Options: option_name (default_value)
    -------
    parent (None): parent widget
    title (''): figure title
    xlabel (''): X-axis label
    ylabel (''): Y-axis label
    xlim (None): X-axis limits ([min, max])
    ylim (None): Y-axis limits ([min, max])
    xscale ('linear'): X-axis scale
    yscale ('linear'): Y-axis scale
    width (4): width in inches
    height (3): height in inches
    dpi (100): resolution in dpi
    hold (False): if False, figure will be cleared each time plot is called

    Widget attributes:
    -----------------
    figure: instance of matplotlib.figure.Figure
    axes: figure axes

    Example:
    -------
    self.widget = MatplotlibWidget(self, yscale='log', hold=True)
    from numpy import linspace
    x = linspace(-10, 10)
    self.widget.axes.plot(x, x**2)
    self.wdiget.axes.plot(x, x**3)
    """
    def __init__(self, parent=None, title='', xlabel='', ylabel='',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=4, height=3, dpi=100, hold=False):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        if xscale is not None:
            self.axes.set_xscale(xscale)
        if yscale is not None:
            self.axes.set_yscale(yscale)
        if xlim is not None:
            self.axes.set_xlim(*xlim)
        if ylim is not None:
            self.axes.set_ylim(*ylim)

        super().__init__(self.figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)


class ImageView(PyDMImageView):

    def __init__(self, callback, **kwargs):
        self.callback = callback
        super().__init__(**kwargs)

    @pyqtSlot(np.ndarray)
    def image_value_changed(self, image):
        image = self.callback(image, self._image_width)
        super().image_value_changed(image)


class ProcessImage(QWidget):
    PROF = 'PRF4'

    def __init__(self, parent=None, prof=None):
        super().__init__(parent)
        self.PROF = prof or self.PROF
        self.cen_x = None
        self.cen_y = None
        self.sigma_x = None
        self.sigma_y = None
        self.bg_ready = False
        self.bg = None
        self.nbg = 0
        self._setupUi()
        self.gauss_coefx = PV('LA-BI:'+self.PROF+':X:Gauss:Coef')
        self.gauss_coefy = PV('LA-BI:'+self.PROF+':Y:Gauss:Coef')

    def _setupUi(self):
        vl = QVBoxLayout(self)
        self.image_view = ImageView(
            self.process_image,
            parent=self,
            image_channel='ca://LA-BI:'+self.PROF+':RAW:ArrayData',
            width_channel='ca://LA-BI:'+self.PROF+':ROI:MaxSizeX_RBV')
        self.image_view.maxRedrawRate = 5
        self.image_view.readingOrder = self.image_view.Clike
        self.plt_roi = PlotCurveItem([0, 0, 400, 400, 0], [0, 400, 400, 0, 0])
        pen = mkPen()
        pen.setColor(QColor('red'))
        pen.setWidth(1)
        self.plt_roi.setPen(pen)
        self.image_view.addItem(self.plt_roi)
        self.plt_fit_x = PlotCurveItem([0, 0], [0, 400])
        self.plt_fit_y = PlotCurveItem([0, 0], [0, 400])
        self.image_view.addItem(self.plt_fit_x)
        self.image_view.addItem(self.plt_fit_y)
        vl.addWidget(self.image_view)

        gb_pos = QGroupBox('Position [mm]', self)
        vl.addWidget(gb_pos)
        hl = QHBoxLayout(gb_pos)
        fl = QFormLayout()
        hl.addItem(fl)
        self.cbox_method = QComboBox(gb_pos)
        self.cbox_method.addItem('Gauss Fit')
        self.cbox_method.addItem('Moments')
        fl.addRow(QLabel('Method', gb_pos), self.cbox_method)
        self.spbox_roi_size_x = QSpinBox(gb_pos)
        self.spbox_roi_size_y = QSpinBox(gb_pos)
        self.spbox_roi_center_x = QSpinBox(gb_pos)
        self.spbox_roi_center_y = QSpinBox(gb_pos)
        self.spbox_roi_size_x.setKeyboardTracking(False)
        self.spbox_roi_size_y.setKeyboardTracking(False)
        self.spbox_roi_center_x.setKeyboardTracking(False)
        self.spbox_roi_center_y.setKeyboardTracking(False)
        self.spbox_roi_size_x.setMaximum(2448)
        self.spbox_roi_size_y.setMaximum(2050)
        self.spbox_roi_center_x.setMaximum(2448)
        self.spbox_roi_center_y.setMaximum(2050)
        self.spbox_roi_size_x.setValue(300)
        self.spbox_roi_size_y.setValue(400)
        self.spbox_roi_center_x.setValue(500)
        self.spbox_roi_center_y.setValue(500)
        fl.addRow(QLabel('ROI Size X', gb_pos), self.spbox_roi_size_x)
        fl.addRow(QLabel('ROI Size Y', gb_pos), self.spbox_roi_size_y)
        self.cbbox_auto_center = QCheckBox('Automatic Centering', gb_pos)
        self.cbbox_auto_center.clicked.connect(self.cbbox_auto_center_clicked)
        self.cbbox_auto_center.setChecked(True)
        fl.addRow(self.cbbox_auto_center)
        fl.addRow(QLabel('ROI Center X', gb_pos), self.spbox_roi_center_x)
        fl.addRow(QLabel('ROI Center Y', gb_pos), self.spbox_roi_center_y)
        self.spbox_img_max = QSpinBox(gb_pos)
        self.spbox_img_max.setKeyboardTracking(False)
        self.spbox_img_max.setMinimum(0)
        self.spbox_img_max.setMaximum(2448)
        self.spbox_img_max.setValue(0)
        fl.addRow(QLabel('Max. Pixel Val.', gb_pos), self.spbox_img_max)
        self.cbbox_acq_bg = QCheckBox('Acquire Background', gb_pos)
        self.cbbox_acq_bg.clicked.connect(self.cbbox_acq_bg_checked)
        fl.addRow(self.cbbox_acq_bg)
        self.pb_reset_bg = QPushButton('Reset BG', gb_pos)
        self.pb_reset_bg.clicked.connect(self.pb_reset_bg_clicked)
        fl.addRow(self.pb_reset_bg)
        fl = QFormLayout()
        hl.addItem(fl)
        self.lb_xave = QLabel('0.000', gb_pos)
        self.lb_yave = QLabel('0.000', gb_pos)
        self.lb_xstd = QLabel('0.000', gb_pos)
        self.lb_ystd = QLabel('0.000', gb_pos)
        fl.addRow(QLabel('Average Position', gb_pos))
        fl.addRow(QLabel('x = ', gb_pos), self.lb_xave)
        fl.addRow(QLabel('y = ', gb_pos), self.lb_yave)
        fl.addRow(QLabel('Beam Size', gb_pos))
        fl.addRow(QLabel('x = ', gb_pos), self.lb_xstd)
        fl.addRow(QLabel('y = ', gb_pos), self.lb_ystd)

    def cbbox_auto_center_clicked(self, clicked):
        self.spbox_roi_center_x.setEnabled(not clicked)
        self.spbox_roi_center_y.setEnabled(not clicked)

    def pb_reset_bg_clicked(self, clicked=False):
        self.bg_ready = False
        self.bg = None
        self.nbg = 0

    def cbbox_acq_bg_checked(self, check):
        if check:
            self.pb_reset_bg_clicked()
        else:
            if self.bg is not None:
                self.bg /= self.nbg
                self.bg_ready = True

    def calc_roi(self, image):
        proj_x = image.sum(axis=0)
        proj_y = image.sum(axis=1)
        axis_x = np.arange(image.shape[1])
        axis_y = np.arange(image.shape[0])

        if self.cbbox_auto_center.isChecked():
            cen_x, _ = _calc_moments(axis_x, proj_x)
            cen_y, _ = _calc_moments(axis_y, proj_y)
        else:
            cen_x = self.spbox_roi_center_x.value()
            cen_y = self.spbox_roi_center_y.value()

        roi_size_x = self.spbox_roi_size_x.value()
        roi_size_y = self.spbox_roi_size_y.value()
        strt_x, end_x = np.array([-1, 1])*roi_size_x + int(cen_x)
        strt_y, end_y = np.array([-1, 1])*roi_size_y + int(cen_y)
        strt_x = max(strt_x, 0)
        strt_y = max(strt_y, 0)
        end_x = min(end_x, image.shape[1])
        end_y = min(end_y, image.shape[0])
        self.plt_roi.setData(
            np.array([strt_x, strt_x, end_x, end_x, strt_x]),
            np.array([strt_y, end_y, end_y, strt_y, strt_y]))

        proj_x = proj_x[strt_x:end_x]
        axis_x = axis_x[strt_x:end_x]
        proj_y = proj_y[strt_y:end_y]
        axis_y = axis_y[strt_y:end_y]
        return proj_x, proj_y, axis_x, axis_y

    def process_image(self, image, wid):
        if wid <= 0:
            return image
        try:
            image = image.reshape((-1, wid))
        except (TypeError, ValueError, AttributeError):
            return image

        if self.cbbox_acq_bg.isChecked():
            if self.bg is None:
                self.bg = np.array(image, dtype=float)
            else:
                self.bg += np.array(image, dtype=float)
            self.nbg += 1
            return image

        if self.bg_ready:
            image -= np.array(self.bg, dtype=image.dtype)
            b = np.where(image <0)
            image[b] = 0

        maxi = self.spbox_img_max.value()
        if maxi>0:
            b = np.where(image > maxi)
            self.image_view.colorMapMax = maxi
            image[b] = maxi

        proj_x, proj_y, axis_x, axis_y = self.calc_roi(image)

        coefx = self.gauss_coefx.value
        coefy = self.gauss_coefy.value
        if coefx is None or coefy is None:
            return

        if self.cbox_method.currentIndex():
            cen_x, std_x = _calc_moments(axis_x, proj_x)
            cen_y, std_y = _calc_moments(axis_y, proj_y)
        else:
            _, cen_x, std_x, _ = _fit_gaussian(axis_x, proj_x)
            _, cen_y, std_y, _ = _fit_gaussian(axis_y, proj_y)
        std_x = abs(std_x)
        std_y = abs(std_y)
        yd = _gaussian(axis_x, -400, cen_x, std_x, 0)
        self.plt_fit_x.setData(axis_x, yd + 1000)
        yd = _gaussian(axis_y, 400, cen_y, std_y, 0)
        self.plt_fit_y.setData(yd + 500, axis_y)

        offset_x = image.shape[1]/2
        offset_y = image.shape[0]/2
        cen_x -= offset_x
        cen_y -= offset_y
        self.lb_xave.setText('{0:.3f}'.format(cen_x * coefx))
        self.lb_yave.setText('{0:.3f}'.format(cen_y * coefx))
        self.lb_xstd.setText('{0:.3f}'.format(std_x * coefx))
        self.lb_ystd.setText('{0:.3f}'.format(std_y * coefx))

        self.cen_x = cen_x * coefx*1e-3  # transform to meter
        self.cen_y = cen_y * coefy*1e-3
        self.sigma_x = std_x * coefx*1e-3
        self.sigma_y = std_y * coefy*1e-3

        return image

    def get_params(self):
        return self.cen_x, self.sigma_x, self.cen_y, self.sigma_y
