import argparse
import sys
from PyQt4 import QtGui
from argparse import RawTextHelpFormatter

import VisConfig
from windows import Constants
from windows import MainWindow
from LocalSolver import SolverConfig


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
                                                 "It loads instance and solves it by sending messages to a server or using the build in solver.\n" \
                                                 "Requests can be added at anytime if it is support by the solver.\n\n" \
                                                 "\ninstance file paths can be either given with the VisConfig file or with argument described below."

    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-o", "--off-line", help="1 : Solve and print the full plan without the visualizer then exit.\n" \
                                                 "2 : Also print the request atoms.\n3 : Write answer to a file", action="count", default=0)
    parser.add_argument("-m", "--local-mode", help="Set initial connection mode to local instead of socket", action="store_true")
    parser.add_argument("-i", "--instance", help="Instance file name to use initially.", default=VisConfig.instance)
    parser.add_argument("-e", "--encoding", help="Encoding that the LOCAL solver uses initially.", default=SolverConfig.encoding)
    parser.add_argument("-H", "--host", help="Host IP address", default=VisConfig.host)
    parser.add_argument("-P", "--port", help="Port for the server", default=VisConfig.port)


    args = parser.parse_args()


    VisConfig.instance = args.instance
    VisConfig.host = args.host
    VisConfig.port = args.port

    SolverConfig.encoding = args.encoding

    connectionMode = Constants.SOCKET
    if args.local_mode:
        connectionMode = Constants.LOCAL


    if args.off_line > 0:
        print "Solving encoding"
        from LocalSolver import LocalClient

        bridge = LocalClient.Connect(VisConfig.instance)
        bridge.createSolver()
        printAll = args.off_line < 3
        actions, reqs = bridge.solveFullPlan(printAll, args.off_line > 1)
        print "\n---Finished---\n"
        if args.off_line > 2:
            writeAnswer(VisConfig.instance, actions, reqs)
    else:
        app = QtGui.QApplication(sys.argv)
        gui = MainWindow.MainWindow(connectionMode)
        sys.exit(app.exec_())


