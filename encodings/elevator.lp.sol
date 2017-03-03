% INSERT NAMES AND EMAIL ADDRESSES OF YOUR GROUP MEMBERS:
%
%

%#include <incmode>. % built-in incremental mode of clingo

#show. % output atoms will be declared below

#program base. % static rules go below

dir( 1).
dir(-1).

taken(F) :- init(request(deliver(E),F)).
quest(F) :- init(request(call(D),F)).
guess(F) :- quest(F), not taken(F).

given(elevator(E),F, 1) :- init(request(deliver(E),F)), init(at(elevator(E),G)), G < F.
given(elevator(E),F,-1) :- init(request(deliver(E),F)), init(at(elevator(E),G)), F < G.
given(A,D)              :- given(A,F,D).
given(A)                :- given(A,D).

range(A,F) :- given(A,F,D).
range(A,F) :- agent(A), guess(F).

limit(A,F, 1) :- init(at(A,G)), F != #inf, F = #max{H : range(A,H), G < H}.
limit(A,F,-1) :- init(at(A,G)), F != #sup, F = #min{H : range(A,H), H < G}.
limit(A,D)    :- limit(A,F,D).

prior(A,-1) :- limit(A,-1), limit(A,1), not given(A).
prior(A,-1) :- limit(A,-1), given(A,1).
prior(A, 1) :- given(A,-1), limit(A,1), not given(A,1).

cando(A,F,D) :- limit(A,L,D), floor(F), init(at(A,G)), H = D*F, D*G < H, H <= D*L.
cando(A,F,D) :- limit(A,L,-D), floor(F), init(at(A,G)), H = D*F, D*L < H, H <= D*G, prior(A,D).

{ take(A,F) : agent(A) } = 1 :- guess(F).

taken(A,F)           :- take(A,F).
taken(elevator(E),F) :- init(request(deliver(E),F)).

order(A,F,D) :- taken(A,F), init(at(A,G)), dir(D), D*G < D*F.
order(A,F,D) :- order(A,F+D,D), init(at(A,G)), cando(A,F,D), D*G < D*F.
order(A,F,D) :- order(A,G+D,D), init(at(A,G)), cando(A,F,D), order(A,F-D,-D), prior(A,D).

stage(A, 1,0) :- given(A, 1).
stage(A,-1,0) :- given(A,-1), not given(A,1).
stage(A, 1,0) :- init(at(A,F)), order(A,F+1, 1), not given(A).
stage(A,-1,0) :- init(at(A,F)), order(A,F-1,-1), not given(A), not order(A,F+1,1).

holds(X,0) :- init(X).

#program step(t). % actions, effects, and minimization go below

#show do(A,X,t) : do(A,X,t). % output atoms indicating actions

clear(A,F,t) :- holds(at(A,F),t-1), taken(A,F), quest(F).
clear(F,t)   :- clear(A,F,t).

do(elevator(E),serve,t) :- holds(request(deliver(E),F),t-1), holds(at(elevator(E),F),t-1).
do(A,serve,t)           :- holds(request(call(D),F),t-1), clear(A,F,t), guess(F).
do(A,move(D),t)         :- stage(A,D,t-1), not do(A,serve,t).

holds(request(deliver(E),F),t) :- holds(request(deliver(E),F),t-1),
                                  not holds(at(elevator(E),F),t-1).
holds(request(call(D),F),t)    :- holds(request(call(D),F),t-1), not clear(F,t).
holds(at(A,F),t)               :- holds(at(A,F-D),t-1), do(A,move(D),t), cando(A,F,D).
holds(at(A,F),t)               :- holds(at(A,F),t-1),
                                  not holds(at(A,F+1),t), not holds(at(A,F-1),t).

stage(A,D,t) :- order(A,F+D,D), holds(at(A,F),t-1), stage(A,D,t-1).
stage(A,D,t) :- order(A,G+D,D), init(at(A,G)), prior(A,D), stage(A,-D,t-1), not stage(A,-D,t).

:~ do(A,move(D),t). [1,A,t]

#program check(t). % fulfillment of all requests can, e.g., be checked as follows
#external query(t).
#show holds(X,t) : holds(X,t). % output atoms indicating states

:- query(t), stage(A,D,t).

:- stage(A,1,t), stage(A,-1,t).
:- agent(A), #count{F : holds(at(A,F),t)} != 1.
