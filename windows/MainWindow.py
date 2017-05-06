from PyQt4 import QtGui, QtCore

import VisConfig
import ElevatorWindow, Widgets
from Constants import *

import os

class MainWindow(QtGui.QMainWindow):
    """
    Main class. It creates a window with the parameters in the VisConfig.py file.
    It also creates the window that displays the instance and the plan + request windows.
    """

    def __init__(self, connMode):
        super(MainWindow, self).__init__()
        self.connMode = connMode

        self.setGeometry(VisConfig.width, VisConfig.height, VisConfig.width, VisConfig.height)
        self.setWindowTitle("Elevator")

        self.mainVbox = QtGui.QVBoxLayout()

        self.initWindows()

        self.prepareMenuBar()

        self.prepareButtons()

        self.prepareInterface()

        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.mainVbox)

        self.setCentralWidget(self.mainWidget)

        self.show()


    def initWindows(self):
        self.elevatorWindow = ElevatorWindow.ElevatorWindow()
        # Set comm via sockets of local
        self.elevatorWindow.elevatorInterface.setMode(self.connMode)
        self.elevatorWindow.show()

        self.requestWindow = Widgets.RequestsWindow()

        self.planWindow = Widgets.PlanWindow()

        #Conections for updates
        self.elevatorWindow.elevatorInterface.planChangedSignal.connect(self.planWindow.setPlan)
        self.elevatorWindow.elevatorInterface.requestChangedSignal.connect(self.requestWindow.setRequests)

    def prepareMenuBar(self):

        self.menuBar = QtGui.QMenuBar()
        self.menuBar.setNativeMenuBar(False)

        ### Load Menu
        loadMenu = self.menuBar.addMenu("Load")

        loadInstanceAction = QtGui.QAction("Load Instance", self)
        loadInstanceAction.triggered.connect(self.loadInstance)
        loadInstanceAction.setShortcut("Ctrl+I")
        loadMenu.addAction(loadInstanceAction)

        loadEncodingAction = QtGui.QAction("Load Encoding/LocalSolver", self)
        loadEncodingAction.triggered.connect(self.loadEncoding)
        loadEncodingAction.setShortcut("Ctrl+E")
        loadMenu.addAction(loadEncodingAction)

        ### Window Menu
        windowMenu = self.menuBar.addMenu("Windows")

        reqWindow = QtGui.QAction("Show Requests", self)
        reqWindow.triggered.connect(lambda: self.requestWindow.show())
        reqWindow.setShortcut("Ctrl+R")
        windowMenu.addAction(reqWindow)

        planWindow = QtGui.QAction("Show Plan", self)
        planWindow.triggered.connect(lambda: self.planWindow.show())
        planWindow.setShortcut("Ctrl+P")
        windowMenu.addAction(planWindow)

        ### Connect Menu
        connectMenu = self.menuBar.addMenu("Connect")

        connect = QtGui.QAction("Initialize Connection", self)
        connect.triggered.connect(self.initialize)
        connectMenu.addAction(connect)

        setConnInfo = QtGui.QAction("Set host/port", self)
        setConnInfo.triggered.connect(self.setConnectionInfo)
        connectMenu.addAction(setConnInfo)

        switch = QtGui.QAction("Use sockets Comms", self)
        switch.triggered.connect(lambda: self.switch(SOCKET))
        connectMenu.addAction(switch)

        switch = QtGui.QAction("Use local Comms", self)
        switch.triggered.connect(lambda: self.switch(LOCAL))
        connectMenu.addAction(switch)

        self.mainVbox.addWidget(self.menuBar)

    def initialize(self):
        """
        Function called when the instance information has been received from the connected solver
        """
        self.elevatorWindow.initialize()

    def setConnectionInfo(self):
        text, ok = QtGui.QInputDialog.getText(self, "Connection Details", "Enter HOST:PORT")

        if ok:
            text = text.split(":")
            host = str(text[0])
            port = int(text[1])
            print host, port
            self.elevatorWindow.elevatorInterface.setConnectionInfo(host, port)

    def switch(self, mode):
        """
        Switch to connection mode given in the parameter. Hard reset since solver changes. Need to make sure that the
        solver is in the correct state.
        :param mode: SOCKET or LOCAL
        """
        self.elevatorWindow.elevatorInterface.setMode(mode)
        self.hardReset()

    def loadInstance(self):
        """
        Changes the instance var in the elevatorInterface. Then it hardresets (Which in turn initializes again
        """

        dialog = QtGui.QFileDialog()
        instance = str(dialog.getOpenFileName(self, "Open File", os.getcwd(), "All files (*.*)", options=QtGui.QFileDialog.DontUseNativeDialog))

        self.instanceInfo["instance"].setText("Instance : " + instance)

        if instance != "":
            self.elevatorWindow.elevatorInterface.setInstance(instance)
            self.hardReset()

    def loadEncoding(self):
        """
        Receive some user input and send that same input to the solver
        """
        text, ok = QtGui.QInputDialog.getText(self, "Encoding", "Enter Encoding/LocalSolver Details: ")

        if ok:
            text = str(text)
            if self.elevatorWindow.elevatorInterface.sendEncoding(text):
                self.reset()

    def prepareButtons(self):
        #creates all buttons and adds them to the Hbox

        self.buttonsHbox = QtGui.QHBoxLayout()  # HBox for the buttons
        self.buttonsHbox.setAlignment(QtCore.Qt.AlignLeft)

        self.prevBtn = QtGui.QPushButton("Previous Action", self)
        self.prevBtn.clicked.connect(self.previous)
        self.prevBtn.resize(self.prevBtn.sizeHint())
        self.buttonsHbox.addWidget(self.prevBtn)

        self.nextBtn = QtGui.QPushButton("Next Action", self)
        self.nextBtn.clicked.connect(self.next)
        self.nextBtn.resize(self.nextBtn.sizeHint())
        self.buttonsHbox.addWidget(self.nextBtn)

        self.callRequestBtn = QtGui.QPushButton("Add Call Request", self)
        self.callRequestBtn.clicked.connect(self.addCallRequest)
        self.callRequestBtn.resize(self.callRequestBtn.sizeHint())
        self.buttonsHbox.addWidget(self.callRequestBtn)

        self.deliverRequestBtn = QtGui.QPushButton("Add Deliver Request", self)
        self.deliverRequestBtn.clicked.connect(self.addDeliverRequest)
        self.deliverRequestBtn.resize(self.deliverRequestBtn.sizeHint())
        self.buttonsHbox.addWidget(self.deliverRequestBtn)

        self.resetBtn = QtGui.QPushButton("Reset", self)
        self.resetBtn.clicked.connect(self.reset)
        self.resetBtn.resize(self.resetBtn.sizeHint())
        self.buttonsHbox.addWidget(self.resetBtn)

        self.mainVbox.addLayout(self.buttonsHbox)

    def addCallRequest(self):
        """
        Uses the Widget specific for this request defined in windows/Widgets.py
        """
        if self.elevatorWindow.hasInitialized:
            floors = self.elevatorWindow.elevatorInterface.floors

            ok, type, floor = Widgets.CallRequestDialog.getRequest(floors, self)

            if ok:
                if type is not None and floor is not None:
                    self.elevatorWindow.addRequest(REQ_CALL, type, floor)
                else:
                    print "Both, Type and floor, must be selected."


    def addDeliverRequest(self):
        """
        Uses the Widget specific for this request defined in windows/Widgets.py
        """
        if self.elevatorWindow.hasInitialized:
            floors = self.elevatorWindow.elevatorInterface.floors
            elevs = self.elevatorWindow.elevatorInterface.elevatorCount

            ok, elev, floor = Widgets.DeliverRequestDialog.getRequest(floors, elevs, self)

            if ok:
                if floor is not None and elev is not None:
                    self.elevatorWindow.addRequest(REQ_DELIVER, elev, floor)
                else:
                    print "Both, elevator and floor, must be selected."


    def next(self):
        """
        Function is called when the "Next Action" button is pressed.
        """
        self.elevatorWindow.next()
        self.updateInfo()

    def previous(self):
        """
        Function is called when the "Previous Action" button is pressed.
        """
        self.elevatorWindow.previous()
        self.updateInfo()

    def updateInfo(self):
        """
        Extract informaiton from the elevatorInterface and update the references
        """

        self.instanceInfo["Current Step"].setText("Current Step : " + str(self.elevatorWindow.elevatorInterface.step))

        self.instanceInfo["Highest Step"].setText("Highest Step : " + str(self.elevatorWindow.elevatorInterface.highestStep))

        self.instanceInfo["Total Plan Length"].setText("Total Plan Length : " + str(self.elevatorWindow.elevatorInterface.planLength))

        self.instanceInfo["Current Requests"].setText("Current Requests : " + str(self.elevatorWindow.elevatorInterface.currentRequests))

        self.instanceInfo["Requests Completed"].setText("Requests Completed : " + str(self.elevatorWindow.elevatorInterface.requestCompleted))

    def prepareInterface(self):
        """
        Creates a window for the instance. It also extracts information from it and initializes the information display
        """
        self.ConfigInfoVbox = QtGui.QVBoxLayout()
        self.ConfigInfoVbox.setAlignment(QtCore.Qt.AlignLeft)

        self.instanceInfo = {}

        # Instance
        self.instanceInfo["instance"] = QtGui.QLabel("Instance : " + VisConfig.instance)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["instance"])

        # Floors
        text = "floors : " + str(self.elevatorWindow.elevatorInterface.floors)
        self.instanceInfo["floors"] = QtGui.QLabel(text, self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["floors"])

        # Elevators
        text = "Elevators : " + str(self.elevatorWindow.elevatorInterface.elevatorCount)
        self.instanceInfo["agents"] = QtGui.QLabel(text, self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["agents"])

        # Current Step
        self.instanceInfo["Current Step"] = QtGui.QLabel("Current Step : " + str(self.elevatorWindow.elevatorInterface.step), self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Step"])

        # Highest Step
        self.instanceInfo["Highest Step"] = QtGui.QLabel("Highest Step : " + str(self.elevatorWindow.elevatorInterface.highestStep), self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Highest Step"])

        # Total plan length
        self.instanceInfo["Total Plan Length"] = QtGui.QLabel("Total Plan Length : " + str(self.elevatorWindow.elevatorInterface.planLength), self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Total Plan Length"])

        # Current Requests
        self.instanceInfo["Current Requests"] = QtGui.QLabel("Current Requests : " + str(self.elevatorWindow.elevatorInterface.currentRequests), self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Requests"])

        # Requests Completed
        self.instanceInfo["Requests Completed"] = QtGui.QLabel("Requests Completed : " + str(self.elevatorWindow.elevatorInterface.requestCompleted), self)
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Requests Completed"])

        self.ConfigInfoVbox.addStretch(1)

        self.mainVbox.addLayout(self.ConfigInfoVbox)


    def reset(self):
        """
        Makes a soft reset. Soft reset means that only resets variables, instance stays the same, hence no need to reset
        the visualization
        """
        self.elevatorWindow.reset()

        self.planWindow.reset()
        self.requestWindow.reset()

        self.updateInfo()

    def hardReset(self):
        """
        Hard reset is done just before changing instances, hence it also resets the visualization
        """

        self.elevatorWindow.hardReset()

        self.planWindow.reset()
        self.requestWindow.reset()

        self.updateInfo()

    def closeEvent(self, QCloseEvent):
        print "Clicking the x!"
        self.planWindow.close()
        self.requestWindow.close()
        self.elevatorWindow.close()

