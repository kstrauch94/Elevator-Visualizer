from PyQt4 import QtGui, QtCore

import EncodingManager
import SolverConfig, VisConfig
from Constants import *

import os


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

        # this should be changed. Generally x stays at 0 but y must best the amount of floors time the size of the floors in pixels.
        self.xpos = 0
        self.ypos = 0

        # images for the actions
        self.actionpic = QtGui.QLabel(self)
        # images
        self.uparrowImg = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.downarrowImg = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.stayImg = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.noneImg = QtGui.QPixmap(os.getcwd() + "/res/none.png")

    def setDrawPos(self, x, y):
        """
        :param x: usually left as 0 as the pyQT widget superclass takes over the x positioning.
        :param y: should be the position when on floor 1 (ground floor), basically the height of the whole elevator "shaft"
        :return: void
        """

        self.xpos = x
        self.ypos = y

    def paintEvent(self, QPaintEvent):
        qp = QtGui.QPainter()
        qp.begin(self)

        self.drawWidget(qp)

        qp.end()

    def updateElevator(self, elevator):
        """
        Get elevator data object to display on the next draw call
        :param elevator: elevator data object
        :return: void
        """
        self.floors = elevator.floors
        self.currentFloor = elevator.currentFloor
        self.lastAction = elevator.lastAction

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

        if self.lastAction == SERVE:
            qp.setBrush(QtGui.QColor(0, 200, 0))
        else:
            qp.setBrush(QtGui.QColor(200, 0, 0))

        #the +2 and -4 are to make the elevator square a bit smaller than the floor box
        #should probably add a variable for those :v
        qp.drawRect(self.xpos + 2, self.ypos + 2 - self.currentFloor * self.size, self.size - 4, self.size - 4)

        # draw image of last action
        if self.lastAction == SERVE or self.lastAction == WAIT:
            self.actionpic.setPixmap(self.stayImg)
        elif self.lastAction == UP:
            self.actionpic.setPixmap(self.uparrowImg)
        elif self.lastAction == DOWN:
            self.actionpic.setPixmap(self.downarrowImg)
        elif self.lastAction == NONEACT:
            self.actionpic.setPixmap(self.noneImg)


        # the +15 after ypos is to separate the image from the elevator a bit
        self.actionpic.setGeometry((self.size-32)/2, self.ypos + 15, self.size, self.size)

class Elevator():
    """
    Elevator data class. Keeps track of the elevator position.
    """
    def __init__(self, floors, startPos):
        """

        :param floors: total amount of floors
        :param startPos: starting floor
        """
        self.floors = floors
        self.step = 0
        self.lastStep = 0
        self.history = [startPos]

        self.actionHistory = [None]

    def execute(self, action):
        """
        Only needs to know where to move. So depending on the action is goes up, down or stays.
        This should only be called with a new action that directly follows the last one completed
        :param action: Action as defined in the Constants.py file
        :return: void
        """
        currentFloor = self.history[self.lastStep]
        self.actionHistory.append(action)
        if action == DOWN and currentFloor == 1:
            print "Invalid move, trying to move down when already at the bottom floor."
            return

        if action == UP and currentFloor == self.floors:
            print "Invalid move, trying to move up when already at the top floor."
            return

        if action != WAIT and action != NONEACT:

            self.history.append(currentFloor + action)

        elif action == WAIT or action == NONEACT:

            self.history.append(currentFloor)

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
        if self.step == 0:
            return None
        else:
            return self.actionHistory[self.step]

class ElevatorInterfaceVis(QtGui.QWidget):
    """ Visualizer for the whole instance. Keeps track of every elevator in the instance."""
    def __init__(self, size):
        """
        Initialize core visualization stuff. It is necessary to pass the data object to the initialize function after creating the object
        :param encoding: encoding
        :param instance: instance
        :param size: size of the squares that represent the floors, usually defined in the VisConfig.py file
        """
        super(ElevatorInterfaceVis, self).__init__()

        self.size = size

        #distance between elevator shafts
        self.elevatorSeparation = 20

        self.hbox = QtGui.QHBoxLayout()

        self.setLayout(self.hbox)


    def initialize(self, elevatorInterface):

        # calculate the total height of the shaft
        self.ypos = self.size * elevatorInterface.floors

        self.setElevVis(elevatorInterface.elevatorCount, elevatorInterface.floors)
        self.updateElevators(elevatorInterface)

    def setElevVis(self, elevatorCount, floors):
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
        Resets the whole interface and deletes the old elevator visualizers from the layout container. Then, it creates everything again
        """
        for i in reversed(range(self.hbox.count())):
            self.hbox.itemAt(i).widget().setParent(None)




class ElevatorInterface():
    """
    Data class for the whole instance. Keeps track of every individual elevator.
    """
    def __init__(self, id):
        """
        Parameters usually in the VisConfig.py file
        :param id : id of the solver to be used.
        """

        self.bridge = Connect(id)

        self.elevatorCount = self.bridge.getElevatorAmt()
        self.floors = self.bridge.getFloorAmt()

        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.setElevators()

        self.completePlan = None

        self.hasToSolve = True

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
        Solves if it needs to solve
        go to the next step, if it has not been executed -> give the action to elevator to execute it
                             if it has been executed -> increase step counter by one
        Then, call the next function on every elevator
        """

        if self.hasToSolve:
            self.solve()
            self.hasToSolve = False



        if len(self.plan) > self.step:
            self.step += 1

            if self.step - 1 == self.highestStep :
                self.highestStep += 1

                moves = self.plan[self.step]
                if moves != []:
                    for move in moves:
                        # get elevator ID
                        elevator = move[0]
                        action = move[1]
                        self.elevators[elevator - 1].execute(action)


            for e in self.elevators:
                e.next()


    def previous(self):
        """
        Lowers step value. if counter is at 1 (lowest) -> do nothing
        :return:
        """

        if self.step >= 1:
            self.step -= 1

            for e in self.elevators:
                e.previous()



    def solve(self):
        self.plan = self.bridge.nextMoves(self.highestStep)

        self.planLength = len(self.plan)


    def addRequest(self, type, *params):
        self.hasToSolve = True
        self.bridge.addRequest(type, self.highestStep, params)

    def getStats(self):
        """
        It just calls the getStats function from the encoding manager (solver) and return the value
        :return: list of Stat objects
        """

        return self.bridge.getStats()

    def reset(self):
        """
        Creates a new solver object so that it reloads everything.
        The request amount is not used for now.

        It also creates the elevetor object again.
        """
        self.bridge.reset()
        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.setElevators()

        self.hasToSolve = True


class Interface(QtGui.QWidget):
    """
    Class that should hold the information for the elevator. Currently only has the interface but in the future it should hold the stats aswell.
    """
    def __init__(self, id):
        super(Interface, self).__init__()

        self.elevatorInterface = ElevatorInterface(id)
        self.elevatorInterfaceVis = ElevatorInterfaceVis(VisConfig.size)
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)


        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel = InfoPanel(stats)

        self.hbox = QtGui.QHBoxLayout()

        self.hbox.addWidget(self.elevatorInterfaceVis)
        self.hbox.addWidget(self.infoPanel)

        self.setLayout(self.hbox)

    def update(self, *__args):
        self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

    def next(self):
        self.elevatorInterface.next()
        self.update()

    def previous(self):
        self.elevatorInterface.previous()
        self.update()

    def reset(self):
        self.elevatorInterface.reset()

        self.elevatorInterfaceVis.reset()
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

class ElevatorWindow(Interface):
    """
    This class just creates a window for a given encoding.
    """
    def __init__(self, id):
        super(ElevatorWindow, self).__init__(id)

        self.id = id

        self.setGeometry(VisConfig.width, VisConfig.height, VisConfig.width, VisConfig.height)
        self.setWindowTitle("Window"+ " (" + str(self.id) + ")")

        #this is here so that when multiple encodings are present the windows are not created in the same spot,
        #they are created side by side until no more room is left. Then they are created in the same place.
        self.move((VisConfig.width+100)*(self.id), 0)


class InfoPanel(QtGui.QWidget):

    def __init__(self, labels):
        super(InfoPanel, self).__init__()

        self.separation = 10

        self.stats = {}

        self.vbox = QtGui.QVBoxLayout()

        self.initLabels(labels)

        self.setLayout(self.vbox)

    def initLabels(self, labels):

        for s in labels:
            if s.name not in self.stats:
                # create the label and add it vbox
                label = QtGui.QLabel(s.string(), self)
                self.stats[s.name] = label
                self.vbox.addWidget(label)

        self.vbox.addStretch(-1)

    def updateStats(self, stats):

        for s in stats:
            # update label value
            self.stats[s.name].setText(s.string())


class Connect(object):

    def __init__(self, id):
        self.instance = SolverConfig.instance
        self.encoding = SolverConfig.encoding[id]
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

        self.elevatorCount = self.solver.control.get_const("agents").number
        self.floors = self.solver.control.get_const("floors").number

    def getElevatorAmt(self):

        return self.solver.control.get_const("agents").number

    def getFloorAmt(self):

        return self.solver.control.get_const("floors").number

    def startingPosition(self, elev):

        return self.solver.control.get_const("start%d" % (elev)).number

    def nextMoves(self, step):

        self.solver.callSolver(step)

        return self.solver.getFullPlan()

    def solveFullPlan(self):
        # only prints the plan cause its printed in the encoding manager
        return self.solver.solveFullPlan()

    def getStats(self):

        return self.solver.getStats()

    def addRequest(self, type, time, params):

        self.solver.addRequest(type, time, params)

    def reset(self):
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

    def getWindowAmt(self):

        return SolverConfig.windows
