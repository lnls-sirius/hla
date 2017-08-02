from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

WName = PVUtil.getString(pvs[0])
window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
window.getShell().setText(WName)

