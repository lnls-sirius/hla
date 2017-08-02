from org.csstudio.opibuilder.scriptUtil import PVUtil, ScriptUtil, DataUtil
from org.eclipse.ui import PlatformUI

## Set OPI File
opi_file = "error/error_window.opi"

## Open OPI
if PVUtil.getDouble(pvArray[0]) != 0:
	ScriptUtil.openOPI(widget, opi_file, 2, None)


    