from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import distanceCalculator
import random, time, util
from game import Directions
import keyboardAgents
import game
from util import nearestPoint
import regularMutation


#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='Defender', **kwargs):
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

    return [eval(first)(firstIndex, **kwargs), eval(second)(secondIndex, **kwargs)]

##########
# Agents #
##########
class QCaptureAgent(CaptureAgent):
  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0

  """
  A base class for Q agents that chooses score-maximizing actions
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
  def getPosition(self, gameState):
    """
    Returns the position of this particular agent.
    """
    return gameState.getAgentState(self.index).getPosition()

  def getTeamPositions(self, gameState):
    """
    Returns a list of the position of all your team's agents.
    """
    return [gameState.getAgentPosition(ally) for ally in self.getTeam(gameState)]

  def getOpponentPositions(self, gameState):
    """
    Returns a list of the position of all your enemy's agents.
    NOTE: This returns None for agents at distances > 5
    """
    return [gameState.getAgentPosition(enemy) for enemy in self.getOpponents(gameState)]

  def isPacman(self, gameState):
    """
    Returns true if the agent is a Pacman.
    """
    return gameState.getAgentState(self.index).isPacman

  def getScaredTimer(self, gameState):
    """
    Returns the time left for which the Agent is scared. Note that when the
    agent is a Pacman he can still be scared, but it doesn't affect him in
    any way -- unless he comes back to ghost land without being eaten.
    """
    return gameState.getAgentState(self.index).scaredTimer

  def isPositionInTeamTerritory(self, gameState, position):
    """
    Returns true if the given position is in your team's territory.
    """
    width = self.getLayoutWidth(gameState)
    return (position[0] < width/2 and self.red) or (position[0] >= width/2 and not self.red)

  def getLayoutWidth(self, gameState):
    """
    Returns the width of the layout
    """
    return gameState.data.layout.width

  def getLayoutHeight(self, gameState):
    """
    Returns the height of the layout
    """
    return gameState.data.layout.height

  def getLayoutDimensions(self, gameState):
    """
    Returns a tuple of (width, height)
    """
    return (self.getLayoutWidth(gameState), self.getLayoutHeight(gameState))

  # Left as getFood instead of getFoodYouAreAttacking for backwards compatibility
  def getFood(self, gameState):
    """
    Returns the food you're meant to eat. This is in the form of a matrix
    where m[x][y]=true if there is food you can eat (based on your team) in that square.
    """
    if self.red:
      return gameState.getBlueFood()

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
    features['avgEnemyX'] = distances

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
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      minDiffDistance = min(
        [1000] + [self.getMazeDistance(position, food) - self.getMazeDistance(minOppPos, food) for food in foodList if
                  minOppDist < 1000])
      features['blockableFood'] = 1.0 if minDiffDistance < 1.0 else 0.0

    return features


class OffensiveQAgent(QCaptureAgent):
  """
  A Q agent that seeks food. This is an agent
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
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
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


class DefensiveQAgent(QCaptureAgent):
  """
  A Q agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

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
    features['avgEnemyX'] = distances

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
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      minDiffDistance = min(
        [1000] + [self.getMazeDistance(position, food) - self.getMazeDistance(minOppPos, food) for food in foodList if
                  minOppDist < 1000])
      features['blockableFood'] = 1.0 if minDiffDistance < 1.0 else 0.0

    return features

  def getPosition(self, gameState):
    """
    Returns the position of this particular agent.
    """
    return gameState.getAgentState(self.index).getPosition()

  def getTeamPositions(self, gameState):
    """
    Returns a list of the position of all your team's agents.
    """
    return [gameState.getAgentPosition(ally) for ally in self.getTeam(gameState)]

  def getOpponentPositions(self, gameState):
    """
    Returns a list of the position of all your enemy's agents.
    NOTE: This returns None for agents at distances > 5
    """
    return [gameState.getAgentPosition(enemy) for enemy in self.getOpponents(gameState)]

  def isPacman(self, gameState):
    """
    Returns true if the agent is a Pacman.
    """
    return gameState.getAgentState(self.index).isPacman

  def getScaredTimer(self, gameState):
    """
    Returns the time left for which the Agent is scared. Note that when the
    agent is a Pacman he can still be scared, but it doesn't affect him in
    any way -- unless he comes back to ghost land without being eaten.
    """
    return gameState.getAgentState(self.index).scaredTimer

  def isPositionInTeamTerritory(self, gameState, position):
    """
    Returns true if the given position is in your team's territory.
    """
    width = self.getLayoutWidth(gameState)
    return (position[0] < width/2 and self.red) or (position[0] >= width/2 and not self.red)

  def getLayoutWidth(self, gameState):
    """
    Returns the width of the layout
    """
    return gameState.data.layout.width

  def getLayoutHeight(self, gameState):
    """
    Returns the height of the layout
    """
    return gameState.data.layout.height

  def getLayoutDimensions(self, gameState):
    """
    Returns a tuple of (width, height)
    """
    return (self.getLayoutWidth(gameState), self.getLayoutHeight(gameState))

  # Left as getFood instead of getFoodYouAreAttacking for backwards compatibility
  def getFood(self, gameState):
    """
    Returns the food you're meant to eat. This is in the form of a matrix
    where m[x][y]=true if there is food you can eat (based on your team) in that square.
    """
    if self.red:
      return gameState.getBlueFood()


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
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
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


class MCTSOffensiveAgent(EvaluationBasedAgent):
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

class Defender(CaptureAgent):
  "Gera Monte, o agente defensivo."

  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.target = None
    self.lastObservedFood = None
    # This variable will store our patrol points and
    # the agent probability to select a point as target.
    self.patrolDict = {}

  def distFoodToPatrol(self, gameState):
    """
    This method calculates the minimum distance from our patrol
    points to our pacdots. The inverse of this distance will
    be used as the probability to select the patrol point as
    target.
    """
    food = self.getFoodYouAreDefending(gameState).asList()
    total = 0

    # Get the minimum distance from the food to our
    # patrol points.
    for position in self.noWallSpots:
      closestFoodDist = "+inf"
      for foodPos in food:
        dist = self.getMazeDistance(position, foodPos)
        if dist < closestFoodDist:
          closestFoodDist = dist
      # We can't divide by 0!
      if closestFoodDist == 0:
        closestFoodDist = 1
      self.patrolDict[position] = 1.0/float(closestFoodDist)
      total += self.patrolDict[position]
    # Normalize the value used as probability.
    if total == 0:
      total = 1
    for x in self.patrolDict.keys():
      self.patrolDict[x] = float(self.patrolDict[x])/float(total)

  def selectPatrolTarget(self):
    """
    Select some patrol point to use as target.
    """
    rand = random.random()
    sum = 0.0
    for x in self.patrolDict.keys():
      sum += self.patrolDict[x]
      if rand < sum:
        return x

  # Implemente este metodo para pre-processamento (15s max).
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.distancer.getMazeDistances()

    # Compute central positions without walls from map layout.
    # The defender will walk among these positions to defend
    # its territory.
    if self.red:
      centralX = (gameState.data.layout.width - 2)/2
    else:
      centralX = ((gameState.data.layout.width - 2)/2) + 1
    self.noWallSpots = []
    for i in range(1, gameState.data.layout.height - 1):
      if not gameState.hasWall(centralX, i):
        self.noWallSpots.append((centralX, i))
    # Remove some positions. The agent do not need to patrol
    # all positions in the central area.
    while len(self.noWallSpots) > (gameState.data.layout.height -2)/2:
      self.noWallSpots.pop(0)
      self.noWallSpots.pop(len(self.noWallSpots)-1)
    # Update probabilities to each patrol point.
    self.distFoodToPatrol(gameState)


  # Implemente este metodo para controlar o agente (1s max).
  def chooseAction(self, gameState):
    # You can profile your evaluation time by uncommenting these lines
    #start = time.time()

    # If some of our food was eaten, we need to update
    # our patrol points probabilities.
    if self.lastObservedFood and len(self.lastObservedFood) != len(self.getFoodYouAreDefending(gameState).asList()):
      self.distFoodToPatrol(gameState)

    mypos = gameState.getAgentPosition(self.index)
    if mypos == self.target:
      self.target = None

    # If we can see an invader, we go after him.
    x = self.getOpponents(gameState)
    enemies  = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = filter(lambda x: x.isPacman and x.getPosition() != None, enemies)
    if len(invaders) > 0:
      positions = [agent.getPosition() for agent in invaders]
      self.target = min(positions, key = lambda x: self.getMazeDistance(mypos, x))
    # If we can't see an invader, but our pacdots were eaten,
    # we will check the position where the pacdot disappeared.
    elif self.lastObservedFood != None:
      eaten = set(self.lastObservedFood) - set(self.getFoodYouAreDefending(gameState).asList())
      if len(eaten) > 0:
        self.target = eaten.pop()

    # Update the agent memory about our pacdots.
    self.lastObservedFood = self.getFoodYouAreDefending(gameState).asList()

    # No enemy in sight, and our pacdots are not disappearing.
    # If we have only a few pacdots, let's walk among them.
    if self.target == None and len(self.getFoodYouAreDefending(gameState).asList()) <= 4:
      food = self.getFoodYouAreDefending(gameState).asList() \
           + self.getCapsulesYouAreDefending(gameState)
      self.target = random.choice(food)
    # If we have many pacdots, let's patrol the map central area.
    elif self.target == None:
      self.target = self.selectPatrolTarget()

    # Choose action. We will take the action that brings us
    # closer to the target. However, we will never stay put
    # and we will never invade the enemy side.
    actions = gameState.getLegalActions(self.index)
    goodActions = []
    fvalues = []
    for a in actions:
      new_state = gameState.generateSuccessor(self.index, a)
      if not new_state.getAgentState(self.index).isPacman and not a == Directions.STOP:
        newpos = new_state.getAgentPosition(self.index)
        goodActions.append(a)
        fvalues.append(self.getMazeDistance(newpos, self.target))

    # Randomly chooses between ties.
    best = min(fvalues)
    ties = filter(lambda x: x[0] == best, zip(fvalues, goodActions))

    #print 'eval time for defender agent %d: %.4f' % (self.index, time.time() - start)
    return random.choice(ties)[1]

class ReflexCaptureAgent(CaptureAgent):
    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
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


class OffensiveReflexAgent(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        features['successorScore'] = self.getScore(successor)

        foodList = self.getFood(successor).asList()
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        myPos = successor.getAgentState(self.index).getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
        if len(inRange) > 0:
            positions = [agent.getPosition() for agent in inRange]
            closest = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
            closestDist = self.getMazeDistance(myPos, closest)
            if closestDist <= 5:
                features['distanceToGhost'] = closestDist

        features['isPacman'] = 1 if successor.getAgentState(self.index).isPacman else 0

        return features

    def getWeights(self, gameState, action):
        if self.inactiveTime > 80:
            return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 1000}

        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
        if len(inRange) > 0:
            positions = [agent.getPosition() for agent in inRange]
            closestPos = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
            closestDist = self.getMazeDistance(myPos, closestPos)
            closest_enemies = filter(lambda x: x[0] == closestPos, zip(positions, inRange))
            for agent in closest_enemies:
                if agent[1].scaredTimer > 0:
                    return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 0, 'isPacman': 0}

        return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 0}

    def randomSimulation(self, depth, gameState):
        new_state = gameState.deepCopy()
        while depth > 0:
            actions = new_state.getLegalActions(self.index)
            actions.remove(Directions.STOP)
            current_direction = new_state.getAgentState(self.index).configuration.direction
            reversed_direction = Directions.REVERSE[new_state.getAgentState(self.index).configuration.direction]
            if reversed_direction in actions and len(actions) > 1:
                actions.remove(reversed_direction)
            a = random.choice(actions)
            new_state = new_state.generateSuccessor(self.index, a)
            depth -= 1
        return self.evaluate(new_state, Directions.STOP)

    def takeToEmptyAlley(self, gameState, action, depth):
        if depth == 0:
            return False
        old_score = self.getScore(gameState)
        new_state = gameState.generateSuccessor(self.index, action)
        new_score = self.getScore(new_state)
        if old_score < new_score:
            return False
        actions = new_state.getLegalActions(self.index)
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
        self.numEnemyFood = "+inf"
        self.inactiveTime = 0

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.distancer.getMazeDistances()

    def chooseAction(self, gameState):
        currentEnemyFood = len(self.getFood(gameState).asList())
        if self.numEnemyFood != currentEnemyFood:
            self.numEnemyFood = currentEnemyFood
            self.inactiveTime = 0
        else:
            self.inactiveTime += 1
        if gameState.getInitialAgentPosition(self.index) == gameState.getAgentState(self.index).getPosition():
            self.inactiveTime = 0

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
            for i in range(1, 31):
                value += self.randomSimulation(10, new_state)
            fvalues.append(value)

        best = max(fvalues)
        ties = filter(lambda x: x[0] == best, zip(fvalues, actions))
        toPlay = random.choice(ties)[1]

        return toPlay