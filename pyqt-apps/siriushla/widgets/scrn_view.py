"""SiriusScrnView widget."""

import sys
import time
from copy import deepcopy as _dcopy
from threading import Thread
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QFormLayout, \
                           QSpacerItem, QWidget, QGroupBox, QLabel, \
                           QComboBox, QPushButton, QCheckBox, QMessageBox, \
                           QSizePolicy as QSzPlcy, QVBoxLayout, QSpinBox
from qtpy.QtCore import Qt, Slot, Signal, Property
from pydm.widgets import PyDMImageView, PyDMLabel, PyDMSpinbox, \
                         PyDMPushButton, PyDMEnumComboBox
from pydm.widgets.channel import PyDMChannel
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util
from siriushla.widgets import PyDMStateButton, SiriusLedState, PyDMLed, \
                              PyDMLedMultiChannel
from siriushla.widgets.signal_channel import SiriusConnectionSignal
from siriushla.widgets.windows import SiriusMainWindow, SiriusDialog
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed


class _SiriusImageView(PyDMImageView):
    """A PyDMImageView with methods to handle screens calibration grids."""

    failToSaveGrid = Signal()

    def __init__(self, parent=None,
                 image_channel=None, width_channel=None,
                 offsetx_channel=None, offsety_channel=None,
                 maxwidth_channel=None, maxheight_channel=None):
        """Initialize the object."""
        PyDMImageView.__init__(
            self, parent=parent, image_channel=image_channel,
            width_channel=width_channel)
        self._channels.extend(4*[None, ])
        self._calibration_grid_image = None
        self._calibration_grid_maxdata = None
        self._calibration_grid_width = None
        self._calibration_grid_filterfactor = 0.5
        self._image_roi_offsetx = 0
        self._offsetxchannel = None
        self._image_roi_offsety = 0
        self._offsetychannel = None
        self._image_maxwidth = 0
        self._maxwidthchannel = None
        self._image_maxheight = 0
        self._maxheightchannel = None
        self._show_calibration_grid = False
        # Set live channels if requested on initialization
        if offsetx_channel:
            self.ROIOffsetXChannel = offsetx_channel
        if offsety_channel:
            self.ROIOffsetYChannel = offsety_channel
        if maxwidth_channel:
            self.maxWidthChannel = maxwidth_channel
        if maxheight_channel:
            self.maxHeightChannel = maxheight_channel

    @Slot()
    def saveCalibrationGrid(self):
        """Save current image as calibration_grid_image."""
        for i in range(40):
            if self.image_waveform.size == (
                    self.image_maxwidth*self.image_maxheight):
                img = self.image_waveform.copy()
                self._calibration_grid_orig = img
                self._calibration_grid_width = self.imageWidth
                self._calibration_grid_maxdata = img.max()
                self._update_calibration_grid_image()
                break
            time.sleep(0.05)
        else:
            self.failToSaveGrid.emit()

    def _update_calibration_grid_image(self):
        img = self._calibration_grid_orig
        grid = np.where(img < self._calibration_grid_filterfactor *
                        self._calibration_grid_maxdata, True, False)
        if self.readingOrder == self.ReadingOrder.Clike:
            self._calibration_grid_image = grid.reshape(
                (-1, self._calibration_grid_width), order='C')
        else:
            self._calibration_grid_image = grid.reshape(
                (self._calibration_grid_width, -1), order='F')

    @Slot(bool)
    def showCalibrationGrid(self, show):
        """Show calibration_grid_image over the current image_waveform."""
        self._show_calibration_grid = show
        self.needs_redraw = True

    @property
    def calibration_grid_filterfactor(self):
        """Factor used to filter calibration grid.

        Pixels with values smaller than filterfactor*img_maxdata
        are set to zero.

        Returns
        -------
        float
            Calibration Grid Filter Factor
        """
        return self._calibration_grid_filterfactor*100

    def set_calibration_grid_filterfactor(self, value):
        """Set factor used to filter calibration grid.

        Pixels with values smaller than filterfactor*img_maxdata
        are set to zero.

        Parameters
        ----------
        value: int
            Calibration Grid Filter Factor
        """
        value /= 100
        if value >= 0 and self._calibration_grid_filterfactor != value:
            self._calibration_grid_filterfactor = value
            if self._calibration_grid_image is not None:
                self._update_calibration_grid_image()

    def process_image(self, image):
        """Reimplement process_image method to add grid to image."""
        image2process = _dcopy(image)
        if ((self._show_calibration_grid) and
                (self._calibration_grid_image is not None)):
            try:
                grid = self._adjust_calibration_grid(image2process)
                image2process[grid] = self._calibration_grid_maxdata
            except Exception:
                print('Grid dimentions do not match image dimentions!')
        return image2process

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
        self._image_maxwidth = int(new_max)

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
        self._image_maxheight = int(new_max)

    @Property(str)
    def ROIOffsetXChannel(self):
        """
        The channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address
        """
        if self._offsetxchannel:
            return str(self._offsetxchannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._offsetxchannel:
                self._offsetxchannel.disconnect()
            # Create and connect new channel
            self._offsetxchannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsetx_connection_state_changed,
                value_slot=self.image_roioffsetx_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[2] = self._offsetxchannel
            self._offsetxchannel.connect()

    @Property(str)
    def ROIOffsetYChannel(self):
        """
        The channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address
        """
        if self._offsetychannel:
            return str(self._offsetychannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._offsetychannel:
                self._offsetychannel.disconnect()
            # Create and connect new channel
            self._offsetychannel = PyDMChannel(
                address=value,
                connection_slot=self.roioffsety_connection_state_changed,
                value_slot=self.image_roioffsety_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[3] = self._offsetychannel
            self._offsetychannel.connect()

    @Property(str)
    def maxWidthChannel(self):
        """
        The channel address in use for the image ROI horizontal offset.

        Returns
        -------
        str
            Channel address
        """
        if self._maxwidthchannel:
            return str(self._maxwidthchannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._maxwidthchannel:
                self._maxwidthchannel.disconnect()
            # Create and connect new channel
            self._maxwidthchannel = PyDMChannel(
                address=value,
                value_slot=self.image_maxwidth_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[4] = self._maxwidthchannel
            self._maxwidthchannel.connect()

    @Property(str)
    def maxHeightChannel(self):
        """
        The channel address in use for the image ROI vertical offset.

        Returns
        -------
        str
            Channel address
        """
        if self._maxheightchannel:
            return str(self._maxheightchannel.address)
        else:
            return ''

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
            # Disconnect old channel
            if self._maxheightchannel:
                self._maxheightchannel.disconnect()
            # Create and connect new channel
            self._maxheightchannel = PyDMChannel(
                address=value,
                value_slot=self.image_maxheight_changed,
                severity_slot=self.alarmSeverityChanged)
            self._channels[5] = self._maxheightchannel
            self._maxheightchannel.connect()


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
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = self.prefix+self.device
        self._calibrationgrid_flag = False
        screen_type_conn = SiriusConnectionSignal(
            self.scrn_prefix+':ScrnType-Sts')
        screen_type_conn.new_value_signal.connect(
            self.updateCalibrationGridFlag)
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
        self.layout().addWidget(self.cameraview_widget, 0, 0, 1, 5)

        self.layout().addItem(
            QSpacerItem(4, 20, QSzPlcy.Preferred, QSzPlcy.Preferred), 1, 0)

        self.settings_groupBox = QGroupBox('Settings', self)
        self.settings_groupBox.setLayout(self._settingsLayout())
        self.layout().addWidget(self.settings_groupBox, 2, 1, 3, 1)

        self.layout().addItem(
            QSpacerItem(10, 20, QSzPlcy.Preferred, QSzPlcy.Preferred), 2, 2)

        self.statistics_groupBox = QGroupBox('Statistics', self)
        self.statistics_groupBox.setLayout(self._statisticsLayout())
        self.layout().addWidget(self.statistics_groupBox, 2, 3)
        self.statistics_groupBox.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Expanding)
        self.statistics_groupBox.setStyleSheet("""
            .QLabel{
                min-width:0.32em;\nmax-width:0.32em;\n
                min-height:1.29em;\nmax-height:1.29em;\n}
            QLabel{
                qproperty-alignment: AlignCenter;\n}
            PyDMWidget{
                min-width:4.84em;\nmax-width:4.84em;\n
                min-height:1.29em;\nmax-height:1.29em;\n}""")

        self.layout().addItem(
            QSpacerItem(30, 20, QSzPlcy.Preferred, QSzPlcy.Preferred), 3, 3)

        self.calibrationgrid_groupBox = QGroupBox('Calibration')
        self.calibrationgrid_groupBox.setLayout(self._calibrationgridLayout())
        self.calibrationgrid_groupBox.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Expanding)
        self.calibrationgrid_groupBox.layout().setAlignment(Qt.AlignHCenter)
        self.layout().addWidget(self.calibrationgrid_groupBox, 4, 3)

        self.layout().addItem(
            QSpacerItem(4, 20, QSzPlcy.Preferred, QSzPlcy.Preferred), 5, 4)

        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 5)
        self.layout().setColumnStretch(2, 1)
        self.layout().setColumnStretch(3, 5)
        self.layout().setColumnStretch(4, 1)

    def _cameraviewLayout(self):
        label = QLabel(self.device, self)
        label.setStyleSheet("""font-weight: bold;max-height:1.29em;""")
        label.setAlignment(Qt.AlignCenter)
        self.image_view = _SiriusImageView(
            parent=self,
            image_channel=self.scrn_prefix+':ImgData-Mon',
            width_channel=self.scrn_prefix+':ImgROIWidth-RB',
            offsetx_channel=self.scrn_prefix+':ImgROIOffsetX-RB',
            offsety_channel=self.scrn_prefix+':ImgROIOffsetY-RB',
            maxwidth_channel=self.scrn_prefix+':ImgMaxWidth-Cte',
            maxheight_channel=self.scrn_prefix+':ImgMaxHeight-Cte')
        self.image_view.setObjectName('ScrnView')
        self.image_view.normalizeData = True
        self.image_view.readingOrder = self.image_view.Clike
        self.image_view.maxRedrawRate = 15
        self.image_view.setStyleSheet("""
            #ScrnView{
                min-width:42em;\nmax-width:42m;
                min-height:32em;\nmax-height:32em;\n}""")
        self.image_view.failToSaveGrid.connect(self._showFailToSaveGridMsg)

        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(label, 0, 1)
        lay.addItem(QSpacerItem(40, 2, QSzPlcy.Preferred, QSzPlcy.Fixed), 1, 1)
        lay.addWidget(self.image_view, 2, 1)
        return lay

    def _calibrationgridLayout(self):
        self.checkBox_showgrid = QCheckBox('Show', self)
        self.checkBox_showgrid.setEnabled(False)
        self.checkBox_showgrid.setStyleSheet("""
            min-width:4.36em;\nmax-width:4.36em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.checkBox_showgrid.toggled.connect(
            self.image_view.showCalibrationGrid)
        self.pushbutton_savegrid = QPushButton('Save', self)
        self.pushbutton_savegrid.setEnabled(False)
        self.pushbutton_savegrid.setStyleSheet("""
            min-width:4.36em;\nmax-width:4.36em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.pushbutton_savegrid.clicked.connect(self._saveCalibrationGrid)
        hbox_grid = QHBoxLayout()
        hbox_grid.addWidget(self.checkBox_showgrid)
        hbox_grid.addWidget(self.pushbutton_savegrid)

        self.spinbox_gridfilterfactor = QSpinBox()
        self.spinbox_gridfilterfactor.setMaximum(100)
        self.spinbox_gridfilterfactor.setMinimum(0)
        self.spinbox_gridfilterfactor.setValue(
            self.image_view.calibration_grid_filterfactor)
        self.spinbox_gridfilterfactor.editingFinished.connect(
            self._setCalibrationGridFilterFactor)
        self.spinbox_gridfilterfactor.setStyleSheet("""
            min-width:2.90em;\nmax-width:2.90em;""")
        hbox_filter = QHBoxLayout()
        hbox_filter.setSpacing(0)
        hbox_filter.addWidget(QLabel('Show levels <'))
        hbox_filter.addWidget(self.spinbox_gridfilterfactor)
        hbox_filter.addWidget(QLabel('%'))

        hbox_EnblLED = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='EnblLED',
            propty_type='enbldisabl', width=4.68)

        lay = QFormLayout()
        lay.addItem(QSpacerItem(40, 10, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addRow('     Grid: ', hbox_grid)
        lay.addItem(QSpacerItem(40, 10, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addRow('     ', hbox_filter)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addRow('     LED: ', hbox_EnblLED)
        lay.addItem(QSpacerItem(40, 10, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        return lay

    def _settingsLayout(self):
        label_CamEnbl = QLabel('Enable: ', self, alignment=Qt.AlignCenter)
        hbox_CamEnbl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamEnbl',
            propty_type='enbldisabl', width=4.68)

        label_CamAcqPeriod = QLabel('Acquire\nPeriod [s]:', self,
                                    alignment=Qt.AlignCenter)
        hbox_CamAcqPeriod = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqPeriod',
            propty_type='sprb', width=4.68)

        label_CamExposureTime = QLabel('Exposure\nTime [us]:', self,
                                       alignment=Qt.AlignCenter)
        hbox_CamExposureTime = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureTime',
            propty_type='sprb', width=4.68)

        label_CamGain = QLabel('Gain[dB]:', self, alignment=Qt.AlignRight)
        hbox_CamGain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamGain',
            propty_type='sprb', width=4.68)
        hbox_AutoCamGain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='AutoGain',
            propty_type='', width=4.68, cmd={'label': 'Auto Gain',
                                             'pressValue': 1,
                                             'name': 'CamAutoGain'})

        label_ROIOffsetX = QLabel('Offset X: ', self, alignment=Qt.AlignRight)
        hbox_ROIOffsetX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetX',
            propty_type='sprb', width=4.68)

        label_ROIOffsetY = QLabel('Offset Y: ', self, alignment=Qt.AlignRight)
        hbox_ROIOffsetY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetY',
            propty_type='sprb', width=4.68)

        label_ROIWidth = QLabel('Width: ', self, alignment=Qt.AlignRight)
        hbox_ROIWidth = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIWidth',
            propty_type='sprb', width=4.68)

        label_ROIHeight = QLabel('Heigth: ', self, alignment=Qt.AlignRight)
        hbox_ROIHeight = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIHeight',
            propty_type='sprb', width=4.68)

        self.pb_moreSettings = QPushButton('More settings...', self)
        util.connect_window(self.pb_moreSettings, _ScrnSettingsDetails,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QFormLayout()
        lay.setFormAlignment(Qt.AlignCenter)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.addRow(QLabel('<h4>Camera Acquisition</h4>',
                          alignment=Qt.AlignCenter))
        lay.addRow(label_CamEnbl, hbox_CamEnbl)
        lay.addRow(label_CamAcqPeriod, hbox_CamAcqPeriod)
        lay.addRow(label_CamExposureTime, hbox_CamExposureTime)
        lay.addRow(label_CamGain, hbox_CamGain)
        lay.addRow('', hbox_AutoCamGain)
        lay.addItem(QSpacerItem(4, 20, QSzPlcy.Fixed, QSzPlcy.Preferred))
        lay.addRow(QLabel('<h4>Camera ROI Settings [pixels]</h4>',
                          alignment=Qt.AlignCenter))
        lay.addRow(label_ROIWidth, hbox_ROIWidth)
        lay.addRow(label_ROIHeight, hbox_ROIHeight)
        lay.addRow(label_ROIOffsetX, hbox_ROIOffsetX)
        lay.addRow(label_ROIOffsetY, hbox_ROIOffsetY)
        lay.addItem(QSpacerItem(4, 20, QSzPlcy.Fixed, QSzPlcy.Preferred))
        lay.addRow('', self.pb_moreSettings)
        return lay

    def _statisticsLayout(self):
        # - Method
        label_Method = QLabel('CalcMethod: ', self)
        label_Method.setStyleSheet("""min-width:6em;""")

        self.comboBox_Method = QComboBox(self)
        self.comboBox_Method.addItem('DimFei', 0)
        self.comboBox_Method.addItem('NDStats', 1)
        self.comboBox_Method.setCurrentIndex(0)
        self.comboBox_Method.setStyleSheet("""
            QComboBox::item {\nheight: 1em;}
            QComboBox{\nmin-width: 6em;}
            """)
        self.comboBox_Method.currentIndexChanged.connect(
            self._handleShowStatistics)

        # - Centroid
        label_Centroid = QLabel('Centroid [mm]', self)
        label_Centroid.setStyleSheet("""min-width:15em;max-width:25em;""")
        label_i_Center = QLabel('(', self)

        self.PyDMLabel_CenterXDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterXDimFei-Mon')
        self.PyDMLabel_CenterXNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterXNDStats-Mon')
        self.PyDMLabel_CenterXNDStats.setVisible(False)

        label_m_Center = QLabel(',', self)

        self.PyDMLabel_CenterYDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterYDimFei-Mon')
        self.PyDMLabel_CenterYNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CenterYNDStats-Mon')
        self.PyDMLabel_CenterYNDStats.setVisible(False)

        label_f_Center = QLabel(')', self)

        # - Sigma
        label_Sigma = QLabel('Sigma [mm]', self)
        label_Sigma.setStyleSheet("""min-width:15em;max-width:25em;""")
        label_i_Sigma = QLabel('(', self)

        self.PyDMLabel_SigmaXDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaXDimFei-Mon')
        self.PyDMLabel_SigmaXNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaXNDStats-Mon')
        self.PyDMLabel_SigmaXNDStats.setVisible(False)

        label_m_Sigma = QLabel(',', self)

        self.PyDMLabel_SigmaYDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaYDimFei-Mon')
        self.PyDMLabel_SigmaYNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':SigmaYNDStats-Mon')
        self.PyDMLabel_SigmaYNDStats.setVisible(False)

        label_f_Sigma = QLabel(')', self)

        # - Theta
        label_Theta = QLabel('Theta [rad]')
        label_Theta.setStyleSheet("""min-width:15em;max-width:25em;""")
        label_i_Theta = QLabel('(', self)

        self.PyDMLabel_ThetaDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaDimFei-Mon')
        self.PyDMLabel_ThetaNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaNDStats-Mon')
        self.PyDMLabel_ThetaNDStats.setVisible(False)

        label_f_Theta = QLabel(')', self)

        lay = QGridLayout()
        lay.addItem(QSpacerItem(20, 2, QSzPlcy.Fixed, QSzPlcy.Expanding), 0, 0)
        lay.addWidget(label_Method, 1, 1, 1, 2)
        lay.addWidget(self.comboBox_Method, 1, 4)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Fixed, QSzPlcy.Preferred), 2, 2)
        lay.addWidget(label_Centroid, 3, 1, 1, 5)
        lay.addWidget(label_i_Center, 4, 1)
        lay.addWidget(self.PyDMLabel_CenterXDimFei, 4, 2)
        lay.addWidget(self.PyDMLabel_CenterXNDStats, 4, 2)
        lay.addWidget(label_m_Center, 4, 3)
        lay.addWidget(self.PyDMLabel_CenterYDimFei, 4, 4)
        lay.addWidget(self.PyDMLabel_CenterYNDStats, 4, 4)
        lay.addWidget(label_f_Center, 4, 5)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Fixed, QSzPlcy.Preferred), 5, 2)
        lay.addWidget(label_Sigma, 6, 1, 1, 5)
        lay.addWidget(label_i_Sigma, 7, 1)
        lay.addWidget(self.PyDMLabel_SigmaXDimFei, 7, 2)
        lay.addWidget(self.PyDMLabel_SigmaXNDStats, 7, 2)
        lay.addWidget(label_m_Sigma, 7, 3)
        lay.addWidget(self.PyDMLabel_SigmaYDimFei, 7, 4)
        lay.addWidget(self.PyDMLabel_SigmaYNDStats, 7, 4)
        lay.addWidget(label_f_Sigma, 7, 5)
        lay.addItem(QSpacerItem(4, 2, QSzPlcy.Fixed, QSzPlcy.Preferred), 8, 2)
        lay.addWidget(label_Theta, 9, 1, 1, 5)
        lay.addWidget(label_i_Theta, 10, 1)
        lay.addWidget(self.PyDMLabel_ThetaDimFei, 10, 2, 1, 3)
        lay.addWidget(self.PyDMLabel_ThetaNDStats, 10, 2, 1, 3)
        lay.addWidget(label_f_Theta, 10, 5)
        lay.addItem(
            QSpacerItem(20, 2, QSzPlcy.Fixed, QSzPlcy.Expanding), 11, 6)
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
        roi_h = float(self.PyDMLabel_ImgROIHeight.text())
        roi_w = float(self.PyDMLabel_ImgROIWidth.text())
        roi_offsetx = float(self.PyDMLabel_ImgROIOffsetX.text())
        roi_offsety = float(self.PyDMLabel_ImgROIOffsetY.text())

        # Change ROI to get entire image
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(0)
        self.PyDMSpinbox_ImgROIHeight.send_value_signal[float].emit(
            float(self.image_view.image_maxheight))
        self.PyDMSpinbox_ImgROIWidth.send_value_signal[float].emit(
            float(self.image_view.image_maxwidth))
        self.PyDMSpinbox_ImgROIOffsetX.send_value_signal[float].emit(0)
        self.PyDMSpinbox_ImgROIOffsetY.send_value_signal[float].emit(0)
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(1)

        # Save grid
        self.image_view.saveCalibrationGrid()

        # Change ROI to original size
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(0)
        self.PyDMSpinbox_ImgROIHeight.send_value_signal[float].emit(roi_h)
        self.PyDMSpinbox_ImgROIWidth.send_value_signal[float].emit(roi_w)
        self.PyDMSpinbox_ImgROIOffsetX.send_value_signal[float].emit(
            roi_offsetx)
        self.PyDMSpinbox_ImgROIOffsetY.send_value_signal[float].emit(
            roi_offsety)
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(1)

        # Enable showing saved grid
        time.sleep(0.1)
        self.checkBox_showgrid.setEnabled(True)

    def _setCalibrationGridFilterFactor(self):
        self.image_view.set_calibration_grid_filterfactor(
            self.spinbox_gridfilterfactor.value())

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
        self.scrn_prefix = self.prefix+self.device
        self.setWindowTitle('Screen Settings Details')
        self.centralwidget = QWidget(self)
        self._setupUi()
        self.setCentralWidget(self.centralwidget)

    def _setupUi(self):
        label = QLabel('<h3>'+self.scrn_prefix+' Settings</h3>', self,
                       alignment=Qt.AlignCenter)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_acq = QGroupBox('Camera Acquire Settings', self)
        gbox_acq.setLayout(self._setupCamAcqSettingsLayout())

        gbox_trg = QGroupBox('Screen Trigger', self)
        gbox_trg.setLayout(self._setupScrnTriggerLayout())

        gbox_ROI = QGroupBox('Camera Region of Interest (ROI) Settings', self)
        gbox_ROI.setLayout(self._setupROISettingsLayout())

        gbox_err = QGroupBox('Camera Errors Monitoring', self)
        gbox_err.setLayout(self._setupErrorMonLayout())

        bt_cal = QPushButton('Screen Calibration', self)
        util.connect_window(bt_cal, _ScrnCalibrationSettings,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QGridLayout()
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 1, 0)
        lay.addWidget(gbox_general, 2, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 3, 0)
        lay.addWidget(gbox_acq, 4, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 5, 0)
        lay.addWidget(gbox_trg, 6, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 7, 0)
        lay.addWidget(gbox_ROI, 8, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 9, 0)
        lay.addWidget(gbox_err, 10, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 11, 0)
        lay.addWidget(bt_cal, 12, 1)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 13, 0)
        self.centralwidget.setLayout(lay)

    def _setupGeneralInfoLayout(self):
        label_MtrPrefix = QLabel('Motor Prefix: ', self)
        self.PyDMLabel_MtrPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':MtrCtrlPrefix-Cte')
        self.PyDMLabel_MtrPrefix.setStyleSheet(
            """max-width:14.20em; max-height:1.29em;""")

        label_CamPrefix = QLabel('Camera Prefix: ', self)
        self.PyDMLabel_CamPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamPrefix-Cte')
        self.PyDMLabel_CamPrefix.setStyleSheet(
            """max-width:14.20em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_MtrPrefix, self.PyDMLabel_MtrPrefix)
        flay.addRow(label_CamPrefix, self.PyDMLabel_CamPrefix)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupCamAcqSettingsLayout(self):
        label_CamEnbl = QLabel('Acquire Enable Status: ', self)
        hbox_CamEnbl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamEnbl',
            propty_type='enbldisabl')

        label_AcqMode = QLabel('Acquire Mode: ', self)
        hbox_AcqMode = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqMode',
            propty_type='enum')

        label_AcqPeriod = QLabel('Acquire Period [s]: ', self)
        hbox_AcqPeriod = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqPeriod',
            propty_type='sprb')

        label_ExpMode = QLabel('Exposure Mode: ', self)
        hbox_ExpMode = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureMode',
            propty_type='enum')

        label_ExpTime = QLabel('Exposure Time [us]: ', self)
        hbox_ExpTime = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureTime',
            propty_type='sprb')

        label_Gain = QLabel('Gain [dB]: ', self)
        hbox_Gain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamGain',
            propty_type='sprb', cmd={'label': 'Auto Gain',
                                     'pressValue': 1,
                                     'name': 'CamAutoGain'})

        label_BlackLevel = QLabel('Black Level: ', self)
        hbox_BlackLevel = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamBlackLevel',
            propty_type='sprb')

        flay = QFormLayout()
        flay.addRow(label_CamEnbl, hbox_CamEnbl)
        flay.addRow(label_AcqMode, hbox_AcqMode)
        flay.addRow(label_AcqPeriod, hbox_AcqPeriod)
        flay.addRow(label_ExpMode, hbox_ExpMode)
        flay.addRow(label_ExpTime, hbox_ExpTime)
        flay.addRow(label_Gain, hbox_Gain)
        flay.addRow(label_BlackLevel, hbox_BlackLevel)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupScrnTriggerLayout(self):
        if 'TB' in self.device:
            trg_prefix = self.prefix+'TB-Fam:TI-Scrn'
        elif 'BO' in self.device:
            trg_prefix = self.prefix+'BO-Fam:TI-Scrn'
        elif 'TS' in self.device:
            trg_prefix = self.prefix+'TS-Fam:TI-Scrn'

        l_TIstatus = QLabel('Status: ', self)
        self.ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self, channels2values={trg_prefix+':State-Sts': 1,
                                          trg_prefix+':Status-Mon': 0})
        self.ledmulti_TIStatus.setStyleSheet("""
            min-width:7.10em;\nmax-width:7.10em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.pb_trgdetails = QPushButton('Open details', self)
        self.pb_trgdetails.setStyleSheet("""
            min-width:7.10em;\nmax-width:7.10em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        util.connect_window(self.pb_trgdetails, HLTriggerDetailed, parent=self,
                            prefix=trg_prefix+':')
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(self.ledmulti_TIStatus)
        hlay_TIstatus.addWidget(self.pb_trgdetails)

        l_TIdelay = QLabel('Delay [us]: ', self)
        hlay_TIdelay = _create_propty_layout(
            parent=self, prefix=trg_prefix, propty='Delay',
            propty_type='sprb')

        flay = QFormLayout()
        flay.addRow(l_TIstatus, hlay_TIstatus)
        flay.addRow(l_TIdelay, hlay_TIdelay)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        return flay

    def _setupROISettingsLayout(self):
        label_ImgMaxWidth = QLabel('Maximum Width [pixels]: ', self)
        self.PyDMLabel_ImgMaxWidth = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxWidth-Cte')
        self.PyDMLabel_ImgMaxWidth.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_ImgMaxHeight = QLabel('Maximum Height [pixels]: ', self)
        self.PyDMLabel_ImgMaxHeight = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxHeight-Cte')
        self.PyDMLabel_ImgMaxHeight.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_ROIWidth = QLabel('Width [pixels]: ', self)
        hbox_ROIWidth = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIWidth',
            propty_type='sprb')

        label_ROIHeight = QLabel('Heigth [pixels]: ', self)
        hbox_ROIHeight = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIHeight',
            propty_type='sprb')

        label_ROIOffsetX = QLabel('Offset X [pixels]: ', self)
        hbox_ROIOffsetX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetX',
            propty_type='sprb')

        label_ROIOffsetY = QLabel('Offset Y [pixels]: ', self)
        hbox_ROIOffsetY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetY',
            propty_type='sprb')

        label_AutoCenterX = QLabel('Auto Center X: ', self)
        hbox_AutoCenterX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIAutoCenterX',
            propty_type='offon')

        label_AutoCenterY = QLabel('Auto Center Y: ', self)
        hbox_AutoCenterY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIAutoCenterY',
            propty_type='offon')

        flay = QFormLayout()
        flay.addRow(label_ImgMaxWidth, self.PyDMLabel_ImgMaxWidth)
        flay.addRow(label_ImgMaxHeight, self.PyDMLabel_ImgMaxHeight)
        flay.addRow(label_ROIWidth, hbox_ROIWidth)
        flay.addRow(label_ROIHeight, hbox_ROIHeight)
        flay.addRow(label_ROIOffsetX, hbox_ROIOffsetX)
        flay.addRow(label_ROIOffsetY, hbox_ROIOffsetY)
        flay.addRow(label_AutoCenterX, hbox_AutoCenterX)
        flay.addRow(label_AutoCenterY, hbox_AutoCenterY)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        return flay

    def _setupErrorMonLayout(self):
        label_CamTemp = QLabel('Temperature State: ', self)
        hbox_CamTempState = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamTempState',
            propty_type='mon')

        label_LastErr = QLabel('Last Error: ', self)
        hbox_LastErr = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamLastErr',
            propty_type='mon', cmd={'label': 'Clear Last Error',
                                    'pressValue': 1,
                                    'name': 'CamClearLastErr'})

        flay = QFormLayout()
        flay.addRow(label_CamTemp, hbox_CamTempState)
        flay.addRow(label_LastErr, hbox_LastErr)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay


class _ScrnCalibrationSettings(SiriusDialog):

    def __init__(self, parent=None, device=None, prefix=None):
        super().__init__(parent=parent)
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = self.prefix+self.device
        self.setWindowTitle('Screen Calibration')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>'+self.scrn_prefix+' Calibration</h3>', self,
                       alignment=Qt.AlignCenter)

        positioning = QGroupBox('Positioning', self)

        label_AcceptedErr = QLabel('Error Tolerance [mm]: ', self)
        hbox_AcceptedErr = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='AcceptedErr',
            propty_type='sprb')

        label_FluorScrnPos = QLabel('Fluorescent Screen Position [mm]: ', self)
        hbox_FluorScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='FluorScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetFluorScrnPos'})

        label_CalScrnPos = QLabel('Calibration Screen Position [mm]: ', self)
        hbox_CalScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CalScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetCalScrnPos'})

        label_NoneScrnPos = QLabel('Receded Screen Position [mm]: ', self)
        hbox_NoneScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='NoneScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetNoneScrnPos'})

        LED = QGroupBox('LED Brightness', self)

        label_LedPwrLvl = QLabel('Intensity [%]: ', self)
        hbox_LedPwrLvl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDPwrLvl',
            propty_type='sprb')

        label_LedPwrScaleFactor = QLabel('Power Scale Factor: ', self)
        hbox_LedPwrScaleFactor = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDPwrScaleFactor',
            propty_type='sprb')

        label_LedThold = QLabel('Voltage Threshold [V]: ', self)
        hbox_LedThold = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDThold',
            propty_type='sprb')

        Img = QGroupBox('Statistics Unit Conversion (Pixels→mm)', self)

        label_ImgScaleFactor = QLabel('Scale Factor: ', self)
        hbox_ImgScaleFactor = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgScaleFactor',
            propty_type='sprb')

        label_ImgCenterOffsetX = QLabel('Center Offset X: ', self)
        hbox_ImgCenterOffsetX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgCenterOffsetX',
            propty_type='sprb')

        label_ImgCenterOffsetY = QLabel('Center Offset Y: ', self)
        hbox_ImgCenterOffsetY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgCenterOffsetY',
            propty_type='sprb')

        positioning.setStyleSheet("""
            .QLabel{
                min-width:16em;\nmax-width:16em;
                qproperty-alignment: AlignRight;\n}""")
        LED.setStyleSheet("""
            .QLabel{
                min-width:11em;\nmax-width:11em;
                qproperty-alignment: AlignRight;\n}""")
        Img.setStyleSheet("""
            .QLabel{
                min-width:8em;\nmax-width:8em;
                qproperty-alignment: AlignRight;\n}""")

        flay_pos = QFormLayout()
        flay_pos.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_pos.addRow(label_AcceptedErr, hbox_AcceptedErr)
        flay_pos.addRow(label_FluorScrnPos, hbox_FluorScrnPos)
        flay_pos.addRow(label_CalScrnPos, hbox_CalScrnPos)
        flay_pos.addRow(label_NoneScrnPos, hbox_NoneScrnPos)
        flay_pos.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_pos.setLabelAlignment(Qt.AlignRight)
        flay_pos.setFormAlignment(Qt.AlignCenter)
        positioning.setLayout(flay_pos)

        flay_LED = QFormLayout()
        flay_LED.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_LED.addRow(label_LedPwrLvl, hbox_LedPwrLvl)
        flay_LED.addRow(label_LedPwrScaleFactor, hbox_LedPwrScaleFactor)
        flay_LED.addRow(label_LedThold, hbox_LedThold)
        flay_LED.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_LED.setLabelAlignment(Qt.AlignRight)
        flay_LED.setFormAlignment(Qt.AlignCenter)
        LED.setLayout(flay_LED)

        flay_Img = QFormLayout()
        flay_Img.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_Img.addRow(label_ImgScaleFactor, hbox_ImgScaleFactor)
        flay_Img.addRow(label_ImgCenterOffsetX, hbox_ImgCenterOffsetX)
        flay_Img.addRow(label_ImgCenterOffsetY, hbox_ImgCenterOffsetY)
        flay_Img.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_Img.setLabelAlignment(Qt.AlignRight)
        flay_Img.setFormAlignment(Qt.AlignCenter)
        Img.setLayout(flay_Img)

        vlay = QVBoxLayout()
        vlay.addWidget(label)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(positioning)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(LED)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(Img)
        self.setLayout(vlay)


def _create_propty_layout(parent, prefix, propty, propty_type, cmd=dict(),
                          layout='hbox', width=7.10, height=1.29):
    if layout == 'hbox':
        layout = QHBoxLayout()
    elif layout == 'vbox':
        layout = QVBoxLayout()

    if propty_type == 'sprb':
        setattr(parent, 'PyDMSpinbox_'+propty,
                PyDMSpinbox(parent=parent,
                            init_channel=prefix+':'+propty+'-SP'))
        spinbox = getattr(parent, 'PyDMSpinbox_'+propty)
        spinbox.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        spinbox.setAlignment(Qt.AlignCenter)
        spinbox.showStepExponent = False
        layout.addWidget(spinbox)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-RB'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'enbldisabl':
        setattr(parent, 'PyDMStateButton_'+propty,
                PyDMStateButton(parent=parent,
                                init_channel=prefix+':'+propty+'-Sel'))
        statebutton = getattr(parent, 'PyDMStateButton_'+propty)
        statebutton.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        statebutton.shape = 1
        layout.addWidget(statebutton)
        setattr(parent, 'SiriusLedState_'+propty,
                SiriusLedState(parent=parent,
                               init_channel=prefix+':'+propty+'-Sts'))
        led = getattr(parent, 'SiriusLedState_'+propty)
        led.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        led.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        layout.addWidget(led)
    elif propty_type == 'offon':
        setattr(parent, 'PyDMStateButton_'+propty,
                PyDMStateButton(parent=parent,
                                init_channel=prefix+':'+propty+'-Sel'))
        statebutton = getattr(parent, 'PyDMStateButton_'+propty)
        statebutton.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        statebutton.shape = 1
        layout.addWidget(statebutton)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Sts'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'enum':
        setattr(parent, 'PyDMEnumComboBox_'+propty,
                PyDMEnumComboBox(parent=parent,
                                 init_channel=prefix+':'+propty+'-Sel'))
        combobox = getattr(parent, 'PyDMEnumComboBox_'+propty)
        combobox.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        layout.addWidget(combobox)
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Sts'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    elif propty_type == 'mon':
        setattr(parent, 'PyDMLabel_'+propty,
                PyDMLabel(parent=parent,
                          init_channel=prefix+':'+propty+'-Mon'))
        label = getattr(parent, 'PyDMLabel_'+propty)
        label.setStyleSheet("""
            min-width:wvalem; max-width:wvalem; min-height:hvalem;
            max-height:hvalem;""".replace('wval', str(width)).replace(
            'hval', str(height)))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

    if cmd:
        setattr(parent, 'PyDMPushButton_'+propty,
                PyDMPushButton(parent=parent, label=cmd['label'],
                               pressValue=cmd['pressValue'],
                               init_channel=prefix+':'+cmd['name']+'-Cmd'))
        pb = getattr(parent, 'PyDMPushButton_'+propty)
        pb.setStyleSheet("""max-width:wvalem; max-height:hvalem;""".replace(
            'wval', str(width)).replace('hval', str(height)))
        layout.addWidget(pb)

    layout.setAlignment(Qt.AlignVCenter)

    return layout


if __name__ == '__main__':
    """Run test."""
    import os
    from siriushla.sirius_application import SiriusApplication

    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()
    util.set_style(app)

    centralwidget = QWidget()
    prefix = _vaca_prefix
    scrn_device = 'TB-01:DI-Scrn-1'
    cw = QWidget()
    scrn_view = SiriusScrnView(prefix=prefix, device=scrn_device)
    cb_scrntype = PyDMEnumComboBox(
        parent=cw, init_channel=prefix+scrn_device+':ScrnType-Sel')
    l_scrntype = PyDMLabel(
        parent=cw, init_channel=prefix+scrn_device+':ScrnType-Sts')
    led_movests = PyDMLed(
        parent=cw, init_channel=prefix+scrn_device+':DoneMov-Mon',
        color_list=[PyDMLed.LightGreen, PyDMLed.DarkGreen])
    led_movests.shape = 2
    led_movests.setStyleSheet("""min-height:1.29em; max-height:1.29em;""")

    lay = QGridLayout()
    lay.addWidget(QLabel('<h3>Screen View</h3>',
                         cw, alignment=Qt.AlignCenter), 0, 0, 1, 2)
    lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 1, 0)
    lay.addWidget(QLabel('Select Screen Type: ', cw,
                         alignment=Qt.AlignRight), 2, 0)
    lay.addWidget(cb_scrntype, 2, 1)
    lay.addWidget(l_scrntype, 2, 2)
    lay.addWidget(QLabel('Motor movement status: ', cw,
                         alignment=Qt.AlignRight), 3, 0)
    lay.addWidget(led_movests, 3, 1)

    lay.addItem(QSpacerItem(20, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 0)
    lay.addWidget(scrn_view, 5, 0, 1, 3)
    cw.setLayout(lay)

    window = SiriusMainWindow()
    window.setWindowTitle('Screen View: '+scrn_device)
    window.setCentralWidget(cw)
    window.show()
    sys.exit(app.exec_())
