from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil

def get_power_supply_list(family):
    if family == 'BPM':
        power_supplies = [
            "QFA-01M2", "QFA-02M2", "QFA-03M2", "QFA-04M2", "QFA-05M2", 
            "QFA-06M2", "QFA-07M2", "QFA-08M2", "QFA-09M2", "QFA-10M2", 
            "QFA-11M2", "QFA-12M2", "QFA-13M2", "QFA-14M2", "QFA-15M2", 
            "QFA-16M2", "QFA-17M2", "QFA-18M2", "QFA-19M2", "QFA-20M2", 
            ]
    
    elif family == 'QDA':
        power_supplies = [
            "QDA-01M2", "QDA-02M2", "QDA-03M2", "QDA-04M2", "QDA-05M2", 
            "QDA-06M2", "QDA-07M2", "QDA-08M2", "QDA-09M2", "QDA-10M2", 
            "QDA-11M2", "QDA-12M2", "QDA-13M2", "QDA-14M2", "QDA-15M2", 
            "QDA-16M2", "QDA-17M2", "QDA-18M2", "QDA-19M2", "QDA-20M2",                     
            ]
        
    elif family == 'QF1':
        power_supplies = [
            "QF1-01C1", "QF1-01C4", "QF1-02C1", "QF1-02C4", "QF1-03C1", 
            "QF1-03C4", "QF1-04C1", "QF1-04C4", "QF1-05C1", "QF1-05C4", 
            "QF1-06C1", "QF1-06C4", "QF1-07C1", "QF1-07C4", "QF1-08C1", 
            "QF1-08C4", "QF1-09C1", "QF1-09C4", "QF1-10C1", "QF1-10C4", 
            "QF1-11C1", "QF1-11C4", "QF1-12C1", "QF1-12C4", "QF1-13C1", 
            "QF1-13C4", "QF1-14C1", "QF1-14C4", "QF1-15C1", "QF1-15C4", 
            "QF1-16C1", "QF1-16C4", "QF1-17C1", "QF1-17C4", "QF1-18C1", 
            "QF1-18C4", "QF1-19C1", "QF1-19C4", "QF1-20C1", "QF1-20C4",              
            ]
        
    elif family == 'QF2':
        power_supplies = [
            "QF2-01C1", "QF2-01C4", "QF2-02C1", "QF2-02C4", "QF2-03C1", 
            "QF2-03C4", "QF2-04C1", "QF2-04C4", "QF2-05C1", "QF2-05C4", 
            "QF2-06C1", "QF2-06C4", "QF2-07C1", "QF2-07C4", "QF2-08C1", 
            "QF2-08C4", "QF2-09C1", "QF2-09C4", "QF2-10C1", "QF2-10C4", 
            "QF2-11C1", "QF2-11C4", "QF2-12C1", "QF2-12C4", "QF2-13C1", 
            "QF2-13C4", "QF2-14C1", "QF2-14C4", "QF2-15C1", "QF2-15C4", 
            "QF2-16C1", "QF2-16C4", "QF2-17C1", "QF2-17C4", "QF2-18C1", 
            "QF2-18C4", "QF2-19C1", "QF2-19C4", "QF2-20C1", "QF2-20C4",               
            ]
        
    elif family == 'QF3':
        power_supplies = [
            "QF3-01C2", "QF3-01C3", "QF3-02C2", "QF3-02C3", "QF3-03C2", 
            "QF3-03C3", "QF3-04C2", "QF3-04C3", "QF3-05C2", "QF3-05C3", 
            "QF3-06C2", "QF3-06C3", "QF3-07C2", "QF3-07C3", "QF3-08C2", 
            "QF3-08C3", "QF3-09C2", "QF3-09C3", "QF3-10C2", "QF3-10C3", 
            "QF3-11C2", "QF3-11C3", "QF3-12C2", "QF3-12C3", "QF3-13C2", 
            "QF3-13C3", "QF3-14C2", "QF3-14C3", "QF3-15C2", "QF3-15C3", 
            "QF3-16C2", "QF3-16C3", "QF3-17C2", "QF3-17C3", "QF3-18C2", 
            "QF3-18C3", "QF3-19C2", "QF3-19C3", "QF3-20C2", "QF3-20C3",               
            ]
        
    elif family == 'QF4':
        power_supplies = [
            "QF4-01C2", "QF4-01C3", "QF4-02C2", "QF4-02C3", "QF4-03C2", 
            "QF4-03C3", "QF4-04C2", "QF4-04C3", "QF4-05C2", "QF4-05C3", 
            "QF4-06C2", "QF4-06C3", "QF4-07C2", "QF4-07C3", "QF4-08C2", 
            "QF4-08C3", "QF4-09C2", "QF4-09C3", "QF4-10C2", "QF4-10C3", 
            "QF4-11C2", "QF4-11C3", "QF4-12C2", "QF4-12C3", "QF4-13C2", 
            "QF4-13C3", "QF4-14C2", "QF4-14C3", "QF4-15C2", "QF4-15C3", 
            "QF4-16C2", "QF4-16C3", "QF4-17C2", "QF4-17C3", "QF4-18C2", 
            "QF4-18C3", "QF4-19C2", "QF4-19C3", "QF4-20C2", "QF4-20C3",               
            ]
        
    elif family == 'QDB1':
        power_supplies = [
            "QDB1-01M1", "QDB1-02M1", "QDB1-03M1", "QDB1-04M1", "QDB1-05M1", 
            "QDB1-06M1", "QDB1-07M1", "QDB1-08M1", "QDB1-09M1", "QDB1-10M1", 
            "QDB1-11M1", "QDB1-12M1", "QDB1-13M1", "QDB1-14M1", "QDB1-15M1", 
            "QDB1-16M1", "QDB1-17M1", "QDB1-18M1", "QDB1-19M1", "QDB1-20M1",                
            ]
        
    elif family == 'QFB':
        power_supplies = [
            "QFB-01M1", "QFB-02M1", "QFB-03M1", "QFB-04M1", "QFB-05M1", 
            "QFB-06M1", "QFB-07M1", "QFB-08M1", "QFB-09M1", "QFB-10M1", 
            "QFB-11M1", "QFB-12M1", "QFB-13M1", "QFB-14M1", "QFB-15M1", 
            "QFB-16M1", "QFB-17M1", "QFB-18M1", "QFB-19M1", "QFB-20M1",               
            ]
        
    elif family == 'QDB2':
        power_supplies = [
            "QDB2-01M1", "QDB2-02M1", "QDB2-03M1", "QDB2-04M1", "QDB2-05M1", 
            "QDB2-06M1", "QDB2-07M1", "QDB2-08M1", "QDB2-09M1", "QDB2-10M1", 
            "QDB2-11M1", "QDB2-12M1", "QDB2-13M1", "QDB2-14M1", "QDB2-15M1", 
            "QDB2-16M1", "QDB2-17M1", "QDB2-18M1", "QDB2-19M1", "QDB2-20M1",             
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
        if w.getPropertyValue("widget_type") == "Boolean Button":
            button = w

    setpoint = subsystem + power_supply.upper() + '-SP'
    readback = subsystem + power_supply.upper() + '-RB'
    
    button.setPropertyValue("pv_name", power_supply)
    #button.setPropertyValue("text", power_supply)
    #spinner.setPropertyValue("pv_name", setpoint)
    #text_update.setPropertyValue("pv_name", readback)
    #led.setPropertyValue("pv_name", '$(power_supply_status)')
           
    macro_inputs = DataUtil.createMacrosInput(True)
    macro_inputs.put("power_supply", power_supply)
    macro_inputs.put("power_supply_sp", setpoint)
    macro_inputs.put("power_supply_rb", readback)
    macro_inputs.put("power_supply_start", 'sim://const("quadrupole")')
    linkingContainer.setPropertyValue("macros", macro_inputs)
    

subsystem      = "SIPS-"
family         = PVUtil.getString(pvs[0]).upper()
power_supplies = get_power_supply_list(family)
header_opi     = "table/selection_table_low_header.opi"
line_opi       = "table/selection_table_line.opi"

table_container  = display.getWidget("table_container")
#fam_table   = display.getWidget("fam_table")
#shunt_table_1 = display.getWidget("shunt_table_1")
#shunt_table_2 = display.getWidget("shunt_table_2")

#fam_table.removeAllChildren()
#shunt_table_1.removeAllChildren()
#shunt_table_2.removeAllChildren()
      
if power_supplies is None:
    table_container.setPropertyValue("visible", False)
    
else: 
    # create table for family power supply
    #add_header(fam_table, header_opi)
    #power_supply = family.upper() + '-FAM'
    #add_line(fam_table, line_opi, power_supply)
    #add_header(table_container, header_opi)
    power_supply = family.upper() + '-FAM'
    add_line(table_container, line_opi, power_supply)
    #add_header(table_container, header_opi)
    #power_supply = family.upper() + '-FAM'
    #add_line(table_container, line_opi, power_supply)
    
    """   
    # create table for shunt power supply
    length    = len(power_supplies)
    table_len = 20
    table     = shunt_table_1
    add_header(table, header_opi)    
    for i in range(1,length+1):
        power_supply = power_supplies[i-1]
        add_line(table, line_opi, power_supply)       
        if i == table_len and length > table_len: 
            table = shunt_table_2
            add_header(table, header_opi) 

    fam_table.performAutosize()        
    shunt_table_1.performAutosize()
    shunt_table_2.performAutosize()"""
    table_container.setPropertyValue("visible", True)
