from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil

def get_trims_list(family):
    if (family == 'QFA') or (family == 'QDA'):
        TrimsAreaName = [
            ("SI-01M1", "SI-01M2"), 
            ("SI-05M1", "SI-05M2"), 
            ("SI-09M1", "SI-09M2"), 
            ("SI-13M1", "SI-13M2"), 
            ("SI-17M1", "SI-17M2")  ]
    
    elif (family == 'QFP') or (family == 'QDP1') or (family == 'QDP2'):
        TrimsAreaName = [
            ("SI-03M1", "SI-03M2"), 
            ("SI-07M1", "SI-07M2"), 
            ("SI-11M1", "SI-11M2"), 
            ("SI-15M1", "SI-15M2"), 
            ("SI-19M1", "SI-19M2")  ]
        
    elif (family == 'QFB') or (family == 'QDB1') or (family == 'QDB2'):
        TrimsAreaName = [
            ("SI-02M1", "SI-02M2"), 
            ("SI-04M1", "SI-04M2"), 
            ("SI-06M1", "SI-06M2"), 
            ("SI-08M1", "SI-08M2"), 
            ("SI-10M1", "SI-10M2"),
            ("SI-12M1", "SI-12M2"), 
            ("SI-14M1", "SI-14M2"), 
            ("SI-16M1", "SI-16M2"), 
            ("SI-18M1", "SI-18M2"), 
            ("SI-20M1", "SI-20M2")  ]

    elif (family == 'Q1') or (family == 'Q2'):
        TrimsAreaName = [
            ("SI-01C1", "SI-01C4"), 
            ("SI-02C1", "SI-02C4"), 
            ("SI-03C1", "SI-03C4"), 
            ("SI-04C1", "SI-04C4"), 
            ("SI-05C1", "SI-05C4"), 
            ("SI-06C1", "SI-06C4"), 
            ("SI-07C1", "SI-07C4"), 
            ("SI-08C1", "SI-08C4"), 
            ("SI-09C1", "SI-09C4"), 
            ("SI-10C1", "SI-10C4"), 
            ("SI-11C1", "SI-11C4"), 
            ("SI-12C1", "SI-12C4"), 
            ("SI-13C1", "SI-13C4"), 
            ("SI-14C1", "SI-14C4"), 
            ("SI-15C1", "SI-15C4"), 
            ("SI-16C1", "SI-16C4"), 
            ("SI-17C1", "SI-17C4"), 
            ("SI-18C1", "SI-18C4"), 
            ("SI-19C1", "SI-19C4"), 
            ("SI-20C1", "SI-20C4")   ]

    elif (family == 'Q3') or (family == 'Q4'):
        TrimsAreaName = [
            ("SI-01C2", "SI-01C3"), 
            ("SI-02C2", "SI-02C3"), 
            ("SI-03C2", "SI-03C3"), 
            ("SI-04C2", "SI-04C3"), 
            ("SI-05C2", "SI-05C3"), 
            ("SI-06C2", "SI-06C3"), 
            ("SI-07C2", "SI-07C3"), 
            ("SI-08C2", "SI-08C3"), 
            ("SI-09C2", "SI-09C3"), 
            ("SI-10C2", "SI-10C3"), 
            ("SI-11C2", "SI-11C3"), 
            ("SI-12C2", "SI-12C3"), 
            ("SI-13C2", "SI-13C3"), 
            ("SI-14C2", "SI-14C3"), 
            ("SI-15C2", "SI-15C3"), 
            ("SI-16C2", "SI-16C3"), 
            ("SI-17C2", "SI-17C3"), 
            ("SI-18C2", "SI-18C3"), 
            ("SI-19C2", "SI-19C3"), 
            ("SI-20C2", "SI-20C3")   ]
 
    else:
        TrimsAreaName = None
    
    return TrimsAreaName

def get_si_sector_SlowCors(plane):
    if (plane.upper() == 'HORIZONTAL'):
        SectorCors = [
            ("M1", "CH"), 
            ("M2", "CH"), 
            ("C1", "CH"), 
            ("C2", "CH"), 
            ("C3", "CH"),
            ("C4", "CH")   ]  
    elif (plane.upper() == 'VERTICAL'):
        SectorCors = [
            ("M1", "CV"), 
            ("M2", "CV"), 
            ("C1", "CV"), 
            ("C2", "CV-1"), 
            ("C2", "CV-2"), 
            ("C3", "CV-1"),
            ("C3", "CV-2"),
            ("C4", "CV")    ]
    else:
        SectorCors = None
    
    return SectorCors

def get_si_sector_FastCors(plane):
    if (plane.upper() == 'HORIZONTAL'):
        SectorCors = [
            ("M1", "FCH"), 
            ("M2", "FCH"), 
            ("C2", "FCH"), 
            ("C3", "FCH")   ]  
    elif (plane.upper() == 'VERTICAL'):
        SectorCors = [
            ("M1", "FCV"), 
            ("M2", "FCV"), 
            ("C2", "FCV"), 
            ("C3", "FCV")   ]  
    else:
        SectorCors = None
    
    return SectorCors

def get_si_sector_QS():
    SectorQS = [
        ("M1", "QS"), 
        ("M2", "QS"), 
        ("C1", "QS"), 
        ("C2", "QS"), 
        ("C3", "QS")   ] 
    return SectorQS


def add_line(table, group, area, dev, pY):
    linkingContainer = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.linkingContainer")   
    input_macro = DataUtil.createMacrosInput(True)
    input_macro.put("AreaName", area)
    input_macro.put("devName", dev)
    linkingContainer.setPropertyValue("macros", input_macro)
    line_opi_file = "../magnet_interfaces/magnet_interfaces_Lines.opi"
    linkingContainer.setPropertyValue("opi_file", line_opi_file)
    linkingContainer.setPropertyValue("group_name", group)
    linkingContainer.setX(0)
    linkingContainer.setY(pY)
    linkingContainer.setPropertyValue("border_style", 0)
    linkingContainer.setPropertyValue("background_color", (255,255,255))
    linkingContainer.setPropertyValue("foreground_color", (255,255,255))
    linkingContainer.setPropertyValue("resize_behaviour", 1)
    table.addChild(linkingContainer)
             

def create_SI_QuadTrimTable(display,QuadFamName):
    group         = "GC_QuadTrim"
    GC_Trims1     = display.getWidget("Trims1")
    GC_Trims2     = display.getWidget("Trims2")
    TrimsAreaName = get_trims_list(QuadFamName)
  
    if TrimsAreaName is None:
        GC_Trims1.setPropertyValue("visible", False)
        GC_Trims2.setPropertyValue("visible", False)
    else: 
        length = len(TrimsAreaName)

        # create table1 for quadrupole trim coils
        GC     = GC_Trims1 
        for i in range(1,length+1):
	    pY = 37 + (i-1)*35
            TrimArea = TrimsAreaName[i-1][0]
            add_line(GC, group, TrimArea, QuadFamName, pY)

        # create table2 for quadrupole trim coils
        GC     = GC_Trims2 
        for i in range(1,length+1):
	    pY = 37 + (i-1)*35
            TrimArea = TrimsAreaName[i-1][1]
            add_line(GC, group, TrimArea, QuadFamName, pY)

        h = 200 + 35*(length+1)
        GC_Trims1.performAutosize()
        GC_Trims2.performAutosize()  

        display.setWidth(1600)
        display.setHeight(h)


def create_SI_CorsTable(display,plane,CorType):
    group     = "GC_Cor"

    if CorType == "Slow":
        CorsList  = get_si_sector_SlowCors(plane)
    elif CorType == "Fast":
        CorsList  = get_si_sector_FastCors(plane)
    else:
        CorsList = None
    
    GCName  = CorType + "CorsTable_" + plane
    GC_Cors = display.getWidget(GCName)
   
    if CorsList is None:
        GC_Cors.setPropertyValue("visible", False)
    else:
        length   = len(CorsList)
	dyline   = 35
        dysector = length * 35 + 30

	for s in range(1,20+1):    #loop for 20 sectors
	    sec = "%02d"%s
	    pY = (s-1)*dysector + 5
	    TUtext = "Sector " + sec
	    TU = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.TextUpdate")   
            TU.setPropertyValue("text", TUtext)
	    TU.setWidth(80)
	    TU.setHeight(20)
	    TU.setX(30)
	    TU.setY(pY)
            GC_Cors.addChild(TU)

            for i in range(1,length+1):
	        pY   = 30 + (s-1)*dysector + (i-1)*dyline
                Area = "SI-" + sec + CorsList[i-1][0]
	        dev  = CorsList[i-1][1]
                add_line(GC_Cors, group, Area, dev, pY)
            
        GC_Cors.performAutosize()


def create_SI_SkewQuadTable(display):
    group  = "GC_QuadFam_NoTrim"

    QSList = get_si_sector_QS()
    
    GCName = "QSTable"
    GC_QS  = display.getWidget(GCName)
   
    if QSList is None:
        GC_QS.setPropertyValue("visible", False)
    else:
        length   = len(QSList)
	dyline   = 35
        dysector = length * 35 + 30

	for s in range(1,20+1):    #loop for 20 sectors
	    sec = "%02d"%s
	    pY = (s-1)*dysector + 5
	    TUtext = "Sector " + sec
	    TU = WidgetUtil.createWidgetModel("org.csstudio.opibuilder.widgets.TextUpdate")   
            TU.setPropertyValue("text", TUtext)
	    TU.setWidth(80)
	    TU.setHeight(20)
	    TU.setX(30)
	    TU.setY(pY)
            GC_QS.addChild(TU)

            for i in range(1,length+1):
	        pY   = 30 + (s-1)*dysector + (i-1)*dyline
                Area = "SI-" + sec + QSList[i-1][0]
	        dev  = QSList[i-1][1]
                add_line(GC_QS, group, Area, dev, pY)
            
        GC_QS.performAutosize()

