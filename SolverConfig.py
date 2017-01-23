# ASP configuration

#list of encodings and instance

encoding = ["encodings/Elevator.lp", "encodings/plan.lp"]
windows = len(encoding)

instance = "instances/Elevatorinstance.lp"

# Checker encoding
checker = "encodings/checker.lp"

# clingo solver options
# for more information on the options use the help command of the clingo module (clingo -h)
options = ["--configuration=auto"]

# Misc configuration

printAtoms = False
