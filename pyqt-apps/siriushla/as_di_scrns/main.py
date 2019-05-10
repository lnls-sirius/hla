"""SiriusScrnView widget."""

import sys
import os
import time
from threading import Thread
from datetime import datetime
import numpy as np
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QFormLayout, \
                           QSpacerItem, QWidget, QGroupBox, QLabel, \
                           QComboBox, QPushButton, QCheckBox, QMessageBox, \
                           QSizePolicy as QSzPlcy, QSpinBox, QFileDialog
from qtpy.QtCore import Qt, Slot, Signal

from pydm.widgets import PyDMLabel, PyDMEnumComboBox

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.namesys import SiriusPVName

from siriushla import util
from siriushla.widgets import PyDMLed, SiriusConnectionSignal, SiriusMainWindow
from siriushla.as_di_scrns.base import \
    SiriusImageView as _SiriusImageView, \
    create_propty_layout as _create_propty_layout, \
    create_trigger_layout as _create_trigger_layout
from siriushla.as_di_scrns.scrn_details import \
    ScrnSettingsDetails as _ScrnSettingsDetails


class SiriusScrnView(QWidget):
    """
    Class to read Sirius screen cameras image data.

    To allow saving a grid correctly, control calibrationgrid_flag, which
    indicates if the screen is in calibration grid position.
    You can control it by using the method/Slot updateCalibrationGridFlag.
    """

    save_files = Signal()

    def __init__(self, parent=None, prefix=_vaca_prefix, device=None):
        """Initialize object."""
        QWidget.__init__(self, parent=parent)
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = self.prefix+self.device
        self._receivedData = False

        self.screen_type_conn = SiriusConnectionSignal(
            self.scrn_prefix+':ScrnType-Sts')
        self.screen_type_conn.new_value_signal.connect(
            self.updateCalibrationGridFlag)
        self._calibrationgrid_flag = self.screen_type_conn.getvalue()
        self.save_files.connect(self._saveGridLocalFiles)
        self.ch_ImgROIHeight = SiriusConnectionSignal(
            self.scrn_prefix+':ImgROIHeight-RB')
        self.ch_ImgROIWidth = SiriusConnectionSignal(
            self.scrn_prefix+':ImgROIWidth-RB')
        self.ch_ImgROIOffsetX = SiriusConnectionSignal(
            self.scrn_prefix+':ImgROIOffsetX-RB')
        self.ch_ImgROIOffsetY = SiriusConnectionSignal(
            self.scrn_prefix+':ImgROIOffsetY-RB')

        self._setupUi()
        self._loadCalibrationGrid(default=True)

    @property
    def calibrationgrid_flag(self):
        """Indicate if the screen device is in calibration grid position."""
        return self._calibrationgrid_flag

    @Slot(int)
    def updateCalibrationGridFlag(self, new_state):
        """Update calibrationgrid_flag property."""
        self._calibrationgrid_flag = new_state
        if new_state == 1:
            self.pushbutton_savegrid.setEnabled(True)
        else:
            self.pushbutton_savegrid.setEnabled(False)

    def _setupUi(self):
        self.setLayout(QGridLayout())
        self.layout().setHorizontalSpacing(10)
        self.layout().setVerticalSpacing(10)

        self.cameraview_widget = QWidget()
        self.cameraview_widget.setLayout(self._cameraviewLayout())
        self.layout().addWidget(self.cameraview_widget, 0, 0, 1, 2)

        self.settings_groupBox = QGroupBox('Settings', self)
        self.settings_groupBox.setLayout(self._settingsLayout())
        self.layout().addWidget(self.settings_groupBox, 1, 0, 5, 1)
        self.settings_groupBox.setStyleSheet("""
            .QLabel{
                min-width: 5em;}
            QLabel{
                qproperty-alignment: AlignCenter;}""")

        self.trigger_groupBox = QGroupBox('Trigger', self)
        self.trigger_groupBox.setLayout(self._triggerLayout())
        self.layout().addWidget(self.trigger_groupBox, 6, 0, 3, 1)

        self.statistics_groupBox = QGroupBox('Statistics', self)
        self.statistics_groupBox.setLayout(self._statisticsLayout())
        self.layout().addWidget(self.statistics_groupBox, 1, 1, 4, 1)
        self.statistics_groupBox.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Expanding)
        self.statistics_groupBox.setStyleSheet("""
            .QLabel{
                min-width:0.32em; max-width:0.32em;
                min-height:1.29em; max-height:1.29em;}
            QLabel{
                qproperty-alignment: AlignCenter;}
            PyDMWidget{
                min-width:4.84em; max-width:4.84em;
                min-height:1.29em; max-height:1.29em;}""")

        self.calibrationgrid_groupBox = QGroupBox('Calibration')
        self.calibrationgrid_groupBox.setLayout(self._calibrationgridLayout())
        self.calibrationgrid_groupBox.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Expanding)
        self.calibrationgrid_groupBox.layout().setAlignment(Qt.AlignHCenter)
        self.layout().addWidget(self.calibrationgrid_groupBox, 5, 1, 4, 1)

        self.layout().setRowStretch(0, 12)
        self.layout().setRowStretch(1, 1)
        self.layout().setRowStretch(2, 1)
        self.layout().setRowStretch(3, 1)
        self.layout().setRowStretch(4, 1)
        self.layout().setRowStretch(5, 1)
        self.layout().setRowStretch(6, 1)
        self.layout().setRowStretch(7, 1)
        self.layout().setRowStretch(8, 1)
        self.layout().setRowStretch(9, 1)

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
            #ScrnView{min-width:42em; min-height:32em;}""")
        self.image_view.failToSaveGrid.connect(self._showFailToSaveGridMsg)
        self.image_view.receivedData.connect(self._setReceivedDataFlag)

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
        self.pushbutton_loadgrid = QPushButton('Load', self)
        self.pushbutton_loadgrid.setStyleSheet("""
            min-width:4.36em;\nmax-width:4.36em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.pushbutton_loadgrid.clicked.connect(self._loadCalibrationGrid)
        hbox_grid = QHBoxLayout()
        hbox_grid.addWidget(self.checkBox_showgrid)
        hbox_grid.addWidget(self.pushbutton_savegrid)
        hbox_grid.addWidget(self.pushbutton_loadgrid)

        lb = QLabel('Show levels <')
        lb.setStyleSheet("""min-width:6em;max-width:6em;""")
        self.spinbox_gridfilterfactor = QSpinBox()
        self.spinbox_gridfilterfactor.setMaximum(100)
        self.spinbox_gridfilterfactor.setMinimum(0)
        self.spinbox_gridfilterfactor.setValue(
            self.image_view.calibration_grid_filterfactor)
        self.spinbox_gridfilterfactor.editingFinished.connect(
            self._setCalibrationGridFilterFactor)
        self.spinbox_gridfilterfactor.setStyleSheet("""
            min-width:4em;\nmax-width:4em;""")
        hbox_filter = QHBoxLayout()
        hbox_filter.setSpacing(0)
        hbox_filter.addWidget(lb)
        hbox_filter.addWidget(self.spinbox_gridfilterfactor)
        hbox_filter.addWidget(QLabel(' %'))

        lb = QLabel('Remove ')
        lb.setStyleSheet("""min-width:6em;max-width:6em;""")
        self.spinbox_removeborder = QSpinBox()
        self.spinbox_removeborder.setMaximum(512)
        self.spinbox_removeborder.setMinimum(0)
        self.spinbox_removeborder.setValue(
            self.image_view.calibration_grid_removeborder)
        self.spinbox_removeborder.editingFinished.connect(
            self._setCalibrationGridBorder2Remove)
        self.spinbox_removeborder.setStyleSheet("""
            min-width:4em; max-width:4em;""")
        hbox_remove = QHBoxLayout()
        hbox_remove.setSpacing(0)
        hbox_remove.addWidget(lb)
        hbox_remove.addWidget(self.spinbox_removeborder)
        hbox_remove.addWidget(QLabel(' px border'))

        hbox_EnblLED = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='EnblLED',
            propty_type='enbldisabl', width=4.68)

        lay = QFormLayout()
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Preferred))
        lay.addRow('     Grid: ', hbox_grid)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Preferred))
        lay.addRow('     ', hbox_filter)
        lay.addRow('     ', hbox_remove)
        lay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        lay.addRow('     LED: ', hbox_EnblLED)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Preferred))
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        return lay

    def _settingsLayout(self):
        label_CamEnbl = QLabel('Enable: ', self)
        hbox_CamEnbl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamEnbl',
            propty_type='enbldisabl')

        label_CamAcqPeriod = QLabel('Acquire\nPeriod [s]:', self)
        hbox_CamAcqPeriod = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqPeriod',
            propty_type='sprb')

        label_CamExposureTime = QLabel('Exposure\nTime [us]:', self)
        hbox_CamExposureTime = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureTime',
            propty_type='sprb')

        label_CamGain = QLabel('Gain[dB]:', self)
        hbox_CamGain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamGain',
            propty_type='sprb')
        hbox_AutoCamGain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='AutoGain',
            propty_type='', cmd={'label': 'Auto Gain',
                                 'pressValue': 1,
                                 'name': 'CamAutoGain'})

        cam_prefix = SiriusPVName(self.scrn_prefix).substitute(dev='ScrnCam')
        label_Reset = QLabel('Reset: ', self)
        hbox_Reset = _create_propty_layout(
            parent=self, prefix=cam_prefix, propty='Reset',
            cmd={'label': 'Reset', 'pressValue': 1, 'name': 'Rst'})

        self.pb_moreSettings = QPushButton('More settings...', self)
        self.pb_moreSettings.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Preferred)
        util.connect_window(self.pb_moreSettings, _ScrnSettingsDetails,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QFormLayout()
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(QLabel('<h4>Camera Acquisition</h4>', self))
        lay.addRow(label_CamEnbl, hbox_CamEnbl)
        lay.addRow(label_CamAcqPeriod, hbox_CamAcqPeriod)
        lay.addRow(label_CamExposureTime, hbox_CamExposureTime)
        lay.addRow(label_CamGain, hbox_CamGain)
        lay.addRow('', hbox_AutoCamGain)
        lay.addRow(label_Reset, hbox_Reset)
        lay.addRow('', self.pb_moreSettings)
        return lay

    def _triggerLayout(self):
        return _create_trigger_layout(
            parent=self, device=self.device, prefix=self.prefix)

    def _statisticsLayout(self):
        # - Method
        label_Method = QLabel('CalcMethod: ', self)
        label_Method.setStyleSheet("""min-width:6em;""")

        self.comboBox_Method = QComboBox(self)
        self.comboBox_Method.addItem('DimFei', 0)
        self.comboBox_Method.addItem('NDStats', 1)
        self.comboBox_Method.setCurrentIndex(0)
        self.comboBox_Method.setStyleSheet("""
            QComboBox::item {height: 1em;}
            QComboBox{min-width:6em;}""")
        self.comboBox_Method.currentIndexChanged.connect(
            self._handleShowStatistics)

        # - Centroid
        label_Centroid = QLabel('Centroid [mm]', self)
        label_Centroid.setStyleSheet("""min-width:15em;""")
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
        label_Sigma.setStyleSheet("""min-width:15em;""")
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
        label_Theta.setStyleSheet("""min-width:15em;""")
        label_i_Theta = QLabel('(', self)

        self.PyDMLabel_ThetaDimFei = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaDimFei-Mon')
        self.PyDMLabel_ThetaNDStats = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ThetaNDStats-Mon')
        self.PyDMLabel_ThetaNDStats.setVisible(False)

        label_f_Theta = QLabel(')', self)

        lay = QGridLayout()
        lay.addWidget(label_Method, 1, 1, 1, 2)
        lay.addWidget(self.comboBox_Method, 1, 4)
        lay.addItem(
            QSpacerItem(4, 2, QSzPlcy.Ignored, QSzPlcy.Preferred), 2, 2)
        lay.addWidget(label_Centroid, 3, 1, 1, 5, alignment=Qt.AlignCenter)
        lay.addWidget(label_i_Center, 4, 1)
        lay.addWidget(self.PyDMLabel_CenterXDimFei, 4, 2)
        lay.addWidget(self.PyDMLabel_CenterXNDStats, 4, 2)
        lay.addWidget(label_m_Center, 4, 3)
        lay.addWidget(self.PyDMLabel_CenterYDimFei, 4, 4)
        lay.addWidget(self.PyDMLabel_CenterYNDStats, 4, 4)
        lay.addWidget(label_f_Center, 4, 5)
        lay.addItem(
            QSpacerItem(4, 2, QSzPlcy.Ignored, QSzPlcy.Preferred), 5, 2)
        lay.addWidget(label_Sigma, 6, 1, 1, 5, alignment=Qt.AlignCenter)
        lay.addWidget(label_i_Sigma, 7, 1)
        lay.addWidget(self.PyDMLabel_SigmaXDimFei, 7, 2)
        lay.addWidget(self.PyDMLabel_SigmaXNDStats, 7, 2)
        lay.addWidget(label_m_Sigma, 7, 3)
        lay.addWidget(self.PyDMLabel_SigmaYDimFei, 7, 4)
        lay.addWidget(self.PyDMLabel_SigmaYNDStats, 7, 4)
        lay.addWidget(label_f_Sigma, 7, 5)
        lay.addItem(
            QSpacerItem(4, 2, QSzPlcy.Ignored, QSzPlcy.Preferred), 8, 2)
        lay.addWidget(label_Theta, 9, 1, 1, 5, alignment=Qt.AlignCenter)
        lay.addWidget(label_i_Theta, 10, 1)
        lay.addWidget(self.PyDMLabel_ThetaDimFei, 10, 2, 1, 3)
        lay.addWidget(self.PyDMLabel_ThetaNDStats, 10, 2, 1, 3)
        lay.addWidget(label_f_Theta, 10, 5)
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
        t = Thread(target=self._saveCalibrationGrid_thread, daemon=True)
        t.start()

    def _saveCalibrationGrid_thread(self):
        roi_h = float(self.ch_ImgROIHeight.value)
        roi_w = float(self.ch_ImgROIWidth.value)
        roi_offsetx = float(self.ch_ImgROIOffsetX.value)
        roi_offsety = float(self.ch_ImgROIOffsetY.value)

        # Disable camera acquisition and wait for disabling
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(0)
        state = self.SiriusLedState_CamEnbl.state
        while state == 1:
            time.sleep(0.1)
            state = self.SiriusLedState_CamEnbl.state

        # Change ROI to get entire image
        self.ch_ImgROIHeight.send_value_signal[float].emit(
            float(self.image_view.image_maxheight))
        self.ch_ImgROIWidth.send_value_signal[float].emit(
            float(self.image_view.image_maxwidth))
        self.ch_ImgROIOffsetX.send_value_signal[float].emit(0)
        self.ch_ImgROIOffsetY.send_value_signal[float].emit(0)

        # Enable led and wait for status
        self.PyDMStateButton_EnblLED.send_value_signal[int].emit(1)
        while not self.SiriusLedState_EnblLED.state:
            time.sleep(0.1)

        # Enable camera acquisition and wait for receiveing first frame
        self._receivedData = False
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(1)
        while not self._receivedData:
            time.sleep(0.1)

        # Save grid
        self.image_view.saveCalibrationGrid()

        # Disable camera acquisition and wait for disabling
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(0)
        state = self.SiriusLedState_CamEnbl.state
        while state == 1:
            time.sleep(0.1)
            state = self.SiriusLedState_CamEnbl.state

        # Change ROI to original size
        self.ch_ImgROIHeight.send_value_signal[float].emit(roi_h)
        self.ch_ImgROIWidth.send_value_signal[float].emit(roi_w)
        self.ch_ImgROIOffsetX.send_value_signal[float].emit(roi_offsetx)
        self.ch_ImgROIOffsetY.send_value_signal[float].emit(roi_offsety)

        # Enable camera acquisition
        self.PyDMStateButton_CamEnbl.send_value_signal[int].emit(1)

        # Enable showing saved grid
        time.sleep(0.1)
        self.checkBox_showgrid.setEnabled(True)
        self.save_files.emit()

    def _saveGridLocalFiles(self):
        home = os.path.expanduser('~')
        folder_month = datetime.now().strftime('%Y-%m')
        folder_day = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(
            home, 'Desktop', 'screens-iocs', folder_month, folder_day)
        if not os.path.exists(path):
            os.makedirs(path)
        fn, _ = QFileDialog.getSaveFileName(
            self, 'Save Grid As...', path + '/' + self.device +
            datetime.now().strftime('_%Y-%m-%d_%Hh%Mmin'), '*.npy')
        if not fn:
            return False

        path_default = os.path.join(
            home, 'Desktop', 'screens-iocs', 'default')
        if not os.path.exists(path_default):
            os.makedirs(path_default)
        fn_default = path_default + '/' + self.device

        grid = self.image_view.calibrationGrid
        width = self.image_view.imageWidth
        data = np.append(width, grid)
        np.save(fn, data)
        np.save(fn_default, data)

    def _loadCalibrationGrid(self, default=False):
        home = os.path.expanduser('~')
        if not default:
            folder_month = datetime.now().strftime('%Y-%m')
            path = os.path.join(
                home, 'Desktop', 'screens-iocs', folder_month)
            fn, _ = QFileDialog.getOpenFileName(
                self, 'Load Grid...', path, '*.npy')
            if not fn:
                return
        else:
            path = os.path.join(
                home, 'Desktop', 'screens-iocs', 'default')
            fn = path + '/' + self.device

        try:
            data = np.load(fn+'.npy')
            self.image_view.calibrationGrid = data
        except Exception:
            if not default:
                QMessageBox.critical(
                    self, 'Error',
                    'Could not load calibration grid from file '+fn,
                    QMessageBox.Ok)
            return

        # Enable showing saved grid
        self.checkBox_showgrid.setEnabled(True)

    def _setReceivedDataFlag(self):
        self._receivedData = True

    def _setCalibrationGridFilterFactor(self):
        self.image_view.set_calibration_grid_filterfactor(
            self.spinbox_gridfilterfactor.value())

    def _setCalibrationGridBorder2Remove(self):
        self.image_view.set_calibration_grid_border2remove(
            self.spinbox_removeborder.value())

    @Slot()
    def _showFailToSaveGridMsg(self):
        QMessageBox.warning(self, 'Warning',
                            'Could not save calibration grid!',
                            QMessageBox.Ok)


class IndividualScrn(SiriusMainWindow):
    """Individual Screen."""

    def __init__(self, parent=None, prefix=_vaca_prefix, scrn=''):
        """Init."""
        super().__init__(parent=parent)
        self._prefix = prefix
        self._scrn = scrn
        self._setupUi()

    def _setupUi(self):
        cw = QWidget()
        self.scrn_view = SiriusScrnView(prefix=self._prefix, device=self._scrn)
        self.cb_scrntype = PyDMEnumComboBox(
            parent=cw, init_channel=self._prefix+self._scrn+':ScrnType-Sel')
        self.l_scrntype = PyDMLabel(
            parent=cw, init_channel=self._prefix+self._scrn+':ScrnType-Sts')
        self.led_scrntype = PyDMLed(
            parent=cw, init_channel=self._prefix+self._scrn+':ScrnType-Sts',
            color_list=[PyDMLed.LightGreen, PyDMLed.Red, PyDMLed.Red,
                        PyDMLed.Yellow])
        self.led_scrntype.shape = 2

        lay = QGridLayout()
        lay.addWidget(QLabel('<h3>Screen View</h3>',
                             cw, alignment=Qt.AlignCenter), 0, 0, 1, 4)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(QLabel('Select Screen Type: ', cw,
                             alignment=Qt.AlignRight), 2, 0)
        lay.addWidget(self.cb_scrntype, 2, 1)
        lay.addWidget(self.l_scrntype, 2, 2)
        lay.addWidget(self.led_scrntype, 2, 3)

        lay.addItem(QSpacerItem(20, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 0)
        lay.addWidget(self.scrn_view, 5, 0, 1, 4)
        cw.setLayout(lay)

        self.setWindowTitle('Screen View: '+self._scrn)
        self.setCentralWidget(cw)


if __name__ == '__main__':
    """Run test."""
    from siriushla.sirius_application import SiriusApplication

    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()

    scrn = 'TB-01:DI-Scrn-1'
    window = IndividualScrn(None, prefix=_vaca_prefix, scrn=scrn)
    window.setWindowTitle('Screen View: '+scrn)
    window.show()
    sys.exit(app.exec_())
