# Elevator-Visualizer
This program was tested with PyQt4 version 4.11.4 and with clingo version 5.1.0.

PyQt4 can be found at: https://riverbankcomputing.com/software/pyqt/download

Clingo can be found at: https://potassco.org/

## Visualizer
The visualizer can be configured in the VisCofig.py file. To start the visualizer try:
```
$ python Elevator.py
```

The command opens a visualization window and a control window with several buttons. Press "Initialize Connection" to start visualizing. If using the server make sure to start it.

The visualization has vertical rectangle divided into squares as the elevator shaft. The elevator is a red square. The last action performed is visualized below by either an arrow or a rectangle. An "N" is displayed if no action was taken. Stats might be displayed on the right side of the window.

It is also possible to just solve the instance with the encodings provided in the Config.py file or by arguments, and print the full plan without visualizing by using the -o command. (clingo is required)

```
$ python Elevator.py -o
```

## Encoding and Instance specification

The encodings and instances specification depend on the system being used. The following specifications are for the built in systems.

#### When visualizing a plan the plan file must have:

- "do(E, A, t)" action predicates
- (optional) holds(request(Type,Floor), Time) predicates for the requests that are active at some timepoint

#### The clingo encoding specified in the SolverConfig.py file must have the following properties:

- The actions must be: move(1), move(-1), serve, and wait
- The action execution predicate must have the form "do(E, A, t)" where E is of the form "elevator(N)" with N being a integer, A is an action as the ones described above and t the timestep. E.g. do(elevator(1),serve,5).
- The usual clingo directives for incremental solving (including the query(t) external)

#### Additional properties for online planning:

- The external history(E,A,t) : agent(E), action(A).
- The externals #external callrequest(D, Floor, t) : dir(D), Floor = 1..floors.
-				#external deliverrequest(ID, Floor, t) : ID = 1..agents, Floor = 1..floors.

#### The instances must have the following properties:

- #const agents=N. line with N being the amount of elevators
- #const floors = F. line with F being the amount of floors
- #const startID = S. line for every elevator. The ID is replaced with the elevator ID and S is the starting position.


Example encodings and instances are provided in the encodings folder and in the instances folder respectively.


The instance generator and the checker can also be used independently from the visualizer. For examples of how to use them refer to the EXAMPLES file.
	
## Instance Generator

Instances can be created with the InstanceGenerator.py script. It can either prompt for the details or they can be given as parameters in the command line. The instances created conform to the standards described above. Use the -h command for more information. Examples can be found in the EXAMPLES file.

## Checker

The Checker.py script uses an encoding (found in the encodings folder, named checker.lp) to check a plan. If any error is found, E.G applying an action that is not posisble to apply, this is logged with an "error" predicate that saves the error type, the elevator that has the error and the time step it happened in, e.g. error(notposs,elevator(2),4) which means that elevator(2) executed an action which was not possible to execute at time point 4. Use -h for more information on the parameters. Examples can be seen in the EXAMPLES file.

The error types are:
```
notposs     : The action executed was not possible to execute. Since serve and wait are always possible this refers to the move actions.
isbelow1    : The elevator is at a floor below the minimum (below 1). 
isabovemax  : The elevator is is above the highest floor.
multactions : The elevator executed more than one action at the same time point.
longmove    : The elevator moved more than 1 floor in one time point.
clone       : An elevator is at multiple places at once.

badreq      : A request directed to a floor that doesnt exist or a deliver request directed to an elevator that doesn't exist.
```
