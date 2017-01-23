%Elevator encoding


#program base.

error(notposs).
error(isbelow1).
error(isabovemax).
error(multactions).
error(longmove).

error(clone).
error(badreq).

time(0).
time(T-1) :- time(T), T > 0.
time(T) :- do(_,_,T).

action(move(1)).
action(move(-1)).
action(wait).
action(serve).


holds(F,0) :- init(F).


error(notposs, E, T) :- do(E,A,T), not possible(E,A,T).

%%% Preconditions

possible(E,wait,T) 		:- agent(E), time(T).

possible(E,move(Y),T) 	:-  holds(at(E,Pos),T-1),
                                    action(move(Y)),
                                    floor(Pos + Y).

possible(E,serve,T)	  	 :- agent(E), time(T).

possible(E,serve,T)	     :-  agent(E), time(T).
%%% Effects

holds(at(E,F+Y),T)				      		:-  do(E,move(Y),T), holds(at(E, F),T-1).

abnormal(at(E,F),T)							:-	do(E,move(Y),T), holds(at(E,F),T-1).


abnormal(request(call(D),Floor),T) 	      	:-	do(E,serve,T),
                                                holds(request(call(D),Floor),T-1),
											    holds(at(E,Floor),T).


abnormal(request(deliver(ID),Floor), T) 	:-	do(E,serve,T), E = elevator(ID),
                                                holds(request(deliver(ID),Floor), T-1),
                                                holds(at(E,Floor),T-1).


% Inertia
holds(F,T) :- holds(F,T-1), not abnormal(F,T), time(T).

% static laws as errors


error(isbelow1, E, T) 		:- holds(at(E,F),T), F < 1.
error(isabovemax, E, T) 	:- holds(at(E,F),T), F > floors.

error(multactions, E, T) 	:- do(E, A, T), do(E, A2, T), A != A2.

error(longmove, E, T) 		:- holds(at(E, F), T-1), holds(at(E, F2), T), |F2-F| > 1.


error(clone, E, T) 			:- holds(at(E,F),T), holds(at(E,F2),T), F != F2.

error(badreq, R, noelev) 	:- holds(R, T), R = request(deliver(ID),Floor), not agent(elevator(ID)).
error(badreq, R, nofloor) 	:- holds(R, T), R = request(deliver(ID),Floor), not floor(Floor).

error(badreq, R, nofloor) 	:- holds(R, T), R = request(call(D),Floor), not floor(Floor).

noerror(E) :- { error(Type,E,T) : error(Type), time(T) }=0, agent(E).


#show error/3.
#show noerror/1.

