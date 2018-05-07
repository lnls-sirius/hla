"""SiriusScrnView widget."""

import numpy as np
from pydm.PyQt.QtGui import (QWidget, QLabel, QGridLayout,
                             QSpacerItem, QGroupBox, QComboBox, QPushButton,
                             QCheckBox)
from pydm.PyQt.QtGui import QSizePolicy as QSzPlcy
from pydm.PyQt.QtCore import Qt, pyqtSlot
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMLineEdit
from siriuspy.envars import vaca_prefix as _vaca_prefix


class _SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    def __init__(self, parent=None, image_channel=None, width_channel=None):
        """Initialize the object."""
        PyDMImageView.__init__(self, parent=parent,
                               image_channel=image_channel,
                               width_channel=width_channel)
        self._calibration_grid_image = None
        self._show_calibration_grid = False

    @pyqtSlot()
    def saveCalibrationGrid(self):
        """Save current image as calibration_grid_image."""
        img = self.image_waveform
        self._calibration_grid_image = np.where(img < 0.5, True, False)

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
        if image_dimensions == 1:
            if self.imageWidth < 1:
                # We don't have a width for this image yet,
                # so we can't draw it
                return
            try:
                img = self.image_waveform.reshape(
                    self.imageWidth, -1,
                    order=self.reading_orders[self._reading_order])
            except Exception:
                print('Width does not match the image_waveform shape.')
        else:
            img = self.image_waveform

        if len(img) <= 0:
            return
        if (self._show_calibration_grid and
                self._calibration_grid_image is not None):
            try:
                grid = self._calibration_grid_image.reshape(
                    self.imageWidth, -1,
                    order=self.reading_orders[self._reading_order])
                img[grid] = img.max()
            except Exception:
                print('Image dimensions does not match grid dimensions.')
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
        # Camera View Widget
        self.cameraview_widget = QWidget()
        self.cameraview_layout = QGridLayout()
        self.cameraview_layout.setContentsMargins(0, 0, 0, 0)
        self.cameraview_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)
        self.device_label = QLabel(self.device)
        self.device_label.setVisible(False)
        self.cameraview_layout.addWidget(self.device_label, 2, 1)
        self.image_view = _SiriusImageView(
            parent=self,
            image_channel='ca://'+self.prefix+self.device+':ImgData-Mon',
            width_channel='ca://'+self.prefix+self.device+':ImgROIWidth-RB')
        self.image_view.normalizeData = True
        self.image_view.readingOrder = self.image_view.Clike
        self.image_view.setMinimumSize(800, 640)
        self.cameraview_layout.addWidget(self.image_view, 3, 1)
        self.cameraview_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 4, 1)
        self.cameraview_widget.setLayout(self.cameraview_layout)
        self.layout().addWidget(self.cameraview_widget, 1, 1, 1, 3)

        # Camera Settings
        self.camerasettings_groupox = QGroupBox('Camera Settings', self)
        self.camerasettings_layout = QGridLayout()
        self.camerasettings_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 2, 1)
        self.label = QLabel('CamGain', self)
        self.label.setAlignment(Qt.AlignHCenter)
        self.camerasettings_layout.addWidget(self.label, 3, 1, 1, 2)
        self.PyDMLineEdit_CamGain = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CamGain-SP')
        self.PyDMLineEdit_CamGain.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLineEdit_CamGain, 4, 1)
        self.PyDMLabel_CamGain = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CamGain-RB')
        self.PyDMLabel_CamGain.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLabel_CamGain, 4, 2)
        self.label = QLabel('ROI Heigth', self)
        self.label.setAlignment(Qt.AlignHCenter)
        self.camerasettings_layout.addWidget(self.label, 5, 1, 1, 2)
        self.PyDMLineEdit_ROIHeight = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIHeight-SP')
        self.PyDMLineEdit_ROIHeight.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLineEdit_ROIHeight, 6, 1)
        self.PyDMLabel_ROIHeight = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIHeight-RB')
        self.PyDMLabel_ROIHeight.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLabel_ROIHeight, 6, 2)
        self.label = QLabel('ROI Width', self)
        self.label.setAlignment(Qt.AlignHCenter)
        self.camerasettings_layout.addWidget(self.label, 7, 1, 1, 2)
        self.PyDMLineEdit_ROIWidth = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIWidth-SP')
        self.PyDMLineEdit_ROIWidth.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLineEdit_ROIWidth, 8, 1)
        self.PyDMLabel_ROIWidth = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ImgROIWidth-RB')
        self.PyDMLabel_ROIWidth.setMaximumSize(140, 40)
        self.camerasettings_layout.addWidget(self.PyDMLabel_ROIWidth, 8, 2)
        self.camerasettings_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 9, 1)
        self.camerasettings_groupox.setLayout(self.camerasettings_layout)
        self.layout().addWidget(self.camerasettings_groupox, 2, 1)

        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 1)

        # Calibration Grid Widget
        self.calibrationgrid_groupox = QGroupBox('Screen Calibration', self)
        self.calibrationgrid_layout = QGridLayout()
        self.calibrationgrid_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)
        self.checkBox_showgrid = QCheckBox('Show grid', self)
        self.checkBox_showgrid.toggled.connect(
            self.image_view.showCalibrationGrid)
        self.calibrationgrid_layout.addWidget(self.checkBox_showgrid, 2, 1)
        self.pushbutton_savegrid = QPushButton(
            'Save current \n calibration grid', self)
        self.calibrationgrid_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 1)
        self.pushbutton_savegrid.clicked.connect(
            self.image_view.saveCalibrationGrid)
        self.pushbutton_savegrid.setEnabled(False)
        self.calibrationgrid_layout.addWidget(self.pushbutton_savegrid, 4, 1)
        self.calibrationgrid_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 5, 1)
        self.calibrationgrid_groupox.setLayout(self.calibrationgrid_layout)
        self.calibrationgrid_layout.setAlignment(Qt.AlignHCenter)
        self.layout().addWidget(self.calibrationgrid_groupox, 4, 1)

        # Statistics Widget
        self.statistics_groupox = QGroupBox('Statistics', self)
        self.statistics_layout = QGridLayout()
        self.statistics_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 1)

        # - Method
        self.label_Method = QLabel('CalcMethod', self)
        self.label_Method.setMaximumHeight(40)
        self.statistics_layout.addWidget(self.label_Method, 2, 1, 1, 5)

        self.comboBox_Method = QComboBox(self)
        self.comboBox_Method.addItem('Dimfei', 0)
        self.comboBox_Method.addItem('NDStats', 1)
        self.comboBox_Method.setCurrentIndex(0)
        self.comboBox_Method.currentIndexChanged.connect(
            self._handleShowStatistics)
        self.statistics_layout.addWidget(self.comboBox_Method, 3, 1, 1, 5)

        # - Centroid
        self.label_Centroid = QLabel('Centroid', self)
        self.label_Centroid.setMaximumHeight(40)
        self.statistics_layout.addWidget(self.label_Centroid, 4, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 5, 1)

        self.PyDMLabel_CenterXDimfei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterXDimfei-Mon')
        self.PyDMLabel_CenterXDimfei.setAlignment(Qt.AlignHCenter)
        self.statistics_layout.addWidget(self.PyDMLabel_CenterXDimfei, 5, 2)

        self.PyDMLabel_CenterXNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterXNDStats-Mon')
        self.PyDMLabel_CenterXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterXNDStats.setVisible(False)
        self.statistics_layout.addWidget(self.PyDMLabel_CenterXNDStats, 5, 2)

        self.label = QLabel(',', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 5, 3)

        self.PyDMLabel_CenterYDimfei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterYDimfei-Mon')
        self.PyDMLabel_CenterYDimfei.setAlignment(Qt.AlignHCenter)
        self.statistics_layout.addWidget(self.PyDMLabel_CenterYDimfei, 5, 4)

        self.PyDMLabel_CenterYNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':CenterYNDStats-Mon')
        self.PyDMLabel_CenterYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterYNDStats.setVisible(False)
        self.statistics_layout.addWidget(self.PyDMLabel_CenterYNDStats, 5, 4)

        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 5, 5)

        # - Sigma
        self.label_Sigma = QLabel('Sigma', self)
        self.label_Sigma.setMaximumHeight(40)
        self.statistics_layout.addWidget(self.label_Sigma, 6, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 7, 1)

        self.PyDMLabel_SigmaXDimfei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaXDimfei-Mon')
        self.PyDMLabel_SigmaXDimfei.setAlignment(Qt.AlignHCenter)
        self.statistics_layout.addWidget(self.PyDMLabel_SigmaXDimfei, 7, 2)

        self.PyDMLabel_SigmaXNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaXNDStats-Mon')
        self.PyDMLabel_SigmaXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaXNDStats.setVisible(False)
        self.statistics_layout.addWidget(self.PyDMLabel_SigmaXNDStats, 7, 2)

        self.label = QLabel(',', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 7, 3)
        self.PyDMLabel_SigmaYDimfei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaYDimfei-Mon')
        self.PyDMLabel_SigmaYDimfei.setAlignment(Qt.AlignHCenter)

        self.statistics_layout.addWidget(self.PyDMLabel_SigmaYDimfei, 7, 4)
        self.PyDMLabel_SigmaYNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':SigmaYNDStats-Mon')
        self.PyDMLabel_SigmaYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaYNDStats.setVisible(False)
        self.statistics_layout.addWidget(self.PyDMLabel_SigmaYNDStats, 7, 4)

        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 7, 5)

        # - Theta
        self.label_Theta = QLabel('Theta', self)
        self.label_Theta.setMaximumHeight(40)
        self.statistics_layout.addWidget(self.label_Theta, 8, 1, 1, 5)
        self.label = QLabel('(', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 9, 1)
        self.PyDMLabel_ThetaDimfei = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ThetaDimfei-Mon')
        self.PyDMLabel_ThetaDimfei.setAlignment(Qt.AlignHCenter)
        self.statistics_layout.addWidget(self.PyDMLabel_ThetaDimfei,
                                         9, 2, 1, 3)
        self.PyDMLabel_ThetaNDStats = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+self.device+':ThetaNDStats-Mon')
        self.PyDMLabel_ThetaNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_ThetaNDStats.setVisible(False)
        self.statistics_layout.addWidget(self.PyDMLabel_ThetaNDStats,
                                         9, 2, 1, 3)
        self.label = QLabel(')', self)
        self.label.setMaximumSize(10, 40)
        self.statistics_layout.addWidget(self.label, 9, 5)

        self.statistics_layout.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 10, 1)

        self.statistics_groupox.setLayout(self.statistics_layout)
        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 2, 2)
        self.layout().addWidget(self.statistics_groupox, 2, 3, 3, 1)

    def _handleShowStatistics(self, visible):
        self.PyDMLabel_CenterXDimfei.setVisible(not visible)
        self.PyDMLabel_CenterXNDStats.setVisible(visible)
        self.PyDMLabel_CenterYDimfei.setVisible(not visible)
        self.PyDMLabel_CenterYNDStats.setVisible(visible)
        self.PyDMLabel_ThetaDimfei.setVisible(not visible)
        self.PyDMLabel_ThetaNDStats.setVisible(visible)
        self.PyDMLabel_SigmaXDimfei.setVisible(not visible)
        self.PyDMLabel_SigmaXNDStats.setVisible(visible)
        self.PyDMLabel_SigmaYDimfei.setVisible(not visible)
        self.PyDMLabel_SigmaYNDStats.setVisible(visible)
