from org.csstudio.opibuilder.scriptUtil import PVUtil, ScriptUtil, GUIUtil     
from org.eclipse.ui import PlatformUI

opi_container = display.getWidget("opi_container")
linking_container = opi_container.getChild("linking_container")

if linking_container is not None:
    opi_file = linking_container.getPropertyValue("opi_file")
    opi_container.removeAllChildren()
    GUIUtil.compactMode()
    ScriptUtil.openOPI(widget, str(opi_file), 2, None)
    widget.getPV().setValue(1)


    