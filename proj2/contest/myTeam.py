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


from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import random, time, util, math
from game import Directions, Actions
import game
from util import nearestPoint
import distanceCalculator
import regularMutation

from util import Counter
from distanceCalculator import manhattanDistance

SIGHT_RANGE = 5

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
    first = 'TimidAgent', second = 'MCTSDefendAgent'):
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

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses actions which maximize the score
  """
  def chooseAction(self, gameState):
    """
    pick action with the highest Q(s,a)
    """    
    actions = gameState.getLegalActions()
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions,values) if v == maxValue]

    return random.choice(bestActions)


  def getSuccessor(self, gameState, action):
    """
    find the next successor
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
        # only half a grid position is covered
        return successor.generateSuccessor(self.index, action)
    else:
        return successor 

  def evaluate(self, gameState, action):
    """
    compute combination of features and feature weights
    """    
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    get a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState,action)
    features['successorScore'] = self.getScore(successor)
    return features
  
  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}  
        
        

class DummyAgent(CaptureAgent):
      
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
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)


class CustomAttackAgent(ReflexCaptureAgent):
  def getFeatures(self, state, action):
      	food = self.getFood(state)
  	foodList=food.asList()
  	walls = state.getWalls()
	isPacman = self.getSuccessor(state, action).getAgentState(self.index).isPacman
	
    #Zone of the board agent is primarily responsible for
  	zone=(self.index-self.index%2)/2
  	
  	teammates=[state.getAgentState(i).getPosition() for i in self.getTeam(state)]
  	opponents = [state.getAgentState(i) for i in self.getOpponents(state)]
  	chasers = [a for a in opponents if not (a.isPacman) and a.getPosition() != None]
  	prey=[a for a in opponents if a.isPacman and a.getPosition() != None]
    
  	features = util.Counter()
  	if action==Directions.STOP:
  		features["stopped"]=1.0
  	# compute the location of pacman after he takes the action
  	x, y = state.getAgentState(self.index).getPosition()
  	dx, dy = Actions.directionToVector(action)
  	next_x, next_y = int(x + dx), int(y + dy)

  	# count the number of ghosts 1-step away
  	for g in chasers:
  		if (next_x, next_y)==g.getPosition():
  			if g.scaredTimer>0:
  				features["eats-ghost"]+=1
  				features["eats-food"]+=2
  			else:
  				features["#-of-dangerous-ghosts-1-step-away"]=1
  				features["#-of-harmless-ghosts-1-step-away"]=0
  		elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  			if g.scaredTimer>0:
  				features["#-of-harmless-ghosts-1-step-away"]+=1
  			elif isPacman:
  				features["#-of-dangerous-ghosts-1-step-away"]+=1
  				features["#-of-harmless-ghosts-1-step-away"]=0
  	if state.getAgentState(self.index).scaredTimer==0:		
  		for g in prey:
  			if (next_x, next_y)==g.getPosition:
  				features["eats-invader"]=1
  			elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  				features["invaders-1-step-away"]+=1
  	else:
  		for g in opponents:
  			if g.getPosition()!=None:
  				if (next_x, next_y)==g.getPosition:
  					features["eats-invader"]=-10
  				elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  					features["invaders-1-step-away"]+=-10
  		
  			
  	for capsule_x, capsule_y in state.getCapsules():
  		if next_x==capsule_x and next_y==capsule_y and isPacman:
  			features["eats-capsules"]=1.0
  	if not features["#-of-dangerous-ghosts-1-step-away"]:
  		if food[next_x][next_y]:
  			features["eats-food"] = 1.0
  		if len(foodList) > 0: # This should always be True,  but better safe than sorry
  			myFood=[]
  			for food in foodList:
  				food_x, food_y=food
  				if (food_y>zone*walls.height/3 and food_y<(zone+1)*walls.height/3):
  					myFood.append(food)
   			if len(myFood)==0:
   				myFood=foodList
			myMinDist = min([self.getMazeDistance((next_x, next_y), food) for food in myFood])
			if myMinDist is not None:
				features["closest-food"] = float(myMinDist) / (walls.width * walls.height) 	
	
	features.divideAll(10.0)
	
	return features
  
  def getWeights(self, gameState, action):
    return {'eats-invader':5, 'invaders-1-step-away':0, 'teammateDist': 1.5, 'closest-food': -1, 'eats-capsules': 10.0, '#-of-dangerous-ghosts-1-step-away': -20, 'eats-ghost': 1.0, '#-of-harmless-ghosts-1-step-away': 0.1, 'stopped': -5, 'eats-food': 1}


      

class QCaptureAgent(CaptureAgent):
  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0
    
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    if not self.firstTurnComplete:
      self.firstTurnComplete = True
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
    
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    
    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
        
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
  
  """
  Features (not the best features) which have learned weight values stored.
  """
  def getMutationFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    position = self.getPosition(gameState)

    distances = 0.0
    for tpos in self.getTeamPositions(successor):
      distances = distances + abs(tpos[0] - position[0])
    features['xRelativeToFriends'] = distances
    
    enemyX = 0.0
    for epos in self.getOpponentPositions(successor):
      if epos is not None:
        enemyX = enemyX + epos[0]
    features['avgEnemyX'] = enemyX
    
    foodLeft = len(self.getFoodYouAreDefending(successor).asList())
    features['percentOurFoodLeft'] = foodLeft / self.startingFood
    
    foodLeft = len(self.getFood(successor).asList())
    features['percentTheirFoodLeft'] = foodLeft / self.theirStartingFood
    
    features['IAmAScaredGhost'] = 1.0 if self.isPacman(successor) and self.getScaredTimer(successor) > 0 else 0.0
    
    features['enemyPacmanNearMe'] = 0.0
    minOppDist = 10000
    minOppPos = (0, 0)
    for ep in self.getOpponentPositions(successor):
      # For a feature later on
      if ep is not None and self.getMazeDistance(ep, position) < minOppDist:
        minOppDist = self.getMazeDistance(ep, position)
        minOppPos = ep
      if ep is not None and self.getMazeDistance(ep, position) <= 1 and self.isPositionInTeamTerritory(successor, ep):
        features['enemyPacmanNearMe'] = 1.0
        
    features['numSameFriends'] = 0
    for friend in self.getTeam(successor):
      if successor.getAgentState(self.index).isPacman is self.isPacman(successor):
        features['numSameFriends'] = features['numSameFriends'] + 1

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDiffDistance = min([1000] + [self.getMazeDistance(position, food) - self.getMazeDistance(minOppPos, food) for food in foodList if minOppDist < 1000])
      features['blockableFood'] = 1.0 if minDiffDistance < 1.0 else 0.0

    return features

class CustomOffendAgent(QCaptureAgent):
    def getFeatures(self, state, action):
                
        # extract the grid of food and wall locations and get the ghost locations    
        food = self.getFood(state)                  
        walls = state.getWalls()
        successor = self.getSuccessor(state, action)
        
        opponents = [state.getAgentState(i) for i in self.getOpponents(state)]        
        ghosts = [a for a in opponents if not (a.isPacman) and a.getPosition() != None]
        scaredGhosts = [g for g in ghosts if g.scaredTimer > 0]
        nonScaredGhosts = [g for g in ghosts if g.scaredTimer == 0]
        
        features = util.Counter()        
        if action==Directions.STOP:
          features["stopped"]=1.0
            
        # compute the location of pacman after he takes the action
        x, y = state.getAgentState(self.index).getPosition()
        dx, dy = self.getDirectionalVector(action)
        next_x, next_y = int(x + dx), int(y + dy)
        
        # is there a ghost at the next step?
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in g.getPosition() for g in nonScaredGhosts)    
                        
        # is there a scared ghost at the next step?
        features["eats-ghost"] = sum((next_x, next_y) in g.getPosition() for g in scaredGhosts)
            
        # count the number of ghosts 1-step away        
        features["#-of-ghosts-1-step-away"] += sum((next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls) for g in nonScaredGhosts)
                            
        # count the number of scared ghosts 1-step away
        features["#-of-scared-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls) for g in scaredGhosts)
                            
        for capsule_x, capsule_y in state.getCapsules():
            if next_x==capsule_x and next_y==capsule_y and self.getSuccessor(state, action).getAgentState(self.index).isPacman:
                features["eats-capsules"]=1.0
            
        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0
        
        # Compute distance to the nearest food
        foodList = self.getFood(successor).asList()    
        if len(foodList) > 0: # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])            
        
        if minDistance is not None:
          # make the distance a number less than one otherwise the update
          # will diverge wildly
          features["closest-food"] = float(minDistance) / (walls.width * walls.height) 
        
        features.divideAll(10.0)
        
        return features
        
    def getWeights(self, gameState, action):        
        return {'stopped': -7.0, 'closest-food': -1.0, 'eats-capsules': 10.0, '#-of-ghosts-1-step-away': -10.0, 'eats-ghost': 5.0, '#-of-scared-ghosts-1-step-away': 0.5, 'eats-food': 1.0}
        


class Caesar1(ReflexCaptureAgent):
    
  def getFeatures(self, state, action):
  	food = self.getFood(state)
  	foodList=food.asList()
  	walls = state.getWalls()
	isPacman = self.getSuccessor(state, action).getAgentState(self.index).isPacman
	
 	#Zone of the board agent is primarily responsible for
  	zone=(self.index-self.index%2)/2
  	
  	teammates=[state.getAgentState(i).getPosition() for i in self.getTeam(state)]
  	opponents = [state.getAgentState(i) for i in self.getOpponents(state)]
  	chasers = [a for a in opponents if not (a.isPacman) and a.getPosition() != None]
  	prey=[a for a in opponents if a.isPacman and a.getPosition() != None]
    
  	features = util.Counter()
  	if action==Directions.STOP:
  		features["stopped"]=1.0
  	# compute the location of pacman after he takes the action
  	x, y = state.getAgentState(self.index).getPosition()
  	dx, dy = Actions.directionToVector(action)
  	next_x, next_y = int(x + dx), int(y + dy)
 	  	  	  	
  	# count the number of ghosts 1-step away
  	for g in chasers:
  		if (next_x, next_y)==g.getPosition():
  			if g.scaredTimer>0:
  				features["eats-ghost"]+=1
  				features["eats-food"]+=2
  			else:
  				features["#-of-dangerous-ghosts-1-step-away"]=1
  				features["#-of-harmless-ghosts-1-step-away"]=0
  		elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  			if g.scaredTimer>0:
  				features["#-of-harmless-ghosts-1-step-away"]+=1
  			elif isPacman:
  				features["#-of-dangerous-ghosts-1-step-away"]+=1
  				features["#-of-harmless-ghosts-1-step-away"]=0
  	if state.getAgentState(self.index).scaredTimer==0:		
  		for g in prey:
  			if (next_x, next_y)==g.getPosition:
  				features["eats-invader"]=1
  			elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  				features["invaders-1-step-away"]+=1
  	else:
  		for g in opponents:
  			if g.getPosition()!=None:
  				if (next_x, next_y)==g.getPosition:
  					features["eats-invader"]=-10
  				elif (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
  					features["invaders-1-step-away"]+=-10
  		
  			
  	for capsule_x, capsule_y in state.getCapsules():
  		if next_x==capsule_x and next_y==capsule_y and isPacman:
  			features["eats-capsules"]=1.0
  	if not features["#-of-dangerous-ghosts-1-step-away"]:
  		if food[next_x][next_y]:
  			features["eats-food"] = 1.0
  		if len(foodList) > 0: # This should always be True,  but better safe than sorry
  			myFood=[]
  			for food in foodList:
  				food_x, food_y=food
  				if (food_y>zone*walls.height/3 and food_y<(zone+1)*walls.height/3):
  					myFood.append(food)
  	  		if len(myFood)==0:
  	  			myFood=foodList
			myMinDist = min([self.getMazeDistance((next_x, next_y), food) for food in myFood])
			if myMinDist is not None:
				features["closest-food"] = float(myMinDist) / (walls.width * walls.height) 	
	
	features.divideAll(10.0)
	
	return features
  
  def getWeights(self, gameState, action):
    return {'eats-invader':5, 'invaders-1-step-away':1, 'teammateDist': 1.5, 'closest-food': -1, 'eats-capsules': 10.0, '#-of-dangerous-ghosts-1-step-away': -20, 'eats-ghost': 1.0, '#-of-harmless-ghosts-1-step-away': 0.1, 'stopped': -5, 'eats-food': 1}


class ApproximateAdversarialAgent(CaptureAgent):
  """
  Superclass for agents choosing actions via alpha-beta search, with
  positions of unseen enemies approximated by Bayesian inference
  """
  #####################
  # AI algorithm code #
  #####################

  SEARCH_DEPTH = 5

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

    # Get all non-wall positions on the board
    self.legalPositions = gameState.data.layout.walls.asList(False)

    # Initialize position belief distributions for opponents
    self.positionBeliefs = {}
    for opponent in self.getOpponents(gameState):
      self.initializeBeliefs(opponent)

  def initializeBeliefs(self, agent):
    """
    Uniformly initialize belief distributions for opponent positions.
    """
    self.positionBeliefs[agent] = util.Counter()
    for p in self.legalPositions:
      self.positionBeliefs[agent][p] = 1.0

  def chooseAction(self, gameState):
    # Update belief distribution about opponent positions and place hidden
    # opponents in their most likely positions
    myPosition = gameState.getAgentState(self.index).getPosition()
    noisyDistances = gameState.getAgentDistances()
    probableState = gameState.deepCopy()

    for opponent in self.getOpponents(gameState):
      pos = gameState.getAgentPosition(opponent)
      if pos:
        self.fixPosition(opponent, pos)
      else:
        self.elapseTime(opponent, gameState)
        self.observe(opponent, noisyDistances[opponent], gameState)

    self.displayDistributionsOverPositions(self.positionBeliefs.values())
    for opponent in self.getOpponents(gameState):
      probablePosition = self.guessPosition(opponent)
      conf = game.Configuration(probablePosition, Directions.STOP)
      probableState.data.agentStates[opponent] = game.AgentState(
        conf, probableState.isRed(probablePosition) != probableState.isOnRedTeam(opponent))

    # Run negamax alpha-beta search to pick an optimal move
    bestVal, bestAction = float("-inf"), None
    for opponent in self.getOpponents(gameState):
      value, action = self.expectinegamax(opponent,
                                          probableState,
                                          self.SEARCH_DEPTH,
                                          1,
                                          retAction=True)
      if value > bestVal:
        bestVal, bestAction = value, action

    return action

  def fixPosition(self, agent, position):
    """
    Fix the position of an opponent in an agent's belief distributions.
    """
    updatedBeliefs = util.Counter()
    updatedBeliefs[position] = 1.0
    self.positionBeliefs[agent] = updatedBeliefs

  def elapseTime(self, agent, gameState):
    """
    Elapse belief distributions for an agent's position by one time step.
    Assume opponents move randomly, but also check for any food lost from
    the previous turn.
    """
    updatedBeliefs = util.Counter()
    for (oldX, oldY), oldProbability in self.positionBeliefs[agent].items():
      newDist = util.Counter()
      for p in [(oldX - 1, oldY), (oldX + 1, oldY),
                (oldX, oldY - 1), (oldX, oldY + 1)]:
        if p in self.legalPositions:
          newDist[p] = 1.0
      newDist.normalize()
      for newPosition, newProbability in newDist.items():
        updatedBeliefs[newPosition] += newProbability * oldProbability

    lastObserved = self.getPreviousObservation()
    if lastObserved:
      lostFood = [food for food in self.getFoodYouAreDefending(lastObserved).asList()
                  if food not in self.getFoodYouAreDefending(gameState).asList()]
      for f in lostFood:
        updatedBeliefs[f] = 1.0/len(self.getOpponents(gameState))

    self.positionBeliefs[agent] = updatedBeliefs


  def observe(self, agent, noisyDistance, gameState):
    """
    Update belief distributions for an agent's position based upon
    a noisy distance measurement for that agent.
    """
    myPosition = self.getAgentPosition(self.index, gameState)
    teammatePositions = [self.getAgentPosition(teammate, gameState)
                         for teammate in self.getTeam(gameState)]
    updatedBeliefs = util.Counter()

    for p in self.legalPositions:
      if any([util.manhattanDistance(teammatePos, p) <= SIGHT_RANGE
              for teammatePos in teammatePositions]):
        updatedBeliefs[p] = 0.0
      else:
        trueDistance = util.manhattanDistance(myPosition, p)
        positionProbability = gameState.getDistanceProb(trueDistance, noisyDistance)
        updatedBeliefs[p] = positionProbability * self.positionBeliefs[agent][p]

    if not updatedBeliefs.totalCount():
      self.initializeBeliefs(agent)
    else:
      updatedBeliefs.normalize()
      self.positionBeliefs[agent] = updatedBeliefs

  def guessPosition(self, agent):
    """
    Return the most likely position of the given agent in the game.
    """
    return self.positionBeliefs[agent].argMax()

  def expectinegamax(self, opponent, state, depth, sign, retAction=False):
    """
    Negamax variation of expectimax.
    """
    if sign == 1:
      agent = self.index
    else:
      agent = opponent

    bestAction = None
    if self.stateIsTerminal(agent, state) or depth == 0:
      bestVal = sign * self.evaluateState(state)
    else:
      actions = state.getLegalActions(agent)
      actions.remove(Directions.STOP)
      bestVal = float("-inf") if agent == self.index else 0
      for action in actions:
        successor = state.generateSuccessor(agent, action)
        value = -self.expectinegamax(opponent, successor, depth - 1, -sign)
        if agent == self.index and value > bestVal:
          bestVal, bestAction = value, action
        elif agent == opponent:
          bestVal += value/len(actions)

    if agent == self.index and retAction:
      return bestVal, bestAction
    else:
      return bestVal

  def stateIsTerminal(self, agent, gameState):
    """
    Check if the search tree should stop expanding at the given game state
    on the given agent's turn.
    """
    return len(gameState.getLegalActions(agent)) == 0

  def evaluateState(self, gameState):
    """
    Evaluate the utility of a game state.
    """
    util.raiseNotDefined()

  #####################
  # Utility functions #
  #####################

  def getAgentPosition(self, agent, gameState):
    """
    Return the position of the given agent.
    """
    pos = gameState.getAgentPosition(agent)
    if pos:
      return pos
    else:
      return self.guessPosition(agent)

  def agentIsPacman(self, agent, gameState):
    """
    Check if the given agent is operating as a Pacman in its current position.
    """
    agentPos = self.getAgentPosition(agent, gameState)
    return (gameState.isRed(agentPos) != gameState.isOnRedTeam(agent))

  def getOpponentDistances(self, gameState):
    """
    Return the IDs of and distances to opponents, relative to this agent.
    """
    return [(o, self.distancer.getDistance(
             self.getAgentPosition(self.index, gameState),
             self.getAgentPosition(o, gameState)))
            for o in self.getOpponents(gameState)]

class CautiousAttackAgent(ApproximateAdversarialAgent):
  """
  An attack-oriented agent that will retreat back to its home zone
  after consuming 5 pellets.
  """
  def registerInitialState(self, gameState):
    ApproximateAdversarialAgent.registerInitialState(self, gameState)
    self.retreating = False

  def chooseAction(self, gameState):
    if (gameState.getAgentState(self.index).numCarrying < 5 and
        len(self.getFood(gameState).asList())):
      self.retreating = False
    else:
      self.retreating = True

    return ApproximateAdversarialAgent.chooseAction(self, gameState)

  def evaluateState(self, gameState):
    myPosition = self.getAgentPosition(self.index, gameState)
    targetFood = self.getFood(gameState).asList()
    distanceFromStart = abs(myPosition[0] - gameState.getInitialAgentPosition(self.index)[0])
    opponentDistances = self.getOpponentDistances(gameState)
    opponentDistance = min([dist for id, dist in opponentDistances])

    if self.retreating:
      return  - len(targetFood) \
              - 2 * distanceFromStart \
              + opponentDistance
    else:
      foodDistances = [self.distancer.getDistance(myPosition, food)
                       for food in targetFood]
      minDistance = min(foodDistances) if len(foodDistances) else 0
      return 2 * self.getScore(gameState) \
             - 100 * len(targetFood) \
             - 3 * minDistance \
             + 2 * distanceFromStart \
             + opponentDistance


class OpportunisticAttackAgent(ApproximateAdversarialAgent):
  def evaluateState(self, gameState):
    myPosition = self.getAgentPosition(self.index, gameState)
    food = self.getFood(gameState).asList()

    targetFood = None
    maxDist = 0

    opponentDistances = self.getOpponentDistances(gameState)
    opponentDistance = min([dist for id, dist in opponentDistances])

    if not food or gameState.getAgentState(self.index).numCarrying > self.getScore(gameState) > 0:
      return 20 * self.getScore(gameState) \
             - self.distancer.getDistance(myPosition, gameState.getInitialAgentPosition(self.index)) \
             + opponentDistance

    for f in food:
      d = min([self.distancer.getDistance(self.getAgentPosition(o, gameState), f)
              for o in self.getOpponents(gameState)])
      if d > maxDist:
        targetFood = f
        maxDist = d
    if targetFood:
      foodDist = self.distancer.getDistance(myPosition, targetFood)
    else:
      foodDist = 0

    distanceFromStart = abs(myPosition[0] - gameState.getInitialAgentPosition(self.index)[0])
    if not len(food):
      distanceFromStart *= -1

    return 2 * self.getScore(gameState) \
           - 100 * len(food) \
           - 2 * foodDist \
           + opponentDistance \
           + distanceFromStart


class EvaluationBasedAgent(CaptureAgent):
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 1.0}


class MCTSOffendAgent(EvaluationBasedAgent):
  "Gera Carlo, o agente ofensivo."

  def getFeatures(self, gameState, action):
    """
    Get features used for state evaluation.
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    # Compute score from successor state
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0:
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Compute distance to closest ghost
    myPos = successor.getAgentState(self.index).getPosition()
    enemies  = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
    if len(inRange) > 0:
      positions = [agent.getPosition() for agent in inRange]
      closest = min(positions, key = lambda x: self.getMazeDistance(myPos, x))
      closestDist = self.getMazeDistance(myPos, closest)
      if closestDist <= 5:
        features['distanceToGhost'] = closestDist

    # Compute if is pacman
    features['isPacman'] = 1 if successor.getAgentState(self.index).isPacman else 0

    return features

  def getWeights(self, gameState, action):
    """
    Get weights for the features used in the evaluation.
    """
    # If tha agent is locked, we will make him try and atack
    if self.inactiveTime > 80:
      return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 1000}

    # If opponent is scared, the agent should not care about distanceToGhost
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    enemies  = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
    if len(inRange) > 0:
      positions = [agent.getPosition() for agent in inRange]
      closestPos = min(positions, key = lambda x: self.getMazeDistance(myPos, x))
      closestDist = self.getMazeDistance(myPos, closestPos)
      closest_enemies = filter(lambda x: x[0] == closestPos, zip(positions, inRange))
      for agent in closest_enemies:
        if agent[1].scaredTimer > 0:
          return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 0, 'isPacman': 0}

    # Weights normally used
    return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 0}

  def randomSimulation(self, depth, gameState):
    """
    Random simulate some actions for the agent. The actions other agents can take
    are ignored, or, in other words, we consider their actions is always STOP.
    The final state from the simulation is evaluated.
    """
    new_state = gameState.deepCopy()
    while depth > 0:
      # Get valid actions
      actions = new_state.getLegalActions(self.index)
      # The agent should not stay put in the simulation
      actions.remove(Directions.STOP)
      current_direction = new_state.getAgentState(self.index).configuration.direction
      # The agent should not use the reverse direction during simulation
      reversed_direction = Directions.REVERSE[new_state.getAgentState(self.index).configuration.direction]
      if reversed_direction in actions and len(actions) > 1:
        actions.remove(reversed_direction)
      # Randomly chooses a valid action
      a = random.choice(actions)
      # Compute new state and update depth
      new_state = new_state.generateSuccessor(self.index, a)
      depth -= 1
    # Evaluate the final simulation state
    return self.evaluate(new_state, Directions.STOP)

  def takeToEmptyAlley(self, gameState, action, depth):
    """
    Verify if an action takes the agent to an alley with
    no pacdots.
    """
    if depth == 0:
      return False
    old_score = self.getScore(gameState)
    new_state = gameState.generateSuccessor(self.index, action)
    new_score = self.getScore(new_state)
    if old_score < new_score:
      return False
    actions   = new_state.getLegalActions(self.index)
    actions.remove(Directions.STOP)
    reversed_direction = Directions.REVERSE[new_state.getAgentState(self.index).configuration.direction]
    if reversed_direction in actions:
      actions.remove(reversed_direction)
    if len(actions) == 0:
      return True
    for a in actions:
      if not self.takeToEmptyAlley(new_state, a, depth - 1):
        return False
    return True

  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    # Variables used to verify if the agent os locked
    self.numEnemyFood = "+inf"
    self.inactiveTime = 0

  # Implemente este metodo para pre-processamento (15s max).
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.distancer.getMazeDistances()

  # Implemente este metodo para controlar o agente (1s max).
  def chooseAction(self, gameState):
    # You can profile your evaluation time by uncommenting these lines
    #start = time.time()

    # Updates inactiveTime. This variable indicates if the agent is locked.
    currentEnemyFood = len(self.getFood(gameState).asList())
    if self.numEnemyFood != currentEnemyFood:
      self.numEnemyFood = currentEnemyFood
      self.inactiveTime = 0
    else:
      self.inactiveTime += 1
    # If the agent dies, inactiveTime is reseted.
    if gameState.getInitialAgentPosition(self.index) == gameState.getAgentState(self.index).getPosition():
      self.inactiveTime = 0

    # Get valid actions. Staying put is almost never a good choice, so
    # the agent will ignore this action.
    all_actions = gameState.getLegalActions(self.index)
    all_actions.remove(Directions.STOP)
    actions = []
    for a in all_actions:
      if not self.takeToEmptyAlley(gameState, a, 5):
        actions.append(a)
    if len(actions) == 0:
      actions = all_actions

    fvalues = []
    for a in actions:
      new_state = gameState.generateSuccessor(self.index, a)
      value = 0
      for i in range(1,31):
        value += self.randomSimulation(10, new_state)
      fvalues.append(value)

    best = max(fvalues)
    ties = filter(lambda x: x[0] == best, zip(fvalues, actions))
    toPlay = random.choice(ties)[1]

    #print 'eval time for offensive agent %d: %.4f' % (self.index, time.time() - start)
    return toPlay


class TimidAgent(CaptureAgent):
    """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.escapepath = []
        self.eaten = 0
        self.height = 0
        self.width = 0
        self.plan = [[], []]

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
        self.eaten = 0

        self.height = len(gameState.getWalls()[0])
        for w in gameState.getWalls().asList():
            if w[1] == 0:
                self.width += 1

        print self.height
        print self.width


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
    """
        start = time.time()

        mypos = gameState.getAgentPosition(self.index)

        if self.getPreviousObservation() is not None:
            if self.getPreviousObservation().hasFood(mypos[0], mypos[1]):
                self.eaten += 1

        nearestFood = self.nearestFood(gameState)
        nearestEnemy = self.getNearestEnemy(gameState)

        if not gameState.getAgentState(self.index).isPacman:
            self.eaten = 0
            while len(self.plan[0]) == 0:
                y = random.choice(range(0, self.height, 1))
                if not gameState.hasWall(int(self.width / 2), y):
                    self.plan = [[int(self.width / 2) + 1, y],
                                 self.bfs(gameState, self.width, self.height, nearestEnemy,
                                          [int(self.width / 2), y])]
            if len(self.plan[1]) == 0:
                if not len(self.plan[0]) == 0:
                    self.plan[1] = self.bfs(gameState, self.width, self.height, nearestEnemy, self.plan[0])
            self.escapepath = self.plan[1]
        else:
            self.plan = [[], []]
            if len(nearestEnemy) > 0:
                if nearestEnemy[1] < 4 : #and len(self.escapepath) == 0:
                    self.escapepath = self.bfs(gameState, self.width, self.height, nearestEnemy, [self.width / 2 - 4])
                    print "RUN!!!"
            else:
                self.escapepath = []
                if self.eaten == 5:
                    self.escapepath = self.bfs(gameState, 36, 17, nearestEnemy, [self.width / 2 - 1])

        # self.debugDraw(self.escapepath, [1.0, 1.0, 1.0], True)
        # print self.escapepath

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, nearestFood, nearestEnemy, self.escapepath, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        action = random.choice(bestActions)
        return action

    def escapePath(self, game_state, width, height, enemy):

        stack = util.Stack()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        stack.push([myPos[0], myPos[1]])
        path = []

        while not stack.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                stack.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                stack.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                stack.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                stack.push(left)
                visited.append(left)
            if left in visited: loop.append(left)

            if len(loop) > 0:
                for i in reversed(path):
                    if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                        path.remove(i)
                    else:
                        break

            if myPos[0] == 1 and myPos[1] == 2:
                # self.debugDraw(path, [1.0, 1.0, 1.0], True)
                # print path
                return path

            myPos = stack.pop()

            for i in reversed(path):
                if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                    path.remove(i)
                else:
                    break
            path.append(myPos)
        return path

    def nearestFood(self, gameState):

        food = self.getFood(gameState).asList()
        distance = [self.getMazeDistance(gameState.getAgentPosition(self.index), a) for a in food]

        if len(food) < 3:
            previous = self.getFoodYouAreDefending(gameState).asList()[0]
            return [previous, self.getMazeDistance(gameState.getAgentPosition(self.index), previous)]
        nearestFood = food[0]
        nearestDstance = distance[0]

        for i in range(len(distance)):
            if distance[i] < nearestDstance:
                nearestFood = food[i]
                nearestDstance = distance[i]

        return [nearestFood, nearestDstance]

    def getNearestEnemy(self, gameState):
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes distance to invaders we can see
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        scare = 0
        if len(invaders) == 0:
            return []
        else:
            nearestEnemy = invaders[0].getPosition()
            isPacman = invaders[0].isPacman
            nearestDstance = dists[0]
            for i in range(len(dists)):
                if dists[i] < nearestDstance:
                    nearestEnemy = invaders[i].getPosition()
                    nearestDstance = dists[i]
                    scare = invaders[i].scaredTimer
        # print scare
        # self.debugDraw(nearestEnemy, [1.0, 0.5, 0.5], True)
        return [nearestEnemy, nearestDstance, scare, isPacman]

    def evaluate(self, gameState, nearestFood, nearestEnemy, escapepath, action):

        score = 0
        scorelist = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        next = gameState.generateSuccessor(self.index, action)
        nextpos = next.getAgentPosition(self.index)
        nextscore = next.getScore()

        if nextscore > gameState.getScore():
            score += 2
            scorelist[0] = 2

        # if len(nearestEnemy) > 0 > nearestEnemy[2] and nearestEnemy[1] < 3:
        #     score -= 2 * (self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
        #     scorelist[1] -= 2 * (
        #         self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])

        # if len(nearestEnemy) == 0 or nearestEnemy[1:
        if self.getMazeDistance(next.getAgentPosition(self.index), nearestFood[0]) < nearestFood[1]:
            score += 1
            scorelist[2] = 1

        pre = self.getPreviousObservation()
        if pre != None:
            if self.getPreviousObservation().getAgentPosition(self.index) == nextpos:
                score -= 5
                scorelist[3] = -5

        if len(nearestEnemy) > 0 and nearestEnemy[1] < 4:
            if next.getAgentState(self.index).isPacman:
                score += (self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
                scorelist[4] = (
                    self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
                nextActions = next.getLegalActions(self.index)
                if len(nextActions) == 2:
                    score -= 100
                    scorelist[5] = -100
        else:
            score += 2
            scorelist[6] = 2

        if len(escapepath) > 0:
            if [nextpos[0], nextpos[1]] in escapepath:
                if not (len(nearestEnemy) > 0 > nearestEnemy[2] and nearestEnemy[1] < 3):
                    score += 10
                    scorelist[7] = 10
        if action == Directions.STOP:
            score = -10
            scorelist[8] = -10

        return score

    def dfs(self, game_state, width, height, enemy):

        stack = util.Stack()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        stack.push([myPos[0], myPos[1]])
        path = []

        while not stack.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                stack.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                stack.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                stack.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                stack.push(left)
                visited.append(left)
            if left in visited: loop.append(left)

            if len(loop) > 0:
                for i in reversed(path):
                    if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                        path.remove(i)
                    else:
                        break

            if myPos[0] == 1 and myPos[1] == 2:
                # self.debugDraw(path, [1.0, 1.0, 1.0], True)
                # print path
                return path

            myPos = stack.pop()

            for i in reversed(path):
                if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                    path.remove(i)
                else:
                    break
            path.append(myPos)
        return path

    def bfs(self, game_state, width, height, enemy, point):

        queue = util.Queue()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        queue.push([myPos[0], myPos[1]])

        path = []

        while not queue.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                queue.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                queue.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                queue.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                queue.push(left)
                visited.append(left)

            if left in visited: loop.append(left)

            # if len(loop) > 0:
            #     for i in reversed(path):
            #         if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
            #             path.remove(i)
            #         else:
            #             break
            myPos = queue.pop()
            path.append(myPos)

            # print path
            if len(point) == 1:
                if myPos[0] == point[0]:
                    a = myPos
                    f = []
                    for i in reversed(path):
                        if abs(a[0] - i[0]) + abs(a[1] - i[1]) <= 1:
                            f.append(i)
                            a = i
                            # self.debugDraw(f, [1.0, 1.0, 1.0], True)
                    return f
            else:

                if myPos[0] == point[0] and myPos[1] == point[1]:
                    a = myPos
                    f = []
                    for i in reversed(path):
                        if abs(a[0] - i[0]) + abs(a[1] - i[1]) <= 1:
                            f.append(i)
                            a = i
                            # self.debugDraw(f, [1.0, 1.0, 1.0], True)
                    return f

        return []

class MCTSDefendAgent(CaptureAgent):
  """
  Defensive Agent using Monte Carlo Search Tree method
  to defend the home spots and capsules
  """
  # Implement the preprocessing procedure (max 15s)
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.distancer.getMazeDistances()        
  
  """
  goal: the target defender will arrest
  lastObservedFood: the food last observed
  defensivePoint: the points defender are patrolling in our home map
  """
  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.goal = None
    self.previousObservedFood = None
    self.guardPoint = {}
    self.defensiveDistance(gameState)
    #Get central positions 
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    if self.blue:
          position = ( width- 2)/2 + 1
    else:
          position = (width - 2)/2
    # get the central position
    self.guardPositions = []
    for i in range(1, height - 1):
          if not gameState.hasWall(position, i):
                self.guardPositions.append((position, i))
    
    #Remove some unnecesaary positions
    while len(self.guardPositions) > (height - 2)/2:
          self.guardPositions.pop(0)
          self.guardPositions.pop(len(self.guardPositions) - 1)
    
  # choose the action defender will do in the next round (max 1s)
  def chooseAction(self, gameState):

  # choose the target defender should guard      
  def chooseTarget(self):
        

  # calculate the distance from food to guard points 
  def defensiveDistance(self, gameState):


  