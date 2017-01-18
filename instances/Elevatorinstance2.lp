%Elevator Instance

#program base.

#const floors = 10.

#const start1 = 1.
#const start2 = 1.
#const start3 = 1.
#const start4 = 1.


#const startingReqs = 2.

#const agents=4.    % number of elevators
agent(elevator(1..agents)).

floor(1..floors).

init(at(elevator(1), 1)).
init(at(elevator(2), 1)).

init(at(elevator(3), 1)).
init(at(elevator(4), 1)).

init(request(deliver(1), 2)).
init(request(call(up), 9)).


