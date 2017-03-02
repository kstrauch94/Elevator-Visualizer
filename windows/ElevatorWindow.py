import os
import time
from PyQt4 import QtGui, QtCore

import VisConfig
from Constants import *
import VisClient
import LocalClient


class ElevatorVis(QtGui.QWidget):
    """Visualizer Class for an individual Elevator"""
    def __init__(self, size):
        """
        :param size: size of the squares
        """
        super(ElevatorVis, self).__init__()

        self.size = size

        # data
        self.floors = None
        self.currentFloor = None
        self.lastAction = None

        self.xpos = 0
        self.ypos = 0

        # images for the actions
        self.actionpic = QtGui.QLabel(self)
        self.imagedict = {}
        self.imagedict[UP] = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.imagedict[DOWN] = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.imagedict[WAIT] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[SERVE] = QtGui.QPixmap(os.getcwd() + "/res/serve.png")
        self.imagedict[NONEACT] = QtGui.QPixmap(os.getcwd() + "/res/none.png")

    def setDrawPos(self, x, y):
        """
        :param x: usually left as 0 as the pyQT layout manages the position
        :param y: should be the position when on floor 1 (ground floor), basically the height of the whole elevator "shaft"7
                  Should be floors * size
        :return: void
        """

        self.xpos = x
        self.ypos = y

    def paintEvent(self, QPaintEvent):
        qp = QtGui.QPainter()
        qp.begin(self)

        self.drawWidget(qp)

        qp.end()
        time.sleep(0.01)

    def updateElevator(self, elevator):
        """
        Get elevator data object to display on the next draw call
        :param elevator: elevator data object
        :return: void
        """
        self.floors = elevator.floors
        self.currentFloor = elevator.currentFloor
        self.lastAction = elevator.lastAction
        self.update()

    def drawWidget(self, qp):

        color = QtGui.QColor(0, 0, 0)
        qp.setPen(color)

        #draw floor squares plus numbers
        qp.drawLine(self.xpos, self.ypos, self.xpos, self.ypos - self.floors * self.size)
        qp.drawLine(self.xpos + self.size, self.ypos, self.xpos + self.size, self.ypos - self.floors * self.size)

        for f in range(0, self.floors + 1):
            y = self.ypos - f * self.size
            qp.drawLine(self.xpos, y, self.xpos + self.size, y)

            if f != self.floors:
                qp.setFont(QtGui.QFont('Decorative', 15))
                text = "%d" %(f+1)
                #NOTE the x and y pos for the text is the BOTTOM LEFT part
                qp.drawText(self.xpos + 2, y - 2, text)

        # Draw the elevator square
        if self.lastAction == SERVE:
            qp.setBrush(QtGui.QColor(0, 200, 0))
        else:
            qp.setBrush(QtGui.QColor(200, 0, 0))

        #the +2 and -4 are to make the elevator square a bit smaller than the floor box
        #should probably add a variable for those :v
        qp.drawRect(self.xpos + 2, self.ypos + 2 - self.currentFloor * self.size, self.size - 4, self.size - 4)

        # draw image of last action
        if self.lastAction != None:
            self.actionpic.setPixmap(self.imagedict[self.lastAction])

        # the +15 after ypos is to separate the image from the elevator a bit
        self.actionpic.setGeometry((self.size-32)/2, self.ypos + 15, self.size, self.size)

class Elevator():
    """
    Elevator data class. Keeps track of the elevator position, history and current +last step.
    """
    def __init__(self, floors, startPos):

        self.floors = floors
        self.step = 0
        self.lastStep = 0
        self.history = [startPos]

        self.moveDict = {}
        self.moveDict[UP] = 1
        self.moveDict[DOWN] = -1
        self.moveDict[WAIT] = 0
        self.moveDict[SERVE] = 0
        self.moveDict[NONEACT] = 0


        self.actionHistory = [NONEACT]

    def execute(self, action):
        """
        Depending on the action is goes up, down or stays.
        This should only be called with a new action that directly follows the last one completed
        :param action: Action as defined in the Constants.py file
        """
        currentFloor = self.history[self.lastStep]
        self.actionHistory.append(action)
        if action == DOWN and currentFloor == 1:
            print "Invalid move, trying to move down when already at the bottom floor."
            return

        if action == UP and currentFloor == self.floors:
            print "Invalid move, trying to move up when already at the top floor."
            return

        self.history.append(self.currentFloor + self.moveDict[action])

        self.lastStep += 1

    def next(self):
        if self.step < self.lastStep:
            self.step += 1

    def previous(self):
        if self.step > 0:
            self.step -= 1

    @property
    def currentFloor(self):
        return self.history[self.step]

    @property
    def lastAction(self):
        return self.actionHistory[self.step]

    def reset(self):
        self.step = 0
        self.lastStep = 0
        self.history = [self.history[0]]
        self.actionHistory = [NONEACT]

class ElevatorInterfaceVis(QtGui.QWidget):
    """
    Visualizer for the whole instance. Keeps track of every elevator visualizer in the instance.
    """
    def __init__(self, size):
        """
        Initialize core visualization stuff. It is necessary to pass the data object to the initialize function
        after creating the object.
        :param size: size of the squares that represent the floors, usually defined in the VisConfig.py file
        """
        super(ElevatorInterfaceVis, self).__init__()

        self.size = size

        self.hbox = QtGui.QHBoxLayout()

        self.setLayout(self.hbox)


    def initialize(self, elevatorInterface):

        # calculate the total height of the shaft
        self.ypos = self.size * elevatorInterface.floors

        self.createElevVis(elevatorInterface.elevatorCount, elevatorInterface.floors)
        self.updateElevators(elevatorInterface)


    def createElevVis(self, elevatorCount, floors):
        """
        Create a visualizer for every elevator in the instance and add it to the layout.
        """
        self.elevatorsVis = []
        for i in range(elevatorCount):
            vis = ElevatorVis(self.size)
            vis.setDrawPos(0, self.ypos)
            # the +2 after the floors thing is to also include the images
            vis.setMinimumSize(self.size + 4, self.size * (floors + 2) + 4)

            self.elevatorsVis.append(vis)
            self.hbox.addWidget(vis)


    def updateElevators(self, elevatorInterface):
        """
        updated object needs to be passed to the individual elevator visualizers.
        """
        for i in range(0, len(self.elevatorsVis)):
            self.elevatorsVis[i].updateElevator(elevatorInterface.elevators[i])

    def reset(self):
        """
        Resets the whole interface and deletes the old elevator visualizers from the layout container.
        """
        for i in reversed(range(self.hbox.count())):
            self.hbox.itemAt(i).widget().setParent(None)




class ElevatorInterface(QtCore.QObject):
    """
    Data class for the whole instance. Keeps track of every individual elevator.
    """

    #Signals that update the plan and request windows
    planChangedSignal = QtCore.pyqtSignal(dict)
    requestChangedSignal = QtCore.pyqtSignal(dict, dict)

    def __init__(self):

        super(ElevatorInterface, self).__init__()

        self.solverConns = {SOCKET: VisClient.VisSocket(), LOCAL: LocalClient.Connect()}
        self.mode = LOCAL

        self.elevatorCount = None
        self.floors = None
        self.elevators = []

        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.plan = {}
        self.initialReqs = None
        self.requestInfo = None
        self.addedRequests = {}

        self.requestsServed = {}

        self.hasToSolve = True

        self.setInstance(VisConfig.instance)

    def setMode(self, mode):
        if mode != LOCAL and mode != SOCKET:
            print "Invalid mode: " + str(mode)
            return 0
        self.mode = mode

    def setConnectionInfo(self, host, port):

        self.bridge.setHost(host)
        self.bridge.setPort(port)

    def initialize(self):
        # Connect and get instance base
        if not self.bridge.reset("hard"):
            return 0
        if not self.bridge.sendBaseRequest(self.instanceStr):
            return 0

        self.elevatorCount = self.bridge.getElevatorAmt()
        self.floors = self.bridge.getFloorAmt()
        self.initialReqs = self.bridge.getRequests()
        self.requestInfo = self.initialReqs.copy()

        self.setElevators()

        return 1

    def setInstance(self, instance):
        self.instance = instance
        with open(self.instance, 'r') as myfile:
            self.instanceStr = myfile.read()

    def sendEncoding(self, encoding):
        return self.bridge.sendEncoding(encoding)

    def setElevators(self):
        """
        Create elevator data object for every elevator
        """
        self.elevators = []

        for i in range(1, self.elevatorCount + 1):
            elevatorStart = self.bridge.startingPosition(i)
            elevator = Elevator(self.floors, elevatorStart)

            self.elevators.append(elevator)


    def next(self):
        """
        increase step count by 1 if its possible. Solve again if a request has been added.
        Also call the next function for every elevator if step count was increased.
        """

        if self.hasToSolve and self.step == self.highestStep:
            if not self.solve():
                return 0
            self.hasToSolve = False



        if len(self.plan) > self.step:
            self.step += 1

            if self.step - 1 == self.highestStep:
                self.highestStep += 1

                moves = self.plan[self.step]
                for move in moves:
                    # get elevator ID
                    elevator = move[0]
                    action = move[1]
                    self.elevators[elevator - 1].execute(action)



            for e in self.elevators:
                e.next()

        return 1
    def previous(self):
        """
        Lowers step value. if counter is at 1 (lowest) -> do nothing
        """

        if self.step >= 1:
            self.step -= 1

            for e in self.elevators:
                e.previous()



    def solve(self):
        """
        Retrieve plan from bridge by calling nextMoves(Which calls the actual solver).
        Process the plan + requests and emit signals that they changed
        """
        self.plan = self.bridge.nextMoves(self.highestStep)
        if self.plan == 0:
            return 0
        self.planLength = int(max(self.plan))

        self.fillPlan()

        self.requestInfo = self.bridge.getRequests()
        if 0 in self.requestInfo:
            self.addedRequests[0] = self.requestInfo[0]

        self.parseRequests()

        self.planChangedSignal.emit(self.plan)
        self.requestChangedSignal.emit(self.requestsServed, self.addedRequests)

        return 1

    def fillPlan(self):
        """
        Fills the spots in the plan with no actions to contain a NONEACT.
        """

        for t in range(1, self.planLength + 1):
            if t in self.plan:
                if len(self.plan[t]) != self.elevatorCount:
                    elevs = range(1, self.elevatorCount+1)
                    for move in self.plan[t]:
                        elevs.remove(move[0])

                    for e in elevs:
                        self.plan[t].append([e, NONEACT])
            else:
                elevs = range(1, self.elevatorCount + 1)
                self.plan[t] = []
                for e in elevs:
                    self.plan[t].append([e, NONEACT])


    def parseRequests(self):
        """
        Sees if a request was completed by comparing time steps. If a request is in time T but not in T+1 then it was completed
        """

        self.requestsServed = self.requestInfo.copy()

        for time in self.requestInfo:
            completed = []
            if time+1 in self.requestInfo:
                for req in self.requestInfo[time]:
                    if req not in self.requestInfo[time+1]:
                        completed.append(req)
            else:
                for req in self.requestInfo[time]:
                    completed.append(req)

            self.requestsServed[time+1] = completed

        self.requestsServed[0] = []

    def addRequest(self, type, params):
        """
        Add request to the solver and keep track of it
        :param type: request type
        :param params: parameters of the request
        """
        self.hasToSolve = True
        if not self.bridge.addRequest(type, self.highestStep, params):
            return 0

        if type == REQ_CALL:
            string = "call({}) to {}".format(params[0], params[1])
        elif type == REQ_DELIVER:
            string = "deliver({}) from {}".format(params[0], params[1])

        if self.highestStep not in self.addedRequests:
            self.addedRequests[self.highestStep] = [string]
        else:
            self.addedRequests[self.highestStep].append(string)

        return 1

    def getStats(self):
        """
        It just calls the getStats function from the encoding manager (solver) and return the value
        :return: list of Stat objects
        """

        return self.bridge.getStats()

    def reset(self):
        """
        Creates a new solver object so that it reloads everything. Resets every tracking variable
        It also creates the elevetor objects again.
        """
        self.bridge.reset("soft")
        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        for e in self.elevators:
            e.reset()

        self.plan = {}
        self.requestInfo = self.initialReqs.copy()
        self.addedRequests = {}

        self.requestsServed = {}


        self.hasToSolve = True


    def hardReset(self):
        self.bridge.reset("hard")
        self.elevatorCount = None
        self.floors = None
        self.elevators = []

        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.plan = {}
        self.initialReqs = None
        self.requestInfo = None
        self.addedRequests = {}

        self.requestsServed = {}

        self.hasToSolve = True

    @property
    def requestCompleted(self):
        try:
            return ", ".join(self.requestsServed[self.step])
        except (TypeError, KeyError):
            return "No Requests"

    @property
    def currentRequests(self):
        try:
            return ", ".join(self.requestInfo[self.step])
        except (TypeError, KeyError):
            return "No Requests"

    @property
    def bridge(self):
        return self.solverConns[self.mode]

class ElevatorWindow(QtGui.QWidget):
    """
    Class that controls the interaction between the elevator interface and its visualizer. Also holds a stats panel
    """
    def __init__(self, parent = None):
        super(ElevatorWindow, self).__init__(parent)

        self.setGeometry(VisConfig.width, VisConfig.height, VisConfig.width, VisConfig.height)
        self.setWindowTitle("Instance")
        self.move(0, 0)

        self.elevatorInterface = ElevatorInterface()
        self.elevatorInterfaceVis = ElevatorInterfaceVis(VisConfig.size)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.elevatorInterfaceVis)
        self.scrollArea.setWidgetResizable(True)

        self.infoPanel = InfoPanel()

        self.hbox = QtGui.QHBoxLayout()

        self.hbox.addWidget(self.scrollArea)
        self.hbox.addWidget(self.infoPanel)

        self.setLayout(self.hbox)

        self.hasInitialized = False


    def initialize(self):

        if not self.elevatorInterface.initialize():
            print "Could not Initialize. Can't connect to server."
            return 0
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

        self.hasInitialized = True

        return 1

    def updateAll(self):
        self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)
        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

    def next(self):
        if self.hasInitialized:
            if not self.elevatorInterface.next():
                print "Could not solve. Can't connect to server."
                return 0
            self.updateAll()

        return 1

    def previous(self):
        if self.hasInitialized:
            self.elevatorInterface.previous()
            self.updateAll()

    def addRequest(self, type, *params):
        if not self.elevatorInterface.addRequest(type, params):
            print "Could not add request. Can't connect to server."
            return 0

        return 1

    def reset(self):
        if self.hasInitialized:
            self.elevatorInterface.reset()

            self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)

            stats = self.elevatorInterface.bridge.getStats()
            self.infoPanel.updateStats(stats)

    def hardReset(self):

        self.elevatorInterface.hardReset()
        self.elevatorInterfaceVis.reset()

        self.initialize()

class InfoPanel(QtGui.QWidget):

    def __init__(self, labels = None):
        super(InfoPanel, self).__init__()

        self.separation = 10

        self.stats = {}

        self.vbox = QtGui.QVBoxLayout()
        self.statsVBox = QtGui.QVBoxLayout()

        self.vbox.addLayout(self.statsVBox)
        self.vbox.addStretch()


        if labels is not None:
            self.updateStats(labels)

        self.setLayout(self.vbox)

    def updateStats(self, stats):

        if stats is not None:
            for s in stats:
                if s not in self.stats:
                    # create the label and add it vbox
                    label = QtGui.QLabel(stats[s], self)
                    self.stats[s] = label
                    self.statsVBox.addWidget(label)
                else:
                    # update label value
                    self.stats[s].setText(stats[s])

