import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import qt
import numpy as np
import math
#
# RobotTrajectoryGenerator
#

class RobotTrajectoryGenerator(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "RobotTrajectoryGenerator"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#RobotTrajectoryGenerator">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # RobotTrajectoryGenerator1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='RobotTrajectoryGenerator',
        sampleName='RobotTrajectoryGenerator1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'RobotTrajectoryGenerator1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='RobotTrajectoryGenerator1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='RobotTrajectoryGenerator1'
    )

    # RobotTrajectoryGenerator2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='RobotTrajectoryGenerator',
        sampleName='RobotTrajectoryGenerator2',
        thumbnailFileName=os.path.join(iconsPath, 'RobotTrajectoryGenerator2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='RobotTrajectoryGenerator2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='RobotTrajectoryGenerator2'
    )


#
# RobotTrajectoryGeneratorWidget
#

class RobotTrajectoryGeneratorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/RobotTrajectoryGenerator.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = RobotTrajectoryGeneratorLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.lookupSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateObservedLookup)
        self.ui.tracePathButton.connect("clicked(bool)", self.onTracePathButton)
        self.ui.clearPathButton.connect("clicked(bool)", self.onClearPathButton)
        self.ui.sendPoseArrayButton.connect("clicked(bool)", self.onSendPoseArrayButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch


        self._parameterNode.EndModify(wasModified)


    def updateObservedLookup(self):
        """
        This function is called when a lookup is selected in the dropdown combo box. This lookup is used as the reference point for tracing.
        """
        self.logic.setObservedLookup(slicer.mrmlScene.GetNodeByID(self.ui.lookupSelector.currentNodeID))

    def onTracePathButton(self):
        """
        This function is called when a user selects the 'Trace path' button.
        """
        print("Tracing started")
        for j in range(0, 5000, 20): # the upper bound here can be changed depending on how long you want to trace
            timer = qt.QTimer()
            timer.singleShot(j, lambda: self.logic.AddToTrajectory())

    def onClearPathButton(self):
        """
        This function is called when the user presses 'Clear path' button.
        """
        self.logic.clearTrajectory()

    def onSendPoseArrayButton(self):
        """
        This function is called when the user presses 'Send trajectory' button.
        """
        self.logic.SendPoseArray()



#
# RobotTrajectoryGeneratorLogic
#

class RobotTrajectoryGeneratorLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        self.trajectoryPoints = slicer.mrmlScene.GetFirstNodeByName("Trajectory") # will be None if this doesn't work
        self.trCollection = vtk.vtkTransformCollection()

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        print('Not using parameter node.')

    def setObservedLookup(self, observedLookup):

        self.observedLookup = observedLookup
        self.createTrajectoryFiducials()

    def createTrajectoryFiducials(self):

        if slicer.mrmlScene.GetFirstNodeByName('Trajectory') is None:
            self.trajectoryPoints = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
            self.trajectoryPoints.SetName('Trajectory')

    def AddToTrajectory(self):
        """
        This function gets the x, y, z coordinate of the observed lookup and adds it as a fiducial for visualization.
        It also takes the entire pose (from the lookup) and saves it to a transform collection for publishing later.
        """

        # Check if the fiducial list exists already
        if self.trajectoryPoints is None:
            self.createTrajectoryFiducials()

        # Check how many fiducials are already in the traced path
        numControlPts = self.trajectoryPoints.GetNumberOfControlPoints()

        # Get the x, y, z position from the observed lookup
        mat = vtk.vtkMatrix4x4()
        self.observedLookup.GetMatrixTransformToWorld(mat)
        transform = slicer.vtkMRMLLinearTransformNode()
        transform.SetMatrixTransformToParent(mat)
        pos_new = [mat.GetElement(0,3), mat.GetElement(1,3), mat.GetElement(2,3)]

        # Store the matrix as a transform (so we can save the full lookup later)
        tr = vtk.vtkTransform()
        tr.SetMatrix(mat)

        # If it's the first point in the trajectory - we always add it to the list
        if numControlPts == 0:
            self.trajectoryPoints.InsertControlPointWorld(0, pos_new)

            # FOR VISUALIZATION - not necessary for functions
            transformNode = slicer.mrmlScene.AddNode(transform)
            slicer.modules.createmodels.widgetRepresentation().OnCreateCoordinateClicked() # dependency on SlicerIGT
            coordinateModels = slicer.mrmlScene.GetNodesByName("CoordinateModel")
            mostRecentCoordinateModel = coordinateModels.GetItemAsObject(coordinateModels.GetNumberOfItems() - 1)
            mostRecentCoordinateModel.SetDisplayVisibility(False)
            mostRecentCoordinateModel.SetAndObserveTransformNodeID(transformNode.GetID())

            # Save to a transform collection list for publishing later on
            self.trCollection.AddItem(tr)
            return

        # If it's not the first point in the trajectory - check how much the lookup has moved (only add to the list if it's moved a certain distance)

        # Get the last point in the trajectory list
        pos = [0, 0, 0, 0]
        self.trajectoryPoints.GetNthFiducialWorldCoordinates(numControlPts - 1, pos)
        pos_prev = pos[0:3]

        # Calculate the distance between new and previous point
        euclidean_distance = math.dist(pos_prev, pos_new)

        if euclidean_distance > 5.0:
            # Append to the list if the distance threshold is achieved
            self.trajectoryPoints.InsertControlPointWorld(numControlPts, pos_new)

            # FOR VISUALIZATION - not necessary for functions
            transformNode = slicer.mrmlScene.AddNode(transform)  # This is just for visualization
            slicer.modules.createmodels.widgetRepresentation().OnCreateCoordinateClicked()
            coordinateModels = slicer.mrmlScene.GetNodesByName("CoordinateModel")
            mostRecentCoordinateModel = coordinateModels.GetItemAsObject(coordinateModels.GetNumberOfItems() - 1)
            mostRecentCoordinateModel.SetDisplayVisibility(False)
            mostRecentCoordinateModel.SetAndObserveTransformNodeID(transformNode.GetID())

            # Save to a transform collection list for publishing later on
            self.trCollection.AddItem(tr)


    def clearTrajectory(self):
        """
        Clear the fiducial list, the nodes that have been added for visualization and the transform collection so the
        user can trace a new path.
        """
        if self.trajectoryPoints is not None:
            self.trajectoryPoints.RemoveAllMarkups()
        self.RemoveTransforms()
        self.trCollection = vtk.vtkTransformCollection()
        print('Trajectory has been cleared')

    def SendPoseArray(self):
        """
        Take the transform collection and publish the trajectory as a pose array.
        """
        ros2Node = slicer.mrmlScene.GetFirstNodeByName("ros2:node:slicer")
        publisher = slicer.mrmlScene.GetFirstNodeByName('ros2:pub:/slicer_posearray')
        if publisher is None:
            publisher = ros2Node.CreateAndAddPublisherNode("vtkMRMLROS2PublisherPoseArrayNode", "/slicer_posearray")
        publisher.Publish(self.trCollection) # Publishes a pose array that consists of each matrix in the path
        print('Pose array published')

    def RemoveTransforms(self):
        """
        Remove the transform & model nodes from the scene for visualization.
        """
        transforms = slicer.mrmlScene.GetNodesByClass("vtkMRMLLinearTransformNode")
        for j in range(0, transforms.GetNumberOfItems()):
            transform = transforms.GetItemAsObject(j)
            transformName = transform.GetName()
            if ("LinearTransform" in transformName):
                slicer.mrmlScene.RemoveNode(transform)

        models = slicer.mrmlScene.GetNodesByName("CoordinateModel")
        for j in range(0, models.GetNumberOfItems()):
            model = models.GetItemAsObject(j)
            slicer.mrmlScene.RemoveNode(model)



#
# RobotTrajectoryGeneratorTest
#

class RobotTrajectoryGeneratorTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_RobotTrajectoryGenerator1()

    def test_RobotTrajectoryGenerator1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('RobotTrajectoryGenerator1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = RobotTrajectoryGeneratorLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
