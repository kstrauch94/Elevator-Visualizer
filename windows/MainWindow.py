from PyQt4 import QtGui, QtCore

import VisConfig, SolverConfig
import ElevatorWindow
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

        self.menuBar = QtGui.QMenuBar()
        self.menuBar.setNativeMenuBar(False)
        self.prepareMenuBar()


        self.buttonsHbox = QtGui.QHBoxLayout() #HBox for the buttons
        self.buttonsHbox.setAlignment(QtCore.Qt.AlignLeft)

        self.ConfigInfoVbox = QtGui.QVBoxLayout()
        self.ConfigInfoVbox.setAlignment(QtCore.Qt.AlignLeft)

        #info is set in the setInterface function
        self.instanceInfo = {}
        self.setInterface()

        self.prepareButtons()

        self.mainVbox.addWidget(self.menuBar)
        self.mainVbox.addLayout(self.buttonsHbox)
        self.mainVbox.addLayout(self.ConfigInfoVbox)

        self.setLayout(self.mainVbox)

        self.show()


    def prepareMenuBar(self):

        loadMenu = self.menuBar.addMenu("Load")
        loadInstanceAction = QtGui.QAction("Load Instance", self)
        loadInstanceAction.triggered.connect(self.loadInstance)
        loadMenu.addAction(loadInstanceAction)

        loadEncodingAction = QtGui.QAction("Load Encoding", self)
        loadEncodingAction.triggered.connect(self.loadEncoding)
        loadMenu.addAction(loadEncodingAction)


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


    def addCallRequest(self):
        """
        Function called after pressing the "add call request" button. The input in the dialog is the direction("up" or "down")
        and the destination floor(an int). The input is stripped of whitespace and separated by comma.
        :return: Void
        """

        req, ok = QtGui.QInputDialog.getText(self, 'Request',
                                              'Call Request Parameters(direction, floor):')


        if ok:

            req = str(req).strip().split(",")
            dir = str(req[0]).lower()

            if dir != UPDIR and dir != DOWNDIR:
                print "Direction must be up or down"
                return


            try:
                floor = int(req[1])

            except ValueError:
                print "Floor must be an integer."
                return

            if floor < 1 or floor > self.instanceInfo["floors"]:
                print "Floor must be within range."
                return

            self.elevatorWindow.elevatorInterface.addRequest(REQ_CALL, dir, floor)

    def addDeliverRequest(self):
        """
        Function called after pressing the "add deliver request" button. The input in the dialog is the elevator id(an integer)
        and the destination floor(an int). The input is stripped of whitespace and separated by comma.
        :return: Void
        """
        req, ok = QtGui.QInputDialog.getText(self, 'Request',
                                             'Call Request Parameters(Elevator, floor):')

        if ok:
            req = str(req)
            req = req.strip().split(",")
            try:
                elevator = int(req[0])

            except ValueError:
                print "Elevator must be an integer."
                return

            if elevator > self.instanceInfo["agents"]:
                print "Elevator number must be within range"
                return
            elif elevator < 1:
                print "Elevator number must be a positive integer"
                return
            try:
                floor = int(req[1])

            except ValueError:
                print "Floor must be an integer."
                return

            if floor < 1 or floor > self.instanceInfo["floors"]:
                print "Floor must be within range."
                return

            self.elevatorWindow.elevatorInterface.addRequest(REQ_DELIVER, elevator, floor)

    def next(self):
        """
        Function is called when the "Next Action"button is pressed. It calls an update for every solver(encoding).
        :return: Void
        """
        self.elevatorWindow.next()
        self.elevatorWindow.repaint()

        self.update()

    def previous(self):
        """
        Function is called when the "Previous Action" button is pressed. It calls an update for every solver(encoding).
        :return: Void
        """
        self.elevatorWindow.previous()
        self.elevatorWindow.repaint()

        self.update()

    def update(self, *__args):

        self.instanceInfo["Current Step"].setText("Current Step : " + str(self.elevatorWindow.elevatorInterface.step))

        self.instanceInfo["Highest Step"].setText("Highest Step : " + str(self.elevatorWindow.elevatorInterface.highestStep))

        self.instanceInfo["Total Plan Length"].setText("Total Plan Length : " + str(self.elevatorWindow.elevatorInterface.planLength))

        self.instanceInfo["Current Requests"].setText("Current Requests : " + str(self.elevatorWindow.elevatorInterface.currentRequests))

    def setInterface(self):
        """
        Creates a window for every encoding. It also extracts the floor and agent amounts and stores them.
        :return: Void
        """
        # This list contains the reference to all the created windows for the encodings
        self.elevatorWindow = ElevatorWindow.ElevatorWindow()
        self.elevatorWindow.show()


        text = "floors : " + str(self.elevatorWindow.elevatorInterface.floors)
        self.instanceInfo["floors"] = QtGui.QLabel(text, self)

        text = "Elevators : " + str(self.elevatorWindow.elevatorInterface.elevatorCount)
        self.instanceInfo["agents"] = QtGui.QLabel(text, self)

        self.instanceInfo["Current Step"] = QtGui.QLabel("Current Step : 0", self)

        self.instanceInfo["Highest Step"] = QtGui.QLabel("Highest Step : 0", self)

        self.instanceInfo["Total Plan Length"] = QtGui.QLabel("Total Plan Length : 0", self)

        self.instanceInfo["Current Requests"] = QtGui.QLabel("Current Requests : No Requests", self)


        self.ConfigInfoVbox.addWidget(self.instanceInfo["floors"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["agents"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Step"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Highest Step"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Total Plan Length"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["Current Requests"])

        self.ConfigInfoVbox.addStretch(1)

    def reset(self):

        self.elevatorWindow.reset()
        self.elevatorWindow.repaint()

        self.update()

