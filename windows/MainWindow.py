from PyQt4 import QtGui, QtCore

import Config
import ElevatorWindow
from Constants import *



class MainWindow(QtGui.QWidget):
    """
    Main class. It creates a window with the parameters in the Config.py file.
    It also creates the buttons and the windows for the encodings in the Config.py file.
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setGeometry(Config.width, Config.height, Config.width, Config.height)
        self.setWindowTitle("Elevator")

        self.mainVbox = QtGui.QVBoxLayout() #will contain button HBox and another Hbox which contains Elevator Hbox and info Box

        self.buttonsHbox = QtGui.QHBoxLayout() #HBox for the buttons
        self.buttonsHbox.setAlignment(QtCore.Qt.AlignLeft)

        self.ConfigInfoVbox = QtGui.QVBoxLayout()
        self.ConfigInfoVbox.setAlignment(QtCore.Qt.AlignLeft)

        #info is set in the setInterface function
        self.instanceInfo = {}
        self.setInterface()

        self.prepareButtons()

        self.mainVbox.addLayout(self.buttonsHbox)
        self.mainVbox.addLayout(self.ConfigInfoVbox)

        self.setLayout(self.mainVbox)

        self.show()


    def prepareButtons(self):
        #creates all buttons and adds them to the Hbox

        self.updateBtn = QtGui.QPushButton("Next Action", self)
        self.updateBtn.clicked.connect(self.renew)
        self.updateBtn.resize(self.updateBtn.sizeHint())
        self.buttonsHbox.addWidget(self.updateBtn)

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

            for enc in self.elevatorWindows:
                #the double elevatorInterface is because this should only be used with elevatorInterfaceVis object (the first elevatorInterface) which
                #contains an elevatorInterface object (which is the second one) that actually will add the request to the solver
                enc.elevatorInterface.elevatorInterface.addRequest(REQ_CALL, dir, floor)

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

            for enc in self.elevatorWindows:
                # the double elevatorInterface is because this should only be used with elevatorInterfaceVis object (the first elevatorInterface) which
                # contains an elevatorInterface object (which is the second one) that actually will add the request to the solver
                enc.elevatorInterface.elevatorInterface.addRequest(REQ_DELIVER, elevator, floor)

    def renew(self):
        """
        Function is called when the "Next Action" button is pressed. It calls an update for every solver(encoding).
        :return: Void
        """
        for enc in self.elevatorWindows:
            enc.update()
            enc.repaint()

    def setInterface(self):
        """
        Creates a window for every encoding in the Cofig.py file. It also extracts the floor and agent amounts and stores them.
        :return: Void
        """
        # This list contains the reference to all the created windows for the encodings
        self.elevatorWindows = []

        id = 1
        for enc in Config.encoding:
            self.elevatorWindows.append(ElevatorWindow.ElevatorWindow(enc, id))
            self.elevatorWindows[-1].show()
            id += 1

        text = "Encoding(s) : " + str(Config.encoding)
        self.instanceInfo["encoding"] = QtGui.QLabel(text, self)

        text = "Instance : " + str(Config.instance)
        self.instanceInfo["instance"] = QtGui.QLabel(text, self)

        text = "floors : " + str(self.elevatorWindows[0].elevatorInterface.floors)
        self.instanceInfo["floors"] = QtGui.QLabel(text, self)

        text = "Elevators : " + str(self.elevatorWindows[0].elevatorInterface.elevatorCount)
        self.instanceInfo["agents"] = QtGui.QLabel(text, self)

        self.ConfigInfoVbox.addWidget(self.instanceInfo["encoding"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["instance"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["floors"])
        self.ConfigInfoVbox.addWidget(self.instanceInfo["agents"])
        self.ConfigInfoVbox.addStretch(1)

    def reset(self):

        for enc in self.elevatorWindows:
            enc.reset()
            enc.repaint()


