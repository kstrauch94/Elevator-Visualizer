# ASP configuration

#list of encodings and instance
encoding = ["encodings/Elevator.lp"]

instance = "instances/Elevatorinstance.lp"

# Checker encoding
checker = "encodings/checker.lp"

# clingo solver options
# for more information on the options use the help command of the clingo module (clingo -h)
options = ["--configuration=auto"]

# Misc configuration

printAtoms = False

#Window Configuration

#Size of the window in pixels
width  = 640
height = 520

topOffset  = 40
sideOffset = 30

#if there are multiple elevators, this says how big the separation between them is
elevatorSeparation = 15

#size of the elevators and floors in pixels
size = 32

