

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The current (static) state of the game would be set 
% dynamically for each time tick. The 'planner' then assesses the
% set of actions to achieve the goal state for the Pacman and ghosts
% given an unchanging environment.
%

% For example:
pacManAt(0, 0, s0).         % pacManAt(xCoord, yCoord, situation).
ghostAt(3, 3, 0, s0).       % ghostAt(xCoord, yCoord, scared, situation). Scared is tracked externally and passed in as 0 or 1.
ghostAt(3, 4, 0, s0).
wallAt(2, 2).               % wallAt(xCoord, yCoord).
foodAt(4, 4, s0).           % foodAt(xCord, yCoord, situation).
powerPelletAt(0, 4, s0).    % powerPelletAt(xCord, yCoord, situation).


% Convience to check if two positions are adjacent
adjacent(X1, Y1, X2, Y2) :- 
(
    (abs(X1 - X2) == 1, abs(Y1 - Y2) == 0);
    (abs(X1 - X2) == 0, abs(Y1 - Y2) == 1)
).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Primitive action precoditions
%

% Both Pacman and ghosts can move.
poss(move(X1, Y1, X2, Y2), S) :- 
(
    \+wallAt(X2, Y2),  
    adjacent(X1, Y1, X2, Y2),
    (pacManAt(X1, Y1, S) ; ghostAt(X1, Y1, _, S))
).

% Pacman can eat food
poss(eatFood(X1, Y1, X2, Y2), S) :-
(
    foodAt(X2, Y2, S),  
    adjacent(X1, Y1, X2, Y2, S),
    pacManAt(X1, Y1, S)
).

% ... or power pellets
poss(eatPowerPellet(X1, Y1, X2, Y2), S) :-
(
    powerPelletAt(X2, Y2, S),  
    adjacent(X1, Y1, X2, Y2, S),
    pacManAt(X1, Y1, S)
).

% ... or ghosts (if he has eaten a power pellet).
poss(eatGhost(X1, Y1, X2, Y2), S) :-
(
    ghostAt(X2, Y2, Scared, S),  Scared > 0,
    adjacent(X1, Y1, X2, Y2, S),
    pacManAt(X1, Y1, S)
).

% A ghost can eat Pacman (and only Pacman, no eating walls).
poss(eatPacman(X1, Y1, X2, Y2), S) :-
(
    pacManAt(X2, Y2, S),
    adjacent(X1, Y1, X2, Y2),
    ghostAt(X1, Y1, Scared, s), Scared == 0
).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Successor state axioms
%

% Pacman is at a place if he moves to it, or if he was already at a place and
% doesn't leave or get eaten.
pacManAt(X, Y, do(A, S)) :- 
(
    ( 
        A == move(_, _, X, Y);
        A == eatFood(_, _, X, Y);
        A == eatPowerPellet(_, _, X, Y),
        A == eatGhost(_, _, X, Y)
    ); 
    ( 
        pacManAt(X, Y, S),
        (
            A \= eatPacman(X, X, _, _),
            A \= move(X1, Y1, _, _),
            A \= eatFood(X1, Y1, _, _),
            A \= eatPowerPellet(X1, Y1, _, _),
            A \= eatGhost(X1, Y1, _, _)
        )
    )
).


% A ghost is at a place if it moves to it, or if it's already at a place
% and does not leave it.
ghostAt(X, Y, Scared, do(A, S)) :-
(
    (
        A == move(_, _, X, Y);
        A == eatPacman(_, _, X, Y)
    );
    (
        ghostAt(X, Y, Scared, S),
        (
            A \= move(X, Y, _, _),
            A \= eatPacman(X, Y, _, _)
        )
    )
).

foodAt(X, Y, do(A, S)) :- 
(
    foodAt(X, Y, S),
    A \= eatFood(_, _, X, Y)
).

powerPelletAt(X, Y, do(A,S)) :-
(
    powerPelletAt(X, Y, S),
    A \= eatPowerPellet(_, _, X, Y)
).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Trying to get a running prolog
%

% do(control, s0, S')? to execute
legal(s0).
legal(do(A, S)) :- legal(S), poss(A,S).





% Wrong stuff
% Primitive actions
% move(X1, Y1, X2, Y2, S).
% eat(X1, Y1, X2, Y2, S).

% Fluents
% pacManAt(X, Y, S).
% ghostAt(X, Y, S).
% wallAt(X, Y, S).
% foodAt(X, Y, S).
% powerFoodAt(X, Y, S).
% vulnerableGhosts(Timer, S).  % how do we track this

% poss(eat(X1, Y1, X2, Y2, S), S) :-
% (
%     (
%         pacManAt(X1, Y1, S),
%         (
%             1 == 0
%         )
%     );
%     (
%         ghostAt(X1, Y1, S),
%         (
%             1 == 0
%         )
%     )
% ).