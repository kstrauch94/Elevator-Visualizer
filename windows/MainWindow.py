from PyQt4 import QtGui, QtCore

import VisConfig, SolverConfig
import ElevatorWindow, Widgets
from Constants import *



class MainWindow(QtGui.QWidget):
    """
    Main class. It creates a window with the parameters in the VisConfig.py file.
    It also creates the buttons and the windows for the encodings in the VisConfig.py file.
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setGeometry(VisConfig.width, VisConfig.height, VisConfig.width, VisConfig.height)
        self.setWindowTitle("Elevator")

        self.mainVbox = QtGui.QVBoxLayout() #will contain button HBox and another Hbox which contains Elevator Hbox and info Box

        self.initWindows()

        self.elevatorWindow2 = ElevatorWindow.ElevatorWindow()

        self.prepareMenuBar()

        self.prepareButtons()

        self.prepareInterface()

        self.setLayout(self.mainVbox)

        self.show()


    def initWindows(self):
        self.elevatorWindow = ElevatorWindow.ElevatorWindow()
        self.elevatorWindow.show()

        self.requestWindow = Widgets.RequestsWindow()

        self.planWindow = Widgets.PlanWindow()

    def prepareMenuBar(self):

        self.menuBar = QtGui.QMenuBar()
        self.menuBar.setNativeMenuBar(False)

        ### Load Menu
        loadMenu = self.menuBar.addMenu("Load")

        loadInstanceAction = QtGui.QAction("Load Instance", self)
        loadInstanceAction.triggered.connect(self.loadInstance)
        loadMenu.addAction(loadInstanceAction)

        loadEncodingAction = QtGui.QAction("Load Encoding", self)
        loadEncodingAction.triggered.connect(self.loadEncoding)
        loadMenu.addAction(loadEncodingAction)

        ### Window Menu
        windowMenu = self.menuBar.addMenu("Windows")

        reqWindow = QtGui.QAction("Show Requests", self)
        reqWindow.triggered.connect(lambda: self.requestWindow.show())
        windowMenu.addAction(reqWindow)

        planWindow = QtGui.QAction("Show Plan", self)
        planWindow.triggered.connect(lambda: self.planWindow.show())
        windowMenu.addAction(planWindow)

        self.mainVbox.addWidget(self.menuBar)


    def loadInstance(self):

        dialog = QtGui.QFileDialog()
        instance = str(dialog.getOpenFileName())

        if instance != "":
            self.elevatorWindow.elevatorInterface.bridge.instance = instance
            self.reset()

    def loadEncoding(self):

        dialog = QtGui.QFileDialog()
        encoding = str(dialog.getOpenFileName())

        if encoding != "":
            self.elevatorWindow.elevatorInterface.bridge.encoding = encoding
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

        floors = self.elevatorWindow.elevatorInterface.floors

        ok, type, floor = Widgets.CallRequestDialog.getRequest(floors, self)

        if ok:
            self.elevatorWindow.elevatorInterface.addRequest(REQ_CALL, type, floor)

    def addDeliverRequest(self):

        floors = self.elevatorWindow.elevatorInterface.floors
        elevs = self.elevatorWindow.elevatorInterface.elevatorCount

        ok, elev, floor = Widgets.DeliverRequestDialog.getRequest(floors, elevs, self)

        if ok:
            self.elevatorWindow.elevatorInterface.addRequest(REQ_DELIVER, elev, floor)


    def next(self):
        """
        Function is called when the "Next Action"button is pressed. It calls an update for every solver(encoding).
        :return: Void
        """
        self.elevatorWindow.next()
        self.elevatorWindow.repaint()

        self.updateInfo()

    def previous(self):
        """
        Function is called when the "Previous Action" button is pressed. It calls an update for every solver(encoding).
        :return: Void
        """
        self.elevatorWindow.previous()
        self.elevatorWindow.repaint()

        self.updateInfo()

    def updateInfo(self, *__args):

        self.instanceInfo["Current Step"].setText("Current Step : " + str(self.elevatorWindow.elevatorInterface.step))

        self.instanceInfo["Highest Step"].setText("Highest Step : " + str(self.elevatorWindow.elevatorInterface.highestStep))

        self.instanceInfo["Total Plan Length"].setText("Total Plan Length : " + str(self.elevatorWindow.elevatorInterface.planLength))

        self.instanceInfo["Current Requests"].setText("Current Requests : " + str(self.elevatorWindow.elevatorInterface.currentRequests))

        self.instanceInfo["Requests Completed"].setText("Requests Completed : " + str(self.elevatorWindow.elevatorInterface.requestCompleted))


        self.requestWindow.setRequests(self.elevatorWindow.elevatorInterface.requestsServed, self.elevatorWindow.elevatorInterface.addedRequests)

        self.planWindow.setPlan(self.elevatorWindow.elevatorInterface.plan)

    def prepareInterface(self):
        """
        Creates a window for every encoding. It also extracts the floor and agent amounts and stores them.
        :return: Void
        """
        self.ConfigInfoVbox = QtGui.QVBoxLayout()
        self.ConfigInfoVbox.setAlignment(QtCore.Qt.AlignLeft)

        #info is set in the setInterface function
        self.instanceInfo = {}

        text = "floors : " + str(self.elevatorWindow.elevatorInterface.floors)
        self.instanceInfo["floors"] = QtGui.QLabel(text, self)

        text = "Elevators : " + str(self.elevatorWindow.elevatorInterface.elevatorCount)
        self.instanceInfo["agents"] = QtGui.QLabel(text, self)

        self.instanceInfo["Current Step"] = QtGui.QLabel("Current Step : 0", self)

        self.instanceInfo["Highest Step"] = QtGui.QLabel("Highest Step : 0", self)

        self.instanceInfo["Total Plan Length"] = QtGui.QLabel("Total Plan Length : 0", self)

        self.instanceInfo["Current Requests"] = QtGui.QLabel("Current Requests : No Requests", self)

        self.instanceInfo["Requests Completed"] = QtGui.QLabel("Requests Completed : No Requests", self)



        self.ConfigInfoVbox.addWidget(self.instanceInfo["floors"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["agents"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Step"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Highest Step"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Total Plan Length"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Requests"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Requests Completed"])

        self.ConfigInfoVbox.addStretch(1)

        self.mainVbox.addLayout(self.ConfigInfoVbox)


    def reset(self):

        self.elevatorWindow.reset()
        self.elevatorWindow.repaint()

        self.planWindow.reset()
        self.requestWindow.reset()

        self.updateInfo()

