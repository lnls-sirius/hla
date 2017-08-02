from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil
import os as _os
#import lnls as _lnls

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


def get_device_list(device_type):
    if device_type == 'bpm':
        devices = _read_devicename_file(bpm_fname)
    elif device_type == 'ch':
        devices = _read_devicename_file(ch_fname)
    elif device_type == 'cv':
        devices = _read_devicename_file(cv_fname)
    else:
        devices = None

    return devices


def add_header(table, header_opi):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")
    linkingContainer.setPropertyValue("opi_file", header_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)


def add_line(table, line_opi, device):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")
    linkingContainer.setPropertyValue("opi_file", line_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)
    children = linkingContainer.getChildren()

    for w in children:
        if w.getPropertyValue("widget_type") == "Boolean Button":
            button = w

    device_pv = prefix + device.upper() + sufix

    button.setPropertyValue("pv_name", device_pv)

device_type = PVUtil.getString(pvs[0]).lower()
devices = get_device_list(device_type)
if device_type == 'bpm':
    left_header_opi = "table/selection_table_bpm.opi"
    prefix = 'SIDI-'
    sufix = ''
elif device_type == 'ch':
    left_header_opi = "table/selection_table_ch.opi"
    prefix = 'SIPS-'
    sufix = '-SP'
elif device_type == 'cv':
    left_header_opi = "table/selection_table_cv.opi"
    prefix = 'SIPS-'
    sufix = '-SP'
up_header_opi          = "table/selection_table_up_header.opi"
low_header_opi         = "table/selection_table_low_header.opi"
line_opi               = "table/selection_table_line.opi"

table_container = display.getWidget("table_container")

if devices is None:
    table_container.setPropertyValue("visible", False)

else:
    # create table for family power supply
    add_header(table_container, up_header_opi)
    add_header(table_container, left_header_opi)
    selection_table = table_container.getWidget("selection_container")
    #selection_table.setPropertyValue("visible", False)
    # selection_table.removeAllChildren()
    add_line(selection_table, line_opi, devices[0])

    # # create table for device
    # length    = len(devices)
    # table_len = 20
    # table     = selection_table
    # for i in range(1,length+1):
    #     device = devices[i-1]
    #     add_line(table, line_opi, device)
    #     # if i == table_len and length > table_len:
    #     #     table = shunt_table_2
    #     #     add_header(table, header_opi)

    # # fam_table.performAutosize()
    # # shunt_table_1.performAutosize()
    # # shunt_table_2.performAutosize()
    # # table_container.setPropertyValue("visible", True)
    add_header(table_container, low_header_opi)
