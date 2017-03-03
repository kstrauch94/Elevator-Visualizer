## Server specifications

To interact with the visualizer client the server must have certain properties:

- It must read the message and identify the query type.
- Possibly identify the parameters
- Craft a specific response and send it

### Message form

The messages from the client will always have the following form:

MESSAGE_TYPE + "\n" + ARGUMENTS + "\n" + END_DELIMITER + "\n"

The new line characters are there to indicate that a certain part of the message has ended.

### Message types and responses

The message types can all be seen in the ServerConfig.py file. The following shows the message types from the client and the proper response:
```
Type : BASE
Message Form : BASE + "\n" + instance in string form + DONE + "\n"
Proper Response : dictionary serialized with json containing the keys, FLOORAMT, STARTPOS, REQUESTS + "\n" + DONE + "\n"
```
```
Type : ENCODING
Message Form : ENCODING + "\n" + user input string + "\n" + DONE + "\n"
Proper Responde : SUCCESS or FAIL + "\n" + DONE + "\n"
```
```
Type: SOLVE
Message Form : SOLVE + "\n" + time step to solve from + "\n" + DONE + "\n"
Proper Response : dictionary serialized with json containing the keys ACTIONS, REQUESTS, STATS. ACTIONS key is required, REQUESTS and STATS are not.
```
```
Type : ADDREQS
Message Form : ADDREQS + "\n" + Arguments separated by comma : type, time, request parameter, floor + "\n" + DONE + "\n"
Proper Responde : SUCCESS or FAIL + "\n" + DONE + "\n"
```
```
Type : RESET
Message Form : RESET + "\n" soft or hard + "\n" DONE + "\n"
Proper Responde : SUCCESS or FAIL + "\n" + DONE + "\n"
```
### Notes
####For the BASE message:
The value of the REQUESTS key is defined in the solved message notes below. For this one, only the ones at point 0 are necessary.

The value of the FLOORAMT key must be in integer representing the amount of floors in the instance.

The value of the STARTPOS key must be a list of integers. The integers represent the starting positions of the elevator represented by its index number starting from 1. E.G the list [3,2,5] says that elevator 1 starts in floor 3, elevator 2 in floor 2 and elevator 3 in floor 5.

####For the SOLVE message:
The dictionary in the value of the ACTIONS key must have integer keys representing the time steps. The values for those keys must be a list of lists (or tuples). Each list (tuple) must contain the elevator integer key in the first position and the action type in the second (as defined in the Contants.py file.

The dictionary in the value of REQUESTS key must also have integer keys representing the time steps. Each value be a list of the active requests at that time point. Note that the actual format of the value in the list is up to the server but those strings will be used by the visualizer. Hence, having those strings be something meaningful is helpful for the user.

The dictionary in the value of the STATS key must have keys representing the names of the stats. The valye of those keys must be a string representation of the stat.

#### For the ENCODING and ADDREQS messages
These message types are not necessary to implement. If they are not supported simply return a failure message.
#### For the RESET message
A soft reset means to just start again from the beggining, deleting any request which might have been added and any action history being kept. This usually means that we want to use the same instance.
A hard reset means that the instance has changed. A hard reset message is always sent before sending a new instance.

### Example Messages and Responses
Please note the new lines. All the msaage types in caps should be replace by their respective value defined in the Constants.py file.

####BASE Message:
```
BASE
"instance in string form"
DONE
```
#### BASE response
```
{"startpos": [3], "flooramt": 10, "requests": {"0": ["deliver(1) to 2", "call(up) from 9"], "7": ["call(up) from 2"]}}
DONE
```
####SOLVE Message:
```
SOLVE
0
DONE
```
####SOLVE RESPONSE (Note the ... that shorten the example):
```
{"requests": {"0": ["deliver(1) to 2", "call(up) from 9"], ... , "stats": {"Total Grounding Time": "Total Grounding Time = 0", ... , "actions": {"1": [[1, 1]], "2": [[1, 1]], "3": [[1, 1]], "4": [[1, 1]], ... , "15": [[1, 0]]}}
DONE
```
#### ADDREQS Call request Message (Note the "up" argument for the request):
```
ADDREQS
call
6
up
3
DONE
```
#### ADDREQS Deliver request Message (Note the "1" argument for the request:
```
ADDREQS
deliver
8
1
4
```
#### Success response for ADDREQS, ENCODING, RESET:
```
SUCCESS
DONE
```
#### Fail response for ADDREQS, ENCODING, RESET:
```
FAIL
DONE
```
#### RESET Message:
```
RESET
soft
DONE
```
#### ENCODING Message (Note that path/to/file is user input and depending on the server implementation different messages may be sent E.g a simple int identifier):
```
ENCODING
path/to/file
DONE
```

