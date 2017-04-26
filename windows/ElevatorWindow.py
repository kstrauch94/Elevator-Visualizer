import os
import time
from PyQt4 import QtGui, QtCore

import VisClient
import VisConfig
from Constants import *
from LocalSolver import LocalClient
from LocalSolver import SolverConfig

class ElevatorVis(QtGui.QWidget):
    """
    Visualizer Class for an individual Elevator
    """
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
        :param y: should be the position when on floor 1 (ground floor), basically the height of the whole elevator "shaft"
                  Should be floors * size
        :return: void
        """

        self.xpos = x
        self.ypos = y

    def paintEvent(self, QPaintEvent):
        """
        Qt drawing function that gets called in the internal loop. Currently bugged and gets called as mucha s possible.
        Hence the sleep at the end to limit the cpu usage.
        """
        qp = QtGui.QPainter()
        qp.begin(self)

        self.drawWidget(qp)

        qp.end()
        time.sleep(0.01)

    def updateElevator(self, elevator):
        """
        Get elevator data object to display on the next draw call
        :param elevator: elevator data object
        """
        self.floors = elevator.floors
        self.currentFloor = elevator.currentFloor
        self.lastAction = elevator.lastAction
        print self.floors, self.currentFloor, self.lastAction
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
    Elevator data class. Keeps track of the elevator position, history and current + last step.
    """
    def __init__(self, floors, startPos):

        self.floors = floors
        self.step = 0
        self.lastStep = 0
        self.history = [startPos]
        self.actionHistory = [NONEACT]

        # This is to easily transform the given action to a movement
        self.moveDict = {}
        self.moveDict[UP] = 1
        self.moveDict[DOWN] = -1
        self.moveDict[WAIT] = 0
        self.moveDict[SERVE] = 0
        self.moveDict[NONEACT] = 0

    def execute(self, action):
        """
        Depending on the action t goes up, down or stays.
        This should only be called with a new action that directly follows the last one completed
        :param action: Action as defined in the Constants.py file
        """
        print action
        currentFloor = self.history[self.lastStep]
        if action == DOWN and currentFloor == 1:
            print "Invalid move, trying to move down when already at the bottom floor."
            return 0

        if action == UP and currentFloor == self.floors:
            print "Invalid move, trying to move up when already at the top floor."
            return 0

        self.actionHistory.append(action)
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
    Visualizer for the whole instance. Keeps track of every elevator visualizer in the instance. Updates with an
    ElevatorInterface data class.
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
        Resets the whole interface and deletes the old elevator visualizers from the layout container. Used for hard
        resets.
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

        # This has the Socket client and the local solver. They both have the same functions and return the same thing.
        # Use the bridge @property to acces the correct one based on the self.mode variable.
        self.solverConns = {SOCKET: VisClient.VisSocket(), LOCAL: LocalClient.Connect(encoding=SolverConfig.encoding)}
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
        else:
            self.mode = mode

    def setConnectionInfo(self, host, port):

        self.bridge.setHost(host)
        self.bridge.setPort(port)

    def initialize(self):
        """
        Send reset followed by the instance. Retrieve the instance information.
        :return: int -> Success or fail
        """
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
        """
        set instance and create its string version so that it can be sent via sockets
        :param instance: instance file path
        """
        self.instance = instance
        with open(self.instance, 'r') as myfile:
            self.instanceStr = myfile.read()

    def sendEncoding(self, encoding):
        """
        :param encoding: encoding user input from dialog
        :return: int -> success or fail
        """
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
        :return: int -> success or fail
        """

        if self.hasToSolve and self.step == self.highestStep:
            if not self.solve():
                # If solve fails, E.G. cant connect to server or invalid info was received.
                return 0
            self.hasToSolve = False



        if len(self.plan) > self.step:
            self.step += 1

            if self.step - 1 == self.highestStep:
                self.highestStep += 1

                self.executeStep()

            for e in self.elevators:
                e.next()

        return 1

    def executeStep(self):
        """
        Execute the next step of the plan. Should only be called when a new highest step has been reached.
        Moves in a step are tuples (elevator ID, Action). Plan step is a list of such tuples.
        """
        moves = self.plan[self.step]
        for move in moves:
            # get elevator ID
            elevator = move[0]
            action = move[1]
            self.elevators[elevator - 1].execute(action)

    def previous(self):
        """
        Lowers step value. if counter is at 0 (lowest) -> do nothing
        """

        if self.step >= 1:
            self.step -= 1

            for e in self.elevators:
                e.previous()



    def solve(self):
        """
        Retrieve plan from bridge by calling nextMoves(Which calls the actual solver or sends message).
        Process the plan + requests and emit signals that they changed
        :return: int -> success or fail
        """
        # the parameter means that the actions up to that point were executed and should stay the same
        self.plan = self.bridge.nextMoves(self.highestStep)

        # if retrieving the new plan fails
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

        # for every time step up to the max step
        for t in range(1, self.planLength + 1):
            #check if entries for that step exist
            if t in self.plan:
                # if less entries than elevators
                if len(self.plan[t]) != self.elevatorCount:
                    # Find out which elevators have no entries
                    elevs = range(1, self.elevatorCount+1)
                    for move in self.plan[t]:
                        elevs.remove(move[0])

                    #For every elevator with no entries insert a NONEACT
                    for e in elevs:
                        self.plan[t].append([e, NONEACT])

            # if time step has no entry insert key and fill it with NONEACT for all elevators
            else:
                elevs = range(1, self.elevatorCount + 1)
                self.plan[t] = []
                for e in elevs:
                    self.plan[t].append([e, NONEACT])


    def parseRequests(self):
        """
        Sees if a request was completed by comparing time steps. If a request is in time T but not in T+1 then it was
        completed
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

        #Cant serve requests at point 0 but we populate the dict for consistency
        self.requestsServed[0] = []

    def addRequest(self, type, params):
        """
        Add request to the solver and keep track of it
        :param type: request type
        :param params: parameters of the request
        :return: int -> succes or fail
        """
        if not self.bridge.addRequest(type, self.highestStep, params):
            # return if adding the request fails
            return 0

        self.hasToSolve = True

        if type == REQ_CALL:
            string = "call({}) to {}".format(params[0], params[1])
        elif type == REQ_DELIVER:
            string = "deliver({}) from {}".format(params[0], params[1])
        else:
            print "Request type is invalid: " + str(type)
            return 0

        if self.highestStep not in self.addedRequests:
            self.addedRequests[self.highestStep] = [string]
        else:
            self.addedRequests[self.highestStep].append(string)

        return 1

    def getStats(self):
        """
        It just calls the getStats function from the active connection and return the value
        :return: dictionary with values being strings that represent some stat
        """
        return self.bridge.getStats()

    def reset(self):
        """
        Sends a soft reset message and resets the variables while retaining instance specific ones such as floor amount.
        :return: int -> success or fail
        """
        if not self.bridge.reset("soft"):
            return 0
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

        return 1


    def hardReset(self):
        """
        Sends a hard reset message and resets every variables including instance specific ones such as floor amount.
        :return: int -> success or fail
        """
        if not self.bridge.reset("hard"):
            return 0
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

        return 1

    @property
    def requestCompleted(self):
        """
        Returns a formatted string of the requests completed in the current active time step
        :return string
        """
        try:
            return ", ".join(self.requestsServed[self.step])
        except (TypeError, KeyError):
            return "No Requests"

    @property
    def currentRequests(self):
        """
        Return a formatted string of the requests active in the current active time step
        :return: string
        """
        try:
            return ", ".join(self.requestInfo[self.step])
        except (TypeError, KeyError):
            return "No Requests"

    @property
    def bridge(self):
        """
        returns the correct connection object based on the self.mode variable
        :return: Either a LocalSolver.Localclient.Connect() object or a VisClient.VisSocket() object
        """
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
        """
        Tries to initialize the elevatorInterface which involves sending instance to solver and retrieving instance info.
        Also initializes the elevatorInterface Visualizer.
        :return: int -> function success or fail
        """
        if self.hasInitialized:
            return 0

        if not self.elevatorInterface.initialize():
            print "Could not Initialize. Can't connect to server."
            return 0
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

        self.hasInitialized = True

        return 1

    def updateAll(self):
        """
        passes elevatorInterface to visualizer and also updates stats
        """
        self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)
        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

    def next(self):
        """
        Go to next step
        :return: int -> success or fail
        """
        if self.hasInitialized:
            if not self.elevatorInterface.next():
                print "Could not solve. Can't connect to server."
                return 0
            self.updateAll()

        return 1

    def previous(self):
        """
        Go to previous step. Should never fail
        """
        if self.hasInitialized:
            self.elevatorInterface.previous()
            self.updateAll()

    def addRequest(self, type, *params):
        """
        Sends request to solver
        :param type: type as defined in the Constants.py
        :param params: requests parameters
        :return: int -> success or fail
        """
        if not self.elevatorInterface.addRequest(type, params):
            print "Could not add request. Can't connect to server."
            return 0

        return 1

    def reset(self):
        """
        soft reset. Keep instance variables and dont reset visualizer.
        :return: int -> success or fail
        """
        if self.hasInitialized:
            if not self.elevatorInterface.reset():
                return 0

            self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)

            stats = self.elevatorInterface.bridge.getStats()
            self.infoPanel.updateStats(stats)
        return 1

    def hardReset(self):
        """
        hard reset means a new instance will be given to solver soon.
        :return: int -> success or fail
        """
        if not self.elevatorInterface.hardReset():
            return 0
        self.elevatorInterfaceVis.reset()

        self.hasInitialized = False

        self.initialize()

        return 1
class InfoPanel(QtGui.QWidget):
    """
    Class to visualize the stats
    """

    def __init__(self, labels = None):
        """
        :param labels: dictionary with strings to be visualized. Not necessary to pass anything
        """
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
        """
        Create labels for new stats and update old ones
        :param stats: dictionary with strings to be visualized
        """
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

