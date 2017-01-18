%Elevator encoding

#include "../strats/select.lp".
#include "../strats/train.lp".

#show do/3.

#const istop  = "SAT".
#const imin   = 0.
#const imax   = 100.


#program base.

action(move(1)).
action(move(-1)).
action(wait).
action(serve).

reqtype(call).
reqtype(deliver).

dir(up).
dir(down).


holds(F,0) :- init(F).

#program step(t).
#external history(E, A, t) : agent(E), action(A).
do(E, A, t) :- history(E, A, t).

1 { do(E,A,t) : action(A) } 1       :-  agent(E).
:- do(E,A,t), not possible(E,A,t).

%%% Preconditions

possible(E,wait,t) :- agent(E).

possible(E,move(Y),t)           :-  holds(at(E,Pos),t-1),
                                    action(move(Y)),
                                    floor(Pos + Y).

possible(E,serve,t)	   		    :-  agent(E).

%%% Effects

holds(at(E,F+Y),t)				            :-  do(E,move(Y),t), holds(at(E, F),t-1).

abnormal(at(E,F),t)		    			    :-	do(E,move(Y),t), holds(at(E,F),t-1).


abnormal(request(call(D),Floor),t) 	        :-	do(E,serve,t),
                                                holds(request(call(D),Floor),t-1),
											    holds(at(E,Floor),t).


abnormal(request(deliver(ID),Floor), t) 	:-	do(E,serve,t), E = elevator(ID),
                                                holds(request(deliver(ID),Floor), t-1),
                                                holds(at(E,Floor),t-1).


% Inertia
holds(F,t) :- holds(F,t-1), not abnormal(F,t).


% static laws

:- holds(at(E,F),t), holds(at(E,F2),t), F != F2.

:- holds(at(E,F),t), F < 1.
:- holds(at(E,F),t), F > floors.


#external callrequest(D, Floor, t) : dir(D), Floor = 1..floors.
#external deliverrequest(ID, Floor, t) : ID = 1..agents, Floor = 1..floors.

holds(request(call(D),Floor), t) :- callrequest(D, Floor, t).
holds(request(deliver(ID),Floor), t) :- deliverrequest(ID, Floor, t).


#program check(t).
#external query(t).

goal(t) :- not holds(request(_,_),t).

%#minimize{ 1, E : do(E,_,t) }.

:- not goal(t), query(t).
