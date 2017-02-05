import argparse
import sys
from PyQt4 import QtGui
from argparse import RawTextHelpFormatter

import SolverConfig
from windows import MainWindow
from windows import ElevatorWindow

if __name__ == "__main__":
    desc = "Visualizer for an Elevator domain. Configuration can be set in the VisConfig.py file or specified with arguments\n\n" \
                                                 "It loads the encoding and instance and solves it when the next action button is pressed. " \
                                                 "It then applies one action and updates the visualization to reflect that. Requests can be added at anytime.\n\n" \
                                                 "If extra strategy encodings are used they must be included with #include directive inside the main encoding. " \
                                                 "After solving, it checks the plan for any problems outputs any errors.\n\n" \
                                                 "It is also possible to include more than one encoding. It creates a window for every encoding and has its file name " \
                                                 "as window title plus an id number.\nAdditionally, instead of an encoding, a file with a plan on it can be used to" \
                                                 "visualize said plan.\nEncoding and instance file paths can be either given with the Config file or with arguments described below."

    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-o", "--off-line", help="Solve and print the full plan without the visualizer then exit.", action="store_true")
    parser.add_argument("-e", "--encoding", help="Encoding file name to use initially.", nargs="+", default=SolverConfig.encoding)
    parser.add_argument("-i", "--instance", help="Instance file name to use initially.", default=SolverConfig.instance)


    args = parser.parse_args()


    SolverConfig.encoding = args.encoding
    SolverConfig.instance = args.instance


    if args.off_line:
        print "Solving encoding"
        bridge = ElevatorWindow.Connect()
        bridge.solveFullPlan()
        print "\n---Finished---\n"
    else:
        app = QtGui.QApplication(sys.argv)
        gui = MainWindow.MainWindow()
        sys.exit(app.exec_())