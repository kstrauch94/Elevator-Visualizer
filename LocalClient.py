import EncodingManager
import SolverConfig

class Connect(object):
    """
    class the holds the actual solver (encoding manager).
    """

    def __init__(self, instance=None, encoding=SolverConfig.encoding):
        self.instance = instance
        self.encoding = encoding

    def sendBaseRequest(self, instance):
        self.instance = instance
        self.solver = EncodingManager.Solver(self.encoding)
        self.solver.loadInstanceStr(instance)

        return 1

    def sendEncoding(self, encoding):
        self.encoding = encoding
        self.solver.encoding = self.encoding
        self.solver.reset()

        return 1

    def getElevatorAmt(self):

        return self.solver.control.get_const("agents").number

    def getFloorAmt(self):

        return self.solver.control.get_const("floors").number

    def startingPosition(self, elev):

        return self.solver.control.get_const("start%d" % (elev)).number

    def nextMoves(self, step):

        self.solver.callSolver(step)

        return self.solver.getFullPlan()

    def solveFullPlan(self, printAll = True, printReqs = False):
        actions, reqs = self.solver.solveFullPlan()

        if printAll:
            for a in actions:
                print a

            if printReqs:
                for r in reqs:
                    print r

        return actions, reqs

    def getStats(self):

        return self.solver.getStats()

    def getRequests(self):

        return self.solver.getRequestInfo()

    def addRequest(self, type, time, params):

        self.solver.addRequest(type, time, params)

        return 1

    def reset(self, mode):
        if mode == "hard":
            self.solver = EncodingManager.Solver(self.encoding)
        elif mode == "soft":
            self.solver.reset()

        return 1

