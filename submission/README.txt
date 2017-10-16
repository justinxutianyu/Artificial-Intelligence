COMP90054 AI Planning For Autonomy
Project 2, 2017

Team: Random_Team
Team members: Junwen Zhang, 791773 
              Ziyi Zhang, 798838
              Tianyu Xu, 818236


  ##############################
  ##                          ##
  ##       Run the code       ##
  ##                          ##
  ##############################

1. Usage
-------------------------
Our code is implemented by python. The agent we implemented is saved in myTeam.py. 
To run our code, use the select agent flag to choose the agent for both sides of the competition.

python capture.py -r myTeam -b myTeam -l RANDOM1875
         
Advanced Options:         
                          -r # Set the red agent
                          -b # Set the blue agent
                          -l # Load different layout file eg. RANDOM<Number>
                          -n # Run more competitions in one command
                          -q # Disable the diplay the graphics


2. Code Structure
---------------------------
 2.1 Expectimax Agent
 This class implements the Expectimax agent. It simulates all the actions it will take and 
 the actions opponents will take based on the game state it is situated in. Then it will 
 recursively search the future possible actions and choose the suboptimal action in the future.
 In the agent's round, the agent itself will always adapt the best action. In the opponent's round,
 it will assume the oppoents is clever enough and it will choose the least expectation it can 
 get no matter what action the opponent will take. We set the action time limit and max depth to
 ensure our action will not exceed the time limit of game rule(1s). Besides, when traversing the 
 game simulation tree, it uses Alpha-Beta pruning to decrease the search space and time complexity.
 It uses the Alpha value to filter in its own round and uses the Beta valueto filter in the opponent's round.


 2.2 Inference Module
 This module implements the particle filter to infer the position belief distributions of the opponents.
 It begins with a uniform distribution over ghost positions. Then it updates the beliefs based on the 
 distance observation and Pacman's position. The global variable particles keep storing the posiiton and 
 their particles. The probabilities of the opponents are transformed from the particles. Specially, when 
 a pacman is captured, it will reinitialize the positon belief of the opponent and set it to the starting point.

 2.3 Heuristic Search
 The agent use the heuristic search method to calculate the value for the action evaluation. The weights are 
 manually set by ourselves although it has a Q-learning agent which may get the near perfect heuristic function.
 The features are set before the game starting and the values of those features are calculated when doing evaluation.
 We not only consider the distance of the enemies but also the distance to food, capsules. We use "food_defend" to 
 adjust the efforts between attack and defense. We also take the food carried and food returned into consideration.
 We hope the agent do a tradeofff between eating new food and return the carrying food. 




  ##############################
  ##                          ##
  ##       PDDL Planner       ##
  ##                          ##
  ##############################


We have 4 pddl files which are two domain files and two problem files each for ghost and pacman.


In the pacman domain file, we define 4 acitons and a rule.The rule is that if a super pacman eats a ghost, he will become unsuper. In the pacman domain file，each aciton will take two parameters.  
The first action is moving to a normal location. At that normal location, there will be no ghost, no food and no capsule. 
The second action is moving to eat the food. In this action, the pacman will move to eat the food next to him. 
The third action is moving to eat the capusle. In this move, when the pacman meet a capsule on its way to eat food,the pacman will eat the capsule.Then his statement will be eating capsule which means the pacman will become super and can eat the ghost.
The forth action is moving to eat the ghost. This action happens when the pacman is super and on his way to food.If there is a ghost, the pacman will eat the ghost and become unsuper.


In the pacman problem file, we define an inital grid that looks like the following graph. * means walls, F means food, P means pacman, G means ghost, C means capsule, H means this location is home for pacman.

 -------------------------------------
 |  H  |  H  |  H  |     |     |  P  |
 -------------------------------------
 |  H  |  H  |  H  *     |     |  C  |
 -------*****-------------*****-------
 |  H  *  H  |  H  |     |     *  G  |
 -------------------------------------
 |  H  |  H  |  H  |     |     |  F  |
 -------*****-------------*****-------
 |  H  *  H  |  H  *     |     *  F  |
 -*****-------------------------*****-
 |  H  |  H  |  H  |     |     |     |
 -------------------------------------

The goal state is to eat all the food and go back to the home area location. 
We use our pacman-domain pddl file to solve the problem of our pacman-problem pddl file and get a plan.
The steps show below:

(move_to_eat_capsule l05 l15)
(move_to_eat_ghost l15 l25)
(move_to_eat_food l25 l35)
(move_to_eat_food l35 l45)
(move l45 l35)
(move l35 l34)
(move l34 l33)
(move l33 l32)
(reach-goal)

According to this plan, we can see that first the pacman eats the capsule,then it becomes super.Second,it eats the ghost and become unsuper. Third,it eats the food that is nearest to it. Finally, it eats all other foods and goes back to the home location.



In the ghost doamin file, we define 3 actions and a rule.The rule is that if a ghost moves to a super pacman, it will return to the home location and meanwhile the pacman will become unsuper.
The first action is moving to a normal location. At that location, there will be no pacman. 
The second action is moving to eat pacman. In this action, the ghost will eat the unsuper pacman next to him. 
The third action is moving to super Pacman. In this action, the ghost will move to the location which has a super pacman, and then the ghost will be eaten by that super pacmam and go back to the inital place which is the home location.Meanwhile,the super pacman will become unsuper.

In the ghost problem file, we define an inital grid that looks like the following graph.
H means this location is home location for ghost. SP means super pacman. G means ghost.

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

 The goal state for the ghost is to eat all the pacman.
 We use our ghost-domain pddl file to solve the problem defined in ghost-problem pddl file,then get a plan.
 The steps show below:

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

 According to the plan, we can see that the ghost first move to the nearest super pacman and then the ghost go back to home location, meanwhile the pacman become unsuper. Next, the ghost eats all the unsuper pacmans.
 
 




