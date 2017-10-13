# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'SecretAgent', second = 'SecretAgent'):
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

class SecretAgent(CaptureAgent):
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

    # Store team and enemy indices
    self.teamIndices = self.getTeam(gameState)
    self.enemyIndices = self.getOpponents(gameState)

    # Store map dimensions
    self.mapWidth = gameState.data.layout.width
    self.mapHeight = gameState.data.layout.height


    # Check how recently we were near the enemy to check if we've knocked him out
    self.nearEnemyCounter = 0

    # Set up particle filters to track enemy locations
    self.enemyLocFilters = {}
    for i in self.enemyIndices:
      self.enemyLocFilters[i] = (ParticleFilter(gameState, i,
                              gameState.getInitialAgentPosition(i)))

    # Decide which Pac-man takes the bottom half
    self.isBottom = (self.index == min(self.teamIndices))

    # Divvy up food between the two Pac-men
    self.foodLists = self.distributeFood(gameState)
    self.foodList = self.foodLists['Bottom'] if self.isBottom else self.foodLists['Top']

    self.modes = ['Attack', 'Defend', 'Chase', 'Scatter', 'Reroute']
    self.seenEnemies = []

    # Set up strategy for Minimax simulations
    self.strategies = {}
    for i in range(gameState.getNumAgents()):
      if i in self.teamIndices:
        self.strategies[i] = 'Attack'
      else:
        self.strategies[i] = 'Attack'

    self.startTime = None
    self.timeLimit = 0.8
    self.currentTarget = None
    self.closestEnemy = None

    self.myPos = gameState.getAgentPosition(self.index)
    self.closestFood = self.getClosestFood(self.foodList, self.myPos)[0]

    # For rerouting
    self.lastEnemyY = 0

  def chooseAction(self, gameState):
    self.startTime = time.clock()
    self.myPos = gameState.getAgentPosition(self.index)
    self.updateParticleFilters(gameState)

    # Remove old food from personal lists
    isFoodRemoved = False
    for _, l in self.foodLists.iteritems():
      missingFood = [l1 for l1 in l if l1 not in self.getFood(gameState).asList()]
      for food in missingFood:
        l.remove(food)
        isFoodRemoved = True

    # Compute position of the nearest food
    if len(self.foodList) > 3:
      self.closestFood = self.getClosestFood(self.foodList, self.myPos)[0]
    else:
      self.closestFood = self.getClosestFood(self.getFood(gameState).asList(), self.myPos)[0]

    # Check if the enemy is observable
    self.seenEnemies = []
    for i in self.enemyIndices:
      exactPosition = gameState.getAgentPosition(i)
      if exactPosition is not None:
        self.seenEnemies.append(i)

    # Reset strategy to attack
    if gameState.getAgentState(self.index).isPacman or \
        self.myPos == gameState.getInitialAgentPosition(self.index) or (not self.seenEnemies and
        (self.strategies[self.index] == "Chase" or self.strategies[self.index] == "Scatter")):
      self.strategies[self.index] = "Attack"

    # Choose whether or not to change strategy based on seen enemies
    if self.seenEnemies:
      newStrat = None
      closestEnemyDist = None
      for e in self.seenEnemies:
        enemyPos = gameState.getAgentPosition(e)
        dist = self.distancer.getDistance(self.myPos, enemyPos)
        if not closestEnemyDist or dist < closestEnemyDist:
          self.closestEnemy = e
          closestEnemyDist = dist
      newStrat = self.evalStratChange(gameState, self.closestEnemy)
      if newStrat is not None:
        self.strategies[self.index] = newStrat


    # Get possible actions
    if isFoodRemoved or not self.seenEnemies:
      actions = self.getGoodLegalActions(gameState, self.index, True)
    else:
      actions = self.getGoodLegalActions(gameState, self.index)

    ''' debugging pellets  
    dist = util.Counter()
    l = 'Bottom' if self.isBottom else 'Top'
    for food in self.foodLists[l]: 
      dist[food] += 1
    dist.normalize()
    self.displayDistributionsOverPositions([dist])
    '''
    ''' debugging target
    dist = util.Counter()
    dist[self.currentTarget] += 1
    dist.normalize()
    self.displayDistributionsOverPositions([dist])
    '''

    # If there's only one action, just take it
    if len(actions) is 1:
      return actions[0]

    # Create simulated game state based on estimated enemy locations
    simState = gameState.deepCopy()
    for i in self.enemyIndices:
      if gameState.getAgentPosition(i) is None:
        mostLikelyPos = self.enemyLocFilters[i].getMostLikelyPos()
        conf = game.Configuration(mostLikelyPos, game.Directions.STOP)
        simState.data.agentStates[i] = game.AgentState(conf, False)

    bestAction = random.choice(actions)
    currBestAction = self.getBestAction(simState, 2, actions)
    bestAction = currBestAction
    return bestAction

  def evalStratChange(self, gameState, enemyIndex):
    selfState = gameState.getAgentState(self.index)
    enemyState = gameState.getAgentState(enemyIndex)
    distance = self.distancer.getDistance(self.myPos, 
                        gameState.getAgentPosition(enemyIndex))
    if distance < 6:
      isMuchFoodLeft = ((len(self.getFood(gameState).asList()) > 4 
                            and gameState.data.timeleft > 300) or distance < 2)
      if ((enemyState.isPacman and selfState.scaredTimer < distance / 2) 
            or (enemyState.scaredTimer > distance / 2)) and isMuchFoodLeft:
        self.currentTarget = self.getTarget(gameState, self.closestEnemy)
        return 'Chase'
      elif ((selfState.scaredTimer > distance) or selfState.isPacman) and isMuchFoodLeft:
        return 'Scatter'
      elif not selfState.isPacman and not enemyState.isPacman:
        self.currentTarget = self.getClosestDetourPoint(gameState)
        return 'Reroute'
    return None

  def distributeFood(self, gameState):
    foodLists = self.createFoodLists(gameState)
    while len(foodLists['Neither']) > 0:
      # Assign unassigned food based on proximity and amount assigned already
      bottomFoodNum = len(foodLists['Bottom'])
      topFoodNum = len(foodLists['Top'])
      if bottomFoodNum < topFoodNum:
        newFood, _ = self.getClosestFoodFromLists(foodLists['Neither'], foodLists['Bottom'])
        foodLists['Bottom'].append(newFood)
      else:
        newFood, _ = self.getClosestFoodFromLists(foodLists['Neither'], foodLists['Top'])
        foodLists['Top'].append(newFood)
      foodLists['Neither'].remove(newFood)
    foodLists['Bottom'], foodLists['Top'] = self.fixOutlierPellets(foodLists['Bottom'], 
                                                                      foodLists['Top'])
    return foodLists

  def fixOutlierPellets(self, topList, bottomList):
    # Do another pass on bordering pellets to reduce outliers
    bottomFoodNum = len(bottomList)
    topFoodNum = len(topList)
    if bottomFoodNum < topFoodNum:
      newFood, minDist = self.getClosestFoodFromLists(topList, bottomList)
      while (minDist < 2):
        bottomList.append(newFood)
        topList.remove(newFood)
        newFood, minDist = self.getClosestFoodFromLists(topList, bottomList)
    else:
      newFood, minDist = self.getClosestFoodFromLists(bottomList, topList)
      while (minDist < 2):
        topList.append(newFood)
        bottomList.remove(newFood)
        newFood, minDist = self.getClosestFoodFromLists(bottomList, topList)
    return topList, bottomList


  def createFoodLists(self, gameState):
    foodLists = {'Bottom':[], 'Top':[], 'Neither':[]}
    foodLocs = self.getFood(gameState).asList()
    for x, y in foodLocs:
      topLimit = self.mapHeight - 7
      if y < 6:
        foodLists['Bottom'].append((x,y))
      elif y > topLimit:
        foodLists['Top'].append((x,y))
      else:
        foodLists['Neither'].append((x,y))
    return foodLists

  def getClosestFoodFromLists(self, sourceList, destList):
    closestFoodDist = None
    closestFoodPos = None
    for food in destList:
      currFoodPos, currFoodDist = self.getClosestFood(sourceList, food)
      if closestFoodPos is None or currFoodDist < closestFoodDist:
        closestFoodPos = currFoodPos
        closestFoodDist = currFoodDist
    return (closestFoodPos, closestFoodDist)

  def getClosestFood(self, foodList, pos):
    closestFoodDist = None
    closestFoodPos = None
    for food in foodList:
      currFoodDist = self.distancer.getDistance(food, pos)
      if closestFoodPos is None or currFoodDist < closestFoodDist:
        closestFoodPos = food
        closestFoodDist = currFoodDist
    return (closestFoodPos, closestFoodDist)

  def getTarget(self, gameState, enemyIndex):
    enemyPos = gameState.getAgentPosition(enemyIndex)
    enemyDirection = gameState.getAgentState(enemyIndex).configuration.direction
    target = enemyPos

    if self.distancer.getDistance(self.myPos, enemyPos) > 2:
      if enemyDirection == Directions.NORTH:
        target = (enemyPos[0], enemyPos[1] + 1)
      elif enemyDirection == Directions.SOUTH:
        target = (enemyPos[0], enemyPos[1] - 1)
      elif enemyDirection == Directions.EAST:
        target = (enemyPos[0] + 1, enemyPos[1])
      elif enemyDirection == Directions.WEST:
        target = (enemyPos[0] - 1, enemyPos[1])
    else:
      if enemyPos[0] == self.myPos[0] and enemyPos[1] == self.myPos[1] + 1:
        target = (self.myPos[0], self.myPos[1] + 2)
      elif enemyPos[0] == self.myPos[0] and enemyPos[1] == self.myPos[1] + 2:
        target = (self.myPos[0], self.myPos[1] + 3)
      elif enemyPos[0] == self.myPos[0] and enemyPos[1] == self.myPos[1] - 1:
        target = (self.myPos[0], self.myPos[1] - 2)
      elif enemyPos[0] == self.myPos[0] and enemyPos[1] == self.myPos[1] - 2:
        target = (self.myPos[0], self.myPos[1] - 3)
      elif enemyPos[0] == self.myPos[0] - 1 and enemyPos[1] == self.myPos[1]:
        target = (self.myPos[0] - 2, self.myPos[1])
      elif enemyPos[0] == self.myPos[0] - 2 and enemyPos[1] == self.myPos[1]:
        target = (self.myPos[0] - 3, self.myPos[1])
      elif enemyPos[0] == self.myPos[0] + 1 and enemyPos[1] == self.myPos[1]:
        target = (self.myPos[0] + 2, self.myPos[1])
      elif enemyPos[0] == self.myPos[0] + 3 and enemyPos[1] == self.myPos[1]:
        target = (self.myPos[0] + 3, self.myPos[1])
    return target

  def getBestAction(self, gameState, depth, possibleActions):
    """
      Returns the minimax action using depth and self.evaluationFunction
    """
    if (time.clock() - self.startTime > self.timeLimit):
      print('fail0')
      return random.choice(possibleActions)

    # Run AlphaBeta for each initial action possibility to specified depth
    bestActions = []
    bestScore = None
    for action in possibleActions:
      newState = gameState.generateSuccessor(self.index, action)
      newScore = self.runAlphaBeta(newState, getNextIndex(gameState, self.index),
                    depth, float("-inf"), float("inf"))
      # If out of time, abort
      if newScore is None:
        return random.choice(possibleActions)
      if bestScore is None or newScore > bestScore:
        bestScore = newScore
        bestActions = [action]
      elif newScore == bestScore:
        bestActions.append(action)
    return random.choice(bestActions)

  # Returns score of going down a given path based on eval function
  def runAlphaBeta(self, gameState, currAgentNum, depthRemaining, alpha, beta):
    # Abort if we're running out of time
    if (time.clock() - self.startTime > self.timeLimit):
      print('fail1')
      return None

    # If the current state is terminal according to current strategy, stop evaluation
    terminalScore = self.getScoreIfTerminal(gameState)
    if terminalScore:
      return terminalScore

    # Return if at leaf node
    if depthRemaining is 0:
      return self.evaluationFunction(gameState)

    nextAgentNum = getNextIndex(gameState, currAgentNum)  # Index of agent to eval next
    nextDepthRemaining = depthRemaining        # Remaining depth at next eval
    # If done with all agents, decrease depth and go to our agent
    if nextAgentNum == self.index:
      nextAgentNum = 0
      nextDepthRemaining -= 1

    # Get list of actions, and consider more actions if it's urgent
    actions = self.getGoodLegalActions(gameState, currAgentNum)

    bestScore = None
    newAlpha = alpha
    newBeta = beta
    if currAgentNum in self.teamIndices:   # Evaluate max
      for action in actions:
        successor = gameState.generateSuccessor(currAgentNum, action)
        newScore = self.runAlphaBeta(successor, nextAgentNum,
                                     nextDepthRemaining, newAlpha, newBeta)
        # If out of time, abort
        if newScore is None:
          return None
        # If new score is the best, set best
        if bestScore is None or newScore > bestScore:
          bestScore = newScore
        # If new score is more than alpha, change alpha
        if bestScore > newAlpha:
          newAlpha = bestScore
        # Stop searching nodes if not viable
        if newBeta <= newAlpha:
          break
    else:   # Evaluate min
      newBeta = beta
      for action in actions:
        successor = gameState.generateSuccessor(currAgentNum, action)
        newScore = self.runAlphaBeta(successor, nextAgentNum, 
                                    nextDepthRemaining, newAlpha, newBeta)
        # If out of time, abort
        if newScore is None:
          return None
        # If new score is the best, set best
        if bestScore is None or newScore < bestScore:
          bestScore = newScore
        # If new score is less than beta, change beta
        if bestScore < newBeta:
          newBeta = bestScore
        # Stop searching nodes if not viable
        if newBeta <= newAlpha and nextAgentNum is 0:
          break
    return bestScore

  def evaluationFunction(self, gameState):
    """
    Computes a linear combination of features and feature weights
    """
    # Halt if out of time
    if (time.clock() - self.startTime > self.timeLimit):
      print('fail2')
      return float("-inf")

    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    return features * weights

  def getFeatures(self, gameState):
    features = util.Counter()
    myPos = gameState.getAgentPosition(self.index)
    if self.strategies[self.index] == 'Attack':
      features['score'] = self.getScore(gameState)

      # Compute distance to the nearest food
      features['foodDist'] = self.getMazeDistance(myPos, self.closestFood)

    elif self.strategies[self.index] == 'Chase':
      if 0 < self.currentTarget[0] < self.mapWidth and \
        0 < self.currentTarget[1] < self.mapHeight and not \
          gameState.hasWall(self.currentTarget[0], self.currentTarget[1]):
        features['targetDist'] = self.getMazeDistance(myPos, self.currentTarget)
      else:
        features['targetDist'] = util.manhattanDistance(myPos, self.currentTarget)

    elif self.strategies[self.index] == 'Scatter':
      # Get distance to hunter
      features['hunterDist'] = self.getMazeDistance(myPos, 
                                  gameState.getAgentPosition(self.closestEnemy))

      # Get closest power pellet
      pelletLocations = self.getCapsules(gameState)
      if pelletLocations:
        features['powerPelletDist'] = min([self.getMazeDistance(myPos, l) for l in pelletLocations])
      else:
        features['powerPelletDist'] = 0
      features['foodDist'] = self.getMazeDistance(myPos, self.closestFood)
    elif self.strategies[self.index] == 'Reroute':
      features['closestDetourDist'] = self.getMazeDistance(myPos, self.currentTarget)
    return features

  def getWeights(self, gameState):
    if self.strategies[self.index] == 'Attack':
      weights = {'score': 100, 'foodDist': -1}
    elif self.strategies[self.index] == 'Chase':
      weights = {'targetDist': -1}
    elif self.strategies[self.index] == 'Scatter':
      weights = {'hunterDist': 30, 'powerPelletDist': -10, 'foodDist': -1}
    elif self.strategies[self.index] == 'Reroute':
      weights = {'closestDetourDist': -1}
    return weights

  def getClosestDetourPoint(self, gameState):
    if gameState.isOnRedTeam(self.index):
      detourX = self.mapWidth / 2
    else:
      detourX = self.mapWidth / 2 - 1

    enemyPosition = gameState.getAgentPosition(self.closestEnemy)
    if enemyPosition is not None:
      self.lastEnemyY = enemyPosition[1]

    detourPoints = [(detourX, y) for y in range(0, self.mapHeight) 
      if not gameState.hasWall(detourX, y) and not (self.lastEnemyY - 4 < y < self.lastEnemyY + 4)]

    # Make sure the detour point is also close to food
    currFoodList = None
    if len(self.foodList) > 3:
      currFoodList = self.foodList
    else:
      currFoodList = self.getFood(gameState).asList()

    closestDetourDist = None
    closestDetourPos = None
    for detour in detourPoints:
      _, currFoodDist = self.getClosestFood(currFoodList, detour)
      totalDetourDist = currFoodDist + self.distancer.getDistance(self.myPos, detour)
      if closestDetourPos is None or totalDetourDist < closestDetourDist:
        closestDetourPos = detour
        closestDetourDist = totalDetourDist

    ''' debugging detour
    dist = util.Counter()
    dist[closestDetourPos] += 1
    dist.normalize()
    self.displayDistributionsOverPositions([dist])
    '''
    return closestDetourPos


  def getScoreIfTerminal(self, gameState):
    """
    Returns infinity if the current state is terminal for our Pac-man -- i.e. a natural endpoint
    for the current strategy, either good or bad
    """
    if self.strategies[self.index] == 'Scatter' or self.strategies[self.index] == 'Chase':
      # Was killed in action
      myPos = gameState.getAgentPosition(self.index)
      myStart = gameState.getInitialAgentPosition(self.index)
      if self.distancer.getDistance(myPos, myStart) < 4:
        return float("-inf")
      if self.strategies[self.index] == 'Scatter':
        # Is no longer prey
        selfState = gameState.getAgentState(self.index)
        enemyState = gameState.getAgentState(self.closestEnemy)
        if enemyState.scaredTimer > 0 or (enemyState.isPacman and not selfState.scaredTimer > 0):
          return float("inf")
    return None

  def updateParticleFilters(self, gameState):
    # Populate particle filters with most recent data
    actions = gameState.getLegalActions(self.index)
    for i, f in self.enemyLocFilters.iteritems():
      exactPosition = gameState.getAgentPosition(i)
      # If we can see the enemy, cluster all particles on his position
      if exactPosition is not None:
        f.clusterParticles(exactPosition)
        self.nearEnemyCounter = 2
      else: # Otherwise, run particle filtering calculations
        f.elapseTime(gameState)
        f.observe(gameState, self.myPos, 
                            self.nearEnemyCounter > 0)
        if (self.nearEnemyCounter > 0): self.nearEnemyCounter -= 1
    
    """ For debugging purposes
    self.displayDistributionsOverPositions(
        [f.getBeliefDistribution() for i, f in self.enemyLocFilters.iteritems()])
    """

  def getGoodLegalActions(self, gameState, index, shouldInclRev=False):
    """
    Same as 'getLegalActions', sans Stop (and Reverse if canReverse is False)
    """
    legalActions = gameState.getLegalActions(index)
    #closestFood = min([self.getMazeDistance(gameState.getAgentPosition(self.index), food)
    #                    for food in self.getFood(gameState).asList()])
  
    if self.strategies[index] == 'Chase' or self.strategies[index] == 'Scatter' or shouldInclRev:
      goodActions = [a for a in legalActions if a != Directions.STOP]
    else:
      rev = Directions.REVERSE[gameState.getAgentState(index).configuration.direction]
      goodActions = [a for a in legalActions if a != Directions.STOP and a != rev]
      if not goodActions:
        goodActions = [rev]
    return goodActions



###################
# Particle Filter #
###################
class ParticleFilter(object):
  """
  Based on my work for Project 4
  """
  def __init__(self, gameState, index, startPos, numParticles=100):
    "Initializes a list of particles."
    self.legalPositions = gameState.getWalls().asList(False)
    self.numParticles = numParticles
    self.particles = [startPos for _ in range(0, self.numParticles)]
    self.index = index # Index of the tracked agent

  def clusterParticles(self, position):
    "Put all particles in one place, to be used when enemy is visible"
    self.particles = [position for _ in range(0, self.numParticles)]

  def resetParticles(self):
    "Scatter the particles randomly, if our estimates are too far off"
    self.particles = [random.choice(self.legalPositions) for _ in range(0, self.numParticles)]

  def observe(self, gameState, selfPosition, shouldClusterToInit):
    "Update beliefs based on the given distance observation."
    observation = gameState.getAgentDistances()[self.index]
    particleWeights = util.Counter()
    newParticleList = []
    beliefDist = self.getBeliefDistribution()
    cumulativeProb = 0
    # Assign weights to particles depending on how likely it is for that location to be
    # correct given the most recent observation
    for particle in self.particles:
      trueDistance = util.manhattanDistance(particle, selfPosition)
      distanceProb = gameState.getDistanceProb(observation, trueDistance)

      particleWeights[particle] = (distanceProb * beliefDist[particle])
      # If the probablity of all particles is 0, we're either way off or we've knocked out the
      # enemy.  We keep track of this, and either reset or cluster to init if it is 0.
      cumulativeProb += distanceProb

    if cumulativeProb != 0:
      # Resample based on new weights
      for _ in range(self.numParticles):
        newParticleList.append(util.sample(particleWeights))
      self.particles = newParticleList
    else:
      # Reset particles if we're too far off
      if shouldClusterToInit:
        self.clusterParticles(gameState.getInitialAgentPosition(self.index))
      else:
        self.resetParticles()
    
  def elapseTime(self, gameState):
    """
    Update beliefs for a time step elapsing.
    """
    newParticleList = []
    # Pretend each particle is a ghost, and set its position semi-randomly based on how
    # likely the ghost is to move to that position
    for particle in self.particles:
      newPosDist = self.getPositionDistribution(gameState, particle)
      newParticleList.append(util.sample(newPosDist))
    self.particles = newParticleList

  def getPositionDistribution(self, gameState, position):
    """
    Returns a distribution over successor positions of the ghost from the given gameState.
    """
    dist = util.Counter()
    conf = game.Configuration(position, game.Directions.STOP)
    newState = gameState.deepCopy()
    newState.data.agentStates[self.index] = game.AgentState(conf, False)

    for action in newState.getLegalActions(self.index):
      successorPosition = game.Actions.getSuccessor(position, action)
      if (action is game.Directions.STOP or action is game):
        dist[successorPosition] += .1
      else:
        dist[successorPosition] += 1
    return dist

  def getBeliefDistribution(self):
    """
    Return the agent's current belief state, a distribution over
    ghost locations conditioned on all evidence and time passage.
    """
    # This essentially gives a point to a location for each particle there, then 
    # normalizes the point values so they add up to 1.
    dist = util.Counter()
    for part in self.particles: dist[part] += 1
    dist.normalize()
    return dist

  def getMostLikelyPos(self):
    """
    Return the ghost position considered most likely by our current model.
    """
    mostLikelyPos = None
    mostLikelyProb = None
    beliefDist = self.getBeliefDistribution()
    for part in self.particles:
      currProb = beliefDist[part]
      if mostLikelyPos is None or currProb > mostLikelyProb:
        mostLikelyPos = part 
        mostLikelyProb = currProb
    return mostLikelyPos


#####################
# Utility Functions #
#####################
def getNextIndex(gameState, currIndex):
  """
  Utility function to get the index of the next agent whose turn it is
  """
  nextIndex = currIndex + 1
  if (nextIndex >= gameState.getNumAgents()):
    nextIndex = 0
  return nextIndex


class MCTSDefendAgent(CaptureAgent):
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







