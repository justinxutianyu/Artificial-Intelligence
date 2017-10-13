1. PPDL:

Domain for Pacman's perspective:
"pacman-ghost-not-moving.pddl"

Problem file for Pacman's perspective:
"pacman.pddl"

Domain for ghost's perspective:
"ghost-pacman-not-moving.pddl"

Problem for ghost's perspective:
"ghost.pddl"


For assumptions, please refer to the problem files. They are commented in.


2: Pacman Agents:

file: team.py

we have designed and implemented two agents for this contest, one specified 
for offensive and the other one for defensive and both of agents are based 
on A star search to accomplish their goal states. Each agent will search for 
a series of actions to achieving its goal states then take the first action 
in this series to get into the next state and repeat the previous search in 
the next state considering new observation of dots and enemies. 

For the attacker agent, its separates the goal for getting points into two 
steps which the first step is to take the nearest dot and the second is to 
carry the dot back to our territory. Both of these steps should avoid engaging 
with enemies by increasing the heuristic values to infinite when observing enemies. 
For step one the heuristic function is the distance to the closest dots plus the 
quantity of remaining food and the second one is the distance to the initial 
position. The switching mechanism is whether the agent is carrying a dot. If it 
has a dot, it will calculate the path using the heuristic for food otherwise, 
it uses the heuristic for going back.  

For the defender agent, it uses A star search to find the goal coordinate, and spits
out a path to that goal. the heuristic it uses to reach that goal is quite simple, it
is the maze distance. 

The 'goal coordinate' is defined as follows:
-is there an enemy pacman visible? if so then the enemy's position is the goal
-is there a power capsul present? if so then that is the goal
-what is the biggest cluter of food that I am defending? if there is no pacman visible
and no power capsules left then that is my goal

Depending on the situation of the gameState, different goals are being defined and updated.

In any case once the ghost defensive agent reaches the goal coordinate, it will then 'float' and 
return a random legal action, and return back to the goal position.   



Regards,
Wilkins Leong -leongw1@student.unimelb.edu.au
Tim Chen -botianc@student.unimelb.edu.au
