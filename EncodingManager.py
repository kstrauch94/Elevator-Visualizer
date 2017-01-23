import json

import clingo

import Checker
import SolverConfig
from windows.Constants import *


class Solver():

    def __init__(self, encoding, instance):
        self.encoding = encoding
        self.instance = instance

        self.control = clingo.Control(SolverConfig.options)
        self.control.load(instance)
        self.control.load(encoding)

        self.step = 0
        self.grounded = 0

        #self.imin = self.get(self.control.get_const("imin"), clingo.Number(0))
        self.imax = self.get(self.control.get_const("imax"), clingo.Number(100))
        self.istop = self.get(self.control.get_const("istop"), clingo.String("SAT"))

        self.elevAmt = self.control.get_const("agents").number

        self.step, self.ret = 1, None

        self.grounded = 0
        self.solvingStep = 0

        # output config
        self.showStats = True
        self.printOutput = SolverConfig.printAtoms

        # lists for externals
        self.moved = []
        self.newRequests = []

        # full solution for the last solve call
        self.completePlan = []

        # stat recording vars

        self.totalSolvingTime = Stat(name = "Total Solving Time", val = 0)
        self.totalGroundingTime = Stat(name = "Total Grounding Time", val = 0)
        self.currentStep = Stat(name="Current Step", val = 0)
        self.checkErrors = CheckerStat(name="Checker Status")
        self.solved = Stat(name="Last Step Solved", val=False)
        self.reqs = RequestStat(name="Current Requests")

        self.groundStart()

        self.checker = Checker.Checker(SolverConfig.checker)


    def get(self, val, default):
        return val if val != None else default


    def groundStart(self):
        # have to call this if something is to be added at time 0, E.G requests
        if self.grounded == 0 and self.step == 1:
            self.control.ground([("base", []), ("init", []), ("step", [self.step]), ("check", [self.step])])
            self.grounded = 1

    def solve(self):

        self.solved.val = False

        self.ret = None
        self.lastMove = None
        #add the last actions
        for move in self.moved:
            self.control.assign_external(move, True)

        for req in self.newRequests:
            self.control.assign_external(req, True)

        #self.newRequests = []

        while (self.step < self.imax.number) and\
                (self.ret == None or (self.istop.string == "SAT" and not self.ret.satisfiable)):

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
            self.ret = self.control.solve(self.on_model)
            self.control.release_external(clingo.Function("query", [self.step]))

            self.step = self.step + 1

    def on_model(self, model):
        print "Model found\n"
        #increase solving step and set the step var to this value so that on the next solve call it starts solving there.
        self.solvingStep += 1
        self.step = self.solvingStep

        # update stat recording of the current step and stat var for the solving status is made true
        self.currentStep.val = self.solvingStep
        self.solved.val = True

        # check model
        # convert shown atoms into a list of strings
        self.checker.checkList(self.instance, [a.__str__() for a in model.symbols(shown = True)])
        self.checkErrors.val = self.checker.shownAtoms

        ####
        # look for the last action to perform and add it to moved and lastmove
        ####
        actionFound = False
        self.lastMove = []
        self.completePlan = []

        #elevs has the id of the elevators
        elevs = range(1, self.elevAmt+1)

        for atom in model.symbols(shown = True):
            # get the first move and add it to the already made moves.
            if atom.arguments[-1].number == self.solvingStep:
                          #do(  elevator( number))
                elevator = atom.arguments[0].arguments[0].number
                action   = atom.arguments[1]
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

                self.lastMove.append([elevator, actionType])
                self.moved.append(clingo.Function("history", atom.arguments))

                elevs.remove(elevator)

            if atom.name == "do":
                self.completePlan.append(atom)

        #pass None as action to elevator without one
        for e in elevs:
            self.lastMove.append([e, NONEACT])


        # at this point elevs holds all elevators without actions
        if len(elevs) != 0:
            print "No action was found for at least one elevator in step " + str(self.solvingStep) + ". This might create problems on the next solve call."


        self.reqs.val = []
        for atom in model.symbols(atoms=True):
            if atom.name == "holds":
                if atom.arguments[0].name == "request" and atom.arguments[-1].number == self.solvingStep:
                    self.reqs.val.append(atom)


        if self.printOutput:
            self.printAtoms(model.symbols(atoms=True))

    def callSolver(self):
        print "Solving... \n" + self.encoding
        self.solve()
        #self.stats()
        print "Finished Solving.\n"

    def solveFullPlan(self):
        """
        Use this to only solve and print the full plan
        """

        self.solve()
        for a in self.completePlan:
            print a

    def printAtoms(self, atoms):
        # atoms is usually a list of all atoms in the model
        # use model.symbols(atoms=True) as parameter inside the onmodel function to give the full atom list

        #######
        # use this function just for printing atoms
        #######

        goal = None

        for atom in atoms:
            if atom.name == "holds":
                if atom.arguments[0].name == "request" and atom.arguments[-1].number == self.solvingStep:
                    print atom
                if atom.arguments[0].name == "at" and atom.arguments[-1].number == self.solvingStep:
                    print atom

            if atom.name == "goal":
                if goal != None:
                    if atom.arguments[0] > goal.arguments[0]:
                        goal = atom
                else:
                    goal = atom


        print goal

    def addRequest(self, reqtype, params):
        """
        Create a clingo function object for the request and add it  to the request list of externals.

        :param reqtype: either call or deliver, it should be as the ones defined in the Constants.py file.
        :param params: parameters of the request. Differs depending on the type. Either direction and destination for CALL requests
                       or elevator ID and destination for DELIVER requests
        :return: void
        """
        if self.solvingStep == 0:
            requestTime = 1
        else:
            requestTime = self.solvingStep


        #requestTime = 1


        if reqtype == REQ_CALL:
            request = clingo.Function("callrequest", [clingo.Function(params[0]), params[1], requestTime])

        if reqtype == REQ_DELIVER:
            request = clingo.Function("deliverrequest", [params[0], params[1], requestTime])

        print request
        self.newRequests.append(request)

    def stats(self, printstats = False):

        statistics = json.loads(json.dumps(self.control.statistics, sort_keys=True, indent=4, separators=(',', ': ')))

        solve = statistics["summary"]["time_solve"]
        ground = statistics["summary"]["time_total"] - self.control.stats["summary"]["time_solve"]

        #record stats

        self.totalSolvingTime.val += float(solve)
        self.totalGroundingTime.val += float(ground)


        if printstats:
            #print stats for current step
            print self.ret
            if self.showStats == True:
                print "step: ", self.step
                print "solve: ", solve
                print "ground: ", ground


    def getStats(self):
        # order matters if being used by the InfoPanel class of the visualizer
        return [self.currentStep,
                self.solved,
                self.checkErrors,
                self.reqs,
                self.totalSolvingTime,
                self.totalGroundingTime]


class Stat(object):

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
