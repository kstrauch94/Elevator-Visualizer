from PyQt4 import QtGui, QtCore
from functools import partial

from math import ceil

import os

import Constants

class CallRequestDialog(QtGui.QDialog):

    def __init__(self, floorAmt, parent = None,):
        super(CallRequestDialog, self).__init__(parent)

        self.setWindowTitle("Call Request")

        self.cols = 5

        self.type = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.type, self.floor))
        self.mainVBox.addWidget(self.reqLabel)

        self.setTypeButtons()
        self.setFloorButtons(floorAmt)

        buttons = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                        QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.mainVBox.addWidget(buttons)

        self.setLayout(self.mainVBox)

        self.show()

    def setTypeButtons(self):

        hbox = QtGui.QHBoxLayout()

        self.upBtn = QtGui.QPushButton("Up", self)
        self.upBtn.clicked.connect(lambda: self.setType(Constants.UPDIR))
        self.upBtn.resize(self.upBtn.sizeHint())
        hbox.addWidget(self.upBtn)

        self.downBtn = QtGui.QPushButton("Down", self)
        self.downBtn.clicked.connect(lambda: self.setType(Constants.DOWNDIR))
        self.downBtn.resize(self.downBtn.sizeHint())
        hbox.addWidget(self.downBtn)

        self.mainVBox.addLayout(hbox)

    def setFloorButtons(self,floorAmt):

        self.grid = QtGui.QGridLayout()

        rows = int(ceil(floorAmt/float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols*i + j+1 <= floorAmt:
                    button = QtGui.QPushButton(str(self.cols*i + j+1))
                    self.buttons[i,j] = button
                    button.clicked.connect(partial(self.setFloor, self.cols*i + j+1))

                    self.grid.addWidget(self.buttons[i,j], i, j)

        self.mainVBox.addLayout(self.grid)

    def setType(self, dir):
        self.type = dir

        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.type, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.type, self.floor))

    @staticmethod
    def getRequest(floors, parent=None):
        dialog = CallRequestDialog(floors, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.type, dialog.floor)

class DeliverRequestDialog(QtGui.QDialog):

    def __init__(self, floorAmt, elevAmt, parent=None, ):
        super(DeliverRequestDialog, self).__init__(parent)

        self.setWindowTitle("Deliver Request")

        self.cols = 5

        self.elevator = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.elevator, self.floor))
        self.mainVBox.addWidget(self.reqLabel)

        self.setElevatorButtons(elevAmt)
        self.setFloorButtons(floorAmt)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.mainVBox.addWidget(buttons)

        self.setLayout(self.mainVBox)

        self.show()

    def setElevatorButtons(self, elevAmt):

        self.elevatorGrid = QtGui.QGridLayout()

        rows = int(ceil(elevAmt / float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols * i + j + 1 <= elevAmt:
                    button = QtGui.QPushButton("Elev " + str(self.cols * i + j + 1))
                    self.buttons[i, j] = button
                    button.clicked.connect(partial(self.setElevator, self.cols * i + j + 1))

                    self.elevatorGrid.addWidget(self.buttons[i, j], i, j)

        self.mainVBox.addLayout(self.elevatorGrid)


    def setFloorButtons(self, floorAmt):

        self.floorGrid = QtGui.QGridLayout()

        rows = int(ceil(floorAmt / float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols * i + j + 1 <= floorAmt:
                    button = QtGui.QPushButton(str(self.cols * i + j + 1))
                    self.buttons[i, j] = button
                    button.clicked.connect(partial(self.setFloor, self.cols * i + j + 1))

                    self.floorGrid.addWidget(self.buttons[i, j], i, j)

        self.mainVBox.addLayout(self.floorGrid)

    def setElevator(self, elev):
        self.elevator = elev

        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.elevator, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Type : {} \nFloor : {}".format(self.elevator, self.floor))

    @staticmethod
    def getRequest(floors, elevs, parent=None):
        dialog = DeliverRequestDialog(floors, elevs, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.elevator, dialog.floor)

class RequestsWindow(QtGui.QWidget):

    def __init__(self):
        super(RequestsWindow, self).__init__()
        self.setWindowTitle("Requests")

        self.served = {}
        self.added = {}

        self.vbox = QtGui.QVBoxLayout()

        self.headerServed = QtGui.QLabel("No Requests Served")
        self.servedVBox = QtGui.QVBoxLayout()
        self.servedVBox.addWidget(self.headerServed)

        self.headerAdded = QtGui.QLabel("No Requests Added")
        self.addedVBox = QtGui.QVBoxLayout()
        self.addedVBox.addWidget(self.headerAdded)

        self.vbox.addLayout(self.servedVBox)
        self.vbox.addLayout(self.addedVBox)

        self.setLayout(self.vbox)

    def setRequests(self, served, added):

        for time in served:
            if served[time] != []:
                string = "In step " + str(time) + " : " + ", ".join(served[time])
                if time not in self.served:
                    label = QtGui.QLabel(string, self)
                    self.served[time] = label
                    self.servedVBox.addWidget(label)
                else:
                    self.served[time].setText(string)


        for time in added:
            string = "In step " + str(time) + " : " + ",  ".join(added[time])
            if time not in self.added:
                label = QtGui.QLabel(string, self)
                self.added[time] = label
                self.addedVBox.addWidget(label)
            else:
                self.added[time].setText(string)

        if self.served != {}:
            self.headerServed.setText("Served Requests: ")

        if self.added != {}:
            self.headerAdded.setText("Added Requests: ")

    def reset(self):
        for i in reversed(range(self.addedVBox.count())):
            self.addedVBox.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.servedVBox.count())):
            self.servedVBox.itemAt(i).widget().setParent(None)

        self.served = {}
        self.added = {}

        self.headerAdded.setText("No Requests Added")
        self.addedVBox.addWidget(self.headerAdded)

        self.headerServed.setText("No Requests Served")
        self.servedVBox.addWidget(self.headerServed)




class PlanWindow(QtGui.QWidget):

    def __init__(self):
        super(PlanWindow, self).__init__()
        self.setWindowTitle("Plan")

        # images for the actions
        self.actionpic = QtGui.QLabel(self)
        # images
        self.imagedict = {}
        self.imagedict[Constants.UP] = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.imagedict[Constants.DOWN] = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.imagedict[Constants.WAIT] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[Constants.SERVE] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[Constants.NONEACT] = QtGui.QPixmap(os.getcwd() + "/res/none.png")

        self.vbox = QtGui.QVBoxLayout()

        self.elevatorHBox = QtGui.QHBoxLayout()

        self.elevatorVBoxDict = {}
        self.elevatorActionDict = {}

        self.vbox.addLayout(self.elevatorHBox)

        self.setLayout(self.vbox)

    def setPlan(self, plan):

        if plan != {}:

            if self.elevatorHBox.count() == 0:
                #Adding the time step vbox
                vbox = QtGui.QVBoxLayout()
                label = QtGui.QLabel("Step")
                vbox.addWidget(label)

                for i in range(len(plan[1])):
                    #Adding a vbox for every elevator
                    vbox = QtGui.QVBoxLayout()
                    label = QtGui.QLabel("Elev " + str(i+1))
                    vbox.addWidget(label)

                    self.elevatorActionDict[i+1] = {}

                    self.elevatorVBoxDict[i+1] = vbox
                    self.elevatorHBox.addLayout(vbox)

            for time in plan:
                for move in plan[time]:
                    elev = move[0]
                    action = move[1]

                    if time not in self.elevatorActionDict[elev]:
                        label = QtGui.QLabel(self)
                        label.setPixmap(self.imagedict[action])
                        self.elevatorActionDict[elev][time] = label
                        self.elevatorVBoxDict[elev].addWidget(label)

                    else:
                        self.elevatorActionDict[elev][time].setPixmap(self.imagedict[action])

    def reset(self):

        self.vbox = QtGui.QVBoxLayout()

        #for every vbox in the dict
        for i in range(len(self.elevatorVBoxDict)):
            #for every element in the vbox
            for j in reversed(range(self.elevatorVBoxDict[i+1].count())):
                self.elevatorVBoxDict[i+1].itemAt(j).widget().setParent(None)

        for i in reversed(range(self.elevatorHBox.count())):
            self.elevatorHBox.itemAt(i).layout().setParent(None)

        self.elevatorVBoxDict = {}
        self.elevatorActionDict = {}



