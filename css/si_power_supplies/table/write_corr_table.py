from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil
import math

def get_power_supply_list(family):
    if family == 'CH':
        power_supplies = [
            "CH-01M1", "CH-01M2", "CH-01C1", "CH-01C2", "CH-01C3", 
            "CH-01C4", "CH-02M1", "CH-02M2", "CH-02C1", "CH-02C2", 
            "CH-02C3", "CH-02C4", "CH-03M1", "CH-03M2", "CH-03C1", 
            "CH-03C2", "CH-03C3", "CH-03C4", "CH-04M1", "CH-04M2", 
            "CH-04C1", "CH-04C2", "CH-04C3", "CH-04C4", "CH-05M1", 
            "CH-05M2", "CH-05C1", "CH-05C2", "CH-05C3", "CH-05C4", 
            "CH-06M1", "CH-06M2", "CH-06C1", "CH-06C2", "CH-06C3", 
            "CH-06C4", "CH-07M1", "CH-07M2", "CH-07C1", "CH-07C2", 
            "CH-07C3", "CH-07C4", "CH-08M1", "CH-08M2", "CH-08C1", 
            "CH-08C2", "CH-08C3", "CH-08C4", "CH-09M1", "CH-09M2", 
            "CH-09C1", "CH-09C2", "CH-09C3", "CH-09C4", "CH-10M1", 
            "CH-10M2", "CH-10C1", "CH-10C2", "CH-10C3", "CH-10C4", 
            "CH-11M1", "CH-11M2", "CH-11C1", "CH-11C2", "CH-11C3", 
            "CH-11C4", "CH-12M1", "CH-12M2", "CH-12C1", "CH-12C2", 
            "CH-12C3", "CH-12C4", "CH-13M1", "CH-13M2", "CH-13C1", 
            "CH-13C2", "CH-13C3", "CH-13C4", "CH-14M1", "CH-14M2", 
            "CH-14C1", "CH-14C2", "CH-14C3", "CH-14C4", "CH-15M1", 
            "CH-15M2", "CH-15C1", "CH-15C2", "CH-15C3", "CH-15C4", 
            "CH-16M1", "CH-16M2", "CH-16C1", "CH-16C2", "CH-16C3", 
            "CH-16C4", "CH-17M1", "CH-17M2", "CH-17C1", "CH-17C2", 
            "CH-17C3", "CH-17C4", "CH-18M1", "CH-18M2", "CH-18C1", 
            "CH-18C2", "CH-18C3", "CH-18C4", "CH-19M1", "CH-19M2", 
            "CH-19C1", "CH-19C2", "CH-19C3", "CH-19C4", "CH-20M1", 
            "CH-20M2", "CH-20C1", "CH-20C2", "CH-20C3", "CH-20C4", 
            ]
        
    elif family == 'CV':
        power_supplies = [
            "CV-01M1",
            "CV-01M2",   "CV-01C1",   "CV-01C2-A", "CV-01C2-B", "CV-01C3-A", 
            "CV-01C3-B", "CV-01C4",   "CV-02M1",   "CV-02M2",   "CV-02C1", 
            "CV-02C2-A", "CV-02C2-B", "CV-02C3-A", "CV-02C3-B", "CV-02C4", 
            "CV-03M1",   "CV-03M2",   "CV-03C1",   "CV-03C2-A", "CV-03C2-B", 
            "CV-03C3-A", "CV-03C3-B", "CV-03C4",   "CV-04M1",   "CV-04M2", 
            "CV-04C1",   "CV-04C2-A", "CV-04C2-B", "CV-04C3-A", "CV-04C3-B", 
            "CV-04C4",   "CV-05M1",   "CV-05M2",   "CV-05C1",   "CV-05C2-A", 
            "CV-05C2-B", "CV-05C3-A", "CV-05C3-B", "CV-05C4",   "CV-06M1", 
            "CV-06M2",   "CV-06C1",   "CV-06C2-A", "CV-06C2-B", "CV-06C3-A", 
            "CV-06C3-B", "CV-06C4",   "CV-07M1",   "CV-07M2",   "CV-07C1", 
            "CV-07C2-A", "CV-07C2-B", "CV-07C3-A", "CV-07C3-B", "CV-07C4", 
            "CV-08M1",   "CV-08M2",   "CV-08C1",   "CV-08C2-A", "CV-08C2-B", 
            "CV-08C3-A", "CV-08C3-B", "CV-08C4",   "CV-09M1",   "CV-09M2", 
            "CV-09C1",   "CV-09C2-A", "CV-09C2-B", "CV-09C3-A", "CV-09C3-B", 
            "CV-09C4",   "CV-10M1",   "CV-10M2",   "CV-10C1",   "CV-10C2-A", 
            "CV-10C2-B", "CV-10C3-A", "CV-10C3-B", "CV-10C4",   "CV-11M1", 
            "CV-11M2",   "CV-11C1",   "CV-11C2-A", "CV-11C2-B", "CV-11C3-A", 
            "CV-11C3-B", "CV-11C4",   "CV-12M1",   "CV-12M2",   "CV-12C1", 
            "CV-12C2-A", "CV-12C2-B", "CV-12C3-A", "CV-12C3-B", "CV-12C4", 
            "CV-13M1",   "CV-13M2",   "CV-13C1",   "CV-13C2-A", "CV-13C2-B", 
            "CV-13C3-A", "CV-13C3-B", "CV-13C4",   "CV-14M1",   "CV-14M2", 
            "CV-14C1",   "CV-14C2-A", "CV-14C2-B", "CV-14C3-A", "CV-14C3-B", 
            "CV-14C4",   "CV-15M1",   "CV-15M2",   "CV-15C1",   "CV-15C2-A", 
            "CV-15C2-B", "CV-15C3-A", "CV-15C3-B", "CV-15C4",   "CV-16M1", 
            "CV-16M2",   "CV-16C1",   "CV-16C2-A", "CV-16C2-B", "CV-16C3-A", 
            "CV-16C3-B", "CV-16C4",   "CV-17M1",   "CV-17M2",   "CV-17C1", 
            "CV-17C2-A", "CV-17C2-B", "CV-17C3-A", "CV-17C3-B", "CV-17C4", 
            "CV-18M1",   "CV-18M2",   "CV-18C1",   "CV-18C2-A", "CV-18C2-B", 
            "CV-18C3-A", "CV-18C3-B", "CV-18C4",   "CV-19M1",   "CV-19M2", 
            "CV-19C1",   "CV-19C2-A", "CV-19C2-B", "CV-19C3-A", "CV-19C3-B", 
            "CV-19C4",   "CV-20M1",   "CV-20M2",   "CV-20C1",   "CV-20C2-A", 
            "CV-20C2-B", "CV-20C3-A", "CV-20C3-B", "CV-20C4",   
            ]
    elif family == 'FCH':
        power_supplies = [
            "FCH-01M1",
            "FCH-01M2", "FCH-01C2", "FCH-01C3", "FCH-02M1", "FCH-02M2", 
            "FCH-02C2", "FCH-02C3", "FCH-03M1", "FCH-03M2", "FCH-03C2", 
            "FCH-03C3", "FCH-04M1", "FCH-04M2", "FCH-04C2", "FCH-04C3", 
            "FCH-05M1", "FCH-05M2", "FCH-05C2", "FCH-05C3", "FCH-06M1", 
            "FCH-06M2", "FCH-06C2", "FCH-06C3", "FCH-07M1", "FCH-07M2", 
            "FCH-07C2", "FCH-07C3", "FCH-08M1", "FCH-08M2", "FCH-08C2", 
            "FCH-08C3", "FCH-09M1", "FCH-09M2", "FCH-09C2", "FCH-09C3", 
            "FCH-10M1", "FCH-10M2", "FCH-10C2", "FCH-10C3", "FCH-11M1", 
            "FCH-11M2", "FCH-11C2", "FCH-11C3", "FCH-12M1", "FCH-12M2", 
            "FCH-12C2", "FCH-12C3", "FCH-13M1", "FCH-13M2", "FCH-13C2", 
            "FCH-13C3", "FCH-14M1", "FCH-14M2", "FCH-14C2", "FCH-14C3", 
            "FCH-15M1", "FCH-15M2", "FCH-15C2", "FCH-15C3", "FCH-16M1", 
            "FCH-16M2", "FCH-16C2", "FCH-16C3", "FCH-17M1", "FCH-17M2", 
            "FCH-17C2", "FCH-17C3", "FCH-18M1", "FCH-18M2", "FCH-18C2", 
            "FCH-18C3", "FCH-19M1", "FCH-19M2", "FCH-19C2", "FCH-19C3", 
            "FCH-20M1", "FCH-20M2", "FCH-20C2", "FCH-20C3",        
            ]    
    
    elif family == 'FCV':
        power_supplies = [
            "FCV-01M1", 
            "FCV-01M2", "FCV-01C2", "FCV-01C3", "FCV-02M1", "FCV-02M2", 
            "FCV-02C2", "FCV-02C3", "FCV-03M1", "FCV-03M2", "FCV-03C2", 
            "FCV-03C3", "FCV-04M1", "FCV-04M2", "FCV-04C2", "FCV-04C3", 
            "FCV-05M1", "FCV-05M2", "FCV-05C2", "FCV-05C3", "FCV-06M1", 
            "FCV-06M2", "FCV-06C2", "FCV-06C3", "FCV-07M1", "FCV-07M2", 
            "FCV-07C2", "FCV-07C3", "FCV-08M1", "FCV-08M2", "FCV-08C2", 
            "FCV-08C3", "FCV-09M1", "FCV-09M2", "FCV-09C2", "FCV-09C3", 
            "FCV-10M1", "FCV-10M2", "FCV-10C2", "FCV-10C3", "FCV-11M1", 
            "FCV-11M2", "FCV-11C2", "FCV-11C3", "FCV-12M1", "FCV-12M2", 
            "FCV-12C2", "FCV-12C3", "FCV-13M1", "FCV-13M2", "FCV-13C2", 
            "FCV-13C3", "FCV-14M1", "FCV-14M2", "FCV-14C2", "FCV-14C3", 
            "FCV-15M1", "FCV-15M2", "FCV-15C2", "FCV-15C3", "FCV-16M1", 
            "FCV-16M2", "FCV-16C2", "FCV-16C3", "FCV-17M1", "FCV-17M2", 
            "FCV-17C2", "FCV-17C3", "FCV-18M1", "FCV-18M2", "FCV-18C2", 
            "FCV-18C3", "FCV-19M1", "FCV-19M2", "FCV-19C2", "FCV-19C3", 
            "FCV-20M1", "FCV-20M2", "FCV-20C2", "FCV-20C3",        
            ]
        
    elif family == 'QS' or family == 'SKEW':
        power_supplies = [
            "QS-01M1",
            "QS-01M2", "QS-01C1", "QS-01C4", "QS-02M1", "QS-02M2", 
            "QS-02C1", "QS-02C4", "QS-03M1", "QS-03M2", "QS-03C1", 
            "QS-03C4", "QS-04M1", "QS-04M2", "QS-04C1", "QS-04C4", 
            "QS-05M1", "QS-05M2", "QS-05C1", "QS-05C4", "QS-06M1", 
            "QS-06M2", "QS-06C1", "QS-06C4", "QS-07M1", "QS-07M2", 
            "QS-07C1", "QS-07C4", "QS-08M1", "QS-08M2", "QS-08C1", 
            "QS-08C4", "QS-09M1", "QS-09M2", "QS-09C1", "QS-09C4", 
            "QS-10M1", "QS-10M2", "QS-10C1", "QS-10C4", "QS-11M1", 
            "QS-11M2", "QS-11C1", "QS-11C4", "QS-12M1", "QS-12M2", 
            "QS-12C1", "QS-12C4", "QS-13M1", "QS-13M2", "QS-13C1", 
            "QS-13C4", "QS-14M1", "QS-14M2", "QS-14C1", "QS-14C4", 
            "QS-15M1", "QS-15M2", "QS-15C1", "QS-15C4", "QS-16M1", 
            "QS-16M2", "QS-16C1", "QS-16C4", "QS-17M1", "QS-17M2", 
            "QS-17C1", "QS-17C4", "QS-18M1", "QS-18M2", "QS-18C1", 
            "QS-18C4", "QS-19M1", "QS-19M2", "QS-19C1", "QS-19C4", 
            "QS-20M1", "QS-20M2", "QS-20C1", "QS-20C4", 
            ] 
        
    else:
        power_supplies = None
        
    return power_supplies


def add_header(table, header_opi):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")   
    linkingContainer.setPropertyValue("opi_file", header_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)


def add_line(table, line_opi, power_supply):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")   
    linkingContainer.setPropertyValue("opi_file", line_opi)
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    linkingContainer.setPropertyValue("border_style", 0)
    table.addChildToBottom(linkingContainer)
    
    children = linkingContainer.getChildren()
    for w in children:
        if w.getPropertyValue("widget_type") == "Action Button":
            button = w
        elif w.getPropertyValue("widget_type") == "Spinner":
            spinner = w
        elif w.getPropertyValue("widget_type") == "Text Update":
            text_update = w
        elif w.getPropertyValue("widget_type") == "Grouping Container":
            container = w
            led = container.getChildren()[0]  
           
    setpoint = subsystem + power_supply.upper() + '-SP'
    readback = subsystem + power_supply.upper() + '-RB' 
    
    button.setPropertyValue("text", power_supply)
    spinner.setPropertyValue("pv_name", setpoint)
    text_update.setPropertyValue("pv_name", readback)
    led.setPropertyValue("pv_name", '$(power_supply_status)')
    
    macro_inputs = DataUtil.createMacrosInput(True)
    macro_inputs.put("power_supply", power_supply)
    macro_inputs.put("power_supply_sp", setpoint)
    macro_inputs.put("power_supply_rb", readback)
    macro_inputs.put("power_supply_start", 'sim://const("corrector")')
    linkingContainer.setPropertyValue("macros", macro_inputs)
    
    
subsystem  = "SIPS-"
family     = PVUtil.getString(pvs[0]).upper()
if family == 'CV':
    table_len  = 32
    header_opi = "table/tiny_table_header.opi"
    line_opi   = "table/tiny_table_line.opi"
elif family == 'CH': 
    table_len  = 30
    header_opi = "table/small_table_header.opi"
    line_opi   = "table/small_table_line.opi"
else:
    table_len = 20
    header_opi = "table/table_header.opi"
    line_opi   = "table/table_line.opi"    

power_supplies   = get_power_supply_list(family)
len_ps           = len(power_supplies)
nr_tables        = int(math.ceil(len_ps/table_len))
table_container  = display.getWidget("table_container")
tables = []
for i in range(nr_tables):
    table = display.getWidget("table_%i"%(i+1))
    table.removeAllChildren()
    tables.append(table)
    
if power_supplies is None:
    table_container.setPropertyValue("visible", False)
    
else:
    j = 0
    for table in tables:
        add_header(table, header_opi)    
        for i in range(1,table_len+1):
            power_supply = power_supplies[j]
            add_line(table, line_opi, power_supply)   
            j += 1
        table.performAutosize()  
        
    table_container.setPropertyValue("visible", True)
