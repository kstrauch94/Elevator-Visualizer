import argparse
import sys
from PyQt4 import QtGui
from argparse import RawTextHelpFormatter

import SolverConfig
from windows import MainWindow
from windows import ElevatorWindow


def writeAnswer(instance, actions, reqs):
    """
    Writes the answer returned from the encoding manager to a file.
    :param instance: instance file name
    :param actions: list of action terms as returned by clingo or as strings
    :param reqs: list of action terms as returned by cling or as strings
    """
    name = instance + ".sol"

    actions = [a.__str__() for a in actions]
    reqs = [r.__str__() for r in reqs]

    with open(name, "w") as t:
        for line in actions:
            t.write(line + ".")

        t.write("\n\n")

        for line in reqs:
            t.write(line + ".")

    print "Saved answer to file : " + name + "\n"


if __name__ == "__main__":
    desc = "Visualizer for an Elevator domain. Configuration can be set in the VisConfig.py file or specified with arguments\n\n" \
                                                 "It loads the encoding and instance and solves it when the next action button is pressed. " \
                                                 "It then applies one action and updates the visualization to reflect that. Requests can be added at anytime.\n\n" \
                                                 ".\nAdditionally, instead of an encoding, a file with a plan on it can be used to" \
                                                 "visualize said plan.\nEncoding and instance file paths can be either given with the Config file or with arguments described below."

    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-o", "--off-line", help="1 : Solve and print the full plan without the visualizer then exit.\n2 : Also print the request atoms.\n3 : Write answer to a file", action="count", default=0)
    parser.add_argument("-e", "--encoding", help="Encoding file name to use initially.", default=SolverConfig.encoding)
    parser.add_argument("-i", "--instance", help="Instance file name to use initially.", default=SolverConfig.instance)


    args = parser.parse_args()


    SolverConfig.encoding = args.encoding
    SolverConfig.instance = args.instance


    if args.off_line > 0:
        print "Solving encoding"
        bridge = ElevatorWindow.Connect()
        printAll = args.off_line < 3
        actions, reqs = bridge.solveFullPlan(printAll, args.off_line > 1)
        print "\n---Finished---\n"
        if args.off_line > 2:
            writeAnswer(SolverConfig.instance, actions, reqs)
    else:
        app = QtGui.QApplication(sys.argv)
        gui = MainWindow.MainWindow()
        sys.exit(app.exec_())


