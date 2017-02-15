from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil

if widget.getVar('FirstTime') == None:
    widget.setVar('FirstTime', True)
else:
    selection_type = PVUtil.getString(pvs[0])
    #opi_name = "%s.opi"%selection_type
    opi_name = "selection.opi"
    widget.removeAllChildren()
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")
    linkingContainer.setPropertyValue("name", "linking_container")   
    linkingContainer.setPropertyValue("opi_file", opi_name)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 5)
    widget.addChildToBottom(linkingContainer)
    widget.performAutosize()
