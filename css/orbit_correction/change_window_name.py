from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

selection_type = PVUtil.getString(pvs[0]).upper()
title = selection_type + ' Selection'
window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
window.getShell().setText(title)

