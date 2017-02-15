from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

if PVUtil.getDouble(pvs[0]):
    magnet_type = PVUtil.getString(pvs[1])
    if magnet_type in ['ch', 'cv', 'fch', 'fcv', 'qs']: magnet_type = "Corrector"
    title = magnet_type.capitalize() + ' Power Supply'
    window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
    window.getShell().setText(title)
    pvs[0].setValue(0)
