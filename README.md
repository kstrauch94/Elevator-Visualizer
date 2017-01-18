# Elevator-Visualizer
This program was tested with PyQt4 version 4.11.4 and with clingo version 5.1.0

PyQt4 can be found at: https://riverbankcomputing.com/software/pyqt/download

Clingo can be found at: https://potassco.org/

## Visualizer

The visualizer can be configured in the Cofig.py file. The important variables are the encoding and the instances. The encoding variable must be a list with the encodings that want to be used in the visualization. These variables can also be set with command line arguments. A separate window will be created for every encoding in the list. The window will have the encoding file name in its title. The instance must be one file.

Any extra files can be included with the #include directive in the encoding file. The printOuput variable can be set to either "True" or "False". When it is True the following atoms for the last executed step are printed: the action execution atom, the position of the elevator(s), and the current requests. This only works if the atoms are named as in the example encoding. This information also displayed on the visualization windows.

The visualization has vertical rectangle divided into squares as the elevator shaft. The elevator is a red square. The last action performed is visualized below by either an arrow or a rectangle. An "N" is displayed if there no action was taken. To the right there are several stats about the last solved call such as the current time step.

It is also possible to just solve the instance with the encodings provided in the Config.py file or by arguments, and print the full plan without visualizing by using the -o command.

```
$ python Elevator.py -o
```

#### Buttons

The visualizer has buttons to solve and apply the next action, add new requests, and to reset. After every solve call the found plan is tested and an output is given that reports any errors that were found.

The "Next Action" button solves the instance. On repeated clicks it remembers the past actions and keeps them in the plan. The "add call request" button takes as parameters a direction(either "up" or "down") and a destination floor, e.g "up,5". This request is added to the solver and taken into account on the next click of the "Next Action" button. Similarly, the "add deliver request" button takes as parameters an elevator and a destination, e.g. 1,5 (elevator 1 goes to floor 5). This request is also taken into account on the next click of the "Next Action" button.

## Encoding and Instance specification

#### The clingo encoding specified in the Config.py file must have the following properties:

- The actions must be: move(1), move(-1), serve, and wait
- The action execution predicate must have the form "do(E, A, t)" where E is of the form "elevator(N)" with N being a integer, A is an action as the ones described above and t the timestep. E.g. do(elevator(1),serve,5).
- The external history(E,A,t) : agent(E), action(A).
- The externals #external callrequest(D, Floor, t) : dir(D), Floor = 1..floors.
-				#external deliverrequest(ID, Floor, t) : ID = 1..agents, Floor = 1..floors.
- a #show do/3. statement.
- no #minimize statements
- The usual clingo #program directives for incremental solving, base, step(t) and check(t).
- The #external query(t)

#### The instances must have the following properties:

- #program base. directive
- #const agents=N. line with N being the amount of elevators
- #const floors = F. line with F being the amount of floors
- #const startID = S. line for every elevator. The ID is replaced with the elevator ID and S is the starting position.
- #const startingReqs = N line where N is the amount of request at time point 0. This is not currently being used but might be in the future.


Example encodings and instances are provided in the encodings folder and in the instances folder respectively.


The instance generator and the checker can also be used independently from the visualizer. For examples of how to use them refer to the EXAMPLES file.
	
## Instance Generator

Instances can be created with the InstanceGenerator.py script. It can either prompt for the details or they can be given as parameters in the command line. The instances created conform to the standards described above. Use the -h command for more info. Examples can be found in the EXAMPLES file.

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
```
