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
from util import *

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent2'):
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

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """


  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    myState = successor.getAgentState(self.index)
    #print "self index ", self.index
    if self.index < 2:
      otherState = successor.getAgentState((2-self.index))
      enemyState = successor.getAgentState(1)
      enemy2State = successor.getAgentState(3)
    else:
      otherState = successor.getAgentState((4-self.index))
      enemyState = successor.getAgentState(0)
      enemy2State = successor.getAgentState(2)
    myPos = myState.getPosition()
    otherPos = otherState.getPosition()
    enemyPos = enemyState.getPosition()
    enemy2Pos = enemy2State.getPosition()
    if enemyPos is not None:
      enemyDist = abs(myPos[1] - enemyPos[1])
      features['enemyDist'] = enemyDist
    elif enemy2Pos is not None:
      enemyDist = abs(myPos[1] - enemy2Pos[1])
      features['enemyDist'] = enemyDist

    if otherPos is not None:
      otherDist = abs(myPos[1] - otherPos[1])
      features['otherDist'] = otherDist
    enemyPos = enemyState.getPosition()
    #print enemyPos 
    #HEyyooo new code here
    
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
    #Watch out!!

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    #foodLeft = len(foodList)

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
      #features['foodLeft'] = foodLeft
    return features

  def getWeights(self, gameState, action):
    #                         100                    -1
    return {'successorScore': 1000, 'distanceToFood': -20, 'invaderDistance': -10, 'otherDist': -4, 'enemyDist': -5}

class OffensiveReflexAgent2(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def capsuleLen(self):

    capsuleList = [4, 2, 5, 4] #self.getCapsules(successor)
    SaveList = len(capsuleList)
    return SaveList

  #SaveList = capsuleLen()

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    self.sizeOfCapsuleListOld = 2
    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    capsuleList = self.getCapsules(successor)
    #sizeOfCapsuleListNew = len(capsuleList)
    #sizeOfCapsuleListNew = sizeOfCapsuleListOld
    myState = successor.getAgentState(self.index)
    if self.index < 3:
      otherState = successor.getAgentState((2-self.index))
      enemyState = successor.getAgentState(1)
      enemy2State = successor.getAgentState(3)
    else:
      otherState = successor.getAgentState((4-self.index))
      enemyState = successor.getAgentState(0)
      enemy2State = successor.getAgentState(2)
    myPos = myState.getPosition()
    otherPos = otherState.getPosition()
    enemyPos = enemyState.getPosition()
    enemy2Pos = enemy2State.getPosition()
    if enemyPos is not None:
      enemyDist = abs(myPos[1] - enemyPos[1])
      features['enemyDist'] = enemyDist
    elif enemy2Pos is not None:
      enemyDist = abs(myPos[1] - enemy2Pos[1])
      features['enemyDist'] = enemyDist
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      ppDistance = 0
      if len(capsuleList) > 0:
        ppDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
      features['distanceToFood'] = minDistance
      if self.sizeOfCapsuleListOld > len(capsuleList):
          ppDistance = -100
          self.sizeOfCapsuleListOld = self.sizeOfCapsuleListOld - 1
      features['distanceToPowerPellet'] = ppDistance
    #sizeOfCapsuleListOld = len(capsuleList)
    return features

  def getWeights(self, gameState, action):
    #                         100                    -1
    return {'successorScore': 100, 'distanceToFood': -10, 'distanceToPowerPellet': -100, 'enemyDist': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
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

    return features

  def getWeights(self, gameState, action):
  #                        -1000               100                     -10          -100              -2
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
