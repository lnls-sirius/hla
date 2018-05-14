"""SiriusScrnView widget."""

import numpy as np
import time
import epics
# from pyqtgraph import PlotWidget
from pydm.PyQt.QtGui import (QWidget, QLabel, QGridLayout, QVBoxLayout,
                             QSpacerItem, QGroupBox, QComboBox, QPushButton,
                             QCheckBox)
from pydm.PyQt.QtGui import QSizePolicy as QSzPlcy
from pydm.PyQt.QtCore import Qt, pyqtSlot
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMLineEdit
from siriuspy.envars import vaca_prefix as _vaca_prefix

IMAGE_MAX_HEIGHT = 1024
IMAGE_MAX_WIDTH = 1280


class _SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    def __init__(self, parent=None, image_channel=None, width_channel=None):
        """Initialize the object."""
        PyDMImageView.__init__(self, parent=parent,
                               image_channel=image_channel,
                               width_channel=width_channel)
        self._calibration_grid_image = None
        self._calibration_grid_maxdata = None
        self._calibration_grid_width = None
        self._show_calibration_grid = False

    @pyqtSlot()
    def saveCalibrationGrid(self, img, w):
    # def saveCalibrationGrid(self):
        """Save current image as calibration_grid_image."""
        # print('got grid')
        self._calibration_grid_width = w
        # img = self.image_waveform
        # self._calibration_grid_width = self.imageWidth
        self._calibration_grid_maxdata = img.max()
        grid = np.where(img < 0.5*self._calibration_grid_maxdata, True, False)
        if self.readingOrder == self.ReadingOrder.Clike:
            self._calibration_grid_image = grid.reshape(
                (-1, self._calibration_grid_width), order='C')
        else:
            self._calibration_grid_image = grid.reshape(
                (self._calibration_grid_width, -1), order='F')

    @pyqtSlot(bool)
    def showCalibrationGrid(self, show):
        """Show calibration_grid_image over the current image_waveform."""
        self._show_calibration_grid = show

    def redrawImage(self):
        """
        Set the image data into the ImageItem, if needed.

        If necessary, reshape the image to 2D first.
        """
        if not self.needs_redraw:
            return
        image_dimensions = len(self.image_waveform.shape)
        img = np.array([])
        if image_dimensions == 1:
            if self.imageWidth < 1:
                # We don't have a width for this image yet, so we can't draw it
                return
            try:
                if self.readingOrder == self.ReadingOrder.Clike:
                    img = self.image_waveform.reshape((-1, self.imageWidth),
                                                      order='C')
                else:
                    img = self.image_waveform.reshape((self.imageWidth, -1),
                                                      order='F')
            except Exception:
                print('ImageWidth property does not match image dimentions!')
        else:
            img = self.image_waveform
        # if img.shape == (1024, 1280):
        #     print(img.shape)
        if len(img) <= 0:
            return
        if ((self._show_calibration_grid) and
                (self._calibration_grid_image is not None)):
            try:
                grid = self.adjust_calibration_grid(img)
                img[grid] = self._calibration_grid_maxdata
            except Exception:
                print('Grid dimentions do not match image dimentions!')
        if self._normalize_data:
            mini = self.image_waveform.min()
            maxi = self.image_waveform.max()
        else:
            mini = self.cm_min
            maxi = self.cm_max
        self.getImageItem().setLevels([mini, maxi])
        self.getImageItem().setImage(
            img,
            autoLevels=False,
            autoDownsample=True)
        self.needs_redraw = False

    def adjust_calibration_grid(self, img):
        grid_h = min(np.size(img, 0), np.size(self._calibration_grid_image, 0))
        # print(np.size(img, 0), np.size(self._calibration_grid_image, 0))
        grid_w = min(np.size(img, 1), np.size(self._calibration_grid_image, 1))
        # print(np.size(img, 1), np.size(self._calibration_grid_image, 1))
        grid = self._calibration_grid_image[0:grid_h, 0:grid_w]
        return grid


class SiriusScrnView(QWidget):
    """
    Class to read Sirius screen cameras image data.

    To allow saving a grid correctly, control calibrationgrid_flag, which
    indicates if the screen is in calibration grid position.
    You can control it by using the method/pyqtSlot updateCalibrationGridFlag.
    """

    def __init__(self, parent=None, prefix='', device=None):
        """Initialize object."""
        QWidget.__init__(self, parent=parent)
        if prefix == '':
            self.prefix = _vaca_prefix
        else:
            self.prefix = prefix
        self.device = device
        self._calibrationgrid_flag = False
        self.setLayout(QGridLayout())
        self.setStyleSheet("""font-size:20pt;""")
        self._setupUi()

    @property
    def calibrationgrid_flag(self):
        """Indicate if the screen device is in calibration grid position."""
        return self._calibrationgrid_flag

    @pyqtSlot(int)
    def updateCalibrationGridFlag(self, new_state):
        """Update calibrationgrid_flag property."""
        if new_state != self._calibrationgrid_flag:
            self._calibrationgrid_flag = new_state

            if new_state == 2:
                self.pushbutton_savegrid.setEnabled(True)
            else:
                self.pushbutton_savegrid.setEnabled(False)

    def _setupUi(self):
        self.cameraview_widget = QWidget()
        self.cameraview_widget.setLayout(self._cameraviewLayout())
        self.layout().addWidget(self.cameraview_widget, 1, 1, 1, 3)

        self.camerasettings_groupBox = QGroupBox('Camera Settings', self)
        self.camerasettings_groupBox.setLayout(self._camerasettingsLayout())
        self.layout().addWidget(self.camerasettings_groupBox, 2, 1)

        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 1)

        self.calibrationgrid_groupBox = QGroupBox('Screen Calibration', self)
        self.calibrationgrid_groupBox.setLayout(self._calibrationgridLayout())
        self.calibrationgrid_groupBox.layout().setAlignment(Qt.AlignHCenter)
        self.layout().addWidget(self.calibrationgrid_groupBox, 4, 1)

        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 2, 2)

        self.statistics_groupBox = QGroupBox('Statistics', self)
        self.statistics_groupBox.setLayout(self._statisticsLayout())
        self.layout().addWidget(self.statistics_groupBox, 2, 3)

        self.imagesettings_groupBox = QGroupBox('Image Settings', self)
        self.imagesettings_groupBox.setLayout(self._imagesettingsLayout())
        self.layout().addWidget(self.imagesettings_groupBox, 4, 3)

    def _cameraviewLayout(self):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)
        self.device_label = QLabel(self.device)
        self.device_label.setVisible(False)
        layout.addWidget(self.device_label, 2, 1)
        self.image_view = _SiriusImageView(
            parent=self,
            image_channel='ca://'+self.prefix+self.device+':ImgData-Mon',
            width_channel='ca://'+self.prefix+self.device+':ImgROIWidth-RB')
        self.image_view.normalizeData = True
        self.image_view.readingOrder = self.image_view.Clike
        self.image_view.maxRedrawRate = 20
        self.image_view.setMinimumSize(800, 640)
        layout.addWidget(self.image_view, 3, 1)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 4, 1)
        return layout

    def _camerasettingsLayout(self):
        layout = QGridLayout()
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 2, 1)

        self.label = QLabel('CamGain', self)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label, 3, 1, 1, 2)
        self.PyDMLineEdit_CamGain = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CamGain-SP')
        self.PyDMLineEdit_CamGain.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLineEdit_CamGain, 4, 1)
        self.PyDMLabel_CamGain = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CamGain-RB')
        self.PyDMLabel_CamGain.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLabel_CamGain, 4, 2)

        self.label = QLabel('ROI Width', self)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label, 5, 1, 1, 2)
        self.PyDMLineEdit_ROIWidth = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIWidth-SP')
        self.PyDMLineEdit_ROIWidth.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLineEdit_ROIWidth, 6, 1)
        self.PyDMLabel_ROIWidth = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIWidth-RB')
        self.PyDMLabel_ROIWidth.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLabel_ROIWidth, 6, 2)

        self.label = QLabel('ROI Heigth', self)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label, 7, 1, 1, 2)
        self.PyDMLineEdit_ROIHeight = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIHeight-SP')
        self.PyDMLineEdit_ROIHeight.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLineEdit_ROIHeight, 8, 1)
        self.PyDMLabel_ROIHeight = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIHeight-RB')
        self.PyDMLabel_ROIHeight.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLabel_ROIHeight, 8, 2)

        self.label = QLabel('ROI Offset X', self)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label, 9, 1, 1, 2)
        self.PyDMLineEdit_ROIOffsetX = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIOffsetX-SP')
        self.PyDMLineEdit_ROIOffsetX.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLineEdit_ROIOffsetX, 10, 1)
        self.PyDMLabel_ROIOffsetX = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIOffsetX-RB')
        self.PyDMLabel_ROIOffsetX.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLabel_ROIOffsetX, 10, 2)

        self.label = QLabel('ROI Offset Y', self)
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label, 11, 1, 1, 2)
        self.PyDMLineEdit_ROIOffsetY = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIOffsetY-SP')
        self.PyDMLineEdit_ROIOffsetY.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLineEdit_ROIOffsetY, 12, 1)
        self.PyDMLabel_ROIOffsetY = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIOffsetY-RB')
        self.PyDMLabel_ROIOffsetY.setMaximumSize(140, 40)
        layout.addWidget(self.PyDMLabel_ROIOffsetY, 12, 2)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 13, 1)
        return layout

    def _calibrationgridLayout(self):
        layout = QGridLayout()
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)
        self.checkBox_showgrid = QCheckBox('Show grid', self)
        self.checkBox_showgrid.toggled.connect(
            self.image_view.showCalibrationGrid)
        layout.addWidget(self.checkBox_showgrid, 2, 1)
        self.pushbutton_savegrid = QPushButton(
            'Save current \n calibration grid', self)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 1)
        self.pushbutton_savegrid.setEnabled(False)
        self.pushbutton_savegrid.clicked.connect(self._saveCalibrationGrid)
        layout.addWidget(self.pushbutton_savegrid, 4, 1)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 5, 1)
        return layout

    def _statisticsLayout(self):
        layout = QGridLayout()
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)

        # - Method
        self.label_Method = QLabel('CalcMethod', self)
        self.label_Method.setMaximumHeight(40)
        layout.addWidget(self.label_Method, 2, 1, 1, 5)

        self.comboBox_Method = QComboBox(self)
        self.comboBox_Method.addItem('DimFei', 0)
        self.comboBox_Method.addItem('NDStats', 1)
        self.comboBox_Method.setCurrentIndex(0)
        self.comboBox_Method.currentIndexChanged.connect(
            self._handleShowStatistics)
        layout.addWidget(self.comboBox_Method, 3, 1, 1, 5)

        # - Centroid
        self.label_Centroid = QLabel('Centroid', self)
        self.label_Centroid.setMaximumHeight(40)
        layout.addWidget(self.label_Centroid, 4, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 5, 1)

        self.PyDMLabel_CenterXDimFei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterXDimFei-Mon')
        self.PyDMLabel_CenterXDimFei.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.PyDMLabel_CenterXDimFei, 5, 2)

        self.PyDMLabel_CenterXNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterXNDStats-Mon')
        self.PyDMLabel_CenterXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterXNDStats.setVisible(False)
        layout.addWidget(self.PyDMLabel_CenterXNDStats, 5, 2)

        self.label = QLabel(',', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 5, 3)

        self.PyDMLabel_CenterYDimFei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterYDimFei-Mon')
        self.PyDMLabel_CenterYDimFei.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.PyDMLabel_CenterYDimFei, 5, 4)

        self.PyDMLabel_CenterYNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterYNDStats-Mon')
        self.PyDMLabel_CenterYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterYNDStats.setVisible(False)
        layout.addWidget(self.PyDMLabel_CenterYNDStats, 5, 4)

        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 5, 5)

        # - Sigma
        self.label_Sigma = QLabel('Sigma', self)
        self.label_Sigma.setMaximumHeight(40)
        layout.addWidget(self.label_Sigma, 6, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 7, 1)

        self.PyDMLabel_SigmaXDimFei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaXDimFei-Mon')
        self.PyDMLabel_SigmaXDimFei.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.PyDMLabel_SigmaXDimFei, 7, 2)

        self.PyDMLabel_SigmaXNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaXNDStats-Mon')
        self.PyDMLabel_SigmaXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaXNDStats.setVisible(False)
        layout.addWidget(self.PyDMLabel_SigmaXNDStats, 7, 2)

        self.label = QLabel(',', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 7, 3)
        self.PyDMLabel_SigmaYDimFei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaYDimFei-Mon')
        self.PyDMLabel_SigmaYDimFei.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.PyDMLabel_SigmaYDimFei, 7, 4)
        self.PyDMLabel_SigmaYNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaYNDStats-Mon')
        self.PyDMLabel_SigmaYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaYNDStats.setVisible(False)
        layout.addWidget(self.PyDMLabel_SigmaYNDStats, 7, 4)

        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 7, 5)

        # - Theta
        self.label_Theta = QLabel('Theta', self)
        self.label_Theta.setMaximumHeight(40)
        layout.addWidget(self.label_Theta, 8, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 9, 1)
        self.PyDMLabel_ThetaDimFei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ThetaDimFei-Mon')
        self.PyDMLabel_ThetaDimFei.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.PyDMLabel_ThetaDimFei, 9, 2, 1, 3)
        self.PyDMLabel_ThetaNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ThetaNDStats-Mon')
        self.PyDMLabel_ThetaNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_ThetaNDStats.setVisible(False)
        layout.addWidget(self.PyDMLabel_ThetaNDStats, 9, 2, 1, 3)
        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        layout.addWidget(self.label, 9, 5)

        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 10, 1)
        return layout

    def _imagesettingsLayout(self):
        layout = QVBoxLayout()
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.PyDMPushButton_zoomIn = QPushButton('Zoom In', self)
        self.PyDMPushButton_zoomIn.clicked.connect(self._zoomIn)
        layout.addWidget(self.PyDMPushButton_zoomIn)
        self.PyDMPushButton_zoomOut = QPushButton('Zoom Out', self)
        self.PyDMPushButton_zoomOut.clicked.connect(self._zoomOut)
        layout.addWidget(self.PyDMPushButton_zoomOut)
        self.PyDMPushButton_zoomActualSize = QPushButton(
            'Zoom To Actual Size', self)
        self.PyDMPushButton_zoomActualSize.clicked.connect(
            self._zoomToActualSize)
        layout.addWidget(self.PyDMPushButton_zoomActualSize)
        layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        return layout

    def _handleShowStatistics(self, visible):
        self.PyDMLabel_CenterXDimFei.setVisible(not visible)
        self.PyDMLabel_CenterXNDStats.setVisible(visible)
        self.PyDMLabel_CenterYDimFei.setVisible(not visible)
        self.PyDMLabel_CenterYNDStats.setVisible(visible)
        self.PyDMLabel_ThetaDimFei.setVisible(not visible)
        self.PyDMLabel_ThetaNDStats.setVisible(visible)
        self.PyDMLabel_SigmaXDimFei.setVisible(not visible)
        self.PyDMLabel_SigmaXNDStats.setVisible(visible)
        self.PyDMLabel_SigmaYDimFei.setVisible(not visible)
        self.PyDMLabel_SigmaYNDStats.setVisible(visible)

    def _saveCalibrationGrid(self):
        roi_h = epics.caget(self.prefix+self.device+':ImgROIHeight-RB')
        roi_w = epics.caget(self.prefix+self.device+':ImgROIWidth-RB')

        epics.caput(self.prefix+self.device+':ImgROIHeight-SP',
                    IMAGE_MAX_HEIGHT)
        epics.caput(self.prefix+self.device+':ImgROIWidth-SP',
                    IMAGE_MAX_WIDTH)
        # print('max size')
        time.sleep(1)
        # print('will save')
        img = epics.caget(self.prefix+self.device+':ImgData-Mon')
        self.image_view.saveCalibrationGrid(img, IMAGE_MAX_WIDTH)
        # print('saved')
        time.sleep(1)
        # print('will return size')
        epics.caput(self.prefix+self.device+':ImgROIHeight-SP', roi_h)
        epics.caput(self.prefix+self.device+':ImgROIWidth-SP', roi_w)
        # w = self.PyDMLabel_ROIWidth.text()
        # h = self.PyDMLabel_ROIHeight.text()
        # self.PyDMLineEdit_ROIWidth.setText(str(IMAGE_MAX_WIDTH))
        # self.PyDMLineEdit_ROIWidth.send_value()
        # self.PyDMLineEdit_ROIHeight.setText(str(IMAGE_MAX_HEIGHT))
        # self.PyDMLineEdit_ROIHeight.send_value()
        # print('max size')
        # time.sleep(3)
        # print('will save')
        # self.image_view.saveCalibrationGrid()
        # print('saved')
        # time.sleep(3)
        # print('will return size')
        # self.PyDMLineEdit_ROIWidth.setText(w)
        # self.PyDMLineEdit_ROIWidth.send_value()
        # self.PyDMLineEdit_ROIHeight.setText(h)
        # self.PyDMLineEdit_ROIHeight.send_value()

    @pyqtSlot()
    def _zoomIn(self):
        """Zoom ImageView to 0.5x current image scale."""
        self.image_view.getView().scaleBy((0.5, 0.5))

    @pyqtSlot()
    def _zoomOut(self):
        """Zoom ImageView to 2x current image scale."""
        self.image_view.getView().scaleBy((2.0, 2.0))

    @pyqtSlot()
    def _zoomToActualSize(self):
        """Zoom ImqgeView to actual image size."""
        if len(self.image_view.image_waveform) == 0:
            return
        self.image_view.getView().setRange(
            xRange=(0, self.image_view.imageWidth),
            yRange=(0, self.image_view.image_waveform.shape[0] /
                    self.image_view.imageWidth))
