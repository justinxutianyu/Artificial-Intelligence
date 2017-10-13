# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from pddl.pddl_template import *
from captureAgents import CaptureAgent
import random, time, util, math
from game import Directions
import game
import os
from subprocess import call


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AggressiveAgent', second = 'AggressiveAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.
    
  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  agent1 = eval(first)(firstIndex)
  agent2 = eval(second)(secondIndex)
  agent1.UpdateAnxiety(0.20)
  agent2.UpdateAnxiety(0.80)
    #we should do a bit of magic here I have some ideas about shared info
  # The following line is an example only; feel free to change it.
  return [agent1, agent2]

##########
# Agents #
##########
class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST:  (1, 0),
                   Directions.WEST:  (-1, 0),
                   Directions.STOP:  (0, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action
    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP
    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed = 1.0):
        dx, dy =  Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x,y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors
    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)

def distance(pos1, pos2):
    return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)

#finds shortest pair wise from pos to listOfFrontier
def shortestPathEZone(pos,listOfFrontier, mazeDistFunctor):
    rItem = None
    pathLength = 9999999999
    for item in listOfFrontier:
        tmp = mazeDistFunctor(pos,item)
        if(tmp < pathLength):
            rItem = item
            pathLength = tmp
    return rItem

def DeadendNormalize(initialS, action):
    if(action == "SOUTH"): initialS.remove("NORTH")
    if(action == "NORTH"): initialS.remove("SOUTH")
    if(action == "EAST"): initialS.remove("WEST")
    if(action == "WEST"): initialS.remove("EAST")
    if("STOP" in initialS): initialS.remove("STOP")

def getSuccessors(walls, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = 1#self.costFn(nextState)
                successors.append( ( nextState, action, cost) )
        return successors
    
def isDeadend(loc, initialS = [], action = [], walls = [], initialStateMultiDir = False):
    
    if(action == []):
        action = getSuccessors(walls, loc)
    if(len(action) == 2):
        #split
        if(isDeadend(loc, [],action[0][1], walls) or isDeadend(loc, [],action[1][1], walls)):
            return True
        else:
            return False
    if(len(action) > 2):
        return False

    action = action[0][1]
    if(len(initialS) == 0): 
        for item in getSuccessors(walls, loc):
            initialS.append(item[1])
        
    DeadendNormalize(initialS,action)
    if(initialStateMultiDir):
        if(len(initialS) == 1):
            return True
        else:
            return False
    while(len(initialS) == 1):
        #print initialS
        loc = (loc[0] + Actions.directionToVector(initialS[0])[0], loc[1] + Actions.directionToVector(initialS[0])[1])
        #print loc
        action = initialS[0][1]
        for item in getSuccessors(walls, loc):
            initialS.append(item[1])
        DeadendNormalize(initialS, action)
        if(len(initialS) == 0): return True
        if(len(initialS) > 1): return False
    if(len(initialS) == 0): return True
    if(len(initialS) > 1): return False
  
def Interpolate(a, b, alpha):
    return a + (b - a) * alpha
  
def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def AggroHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is non-trivial.
    """
    val = 0
    if(state in problem.nGoals):
        val += 10000000
    
    for item in problem.nGoals:
        val += 100.0 / (1 + distance(state,item))
        if(distance(state,item) <= 1):
            val += 10000000
    if(state in problem.killableEnemies):
        val -= 100
    if(isDeadend(state,[],[],problem.walls)): #instead of doing this here do this when finding a pallet, order by safe then to hardest to get.
        v += 200
    return distance((state[0],state[1]),problem.goal) + val

class problemS():

    def __init__(self, startingPosition, walls, goal, negativeGoals, killableEnemies):
        
        self.start = startingPosition
        self.walls = walls
        self.nGoals = negativeGoals
        self.killableEnemies = killableEnemies
        self.goal = goal
        self.startingGameState = None
        self._expanded = 0 # DO NOT CHANGE
        #self.heuristicInfo = {} # A dictionary for the heuristic to store information
    def getStartState(self):
        return self.start
    def setGoal(self, goal):
        self.goal = goal
    def isGoalState(self, state):
        return self.goal == state
    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = 1#self.costFn(nextState)
                successors.append( ( nextState, action, cost) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    from util import PriorityQueue
    start = problem.getStartState()

    if(problem.isGoalState(start)):
        return []
    frontier = problem.getSuccessors(start)
    closedList = [start]
    dict = {}
    listOfFrontier = []
    pqQueue = PriorityQueue()
    movementList = []
    #initialization
    for item in frontier:
        listOfFrontier.append(item)
    cheapest = aStarPath(problem, (start, 0, 0) ,pqQueue, listOfFrontier, dict, closedList, heuristic)
    #now that we have the cheapest, OR a decent solution lets rebuild the path backwards
    if(cheapest == None):
        return []
    inc = cheapest[0]
    while (inc != start):
        movementList.append(dict[inc][1])
        inc = dict[inc][0][0]
    #return the reverse list of movements to achieve the outcome
    return movementList[::-1]
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()
#Non recursive implementation of the A* algorithm...(recursion is terrible with exponential stuff)

def aStarPath(problem, expanded, myQueue, listOfFrontier, dict, closedList, heuristic):
    from util import PriorityQueue
    while((myQueue.isEmpty() == False) or len(listOfFrontier) > 0):
        tmpList = []
        #apply heuristics and costs to frontier
        for item in listOfFrontier:
            item = (item[0], item[1], item[2] + expanded[2])
            myQueue.push(item, item[2] + heuristic(item[0], problem))
            #build a path forwards for reconstruction backwards
            if(dict.has_key(item[0]) == False):
                dict[item[0]] = (expanded, item[1], item[2] + heuristic(item[0], problem))
        if(myQueue.isEmpty()):
            return expanded
        cheapest = myQueue.pop()
        #cull those that have been seen before at a cheaper weighting.
        while((cheapest[0] in closedList)):
            if(myQueue.isEmpty()):
                return cheapest
            cheapest = myQueue.pop()
        closedList.append(cheapest[0])
        if(problem.isGoalState(cheapest[0])):
            return cheapest

        listOfFrontier = problem.getSuccessors(cheapest[0])
        ls = []
        #get new frontiers from the successors, and also cull those already expanded
        for item in listOfFrontier:
            if(item[0] not in closedList):
                ls.append(item)
                #build a path forwards for reconstruction backwards
                if(dict.has_key(item[0])):
                    if(dict[item[0]][2] > (cheapest[2] + item[2] + heuristic(item[0], problem))):
                        dict[item[0]] = (cheapest, item[1], cheapest[2] + item[2] + heuristic(item[0], problem))

        expanded = cheapest
        listOfFrontier = ls

def RightA(original, val):
    if(val >= original):
        return True
    return False

def LeftA(original, val):
    if(val <= original):
        return True
    return False

def isGhost(gamestate, index):
    str = ""
    S = "{}".format(gamestate.getAgentState(index))
    for item in S:
        if(item != ':'):
            str = str + item
        else:
            break
    print str
    if(str == "Ghost"):
        return True
    return False

#Supply LISTS of your current food, AND the self.getDefendingFood....thing, This Function can be improved to linear time... will be done during optimization
def GetChangeInOurFood(currentFood, defendingFood):
    posseseses = []
    for pos in currentFood:
        if(pos not in defendingFood):
            posseseses.append(pos)
    return posseseses

#returns a tuple (goal, goalThatIsNotADeadend)
def GetClosestFood(pos, self, gameState):
    pathL = 9999999
    pathL2 = 9999999
    #first sort by distance, not being done right now -- Might not be necessary since all locations are cached...
    
    foodItem = (None, None)
    foodItem2 = (None,None)
    #This is just finding the closest pallet/food to eat
    #problemA = problemS(gameState.getAgentPosition(self.index), gameState.getWalls(), None, negativeGoals=[],killableEnemies=[])
    foodList = self.getFood(gameState).asList()
    for capsule in self.getCapsules(gameState):
        foodList.append(capsule)
    for food in foodList:
        tmp = self.getMazeDistance(pos, food)
        if tmp < pathL:
            foodItem = food
            pathL = tmp

        if tmp < pathL2:
            if(not isDeadend(loc=food, walls=gameState.getWalls(), initialStateMultiDir=True)):
                foodItem2 = food
                pathL2 = tmp
    return (foodItem, foodItem2)
  
def UpdateFleeing(pos, self, gameState, goal):
    #IF the agent is safe in any sense, reset
    if(self.Safe(self.original,pos[0])):
        #self.startingPosition = pos
        self.Fleeing = False
        self.foodCount = 0
    if((len(self.getFood(gameState).asList()) < 3) or self.Fleeing):
        goal = self.startingPosition
        #goal == one_and_only_goal
    #every step decide randomly if we should dump the pallets/food
    if(not self.Fleeing):
        t = len(self.getFood(gameState).asList())
        if(t <= 0):
            t = 1
        #randomly choose to go home to protect pallet/food based on how many you have.
        turnaround = random.randint(0,len(self.getFoodYouAreDefending(gameState).asList()))
        if(gameState.data.agentStates[self.index].scaredTimer < 2):
            if(turnaround < self.foodCount):
                if(self.fleeingCD <= 0):
                    self.Fleeing = True

    #if the current agent intersects a pallet/food, isnt supplied normally.
    if(pos in self.getFood(self.prevGameState).asList()):
        self.foodCount += 1
    return (self,goal)
    
def GetFoodChanges(changes, self, gameState):
    
    if(len(self.currentFoodCount) > len(self.getFoodYouAreDefending(gameState).asList())):
        Achanges = GetChangeInOurFood(self.currentFoodCount, self.getFoodYouAreDefending(gameState).asList())
        if(len(Achanges) != 0):
            changes = []
            changes = Achanges
    return changes
    
def MaximizeScoring(stayAwayFF, self, goal, gameState):
    pos = gameState.getAgentPosition(self.index)
    for agent in self.getTeam(gameState):
        if(agent == self.index):
            continue #we are looking at ourselves...oh no self-awareness!
        if(not self.Fleeing):
            stayAwayFF.append(gameState.getAgentPosition(agent)) #Add other team members
    #reset just in case, seeing an issue
    #changes = []
    for agent in self.getOpponents(gameState): # Try for our enemies...
        en = gameState.getAgentPosition(agent)
        #if we can ACTUALLY see them (we should have a limited memory instead of reflex actions like this... we will get there
        if(en != None):
            if(self.Safe(self.original, en[0])): #IF the enemy is 'Safe' within our zone... :P
                if(self.getMazeDistance(pos, en) * 0.01 < self.getMazeDistance(pos, goal)): #if it is closer than our current goal... just default to it
                    goal = en #OVERRIDE GOAL (goal) To represent the enemy agent
            else:
                
                if(gameState.data.agentStates[agent].scaredTimer < 2):
                    stayAwayFF.append(en) #otherwise just stay away from it
                    if(distance(en,pos) <= 3.9): #SHOULD BE CHANGED WHEN Memory is used, for now it see's how far the enemy agent is
                        #if its hot on its trail then just flee back home as nothing more can actually be done... --- Potentially add pallets to optional goals so that it can maximise
                        #Score while fleeing.....
                        #if(isGhost(gameState,agent)):
                        for capsule in self.getCapsules(gameState):
                            goal = capsule
                            return (stayAwayFF, self, goal)
                        self.Fleeing = True
                else:
                    self.fleeingCD = gameState.data.agentStates[agent].scaredTimer - 1
    return (stayAwayFF, self, goal)
    
def Intercept(goal, self, changes, gameState):
    if(len(self.getFoodYouAreDefending(gameState).asList()) <(self.threashold)):#try using score but try negating it first (because it might be the opposite team)
        if(len(changes) == 0):
            return (goal, self)
        #if(not self.Safe(self.original, pos[0])):
            #goal = self.startingPosition
        pos = gameState.getAgentPosition(self.index)
        interceptPathStart = shortestPathEZone(changes[0], self.frontiers, self.getMazeDistance)
        #myProblem = problemS(interceptPathStart, gameState.getWalls(), changes[0], stayAwayFF, [])
        goal = interceptPathStart
        if(pos == goal or self.intercepting):
            goal = changes[0]
            self.intercepting = True
        if(pos == goal):
            self.intercepting = False
            goal = GetClosestFood(pos, self, gameState)[0]
            return (goal, self)
        # = aStarSearch(myProblem, AggroHeuristic)
        #print ("WE SHOULD START INTERCEPTING: ", interceptPath)
        for agent in self.getOpponents(gameState): # Try for our enemies...
            en = gameState.getAgentPosition(agent)
            #if we can ACTUALLY see them (we should have a limited memory instead of reflex actions like this... we will get there
            if(en != None):
                if(self.Safe(self.original, en[0])):
                    goal = en
    return (goal, self)

def doesPathIntersectWithEnemy(actions, pos, enemyPos):
    for action in actions:
        if(action == "SOUTH"): pos = (pos[0], pos[1] - 1)
        if(action == "NORTH"): pos = (pos[0], pos[1] + 1)
        if(action == "EAST"): pos = (pos[0] + 1, pos[1])
        if(action == "WEST"): pos = (pos[0] - 1, pos[1])
        if(pos in enemyPos):
            return True
    return False
class AggressiveAgent(CaptureAgent):


    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        #get coordinates of the entire space (LIMITED TO 2D SINCE ITS EXPLICIT)
        #-----------------------------------------------------------------#
        #INITIALIZATION
        topLeft = (0,0)
        #could be a problem if the algorithm doesnt find the longest dist....
        bottomRight = (0,0)
        #FUNCTOR for safe locations.
        self.Safe = None
        #Basically trying its hardest to reach safety
        self.Fleeing = False
        self.startingPosition = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.currentFoodCount = self.getFoodYouAreDefending(gameState).asList()
        self.totalDefFood = len(self.currentFoodCount)
        self.lastKnownEnemyPosition = []
        self.dangerousEnemies = []
        self.killableEnemies = []
        #prevGameState provides a snapshot of the previous session....
        self.prevGameState = gameState
        self.foodCount = 0
        self.original = 0
        self.changes = []
        self.intercepting = False
        self.fleeingCD = 0
        self.threashold = Interpolate(1.0,float(self.totalDefFood), self.Anxiety)
        self.maxMoves = 300
        #frontiers of the enemy zone
        self.frontiers = []
        #NEEDS TO BE USED INSTEAD OF LOCAL (LOCAL IN THE SENSE OF SCOPE) memory
            #To be used well it needs to have an expirey time (I WOULD RECOMMEND 4 or so steps, then updating and storing a tuple rather
            #than the individual locations of x then y etc etc --- HORRIBLE FORMAT I KNOW SUE ME..... Couldnt be fucked. (KAI - ALECK FIX IF YOU CARE)
        for item in self.getOpponents(gameState):
            #Last Seen enemy regardless of where I am
            self.lastKnownEnemyPosition.append(999999999)
            self.lastKnownEnemyPosition.append(999999999)
            #Dangerous only contains enemies that are in their own safe zone
            #killable contains enemies that are outside
            self.dangerousEnemies.append(999999999)
            self.killableEnemies.append(999999999)
            self.dangerousEnemies.append(999999999)
            self.killableEnemies.append(999999999)
        self.ourFronteirs = []
        #END INITIALIZATION
        #-----------------------------------------------------------------#
        #figures out the most distant corner from topLeft, (ASSUMES a RECTANGLE -- could be false but screw it)
        for wall in gameState.getWalls().asList():
            if(wall[0] + wall[1] > bottomRight[0] + bottomRight[1]):
                bottomRight = wall
        #IF we are the RED TEAM, basically we subtract or add one so that the division doesnt get rid of the mid point.
        if(gameState.getAgentPosition(self.index)[0] > bottomRight[0]/2):
            self.Safe = RightA
            self.original = int(bottomRight[0]/2) + 1
            y = 0
            while y != bottomRight[1]:
                if((self.original, y) not in gameState.getWalls().asList()):#PERREN FIX THIS TO BE LINEAR TIME!!!! OPTIMIZATION
                    self.frontiers.append((self.original, y))
                if((self.original - 1, y) not in gameState.getWalls().asList()):
                    self.ourFronteirs.append((self.original -1, y))
                y += 1
        else:
            self.Safe = LeftA
            self.original = int(bottomRight[0]/2) - 1
            y = 0
            while y <= bottomRight[1]:
                if((self.original, y) not in gameState.getWalls().asList()):#PERREN FIX THIS TO BE LINEAR TIME!!!! OPTIMIZATION
                    self.frontiers.append((self.original, y))
                if((self.original + 1, y) not in gameState.getWalls().asList()):
                    self.ourFronteirs.append((self.original + 1, y))
                y += 1

        '''
        Your initialization code goes here, if you need any.
        '''
    def UpdateAnxiety(self, val):
        self.Anxiety = val
    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        #dangerousEnemies = []
        #currently the local positions (individual indicies) -- again, sue me...
        killableEnemies = []
        actions = gameState.getLegalActions(self.index)
        
        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        #USEAGE OF GetChangeInOurFood...
        changes = self.changes
        changes = GetFoodChanges(changes, self, gameState)
        #these changes (provided its not empty) are the locations of the enemy and which food they just ate... could be useful
        #self.currentFoodCount = self.getFoodYouAreDefending(gameState).asList() -- to make sure its updated once found
        #print enemyLoc
        self.currentFoodCount = self.getFoodYouAreDefending(gameState).asList()
        #print "we know the enemy is at: ", (a in self.currentFoodCount not in self.getFoodYouAreDefending(gameState).asList())
        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        path = []
        pos = gameState.getAgentPosition(self.index)
        
        temp = GetClosestFood(pos, self, gameState)
        goal = temp[0]
        #if(temp[1] != (None, None)):
        #    goal = temp[1]


        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        enemyLoc = []
        i = 0
        for item in self.getOpponents(gameState):
            loc = gameState.getAgentPosition(item) #Tries to get enemy locations
            if loc == None: #IF THIS IS FALSE THEN THE AGENT CAN SEE THEM!
                i += 2
                continue
            if(len(loc) != 0):
                #print loc
                self.lastKnownEnemyPosition[i] = loc[0]
                self.lastKnownEnemyPosition[i+1] = loc[1]
                if(self.Safe(self.original,loc[0])): #This means that the enemy is within OUR safe Zone
                    killableEnemies.append(loc[0])
                    killableEnemies.append(loc[1])
                else:
                    self.dangerousEnemies[i] = loc[0]
                    self.dangerousEnemies[i + 1] = loc[1] #any self.X(LIST) is not really in use right now...
            i += 2
        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        #IF THERE IS LESS THAN 3 FOOD LEFT THEN JUST GO STRAIGHT HOME (this is because we basically win then)
        #If already fleeing override the food to be home (just to be simple) -- goal IS THE GOAL.

        self, goal = UpdateFleeing(pos, self, gameState, goal)

        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        
        stayAwayFF = [] #stay away from friends to maximise scoring. (ONLY LOOKS AT CURRENT FRAME -- could have issues)
        stayAwayFF, self, goal = MaximizeScoring(stayAwayFF,self,goal, gameState)

        ####################################################################################
        ####################################################################################
        ####################################################################################
        ####################################################################################
        #lets generate a snapshot of the current game and solve it.
        #pos = position, walls (self explaining), goal is the GOAL, stayAwayFF is the set of negativeGoals, havent yet exposed optional goals (not imp in heuristic)
        #to stop any overlap
        interceptPath = []
        minReturnDist = 999999
        returnPos = (0,0)
        for item in self.ourFronteirs:
            tmp = self.getMazeDistance(item, pos)
            if(tmp < minReturnDist):
                returnPos = item
                minReturnDist = tmp
        if(self.maxMoves - 3 < minReturnDist):
            goal = returnPos
        goal, self = Intercept(goal,self,changes,gameState)
        if(pos in self.getCapsules(gameState)):
            self.fleeing = False
        #else:
            #self.intercepting = False
        if(goal == pos):
            if(len(changes) != 0):
                goal = changes[0]
            else:
                goal = self.getFood(gameState).asList()[0]
        
        foodList = self.getFood(gameState).asList()
        for capsule in self.getCapsules(gameState):
            foodList.append(capsule)
        
        myProblem = problemS(pos, gameState.getWalls(), goal, stayAwayFF, foodList)
        path = aStarSearch(myProblem, AggroHeuristic) #Solve...

        self.changes = changes
        self.prevGameState = gameState #late-update.
        '''
        You should change this in your own agent. #should I?
        '''
        self.maxMoves -= 1
        #get first move.
        if(len(path) != 0):
            return path[0]
        path = aStarSearch(myProblem) #Solve...
        if(doesPathIntersectWithEnemy(pos, path, stayAwayFF)):
            if(not self.Safe(self.original,pos[0])):
                self.fleeing = True
        if(len(path) != 0):
            return path[0]
        #print "ERROR", goal, pos, self.getMazeDistance(pos,goal)
        #or if the path has not been successful (negative goals or stuck), then move randomly -- ALSO could be useful to check if moved to the same location 3 times in the past 5 turns...
        return random.choice(actions)


class BlankAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)
    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    
    
    domain = PDDLDomain("pac-man")
    problem = PDDLProblem("pac-man-problem", domain)

    coords = {}
    coords["food"] = self.getFood(gameState).asList()
    coords["power_pellet"] = self.getCapsules(gameState)
    coords["walls"] = gameState.getWalls().asList()
    coords["enemies"] = [
        gameState.getAgentPosition(enemy)
        for enemy in self.getOpponents(gameState)
    ]
    coords["agents"] = [
        gameState.getAgentPosition(agent)
        for agent in self.getTeam(gameState)
    ]
    #Enemy Agents
    objects = ""
    i = 0
    for item in coords["enemies"]:
        problem.objects.append(PDDLObject("enemy{}".format(i)))
        i += 1

    i = 0
    for item in coords["enemies"]:
        if(item == None):
            item = (-1,-1)
        problem.initial_state.append(PDDLState("\n\t(locEnemy enemy{} x{} y{})".format(i, item[0], item[1])))
        i += 1

    #Friendly agent
    pos = gameState.getAgentPosition(self.index)
    problem.objects.append(PDDLObject("agent".format(i)))
    problem.initial_state.append(PDDLState("\n\t(loc agent x{} y{})".format(pos[0], pos[1])))

    #Food
    for item in coords["food"]:
        problem.initial_state.append(PDDLState("\n\t(locF x{} y{})".format(item[0], item[1])))
        i += 1

    #Power pellet
    for item in coords["power_pellet"]:
        problem.initial_state.append(PDDLState("\n\t(locP x{} y{})".format(item[0], item[1])))
        i += 1

    #Walls
    for item in coords["walls"]:
        problem.initial_state.append(PDDLState("\n\t(wall x{} y{})".format(item[0], item[1])))
        i += 1
    
    problem.to_file("test.pddl")
    input()
    #pred_x = PDDLPredicate("is-good", ["x"])
    #pred_y = PDDLPredicate("is-bad", ["x", "y"])

    #state_y = PDDLState("not", [pred_y])
    #state_x = PDDLState("and", [pred_x, state_y])

    #do_this = PDDLAction("do-this", ["x", "y"], state_y, state_x)
    #do_that = PDDLAction("do-that", ["x"])

    #domain.add_predicate(pred_x)
    #domain.add_predicate(pred_y)
    #domain.add_action(do_this)

    #domain.to_file("test.pddl")

    #print(self.getFood(gameState)[0][10])
    #path = []
    #pathL = 9999999
    #first sort by distance, not being done right now -- Might not be necessary since all locations are cached...
    #pos = gameState.getAgentPosition(self.index)
    #print(self.getMazeDistance(pos, (3,3)))
    #input()
    #actions = gameState.getLegalActions(self.index)
    #for food in self.getFood(gameState).asList():
#        tmp = self.getMazeDistance(pos, food)
    #    if tmp < pathL:
    #        goal = food
    #        pathL = tmp
    """
    return "Stop"

##########
# Agents #
##########

#Globals used for PDDLAgent
constants = []

class PDDLAgent(CaptureAgent):

    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)

        global constants
        constants = self.genInitConstants(gameState)


    def chooseAction(self, gameState):
        possactions = gameState.getLegalActions(self.index)
        
        global constants
        
        domain = PDDLDomain("PacmanDomain",open("pacman_pddl_domain.pddl", "r").read())
        objects = self.genObjects(gameState)
        predicates = self.genPredicates(gameState)
        initialState = PDDLState("InitialState", predicates + constants)
        goalPred = self.genGoals(gameState)
        goalState = PDDLState("GoalState", goalPred)

        pddlProblem = PDDLProblem("PacmanProblem", domain, objects, initialState, goalState)
        
        pddlProblem.to_file("pacman_pddl_problem.pddl")
        
        plan = call("./ff -o pacman_pddl_domain.pddl -f pacman_pddl_problem.pddl -s 0 >> output.format", shell=True)
        actionFIle = open("output.format", "r")
        try :
            actionsToFormat = actionFIle.read().split("step")[1].split("\n\n")[0].split("\n")
            
            actions = []
            for action in actionsToFormat :
                alist = action.split( )
                if alist[1] == "moveDown":
                    actions.append("South")
                if alist[1] == "moveUp":
                    actions.append("North")
                if alist[1] == "moveLeft":
                    actions.append("West")
                if alist[1] == "moveRight":
                    actions.append("East")  
            os.remove("output.format") 
        except IndexError :
            os.remove("output.format") 
            return possactions[-1]
                
        return actions[0]

    def genInitConstants(self, gameState) :
        global constants
        if constants :
            return constants

        width = gameState.data.layout.width
        height = gameState.data.layout.height
        (cpi, cpj) = gameState.getAgentPosition(self.index)

        constants = []

        # This populates the left, right, up, down without walls
        # Also populates the onLeftSide list
        for i in range(1,width) :
            for j in range(1,height) :

                if i - 1 > 0 and not gameState.hasWall(i - 1, j) :
                    l = PDDLPredicate("left", ["n" + str(i),"n"+ str(j), "n" + str(i - 1),"n" + str(j)])
                    constants.append(l)
                if i + 1 < width and not gameState.hasWall(i + 1, j) :
                    r = PDDLPredicate("right", ["n" + str(i), "n" + str(j), "n" + str(i + 1), "n" + str(j)])
                    constants.append(r)
                if j - 1 > 0 and not gameState.hasWall(i, j - 1) :
                    d = PDDLPredicate("down", ["n" + str(i), "n" + str(j), "n" + str(i), "n" + str(j - 1)])
                    constants.append(d)
                if j + 1 < height and not gameState.hasWall(i, j + 1) :
                    u = PDDLPredicate("up", ["n" + str(i), "n" + str(j), "n" + str(i), "n" + str(j + 1)])
                    constants.append(u)
                if i < width / 2 :
                    on = PDDLPredicate("leftSideSquare", ["n" + str(i), "n" + str(j)])
                    constants.append(on)

        # Populating constant booleans
        if cpi < width / 2 :
            ol = PDDLPredicate("isLeftSide")
            constants.append(ol)

        return  constants

    def genPredicates(self, gameState) :

        # TODO - Capsules and enemy capsules

        predicates = []
        (cpi, cpj) = gameState.getAgentPosition(self.index)
        predicates.append(PDDLPredicate("curLoc", ["n" + str(cpi), "n" + str(cpj)]))

        agentPos = []
        enemyList = []

        for item in self.getTeam(gameState):
            apos = gameState.getAgentPosition(item)
            if apos != (cpi,cpj) :
                agentPos.append(apos)
        for item in self.getOpponents(gameState) :
            epos = gameState.getAgentPosition(item)
            enemyList.append(epos)


        # Produce food location predicates
        foodGrid = self.getFood(gameState).asList()

        for (f1,f2) in foodGrid :
            f = PDDLPredicate("locF", ["n" + str(f1), "n" + str(f2)])
            predicates.append(f)

        # Produce capsule location predicates
        for (p1,p2) in self.getCapsules(gameState) :
            c = PDDLPredicate("locP", ["n" + str(p1), "n" + str(p2)])
            predicates.append(c)

        # Produce agent location predicates
        for (a1, a2) in agentPos :
            a = PDDLPredicate("locA", ["n" + str(a1), "n" + str(a2)])
            predicates.append(a)

        # Produce enemy locations
        for (e1,e2) in [x for x in enemyList if x != None] :
            e = PDDLPredicate("locEnemy", ["n" + str(e1), "n" + str(e2)])
            predicates.append(e)
            
        return predicates

    def genObjects(self,gameState) :
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        
        objects = []

        if height > width :
            max = height
        else :
            max = width

        for i in range(1,max) :
            objects.append(PDDLObject("n" + str(i)))

        return objects
        
    def genGoals(self, gameState) :
        glist = []
        (c1,c2) = gameState.getAgentPosition(self.index)
        minF = min([(self.getMazeDistance((c1,c2), (f1,f2)), (f1,f2)) for (f1,f2) in self.getFood(gameState).asList()])
        (f1,f2) = minF[1]
        g = PDDLPredicate("curLoc", ["n" + str(f1), "n" + str(f2)])
        glist.append(g)
        return glist
