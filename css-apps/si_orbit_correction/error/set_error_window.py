from org.csstudio.opibuilder.scriptUtil import PVUtil, ScriptUtil, DataUtil
from org.eclipse.ui import PlatformUI

## Get PV
error_type = PVUtil.getDouble(pvArray[0])

## Get Widgets
error_window = display.getWidget("Window")
error = error_window.getWidget("Error Type")
error_cause_1 = error_window.getWidget("Error Cause 1")
error_cause_2 = error_window.getWidget("Error Cause 2")

## Set Error Text
if error_type == 1:
        error.setPropertyValue("text", "Matrix measurent request could not be processed.")
	error_cause_1.setPropertyValue("text", "Automatic correction is running.")
elif error_type == 2:
        error.setPropertyValue("text", "Number of samples could not be set.")
	error_cause_1.setPropertyValue("text", "Value out of range. Maximun value is 100.")
elif error_type == 3:
        error.setPropertyValue("text", "Orbit average could not be calculated.")
	error_cause_1.setPropertyValue("text", "Orbit was not correctly read.")
elif error_type == 4:
        error.setPropertyValue("text", "Matrix could not be set.")
	error_cause_1.setPropertyValue("text", "Automatic correction is running.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 5:
        error.setPropertyValue("text", "Reference orbit could not be set.")
        error_cause_1.setPropertyValue("text", "Automatic correction is running.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 6:
        error.setPropertyValue("text","Automatic correction request could not be processed.")
	error_cause_1.setPropertyValue("text","Matrix measurement is running.")
elif error_type == 7:
        error.setPropertyValue("text","Response matrix register could not be set")
	error_cause_1.setPropertyValue("text","Automatic correction is running.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 8:
        error.setPropertyValue("text","Reference orbit register could not be set")
	error_cause_1.setPropertyValue("text","Automatic correction is running.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 9:
        error.setPropertyValue("text","Response matrix could not be update.")
	error_cause_1.setPropertyValue("text","Matrix with incorrect dimension.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 10:
        error.setPropertyValue("text","Referecence orbit could not be update.")
	error_cause_1.setPropertyValue("text","Orbit with incorrect dimension.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
elif error_type == 11:
        error.setPropertyValue("text","Device selection could not be processed.")
	error_cause_1.setPropertyValue("text","Device does not exist.")
        error_cause_2.setPropertyValue("text","SOFB must be off.")
elif error_type == 12:
        error.setPropertyValue("text","Correction kick is out of range.")
	error_cause_1.setPropertyValue("text","BPM removed from correction loop.")
elif error_type == 13:
        error.setPropertyValue("text","Correction weight could not be set.")
	error_cause_1.setPropertyValue("text","Value out of range. Maximun value is 100.")
        error_cause_2.setPropertyValue("text","SOFB must be off.")
elif error_type == 14:
        error.setPropertyValue("text","Mode parameter could not be set.")
        error_cause_1.setPropertyValue("text","SOFB must be off.")
elif error_type == 15:
	error.setPropertyValue("text","Manual correction request could not be processed.")
	error_cause_1.setPropertyValue("text","SOFB must be off.")
elif error_type == 16:
        error.setPropertyValue("text","Referecence orbit could not be update.")
	error_cause_1.setPropertyValue("text","Locked register.")
        error_cause_2.setPropertyValue("text", "Variables are being update.")
