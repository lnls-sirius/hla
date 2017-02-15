from org.csstudio.opibuilder.scriptUtil import PVUtil, ConsoleUtil
from org.eclipse.ui import PlatformUI

window_title = ['Warning']
windows = PlatformUI.getWorkbench().getWorkbenchWindows()
for w in windows:
    title = w.getShell().getText()
    if title in window_title:
        w.close()
