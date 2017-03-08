from org.csstudio.opibuilder.scriptUtil import PVUtil
from org.eclipse.ui import PlatformUI

import imp
import si_magnets_main
imp.reload(si_magnets_main)

def change_window_name(WName):
    window = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
    window.getShell().setText(WName)
    

WName = 'SI-Magnets'
change_window_name(WName)

