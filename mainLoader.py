### Custom path ###


import sys

#Insert path to AnimationGUI.ui
path = r"-path-"

if sys.path.count(path) < 1:
	sys.path.append(path)


###################


import loadXMLUI
reload(loadXMLUI) #Use this to update the module when changes has been made in loadXMLUI
ui = loadXMLUI.loadUI(path + "AnimationGUI.ui")
print path
cont = loadXMLUI.UIController(ui)
print "# GUI Loaded #"
