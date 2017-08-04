# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'event.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(845, 56)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.PyDMLbEventName = PyDMLabel(Form)
        self.PyDMLbEventName.setToolTip("")
        self.PyDMLbEventName.setWhatsThis("")
        self.PyDMLbEventName.setObjectName("PyDMLbEventName")
        self.horizontalLayout.addWidget(self.PyDMLbEventName)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.PyDMEnumComboBox = PyDMEnumComboBox(Form)
        self.PyDMEnumComboBox.setToolTip("")
        self.PyDMEnumComboBox.setWhatsThis("")
        self.PyDMEnumComboBox.setObjectName("PyDMEnumComboBox")
        self.horizontalLayout.addWidget(self.PyDMEnumComboBox)
        self.PyDMLbMode = PyDMLabel(Form)
        self.PyDMLbMode.setToolTip("")
        self.PyDMLbMode.setWhatsThis("")
        self.PyDMLbMode.setObjectName("PyDMLbMode")
        self.horizontalLayout.addWidget(self.PyDMLbMode)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.PyDMECBDelayType = PyDMEnumComboBox(Form)
        self.PyDMECBDelayType.setToolTip("")
        self.PyDMECBDelayType.setWhatsThis("")
        self.PyDMECBDelayType.setObjectName("PyDMECBDelayType")
        self.horizontalLayout.addWidget(self.PyDMECBDelayType)
        self.PyDMLbDelayType = PyDMLabel(Form)
        self.PyDMLbDelayType.setToolTip("")
        self.PyDMLbDelayType.setWhatsThis("")
        self.PyDMLbDelayType.setObjectName("PyDMLbDelayType")
        self.horizontalLayout.addWidget(self.PyDMLbDelayType)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.PyDMSBDelay = PyDMSpinBox(Form)
        self.PyDMSBDelay.setToolTip("")
        self.PyDMSBDelay.setWhatsThis("")
        self.PyDMSBDelay.setDecimals(3)
        self.PyDMSBDelay.setObjectName("PyDMSBDelay")
        self.horizontalLayout.addWidget(self.PyDMSBDelay)
        self.PyDMLbDelay = PyDMLabel(Form)
        self.PyDMLbDelay.setToolTip("")
        self.PyDMLbDelay.setWhatsThis("")
        self.PyDMLbDelay.setPrecFromPV(True)
        self.PyDMLbDelay.setPrecision(3)
        self.PyDMLbDelay.setObjectName("PyDMLbDelay")
        self.horizontalLayout.addWidget(self.PyDMLbDelay)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.PyDMLbEventName.setText(_translate("Form", "Event Name"))
        self.PyDMEnumComboBox.setProperty("channel", _translate("Form", "ca://&PRE&Mode-Sel"))
        self.PyDMLbMode.setText(_translate("Form", "Continuous"))
        self.PyDMLbMode.setChannel(_translate("Form", "ca://&PRE&Mode-Sts"))
        self.PyDMECBDelayType.setProperty("channel", _translate("Form", "ca://&PRE&Delaytype-Sel"))
        self.PyDMLbDelayType.setChannel(_translate("Form", "ca://&PRE&DelayType-Sts"))
        self.PyDMSBDelay.setProperty("channel", _translate("Form", "ca://&PRE&Delay-SP"))
        self.PyDMLbDelay.setText(_translate("Form", "Delay"))
        self.PyDMLbDelay.setChannel(_translate("Form", "ca://&PRE&Delay-RB"))

from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
