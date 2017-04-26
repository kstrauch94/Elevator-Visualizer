import json
import os

import clingo

import Checker
import SolverConfig
from Constants import *


class Solver():

    def __init__(self, encoding=None, instance=None):
        self.control = clingo.Control(SolverConfig.options)

        self.encoding = None
        if encoding is not None:
            self.encoding = encoding
            self.control.load(encoding)

        self.instance = None
        if instance is not None:
            self.control.load(instance)

        self.tempinstancename = None

        self.grounded = 0

        #self.imin = self.get(self.control.get_const("imin"), clingo.Number(0))
        self.imax = self.get(self.control.get_const("imax"), clingo.Number(100))
        self.istop = self.get(self.control.get_const("istop"), clingo.String("SAT"))

        self.elevAmt = None
        self.floors = None
        self.startPos = None

        self.step, self.ret = 1, None
        self.solved = False

        self.grounded = 0
        self.solvingStep = 0

        # lists for externals
        self.moved = []
        self.newRequests = []

        # full solution for the last solve call
        self.completePlan = []

        # stat recording vars

        self.totalSolvingTime = Stat(name = "Total Solving Time", val = 0)
        self.totalGroundingTime = Stat(name = "Total Grounding Time", val = 0)
        self.checkErrors = CheckerStat(name="Checker Status")
        self.reqs = RequestStat(name="Current Requests")

        self.model = Model()

        self.getInitialReqs()

    def loadInstance(self, instance):
        self.instance = instance
        self.control.load(self.instance)

    def loadInstanceStr(self, instanceStr):
        from tempfile import NamedTemporaryFile

        self.tempinstancename = NamedTemporaryFile()
        with open(self.tempinstancename.name, "w") as temp:
            temp.write(instanceStr)

        self.loadInstance(self.tempinstancename.name)

    def loadEncoding(self, encoding):
        self.encoding = encoding
        self.control.load(self.encoding)

    def get(self, val, default):
        return val if val != None else default

    def getInitialReqs(self):
        """
        retrieves the requests from time point 0.
        """
        self.reqs.val = []

        for x in self.control.symbolic_atoms:
            if not x.is_fact:
                continue
            atom = x.symbol
            if atom.name == "holds":
                if atom.arguments[0].name == "request":
                    self.reqs.val.append(atom)

    def getBaseValues(self):
        """
        Retrieves the base values of the instance. Should only be called after the instance has been given, else it crashes
        """
        self.floors = self.control.get_const("floors").number
        self.elevAmt = self.control.get_const("agents").number

        self.startPos = []
        for i in range(1, self.elevAmt + 1):
            self.startPos.append(self.control.get_const("start{}".format(i)).number)

        self.getInitialReqs()

    def groundStart(self):
        """
        Have to call this if something is to be added at time 0, E.G requests
        """

        if self.grounded == 0 and self.step == 1:
            self.control.ground([("base", []), ("init", []), ("step", [self.step]), ("check", [self.step])])
            self.grounded = 1

    def solve(self):

        self.solved = False

        self.ret = None

        # add history (already executed actions)
        for move in self.moved:
            self.control.assign_external(move, True)

        # add any new requests
        if self.newRequests != []:
            if self.grounded == 0: #only ground here if there are requests
                self.groundStart()
            for req in self.newRequests:
                self.control.assign_external(req, True)

        while (self.step < self.imax.number) and\
                (self.ret == None or (self.istop.string == "SAT" and not self.ret.satisfiable)):

            self.control.release_external(clingo.Function("query", [self.step-1]))

            #this is here in case the groundStart function was not called before
            if self.grounded == 0 and self.step == 1:
                self.control.ground([("base", []), ("init", []), ("step", [self.step]), ("check", [self.step])])
                self.grounded = 1
            #####

            elif self.grounded < self.step:
                parts = []
                parts.append(("check", [self.step]))
                parts.append(("step", [self.step]))
                self.control.cleanup()

                self.control.ground(parts)

                self.grounded += 1

            self.control.assign_external(clingo.Function("query", [self.step]), True)
            self.ret = self.control.solve(on_model=self.on_model)

            self.step = self.step + 1

    def on_model(self, model):

        print "Model found\n"
        self.solvingStep += 1
        self.step = self.solvingStep

        self.solved = True

        self.completePlan = []
        for atom in model.symbols(atoms = True):
            if atom.name == "do":
                self.completePlan.append(atom)

        self.reqs.val = []
        for atom in model.symbols(atoms=True):
            if atom.name == "holds":
                if atom.arguments[0].name == "request":
                    self.reqs.val.append(atom)

        self.model.actions = self.completePlan
        self.model.requests = self.reqs.val

    def actionFilter(self, atom):
        """
        Filters an action atom of the form do(E,A,T) and return the elevator number and action type
        :param atom: Action atom do(E,A,T)
        :return: elevator number, action type
        """
        elevator = atom.arguments[0].arguments[0].number

        action = atom.arguments[1]

        if action.name == "serve":
            actionType = SERVE
        elif action.name == "wait":
            actionType = WAIT
        elif action.arguments[0].number == 1:
            actionType = UP
        elif action.arguments[0].number == -1:
            actionType = DOWN
        else:
            print "Invalid action"

        return elevator, actionType

    def check(self):
        """
        Uses checker to see if the model has errors
        """

        if os.path.isfile(SolverConfig.checker):
            checker = Checker.Checker(SolverConfig.checker)
            if os.path.isfile(self.instance):
                # check model
                # convert shown atoms (which should be the actions) into a list of strings
                checker.checkList(self.instance, [str(a) for a in self.model.actions])
                self.checkErrors.val = checker.shownAtoms

    def callSolver(self, step=None):
        """
        This is the main call to the solver. Parameter step is used to know which steps were already executed.
        :param step: Must be the amount of steps that were already executed.
        """
        print "Solving... \n"
        if step is not None and self.solved:
            self.updateHistory(step)
        self.solve()
        self.check()
        self.stats()
        print "Finished Solving.\n"

    def solveFullPlan(self):
        """
        Use this to solve once and return the plan and requests as a list of clingo objects. Does not work for online solving. Mostly here for the
        -o option
        :return: list of clingo objects that represent actions and list of clingo objects that represent requests
        """
        self.solve()
        return self.completePlan, self.reqs.val

    def getFullPlan(self):
        """
        This returns the full plan as a dictionary. Each key is the time step. The value of the key is a list of lists
        that contain the elevator ID and the action
        :return: Plan dictionary
        """
        plan = {}

        for action in self.completePlan:
            elevator, actionType= self.actionFilter(action)
            time = action.arguments[-1].number

            if time not in plan:
                plan[time] = []

            plan[time].append([elevator, actionType])


        return plan

    def getRequestInfo(self):
        """
        Returns the requests as a dictionary similarly to the getFullPlan function.
        Each key is the time point with the value being a list containing the requests as strings
        :return: Request as a dictionary
        """
        reqs = {}

        for req in self.reqs.val:
            time = req.arguments[-1].number

            reqatom = req.arguments[0]
            reqtype = str(reqatom.arguments[0])
            dest = str(reqatom.arguments[1])

            if time not in reqs:
                reqs[time] = []

            if reqtype[:4] == "call":
                middle = " from "
            else:
                middle = " to "

            string = reqtype + middle + dest
            reqs[time].append(string)

        return reqs

    def updateHistory(self, step):
        """
        Updates the History of actions up to the time step provided
        :param step: The last time step where actions will be added
        """

        for action in self.completePlan:
            time = action.arguments[-1].number
            if time >= self.solvingStep and time <= step:
                self.moved.append(clingo.Function("history", action.arguments))

        self.solvingStep = step
        self.step = step

    def addRequest(self, reqtype, time, params):
        """
        Create a clingo function object for the request and add it to the request list of externals.

        :param reqtype: either call or deliver, it should be as the ones defined in the Constants.py file.
        :param time: time at which the request is added
        :param params: parameters of the request. Differs depending on the type. Either direction and destination for CALL requests
                       or elevator ID and destination for DELIVER requests
        """
        if self.solvingStep == 0:
            requestTime = 1
        else:
            requestTime = time


        if reqtype == REQ_CALL:
            request = clingo.Function("callrequest", [clingo.Function(params[0]), params[1], requestTime])

        if reqtype == REQ_DELIVER:
            request = clingo.Function("deliverrequest", [params[0], params[1], requestTime])

        print "Request " + str(request) + " has been added."
        self.newRequests.append(request)

    def stats(self):
        """
        Update the stats. Called after each solver call.
        """
        statistics = json.loads(json.dumps(self.control.statistics, sort_keys=True, indent=4, separators=(',', ': ')))
        solve = statistics["summary"]["times"]["solve"]
        ground = statistics["summary"]["times"]["total"] - solve

        #record stats
        self.totalSolvingTime.val += float(solve)
        self.totalGroundingTime.val += float(ground)

    def getStats(self):
        """
        Returns the stats as a dictionary, key is their name and value is a string
        :return: dictionary of stats
        """
        return {self.totalSolvingTime.name :  self.totalSolvingTime.string(),
                self.totalGroundingTime.name :  self.totalGroundingTime.string(),
                self.checkErrors.name : self.checkErrors.string()}

    def reset(self):
        """
        Reset the solver. Preserves the instance. Does not ground.
        :return:
        """
        self.control = clingo.Control(SolverConfig.options)
        self.loadInstance(self.instance)

        self.control.load(self.encoding)

        self.grounded = 0

        # self.imin = self.get(self.control.get_const("imin"), clingo.Number(0))
        self.imax = self.get(self.control.get_const("imax"), clingo.Number(100))
        self.istop = self.get(self.control.get_const("istop"), clingo.String("SAT"))

        self.elevAmt = None
        self.floors = None
        self.startPos = None

        self.step, self.ret = 1, None
        self.solved = False

        self.grounded = 0
        self.solvingStep = 0

        # lists for externals
        self.moved = []
        self.newRequests = []

        # full solution for the last solve call
        self.completePlan = []

        # stat recording vars
        self.totalSolvingTime.val = 0
        self.totalGroundingTime.val = 0
        self.checkErrors.val = None
        self.reqs.val = None

        self.model = Model()

        self.getInitialReqs()

class Model():
    """
    Simple class to hold the actions and the requests
    """

    def __init__(self):
        self.actions = None
        self.requests = None



class Stat(object):
    """
    Simple stat object to hold stat names and values. Also provides a simple string function
    """

    def __init__(self, name = "", val = None):

        self.name = name
        self.val = val

    def string(self):
        return self.name + " = " + str(self.val)


class CheckerStat(Stat):

    def string(self):
        string = ""
        if self.val is not None:
            for i in self.val:
                string += str(i)+"\n"

        else:
            string = str(self.val)

        return self.name + " = " + string

class RequestStat(Stat):

    def string(self):
        string = ""
        if self.val is not None and self.val != []:
            for i in self.val:
                reqatom = i.arguments[0]
                reqtype = str(reqatom.arguments[0])
                dest = str(reqatom.arguments[1])

                if reqtype[:4] == "call":
                    middle = " from "
                else:
                    middle = " to "

                string += reqtype + middle + dest + "\n"
        else:
            string = "None"

        return self.name + " = " + string


if __name__ == "__main__":
    s = Solver("Elevator.lp", "Elevatorinstance.lp")
    s.callSolver()
