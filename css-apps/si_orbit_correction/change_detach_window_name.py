from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

if PVUtil.getDouble(pvs[0]):
    selection_type = PVUtil.getString(pvs[1])
    #if selection_type in ['ch', 'cv', 'fch', 'fcv', 'qs']: selection_type = "Corrector"
    title = selection_type.upper() + ' Selection'
    window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
    window.getShell().setText(title)
pvs[0].setValue(0)
