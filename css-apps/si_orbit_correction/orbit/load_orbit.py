from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil, FileUtil, ConsoleUtil
#import os.path

try:
	file = FileUtil.openFileDialog(False) # Open file dialog
	#file_name = os.path.basename(file) # Get file name
	widget.setPropertyValue("label", file) # Set file name as widget label
except:
        pass
