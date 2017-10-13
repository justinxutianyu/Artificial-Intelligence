'''
Created on Dec 11, 2013

@author: Ethan
'''
class CustomCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  
  ########################### MAP FUNCTIONS ############################
  
  def setValidPositions(self, gameState):
    """
    Sets the field: validPositions to be a list of all valid position
    tuples on the map
    """
    self.validPositions = []
    walls = gameState.getWalls()
    for x in range(walls.width):
      for y in range(walls.height):
        if not walls[x][y]:
          self.validPositions.append((x,y))
          
  def getValidNeighboringPositions(self, gameState, (x,y)):
    """
    Returns a list of valid neigboring tuple positions to the given position
    (x,y). The position (x,y) itself is returned in the list
    """
    walls = gameState.getWalls()
    positions = [(x,y)]
    if x-1 >= 0 and not walls[x-1][y]: positions.append((x-1,y))
    if y+1 < walls.height and not walls[x][y+1]: positions.append((x,y+1))
    if x+1 < walls.width and not walls[x+1][y]: positions.append((x+1,y))
    if y-1 >= 0 and not walls[x][y-1]: positions.append((x,y-1))
    
    return positions
    
  ######################## INFERENCE FUNCTIONS ########################
    
  def initializeDistribution(self, gameState, agent):
    """
    Initializes the belief distribution in the field: beliefDistributions
    that corresponds to that of the given agent.  All valid positions on
    the map are given an equal probability
    """
    self.beliefDistributions[agent] = Counter()
    walls = gameState.getWalls()
    for (x,y) in self.validPositions:
      if gameState.isOnRedTeam(agent) and x <= walls.width/2 or \
        not gameState.isOnRedTeam(agent) and x >= walls.width/2:
        self.beliefDistributions[agent][(x,y)] = 1
    self.beliefDistributions[agent].normalize()
          
  def initializeBeliefDistributions(self, gameState):
    """
    Initializes the belief distributions in the field: beliefDistributions
    for all enemy agents
    """
    self.beliefDistributions = dict()
    for agent in self.getOpponents(gameState):
      distribution = Counter()
      self.initializeDistribution(gameState, agent)
      
  def observe(self, observedState):
    """
    Inference observation function:
    Combines the existing belief distributions with the noisy distances
    measured to each enemy agent and updates the distributions accordingly
    """
    agentPosition = observedState.getAgentPosition(self.index)
    noisyDistances = observedState.getAgentDistances()
    
    newDistributions = dict()
    for agent in self.getOpponents(observedState):
      if self.beliefDistributions[agent].totalCount() == 0:
        self.initializeDistribution(observedState, agent)
      distribution = Counter()
      if observedState.data.agentStates[agent].configuration != None:
        distribution[observedState.data.agentStates[agent].configuration.getPosition()] = 1
      else:
        for pos in self.validPositions:
          distance = manhattanDistance(agentPosition, pos)
          distribution[pos] = self.beliefDistributions[agent][pos] * \
            observedState.getDistanceProb(distance, noisyDistances[agent])
        distribution.normalize()
      newDistributions[agent] = distribution
    self.beliefDistributions = newDistributions
  def getMostDangerousOpponents(self, observedState):
  
    list = []
    for opponent in self.getOpponents(observedState):
      pos = observedState.getAgentPosition(opponent)
      if pos is None: pos = self.getMostLikelyPosition(opponent)
      (x,_) = pos
      for index in range(len(list)):
        (xl,agent) = list[index]
        if (x < xl and self.red) or (x > xl and not self.red):
          list.insert(index, (x,opponent))
        elif index == len(list)-1:
          list.append((x,opponent))
      if len(list) == 0: list = [(x,opponent)]
    result = []
    for (x,opponent) in list:
      result.append(opponent)
    return result
 
  def elapseTime(self, observedState):
    """
    Inference time elapse function:
    Updates the belief distributions for all enemy agents based on their
    possible moves and the likelihood of each move
    """
    newDistributions = dict()
    for agent in self.getOpponents(observedState):
      distribution = Counter()
      for pos in self.validPositions:
        newPosDist = Counter()
        for neighboringPos in self.getValidNeighboringPositions(observedState, pos):
          newPosDist[neighboringPos] = 1
        newPosDist.normalize()
        for newPos, prob in newPosDist.items():
          distribution[newPos] += self.beliefDistributions[agent][pos] * prob
      distribution.normalize()
      newDistributions[agent] = distribution
    self.beliefDistributions = newDistributions
    
  ###################### CONVENIENCE FUNCTIONS ######################
    
  def getMostLikelyPosition(self, agent):
    """
    Returns the most likely position as a (x,y) tuple for the given agent
    """
    return self.beliefDistributions[agent].argMax()
    
  def getClosestAttacker(self, observedState):
    """
    Returns the agent number for the closest attacker (invaders i.e. pacmen)
    are searched for first, if no invaders are found, the closest defender
    (ghost) is returned
    """    
    myPos = observedState.getAgentPosition(self.index)
    closestAttacker = None
    isPacman = False
    minDistance = float('inf')

    for agent in self.getOpponents(observedState):
      attackerPos = observedState.getAgentPosition(agent)
      if attackerPos is None: attackerPos = self.getMostLikelyPosition(agent)
      attackerDist = self.getMazeDistance(myPos, attackerPos)
      if (not isPacman and (attackerDist < minDistance or \
        observedState.getAgentState(agent).isPacman)) or \
        (observedState.getAgentState(agent).isPacman and \
        attackerDist < minDistance):
        if observedState.getAgentState(agent).isPacman: isPacman = True
        minDistance = attackerDist
        closestAttacker = agent
          
    return closestAttacker
    
  def registerInitialState(self, gameState):
    """
    State initializion function that (in addition to superclass function)
    calculates valid map positions and initializes enemy belief distributions
    """
    self.red = gameState.isOnRedTeam(self.index)
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)
    self.distancer.getMazeDistances()
    
    self.setValidPositions(gameState)
    self.initializeBeliefDistributions(gameState)
 
    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display
      
  ######## THESE FUNCTIONS ARE CALLED/OVERRIDDEN BY REFLEX AGENTS #######
           
  def chooseAction(self, gameState):
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
   
    """ TEST CODE
    distributions = []
    for agent in range(gameState.getNumAgents()):
      if agent in self.beliefDistributions:
        distributions.append(self.beliefDistributions[agent])
      else:
        distributions.append(None)    
    for agent in self.getOpponents(gameState):
      print "Agent " + str(agent) + "'s most likely position is: " + str(self.getMostLikelyPosition(agent))
    self.displayDistributionsOverPositions(distributions)
    """
    
    observedState = self.getCurrentObservation()
    self.observe(observedState)
    self.elapseTime(observedState)

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
