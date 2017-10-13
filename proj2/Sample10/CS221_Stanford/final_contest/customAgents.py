# baselineAgents.py
# -----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import distanceCalculator
import random, time, util
from game import Directions
import keyboardAgents
import game
from game import Directions, Actions
from util import nearestPoint
import regularMutation

#############
# FACTORIES #
#############

NUM_KEYBOARD_AGENTS = 0
class CustomAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, isRed, first='offense', second='defense', third='offense', rest='offense', **args):
    AgentFactory.__init__(self, isRed)
    self.agents = [first, second, third]
    self.rest = rest

  def getAgent(self, index):
    if len(self.agents) > 0:
      return self.choose(self.agents.pop(0), index)
    else:
      return self.choose(self.rest, index)

  def choose(self, agentStr, index):
    if agentStr == 'keys':
      global NUM_KEYBOARD_AGENTS
      NUM_KEYBOARD_AGENTS += 1
      if NUM_KEYBOARD_AGENTS == 1:
        return keyboardAgents.KeyboardAgent(index)
      elif NUM_KEYBOARD_AGENTS == 2:
        return keyboardAgents.KeyboardAgent2(index)
      else:
        raise Exception('Max of two keyboard agents supported')
    elif agentStr == 'offense':
      return CustomOffensiveAgent(index)
    elif agentStr == 'defense':
      return DefensiveReflexAgent(index)
    else:
      raise Exception("No staff agent identified by " + agentStr)

class AllOffenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)

  def getAgent(self, index):
    return OffensiveReflexAgent(index)

class OffenseDefenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)
    self.offense = False

  def getAgent(self, index):
    self.offense = not self.offense
    if self.offense:
      return OffensiveReflexAgent(index)
    else:
      return DefensiveReflexAgent(index)

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
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

class CustomOffensiveAgent(ReflexCaptureAgent):
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
        
    
class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = self.getMutationFeatures(gameState, action)
    successor = self.getSuccessor(gameState, action)
    
    features['successorScore'] = self.getScore(successor)
    
    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    features['numFood'] = len(foodList)
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    weights = regularMutation.aggressiveDWeightsDict
    weights['successorScore'] = 1.5
    # Always eat nearby food
    weights['numFood'] = -1000
    # Favor reaching new food the most
    weights['distanceToFood'] = -5
    return weights

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  
  def getAdjacentPositions(self, gameState, pos):
    adjacent = []
    adjacent.append(pos)
    x, y = pos
        
    if not gameState.data.layout.isWall((x,y+1)):
      adjacent.append((x,y+1))
    if not gameState.data.layout.isWall((x,y-1)):
      adjacent.append((x,y-1) )
    if not gameState.data.layout.isWall((x+1,y)):
      adjacent.append((x+1,y) )
    if not gameState.data.layout.isWall((x-1,y)):
      adjacent.append((x-1,y))
    
    return adjacent
  
  def observe(self, gameState):
    noisyDistances = gameState.getAgentDistances()    
    pacmanPosition = gameState.getAgentPosition(self.index)
    
    allPossible = util.Counter()
    for enemy in self.getOpponents(gameState):
      allPossible[enemy] = util.Counter()
      
      if gameState.data.agentStates[enemy].configuration != None:
        enemyPos = gameState.data.agentStates[enemy].configuration.getPosition()
        for p in self.legalPositions:
          if p == enemyPos:
            allPossible[enemy][p] = 1.0
          else:
            allPossible[enemy][p] = 0.0              
      else:
        for p in self.legalPositions:          
          trueDistance = util.manhattanDistance(p, pacmanPosition)
          distanceProb = gameState.getDistanceProb(trueDistance, noisyDistances[enemy])          
          if distanceProb > 0: allPossible[enemy][p] =  distanceProb * self.beliefs[enemy][p]
          
        allPossible[enemy].normalize()
            
    self.beliefs = allPossible

  def elapseTime(self, gameState):    
    allPossible = util.Counter()
    
    for enemy in self.getOpponents(gameState):
                  
      allPossible[enemy] = util.Counter()
      for p in self.legalPositions:
        newPosDistance = util.Counter()        
        newPositions = self.getAdjacentPositions(gameState, p)
                
        for newPos in newPositions:
          newPosDistance[newPos] = 1.0
          
        newPosDistance.normalize()
        
        for newPos, prob in newPosDistance.items():                    
          allPossible[enemy][newPos] += prob * self.beliefs[enemy][p]
                    
      allPossible[enemy].normalize()

    self.beliefs = allPossible
          
  def registerInitialState(self, gameState):
    self.red = gameState.isOnRedTeam(self.index)
    # Even though there are up to 6 agents creating a distancer, the distances
    # will only actually be computed once, before the start of the game 
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)
    
    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()
    
    self.legalPositions = []
    walls = gameState.getWalls()    
    width = self.getLayoutWidth(gameState)    
    height = self.getLayoutHeight(gameState)
    
    for x in range(width):
      for y in range(height):
        if not walls[x][y]:
          self.legalPositions.append((x,y))
    
    self.beliefs = util.Counter()    
    #check enemy pacman only?
    for agent in self.getOpponents(gameState):
      self.beliefs[agent] = util.Counter()
      
      for p in self.legalPositions:        
        if (p[0] <= width/2 and gameState.isOnRedTeam(agent)) or (p[0] >= width/2 and not gameState.isOnRedTeam(agent)):
          self.beliefs[agent][p] = 1.0
      
      self.beliefs[agent].normalize()
        
    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display
    
    
  def getMaxLikelihoodPosition(self, agent):    
    return self.beliefs[agent].argMax()
    
  def getClosestAttackerPosition(self, observedState):
    myPos = observedState.getAgentPosition(self.index)    
    enemies = [i for i in self.getOpponents(observedState)]
    invaders = [i for i in enemies if observedState.getAgentState(i).isPacman]
    
    if len(invaders) == 0:
        invaders = enemies
    
    invaderPositions = []

    for agent in invaders:      
      invaderPositions.append(self.getMaxLikelihoodPosition(agent))

    closestInvaderPosition = min(invaderPositions, key=lambda x: self.getMazeDistance(myPos, x))

    return closestInvaderPosition
      
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    if not self.firstTurnComplete:
      self.firstTurnComplete = True
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
      
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
   
      
    posDistribution = []
    for agent in range(gameState.getNumAgents()):
      if agent in self.beliefs:
        posDistribution.append(self.beliefs[agent])
      else:
        posDistribution.append(None)
    
    self.displayDistributionsOverPositions(posDistribution)
    
    
    currentObservation = self.getCurrentObservation()
    self.observe(currentObservation)
    self.elapseTime(currentObservation)    
    
    pos = currentObservation.getAgentPosition(self.index)
    bestAction = Directions.STOP

    if gameState.getAgentState(self.index).scaredTimer > 0:
        attackerPos = self.getClosestAttackerPosition(currentObservation)      
        successors = [currentObservation.generateSuccessor(self.index, action) for action in actions]
        successorGhosts = [a for a in successors if not a.getAgentState(self.index).isPacman]

        if len(successorGhosts) != 0:
          successorGhostPositions = [successor.getAgentPosition(self.index) for successor in successorGhosts]        
          farthestSuccessorPosition = max(successorGhostPositions, key=lambda x: self.getMazeDistance(attackerPos, x))
          bestAction = actions[successorGhostPositions.index(farthestSuccessorPosition)]      
    else:
        attackerPos = self.getClosestAttackerPosition(currentObservation)      
        successors = [currentObservation.generateSuccessor(self.index, action) for action in actions]
        successorGhosts = [a for a in successors if not a.getAgentState(self.index).isPacman]

        if len(successorGhosts) != 0:
          successorGhostPositions = [successor.getAgentPosition(self.index) for successor in successorGhosts]        
          closestSuccessorPosition = min(successorGhostPositions, key=lambda x: self.getMazeDistance(attackerPos, x))
          bestAction = actions[successorGhostPositions.index(closestSuccessorPosition)]

    return bestAction     
          
  def getFeatures(self, gameState, action):
    features = self.getMutationFeatures(gameState, action)
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0
    
    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

    enemyIndices = [i for i in self.getOpponents(successor)]
    invaderIndices = [i for i in enemyIndices if successor.getAgentState(i).isPacman]   
    
    noisyInvaderDistances = [successor.getAgentDistance(i) for i in invaderIndices]
    #print "invaderDistances:", noisyInvaderDistances

    """
    allPossible = util.Counter()

    for p in self.legalPositions:
      trueDistance = self.getMazeDistance(p, myPos)
      for noisyDistance in noisyInvaderDistances:
        prob = getDistanceProb(trueDistance, noisyDistance)
        allPossible[p] += prob * self.beliefs[p]

    allPossible.normalize()
    self.beliefs = allPossible

    print "self.beliefs:", self.beliefs
    """
    
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    
    foodList = self.getFoodYouAreDefending(successor).asList()
    distance = 0
    for food in foodList:
      distance = distance + self.getMazeDistance(myPos, food)
    features['totalDistancesToFood'] = distance

    return features

  def getWeights(self, gameState, action):
    weights = regularMutation.goalieDWeightsDict
    weights['numInvaders'] = -100
    weights['onDefense'] = 100
    weights['invaderDistance'] = -1.5
    weights['totalDistancesToFood'] = -0.1
    weights['stop'] = -1
    weights['reverse'] = -1
    return weights


