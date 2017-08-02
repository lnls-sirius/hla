from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil
import os as _os

bpm_fname = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-bpm.txt')
ch_fname  = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-ch.txt')
cv_fname  = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-cv.txt')

def _read_devicename_file(filename):
    with open(filename, 'r') as fp:
        content = fp.read()
    content = content.splitlines()
    devicenames = []
    for line in content:
        line = line.strip()
        if not line or line[0] == '#': continue
        words = line.split()
        devicenames.append(words[0])
    return devicenames


def _get_device_list(device_type):
    if device_type == 'bpm':
        devices = _read_devicename_file(bpm_fname)
    elif device_type == 'ch':
        devices = _read_devicename_file(ch_fname)
    elif device_type == 'cv':
        devices = _read_devicename_file(cv_fname)
    else:
        devices = None
    return devices


def _add_line(table, line_opi, device):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")
    linkingContainer.setPropertyValue("opi_file", line_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)
    children = linkingContainer.getChildren()

    for w in children:
        if w.getPropertyValue("widget_type") == "Grouping Container":
            container = w
            button = container.getChildren()[0]
            led = container.getChildren()[1]

    setpoint = prefix + device.upper() + sufix
    readback = prefix + device.upper() + '-RB'

    button.setPropertyValue("pv_name", setpoint)
    led.setPropertyValue("pv_name", readback)

    macro_inputs = DataUtil.createMacrosInput(True)
    macro_inputs.put("device", device)
    macro_inputs.put("power_supply_sp", setpoint)
    macro_inputs.put("power_supply_rb", readback)
    linkingContainer.setPropertyValue("macros", macro_inputs)

device_type = PVUtil.getString(pvs[0]).lower()
devices = _get_device_list(device_type)
if device_type == 'bpm':
    prefix = 'SIDI-'
    sufix = ''
    column_len = 8
elif device_type == 'ch':
    prefix = 'SIPS-'
    sufix = '-SP'
    column_len = 6
elif device_type == 'cv':
    prefix = 'SIPS-'
    sufix = '-SP'
    column_len = 8
line_opi = "selection_table_line.opi"

table_container = display.getWidget("table_container")
selection_container = table_container.getWidget("selection_container")
children = selection_container.getChildren()
sec_container = []
for child in children:
    if child.getPropertyValue("widget_type") == "Grouping Container":
        sec_container.append(child)

if devices is None:
    selection_container.setPropertyValue("visible", False)

else:
    length = len(devices)
    cnt = 1
    column = sec_container[0]
    for i in range(1,length+1):
        device = devices[i-1]
        _add_line(column, line_opi, device)
        if i == cnt*column_len and len(devices) > column_len:
            if cnt != 20:
                column = sec_container[cnt]
                cnt = cnt + 1

    table_container.setPropertyValue("visible", True)
