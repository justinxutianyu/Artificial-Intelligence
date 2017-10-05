# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util, math
from util import nearestPoint
from game import Directions
import game
import logging

logging.basicConfig(filename='test.txt', level=logging.DEBUG)

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

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
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

class AggressiveAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. The agents will split up and target
  different halves of the map. While in ghost form, they will make
  an attempt at defense but will resume aggression as soon as possible.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute lists for food: top half, bot half
    foodList = self.getFood(successor).asList()
    walls = gameState.getWalls()
    topFoodList = [(x, y) for x, y in foodList if y > math.floor(walls.height/2)]
    botFoodList = [(x, y) for x, y in foodList if y <= math.floor(walls.height/2)]
    
    # Set distanceToFood->mindistance in features dictionary
    if self.index > 1:
      myPos = successor.getAgentState(self.index).getPosition()
      if len(topFoodList) > 0:
        minDistance = min([self.getMazeDistance(myPos, food) for food in topFoodList])
      else:
        minDistance = min([self.getMazeDistance(myPos, food) for food in botFoodList])
      features['distanceToFood'] = minDistance
    else:
      myPos = successor.getAgentState(self.index).getPosition()
      if len(botFoodList) > 0:
        minDistance = min([self.getMazeDistance(myPos, food) for food in botFoodList])
      else:
        minDistance = min([self.getMazeDistance(myPos, food) for food in topFoodList])
      features['distanceToFood'] = minDistance
    
    # Defensive when on myside in features dictionary
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    if not myState.isPacman:
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
    
    # Avoid Ghosts on enemy side
    if myState.isPacman:
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        for a in ghosts:
          dists = [self.getMazeDistance(myPos, a.getPosition())]
          if a.scaredTimer > 0:
            features['scaredGhost'] = min(dists)
          else:
            features['ghostDistance'] = min(dists)

    return features


  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'invaderDistance': -5, 'numInvaders': -1000, 'ghostDistance': 0.9, 'scaredGhost': -1.2}



class DummyAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)
