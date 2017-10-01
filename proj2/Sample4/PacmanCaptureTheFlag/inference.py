# inference.py
# ------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
import random
import baselineAgents
import capture
import game
from game import Directions
from game import Actions

class ExactInference:
  
  def __init__(self,index,enemyIndex):
    self.index = index
    self.enemyIndex = enemyIndex
    self.observationDistributions = {}
    SONAR_MAX = (capture.SONAR_NOISE_RANGE - 1)/2
    SONAR_DENOMINATOR = 2 ** SONAR_MAX  + 2 ** (SONAR_MAX + 1) - 2.0
    self.SONAR_NOISE_PROBS = [2 ** (SONAR_MAX-abs(v)) / SONAR_DENOMINATOR  for v in capture.SONAR_NOISE_VALUES]

  
  def initializeUniformly(self,gameState):
    # Grab all legal positions
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
    
    "Begin with a uniform distribution over enemy positions."
    self.beliefs = util.Counter()
    for p in self.legalPositions: self.beliefs[p] = 1.0
    self.beliefs.normalize()

  def observeState(self, gameState):
    "Compute noisy distance from self to enemy of interest"
    noisyDist = gameState.getAgentDistance(self.enemyIndex)
    self.observe(noisyDist, gameState)
    
  def getObservationDistribution(self,noisyDistance):
      """
      Returns the factor P( noisyDistance | TrueDistances ), the likelihood of the provided noisyDistance
      conditioned upon all the possible true distances that could have generated it.
      """
      if noisyDistance == None:
        return util.Counter()
      if noisyDistance not in self.observationDistributions:
        distribution = util.Counter()
        for error , prob in zip(capture.SONAR_NOISE_VALUES, self.SONAR_NOISE_PROBS):
            distribution[max(1, noisyDistance - error)] += prob
        self.observationDistributions[noisyDistance] = distribution
      return self.observationDistributions[noisyDistance]
    
  def getPositionDistribution(self, gameState, enemyPosition):
    """
    Returns a distribution over successor positions of the enemy from the enemyPosition
    given the gameState.  Models RANDOM movement.
    """
    dist = util.Counter()
    "Try all possible actions"
    for action in [Directions.STOP, Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      successorPosition = game.Actions.getSuccessor(enemyPosition, action)
      "Only allow successorPosition's that put the enemy in a legal position"
      if successorPosition in self.legalPositions:
        "Uniformly distribute probability enemy will move to this successorPosition"
        dist[successorPosition] = 1.0
        
    dist.normalize() 
    return dist

  def observe(self, observation, gameState):
    """
    Updates beliefs based on the distance observation and Pacman's position.
    
    The noisyDistance is the estimated manhattan distance to the enemy you are tracking.
    
    The emissionModel below stores the probability of the noisyDistance for any true 
    distance you supply.  That is, it stores P(noisyDistance | TrueDistance).

    self.legalPositions is a list of the possible enemy positions (you
    should only consider positions that are in self.legalPositions).

    A correct implementation will handle the following special case:
    
      *  When a enemy is captured by Pacman, all beliefs should be updated so
         that the enemy appears in its prison cell, position self.getJailPosition()

         You can check if a enemy has been captured by Pacman by
         checking if it has a noisyDistance of None (a noisy distance
         of None will be returned if, and only if, the enemy is
         captured).
         
    """
    noisyDistance = observation
    emissionModel = self.getObservationDistribution(noisyDistance)
    selfPosition = gameState.getAgentPosition(self.index)
    
    "Case the enemy is near enough to myself or one of my teammates to have an accurate reading"
    enemyPos = gameState.getAgentPosition(self.enemyIndex)
    if enemyPos is not None:
      "Since we know the exact enemy position, ignore the noisyDistance reading and update self.beliefs"
      self.beliefs = util.Counter()
      self.beliefs[enemyPos] = 1
      return
    
    "Otherwise, consider the noisyDistance reading and approximate which positions fit best"
    P_N_given_L = util.Counter()
    sumBeliefs = 0
    for p in self.legalPositions:
      trueDistance = util.manhattanDistance(p, selfPosition)
      "We already know it's not possible for the enemy to be within capture.SIGHT_RANGE (otherwise we would have exactly located it)"
      if trueDistance <= capture.SIGHT_RANGE:
          pProb = 0;
      else:
          pProb = emissionModel[trueDistance]
      if pProb >= 0:
          P_N_given_L[p] = pProb

      "P(L=enemy|N=noisyDistance) = P(N=noisyDistance|L=enemy)*P(L=enemy)/P(N=noisyDistance)"
      self.beliefs[p] = self.beliefs[p] * P_N_given_L[p]
      sumBeliefs += self.beliefs[p]
      
    "Case we've lost track of the ghost and need to redistribute beliefs"
    if sumBeliefs == 0:
      self.initializeUniformly(gameState)
      
    self.beliefs.normalize()
    
  def elapseTime(self, gameState):
    """
    Update self.beliefs in response to a time step passing from the current state.
    
    The transition model is not entirely stationary: it may depend on Pacman's
    current position (e.g., for Directionalenemy).  However, this is not a problem,
    as Pacman's current position is known.

    In order to obtain the distribution over new positions for the
    enemy, given its previous position (oldPos) as well as Pacman's
    current position, use this line of code:

      newPosDist = self.getPositionDistribution(self.setenemyPosition(gameState, oldPos))

    Note that you may need to replace "oldPos" with the correct name
    of the variable that you have used to refer to the previous enemy
    position for which you are computing this distribution.

    newPosDist is a util.Counter object, where for each position p in self.legalPositions,
    
    newPostDist[p] = Pr( enemy is at position p at time t + 1 | enemy is at position oldPos at time t )

    (and also given Pacman's current position).  You may also find it useful to loop over key, value pairs
    in newPosDist, like:

      for newPos, prob in newPosDist.items():
        ...

    As an implementation detail (with which you need not concern
    yourself), the line of code above for obtaining newPosDist makes
    use of two helper methods provided in InferenceModule above:

      1) self.setEnemyPosition(gameState, enemyPosition)
          This method alters the gameState by placing the enemy we're tracking
          in a particular position.  This altered gameState can be used to query
          what the enemy would do in this position.
      
      2) self.getPositionDistribution(gameState)
          This method uses the enemy agent to determine what positions the enemy
          will move to from the provided gameState.  The enemy must be placed
          in the gameState with a call to self.setenemyPosition above.
    """

    """
    Given the newPosDist (i.e. P(pos(i,t)|pos(j,t-1)), the prior probability of
    the enemy at time t can be written as follows:

    P(pos(i,t))=sum over j(P(pos(i,t)|pos(j,t-1))*p(pos(j,t-1)))
    
    """
    newBeliefs = util.Counter()
    "Go through all legal spaces on board"
    for oldPos in self.legalPositions:
      "Get reachable successorPositions from each space and the corresponding probabilities"
      newPosDist = self.getPositionDistribution(gameState,oldPos)
      for newPos in newPosDist.keys():
        "Only consider legal positions"
        if newPos in self.legalPositions:
          newBeliefs[newPos] += self.beliefs[oldPos] * newPosDist[newPos]

    self.beliefs = newBeliefs
    self.beliefs.normalize()
    
  "Return the belief distribution"
  def getBeliefDistribution(self):
    return self.beliefs

  def getEnemyPosition(self):
    "Compute the maximum of the belief distribution as the position of the enemy"
    return max(self.beliefs, key=self.beliefs.get)
      
    
      