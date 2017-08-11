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
        Form.resize(845, 165)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.PyDMLbEventName = PyDMLabel(Form)
        self.PyDMLbEventName.setToolTip("")
        self.PyDMLbEventName.setWhatsThis("")
        self.PyDMLbEventName.setObjectName("PyDMLbEventName")
        self.horizontalLayout.addWidget(self.PyDMLbEventName)
        self.PyDMECBDelayType = PyDMEnumComboBox(Form)
        self.PyDMECBDelayType.setToolTip("")
        self.PyDMECBDelayType.setWhatsThis("")
        self.PyDMECBDelayType.setMaxVisibleItems(6)
        self.PyDMECBDelayType.setObjectName("PyDMECBDelayType")
        self.horizontalLayout.addWidget(self.PyDMECBDelayType)
        self.PyDMCheckbox = PyDMCheckbox(Form)
        self.PyDMCheckbox.setToolTip("")
        self.PyDMCheckbox.setWhatsThis("")
        self.PyDMCheckbox.setObjectName("PyDMCheckbox")
        self.horizontalLayout.addWidget(self.PyDMCheckbox)
        self.PyDMLbDelayType = PyDMLabel(Form)
        self.PyDMLbDelayType.setToolTip("")
        self.PyDMLbDelayType.setWhatsThis("")
        self.PyDMLbDelayType.setAlignment(QtCore.Qt.AlignCenter)
        self.PyDMLbDelayType.setObjectName("PyDMLbDelayType")
        self.horizontalLayout.addWidget(self.PyDMLbDelayType)
        self.PyDMLbDelay = PyDMLabel(Form)
        self.PyDMLbDelay.setToolTip("")
        self.PyDMLbDelay.setWhatsThis("")
        self.PyDMLbDelay.setPrecFromPV(True)
        self.PyDMLbDelay.setPrecision(3)
        self.PyDMLbDelay.setObjectName("PyDMLbDelay")
        self.horizontalLayout.addWidget(self.PyDMLbDelay)
        self.PyDMLed = PyDMLed(Form)
        self.PyDMLed.setToolTip("")
        self.PyDMLed.setWhatsThis("")
        self.PyDMLed.setObjectName("PyDMLed")
        self.horizontalLayout.addWidget(self.PyDMLed)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.PyDMLbEventName.setText(_translate("Form", "Event Name"))
        self.PyDMECBDelayType.setProperty("channel", _translate("Form", "ca://&PRE&Delaytype-Sel"))
        self.PyDMLbDelayType.setChannel(_translate("Form", "ca://&PRE&DelayType-Sts"))
        self.PyDMLbDelay.setText(_translate("Form", "Delay"))
        self.PyDMLbDelay.setChannel(_translate("Form", "ca://&PRE&Delay-RB"))

from pydm.widgets.checkbox import PyDMCheckbox
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.label import PyDMLabel
from pydm.widgets.led import PyDMLed
