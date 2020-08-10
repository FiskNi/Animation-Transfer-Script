from maya import OpenMayaUI as omui
import PySide2
from PySide2 import QtGui, QtCore, QtWidgets, QtUiTools
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import pymel.core as pm
import AniTransfer as atr
reload(atr)

def getMayaWin():
    mayaWinPtr = omui.MQtUtil.mainWindow( )
    mayaWin = wrapInstance( long( mayaWinPtr ), QWidget )

def loadUI( path ):
    loader = QUiLoader()
    uiFile = QFile( path )

    dirIconShapes = ""
    buff = None

    if uiFile.exists():
        dirIconShapes = path
        uiFile.open( QFile.ReadOnly )

        buff = QByteArray( uiFile.readAll() )
        uiFile.close()
    else:
        print "UI file missing! Exiting..."
        exit(-1)

    fixXML( path, buff )
    qbuff = QBuffer()
    qbuff.open( QBuffer.ReadOnly | QBuffer.WriteOnly )
    qbuff.write( buff )
    qbuff.seek( 0 )
    ui = loader.load( qbuff, parentWidget = getMayaWin() )
    ui.path = path

    return ui


def fixXML( path, qbyteArray ):
    # first replace forward slashes for backslashes
    if path[-1] != '/':
        path += '/'
    path = path.replace( "/", "\\" )
    
    # construct whole new path with <pixmap> at the begining
    tempArr = QByteArray( "<pixmap>" + path + "\\" )
    
    # search for the word <pixmap>
    lastPos = qbyteArray.indexOf( "<pixmap>", 0 )
    while lastPos != -1:
        qbyteArray.replace( lastPos, len( "<pixmap>" ), tempArr )
        lastPos = qbyteArray.indexOf( "<pixmap>", lastPos + 1 )
    return


class UIController:
    def __init__(self, ui):  
        # Connect each signal to it's slot one by one

        self.sourceList = []
        self.targetList = []

        self.indexSourceList = []
        self.indexTargetList = []

        self.sourceRoot = pm.ls(type="joint")[0]
        self.targetRoot = pm.ls(type="joint")[1]    
        
        ui.SourceText.textChanged.connect(lambda: self.SetSource(ui))
        ui.TargetText.textChanged.connect(lambda: self.SetTarget(ui))
        
        ui.SourceUp.clicked.connect(lambda: self.SourceUp(ui))
        ui.SourceDown.clicked.connect(lambda: self.SourceDown(ui))
        ui.SourceDelete.clicked.connect(lambda: self.SourceDelete(ui))

        ui.TargetUp.clicked.connect(lambda: self.TargetUp(ui))
        ui.TargetDown.clicked.connect(lambda: self.TargetDown(ui))
        ui.TargetDelete.clicked.connect(lambda: self.TargetDelete(ui))

        ui.Transfer.clicked.connect(self.Transfer)

        self.FillLists(ui)
        self.ui = ui
        ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        ui.show()
        
    ### Set joints
    def SetSource(self, ui):
        self.sourceRoot = pm.nodetypes.Joint(ui.SourceText.toPlainText())
        self.FillLists(ui)
        
    def SetTarget(self, ui):
        self.targetRoot = pm.nodetypes.Joint(ui.TargetText.toPlainText())
        self.FillLists(ui)
        
    ### Source Navigation ###
    def SourceUp(self, ui):
        selection = ui.SourceList.currentIndex()    

        holder = self.sourceList[selection.row()]
        self.sourceList[selection.row()] = self.sourceList[selection.row() - 1]
        self.sourceList[selection.row() - 1] = holder

        holderIndex = self.indexSourceList[selection.row()]
        self.indexSourceList[selection.row()] = self.indexSourceList[selection.row() - 1]
        self.indexSourceList[selection.row() - 1] = holderIndex
        print self.indexSourceList

        self.UpdateListS(ui)

    def SourceDown(self, ui):
        selection = ui.SourceList.currentIndex()    

        holder = self.sourceList[selection.row()]
        self.sourceList[selection.row()] = self.sourceList[selection.row() + 1]
        self.sourceList[selection.row() + 1] = holder

        holderIndex = self.indexSourceList[selection.row()]
        self.indexSourceList[selection.row()] = self.indexSourceList[selection.row() + 1]
        self.indexSourceList[selection.row() + 1] = holderIndex
        print self.indexSourceList

        self.UpdateListS(ui)

    def SourceDelete(self, ui):
        selection = ui.SourceList.currentIndex()

        self.sourceList[selection.row()] = str("- Deleted / Empty")

        for targets in range(len(self.indexSourceList)):
           if len(self.sourceList) < len(self.targetList):
               if targets > self.indexSourceList[selection.row()]:
                   self.indexSourceList[targets] -= 1
        
        self.indexSourceList[selection.row()] = -1
        print self.indexSourceList

        
        self.UpdateListS(ui)

 
    ### Target Navigation ###
    def TargetUp(self, ui):
        selection = ui.TargetList.currentIndex()    

        holder = self.targetList[selection.row()]
        self.targetList[selection.row()] = self.targetList[selection.row() - 1]
        self.targetList[selection.row() - 1] = holder

        holderIndex = self.indexTargetList[selection.row()]
        self.indexTargetList[selection.row()] = self.indexTargetList[selection.row() - 1]
        self.indexTargetList[selection.row() - 1] = holderIndex
        print self.indexTargetList

        self.UpdateListT(ui)

    def TargetDown(self, ui):
        selection = ui.TargetList.currentIndex()    

        holder = self.targetList[selection.row()]
        self.targetList[selection.row()] = self.targetList[selection.row() + 1]
        self.targetList[selection.row() + 1] = holder

        holderIndex = self.indexTargetList[selection.row()]
        self.indexTargetList[selection.row()] = self.indexTargetList[selection.row() + 1]
        self.indexTargetList[selection.row() + 1] = holderIndex

        print self.indexTargetList

        self.UpdateListT(ui)

    def TargetDelete(self, ui):
        selection = ui.TargetList.currentIndex() 

        self.targetList[selection.row()] = str("- Deleted / Empty")
        
        for targets in range(len(self.indexTargetList)):
           if len(self.targetList) < len(self.sourceList):
               if targets > self.indexTargetList[selection.row()]:
                   self.indexTargetList[targets] -= 1


        self.indexTargetList[selection.row()] = -1

        print self.indexTargetList
    
        self.UpdateListT(ui)
        
        
    ### Execution ###
    def Transfer(self):
        atr.runTransfer(self.sourceRoot, self.targetRoot, self.indexSourceList, self.indexTargetList)

    def FillLists(self, ui):
        del self.sourceList[:]
        del self.targetList[:]
        del self.indexSourceList[:]
        del self.indexTargetList[:]

        self.GetHierarchyS(self.sourceRoot)
        self.GetHierarchyT(self.targetRoot)
        for joints in range(len(self.sourceList)):
            self.indexSourceList.append(joints)
        for joints in range(len(self.targetList)):
            self.indexTargetList.append(joints)

        self.UpdateListS(ui)
        self.UpdateListT(ui)
    
    def GetHierarchyS(self, node):
        for child in node.getChildren():
            self.GetHierarchyS(child)
            self.sourceList.append(child)
            
            
    def GetHierarchyT(self, node):
        for child in node.getChildren():
            self.GetHierarchyT(child) 
            self.targetList.append(child)
               
        
    def UpdateListS(self, ui):
        sourceItemModel = QStandardItemModel(ui.SourceList)
        for joint in self.sourceList:
            jointItem = QStandardItem(str(joint))
            sourceItemModel.appendRow(jointItem)
        ui.SourceList.setModel(sourceItemModel)

    def UpdateListT(self, ui):
        targetItemModel = QStandardItemModel(ui.TargetList)
        for joint in self.targetList:
            jointItem = QStandardItem(str(joint))
            targetItemModel.appendRow(jointItem)
        ui.TargetList.setModel(targetItemModel)
