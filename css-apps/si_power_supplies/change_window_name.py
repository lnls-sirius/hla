from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

magnet_type = PVUtil.getString(pvs[0]).capitalize()
title = magnet_type + ' Power Supply'
window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
window.getShell().setText(title)

