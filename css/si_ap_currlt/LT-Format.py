from org.csstudio.opibuilder.scriptUtil import PVUtil, ConsoleUtil

lt = PVUtil.getDouble(pvs[0])

H = str(int(lt//3600))

m = str(int((lt%3600)//60))
if len(m)==1:
	m = '0' + m 
	
s = str(int((lt%3600)%60))
if len(s)==1:
	s = '0' + s 

ltstr = H +':'+ m +':'+ s
#ConsoleUtil.writeInfo(str(type(ltstr)))
pvs[1].setValue(ltstr)
