# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(1630, 1064)
        MainWindow.setDockNestingEnabled(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.Orbit = QtWidgets.QWidget()
        self.Orbit.setObjectName("Orbit")
        self.gridLayout = QtWidgets.QGridLayout(self.Orbit)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.LB_Line2XStd = QtWidgets.QLabel(self.Orbit)
        self.LB_Line2XStd.setObjectName("LB_Line2XStd")
        self.gridLayout.addWidget(self.LB_Line2XStd, 0, 11, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.Orbit)
        self.label_23.setObjectName("label_23")
        self.gridLayout.addWidget(self.label_23, 2, 16, 1, 1)
        self.CB_Line1ShowYStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line1ShowYStat.setText("")
        self.CB_Line1ShowYStat.setChecked(True)
        self.CB_Line1ShowYStat.setObjectName("CB_Line1ShowYStat")
        self.gridLayout.addWidget(self.CB_Line1ShowYStat, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 18, 1, 1)
        self.CB_Line1Show = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line1Show.setText("")
        self.CB_Line1Show.setChecked(True)
        self.CB_Line1Show.setObjectName("CB_Line1Show")
        self.gridLayout.addWidget(self.CB_Line1Show, 5, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 13, 1, 1)
        self.CB_Line3ShowYStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line3ShowYStat.setText("")
        self.CB_Line3ShowYStat.setObjectName("CB_Line3ShowYStat")
        self.gridLayout.addWidget(self.CB_Line3ShowYStat, 2, 14, 1, 1)
        self.CB_Line1ShowXStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line1ShowXStat.setText("")
        self.CB_Line1ShowXStat.setChecked(True)
        self.CB_Line1ShowXStat.setObjectName("CB_Line1ShowXStat")
        self.gridLayout.addWidget(self.CB_Line1ShowXStat, 0, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.Orbit)
        self.label_20.setObjectName("label_20")
        self.gridLayout.addWidget(self.label_20, 2, 10, 1, 1)
        self.LB_Line1XStd = QtWidgets.QLabel(self.Orbit)
        self.LB_Line1XStd.setObjectName("LB_Line1XStd")
        self.gridLayout.addWidget(self.LB_Line1XStd, 0, 3, 1, 1)
        self.LB_Line3XAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line3XAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line3XAve.setObjectName("LB_Line3XAve")
        self.gridLayout.addWidget(self.LB_Line3XAve, 0, 15, 1, 1)
        self.LB_Line3YStd = QtWidgets.QLabel(self.Orbit)
        self.LB_Line3YStd.setObjectName("LB_Line3YStd")
        self.gridLayout.addWidget(self.LB_Line3YStd, 2, 17, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 4, 1, 1)
        self.LB_Line1YAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line1YAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line1YAve.setObjectName("LB_Line1YAve")
        self.gridLayout.addWidget(self.LB_Line1YAve, 2, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 2, 7, 1, 1)
        self.CB_Line2ShowYStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line2ShowYStat.setText("")
        self.CB_Line2ShowYStat.setObjectName("CB_Line2ShowYStat")
        self.gridLayout.addWidget(self.CB_Line2ShowYStat, 2, 8, 1, 1)
        self.LB_Line2YStd = QtWidgets.QLabel(self.Orbit)
        self.LB_Line2YStd.setObjectName("LB_Line2YStd")
        self.gridLayout.addWidget(self.LB_Line2YStd, 2, 11, 1, 1)
        self.LB_Line1YStd = QtWidgets.QLabel(self.Orbit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line1YStd.sizePolicy().hasHeightForWidth())
        self.LB_Line1YStd.setSizePolicy(sizePolicy)
        self.LB_Line1YStd.setObjectName("LB_Line1YStd")
        self.gridLayout.addWidget(self.LB_Line1YStd, 2, 3, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.Orbit)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 10, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.Orbit)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 0, 16, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.Orbit)
        self.label_19.setObjectName("label_19")
        self.gridLayout.addWidget(self.label_19, 2, 2, 1, 1)
        self.LB_Line2XAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line2XAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line2XAve.setObjectName("LB_Line2XAve")
        self.gridLayout.addWidget(self.LB_Line2XAve, 0, 9, 1, 1)
        self.GB_Line1 = QtWidgets.QGroupBox(self.Orbit)
        self.GB_Line1.setObjectName("GB_Line1")
        self.gridLayout_18 = QtWidgets.QGridLayout(self.GB_Line1)
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.PB_Line1Save = QtWidgets.QPushButton(self.GB_Line1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PB_Line1Save.sizePolicy().hasHeightForWidth())
        self.PB_Line1Save.setSizePolicy(sizePolicy)
        self.PB_Line1Save.setObjectName("PB_Line1Save")
        self.gridLayout_18.addWidget(self.PB_Line1Save, 6, 1, 1, 1)
        self.CB_Line1Orb = QtWidgets.QComboBox(self.GB_Line1)
        self.CB_Line1Orb.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line1Orb.sizePolicy().hasHeightForWidth())
        self.CB_Line1Orb.setSizePolicy(sizePolicy)
        self.CB_Line1Orb.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line1Orb.setObjectName("CB_Line1Orb")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.CB_Line1Orb.addItem("")
        self.gridLayout_18.addWidget(self.CB_Line1Orb, 0, 1, 1, 1)
        self.LB_Line1Orb = QtWidgets.QLabel(self.GB_Line1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line1Orb.sizePolicy().hasHeightForWidth())
        self.LB_Line1Orb.setSizePolicy(sizePolicy)
        self.LB_Line1Orb.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line1Orb.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line1Orb.setObjectName("LB_Line1Orb")
        self.gridLayout_18.addWidget(self.LB_Line1Orb, 0, 0, 1, 1)
        self.CB_Line1Ref = QtWidgets.QComboBox(self.GB_Line1)
        self.CB_Line1Ref.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line1Ref.sizePolicy().hasHeightForWidth())
        self.CB_Line1Ref.setSizePolicy(sizePolicy)
        self.CB_Line1Ref.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line1Ref.setObjectName("CB_Line1Ref")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.CB_Line1Ref.addItem("")
        self.gridLayout_18.addWidget(self.CB_Line1Ref, 2, 1, 3, 1)
        self.LB_Line1Ref = QtWidgets.QLabel(self.GB_Line1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line1Ref.sizePolicy().hasHeightForWidth())
        self.LB_Line1Ref.setSizePolicy(sizePolicy)
        self.LB_Line1Ref.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line1Ref.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line1Ref.setObjectName("LB_Line1Ref")
        self.gridLayout_18.addWidget(self.LB_Line1Ref, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.GB_Line1, 5, 1, 1, 4)
        self.LB_Line1XAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line1XAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line1XAve.setObjectName("LB_Line1XAve")
        self.gridLayout.addWidget(self.LB_Line1XAve, 0, 1, 1, 1)
        self.CB_Line2Show = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line2Show.setText("")
        self.CB_Line2Show.setObjectName("CB_Line2Show")
        self.gridLayout.addWidget(self.CB_Line2Show, 5, 8, 1, 1)
        self.LB_Line2YAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line2YAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line2YAve.setObjectName("LB_Line2YAve")
        self.gridLayout.addWidget(self.LB_Line2YAve, 2, 9, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 2, 12, 1, 1)
        self.LB_Line3YAve = QtWidgets.QLabel(self.Orbit)
        self.LB_Line3YAve.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line3YAve.setObjectName("LB_Line3YAve")
        self.gridLayout.addWidget(self.LB_Line3YAve, 2, 15, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.Orbit)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.CB_Line2ShowXStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line2ShowXStat.setText("")
        self.CB_Line2ShowXStat.setObjectName("CB_Line2ShowXStat")
        self.gridLayout.addWidget(self.CB_Line2ShowXStat, 0, 8, 1, 1)
        self.CB_Line3Show = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line3Show.setText("")
        self.CB_Line3Show.setObjectName("CB_Line3Show")
        self.gridLayout.addWidget(self.CB_Line3Show, 5, 14, 1, 1)
        self.LB_Line3XStd = QtWidgets.QLabel(self.Orbit)
        self.LB_Line3XStd.setObjectName("LB_Line3XStd")
        self.gridLayout.addWidget(self.LB_Line3XStd, 0, 17, 1, 1)
        self.CB_Line3ShowXStat = QtWidgets.QCheckBox(self.Orbit)
        self.CB_Line3ShowXStat.setText("")
        self.CB_Line3ShowXStat.setObjectName("CB_Line3ShowXStat")
        self.gridLayout.addWidget(self.CB_Line3ShowXStat, 0, 14, 1, 1)
        self.PyDMMWP_OrbitX = PyDMMultiWaveformPlot(self.Orbit)
        self.PyDMMWP_OrbitX.setToolTip("")
        self.PyDMMWP_OrbitX.setWhatsThis("")
        self.PyDMMWP_OrbitX.setFrameShape(QtWidgets.QFrame.NoFrame)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.PyDMMWP_OrbitX.setBackgroundBrush(brush)
        self.PyDMMWP_OrbitX.setTracesCount(15)
        self.PyDMMWP_OrbitX.setShowXGrid(True)
        self.PyDMMWP_OrbitX.setShowYGrid(True)
        self.PyDMMWP_OrbitX.setYAxis1ShowLabel(True)
        self.PyDMMWP_OrbitX.setTrace0Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_OrbitX.setTrace1Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_OrbitX.setTrace1Title("")
        self.PyDMMWP_OrbitX.setTrace2Symbol(BaseMultiPlot.NoSymbol)
        self.PyDMMWP_OrbitX.setTrace2Title("")
        self.PyDMMWP_OrbitX.setTrace3Title("")
        self.PyDMMWP_OrbitX.setTrace4Title("")
        self.PyDMMWP_OrbitX.setTrace6Title("")
        self.PyDMMWP_OrbitX.setTrace7Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_OrbitX.setTrace7Title("")
        self.PyDMMWP_OrbitX.setTrace8Title("")
        self.PyDMMWP_OrbitX.setTrace9Title("")
        self.PyDMMWP_OrbitX.setTrace10Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_OrbitX.setTrace11Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_OrbitX.setTrace11Title("")
        self.PyDMMWP_OrbitX.setTrace12Title("")
        self.PyDMMWP_OrbitX.setTrace13Title("")
        self.PyDMMWP_OrbitX.setTrace14Title("")
        self.PyDMMWP_OrbitX.setObjectName("PyDMMWP_OrbitX")
        self.gridLayout.addWidget(self.PyDMMWP_OrbitX, 1, 0, 1, 19)
        self.GB_Line2 = QtWidgets.QGroupBox(self.Orbit)
        self.GB_Line2.setObjectName("GB_Line2")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.GB_Line2)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.CB_Line2Orb = QtWidgets.QComboBox(self.GB_Line2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line2Orb.sizePolicy().hasHeightForWidth())
        self.CB_Line2Orb.setSizePolicy(sizePolicy)
        self.CB_Line2Orb.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line2Orb.setObjectName("CB_Line2Orb")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.CB_Line2Orb.addItem("")
        self.gridLayout_15.addWidget(self.CB_Line2Orb, 0, 2, 1, 1)
        self.LB_Line2Orb = QtWidgets.QLabel(self.GB_Line2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line2Orb.sizePolicy().hasHeightForWidth())
        self.LB_Line2Orb.setSizePolicy(sizePolicy)
        self.LB_Line2Orb.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line2Orb.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line2Orb.setObjectName("LB_Line2Orb")
        self.gridLayout_15.addWidget(self.LB_Line2Orb, 0, 1, 1, 1)
        self.LB_Line2Ref = QtWidgets.QLabel(self.GB_Line2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line2Ref.sizePolicy().hasHeightForWidth())
        self.LB_Line2Ref.setSizePolicy(sizePolicy)
        self.LB_Line2Ref.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line2Ref.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line2Ref.setObjectName("LB_Line2Ref")
        self.gridLayout_15.addWidget(self.LB_Line2Ref, 1, 1, 1, 1)
        self.CB_Line2Ref = QtWidgets.QComboBox(self.GB_Line2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line2Ref.sizePolicy().hasHeightForWidth())
        self.CB_Line2Ref.setSizePolicy(sizePolicy)
        self.CB_Line2Ref.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line2Ref.setObjectName("CB_Line2Ref")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.CB_Line2Ref.addItem("")
        self.gridLayout_15.addWidget(self.CB_Line2Ref, 1, 2, 1, 1)
        self.PB_LIne2Save = QtWidgets.QPushButton(self.GB_Line2)
        self.PB_LIne2Save.setObjectName("PB_LIne2Save")
        self.gridLayout_15.addWidget(self.PB_LIne2Save, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.GB_Line2, 5, 9, 1, 4)
        self.GB_Line3 = QtWidgets.QGroupBox(self.Orbit)
        self.GB_Line3.setObjectName("GB_Line3")
        self.gridLayout_16 = QtWidgets.QGridLayout(self.GB_Line3)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.CB_Line3Ref = QtWidgets.QComboBox(self.GB_Line3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line3Ref.sizePolicy().hasHeightForWidth())
        self.CB_Line3Ref.setSizePolicy(sizePolicy)
        self.CB_Line3Ref.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line3Ref.setObjectName("CB_Line3Ref")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.CB_Line3Ref.addItem("")
        self.gridLayout_16.addWidget(self.CB_Line3Ref, 1, 2, 1, 1)
        self.LB_Line3Orb = QtWidgets.QLabel(self.GB_Line3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line3Orb.sizePolicy().hasHeightForWidth())
        self.LB_Line3Orb.setSizePolicy(sizePolicy)
        self.LB_Line3Orb.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line3Orb.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line3Orb.setObjectName("LB_Line3Orb")
        self.gridLayout_16.addWidget(self.LB_Line3Orb, 0, 1, 1, 1)
        self.LB_Line3Ref = QtWidgets.QLabel(self.GB_Line3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Line3Ref.sizePolicy().hasHeightForWidth())
        self.LB_Line3Ref.setSizePolicy(sizePolicy)
        self.LB_Line3Ref.setMinimumSize(QtCore.QSize(60, 0))
        self.LB_Line3Ref.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_Line3Ref.setObjectName("LB_Line3Ref")
        self.gridLayout_16.addWidget(self.LB_Line3Ref, 1, 1, 1, 1)
        self.CB_Line3Orb = QtWidgets.QComboBox(self.GB_Line3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_Line3Orb.sizePolicy().hasHeightForWidth())
        self.CB_Line3Orb.setSizePolicy(sizePolicy)
        self.CB_Line3Orb.setMinimumSize(QtCore.QSize(0, 0))
        self.CB_Line3Orb.setMaxVisibleItems(10)
        self.CB_Line3Orb.setObjectName("CB_Line3Orb")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.CB_Line3Orb.addItem("")
        self.gridLayout_16.addWidget(self.CB_Line3Orb, 0, 2, 1, 1)
        self.PB_Line3Save = QtWidgets.QPushButton(self.GB_Line3)
        self.PB_Line3Save.setObjectName("PB_Line3Save")
        self.gridLayout_16.addWidget(self.PB_Line3Save, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.GB_Line3, 5, 15, 1, 4)
        self.PyDMMWP_Orbity = PyDMMultiWaveformPlot(self.Orbit)
        self.PyDMMWP_Orbity.setToolTip("")
        self.PyDMMWP_Orbity.setWhatsThis("")
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.PyDMMWP_Orbity.setBackgroundBrush(brush)
        self.PyDMMWP_Orbity.setTracesCount(15)
        self.PyDMMWP_Orbity.setShowXGrid(True)
        self.PyDMMWP_Orbity.setShowYGrid(True)
        self.PyDMMWP_Orbity.setXAxis1ShowLabel(True)
        self.PyDMMWP_Orbity.setYAxis1ShowLabel(True)
        self.PyDMMWP_Orbity.setTrace0Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace1Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace1Title("")
        self.PyDMMWP_Orbity.setTrace2Symbol(BaseMultiPlot.NoSymbol)
        self.PyDMMWP_Orbity.setTrace2Title("")
        self.PyDMMWP_Orbity.setTrace3Title("")
        self.PyDMMWP_Orbity.setTrace4Title("")
        self.PyDMMWP_Orbity.setTrace5Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace6Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace6Title("")
        self.PyDMMWP_Orbity.setTrace7Title("")
        self.PyDMMWP_Orbity.setTrace8Title("")
        self.PyDMMWP_Orbity.setTrace9Title("")
        self.PyDMMWP_Orbity.setTrace10Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace11Symbol(BaseMultiPlot.Circle)
        self.PyDMMWP_Orbity.setTrace11Title("")
        self.PyDMMWP_Orbity.setTrace12Title("")
        self.PyDMMWP_Orbity.setTrace13Title("")
        self.PyDMMWP_Orbity.setTrace14Title("")
        self.PyDMMWP_Orbity.setObjectName("PyDMMWP_Orbity")
        self.gridLayout.addWidget(self.PyDMMWP_Orbity, 3, 0, 1, 19)
        self.tabWidget.addTab(self.Orbit, "")
        self.Correctors = QtWidgets.QWidget()
        self.Correctors.setObjectName("Correctors")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.Correctors)
        self.gridLayout_14.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.PyDMMWP_CH = PyDMMultiWaveformPlot(self.Correctors)
        self.PyDMMWP_CH.setToolTip("")
        self.PyDMMWP_CH.setWhatsThis("")
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.PyDMMWP_CH.setBackgroundBrush(brush)
        self.PyDMMWP_CH.setObjectName("PyDMMWP_CH")
        self.gridLayout_14.addWidget(self.PyDMMWP_CH, 0, 0, 1, 1)
        self.PyDMMWP_CV = PyDMMultiWaveformPlot(self.Correctors)
        self.PyDMMWP_CV.setToolTip("")
        self.PyDMMWP_CV.setWhatsThis("")
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.PyDMMWP_CV.setBackgroundBrush(brush)
        self.PyDMMWP_CV.setObjectName("PyDMMWP_CV")
        self.gridLayout_14.addWidget(self.PyDMMWP_CV, 1, 0, 1, 1)
        self.tabWidget.addTab(self.Correctors, "")
        self.ResponseMatrix = QtWidgets.QWidget()
        self.ResponseMatrix.setObjectName("ResponseMatrix")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.ResponseMatrix)
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.PyDMPB_MeasMat = PyDMPushButton(self.ResponseMatrix)
        self.PyDMPB_MeasMat.setEnabled(True)
        self.PyDMPB_MeasMat.setToolTip("")
        self.PyDMPB_MeasMat.setObjectName("PyDMPB_MeasMat")
        self.gridLayout_6.addWidget(self.PyDMPB_MeasMat, 2, 1, 1, 1)
        self.PB_LoadRespMatrix = QtWidgets.QPushButton(self.ResponseMatrix)
        self.PB_LoadRespMatrix.setObjectName("PB_LoadRespMatrix")
        self.gridLayout_6.addWidget(self.PB_LoadRespMatrix, 2, 0, 1, 1)
        self.PyDMLB_MeasStatus = PyDMLabel(self.ResponseMatrix)
        self.PyDMLB_MeasStatus.setToolTip("")
        self.PyDMLB_MeasStatus.setWhatsThis("")
        self.PyDMLB_MeasStatus.setObjectName("PyDMLB_MeasStatus")
        self.gridLayout_6.addWidget(self.PyDMLB_MeasStatus, 4, 0, 1, 1)
        self.LB_NrSIngVals = QtWidgets.QLabel(self.ResponseMatrix)
        self.LB_NrSIngVals.setObjectName("LB_NrSIngVals")
        self.gridLayout_6.addWidget(self.LB_NrSIngVals, 5, 0, 1, 1)
        self.PyDMSB_NrSingVals = PyDMSpinBox(self.ResponseMatrix)
        self.PyDMSB_NrSingVals.setToolTip("")
        self.PyDMSB_NrSingVals.setWhatsThis("")
        self.PyDMSB_NrSingVals.setDecimals(0)
        self.PyDMSB_NrSingVals.setProperty("limitsFromPV", True)
        self.PyDMSB_NrSingVals.setObjectName("PyDMSB_NrSingVals")
        self.gridLayout_6.addWidget(self.PyDMSB_NrSingVals, 5, 1, 1, 1)
        self.PyDMPB_AbortMeas = PyDMPushButton(self.ResponseMatrix)
        self.PyDMPB_AbortMeas.setEnabled(True)
        self.PyDMPB_AbortMeas.setToolTip("")
        self.PyDMPB_AbortMeas.setObjectName("PyDMPB_AbortMeas")
        self.gridLayout_6.addWidget(self.PyDMPB_AbortMeas, 2, 2, 1, 1)
        self.PyDMMWP_SingVals = PyDMMultiWaveformPlot(self.ResponseMatrix)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.PyDMMWP_SingVals.sizePolicy().hasHeightForWidth())
        self.PyDMMWP_SingVals.setSizePolicy(sizePolicy)
        self.PyDMMWP_SingVals.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.PyDMMWP_SingVals.setToolTip("")
        self.PyDMMWP_SingVals.setWhatsThis("")
        self.PyDMMWP_SingVals.setObjectName("PyDMMWP_SingVals")
        self.gridLayout_6.addWidget(self.PyDMMWP_SingVals, 1, 0, 1, 4)
        self.PyDMIV_InvMatrix = PyDMImageView(self.ResponseMatrix)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.PyDMIV_InvMatrix.sizePolicy().hasHeightForWidth())
        self.PyDMIV_InvMatrix.setSizePolicy(sizePolicy)
        self.PyDMIV_InvMatrix.setToolTip("")
        self.PyDMIV_InvMatrix.setWhatsThis("")
        self.PyDMIV_InvMatrix.setObjectName("PyDMIV_InvMatrix")
        self.gridLayout_6.addWidget(self.PyDMIV_InvMatrix, 0, 2, 1, 2)
        self.PyDMIV_RespMatrix = PyDMImageView(self.ResponseMatrix)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.PyDMIV_RespMatrix.sizePolicy().hasHeightForWidth())
        self.PyDMIV_RespMatrix.setSizePolicy(sizePolicy)
        self.PyDMIV_RespMatrix.setToolTip("")
        self.PyDMIV_RespMatrix.setWhatsThis("")
        self.PyDMIV_RespMatrix.setObjectName("PyDMIV_RespMatrix")
        self.gridLayout_6.addWidget(self.PyDMIV_RespMatrix, 0, 0, 1, 2)
        self.PyDMLB_NrSingVals = PyDMLabel(self.ResponseMatrix)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLB_NrSingVals.sizePolicy().hasHeightForWidth())
        self.PyDMLB_NrSingVals.setSizePolicy(sizePolicy)
        self.PyDMLB_NrSingVals.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.PyDMLB_NrSingVals.setToolTip("")
        self.PyDMLB_NrSingVals.setWhatsThis("")
        self.PyDMLB_NrSingVals.setObjectName("PyDMLB_NrSingVals")
        self.gridLayout_6.addWidget(self.PyDMLB_NrSingVals, 5, 2, 1, 1)
        self.PyDMPB_ResetStatus = PyDMPushButton(self.ResponseMatrix)
        self.PyDMPB_ResetStatus.setEnabled(True)
        self.PyDMPB_ResetStatus.setToolTip("")
        self.PyDMPB_ResetStatus.setObjectName("PyDMPB_ResetStatus")
        self.gridLayout_6.addWidget(self.PyDMPB_ResetStatus, 4, 1, 1, 1)
        self.tabWidget.addTab(self.ResponseMatrix, "")
        self.BPMXList = QtWidgets.QWidget()
        self.BPMXList.setObjectName("BPMXList")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.BPMXList)
        self.gridLayout_11.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.SA_BPMXList = QtWidgets.QScrollArea(self.BPMXList)
        self.SA_BPMXList.setWidgetResizable(True)
        self.SA_BPMXList.setObjectName("SA_BPMXList")
        self.SACont_BPMXList = QtWidgets.QWidget()
        self.SACont_BPMXList.setGeometry(QtCore.QRect(0, 0, 1064, 887))
        self.SACont_BPMXList.setObjectName("SACont_BPMXList")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.SACont_BPMXList)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Widget_BPMXList = QtWidgets.QWidget(self.SACont_BPMXList)
        self.Widget_BPMXList.setStyleSheet("font: 16pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.Widget_BPMXList.setObjectName("Widget_BPMXList")
        self.verticalLayout_3.addWidget(self.Widget_BPMXList)
        self.SA_BPMXList.setWidget(self.SACont_BPMXList)
        self.gridLayout_11.addWidget(self.SA_BPMXList, 1, 0, 1, 1)
        self.PyDMPB_BPMXList = PyDMPushButton(self.BPMXList)
        self.PyDMPB_BPMXList.setToolTip("")
        self.PyDMPB_BPMXList.setObjectName("PyDMPB_BPMXList")
        self.gridLayout_11.addWidget(self.PyDMPB_BPMXList, 2, 0, 1, 1)
        self.LB_BPMXList = QtWidgets.QLabel(self.BPMXList)
        self.LB_BPMXList.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.LB_BPMXList.setAlignment(QtCore.Qt.AlignCenter)
        self.LB_BPMXList.setObjectName("LB_BPMXList")
        self.gridLayout_11.addWidget(self.LB_BPMXList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.BPMXList, "")
        self.Tab_BPMYList = QtWidgets.QWidget()
        self.Tab_BPMYList.setObjectName("Tab_BPMYList")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.Tab_BPMYList)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.SA_BPMYList = QtWidgets.QScrollArea(self.Tab_BPMYList)
        self.SA_BPMYList.setWidgetResizable(True)
        self.SA_BPMYList.setObjectName("SA_BPMYList")
        self.SACont_BPMYList = QtWidgets.QWidget()
        self.SACont_BPMYList.setGeometry(QtCore.QRect(0, 0, 1064, 887))
        self.SACont_BPMYList.setObjectName("SACont_BPMYList")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.SACont_BPMYList)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Widget_BPMYList = QtWidgets.QWidget(self.SACont_BPMYList)
        self.Widget_BPMYList.setStyleSheet("font: 16pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.Widget_BPMYList.setObjectName("Widget_BPMYList")
        self.verticalLayout_2.addWidget(self.Widget_BPMYList)
        self.SA_BPMYList.setWidget(self.SACont_BPMYList)
        self.gridLayout_5.addWidget(self.SA_BPMYList, 1, 0, 1, 1)
        self.PyDMPB_BPMYList = PyDMPushButton(self.Tab_BPMYList)
        self.PyDMPB_BPMYList.setToolTip("")
        self.PyDMPB_BPMYList.setObjectName("PyDMPB_BPMYList")
        self.gridLayout_5.addWidget(self.PyDMPB_BPMYList, 2, 0, 1, 1)
        self.LB_BPMYList = QtWidgets.QLabel(self.Tab_BPMYList)
        self.LB_BPMYList.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.LB_BPMYList.setAlignment(QtCore.Qt.AlignCenter)
        self.LB_BPMYList.setObjectName("LB_BPMYList")
        self.gridLayout_5.addWidget(self.LB_BPMYList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Tab_BPMYList, "")
        self.Tab_CHList = QtWidgets.QWidget()
        self.Tab_CHList.setObjectName("Tab_CHList")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.Tab_CHList)
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.SA_CHList = QtWidgets.QScrollArea(self.Tab_CHList)
        self.SA_CHList.setWidgetResizable(True)
        self.SA_CHList.setObjectName("SA_CHList")
        self.SACont_CHList = QtWidgets.QWidget()
        self.SACont_CHList.setGeometry(QtCore.QRect(0, 0, 1064, 887))
        self.SACont_CHList.setObjectName("SACont_CHList")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.SACont_CHList)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Widget_CHList = QtWidgets.QWidget(self.SACont_CHList)
        self.Widget_CHList.setStyleSheet("font: 16pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.Widget_CHList.setObjectName("Widget_CHList")
        self.verticalLayout_4.addWidget(self.Widget_CHList)
        self.SA_CHList.setWidget(self.SACont_CHList)
        self.gridLayout_12.addWidget(self.SA_CHList, 1, 0, 1, 1)
        self.PyDMPB_CHList = PyDMPushButton(self.Tab_CHList)
        self.PyDMPB_CHList.setToolTip("")
        self.PyDMPB_CHList.setObjectName("PyDMPB_CHList")
        self.gridLayout_12.addWidget(self.PyDMPB_CHList, 2, 0, 1, 1)
        self.LB_CHList = QtWidgets.QLabel(self.Tab_CHList)
        self.LB_CHList.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.LB_CHList.setAlignment(QtCore.Qt.AlignCenter)
        self.LB_CHList.setObjectName("LB_CHList")
        self.gridLayout_12.addWidget(self.LB_CHList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Tab_CHList, "")
        self.Tab_CVList = QtWidgets.QWidget()
        self.Tab_CVList.setObjectName("Tab_CVList")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.Tab_CVList)
        self.gridLayout_13.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.SA_CVList = QtWidgets.QScrollArea(self.Tab_CVList)
        self.SA_CVList.setWidgetResizable(True)
        self.SA_CVList.setObjectName("SA_CVList")
        self.SACont_CVList = QtWidgets.QWidget()
        self.SACont_CVList.setGeometry(QtCore.QRect(0, 0, 1064, 887))
        self.SACont_CVList.setObjectName("SACont_CVList")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.SACont_CVList)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Widget_CVList = QtWidgets.QWidget(self.SACont_CVList)
        self.Widget_CVList.setStyleSheet("font: 16pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.Widget_CVList.setObjectName("Widget_CVList")
        self.verticalLayout_5.addWidget(self.Widget_CVList)
        self.SA_CVList.setWidget(self.SACont_CVList)
        self.gridLayout_13.addWidget(self.SA_CVList, 1, 0, 1, 1)
        self.PyDMPB_CVList = PyDMPushButton(self.Tab_CVList)
        self.PyDMPB_CVList.setToolTip("")
        self.PyDMPB_CVList.setObjectName("PyDMPB_CVList")
        self.gridLayout_13.addWidget(self.PyDMPB_CVList, 2, 0, 1, 1)
        self.LB_CVList = QtWidgets.QLabel(self.Tab_CVList)
        self.LB_CVList.setStyleSheet("font: 20pt \"Sans Serif\";\n"
"font-weight: bold;")
        self.LB_CVList.setAlignment(QtCore.Qt.AlignCenter)
        self.LB_CVList.setObjectName("LB_CVList")
        self.gridLayout_13.addWidget(self.LB_CVList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Tab_CVList, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1630, 20))
        self.menubar.setObjectName("menubar")
        self.Menu_Open = QtWidgets.QMenu(self.menubar)
        self.Menu_Open.setObjectName("Menu_Open")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.DW_CorrParams = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DW_CorrParams.sizePolicy().hasHeightForWidth())
        self.DW_CorrParams.setSizePolicy(sizePolicy)
        self.DW_CorrParams.setFloating(False)
        self.DW_CorrParams.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.DW_CorrParams.setObjectName("DW_CorrParams")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.GBManCorr = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.GBManCorr.setObjectName("GBManCorr")
        self.GLManCorr = QtWidgets.QGridLayout(self.GBManCorr)
        self.GLManCorr.setObjectName("GLManCorr")
        self.PyDMPBApplyRF = PyDMPushButton(self.GBManCorr)
        self.PyDMPBApplyRF.setEnabled(True)
        self.PyDMPBApplyRF.setToolTip("")
        self.PyDMPBApplyRF.setObjectName("PyDMPBApplyRF")
        self.GLManCorr.addWidget(self.PyDMPBApplyRF, 2, 2, 1, 1)
        self.PyDMPBCalcKicks = PyDMPushButton(self.GBManCorr)
        self.PyDMPBCalcKicks.setEnabled(True)
        self.PyDMPBCalcKicks.setToolTip("")
        self.PyDMPBCalcKicks.setObjectName("PyDMPBCalcKicks")
        self.GLManCorr.addWidget(self.PyDMPBCalcKicks, 1, 0, 1, 3)
        self.PyDMPBApplyCV = PyDMPushButton(self.GBManCorr)
        self.PyDMPBApplyCV.setEnabled(True)
        self.PyDMPBApplyCV.setToolTip("")
        self.PyDMPBApplyCV.setObjectName("PyDMPBApplyCV")
        self.GLManCorr.addWidget(self.PyDMPBApplyCV, 2, 0, 1, 1)
        self.PyDMPBApplyCH = PyDMPushButton(self.GBManCorr)
        self.PyDMPBApplyCH.setEnabled(True)
        self.PyDMPBApplyCH.setToolTip("")
        self.PyDMPBApplyCH.setObjectName("PyDMPBApplyCH")
        self.GLManCorr.addWidget(self.PyDMPBApplyCH, 3, 0, 1, 1)
        self.PyDMPBApplyAll = PyDMPushButton(self.GBManCorr)
        self.PyDMPBApplyAll.setEnabled(True)
        self.PyDMPBApplyAll.setToolTip("")
        self.PyDMPBApplyAll.setObjectName("PyDMPBApplyAll")
        self.GLManCorr.addWidget(self.PyDMPBApplyAll, 3, 2, 1, 1)
        self.gridLayout_4.addWidget(self.GBManCorr, 6, 3, 1, 1)
        self.GB_Orbit = QtWidgets.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.GB_Orbit.sizePolicy().hasHeightForWidth())
        self.GB_Orbit.setSizePolicy(sizePolicy)
        self.GB_Orbit.setFlat(False)
        self.GB_Orbit.setCheckable(False)
        self.GB_Orbit.setObjectName("GB_Orbit")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.GB_Orbit)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.PyDMSB_NrAverages = PyDMSpinBox(self.GB_Orbit)
        self.PyDMSB_NrAverages.setToolTip("")
        self.PyDMSB_NrAverages.setWhatsThis("")
        self.PyDMSB_NrAverages.setDecimals(0)
        self.PyDMSB_NrAverages.setSingleStep(1.0)
        self.PyDMSB_NrAverages.setProperty("value", 1.0)
        self.PyDMSB_NrAverages.setProperty("limitsFromPV", True)
        self.PyDMSB_NrAverages.setObjectName("PyDMSB_NrAverages")
        self.horizontalLayout_21.addWidget(self.PyDMSB_NrAverages)
        self.PyDMLB_NrAverages = PyDMLabel(self.GB_Orbit)
        self.PyDMLB_NrAverages.setToolTip("")
        self.PyDMLB_NrAverages.setWhatsThis("")
        self.PyDMLB_NrAverages.setObjectName("PyDMLB_NrAverages")
        self.horizontalLayout_21.addWidget(self.PyDMLB_NrAverages)
        self.gridLayout_2.addLayout(self.horizontalLayout_21, 10, 1, 1, 1)
        self.horizontalLayout_22 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.LB_RefOrbit = QtWidgets.QLabel(self.GB_Orbit)
        self.LB_RefOrbit.setMinimumSize(QtCore.QSize(50, 0))
        self.LB_RefOrbit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_RefOrbit.setObjectName("LB_RefOrbit")
        self.horizontalLayout_22.addWidget(self.LB_RefOrbit)
        self.CB_RefOrbit = QtWidgets.QComboBox(self.GB_Orbit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_RefOrbit.sizePolicy().hasHeightForWidth())
        self.CB_RefOrbit.setSizePolicy(sizePolicy)
        self.CB_RefOrbit.setObjectName("CB_RefOrbit")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.CB_RefOrbit.addItem("")
        self.horizontalLayout_22.addWidget(self.CB_RefOrbit)
        self.gridLayout_2.addLayout(self.horizontalLayout_22, 7, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.GB_Orbit)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 9, 1, 1, 1)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.LB_OfflineOrbit = QtWidgets.QLabel(self.GB_Orbit)
        self.LB_OfflineOrbit.setMinimumSize(QtCore.QSize(50, 0))
        self.LB_OfflineOrbit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LB_OfflineOrbit.setObjectName("LB_OfflineOrbit")
        self.horizontalLayout_20.addWidget(self.LB_OfflineOrbit)
        self.CB_OffLineOrbit = QtWidgets.QComboBox(self.GB_Orbit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_OffLineOrbit.sizePolicy().hasHeightForWidth())
        self.CB_OffLineOrbit.setSizePolicy(sizePolicy)
        self.CB_OffLineOrbit.setObjectName("CB_OffLineOrbit")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.CB_OffLineOrbit.addItem("")
        self.horizontalLayout_20.addWidget(self.CB_OffLineOrbit)
        self.gridLayout_2.addLayout(self.horizontalLayout_20, 5, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.GB_Orbit)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 12, 1, 1, 1)
        self.horizontalLayout_183 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_183.setObjectName("horizontalLayout_183")
        self.PyDMSB_NrNeglected = PyDMSpinBox(self.GB_Orbit)
        self.PyDMSB_NrNeglected.setToolTip("")
        self.PyDMSB_NrNeglected.setWhatsThis("")
        self.PyDMSB_NrNeglected.setDecimals(0)
        self.PyDMSB_NrNeglected.setSingleStep(1.0)
        self.PyDMSB_NrNeglected.setProperty("limitsFromPV", True)
        self.PyDMSB_NrNeglected.setObjectName("PyDMSB_NrNeglected")
        self.horizontalLayout_183.addWidget(self.PyDMSB_NrNeglected)
        self.PyDMLB_NrNeglected = PyDMLabel(self.GB_Orbit)
        self.PyDMLB_NrNeglected.setToolTip("")
        self.PyDMLB_NrNeglected.setWhatsThis("")
        self.PyDMLB_NrNeglected.setObjectName("PyDMLB_NrNeglected")
        self.horizontalLayout_183.addWidget(self.PyDMLB_NrNeglected)
        self.gridLayout_2.addLayout(self.horizontalLayout_183, 13, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 11, 1, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem6, 8, 1, 1, 1)
        self.gridLayout_4.addWidget(self.GB_Orbit, 0, 3, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem7, 5, 3, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem8, 3, 3, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem9, 1, 3, 1, 1)
        self.GB_Correctors = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.GB_Correctors.setObjectName("GB_Correctors")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.GB_Correctors)
        self.gridLayout_9.setContentsMargins(9, -1, -1, 9)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.LB_CHStrength = QtWidgets.QLabel(self.GB_Correctors)
        self.LB_CHStrength.setObjectName("LB_CHStrength")
        self.gridLayout_9.addWidget(self.LB_CHStrength, 0, 1, 1, 1)
        self.PyDMLed_SyncKicks = PyDMLed(self.GB_Correctors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLed_SyncKicks.sizePolicy().hasHeightForWidth())
        self.PyDMLed_SyncKicks.setSizePolicy(sizePolicy)
        self.PyDMLed_SyncKicks.setToolTip("")
        self.PyDMLed_SyncKicks.setWhatsThis("")
        self.PyDMLed_SyncKicks.setObjectName("PyDMLed_SyncKicks")
        self.gridLayout_9.addWidget(self.PyDMLed_SyncKicks, 4, 4, 1, 1)
        self.PyDMSB_CVStrength = PyDMSpinBox(self.GB_Correctors)
        self.PyDMSB_CVStrength.setMaximumSize(QtCore.QSize(70, 30))
        self.PyDMSB_CVStrength.setWhatsThis("")
        self.PyDMSB_CVStrength.setMinimum(-1000.0)
        self.PyDMSB_CVStrength.setMaximum(1000.0)
        self.PyDMSB_CVStrength.setSingleStep(2.0)
        self.PyDMSB_CVStrength.setObjectName("PyDMSB_CVStrength")
        self.gridLayout_9.addWidget(self.PyDMSB_CVStrength, 1, 2, 1, 1)
        self.PyDMLed_RFEnbl = PyDMLed(self.GB_Correctors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLed_RFEnbl.sizePolicy().hasHeightForWidth())
        self.PyDMLed_RFEnbl.setSizePolicy(sizePolicy)
        self.PyDMLed_RFEnbl.setToolTip("")
        self.PyDMLed_RFEnbl.setWhatsThis("")
        self.PyDMLed_RFEnbl.setObjectName("PyDMLed_RFEnbl")
        self.gridLayout_9.addWidget(self.PyDMLed_RFEnbl, 6, 4, 1, 1)
        self.LB_CVStrength = QtWidgets.QLabel(self.GB_Correctors)
        self.LB_CVStrength.setObjectName("LB_CVStrength")
        self.gridLayout_9.addWidget(self.LB_CVStrength, 1, 1, 1, 1)
        self.PyDMCB_SyncKicks = PyDMCheckbox(self.GB_Correctors)
        self.PyDMCB_SyncKicks.setEnabled(False)
        self.PyDMCB_SyncKicks.setToolTip("")
        self.PyDMCB_SyncKicks.setWhatsThis("")
        self.PyDMCB_SyncKicks.setObjectName("PyDMCB_SyncKicks")
        self.gridLayout_9.addWidget(self.PyDMCB_SyncKicks, 4, 1, 1, 3)
        self.LB_RFStrength = QtWidgets.QLabel(self.GB_Correctors)
        self.LB_RFStrength.setObjectName("LB_RFStrength")
        self.gridLayout_9.addWidget(self.LB_RFStrength, 7, 1, 1, 1)
        self.PyDMLB_CVStrength = PyDMLabel(self.GB_Correctors)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLB_CVStrength.sizePolicy().hasHeightForWidth())
        self.PyDMLB_CVStrength.setSizePolicy(sizePolicy)
        self.PyDMLB_CVStrength.setWhatsThis("")
        self.PyDMLB_CVStrength.setObjectName("PyDMLB_CVStrength")
        self.gridLayout_9.addWidget(self.PyDMLB_CVStrength, 1, 3, 1, 2)
        self.PyDMSB_CHStrength = PyDMSpinBox(self.GB_Correctors)
        self.PyDMSB_CHStrength.setMaximumSize(QtCore.QSize(70, 30))
        self.PyDMSB_CHStrength.setWhatsThis("")
        self.PyDMSB_CHStrength.setMinimum(-1000.0)
        self.PyDMSB_CHStrength.setMaximum(1000.0)
        self.PyDMSB_CHStrength.setSingleStep(2.0)
        self.PyDMSB_CHStrength.setProperty("limitsFromPV", True)
        self.PyDMSB_CHStrength.setObjectName("PyDMSB_CHStrength")
        self.gridLayout_9.addWidget(self.PyDMSB_CHStrength, 0, 2, 1, 1)
        self.PyDMLB_CHStrength = PyDMLabel(self.GB_Correctors)
        self.PyDMLB_CHStrength.setWhatsThis("")
        self.PyDMLB_CHStrength.setObjectName("PyDMLB_CHStrength")
        self.gridLayout_9.addWidget(self.PyDMLB_CHStrength, 0, 3, 1, 2)
        self.PyDMCB_RFEnbl = PyDMCheckbox(self.GB_Correctors)
        self.PyDMCB_RFEnbl.setEnabled(False)
        self.PyDMCB_RFEnbl.setToolTip("")
        self.PyDMCB_RFEnbl.setWhatsThis("")
        self.PyDMCB_RFEnbl.setObjectName("PyDMCB_RFEnbl")
        self.gridLayout_9.addWidget(self.PyDMCB_RFEnbl, 6, 1, 1, 3)
        self.PyDMLB_RFStrength = PyDMLabel(self.GB_Correctors)
        self.PyDMLB_RFStrength.setWhatsThis("")
        self.PyDMLB_RFStrength.setObjectName("PyDMLB_RFStrength")
        self.gridLayout_9.addWidget(self.PyDMLB_RFStrength, 7, 3, 1, 2)
        self.PyDMSB_RFStrength = PyDMSpinBox(self.GB_Correctors)
        self.PyDMSB_RFStrength.setMaximumSize(QtCore.QSize(70, 30))
        self.PyDMSB_RFStrength.setWhatsThis("")
        self.PyDMSB_RFStrength.setMinimum(-1000.0)
        self.PyDMSB_RFStrength.setMaximum(1000.0)
        self.PyDMSB_RFStrength.setSingleStep(2.0)
        self.PyDMSB_RFStrength.setObjectName("PyDMSB_RFStrength")
        self.gridLayout_9.addWidget(self.PyDMSB_RFStrength, 7, 2, 1, 1)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem10, 5, 1, 1, 4)
        self.gridLayout_4.addWidget(self.GB_Correctors, 2, 3, 1, 1)
        self.GB_AutoCorr = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.GB_AutoCorr.setObjectName("GB_AutoCorr")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.GB_AutoCorr)
        self.gridLayout_7.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_7.setHorizontalSpacing(2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem11, 1, 0, 1, 4)
        self.PyDMSB_NrAverages_2 = PyDMSpinBox(self.GB_AutoCorr)
        self.PyDMSB_NrAverages_2.setToolTip("")
        self.PyDMSB_NrAverages_2.setWhatsThis("")
        self.PyDMSB_NrAverages_2.setDecimals(3)
        self.PyDMSB_NrAverages_2.setMaximum(400.0)
        self.PyDMSB_NrAverages_2.setSingleStep(1.0)
        self.PyDMSB_NrAverages_2.setProperty("value", 1.0)
        self.PyDMSB_NrAverages_2.setObjectName("PyDMSB_NrAverages_2")
        self.gridLayout_7.addWidget(self.PyDMSB_NrAverages_2, 8, 1, 1, 2)
        self.PyDMLE_AutoCorrFreq = PyDMLineEdit(self.GB_AutoCorr)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLE_AutoCorrFreq.sizePolicy().hasHeightForWidth())
        self.PyDMLE_AutoCorrFreq.setSizePolicy(sizePolicy)
        self.PyDMLE_AutoCorrFreq.setToolTip("")
        self.PyDMLE_AutoCorrFreq.setObjectName("PyDMLE_AutoCorrFreq")
        self.gridLayout_7.addWidget(self.PyDMLE_AutoCorrFreq, 4, 1, 1, 2)
        self.LB_AutoCorrFreq = QtWidgets.QLabel(self.GB_AutoCorr)
        self.LB_AutoCorrFreq.setObjectName("LB_AutoCorrFreq")
        self.gridLayout_7.addWidget(self.LB_AutoCorrFreq, 2, 1, 1, 3)
        self.label_17 = QtWidgets.QLabel(self.GB_AutoCorr)
        self.label_17.setObjectName("label_17")
        self.gridLayout_7.addWidget(self.label_17, 11, 0, 1, 4)
        self.PyDMLB_AutoCorrFreq = PyDMLabel(self.GB_AutoCorr)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLB_AutoCorrFreq.sizePolicy().hasHeightForWidth())
        self.PyDMLB_AutoCorrFreq.setSizePolicy(sizePolicy)
        self.PyDMLB_AutoCorrFreq.setToolTip("")
        self.PyDMLB_AutoCorrFreq.setWhatsThis("")
        self.PyDMLB_AutoCorrFreq.setPrecision(3)
        self.PyDMLB_AutoCorrFreq.setObjectName("PyDMLB_AutoCorrFreq")
        self.gridLayout_7.addWidget(self.PyDMLB_AutoCorrFreq, 4, 3, 1, 1)
        self.PyDMLB_NrAverages_3 = PyDMLabel(self.GB_AutoCorr)
        self.PyDMLB_NrAverages_3.setToolTip("")
        self.PyDMLB_NrAverages_3.setWhatsThis("")
        self.PyDMLB_NrAverages_3.setPrecision(3)
        self.PyDMLB_NrAverages_3.setObjectName("PyDMLB_NrAverages_3")
        self.gridLayout_7.addWidget(self.PyDMLB_NrAverages_3, 12, 3, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem12, 5, 1, 1, 3)
        self.PyDMLed_AutoCorr = PyDMLed(self.GB_AutoCorr)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMLed_AutoCorr.sizePolicy().hasHeightForWidth())
        self.PyDMLed_AutoCorr.setSizePolicy(sizePolicy)
        self.PyDMLed_AutoCorr.setToolTip("")
        self.PyDMLed_AutoCorr.setWhatsThis("")
        self.PyDMLed_AutoCorr.setObjectName("PyDMLed_AutoCorr")
        self.gridLayout_7.addWidget(self.PyDMLed_AutoCorr, 0, 3, 1, 1)
        self.PyDMCB_AutoCorr = PyDMCheckbox(self.GB_AutoCorr)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PyDMCB_AutoCorr.sizePolicy().hasHeightForWidth())
        self.PyDMCB_AutoCorr.setSizePolicy(sizePolicy)
        self.PyDMCB_AutoCorr.setToolTip("")
        self.PyDMCB_AutoCorr.setWhatsThis("")
        self.PyDMCB_AutoCorr.setAutoFillBackground(False)
        self.PyDMCB_AutoCorr.setChecked(False)
        self.PyDMCB_AutoCorr.setAutoExclusive(False)
        self.PyDMCB_AutoCorr.setObjectName("PyDMCB_AutoCorr")
        self.gridLayout_7.addWidget(self.PyDMCB_AutoCorr, 0, 2, 1, 1)
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem13, 9, 0, 1, 4)
        self.PyDMLB_NrAverages_2 = PyDMLabel(self.GB_AutoCorr)
        self.PyDMLB_NrAverages_2.setToolTip("")
        self.PyDMLB_NrAverages_2.setWhatsThis("")
        self.PyDMLB_NrAverages_2.setPrecision(3)
        self.PyDMLB_NrAverages_2.setObjectName("PyDMLB_NrAverages_2")
        self.gridLayout_7.addWidget(self.PyDMLB_NrAverages_2, 8, 3, 1, 1)
        self.PyDMSB_NrAverages_3 = PyDMSpinBox(self.GB_AutoCorr)
        self.PyDMSB_NrAverages_3.setToolTip("")
        self.PyDMSB_NrAverages_3.setWhatsThis("")
        self.PyDMSB_NrAverages_3.setDecimals(3)
        self.PyDMSB_NrAverages_3.setMaximum(5000.0)
        self.PyDMSB_NrAverages_3.setSingleStep(10.0)
        self.PyDMSB_NrAverages_3.setProperty("value", 200.0)
        self.PyDMSB_NrAverages_3.setObjectName("PyDMSB_NrAverages_3")
        self.gridLayout_7.addWidget(self.PyDMSB_NrAverages_3, 12, 1, 1, 2)
        self.label_16 = QtWidgets.QLabel(self.GB_AutoCorr)
        self.label_16.setObjectName("label_16")
        self.gridLayout_7.addWidget(self.label_16, 6, 1, 1, 3)
        self.gridLayout_4.addWidget(self.GB_AutoCorr, 4, 3, 1, 1)
        self.DW_CorrParams.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.DW_CorrParams)
        self.DW_OrbRegs = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.DW_OrbRegs.sizePolicy().hasHeightForWidth())
        self.DW_OrbRegs.setSizePolicy(sizePolicy)
        self.DW_OrbRegs.setFloating(False)
        self.DW_OrbRegs.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.DW_OrbRegs.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.DW_OrbRegs.setObjectName("DW_OrbRegs")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.SA_OrbRegs = QtWidgets.QScrollArea(self.dockWidgetContents_2)
        self.SA_OrbRegs.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.SA_OrbRegs.setWidgetResizable(True)
        self.SA_OrbRegs.setObjectName("SA_OrbRegs")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 254, 324))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents_3)
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.PB_Register0 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register0.setEnabled(True)
        self.PB_Register0.setAutoDefault(False)
        self.PB_Register0.setObjectName("PB_Register0")
        self.horizontalLayout_24.addWidget(self.PB_Register0)
        self.LB_Register0 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register0.sizePolicy().hasHeightForWidth())
        self.LB_Register0.setSizePolicy(sizePolicy)
        self.LB_Register0.setMouseTracking(True)
        self.LB_Register0.setAcceptDrops(True)
        self.LB_Register0.setObjectName("LB_Register0")
        self.horizontalLayout_24.addWidget(self.LB_Register0)
        self.verticalLayout.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.PB_Register1 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register1.setEnabled(True)
        self.PB_Register1.setAutoDefault(False)
        self.PB_Register1.setObjectName("PB_Register1")
        self.horizontalLayout_8.addWidget(self.PB_Register1)
        self.LB_Register1 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register1.sizePolicy().hasHeightForWidth())
        self.LB_Register1.setSizePolicy(sizePolicy)
        self.LB_Register1.setMouseTracking(True)
        self.LB_Register1.setAcceptDrops(True)
        self.LB_Register1.setText("")
        self.LB_Register1.setObjectName("LB_Register1")
        self.horizontalLayout_8.addWidget(self.LB_Register1)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.PB_Register2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register2.setEnabled(True)
        self.PB_Register2.setAutoDefault(False)
        self.PB_Register2.setObjectName("PB_Register2")
        self.horizontalLayout_9.addWidget(self.PB_Register2)
        self.LB_Register2 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register2.sizePolicy().hasHeightForWidth())
        self.LB_Register2.setSizePolicy(sizePolicy)
        self.LB_Register2.setText("")
        self.LB_Register2.setObjectName("LB_Register2")
        self.horizontalLayout_9.addWidget(self.LB_Register2)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.PB_Register3 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register3.setEnabled(True)
        self.PB_Register3.setAutoDefault(False)
        self.PB_Register3.setObjectName("PB_Register3")
        self.horizontalLayout_10.addWidget(self.PB_Register3)
        self.LB_Register3 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register3.sizePolicy().hasHeightForWidth())
        self.LB_Register3.setSizePolicy(sizePolicy)
        self.LB_Register3.setText("")
        self.LB_Register3.setObjectName("LB_Register3")
        self.horizontalLayout_10.addWidget(self.LB_Register3)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.PB_Register4 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register4.setEnabled(True)
        self.PB_Register4.setAutoDefault(False)
        self.PB_Register4.setObjectName("PB_Register4")
        self.horizontalLayout_11.addWidget(self.PB_Register4)
        self.LB_Register4 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register4.sizePolicy().hasHeightForWidth())
        self.LB_Register4.setSizePolicy(sizePolicy)
        self.LB_Register4.setText("")
        self.LB_Register4.setObjectName("LB_Register4")
        self.horizontalLayout_11.addWidget(self.LB_Register4)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.PB_Register5 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register5.setEnabled(True)
        self.PB_Register5.setAutoDefault(False)
        self.PB_Register5.setObjectName("PB_Register5")
        self.horizontalLayout_12.addWidget(self.PB_Register5)
        self.LB_Register5 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register5.sizePolicy().hasHeightForWidth())
        self.LB_Register5.setSizePolicy(sizePolicy)
        self.LB_Register5.setText("")
        self.LB_Register5.setObjectName("LB_Register5")
        self.horizontalLayout_12.addWidget(self.LB_Register5)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.PB_Register6 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register6.setEnabled(True)
        self.PB_Register6.setAutoDefault(False)
        self.PB_Register6.setObjectName("PB_Register6")
        self.horizontalLayout_13.addWidget(self.PB_Register6)
        self.LB_Register6 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register6.sizePolicy().hasHeightForWidth())
        self.LB_Register6.setSizePolicy(sizePolicy)
        self.LB_Register6.setText("")
        self.LB_Register6.setObjectName("LB_Register6")
        self.horizontalLayout_13.addWidget(self.LB_Register6)
        self.verticalLayout.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.PB_Register7 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register7.setEnabled(True)
        self.PB_Register7.setAutoDefault(False)
        self.PB_Register7.setObjectName("PB_Register7")
        self.horizontalLayout_14.addWidget(self.PB_Register7)
        self.LB_Register7 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register7.sizePolicy().hasHeightForWidth())
        self.LB_Register7.setSizePolicy(sizePolicy)
        self.LB_Register7.setText("")
        self.LB_Register7.setObjectName("LB_Register7")
        self.horizontalLayout_14.addWidget(self.LB_Register7)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.PB_Register8 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register8.setEnabled(True)
        self.PB_Register8.setAutoDefault(False)
        self.PB_Register8.setObjectName("PB_Register8")
        self.horizontalLayout_15.addWidget(self.PB_Register8)
        self.LB_Register8 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register8.sizePolicy().hasHeightForWidth())
        self.LB_Register8.setSizePolicy(sizePolicy)
        self.LB_Register8.setText("")
        self.LB_Register8.setObjectName("LB_Register8")
        self.horizontalLayout_15.addWidget(self.LB_Register8)
        self.verticalLayout.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.PB_Register9 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.PB_Register9.setEnabled(True)
        self.PB_Register9.setAutoDefault(False)
        self.PB_Register9.setObjectName("PB_Register9")
        self.horizontalLayout_16.addWidget(self.PB_Register9)
        self.LB_Register9 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_Register9.sizePolicy().hasHeightForWidth())
        self.LB_Register9.setSizePolicy(sizePolicy)
        self.LB_Register9.setText("")
        self.LB_Register9.setObjectName("LB_Register9")
        self.horizontalLayout_16.addWidget(self.LB_Register9)
        self.verticalLayout.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_17.addLayout(self.verticalLayout)
        self.SA_OrbRegs.setWidget(self.scrollAreaWidgetContents_3)
        self.gridLayout_8.addWidget(self.SA_OrbRegs, 0, 0, 1, 1)
        self.DW_OrbRegs.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.DW_OrbRegs)
        self.DW_IOCLog = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.DW_IOCLog.sizePolicy().hasHeightForWidth())
        self.DW_IOCLog.setSizePolicy(sizePolicy)
        self.DW_IOCLog.setFloating(False)
        self.DW_IOCLog.setObjectName("DW_IOCLog")
        self.dockWidgetContents_7 = QtWidgets.QWidget()
        self.dockWidgetContents_7.setObjectName("dockWidgetContents_7")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.dockWidgetContents_7)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.PyDMLL_IOCLog = PyDMLogLabel(self.dockWidgetContents_7)
        self.PyDMLL_IOCLog.setToolTip("")
        self.PyDMLL_IOCLog.setWhatsThis("")
        self.PyDMLL_IOCLog.setAlternatingRowColors(True)
        self.PyDMLL_IOCLog.setObjectName("PyDMLL_IOCLog")
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.PyDMLL_IOCLog.addItem(item)
        self.gridLayout_10.addWidget(self.PyDMLL_IOCLog, 0, 0, 1, 1)
        self.DW_IOCLog.setWidget(self.dockWidgetContents_7)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.DW_IOCLog)
        self.Action_openCorrParams = QtWidgets.QAction(MainWindow)
        self.Action_openCorrParams.setCheckable(True)
        self.Action_openCorrParams.setEnabled(True)
        self.Action_openCorrParams.setVisible(True)
        self.Action_openCorrParams.setObjectName("Action_openCorrParams")
        self.Action_openIOCLog = QtWidgets.QAction(MainWindow)
        self.Action_openIOCLog.setCheckable(True)
        self.Action_openIOCLog.setObjectName("Action_openIOCLog")
        self.Action_openOrbRegs = QtWidgets.QAction(MainWindow)
        self.Action_openOrbRegs.setCheckable(True)
        self.Action_openOrbRegs.setObjectName("Action_openOrbRegs")
        self.Action_openAll = QtWidgets.QAction(MainWindow)
        self.Action_openAll.setCheckable(True)
        self.Action_openAll.setChecked(True)
        self.Action_openAll.setObjectName("Action_openAll")
        self.Menu_Open.addAction(self.Action_openCorrParams)
        self.Menu_Open.addAction(self.Action_openIOCLog)
        self.Menu_Open.addAction(self.Action_openOrbRegs)
        self.Menu_Open.addAction(self.Action_openAll)
        self.menubar.addAction(self.Menu_Open.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.CB_Line2Orb.setCurrentIndex(1)
        self.CB_Line2Ref.setCurrentIndex(1)
        self.CB_Line3Ref.setCurrentIndex(1)
        self.CB_Line3Orb.setCurrentIndex(3)
        self.Action_openCorrParams.toggled['bool'].connect(self.DW_CorrParams.setVisible)
        self.DW_CorrParams.visibilityChanged['bool'].connect(self.Action_openCorrParams.setChecked)
        self.Action_openOrbRegs.toggled['bool'].connect(self.DW_OrbRegs.setVisible)
        self.DW_OrbRegs.visibilityChanged['bool'].connect(self.Action_openOrbRegs.setChecked)
        self.Action_openIOCLog.toggled['bool'].connect(self.DW_IOCLog.setVisible)
        self.DW_IOCLog.visibilityChanged['bool'].connect(self.Action_openIOCLog.setChecked)
        self.Action_openAll.toggled['bool'].connect(self.DW_CorrParams.setVisible)
        self.Action_openAll.toggled['bool'].connect(self.DW_IOCLog.setVisible)
        self.Action_openAll.toggled['bool'].connect(self.DW_OrbRegs.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.PyDMPBCalcKicks, self.PyDMPBApplyCV)
        MainWindow.setTabOrder(self.PyDMPBApplyCV, self.PyDMPBApplyRF)
        MainWindow.setTabOrder(self.PyDMPBApplyRF, self.PB_Register1)
        MainWindow.setTabOrder(self.PB_Register1, self.PB_Register2)
        MainWindow.setTabOrder(self.PB_Register2, self.PB_Register3)
        MainWindow.setTabOrder(self.PB_Register3, self.PB_Register4)
        MainWindow.setTabOrder(self.PB_Register4, self.PB_Register5)
        MainWindow.setTabOrder(self.PB_Register5, self.PB_Register6)
        MainWindow.setTabOrder(self.PB_Register6, self.PB_Register7)
        MainWindow.setTabOrder(self.PB_Register7, self.PB_Register8)
        MainWindow.setTabOrder(self.PB_Register8, self.PB_Register9)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Slow Orbit Feedback System"))
        self.LB_Line2XStd.setText(_translate("MainWindow", "TextLabel"))
        self.label_23.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.label_20.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.LB_Line1XStd.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line3XAve.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line3YStd.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line1YAve.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line2YStd.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line1YStd.setText(_translate("MainWindow", "TextLabel"))
        self.label_10.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.label_12.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.label_19.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.LB_Line2XAve.setText(_translate("MainWindow", "TextLabel"))
        self.GB_Line1.setTitle(_translate("MainWindow", "Line 1"))
        self.PB_Line1Save.setText(_translate("MainWindow", "Save"))
        self.CB_Line1Orb.setItemText(0, _translate("MainWindow", "SOFB Orbit"))
        self.CB_Line1Orb.setItemText(1, _translate("MainWindow", "Current Raw Orbit"))
        self.CB_Line1Orb.setItemText(2, _translate("MainWindow", "Register 0"))
        self.CB_Line1Orb.setItemText(3, _translate("MainWindow", "Register 1"))
        self.CB_Line1Orb.setItemText(4, _translate("MainWindow", "Register 2"))
        self.CB_Line1Orb.setItemText(5, _translate("MainWindow", "Register 3"))
        self.CB_Line1Orb.setItemText(6, _translate("MainWindow", "Register 4"))
        self.CB_Line1Orb.setItemText(7, _translate("MainWindow", "Register 5"))
        self.CB_Line1Orb.setItemText(8, _translate("MainWindow", "Register 6"))
        self.CB_Line1Orb.setItemText(9, _translate("MainWindow", "Register 7"))
        self.CB_Line1Orb.setItemText(10, _translate("MainWindow", "Register 8"))
        self.CB_Line1Orb.setItemText(11, _translate("MainWindow", "Register 9"))
        self.CB_Line1Orb.setItemText(12, _translate("MainWindow", "Zero"))
        self.LB_Line1Orb.setText(_translate("MainWindow", "show:"))
        self.CB_Line1Ref.setItemText(0, _translate("MainWindow", "SOFB Reference"))
        self.CB_Line1Ref.setItemText(1, _translate("MainWindow", "Register 0"))
        self.CB_Line1Ref.setItemText(2, _translate("MainWindow", "Register 1"))
        self.CB_Line1Ref.setItemText(3, _translate("MainWindow", "Register 2"))
        self.CB_Line1Ref.setItemText(4, _translate("MainWindow", "Register 3"))
        self.CB_Line1Ref.setItemText(5, _translate("MainWindow", "Register 4"))
        self.CB_Line1Ref.setItemText(6, _translate("MainWindow", "Register 5"))
        self.CB_Line1Ref.setItemText(7, _translate("MainWindow", "Register 6"))
        self.CB_Line1Ref.setItemText(8, _translate("MainWindow", "Register 7"))
        self.CB_Line1Ref.setItemText(9, _translate("MainWindow", "Register 8"))
        self.CB_Line1Ref.setItemText(10, _translate("MainWindow", "Register 9"))
        self.LB_Line1Ref.setText(_translate("MainWindow", "as diff to:"))
        self.LB_Line1XAve.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line2YAve.setText(_translate("MainWindow", "TextLabel"))
        self.LB_Line3YAve.setText(_translate("MainWindow", "TextLabel"))
        self.label_4.setText(_translate("MainWindow", "<html><head/><body><p>&#177;</p></body></html>"))
        self.LB_Line3XStd.setText(_translate("MainWindow", "TextLabel"))
        self.PyDMMWP_OrbitX.setYAxis1Label(_translate("MainWindow", "Horizontal Position [um]"))
        self.PyDMMWP_OrbitX.setTrace0Title(_translate("MainWindow", "Line 1"))
        self.PyDMMWP_OrbitX.setTrace5Title(_translate("MainWindow", "Line 2"))
        self.PyDMMWP_OrbitX.setTrace10Title(_translate("MainWindow", "Line 3"))
        self.GB_Line2.setTitle(_translate("MainWindow", "Line 2"))
        self.CB_Line2Orb.setItemText(0, _translate("MainWindow", "SOFB Orbit"))
        self.CB_Line2Orb.setItemText(1, _translate("MainWindow", "Current Raw Orbit"))
        self.CB_Line2Orb.setItemText(2, _translate("MainWindow", "Register 0"))
        self.CB_Line2Orb.setItemText(3, _translate("MainWindow", "Register 1"))
        self.CB_Line2Orb.setItemText(4, _translate("MainWindow", "Register 2"))
        self.CB_Line2Orb.setItemText(5, _translate("MainWindow", "Register 3"))
        self.CB_Line2Orb.setItemText(6, _translate("MainWindow", "Register 4"))
        self.CB_Line2Orb.setItemText(7, _translate("MainWindow", "Register 5"))
        self.CB_Line2Orb.setItemText(8, _translate("MainWindow", "Register 6"))
        self.CB_Line2Orb.setItemText(9, _translate("MainWindow", "Register 7"))
        self.CB_Line2Orb.setItemText(10, _translate("MainWindow", "Register 8"))
        self.CB_Line2Orb.setItemText(11, _translate("MainWindow", "Register 9"))
        self.CB_Line2Orb.setItemText(12, _translate("MainWindow", "Zero"))
        self.LB_Line2Orb.setText(_translate("MainWindow", "show:"))
        self.LB_Line2Ref.setText(_translate("MainWindow", "as diff to:"))
        self.CB_Line2Ref.setItemText(0, _translate("MainWindow", "SOFB Reference"))
        self.CB_Line2Ref.setItemText(1, _translate("MainWindow", "Register 0"))
        self.CB_Line2Ref.setItemText(2, _translate("MainWindow", "Register 1"))
        self.CB_Line2Ref.setItemText(3, _translate("MainWindow", "Register 2"))
        self.CB_Line2Ref.setItemText(4, _translate("MainWindow", "Register 3"))
        self.CB_Line2Ref.setItemText(5, _translate("MainWindow", "Register 4"))
        self.CB_Line2Ref.setItemText(6, _translate("MainWindow", "Register 5"))
        self.CB_Line2Ref.setItemText(7, _translate("MainWindow", "Register 6"))
        self.CB_Line2Ref.setItemText(8, _translate("MainWindow", "Register 7"))
        self.CB_Line2Ref.setItemText(9, _translate("MainWindow", "Register 8"))
        self.CB_Line2Ref.setItemText(10, _translate("MainWindow", "Register 9"))
        self.PB_LIne2Save.setText(_translate("MainWindow", "Save"))
        self.GB_Line3.setTitle(_translate("MainWindow", "Line 3"))
        self.CB_Line3Ref.setItemText(0, _translate("MainWindow", "SOFB Reference"))
        self.CB_Line3Ref.setItemText(1, _translate("MainWindow", "Register 0"))
        self.CB_Line3Ref.setItemText(2, _translate("MainWindow", "Register 1"))
        self.CB_Line3Ref.setItemText(3, _translate("MainWindow", "Register 2"))
        self.CB_Line3Ref.setItemText(4, _translate("MainWindow", "Register 3"))
        self.CB_Line3Ref.setItemText(5, _translate("MainWindow", "Register 4"))
        self.CB_Line3Ref.setItemText(6, _translate("MainWindow", "Register 5"))
        self.CB_Line3Ref.setItemText(7, _translate("MainWindow", "Register 6"))
        self.CB_Line3Ref.setItemText(8, _translate("MainWindow", "Register 7"))
        self.CB_Line3Ref.setItemText(9, _translate("MainWindow", "Register 8"))
        self.CB_Line3Ref.setItemText(10, _translate("MainWindow", "Register 9"))
        self.LB_Line3Orb.setText(_translate("MainWindow", "show:"))
        self.LB_Line3Ref.setText(_translate("MainWindow", "as diff to:"))
        self.CB_Line3Orb.setItemText(0, _translate("MainWindow", "SOFB Orbit"))
        self.CB_Line3Orb.setItemText(1, _translate("MainWindow", "Current Raw Orbit"))
        self.CB_Line3Orb.setItemText(2, _translate("MainWindow", "Register 0"))
        self.CB_Line3Orb.setItemText(3, _translate("MainWindow", "Register 1"))
        self.CB_Line3Orb.setItemText(4, _translate("MainWindow", "Register 2"))
        self.CB_Line3Orb.setItemText(5, _translate("MainWindow", "Register 3"))
        self.CB_Line3Orb.setItemText(6, _translate("MainWindow", "Register 4"))
        self.CB_Line3Orb.setItemText(7, _translate("MainWindow", "Register 5"))
        self.CB_Line3Orb.setItemText(8, _translate("MainWindow", "Register 6"))
        self.CB_Line3Orb.setItemText(9, _translate("MainWindow", "Register 7"))
        self.CB_Line3Orb.setItemText(10, _translate("MainWindow", "Register 8"))
        self.CB_Line3Orb.setItemText(11, _translate("MainWindow", "Register 9"))
        self.CB_Line3Orb.setItemText(12, _translate("MainWindow", "Zero"))
        self.PB_Line3Save.setText(_translate("MainWindow", "Save"))
        self.PyDMMWP_Orbity.setXAxis1Label(_translate("MainWindow", "Longitudinal Position [m]"))
        self.PyDMMWP_Orbity.setYAxis1Label(_translate("MainWindow", "Vertical Position [um]"))
        self.PyDMMWP_Orbity.setTrace0Title(_translate("MainWindow", "Line 1"))
        self.PyDMMWP_Orbity.setTrace5Title(_translate("MainWindow", "Line 2"))
        self.PyDMMWP_Orbity.setTrace10Title(_translate("MainWindow", "Line 3"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Orbit), _translate("MainWindow", "Orbit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Correctors), _translate("MainWindow", "Correctors"))
        self.PyDMPB_MeasMat.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPB_MeasMat.setText(_translate("MainWindow", "Measure Matrix"))
        self.PB_LoadRespMatrix.setText(_translate("MainWindow", "Load Matrix"))
        self.LB_NrSIngVals.setText(_translate("MainWindow", "Number of SVs:"))
        self.PyDMPB_AbortMeas.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPB_AbortMeas.setText(_translate("MainWindow", "Abort"))
        self.PyDMPB_ResetStatus.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPB_ResetStatus.setText(_translate("MainWindow", "Reset"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ResponseMatrix), _translate("MainWindow", "Response Matrix"))
        self.PyDMPB_BPMXList.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.LB_BPMXList.setText(_translate("MainWindow", "BPM X List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.BPMXList), _translate("MainWindow", "BPM X List"))
        self.PyDMPB_BPMYList.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.LB_BPMYList.setText(_translate("MainWindow", "BPM Y List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_BPMYList), _translate("MainWindow", "BPMYList"))
        self.PyDMPB_CHList.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.LB_CHList.setText(_translate("MainWindow", "CH List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_CHList), _translate("MainWindow", "CH List"))
        self.PyDMPB_CVList.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.LB_CVList.setText(_translate("MainWindow", "CV List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tab_CVList), _translate("MainWindow", "CV List"))
        self.Menu_Open.setTitle(_translate("MainWindow", "open"))
        self.DW_CorrParams.setWindowTitle(_translate("MainWindow", "Correction Parameters"))
        self.GBManCorr.setTitle(_translate("MainWindow", "Manual Correction"))
        self.PyDMPBApplyRF.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPBApplyRF.setText(_translate("MainWindow", "Apply RF"))
        self.PyDMPBCalcKicks.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPBCalcKicks.setText(_translate("MainWindow", "Calculate Kicks"))
        self.PyDMPBApplyCV.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPBApplyCV.setText(_translate("MainWindow", "Apply CV"))
        self.PyDMPBApplyCH.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPBApplyCH.setText(_translate("MainWindow", "Apply CH"))
        self.PyDMPBApplyAll.setWhatsThis(_translate("MainWindow", "\n"
"    Basic PushButton to send a fixed value.\n"
"\n"
"    The PyDMPushButton is meant to hold a specific value, and send that value\n"
"    to a channel when it is clicked, much like the MessageButton does in EDM.\n"
"    The PyDMPushButton works in two different modes of operation, first, a\n"
"    fixed value can be given to the :attr:`.pressValue` attribute, whenever the\n"
"    button is clicked a signal containing this value will be sent to the\n"
"    connected channel. This is the default behavior of the button. However, if\n"
"    the :attr:`.relativeChange` is set to True, the fixed value will be added\n"
"    to the current value of the channel. This means that the button will\n"
"    increment a channel by a fixed amount with every click, a consistent\n"
"    relative move\n"
"\n"
"    Parameters\n"
"    ----------\n"
"    pressValue : int, float, str\n"
"        Value to be sent when the button is clicked\n"
"\n"
"    channel : str\n"
"        ID of channel to manipulate\n"
"\n"
"    parent : QObject, optional\n"
"        Parent of PyDMPushButton\n"
"\n"
"    label : str, optional\n"
"        String to place on button\n"
"\n"
"    icon : QIcon, optional\n"
"        An Icon to display on the PyDMPushButton\n"
"\n"
"\n"
"    relative : bool, optional\n"
"        Choice to have the button peform a relative put, instead of always\n"
"        setting to an absolute value\n"
"    "))
        self.PyDMPBApplyAll.setText(_translate("MainWindow", "Apply All"))
        self.GB_Orbit.setTitle(_translate("MainWindow", "Oribt"))
        self.PyDMSB_NrAverages.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:OrbitAvgNum-SP"))
        self.PyDMLB_NrAverages.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:OrbitAvgNum-RB"))
        self.LB_RefOrbit.setText(_translate("MainWindow", "to:"))
        self.CB_RefOrbit.setItemText(0, _translate("MainWindow", "Register 0"))
        self.CB_RefOrbit.setItemText(1, _translate("MainWindow", "Register 1"))
        self.CB_RefOrbit.setItemText(2, _translate("MainWindow", "Register 2"))
        self.CB_RefOrbit.setItemText(3, _translate("MainWindow", "Register 3"))
        self.CB_RefOrbit.setItemText(4, _translate("MainWindow", "Register 4"))
        self.CB_RefOrbit.setItemText(5, _translate("MainWindow", "Register 5"))
        self.CB_RefOrbit.setItemText(6, _translate("MainWindow", "Register 6"))
        self.CB_RefOrbit.setItemText(7, _translate("MainWindow", "Register 7"))
        self.CB_RefOrbit.setItemText(8, _translate("MainWindow", "Register 8"))
        self.CB_RefOrbit.setItemText(9, _translate("MainWindow", "Register 9"))
        self.CB_RefOrbit.setItemText(10, _translate("MainWindow", "Zero"))
        self.label_13.setText(_translate("MainWindow", "Number of Averages:"))
        self.LB_OfflineOrbit.setText(_translate("MainWindow", "Correct:"))
        self.CB_OffLineOrbit.setItemText(0, _translate("MainWindow", "Current Orbit"))
        self.CB_OffLineOrbit.setItemText(1, _translate("MainWindow", "Register 0"))
        self.CB_OffLineOrbit.setItemText(2, _translate("MainWindow", "Register 1"))
        self.CB_OffLineOrbit.setItemText(3, _translate("MainWindow", "Register 2"))
        self.CB_OffLineOrbit.setItemText(4, _translate("MainWindow", "Register 3"))
        self.CB_OffLineOrbit.setItemText(5, _translate("MainWindow", "Register 4"))
        self.CB_OffLineOrbit.setItemText(6, _translate("MainWindow", "Register 5"))
        self.CB_OffLineOrbit.setItemText(7, _translate("MainWindow", "Register 6"))
        self.CB_OffLineOrbit.setItemText(8, _translate("MainWindow", "Register 7"))
        self.CB_OffLineOrbit.setItemText(9, _translate("MainWindow", "Register 8"))
        self.CB_OffLineOrbit.setItemText(10, _translate("MainWindow", "Register 9"))
        self.label_15.setText(_translate("MainWindow", "Number of neglected:"))
        self.PyDMSB_NrNeglected.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:OrbitNeglectNum-SP"))
        self.PyDMLB_NrNeglected.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:OrbitNeglectNum-RB"))
        self.GB_Correctors.setTitle(_translate("MainWindow", "Correctors"))
        self.LB_CHStrength.setText(_translate("MainWindow", "CH %:"))
        self.PyDMLed_SyncKicks.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:SyncKicks-Sts"))
        self.PyDMSB_CVStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Setpoint)"))
        self.PyDMSB_CVStrength.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:CVStrength-SP"))
        self.PyDMLed_RFEnbl.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:RFEnbl-Sts"))
        self.LB_CVStrength.setText(_translate("MainWindow", "CV %:"))
        self.PyDMCB_SyncKicks.setText(_translate("MainWindow", "Synchronized Kicks?"))
        self.PyDMCB_SyncKicks.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:SyncKicks-Sel"))
        self.LB_RFStrength.setText(_translate("MainWindow", "RF %:"))
        self.PyDMLB_CVStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Readback)"))
        self.PyDMLB_CVStrength.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:CVStrength-RB"))
        self.PyDMSB_CHStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Setpoint)"))
        self.PyDMSB_CHStrength.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:CHStrength-SP"))
        self.PyDMLB_CHStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Readback)"))
        self.PyDMLB_CHStrength.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:CHStrength-RB"))
        self.PyDMCB_RFEnbl.setText(_translate("MainWindow", "Use RF?"))
        self.PyDMCB_RFEnbl.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:RFEnbl-Sel"))
        self.PyDMLB_RFStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Readback)"))
        self.PyDMLB_RFStrength.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:RFStrength-RB"))
        self.PyDMSB_RFStrength.setToolTip(_translate("MainWindow", "Percentage to Apply (Setpoint)"))
        self.PyDMSB_RFStrength.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:RFStrength-SP"))
        self.GB_AutoCorr.setTitle(_translate("MainWindow", "Automatic Correction"))
        self.PyDMSB_NrAverages_2.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrMaxKick-SP"))
        self.PyDMLE_AutoCorrFreq.setWhatsThis(_translate("MainWindow", "\n"
"    Writeable text field to send and display channel values\n"
"    "))
        self.PyDMLE_AutoCorrFreq.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrFreq-SP"))
        self.LB_AutoCorrFreq.setText(_translate("MainWindow", "Frequency [Hz]:"))
        self.label_17.setText(_translate("MainWindow", "Maximum Distortion [um]"))
        self.PyDMLB_AutoCorrFreq.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrFreq-RB"))
        self.PyDMLB_NrAverages_3.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrMaxDist-RB"))
        self.PyDMLed_AutoCorr.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrState-Sts"))
        self.PyDMCB_AutoCorr.setText(_translate("MainWindow", "Auto Correction"))
        self.PyDMCB_AutoCorr.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrState-Sel"))
        self.PyDMLB_NrAverages_2.setChannel(_translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrMaxKick-RB"))
        self.PyDMSB_NrAverages_3.setProperty("channel", _translate("MainWindow", "ca://SI-Glob:AP-SOFB:AutoCorrMaxDist-SP"))
        self.label_16.setText(_translate("MainWindow", "Maximum Kick [urad]"))
        self.DW_OrbRegs.setWindowTitle(_translate("MainWindow", "Orbit Registers"))
        self.PB_Register0.setText(_translate("MainWindow", "Register 0"))
        self.LB_Register0.setText(_translate("MainWindow", "Golden Orbit"))
        self.PB_Register1.setText(_translate("MainWindow", "Register 1"))
        self.PB_Register2.setText(_translate("MainWindow", "Register 2"))
        self.PB_Register3.setText(_translate("MainWindow", "Register 3"))
        self.PB_Register4.setText(_translate("MainWindow", "Register 4"))
        self.PB_Register5.setText(_translate("MainWindow", "Register 5"))
        self.PB_Register6.setText(_translate("MainWindow", "Register 6"))
        self.PB_Register7.setText(_translate("MainWindow", "Register 7"))
        self.PB_Register8.setText(_translate("MainWindow", "Register 8"))
        self.PB_Register9.setText(_translate("MainWindow", "Register 9"))
        self.DW_IOCLog.setWindowTitle(_translate("MainWindow", "IOC Log"))
        __sortingEnabled = self.PyDMLL_IOCLog.isSortingEnabled()
        self.PyDMLL_IOCLog.setSortingEnabled(False)
        item = self.PyDMLL_IOCLog.item(0)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(1)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(2)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(3)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(4)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(5)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(6)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(7)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(8)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(9)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(10)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(11)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(12)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(13)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(14)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(15)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(16)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(17)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(18)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(19)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(20)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(21)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(22)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(23)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(24)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(25)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(26)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(27)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(28)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(29)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(30)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(31)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(32)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(33)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(34)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(35)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(36)
        item.setText(_translate("MainWindow", "a"))
        item = self.PyDMLL_IOCLog.item(37)
        item.setText(_translate("MainWindow", "a"))
        self.PyDMLL_IOCLog.setSortingEnabled(__sortingEnabled)
        self.Action_openCorrParams.setText(_translate("MainWindow", "Correction Parameters"))
        self.Action_openCorrParams.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.Action_openIOCLog.setText(_translate("MainWindow", "IOC Log"))
        self.Action_openIOCLog.setToolTip(_translate("MainWindow", "IOC Log"))
        self.Action_openOrbRegs.setText(_translate("MainWindow", "Orbit Registers"))
        self.Action_openAll.setText(_translate("MainWindow", "Open All"))
        self.Action_openAll.setToolTip(_translate("MainWindow", "Open all dockable windows"))

from pydm.widgets.basemultiplot import BaseMultiPlot
from pydm.widgets.checkbox import PyDMCheckbox
from pydm.widgets.image import PyDMImageView
from pydm.widgets.label import PyDMLabel
from pydm.widgets.led import PyDMLed
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.log_label import PyDMLogLabel
from pydm.widgets.multiwaveformplot import PyDMMultiWaveformPlot
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.spinbox import PyDMSpinBox
