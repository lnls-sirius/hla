"""SiriusScrnView widget."""

import sys
import time
from threading import Thread
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QFormLayout, \
                            QSpacerItem, QWidget, QGroupBox, QLabel, \
                            QComboBox, QPushButton, QCheckBox, QMessageBox, \
                            QSizePolicy as QSzPlcy
from qtpy.QtCore import Qt, Slot, Signal, Property
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMSpinbox, \
                            PyDMPushButton, PyDMEnumComboBox
from pydm.widgets.channel import PyDMChannel
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import PyDMStateButton, SiriusLedState
from siriushla.widgets.windows import SiriusMainWindow


class _SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    failToSaveGrid = Signal()

    def __init__(self, parent=None,
                 image_channel=None, width_channel=None,
                 offsetx_channel=None, offsety_channel=None,
                 maxwidth_channel=None, maxheight_channel=None):
        """Initialize the object."""
        PyDMImageView.__init__(self, parent=parent,
                               image_channel=image_channel,
                               width_channel=width_channel)
        self._calibration_grid_image = None
        self._calibration_grid_maxdata = None
        self._calibration_grid_width = None
        self._image_roi_offsetx = 0
        self._offsetxchannel = offsetx_channel
        self._image_roi_offsety = 0
        self._offsetychannel = offsety_channel
        self._image_maxwidth = 0
        self._maxwidthchannel = maxwidth_channel
        self._image_maxheight = 0
        self._maxheightchannel = maxheight_channel
        self._show_calibration_grid = False

    @Slot()
    def saveCalibrationGrid(self):
        """Save current image as calibration_grid_image."""
        for i in range(40):
            if self.image_waveform.size == (
                    self.image_maxwidth*self.image_maxheight):
                img = self.image_waveform.copy()
                self._calibration_grid_width = self.imageWidth
                self._calibration_grid_maxdata = img.max()
                grid = np.where(img < 0.5*self._calibration_grid_maxdata,
                                True, False)
                if self.readingOrder == self.ReadingOrder.Clike:
                    self._calibration_grid_image = grid.reshape(
                        (-1, self._calibration_grid_width), order='C')
                else:
                    self._calibration_grid_image = grid.reshape(
                        (self._calibration_grid_width, -1), order='F')
                break
            time.sleep(0.05)
        else:
            self.failToSaveGrid.emit()

    @Slot(bool)
    def showCalibrationGrid(self, show):
        """Show calibration_grid_image over the current image_waveform."""
        self._show_calibration_grid = show

    def process_image(self, image):
        """Reimplement process_image method to add grid to image."""
        if ((self._show_calibration_grid) and
                (self._calibration_grid_image is not None)):
            try:
                grid = self._adjust_calibration_grid(image)
                image[grid] = self._calibration_grid_maxdata
            except Exception:
                print('Grid dimentions do not match image dimentions!')
        return image

    def _adjust_calibration_grid(self, img):
        height = np.size(img, 0)
        width = np.size(img, 1)
        grid = self._calibration_grid_image[
            self._image_roi_offsety:(self._image_roi_offsety+height),
            self._image_roi_offsetx:(self._image_roi_offsetx+width)]
        return grid

    def roioffsetx_connection_state_changed(self, conn):
        """
        Callback invoked when the ROIOffsetX Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.
        """
        if not conn:
            self._image_roi_offsetx = 0

    def roioffsety_connection_state_changed(self, conn):
        """
        Callback invoked when the ROIOffsetY Channel connection state changes.

        Parameters
        ----------
        conn : bool
            The new connection state.
        """
        if not conn:
            self._image_roi_offsety = 0

    def image_roioffsetx_changed(self, new_offset):
        """
        Callback invoked when the ROIOffsetX Channel value changes.

        Parameters
        ----------
        new_offsetx : int
            The new image ROI horizontal offset
        """
        if new_offset is None:
            return
        self._image_roi_offsetx = new_offset

    def image_roioffsety_changed(self, new_offset):
        """
        Callback invoked when the ROIOffsetY Channel value changes.

        Parameters
        ----------
        new_offsety : int
            The new image ROI vertical offset
        """
        if new_offset is None:
            return
        self._image_roi_offsety = new_offset

    @property
    def image_maxwidth(self):
        return self._image_maxwidth

    def image_maxwidth_changed(self, new_max):
        """
        Callback invoked when the maxWidth Channel value changes.

        Parameters
        ----------
        new_max : int
            The new image max width
        """
        if new_max is None:
            return
        self._image_maxwidth = new_max

    @property
    def image_maxheight(self):
        return self._image_maxheight

    def image_maxheight_changed(self, new_max):
        """
        Callback invoked when the maxHeight Channel value changes.

        Parameters
        ----------
        new_max : int
            The new image max height
        """
        if new_max is None:
            return
        self._image_maxheight = new_max

    @Property(str)
    def ROIOffsetXChannel(self):
        """
        The channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address
        """
        return str(self._offsetxchannel)

    @ROIOffsetXChannel.setter
    def ROIOffsetXChannel(self, value):
        """
        The channel address in use for the image ROI horizontal offset.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._offsetxchannel != value:
            self._offsetxchannel = str(value)

    @Property(str)
    def ROIOffsetYChannel(self):
        """
        The channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address
        """
        return str(self._offsetychannel)

    @ROIOffsetYChannel.setter
    def ROIOffsetYChannel(self, value):
        """
        The channel address in use for the image ROI vertical offset.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._offsetychannel != value:
            self._offsetychannel = str(value)

    @Property(str)
    def maxWidthChannel(self):
        """
        The channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address
        """
        return str(self._maxwidthchannel)

    @maxWidthChannel.setter
    def maxWidthChannel(self, value):
        """
        The channel address in use for the image ROI horizontal offset.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._maxwidthchannel != value:
            self._maxwidthchannel = str(value)

    @Property(str)
    def maxHeightChannel(self):
        """
        The channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address
        """
        return str(self._maxheightchannel)

    @maxHeightChannel.setter
    def maxHeightChannel(self, value):
        """
        The channel address in use for the image ROI vertical offset.

        Parameters
        ----------
        value : str
            Channel address
        """
        if self._maxheightchannel != value:
            self._maxheightchannel = str(value)

    def channels(self):
        """
        Return the channels being used for this Widget.

        Returns
        -------
        channels : list
            List of PyDMChannel objects
        """
        if self._channels is None:
            self._channels = [
                PyDMChannel(
                    address=self.imageChannel,
                    connection_slot=self.image_connection_state_changed,
                    value_slot=self.image_value_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.widthChannel,
                    connection_slot=self.connectionStateChanged,
                    value_slot=self.image_width_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.ROIOffsetXChannel,
                    connection_slot=self.roioffsetx_connection_state_changed,
                    value_slot=self.image_roioffsetx_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.ROIOffsetYChannel,
                    connection_slot=self.roioffsety_connection_state_changed,
                    value_slot=self.image_roioffsety_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.maxWidthChannel,
                    value_slot=self.image_maxwidth_changed,
                    severity_slot=self.alarmSeverityChanged),
                PyDMChannel(
                    address=self.maxHeightChannel,
                    value_slot=self.image_maxheight_changed,
                    severity_slot=self.alarmSeverityChanged)]
        return self._channels


class SiriusScrnView(QWidget):
    """
    Class to read Sirius screen cameras image data.

    To allow saving a grid correctly, control calibrationgrid_flag, which
    indicates if the screen is in calibration grid position.
    You can control it by using the method/Slot updateCalibrationGridFlag.
    """

    def __init__(self, parent=None, prefix='', device=None):
        """Initialize object."""
        QWidget.__init__(self, parent=parent)
        if prefix == '':
            self.prefix = _vaca_prefix
        else:
            self.prefix = prefix
        self.device = device
        self.scrn_prefix = 'ca://'+self.prefix+self.device
        self._calibrationgrid_flag = False
        self._setupUi()

    @property
    def calibrationgrid_flag(self):
        """Indicate if the screen device is in calibration grid position."""
        return self._calibrationgrid_flag

    @Slot(int)
    def updateCalibrationGridFlag(self, new_state):
        """Update calibrationgrid_flag property."""
        if new_state != self._calibrationgrid_flag:
            self._calibrationgrid_flag = new_state

            if new_state == 1:
                self.pushbutton_savegrid.setEnabled(True)
            else:
                self.pushbutton_savegrid.setEnabled(False)

    def _setupUi(self):
        self.setLayout(QGridLayout())

        self.cameraview_widget = QWidget()
        self.cameraview_widget.setLayout(self._cameraviewLayout())
        self.layout().addWidget(self.cameraview_widget, 1, 1, 1, 3)

        container = QWidget()
        layout_container = QHBoxLayout()
        self.calibrationgrid_widget = QWidget()
        self.calibrationgrid_widget.setLayout(self._calibrationgridLayout())
        self.calibrationgrid_widget.layout().setAlignment(Qt.AlignHCenter)
        self.enablecam_widget = QWidget()
        self.enablecam_widget.setLayout(self._enablecamLayout())
        layout_container.addWidget(self.calibrationgrid_widget)
        layout_container.setStretch(1, 2)
        layout_container.addWidget(self.enablecam_widget)
        layout_container.setStretch(2, 1)
        container.setLayout(layout_container)
        self.layout().addWidget(container, 2, 1, 1, 3)

        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 3, 1)

        self.camerasettings_groupBox = QGroupBox('Camera Settings', self)
        self.camerasettings_groupBox.setLayout(self._camerasettingsLayout())
        self.layout().addWidget(self.camerasettings_groupBox, 4, 1)

        self.layout().addItem(
            QSpacerItem(60, 20, QSzPlcy.Fixed, QSzPlcy.Minimum), 4, 2)

        self.statistics_groupBox = QGroupBox('Statistics', self)
        self.statistics_groupBox.setLayout(self._statisticsLayout())
        self.layout().addWidget(self.statistics_groupBox, 4, 3)

        self.layout().addItem(
            QSpacerItem(60, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 5, 2)

        self.pb_openDetails = QPushButton('Open details...', self)
        self.pb_openDetails.setMaximumWidth(220)
        hlay_openDetails = QHBoxLayout()
        hlay_openDetails.addItem(
            QSpacerItem(60, 20, QSzPlcy.Expanding, QSzPlcy.Fixed))
        hlay_openDetails.addWidget(self.pb_openDetails)
        self.layout().addLayout(hlay_openDetails, 6, 3)
        util.connect_window(self.pb_openDetails, _ScrnSettingsDetails,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        self.layout().addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 7, 2)

    def _cameraviewLayout(self):
        label = QLabel(self.device, self)
        label.setStyleSheet("""font-weight: bold;""")
        label.setAlignment(Qt.AlignCenter)
        self.image_view = _SiriusImageView(
            parent=self,
            image_channel=self.scrn_prefix+':ImgData-Mon',
            width_channel=self.scrn_prefix+':ImgROIWidth-RB',
            offsetx_channel=self.scrn_prefix+':ImgROIOffsetX-RB',
            offsety_channel=self.scrn_prefix+':ImgROIOffsetY-RB',
            maxwidth_channel=self.scrn_prefix+':ImgMaxWidth-Cte',
            maxheight_channel=self.scrn_prefix+':ImgMaxHeight-Cte')
        self.image_view.normalizeData = True
        self.image_view.readingOrder = self.image_view.Clike
        self.image_view.maxRedrawRate = 15
        self.image_view.setMinimumSize(920, 736)
        self.image_view.failToSaveGrid.connect(self._showFailToSaveGridMsg)

        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(label, 0, 1)
        lay.addItem(QSpacerItem(40, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 1, 1)
        lay.addWidget(self.image_view, 2, 1)
        return lay

    def _calibrationgridLayout(self):
        self.checkBox_showgrid = QCheckBox('Show grid', self)
        self.checkBox_showgrid.toggled.connect(
            self.image_view.showCalibrationGrid)
        self.pushbutton_savegrid = QPushButton('Save grid', self)
        self.pushbutton_savegrid.setEnabled(False)
        self.pushbutton_savegrid.setMinimumHeight(40)
        self.pushbutton_savegrid.clicked.connect(self._saveCalibrationGrid)
        label = QLabel('LED: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.PyDMStateButton_EnblLED = PyDMStateButton(
            parent=self, init_channel=self.scrn_prefix+':EnblLED-Sel')
        self.PyDMStateButton_EnblLED.shape = 1
        self.PyDMStateButton_EnblLED.setMaximumHeight(40)
        self.PyDMStateButton_EnblLED.setSizePolicy(
            QSzPlcy.Fixed, QSzPlcy.Maximum)
        self.SiriusLedState_EnblLED = SiriusLedState(
            parent=self, init_channel=self.scrn_prefix+':EnblLED-Sts')
        self.SiriusLedState_EnblLED.setFixedSize(40, 40)
        self.SiriusLedState_EnblLED.setSizePolicy(
            QSzPlcy.Minimum, QSzPlcy.Maximum)

        lay = QHBoxLayout()
        lay.addWidget(self.checkBox_showgrid)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        lay.addWidget(self.pushbutton_savegrid)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        lay.addWidget(label)
        lay.addWidget(self.PyDMStateButton_EnblLED)
        lay.addWidget(self.SiriusLedState_EnblLED)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        lay.setAlignment(Qt.AlignVCenter)
        return lay

    def _enablecamLayout(self):
        label = QLabel('CamEnbl: ', self,
                       alignment=Qt.AlignRight | Qt.AlignBottom)
        self.PyDMStateButton_CamEnbl = PyDMStateButton(
            parent=self, init_channel=self.scrn_prefix+':CamEnbl-Sel')
        self.PyDMStateButton_CamEnbl.shape = 1
        self.PyDMStateButton_CamEnbl.setFixedHeight(40)
        self.SiriusLedState_CamEnbl = SiriusLedState(
            parent=self, init_channel=self.scrn_prefix+':CamEnbl-Sts')
        self.SiriusLedState_CamEnbl.setFixedHeight(40)

        lay = QHBoxLayout()
        lay.addWidget(label)
        lay.addWidget(self.PyDMStateButton_CamEnbl)
        lay.addWidget(self.SiriusLedState_CamEnbl)
        return lay

    def _camerasettingsLayout(self):
        label_CamGain = QLabel('Gain', self, alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_CamGain = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamGain-SP')
        self.PyDMSpinbox_CamGain.setMaximumSize(220, 40)
        self.PyDMSpinbox_CamGain.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_CamGain.showStepExponent = False
        self.PyDMLabel_CamGain = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamGain-RB')
        self.PyDMLabel_CamGain.setMaximumSize(220, 40)
        self.PyDMLabel_CamGain.setAlignment(Qt.AlignCenter)

        label_CamExposureTime = QLabel('Exposure Time', self,
                                       alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_CamExposureTime = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamExposureTime-SP')
        self.PyDMSpinbox_CamExposureTime.setMaximumSize(220, 40)
        self.PyDMSpinbox_CamExposureTime.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_CamExposureTime.showStepExponent = False
        self.PyDMLabel_CamExposureTime = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamExposureTime-RB')
        self.PyDMLabel_CamExposureTime.setMaximumSize(220, 40)
        self.PyDMLabel_CamExposureTime.setAlignment(Qt.AlignCenter)

        label_ROIOffsetX = QLabel('ROI Offset X', self,
                                  alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_ROIOffsetX = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetX-SP')
        self.PyDMSpinbox_ROIOffsetX.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIOffsetX.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIOffsetX.showStepExponent = False
        self.PyDMLabel_ROIOffsetX = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetX-RB')
        self.PyDMLabel_ROIOffsetX.setMaximumSize(220, 40)
        self.PyDMLabel_ROIOffsetX.setAlignment(Qt.AlignCenter)

        label_ROIOffsetY = QLabel('ROI Offset Y', self,
                                  alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_ROIOffsetY = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetY-SP')
        self.PyDMSpinbox_ROIOffsetY.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIOffsetY.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIOffsetY.showStepExponent = False
        self.PyDMLabel_ROIOffsetY = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetY-RB')
        self.PyDMLabel_ROIOffsetY.setMaximumSize(220, 40)
        self.PyDMLabel_ROIOffsetY.setAlignment(Qt.AlignCenter)

        label_ROIWidth = QLabel('ROI Width', self, alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_ROIWidth = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIWidth-SP')
        self.PyDMSpinbox_ROIWidth.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIWidth.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIWidth.showStepExponent = False
        self.PyDMLabel_ROIWidth = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIWidth-RB')
        self.PyDMLabel_ROIWidth.setMaximumSize(220, 40)
        self.PyDMLabel_ROIWidth.setAlignment(Qt.AlignCenter)

        label_ROIHeight = QLabel('ROI Heigth', self, alignment=Qt.AlignHCenter)
        self.PyDMSpinbox_ROIHeight = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIHeight-SP')
        self.PyDMSpinbox_ROIHeight.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIHeight.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIHeight.showStepExponent = False
        self.PyDMLabel_ROIHeight = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIHeight-RB')
        self.PyDMLabel_ROIHeight.setMaximumSize(220, 40)
        self.PyDMLabel_ROIHeight.setAlignment(Qt.AlignCenter)

        lay = QGridLayout()
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 2, 1)
        lay.addWidget(label_CamGain, 3, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_CamGain, 4, 1)
        lay.addWidget(self.PyDMLabel_CamGain, 4, 2)
        lay.addWidget(label_CamExposureTime, 5, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_CamExposureTime, 6, 1)
        lay.addWidget(self.PyDMLabel_CamExposureTime, 6, 2)
        lay.addWidget(label_ROIOffsetX, 7, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_ROIOffsetX, 8, 1)
        lay.addWidget(self.PyDMLabel_ROIOffsetX, 8, 2)
        lay.addWidget(label_ROIOffsetY, 9, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_ROIOffsetY, 10, 1)
        lay.addWidget(self.PyDMLabel_ROIOffsetY, 10, 2)
        lay.addWidget(label_ROIWidth, 11, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_ROIWidth, 12, 1)
        lay.addWidget(self.PyDMLabel_ROIWidth, 12, 2)
        lay.addWidget(label_ROIHeight, 13, 1, 1, 2)
        lay.addWidget(self.PyDMSpinbox_ROIHeight, 14, 1)
        lay.addWidget(self.PyDMLabel_ROIHeight, 14, 2)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 15, 1)
        return lay

    def _statisticsLayout(self):
        # - Method
        label_Method = QLabel('CalcMethod: ', self)
        label_Method.setMaximumHeight(40)

        self.comboBox_Method = QComboBox(self)
        self.comboBox_Method.addItem('DimFei', 0)
        self.comboBox_Method.addItem('NDStats', 1)
        self.comboBox_Method.setCurrentIndex(0)
        self.comboBox_Method.currentIndexChanged.connect(
            self._handleShowStatistics)

        # - Centroid
        label_Centroid = QLabel('Centroid', self, alignment=Qt.AlignHCenter)
        label_Centroid.setMaximumHeight(40)
        label_i_Center = QLabel('(', self)
        label_i_Center.setMaximumSize(10, 40)

        self.PyDMLabel_CenterXDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterXDimFei-Mon')
        self.PyDMLabel_CenterXDimFei.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterXDimFei.setMaximumSize(220, 40)
        self.PyDMLabel_CenterXNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterXNDStats-Mon')
        self.PyDMLabel_CenterXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterXNDStats.setMaximumSize(220, 40)
        self.PyDMLabel_CenterXNDStats.setVisible(False)

        label_m_Center = QLabel(',', self)
        label_m_Center.setMaximumSize(10, 40)

        self.PyDMLabel_CenterYDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterYDimFei-Mon')
        self.PyDMLabel_CenterYDimFei.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterYDimFei.setMaximumSize(220, 40)
        self.PyDMLabel_CenterYNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterYNDStats-Mon')
        self.PyDMLabel_CenterYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_CenterYNDStats.setMaximumSize(220, 40)
        self.PyDMLabel_CenterYNDStats.setVisible(False)

        label_f_Center = QLabel(')', self)
        label_f_Center.setMaximumSize(10, 40)

        # - Sigma
        label_Sigma = QLabel('Sigma', self, alignment=Qt.AlignHCenter)
        label_Sigma.setMaximumHeight(40)
        label_i_Sigma = QLabel('(', self)
        label_i_Sigma.setMaximumSize(10, 40)

        self.PyDMLabel_SigmaXDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaXDimFei-Mon')
        self.PyDMLabel_SigmaXDimFei.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaXDimFei.setMaximumSize(220, 40)
        self.PyDMLabel_SigmaXNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaXNDStats-Mon')
        self.PyDMLabel_SigmaXNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaXNDStats.setMaximumSize(220, 40)
        self.PyDMLabel_SigmaXNDStats.setVisible(False)

        label_m_Sigma = QLabel(',', self)
        label_m_Sigma.setMaximumSize(10, 40)
        self.PyDMLabel_SigmaYDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaYDimFei-Mon')
        self.PyDMLabel_SigmaYDimFei.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaYDimFei.setMaximumSize(220, 40)
        self.PyDMLabel_SigmaYNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaYNDStats-Mon')
        self.PyDMLabel_SigmaYNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_SigmaYNDStats.setMaximumSize(220, 40)
        self.PyDMLabel_SigmaYNDStats.setVisible(False)

        label_f_Sigma = QLabel(')', self)
        label_f_Sigma.setMaximumSize(10, 40)

        # - Theta
        label_Theta = QLabel('Theta', self, alignment=Qt.AlignHCenter)
        label_Theta.setMaximumHeight(40)
        label_i_Theta = QLabel('(', self)
        label_i_Theta.setMaximumSize(10, 40)

        self.PyDMLabel_ThetaDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaDimFei-Mon')
        self.PyDMLabel_ThetaDimFei.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_ThetaNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaNDStats-Mon')
        self.PyDMLabel_ThetaNDStats.setAlignment(Qt.AlignHCenter)
        self.PyDMLabel_ThetaNDStats.setVisible(False)

        label_f_Theta = QLabel(')', self)
        label_f_Theta.setMaximumSize(10, 40)

        lay = QGridLayout()
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 1, 2)
        lay.addWidget(label_Method, 2, 2)
        lay.addWidget(self.comboBox_Method, 2, 4)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 3, 2)
        lay.addWidget(label_Centroid, 4, 1, 1, 5)
        lay.addWidget(label_i_Center, 5, 1)
        lay.addWidget(self.PyDMLabel_CenterXDimFei, 5, 2)
        lay.addWidget(self.PyDMLabel_CenterXNDStats, 5, 2)
        lay.addWidget(label_m_Center, 5, 3)
        lay.addWidget(self.PyDMLabel_CenterYDimFei, 5, 4)
        lay.addWidget(self.PyDMLabel_CenterYNDStats, 5, 4)
        lay.addWidget(label_f_Center, 5, 5)
        lay.addWidget(label_Sigma, 6, 1, 1, 5)
        lay.addWidget(label_i_Sigma, 7, 1)
        lay.addWidget(self.PyDMLabel_SigmaXDimFei, 7, 2)
        lay.addWidget(self.PyDMLabel_SigmaXNDStats, 7, 2)
        lay.addWidget(label_m_Sigma, 7, 3)
        lay.addWidget(self.PyDMLabel_SigmaYDimFei, 7, 4)
        lay.addWidget(self.PyDMLabel_SigmaYNDStats, 7, 4)
        lay.addWidget(label_f_Sigma, 7, 5)
        lay.addWidget(label_Theta, 8, 1, 1, 5)
        lay.addWidget(label_i_Theta, 9, 1)
        lay.addWidget(self.PyDMLabel_ThetaDimFei, 9, 2, 1, 3)
        lay.addWidget(self.PyDMLabel_ThetaNDStats, 9, 2, 1, 3)
        lay.addWidget(label_f_Theta, 9, 5)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed), 10, 2)
        return lay

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
        Thread(target=self._saveCalibrationGrid_thread, daemon=True).start()

    def _saveCalibrationGrid_thread(self):
        roi_h = self.PyDMLabel_ROIHeight.text()
        roi_w = self.PyDMLabel_ROIWidth.text()
        roi_offsetx = self.PyDMLabel_ROIOffsetX.text()
        roi_offsety = self.PyDMLabel_ROIOffsetY.text()
        self.PyDMSpinbox_ROIHeight.value_changed(
                self.image_view.image_maxheight)
        self.PyDMSpinbox_ROIHeight.send_value()
        self.PyDMSpinbox_ROIWidth.value_changed(
                self.image_view.image_maxwidth)
        self.PyDMSpinbox_ROIWidth.send_value()
        self.PyDMSpinbox_ROIOffsetX.value_changed(0)
        self.PyDMSpinbox_ROIOffsetX.send_value()
        self.PyDMSpinbox_ROIOffsetY.value_changed(0)
        self.PyDMSpinbox_ROIOffsetY.send_value()
        self.image_view.saveCalibrationGrid()
        self.PyDMSpinbox_ROIHeight.value_changed(int(roi_h))
        self.PyDMSpinbox_ROIHeight.send_value()
        self.PyDMSpinbox_ROIWidth.value_changed(int(roi_w))
        self.PyDMSpinbox_ROIWidth.send_value()
        self.PyDMSpinbox_ROIOffsetX.value_changed(int(roi_offsetx))
        self.PyDMSpinbox_ROIOffsetX.send_value()
        self.PyDMSpinbox_ROIOffsetY.value_changed(int(roi_offsety))
        self.PyDMSpinbox_ROIOffsetY.send_value()
        time.sleep(0.1)

    @Slot()
    def _showFailToSaveGridMsg(self):
        QMessageBox.warning(self, 'Warning',
                            'Could not save calibration grid!',
                            QMessageBox.Ok)


class _ScrnSettingsDetails(SiriusMainWindow):

    def __init__(self, parent=None, device=None, prefix=None):
        super().__init__(parent=parent)
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = 'ca://'+self.prefix+self.device
        self.setWindowTitle('Screen Settings Details')
        self.centralwidget = QWidget(self)
        self._setupUi()
        self.setCentralWidget(self.centralwidget)

    def _setupUi(self):
        label_general = QLabel('<h4>Screen General Info</h4>')

        label_MtrPrefix = QLabel('Motor Prefix: ', self)
        self.PyDMLabel_MtrPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':MtrCtrlPrefix-Cte')

        label_CamPrefix = QLabel('Camera Prefix: ', self)
        self.PyDMLabel_CamPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamPrefix-Cte')

        label_ImgMaxWidth = QLabel('Image Maximum Width: ', self)
        self.PyDMLabel_ImgMaxWidth = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxWidth-Cte')
        self.PyDMLabel_ImgMaxWidth.setMaximumSize(220, 40)

        label_ImgMaxHeight = QLabel('Image Maximum Height: ', self)
        self.PyDMLabel_ImgMaxHeight = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxHeight-Cte')
        self.PyDMLabel_ImgMaxHeight.setMaximumSize(220, 40)

        label_acq = QLabel('<h4>Camera Acquire Settings</h4>')

        label_CamEnbl = QLabel('Acquire Enable Status', self)
        self.PyDMStateButton_CamEnbl = PyDMStateButton(
            parent=self, init_channel=self.scrn_prefix+':CamEnbl-Sel')
        self.PyDMStateButton_CamEnbl.setMaximumSize(220, 40)
        self.PyDMStateButton_CamEnbl.shape = 1
        self.PyDMLabel_CamEnbl = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamEnbl-Sts')
        self.PyDMLabel_CamEnbl.setMaximumSize(220, 40)
        self.PyDMLabel_CamEnbl.setAlignment(Qt.AlignCenter)
        hbox_CamEnbl = QHBoxLayout()
        hbox_CamEnbl.addWidget(self.PyDMStateButton_CamEnbl)
        hbox_CamEnbl.addWidget(self.PyDMLabel_CamEnbl)

        label_AcqMode = QLabel('Acquire Mode', self)
        self.PyDMEnumComboBox_AcqMode = PyDMEnumComboBox(
            parent=self, init_channel=self.scrn_prefix+':CamAcqMode-Sel')
        self.PyDMEnumComboBox_AcqMode.setMaximumSize(220, 40)
        self.PyDMLabel_AcqMode = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamAcqMode-Sts')
        self.PyDMLabel_AcqMode.setMaximumSize(220, 40)
        self.PyDMLabel_AcqMode.setAlignment(Qt.AlignCenter)
        hbox_AcqMode = QHBoxLayout()
        hbox_AcqMode.addWidget(self.PyDMEnumComboBox_AcqMode)
        hbox_AcqMode.addWidget(self.PyDMLabel_AcqMode)

        label_AcqPeriod = QLabel('Acquire Period', self)
        self.PyDMSpinbox_AcqPeriod = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamAcqPeriod-SP')
        self.PyDMSpinbox_AcqPeriod.setMaximumSize(220, 40)
        self.PyDMSpinbox_AcqPeriod.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_AcqPeriod.showStepExponent = False
        self.PyDMLabel_AcqPeriod = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamAcqPeriod-RB')
        self.PyDMLabel_AcqPeriod.setMaximumSize(220, 40)
        self.PyDMLabel_AcqPeriod.setAlignment(Qt.AlignCenter)
        hbox_AcqPeriod = QHBoxLayout()
        hbox_AcqPeriod.addWidget(self.PyDMSpinbox_AcqPeriod)
        hbox_AcqPeriod.addWidget(self.PyDMLabel_AcqPeriod)

        label_ExpMode = QLabel('Exposure Mode', self)
        self.PyDMEnumComboBox_ExpMode = PyDMEnumComboBox(
            parent=self, init_channel=self.scrn_prefix+':CamExposureMode-Sel')
        self.PyDMEnumComboBox_ExpMode.setMaximumSize(220, 40)
        self.PyDMLabel_ExpMode = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamExposureMode-Sts')
        self.PyDMLabel_ExpMode.setMaximumSize(220, 40)
        self.PyDMLabel_ExpMode.setAlignment(Qt.AlignCenter)
        hbox_ExpMode = QHBoxLayout()
        hbox_ExpMode.addWidget(self.PyDMEnumComboBox_ExpMode)
        hbox_ExpMode.addWidget(self.PyDMLabel_ExpMode)

        label_ExpTime = QLabel('Exposure Time', self)
        self.PyDMSpinbox_ExpTime = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamExposureTime-SP')
        self.PyDMSpinbox_ExpTime.setMaximumSize(220, 40)
        self.PyDMSpinbox_ExpTime.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ExpTime.showStepExponent = False
        self.PyDMLabel_ExpTime = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamExposureTime-RB')
        self.PyDMLabel_ExpTime.setMaximumSize(220, 40)
        self.PyDMLabel_ExpTime.setAlignment(Qt.AlignCenter)
        hbox_ExpTime = QHBoxLayout()
        hbox_ExpTime.addWidget(self.PyDMSpinbox_ExpTime)
        hbox_ExpTime.addWidget(self.PyDMLabel_ExpTime)

        label_Gain = QLabel('Gain', self)
        self.PyDMSpinbox_Gain = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamGain-SP')
        self.PyDMSpinbox_Gain.setFixedSize(220, 40)
        self.PyDMSpinbox_Gain.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_Gain.showStepExponent = False
        self.PyDMLabel_Gain = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamGain-RB')
        self.PyDMLabel_Gain.setFixedSize(220, 40)
        self.PyDMLabel_Gain.setAlignment(Qt.AlignCenter)
        self.PyDMPushButton_AutoGain = PyDMPushButton(
            parent=self, label='Auto Gain', pressValue=1,
            init_channel=self.scrn_prefix+':CamAutoGain-Cmd')
        self.PyDMPushButton_AutoGain.setMaximumSize(220, 40)
        hbox_Gain = QHBoxLayout()
        hbox_Gain.addWidget(self.PyDMSpinbox_Gain)
        hbox_Gain.addWidget(self.PyDMLabel_Gain)
        hbox_Gain.addWidget(self.PyDMPushButton_AutoGain)

        label_BlackLevel = QLabel('Black Level', self)
        self.PyDMSpinbox_BlackLevel = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CamBlackLevel-SP')
        self.PyDMSpinbox_BlackLevel.setMaximumSize(220, 40)
        self.PyDMSpinbox_BlackLevel.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_BlackLevel.showStepExponent = False
        self.PyDMLabel_BlackLevel = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamBlackLevel-RB')
        self.PyDMLabel_BlackLevel.setMaximumSize(220, 40)
        self.PyDMLabel_BlackLevel.setAlignment(Qt.AlignCenter)
        hbox_BlackLevel = QHBoxLayout()
        hbox_BlackLevel.addWidget(self.PyDMSpinbox_BlackLevel)
        hbox_BlackLevel.addWidget(self.PyDMLabel_BlackLevel)

        label_ROI = QLabel('<h4>Camera Region of Interest (ROI) Settings</h4>')

        label_ROIOffsetX = QLabel('Offset X', self)
        self.PyDMSpinbox_ROIOffsetX = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetX-SP')
        self.PyDMSpinbox_ROIOffsetX.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIOffsetX.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIOffsetX.showStepExponent = False
        self.PyDMLabel_ROIOffsetX = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetX-RB')
        self.PyDMLabel_ROIOffsetX.setMaximumSize(220, 40)
        self.PyDMLabel_ROIOffsetX.setAlignment(Qt.AlignCenter)
        hbox_ROIOffsetX = QHBoxLayout()
        hbox_ROIOffsetX.addWidget(self.PyDMSpinbox_ROIOffsetX)
        hbox_ROIOffsetX.addWidget(self.PyDMLabel_ROIOffsetX)

        label_ROIOffsetY = QLabel('Offset Y', self)
        self.PyDMSpinbox_ROIOffsetY = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetY-SP')
        self.PyDMSpinbox_ROIOffsetY.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIOffsetY.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIOffsetY.showStepExponent = False
        self.PyDMLabel_ROIOffsetY = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIOffsetY-RB')
        self.PyDMLabel_ROIOffsetY.setMaximumSize(220, 40)
        self.PyDMLabel_ROIOffsetY.setAlignment(Qt.AlignCenter)
        hbox_ROIOffsetY = QHBoxLayout()
        hbox_ROIOffsetY.addWidget(self.PyDMSpinbox_ROIOffsetY)
        hbox_ROIOffsetY.addWidget(self.PyDMLabel_ROIOffsetY)

        label_ROIWidth = QLabel('Width', self)
        self.PyDMSpinbox_ROIWidth = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIWidth-SP')
        self.PyDMSpinbox_ROIWidth.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIWidth.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIWidth.showStepExponent = False
        self.PyDMLabel_ROIWidth = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIWidth-RB')
        self.PyDMLabel_ROIWidth.setMaximumSize(220, 40)
        self.PyDMLabel_ROIWidth.setAlignment(Qt.AlignCenter)
        hbox_ROIWidth = QHBoxLayout()
        hbox_ROIWidth.addWidget(self.PyDMSpinbox_ROIWidth)
        hbox_ROIWidth.addWidget(self.PyDMLabel_ROIWidth)

        label_ROIHeight = QLabel('Heigth', self)
        self.PyDMSpinbox_ROIHeight = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':ImgROIHeight-SP')
        self.PyDMSpinbox_ROIHeight.setMaximumSize(220, 40)
        self.PyDMSpinbox_ROIHeight.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_ROIHeight.showStepExponent = False
        self.PyDMLabel_ROIHeight = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgROIHeight-RB')
        self.PyDMLabel_ROIHeight.setMaximumSize(220, 40)
        self.PyDMLabel_ROIHeight.setAlignment(Qt.AlignCenter)
        hbox_ROIHeight = QHBoxLayout()
        hbox_ROIHeight.addWidget(self.PyDMSpinbox_ROIHeight)
        hbox_ROIHeight.addWidget(self.PyDMLabel_ROIHeight)

        label_AutoCenterX = QLabel('Auto Center X', self)
        self.PyDMStateButton_AutoCenterX = PyDMStateButton(
            parent=self,
            init_channel=self.scrn_prefix + ':ImgROIAutoCenterX-Sel')
        self.PyDMStateButton_AutoCenterX.setMaximumSize(220, 40)
        self.PyDMStateButton_AutoCenterX.shape = 1
        self.PyDMLabel_AutoCenterX = PyDMLabel(
            parent=self,
            init_channel=self.scrn_prefix + ':ImgROIAutoCenterX-Sts')
        self.PyDMLabel_AutoCenterX.setMaximumSize(220, 40)
        self.PyDMLabel_AutoCenterX.setAlignment(Qt.AlignCenter)
        hbox_AutoCenterX = QHBoxLayout()
        hbox_AutoCenterX.addWidget(self.PyDMStateButton_AutoCenterX)
        hbox_AutoCenterX.addWidget(self.PyDMLabel_AutoCenterX)

        label_AutoCenterY = QLabel('Auto Center Y', self)
        self.PyDMStateButton_AutoCenterY = PyDMStateButton(
            parent=self,
            init_channel=self.scrn_prefix + ':ImgROIAutoCenterY-Sel')
        self.PyDMStateButton_AutoCenterY.setMaximumSize(220, 40)
        self.PyDMStateButton_AutoCenterY.shape = 1
        self.PyDMLabel_AutoCenterY = PyDMLabel(
            parent=self,
            init_channel=self.scrn_prefix + ':ImgROIAutoCenterY-Sts')
        self.PyDMLabel_AutoCenterY.setMaximumSize(220, 40)
        self.PyDMLabel_AutoCenterY.setAlignment(Qt.AlignCenter)
        hbox_AutoCenterY = QHBoxLayout()
        hbox_AutoCenterY.addWidget(self.PyDMStateButton_AutoCenterY)
        hbox_AutoCenterY.addWidget(self.PyDMLabel_AutoCenterY)

        label_err = QLabel('<h4>Camera Errors Monitoring</h4>')

        label_AcceptedErr = QLabel('Positioning Error Tolerance', self)
        self.PyDMSpinbox_AcceptedErr = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':AcceptedErr-SP')
        self.PyDMSpinbox_AcceptedErr.setMaximumSize(220, 40)
        self.PyDMSpinbox_AcceptedErr.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_AcceptedErr.showStepExponent = False
        self.PyDMLabel_AcceptedErr = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':AcceptedErr-RB')
        self.PyDMLabel_AcceptedErr.setMaximumSize(220, 40)
        self.PyDMLabel_AcceptedErr.setAlignment(Qt.AlignCenter)
        hbox_AcceptedErr = QHBoxLayout()
        hbox_AcceptedErr.addWidget(self.PyDMSpinbox_AcceptedErr)
        hbox_AcceptedErr.addWidget(self.PyDMLabel_AcceptedErr)

        label_CamTemp = QLabel('Temperature', self)
        self.PyDMLabel_CamTemp = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamTemp-Mon')
        self.PyDMLabel_CamTemp.setAlignment(Qt.AlignCenter)
        self.PyDMLabel_CamTemp.setMaximumSize(220, 40)
        self.PyDMLabel_CamTempState = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamTempState-Mon')
        self.PyDMLabel_CamTempState.setMaximumSize(220, 40)
        self.PyDMLabel_CamTempState.setAlignment(Qt.AlignCenter)
        hbox_CamTemp = QHBoxLayout()
        hbox_CamTemp.addWidget(self.PyDMLabel_CamTemp)
        hbox_CamTemp.addWidget(self.PyDMLabel_CamTempState)

        label_LastErr = QLabel('Last Error', self)
        self.PyDMLabel_LastErr = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamLastErr-Mon')
        self.PyDMLabel_LastErr.setAlignment(Qt.AlignCenter)
        self.PyDMLabel_LastErr.setMinimumSize(440, 40)
        self.PyDMPushButton_LastErr = PyDMPushButton(
            parent=self, label='Clear Last Error', pressValue=1,
            init_channel=self.scrn_prefix+':CamClearLastErr-Cmd')
        self.PyDMPushButton_LastErr.setMaximumSize(220, 40)
        hbox_LastErr = QHBoxLayout()
        hbox_LastErr.addWidget(self.PyDMLabel_LastErr)
        hbox_LastErr.addWidget(self.PyDMPushButton_LastErr)

        label_details = QLabel('<h4>Detailed Screen Control</h4>')

        label_FluorScrnPos = QLabel('Fluorescent Screen Position', self)
        self.PyDMSpinbox_FluorScrnPos = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':FluorScrnPos-SP')
        self.PyDMSpinbox_FluorScrnPos.setMaximumSize(220, 40)
        self.PyDMSpinbox_FluorScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_FluorScrnPos.showStepExponent = False
        self.PyDMLabel_FluorScrnPos = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':FluorScrnPos-RB')
        self.PyDMLabel_FluorScrnPos.setMaximumSize(220, 40)
        self.PyDMLabel_FluorScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMPushButton_FluorScrnPos = PyDMPushButton(
            parent=self, label='Get Position', pressValue=1,
            init_channel=self.scrn_prefix + ':GetFluorScrnPos-Cmd')
        self.PyDMPushButton_FluorScrnPos.setMaximumSize(220, 40)
        hbox_FluorScrnPos = QHBoxLayout()
        hbox_FluorScrnPos.addWidget(self.PyDMSpinbox_FluorScrnPos)
        hbox_FluorScrnPos.addWidget(self.PyDMLabel_FluorScrnPos)
        hbox_FluorScrnPos.addWidget(self.PyDMPushButton_FluorScrnPos)

        label_CalScrnPos = QLabel('Calibration Screen Position', self)
        self.PyDMSpinbox_CalScrnPos = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':CalScrnPos-SP')
        self.PyDMSpinbox_CalScrnPos.setMaximumSize(220, 40)
        self.PyDMSpinbox_CalScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_CalScrnPos.showStepExponent = False
        self.PyDMLabel_CalScrnPos = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CalScrnPos-RB')
        self.PyDMLabel_CalScrnPos.setMaximumSize(220, 40)
        self.PyDMLabel_CalScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMPushButton_CalScrnPos = PyDMPushButton(
            parent=self, label='Get Position', pressValue=1,
            init_channel=self.scrn_prefix+':GetCalScrnPos-Cmd')
        self.PyDMPushButton_CalScrnPos.setMaximumSize(220, 40)
        hbox_CalScrnPos = QHBoxLayout()
        hbox_CalScrnPos.addWidget(self.PyDMSpinbox_CalScrnPos)
        hbox_CalScrnPos.addWidget(self.PyDMLabel_CalScrnPos)
        hbox_CalScrnPos.addWidget(self.PyDMPushButton_CalScrnPos)

        label_NoneScrnPos = QLabel('Receded Screen Position', self)
        self.PyDMSpinbox_NoneScrnPos = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':NoneScrnPos-SP')
        self.PyDMSpinbox_NoneScrnPos.setMaximumSize(220, 40)
        self.PyDMSpinbox_NoneScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_NoneScrnPos.showStepExponent = False
        self.PyDMLabel_NoneScrnPos = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':NoneScrnPos-RB')
        self.PyDMLabel_NoneScrnPos.setMaximumSize(220, 40)
        self.PyDMLabel_NoneScrnPos.setAlignment(Qt.AlignCenter)
        self.PyDMPushButton_NoneScrnPos = PyDMPushButton(
            parent=self, label='Get Position', pressValue=1,
            init_channel=self.scrn_prefix+':GetNoneScrnPos-Cmd')
        self.PyDMPushButton_NoneScrnPos.setMaximumSize(220, 40)
        hbox_NoneScrnPos = QHBoxLayout()
        hbox_NoneScrnPos.addWidget(self.PyDMSpinbox_NoneScrnPos)
        hbox_NoneScrnPos.addWidget(self.PyDMLabel_NoneScrnPos)
        hbox_NoneScrnPos.addWidget(self.PyDMPushButton_NoneScrnPos)

        label_LedPwrLvl = QLabel('LED Brightness Intensity', self)
        self.PyDMSpinbox_LedPwrLvl = PyDMSpinbox(
            parent=self, init_channel=self.scrn_prefix+':LEDPwrLvl-SP')
        self.PyDMSpinbox_LedPwrLvl.setMaximumSize(220, 40)
        self.PyDMSpinbox_LedPwrLvl.setAlignment(Qt.AlignCenter)
        self.PyDMSpinbox_LedPwrLvl.showStepExponent = False
        self.PyDMLabel_LedPwrLvl = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':LEDPwrLvl-RB')
        self.PyDMLabel_LedPwrLvl.setMaximumSize(220, 40)
        self.PyDMLabel_LedPwrLvl.setAlignment(Qt.AlignCenter)
        hbox_LedPwrLvl = QHBoxLayout()
        hbox_LedPwrLvl.addWidget(self.PyDMSpinbox_LedPwrLvl)
        hbox_LedPwrLvl.addWidget(self.PyDMLabel_LedPwrLvl)

        flay = QFormLayout()
        flay.addRow(label_general)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_MtrPrefix, self.PyDMLabel_MtrPrefix)
        flay.addRow(label_CamPrefix, self.PyDMLabel_CamPrefix)
        flay.addRow(label_ImgMaxWidth, self.PyDMLabel_ImgMaxWidth)
        flay.addRow(label_ImgMaxHeight, self.PyDMLabel_ImgMaxHeight)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_acq)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_CamEnbl, hbox_CamEnbl)
        flay.addRow(label_AcqMode, hbox_AcqMode)
        flay.addRow(label_AcqPeriod, hbox_AcqPeriod)
        flay.addRow(label_ExpMode, hbox_ExpMode)
        flay.addRow(label_ExpTime, hbox_ExpTime)
        flay.addRow(label_Gain, hbox_Gain)
        flay.addRow(label_BlackLevel, hbox_BlackLevel)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_ROI)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_ROIOffsetX, hbox_ROIOffsetX)
        flay.addRow(label_ROIOffsetY, hbox_ROIOffsetY)
        flay.addRow(label_ROIWidth, hbox_ROIWidth)
        flay.addRow(label_ROIHeight, hbox_ROIHeight)
        flay.addRow(label_AutoCenterX, hbox_AutoCenterX)
        flay.addRow(label_AutoCenterY, hbox_AutoCenterY)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_err)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_AcceptedErr, hbox_AcceptedErr)
        flay.addRow(label_CamTemp, hbox_CamTemp)
        flay.addRow(label_LastErr, hbox_LastErr)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_details)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        flay.addRow(label_FluorScrnPos, hbox_FluorScrnPos)
        flay.addRow(label_CalScrnPos, hbox_CalScrnPos)
        flay.addRow(label_NoneScrnPos, hbox_NoneScrnPos)
        flay.addRow(label_LedPwrLvl, hbox_LedPwrLvl)
        self.centralwidget.setLayout(flay)
        flay.setLabelAlignment(Qt.AlignRight)


if __name__ == '__main__':
    """Run test."""
    app = SiriusApplication()
    util.set_style(app)

    centralwidget = QWidget()
    scrn_view = SiriusScrnView(prefix=_vaca_prefix, device='TB-01:DI-Scrn-1')
    cb_scrntype = PyDMEnumComboBox(
        parent=centralwidget,
        init_channel='ca://'+_vaca_prefix+'TB-01:DI-Scrn-1:ScrnType-Sel')
    cb_scrntype.currentIndexChanged.connect(
        scrn_view.updateCalibrationGridFlag)

    lay = QGridLayout()
    lay.addWidget(QLabel('<h3>SiriusScrnView Test</h3>', centralwidget,
                         alignment=Qt.AlignCenter), 0, 0, 1, 2)
    lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 1, 0)
    lay.addWidget(QLabel('Select Screen Type: ', centralwidget,
                         alignment=Qt.AlignRight), 2, 0)
    lay.addWidget(cb_scrntype, 2, 1)
    lay.addItem(QSpacerItem(20, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 0)
    lay.addWidget(scrn_view, 4, 0, 1, 2)
    centralwidget.setLayout(lay)

    window = SiriusMainWindow()
    window.setWindowTitle('SiriusScrnView Test')
    window.setCentralWidget(centralwidget)
    window.show()
    sys.exit(app.exec_())
