from PyQt4 import QtGui, QtCore
from functools import partial

from math import ceil

import os

import Constants

class CallRequestDialog(QtGui.QDialog):
    """
    Custom dialog to handle call requests. Has 2 buttons for the "up" or "down" direction and one button for each floor.
    """

    def __init__(self, floorAmt, parent = None,):
        super(CallRequestDialog, self).__init__(parent)

        self.setWindowTitle("Call Request")

        # Columns for the floors. There will me max 5 floors in a row
        self.cols = 5

        self.type = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))
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
        """
        Set up the "call" and the "down" buttons. Clicking them gives their respective value to the self.type variable
        :return:
        """

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
        """
        Makes rows of buttons for the floors. There is a max for self.cols buttons for every row. Clicking them gives
        value to the self.floor variable.
        :param floorAmt: Amount of floors (int)
        """

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

        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))

    @staticmethod
    def getRequest(floors, parent=None):
        """
        This method should get called when using this dialog.
        :param floors: floor amount
        :param parent: parent widget
        :return:
        """
        dialog = CallRequestDialog(floors, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.type, dialog.floor)

class DeliverRequestDialog(QtGui.QDialog):
    """
    Custom dialog class for the deliver request. Sets up buttons for every elevator and for every floor.
    """

    def __init__(self, floorAmt, elevAmt, parent=None, ):
        super(DeliverRequestDialog, self).__init__(parent)

        self.setWindowTitle("Deliver Request")

        self.cols = 5

        self.elevator = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))
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
        """
        Set a button for every elevator with a max of self.cols per row. Clicking one populates the self.elevator var
        :param elevAmt: amount of elevators
        """

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
        """
        Makes rows of buttons for the floors. There is a max for self.cols buttons for every row. Clicking them gives
        value to the self.floor variable.
        :param floorAmt: Amount of floors (int)
        """

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

        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))

    @staticmethod
    def getRequest(floors, elevs, parent=None):
        """
        This method should get called when using this dialog.
        :param floors: Floor amount
        :param elevs: Amount of elevators
        :param parent: Parent widget
        :return:
        """
        dialog = DeliverRequestDialog(floors, elevs, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.elevator, dialog.floor)


class RequestsWindow(QtGui.QWidget):
    """
    Window that displays when a request was completed and when a request was added
    """

    def __init__(self):
        super(RequestsWindow, self).__init__()
        self.setWindowTitle("Requests")

        self.hbox = QtGui.QHBoxLayout()

        self.served = RequestBox("No Requests Served", "Served Requests: ")
        self.added = RequestBox("No Requests Added", "Added Requests: ")

        self.hbox.addWidget(self.served)
        self.hbox.addWidget(self.added)

        self.setLayout(self.hbox)

    @QtCore.pyqtSlot(dict, dict)
    def setRequests(self, served, added):
        """
        This function gets called when the ElevatorInterface class emits a signal that the requests changed.
        :param served: list of served requests per time point
        :param added: list of added requests per time point
        """

        self.served.setRequests(served)
        self.added.setRequests(added)

    def reset(self):
        self.served.reset()
        self.added.reset()

class RequestBox(QtGui.QWidget):
    """
    Holder class for the request dictionary. Displays some header text and the values of the dictionary in a formatted way
    """

    def __init__(self, emptyStr, Str):
        super(RequestBox, self).__init__()

        self.reqs = {}
        # This are the header Strings, one for the empty dict and one for a populated one
        self.emptyStr = emptyStr
        self.notemptyStr = Str

        # The stretcher is just a way to keep the requests at the top while being able to add to the layout dynamically
        self.StretcherVBox = QtGui.QVBoxLayout()
        self.header = QtGui.QLabel(self.emptyStr)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.header)
        self.StretcherVBox.addLayout(self.vbox)
        self.StretcherVBox.addStretch(1)

        self.setLayout(self.StretcherVBox)

    def setRequests(self, new):
        """
        receive the dictionary with the requests, format it and create a label for it. Also keep the references. If time
        point in dict was already handled just update the variable.
        :param new: dictionary with the requests
        :return:
        """

        for time in new:
            if new[time] != []:
                string = "In step " + str(time) + " : " + ",  ".join(new[time])
                if time not in self.reqs:
                    label = QtGui.QLabel(string, self)
                    self.reqs[time] = label
                    self.vbox.addWidget(label)
                else:
                    self.reqs[time].setText(string)

        if self.reqs != {}:
            self.header.setText(self.notemptyStr)

    def reset(self):

        # Delete all references to the widgets so that they can be garbage collected
        for i in reversed(range(self.vbox.count())):
            self.vbox.itemAt(i).widget().setParent(None)

        self.reqs = {}

        self.header.setText(self.emptyStr)
        self.vbox.addWidget(self.header)


class PlanWindow(QtGui.QWidget):
    """
    Window that displays the actions of the plan in a table like way
    """

    def __init__(self):
        super(PlanWindow, self).__init__()
        self.setWindowTitle("Plan")

        self.vbox = QtGui.QVBoxLayout()
        self.planWidget = PlanWidget()

        self.headerText = QtGui.QLabel("No Plan yet")
        self.headerButton = QtGui.QPushButton("Toggle Action Text")
        self.headerButton.clicked.connect(self.planWidget.toggleText)
        self.headerButton.resize(self.headerButton.sizeHint())

        self.header = QtGui.QHBoxLayout()
        self.header.addWidget(self.headerText)
        self.header.addWidget(self.headerButton)

        self.scroller = QtGui.QScrollArea()
        self.scroller.setWidget(self.planWidget)
        self.scroller.setWidgetResizable(True)

        self.vbox.addLayout(self.header)
        self.vbox.addWidget(self.scroller)

        self.setLayout(self.vbox)

    @QtCore.pyqtSlot(dict)
    def setPlan(self, plan):
        """
        Function gets called when the ElevatorInterface emits a signal that says the plan changed. Passes the plan to
        the widget so that it can be handled
        :param plan: dictionary with the actions
        """

        if plan != {}:
            self.headerText.setText("--- Plan ---")

        self.planWidget.setPlan(plan)

    def reset(self):
        self.planWidget.reset()
        self.headerText.setText("No Plan yet")


class PlanWidget(QtGui.QWidget):
    """
    Widget that has the actual layout of the plan window. Populates a grid layout where the headers are the elevators
    and the left side has the time step number. The actions are handled by a separate widget.
    """

    def __init__(self, parent = None):
        super(PlanWidget, self).__init__(parent)

        self.showText = True

        self.vbox = QtGui.QVBoxLayout()

        self.elevatorGrid = QtGui.QGridLayout()
        self.vbox.addLayout(self.elevatorGrid)
        self.vbox.addStretch(1)

        self.elevatorActionDict = {}

        self.setLayout(self.vbox)

    def setPlan(self, plan):
        """
        Sets the headers and the time point labels on the left side. Also creates the "Action Widgets" for the actions
        and puts them in their respective way.
        :param plan: dictionary with the actions
        """

        if plan != {}:

            if self.elevatorGrid.count() == 0:
                for move in plan[1]:
                    elev = move[0]
                    label = QtGui.QLabel("Elev " + str(elev))
                    self.elevatorGrid.addWidget(label, 0, elev)

            for time in plan:
                if not self.elevatorGrid.itemAtPosition(time, 0):
                    label = QtGui.QLabel("Step " + str(time), self)
                    self.elevatorGrid.addWidget(label, time, 0)

                for move in plan[time]:
                    elev = move[0]
                    action = move[1]

                    if not self.elevatorGrid.itemAtPosition(time, elev):
                        actionwidget = ActionWidget(action, self.showText)
                        self.elevatorActionDict[time, elev] = actionwidget
                        self.elevatorGrid.addWidget(actionwidget, time, elev)
                    else:
                        self.elevatorGrid.itemAtPosition(time, elev).widget().setAction(action)

    def toggleText(self):
        """
        Just toggle if the text shows or not
        """

        self.showText = not self.showText

        if len(self.elevatorActionDict) != 0:
            for item in self.elevatorActionDict:
                self.elevatorActionDict[item].setVisibleText(self.showText)


    def reset(self):

        for i in reversed(range(self.elevatorGrid.count())):
            self.elevatorGrid.itemAt(i).widget().setParent(None)


        self.elevatorActionDict = {}


class ActionWidget(QtGui.QWidget):
    """
    Widget that handles what will be displayed in the plan window for a single action. Contains references to the images
    and displays text if enabled.
    """

    def __init__(self, action, displayText = False):
        super(ActionWidget, self).__init__()

        # images
        self.imagedict = {}
        self.imagedict[Constants.UP] = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.imagedict[Constants.DOWN] = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.imagedict[Constants.WAIT] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[Constants.SERVE] = QtGui.QPixmap(os.getcwd() + "/res/serve.png")
        self.imagedict[Constants.NONEACT] = QtGui.QPixmap(os.getcwd() + "/res/none.png")

        # Action text
        self.textDict = {}
        self.textDict[Constants.UP] = Constants.UPTEXT
        self.textDict[Constants.DOWN] = Constants.DOWNTEXT
        self.textDict[Constants.SERVE] = Constants.SERVETEXT
        self.textDict[Constants.WAIT] = Constants.WAITTEXT
        self.textDict[Constants.NONEACT] = Constants.NONEACTTEXT

        # Actual var that will contain the picture
        self.picture = QtGui.QLabel(self)
        self.picture.setPixmap(self.imagedict[action])
        if self.imagedict[action].isNull():
            self.picture.hide()

        self.text = QtGui.QLabel(self.textDict[action], self)
        if not displayText:
            self.text.hide()

        self.vbox = QtGui.QVBoxLayout()

        self.vbox.addWidget(self.picture)
        self.vbox.addWidget(self.text)

        self.setLayout(self.vbox)

    def setAction(self, action):

        self.picture.setPixmap(self.imagedict[action])
        # if the image could not be loaded hide the label so that the text is at a normal height
        if self.imagedict[action].isNull():
            self.picture.hide()
        else:
            self.picture.show()

        self.text.setText(self.textDict[action])

    def setVisibleText(self, bool):
        if bool:
            self.text.show()
        else:
            self.text.hide()