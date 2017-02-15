from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil

def add_header(table, header_opi):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")
    linkingContainer.setPropertyValue("opi_file", header_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)

device_type = PVUtil.getString(pvs[0]).lower()
if device_type == 'bpm':
    left_header_opi = "table/selection_table_bpm.opi"
elif device_type == 'ch':
    left_header_opi = "table/selection_table_ch.opi"
elif device_type == 'cv':
    left_header_opi = "table/selection_table_cv.opi"
up_header_opi = "table/selection_table_up_header.opi"
low_header_opi = "table/selection_table_low_header.opi"

table_container = display.getWidget("table_container")

if device_type is None:
    table_container.setPropertyValue("visible", False)

else:
    add_header(table_container, up_header_opi)
    add_header(table_container, left_header_opi)
    add_header(table_container, low_header_opi)
