%Elevator Instance

#program base.

#const floors = 10.

#const start1 = 3.

#const startingReqs = 2.

#const agents=1.    % number of elevators
agent(elevator(1..agents)).

floor(1..floors).

init(at(elevator(1), 3)).

init(request(deliver(1), 2)).
init(request(call(up), 9)).

callrequest(up,2,7).