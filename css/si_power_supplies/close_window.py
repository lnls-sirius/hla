from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI            

magnet_type = PVUtil.getString(pvs[0]).capitalize()
if len(magnet_type)>0:
    if magnet_type == 'All':
        window_title = ['Quadrupole Power Supply', 'Sextupole Power Supply', 'Corrector Power Supply']
    else:
        window_title = [magnet_type + ' Power Supply']
    windows = PlatformUI.getWorkbench().getWorkbenchWindows()
    for w in windows:
        title = w.getShell().getText()
        if title in window_title:
            w.close()