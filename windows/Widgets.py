from PyQt4 import QtGui, QtCore
from functools import partial

from math import ceil

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
