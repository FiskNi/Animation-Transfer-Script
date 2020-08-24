### Custom path ###


import sys

path = r"G:/#Old/UD1439/AniTransfer/"

if sys.path.count(path) < 1:
	sys.path.append(path)


###################


import loadXMLUI
reload(loadXMLUI) #Use this to update the module when changes has been made in loadXMLUI
ui = loadXMLUI.loadUI(path + "AnimationGUI.ui")
print path
cont = loadXMLUI.UIController(ui)
print "# GUI Loaded #"