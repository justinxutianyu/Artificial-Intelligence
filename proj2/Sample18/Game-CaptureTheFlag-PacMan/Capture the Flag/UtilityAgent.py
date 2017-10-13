# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint
from util import Counter
from distanceCalculator import manhattanDistance
#from test.test___future__ import features



#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='UtilityAgent', second='UtilityAgent'):
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

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
     
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]        
    chasers = [a for a in enemies if not (a.isPacman) and a.getPosition() != None]
    
    if len(chasers) > 0 and successor.getAgentState(self.index).isPacman:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in chasers]
      features['chaserDistance'] = min(dists)
     
     
    return features     

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood':-1}

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
    return {'numInvaders':-1000, 'onDefense': 100, 'invaderDistance':-10, 'stop':-100, 'reverse':-2}


class UtilityAgent(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        # get the sucessor for the current game state and action 
        successor = self.getSuccessor(gameState, action)

        # getting the state and the position
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
      
        # getting the coordinates 
        xPos, yPos = myState.getPosition()
        # getting relative distance
        relX, relY = Actions.directionToVector(action)
        # next move ahead
        nextX, nextY = int(xPos + relX), int(yPos + relY)
        
        '''
        dividing the maze to two portions based on agent id
        it can be one or two
        '''
        if self.index > 2:
            section = 1
        else:
            section = self.index + 1
              
        # get opponent food in the list
        food = self.getFood(gameState)
        appendFood = []
        foodList = food.asList()
        # get the walls around
        walls = gameState.getWalls()
      
        # is your agent PacMan?
        isPacman = myState.isPacman
        # gets all your opponents
        opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        # gets the opponents pacman in your zone
        invaders = [a for a in opponents if a.isPacman and a.getPosition() != None]
        # gets the ghosts your opponents zone
        chasers = [a for a in opponents if not (a.isPacman) and a.getPosition() != None]
        
        # checking the food and splitting the maze into two for the team 
        if len(foodList) > 0:  
            for foodX, foodY in foodList:
                if (foodY > section * walls.height / 2 and foodY < (section + 1) * walls.height / 2):
                    appendFood.append((foodX,foodY))
            if len(appendFood) == 0: 
                appendFood = foodList
            if min([self.getMazeDistance(myPos, food) for food in appendFood]) is not None:
                features['distanceToFood'] = float(min([self.getMazeDistance(myPos, food) for food in appendFood]))/(walls.width * walls.height)  
      
        '''
        checking the invaders length and if lenght greater than zero finds the 
        minimum distance to attack the invader
        '''
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        
        '''
        checking if there is are chasers around
        '''
        if len(chasers) > 0 and successor.getAgentState(self.index).isPacman:
            for ghosts in chasers:
                if (nextX, nextY) == ghosts.getPosition():
                    '''
                    checks if the next position leads to ghosts position and 
                    attacks the ghost if it is in edible mode
                    '''
                    if ghosts.scaredTimer > 0:
                        features['attack-ghosts'] += -10
                    #moves away from chasers
                    else:
                        features['escape'] += 1
                        features['distanceToFood'] = 0
                      
                elif (nextX, nextY) in Actions.getLegalNeighbors(ghosts.getPosition(), walls):
                    if ghosts.scaredTimer > 0:
                        features['ignore'] += 1
                    elif isPacman:
                        features['escape'] += 1
        
        # if action is stop then set the feature stop               
        if action == Directions.STOP: features['stop'] = 1
        
        return features
    
    # returns the weights with priority set
    def getWeights(self, gameState, action):
        return {'invaderDistance': -10, 'distanceToFood':-1, 'attack-ghosts' : -100, 'escape': -30, 'stop': -5}


