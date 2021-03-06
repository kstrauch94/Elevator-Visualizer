
# Examples

## Visualizer

The Visualizer can communicate with a local solver or via sockets. A sample server is provided in the server directory. To start the server go to the directory and use the command:

```
$ python SolverServer.py
```

With the default configuration of the visualizer one can run the following command:
```
$ python Elevator.py
```

This pops up 2 windows. One contains labeled buttons and one contains nothing. To start the visualization go to the connections tab and press "Initialize Connection". It has some elevator shafts with the elevator(red square) currently sitting in some floor. Pressing the next action button moves the elevator. After clicking the button a couple times, the square will eventually turn green. This means that a "serve" action was executed. Images of the last executed action can be seen at the bottom of the elevator shaft. 

Running the command
```
$ python Elevator.py -i instances/Elevatorinstance2.lp
```

changes the default instance to "instances/Elevatorinstance2.lp". The visualization window now has 4 elevator shafts with the elevators sitting in the first floor. 

To use the visualizer without having to start the server use the -m option:
```
$ python Elevator.py -m
```

For more command line options use the -h help command.

## Checker

Outputing the help text with the command:
```
$ python Checker -h
```
explains the arguments that can be given.

Now, use the following command from the Server directory (which contains the checker) of the packgage:
```
$ python Checker.py encodings/checker.lp ../instances/Elevatorinstance.lp -a "do(elevator(1),move(1),1)" "do(elevator(1),move(-1),2)" "do(elevator(1),move(-1),3)" 
```

we get the following output:
```
Checking model... 
noerror(elevator(1))
Finished Checking.
```
The input expressed that we want to use the checker "checker.lp" located in the encodings folder on the instance "instance/Elevatorinstance.lp" with the plan we give as a list with the -a argument. The quotes are necessary because of the special "(" and ")" characters. The output states that there are no errors for elevator 1.

Running the command:
```
$ python Checker.py encodings/checker.lp ../instances/Elevatorinstance.lp -a "do(elevator(1),move(-1),1)" "do(elevator(1),move(-1),2)" "do(elevator(1),move(-1),3)" 
```

now yields the output:
```
Checking model... 
error(notposs,elevator(1),3)
error(isbelow1,elevator(1),3)
Finished Checking.
```

The difference in the input lies in the first action where the move was changed from 1 to -1. Now the output says that there is an error of the type "notposs" and "isbelow1" from elevator 1 at time point 3. The notposs error means that an action was executed which was not possible to execute. Typically, this are the movement actions. The isbelow1 error means that the elevator is somehow at a position lower that the lowest floor (which is 1). Explanations for the other types of errors are in the README file.

## Instance Generator

The instance generator has multiple ways of receiving input. 1 of those is used by calling the command:
```
$ python InstanceGenerator.py -p
```

The -p argument makes the program prompt the user for the specifications of the instance. It asks for the floor amount, elevator amounts, starting position and requests.

The inputs can also be passed with arguments from the command line. It can also be specified if the starting position and/or the requests want to be randomized. A seed for the randomizer can be provided with '--seed' argument.

Additionally, the -o parameter can be used to specify the folder name where the instance will be placed. If no folder is named, the instance is created in the same folder where the script is called. Lastly, the -i parameter is used to specify how many instances want to be created.

The following command will generate a file named "instance10_(1, 2, 3)_2_0.lp" that has 10 floors, 3 elevators in the starting positions 1, 2 and 3 and an initial call request to go up from floor 7. The floor and starting positions parameters are reflected in the name of the file while the requests are not. 
```
$ python InstanceGenerator.py -f 10 -s 1 2 3 -r call,up,7
```

This command will generate 5 instances where each one has 15 floors, 2 elevators in random positions and 4 randomized requests in a folder named "instance":
```
$ python InstanceGenerator.py -f 15 -e 2 -R 4 -i 5 -o instance
```
