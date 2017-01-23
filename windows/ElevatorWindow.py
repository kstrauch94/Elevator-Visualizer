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
        self.elevator = elevator

    def drawWidget(self, qp):

        color = QtGui.QColor(0, 0, 0)
        qp.setPen(color)

        #draw floor squares plus numbers
        qp.drawLine(self.xpos, self.ypos, self.xpos, self.ypos - self.elevator.floors * self.size)
        qp.drawLine(self.xpos + self.size, self.ypos, self.xpos + self.size, self.ypos - self.elevator.floors * self.size)

        for f in range(0, self.elevator.floors + 1):
            y = self.ypos - f * self.size
            qp.drawLine(self.xpos, y, self.xpos + self.size, y)

            if f != self.elevator.floors:
                qp.setFont(QtGui.QFont('Decorative', 15))
                text = "%d" %(f+1)
                #NOTE the x and y pos for the text is the BOTTOM LEFT part
                qp.drawText(self.xpos + 2, y - 2, text)

        if self.elevator.lastAction == SERVE:
            qp.setBrush(QtGui.QColor(0, 200, 0))
        else:
            qp.setBrush(QtGui.QColor(200, 0, 0))

        #the +2 and -4 are to make the elevator square a bit smaller than the floor box
        #should probably add a variable for those :v
        qp.drawRect(self.xpos + 2, self.ypos + 2 - self.elevator.currentFloor * self.size, self.size - 4, self.size - 4)

        # draw image of last action
        if self.elevator.lastAction == SERVE or self.elevator.lastAction == WAIT:
            self.actionpic.setPixmap(self.stayImg)
        elif self.elevator.lastAction == UP:
            self.actionpic.setPixmap(self.uparrowImg)
        elif self.elevator.lastAction == DOWN:
            self.actionpic.setPixmap(self.downarrowImg)
        elif self.elevator.lastAction == NONEACT:
            self.actionpic.setPixmap(self.noneImg)


        # the +10 after ypos is to separate the image from the elevator a bit
        self.actionpic.setGeometry(0, self.ypos + 15, self.size, self.size)

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
        self.currentFloor = startPos

        #keep track of last action executed
        self.lastAction = None



    def execute(self, action):
        """
        Only needs to know where to move. So depending on the action is goes up, down or stays
        :param action: Action as defined in the Constants.py file
        :return: void
        """
        if action == DOWN and self.currentFloor == 1:
            print "Invalid move, trying to move down when already at the bottom floor."
            return

        if action == UP and self.currentFloor == self.floors:
            print "Invalid move, trying to move up when already at the top floor."
            return

        if action != WAIT and action != NONEACT:
            self.currentFloor += action

        self.lastAction = action

class ElevatorInterfaceVis(QtGui.QWidget):
    """ Visualizer for the whole instance. Keeps track of every elevator in the instance"""
    def __init__(self, id, size):
        """

        :param encoding: encoding
        :param instance: instance
        :param size: size of the squares that represent the floors, usually defined in the VisConfig.py file
        """
        super(ElevatorInterfaceVis, self).__init__()

        self.elevatorInterface = ElevatorInterface(id)
        self.size = size

        # calculate the total height of the shaft
        self.ypos = self.size * self.elevatorInterface.floors

        #distance between elevator shafts
        self.elevatorSeparation = 20

        self.hbox = QtGui.QHBoxLayout()

        self.setElevVis()

        self.setLayout(self.hbox)



    def setElevVis(self):
        """
        Create a visualizer for every elevator in the instance and add it to the layout.
        """
        self.elevatorsVis = []
        for i in range(self.elevatorInterface.elevatorCount):
            vis = ElevatorVis(self.size)
            vis.setDrawPos(0, self.ypos)
            # the +2 after the floors thing is to also include the images
            vis.setMinimumSize(self.size + 4, self.size * (self.elevatorInterface.floors + 2) + 4)

            self.elevatorsVis.append(vis)
            self.hbox.addWidget(vis)

        self.updateElevators()

    def updateElevators(self):
        """
        Function to be called after the solve call. Since the data has changed,
        the updated object needs to be passed to the individual elevator visualizers.
        """

        for i in range(0, len(self.elevatorsVis)):
            self.elevatorsVis[i].updateElevator(self.elevatorInterface.elevators[i])


    def update(self):
        """
        Calls the update for the data class which is the solve call. Then call the updateElevator function to also update the visualizer part.
        """
        self.elevatorInterface.update()
        self.updateElevators()

    def reset(self):
        """
        Resets the whole interface and deletes the old elevator visualizers from the layout container. Then, it creates everything again
        """
        self.elevatorInterface.reset()

        for i in reversed(range(self.hbox.count())):
            self.hbox.itemAt(i).widget().setParent(None)

        self.setElevVis()


    @property
    def floors(self):
        return self.elevatorInterface.floors

    @property
    def elevatorCount(self):
        return self.elevatorInterface.elevatorCount


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

        self.setElevators()

    def setElevators(self):
        """
        Create elevator data object for every elevator
        """
        self.elevators = []

        for i in range(1, self.elevatorCount + 1):
            elevatorStart = self.bridge.startingPosition(i)
            elevator = Elevator(self.floors, elevatorStart)

            self.elevators.append(elevator)


    def update(self):
        """
        Basically solves to get the next moves and "execute" them.
        """
        moves = self.bridge.nextMoves()

        if moves != None:
            for move in moves:
                #get elevator ID
                elevator = move[0]
                action = move[1]
                self.elevators[elevator - 1].execute(action)



    def addRequest(self, type, *params):
        self.bridge.addRequest(type, params)

    def reset(self):
        """
        Creates a new solver object so that it reloads everything.
        The request amount is not used for now.

        It also creates the elevetor object again.
        """
        self.bridge.reset()

        self.setElevators()


class Interface(QtGui.QWidget):
    """
    Class that should hold the information for the elevator. Currently only has the interface but in the future it should hold the stats aswell.
    """
    def __init__(self, id):
        super(Interface, self).__init__()


        self.elevatorInterface = ElevatorInterfaceVis(id, VisConfig.size)

        stats = self.elevatorInterface.elevatorInterface.bridge.getStats()
        self.infoPanel = InfoPanel(stats)

        self.hbox = QtGui.QHBoxLayout()

        self.hbox.addWidget(self.elevatorInterface)
        self.hbox.addWidget(self.infoPanel)


        self.setLayout(self.hbox)

    def update(self, *__args):
        self.elevatorInterface.update()
        #the double elevator interface is because one if of the class that visualizes it and the other the actual class that holds the data
        stats = self.elevatorInterface.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

    def reset(self):
        self.elevatorInterface.reset()
        stats = self.elevatorInterface.elevatorInterface.bridge.getStats()
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

    def nextMoves(self):

        self.solver.callSolver()

        return self.solver.lastMove

    def getFullPlan(self):

        return self.solver.solveFullPlan()

    def getStats(self):

        return self.solver.getStats()

    def addRequest(self, type, params):

        self.solver.addRequest(type, params)

    def reset(self):
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

    def getWindowAmt(self):

        return SolverConfig.windows