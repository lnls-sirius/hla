from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI            

selection_type = PVUtil.getString(pvs[0]).capitalize()
if len(selection_type)>0:
    if selection_type == 'All':
        window_title = ['Quadrupole Power Supply', 'Sextupole Power Supply', 'Corrector Power Supply']
    else:
        window_title = [selection_type + ' Power Supply']
    windows = PlatformUI.getWorkbench().getWorkbenchWindows()
    for w in windows:
        title = w.getShell().getText()
        if title in window_title:
            w.close()