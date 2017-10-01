The University of Melbourne
COMP90054 Software Agents
Project 2, 2013

Team PacMania:
Aram Kocharyan, aramk, 359867
Brendan Studds, bpstudds, 269713
John Fulton, jful, 269328
Yichang Zhang, yichangz, 542656

APPROACH:

A number of basic and some more advanced rules have been implemented for the
pacman and are described below.

The pacman will by default find the closest food and move towards it. This
behaviour is overridden in special cases where the pacman needs to take some
special actions based on the situation.

If the the pacman can see a ghost, the cost of any action which moves closer
to the ghost is increased. This means that the pacman will attempt to run away
from a ghost when necessary. With this behaviour, however, it was observed that
the pacman would often run into dead ends. As a result, some pre-processing was
implemented to determine which squares lead to a dead end. When the pacman is
being chased, he will avoid going down these routes in the direction of the dead
end where possible. He still gets caught in dead ends a lot, however, due to
not being able to see the ghosts and the fact that many pieces of food are down
dead ends.

There is also some co-operative behaviour introduced. If a pacman is being
chased by a ghost, the other pacmen will prioritise eating super food if there
are any available on the map. This can be particularly effective in layouts
where stalemates can occur in the centre.

The map is also broken up into 'zones' and each pacman is designated a zone.
While there is still food in his zone, a pacman will prioritise this food
over food in the other zone to ensure that any two pacmen will not get in
eachothers way attempting to eat the same food.

Both pacmen initially both go for food, however when one dies, it defends and
any currently defending pacman will switch back to going for food.

IMPLEMENTATION:

Initially a PDDL implementation was tried, however after experimenting with a
python implementation, it outperformed the PDDL version and was chosen to
replace it.

The python implementation operates using metrics and weights. At each time
step, a number of metrics are calculated for each move and stored in a hash map.
These are things like 'how close am I to a ghost', 'How far away is the nearest
food' etc. These metrics are then given weightings. Negative weightings indicate
that a metric is bad, positive weightings are good, with the absolute value
of the weighting indicating the degree of goodness/badness.

The intent is to allow metrics to be univesal, but different weightings can be
given to different types of agents to produce different behaviour. For instance,
a defending agent might weight 'distance to enemy pacman' higher when it is a
ghost, whilst an eating pacman may completely ignore this metric by giving it
a weighting of 0.

See 'getMetrics' and 'getWeights' in PacManiaSearchAgents.py for code relating
to metrics and weights.

RUNNING:

To run the planner, simply run 'python capture.py' and specify
PacManiaSearchAgents as the agent on either the red/blue team as desired.
No additional setup required.

ANALYSIS:

Strengths:

- Good at dealing with being chased, especially when super-food is available
- Pacmen go for different food and don't get in eachothers way
- Ignoring vulnerable ghosts means the enemy ghosts are helpless for longer
	and we can eat food faster.

Weakness:

- Still gets caught down dead ends
- Does not listen for enemy ghosts/pacmen
- Can sometimes stale-mate on the border between friendly and enemy space.
- Going for the closest food not really optimal. No consideration of going for
	'dense pockets' of food.