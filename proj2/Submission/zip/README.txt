---- PDDL part -----
we have 4 pddl files. there will be a domain file and a problem file for ghost and pacman.
In the pacman domain file, we define 4 acitons and if a super pacman eats a ghost, he will become unsuper. For the pacman domain file and each aciton will take two parameters.  
The first action is move. In this action, the pacman just moves to a normal location. At that normal location, there will be no ghost, no food and no capsule. 
The second action is move to eat the food. In this action, the pacman will move to eat the food next to him. 
The third action is move to eat the capusle. In this move, if there is a capsule on the pacman`s way to eat the food. The pacman will eat the capsule and his statement will be eatcapsule which means the pacman will become super and can eat the ghost.
The forth action is move to eat the ghost. In this move, if the pacman is super and on his way to food there is a ghost, the pacman will eat the ghost and become unsuper.
In the pacman problem file, we define a inital grid that looks like the following graph. * means walls, F means food, P means pacman, G means ghost, C means capsule, H means this location is home for pacman.

 -------------------------------
 |(H)P |     *     |     |  F  |
 -------------------------------
 |  C  |     |     |     *  G  |
 -------*****-------------------
 |  G  *     |  F  |     |     |
 -------------------*****-*****-
 |  F  *     |     *     |  F  |
 -*****-------------------------
 |     |     |     |     |     |
 -------------------------------

The goal state is to eat all the food and go back to the home location. 
We use our pacman-domain pddl file to solve our pacman-problem pddl file and get a plan.
like the following steps:

(move_to_eat_capsule l00 l10)
(move_to_eat_ghost l10 l20)
(move_to_eat_food l20 l30)
(move l30 l31)
(move l31 l21)
(move_to_eat_food l21 l22)
(move l22 l23)
(move l23 l13)
(move l13 l03)
(move_to_eat_food l03 l04)
(move l04 l03)
(move l03 l02)
(move l02 l12)
(move l12 l22)
(move l22 l32)
(move l32 l42)
(move l42 l43)
(move l43 l44)
(move_to_eat_food l44 l34)
(move l34 l33)
(move l33 l43)
(move l43 l42)
(move l42 l32)
(move l32 l31)
(move l31 l30)
(move l30 l20)
(move l20 l10)
(move l10 l00)

According to this plan, we can see that the pacman first eats the capsule and becomes super and eat the ghost and become unsuper and then eat the food that nearest to him. Next, he eats all other food and goes back the the home location.

In the ghost doamin file, we define 3 actions and if a ghost moves to a super pacman, he will return to the home location and the pacman will become unsuper.
The first action is move. In this action, the ghost just moves to a normal location. A t that location, there will be no pacman. 
The second action is move_to_eat_pacman. In this action, the ghost will eat the unsuper pacman next to him. 
The third action is move_to_superPacman. In this action, the ghost will move the location which has a super pacman, and then be eaten by that pacmam and go back to the inital place which is the home location.
In the ghost problem file, we define a inital grid that looks like the following graph.
H means this location is home for ghost. SP means super pacman. G means ghost.

-------------------------------
 | SP  |     *     |     |     |
 -------------------------------
 |     |     | SP  |     *     |
 -------*****-------------------
 |     *     |     |     | SP  |
 -------------------*****-*****-
 |     *     |     *     |     |
 -*****-------------------------
 |     |     |     |     |(H)G |
 -------------------------------

 The goal state is to eat all the pacman.
 We use our ghost-domain pddl file to solve our ghost-problem pddl file and get a plan.
 like the following steps:

(move l44 l43)
(move l43 l42)
(move l42 l32)
(move l32 l31)
(move l31 l30)
(move l30 l20)
(move l20 l10)
(move_to_eat_superpacman l10 l00 l44)
(move l44 l43)
(move l43 l42)
(move l42 l32)
(move l32 l22)
(move_to_eat_pacman l22 l12)
(move l12 l13)
(move l13 l23)
(move_to_eat_pacman l23 l24)
(move l24 l23)
(move l23 l22)
(move l22 l12)
(move l12 l11)
(move l11 l10)
(move_to_eat_pacman l10 l00)

 According to the plan, we can see that the ghost first move the nearest pacman and then go back to home location and the pacman become unsuper. Next, the ghost eats all the pacman.



