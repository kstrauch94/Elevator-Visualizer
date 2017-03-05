import EncodingManager
import SolverConfig

class Connect(object):
    """
    class the holds the solver (encoding manager) and is used to retrieve info from the solver.
    """

    def __init__(self, instance=None, encoding=SolverConfig.encoding):
        self.instance = instance
        self.encoding = encoding

    def createSolver(self):
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

    def sendBaseRequest(self, instance):
        """
        Pass the instance to the solver.
        :param instance: instance in string form
        :return: 1 -> it should always "succeed"
        """
        self.instance = instance
        self.solver = EncodingManager.Solver(self.encoding)
        self.solver.loadInstanceStr(instance)

        return 1

    def sendEncoding(self, encoding):
        """
        Pass the encoding to the solver.
        :param encoding: encoding (user input)
        :return: 1 -> it should always "succeed"
        """
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
        """
        Calls the solver and return the plan
        :param step: step from which to start solving
        :return: plan dictionary
        """

        self.solver.callSolver(step)

        return self.solver.getFullPlan()

    def solveFullPlan(self, printAll = True, printReqs = False):
        """
        Used by the -o option to print out actions and/or requests and return them
        :param printAll: bool -> if true it activates printing anything
        :param printReqs: bool -> if true it also prints the requests
        :return: list of clingo objects representing actions and list of clingo objects representing requests
        """
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
        """
        Adds request to the solver
        :param type: request type
        :param time: time point where request should be added
        :param params: parameters of the request (tuple)
        :return: 1 -> it should always "succeed"
        """

        self.solver.addRequest(type, time, params)

        return 1

    def reset(self, mode):
        """
        Reset the solver. When its a hard reset if also forgets the instance
        :param mode: "soft" or "hard"
        :return: 1 -> it should always "succeed"
        """
        if mode == "hard":
            self.solver = EncodingManager.Solver(self.encoding)
        elif mode == "soft":
            self.solver.reset()

        return 1

