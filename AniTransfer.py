import pymel.core as pm
import pymel.core.datatypes as dt

# Currently expects the target and source to have the same amounts of joints
sourceBindPose = []
targetBindPose = []

isolatedRotations = []
targetRotations = []
targetRotationsStored = []
targetOrientations = []
translatedRotations = []
translatedRotationsStored = []

def GetBindPoseSource( source ):
    for childJoint in source.getChildren():
        if childJoint.numChildren > 0:
            GetBindPoseSource( childJoint )
        sourceBindPose.append(childJoint.getRotation().asMatrix())


def GetBindPoseTarget( target ):
    for childJoint in target.getChildren():
        if childJoint.numChildren > 0:
            GetBindPoseTarget( childJoint )         
        targetBindPose.append(childJoint.getRotation().asMatrix())


def LoopParentMatrix(joint, matrix):
    parentJoint = joint.getParent()
    if type(parentJoint) == pm.nodetypes.Joint:
        matrix = LoopParentMatrix(parentJoint, matrix)
        matrix = (parentJoint.getRotation().asMatrix() * parentJoint.getOrientation().asMatrix()) * matrix

    return matrix

def LoopSource( source, key, childIndex ):
    for childJoint in source.getChildren():
        if childJoint.numChildren() > 0:
            childIndex = LoopSource( childJoint, key, childIndex )

        sourceRotation = childJoint.getRotation().asMatrix()
        sourceOrientation = childJoint.getOrientation().asMatrix()

        isolatedRotations.append(sourceBindPose[childIndex].inverse() * sourceRotation)
        
        pm.currentTime(0)
        parentMatrix = LoopParentMatrix(childJoint, 1)
        pm.currentTime(key)

        targetRotationsStored.append( sourceOrientation.inverse() * parentMatrix.inverse() * isolatedRotations[childIndex] * parentMatrix * sourceOrientation )
        targetRotations.append( sourceOrientation.inverse() * parentMatrix.inverse() * isolatedRotations[childIndex] * parentMatrix * sourceOrientation )

        childIndex += 1
    return childIndex 

def LoopTarget(target, key, childIndex, listIndex, indexTargetList, indexSourceList):
    for childJoint in target.getChildren():
        if childJoint.numChildren() > 0:
            listIndex, childIndex = LoopTarget(childJoint, key, childIndex, listIndex, indexTargetList, indexSourceList)

        targetOrientation = childJoint.getOrientation().asMatrix()
        targetOrientations.append(childJoint.getOrientation().asMatrix())

        if indexSourceList[listIndex] > -1:
            targetRotations[childIndex] = targetRotationsStored[indexSourceList[listIndex]]

        pm.currentTime(0)
        parentMatrix = LoopParentMatrix(childJoint, 1)
        pm.currentTime(key)

        translatedRotations.append(targetOrientation * parentMatrix * targetRotations[childIndex] * parentMatrix.inverse() * targetOrientation.inverse())
        translatedRotationsStored.append(targetOrientation * parentMatrix * targetRotations[childIndex] * parentMatrix.inverse() * targetOrientation.inverse())

        childIndex += 1    
        listIndex += 1

    return listIndex, childIndex    

def StoreTarget(target, key, childIndex, listIndex, indexTargetList, indexSourceList):
    for childJoint in target.getChildren():
        if childJoint.numChildren() > 0:
            listIndex, childIndex = StoreTarget(childJoint, key, childIndex, listIndex, indexTargetList, indexSourceList)

        pm.currentTime(0)
        parentMatrix = LoopParentMatrix(childJoint, 1)
        pm.currentTime(key)

        translatedRotations[childIndex] = targetBindPose[childIndex] * (targetOrientations[childIndex] * parentMatrix * targetRotations[indexTargetList[listIndex]] * parentMatrix.inverse() * targetOrientations[childIndex].inverse())
        
        print childJoint
        print childIndex
        print indexTargetList[listIndex]
        print indexSourceList[listIndex]

        if indexSourceList[listIndex] > -1:
            if indexTargetList[listIndex] < len(indexSourceList) + 1:
                translatedRotationsStored[childIndex] = translatedRotations[childIndex]

        childIndex += 1    
        listIndex += 1
    return listIndex, childIndex    

def KeyTarget(target, childIndex, listIndex, indexTargetList, indexSourceList):
    for childJoint in target.getChildren():
        if childJoint.numChildren() > 0:
            listIndex, childIndex = KeyTarget( childJoint, childIndex, listIndex, indexTargetList, indexSourceList )

        if indexTargetList[listIndex] < len(indexSourceList) + 1:
            if indexTargetList[listIndex] > -1:
                if indexSourceList[listIndex] > -1:
                    childJoint.setRotation( dt.degrees( dt.EulerRotation( translatedRotationsStored[childIndex] ) ) )
                    pm.setKeyframe(childJoint)

        childIndex += 1    
        listIndex += 1
    return listIndex, childIndex    
            

def transferKeys(keyframes, source, target, indexSourceList, indexTargetList):
    for key in range( keyframes ):

        del targetRotations [:]
        del isolatedRotations[:]
        del translatedRotations[:]

        del targetRotationsStored[:]
        del targetOrientations[:]
        del translatedRotationsStored [:]

        pm.currentTime( key )
        
        target.setOrientation(source.getOrientation())
        target.setRotation(source.getRotation())
        target.setTranslation(source.getTranslation())
        pm.setKeyframe(target)

        LoopSource( source, key, 0 )
        LoopTarget( target, key, 0, 0, indexTargetList, indexSourceList )
        StoreTarget( target, key, 0, 0, indexTargetList, indexSourceList )
        KeyTarget( target, 0, 0, indexTargetList, indexSourceList )

        
        
        
def runTransfer(source, target, indexSourceList, indexTargetList):
    # --- Run --- #
    del sourceBindPose[:]
    del targetBindPose[:]

    pm.currentTime(0)
    


    #source = pm.ls( sl=True )[0]
    #target = pm.ls( sl=True )[1]

    keyframes = pm.keyframe(source, query=True, kc=True) / 10
    testframes = 35

    GetBindPoseSource( source )
    GetBindPoseTarget( target )

    transferKeys( testframes, source, target, indexSourceList, indexTargetList )

    pm.currentTime(0)