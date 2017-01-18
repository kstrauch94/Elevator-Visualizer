
# Examples

## Visualizer

With the default configuration of the visualizer one can run the following command:
```
$ python Elevator.py
```

This pops up 2 windows. One contains 4 labeled buttons and one contains the visualization of the instance. It has 1 elevator shaft with the elevator(red square) currently sitting in the 3rd floor. Pressing the next action button moves the elevator and updates the stat display on the left side. After clicking the button a couple times, the square will eventually turn green. This means that a "serve" action was executed.

Running the command
```
$ python Elevator.py -i instances/Elevatorinstance2.lp
```

to change the default instance to "instances/Elevatorinstance2.lp" opens 2 windows. One has the familiar buttons and the other now has 4 elevator shafts with the elevators sitting in the first floor. As before, the buttons work the same way. The next action solves the instance and moves the elevators one time step, the add request buttons add more requests to the solver and the reset button resets the instance.

Now, using the command 
```
$ python Elevator.py -e encodings/Elevator.lp encodings/Elevator.lp
```

to change the default encoding variable to now contain two encodings, the program will now spawn 3 windows. One contains the usual buttons and the other 2 contain the elevator instance visualization. We can diferentiate which is which by looking at the title of the window. One of them will be called "elevator.lp (1)" and the other "elevator.lp (2)". This is useful when there are multiple encodings that want to be executed concurrently. What happens to one instance is completely unrelated to the others. This way it is possible to visualize the different plans of the different encodings. In this case, however, the plan is the same since the encodings are the same.

The clingo solver arguments can be given in the options variables in the Config.py file. Every option must be a separate item in the list. For more information on those options use the command "clingo -h".

## Checker

Outputing the help with the command:
```
$ python Checker -h
```

explains the arguments that can be given.

Now, use the following command from the home directory of the packgage:
```
$ python Checker.py encodings/checker.lp instances/Elevatorinstance.lp -a "do(elevator(1),move(1),1)" "do(elevator(1),move(-1),2)" "do(elevator(1),move(-1),3)" 
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
$ python Checker.py encodings/checker.lp instances/Elevatorinstance.lp -a "do(elevator(1),move(-1),1)" "do(elevator(1),move(-1),2)" "do(elevator(1),move(-1),3)" 
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

The instance generator has 3 ways of receiving input. 1 of those is used by calling the command:
```
$ python InstanceGenerator.py -p
```

The -p argument makes the program prompt the user for the specifications of the instance. It asks for the floor amount, elevator amounts, starting position and requests.

The second and third ways are similar. One of them involves passing the starting positions of all elevators using the -s parameter. The other one involves saying how many elevators there are in the instance using the -e parameter, defaulting the starting positions for all elevator to floor 1. By using any of these 2 methods the rest of the parameters must also be given. Use -h to read more about them.

Additionally, the -o parameter can be used to specify the folder name where the instance will be placed. If no folder is named, the instance is created in the same folder where the script is called.

The following command will generate a file named "instance10_(1, 2, 3).lp" that has 10 floors, 3 elevators in the starting positions 1, 2 and 3 and an initial call request to go up from floor 7. The requests must have the form "call,D,F" or "del,E,F" with D = up | down, E = elevator number and F = target floor. The floor and starting positions parameters are reflected in the name of the file while the requests are not. 
```
$ python InstanceGenerator.py -f 10 -s 1 2 3 -r call,up,7
```
