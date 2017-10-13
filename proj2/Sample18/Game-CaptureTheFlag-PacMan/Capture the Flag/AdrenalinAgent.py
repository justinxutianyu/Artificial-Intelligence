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
from test.test___future__ import features


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='AdrenalinAgent', second='AdrenalinAgent'):
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


'''
Adrenalin agent because it either goes into attacking mode
or take the defensive based on weights
'''
class AdrenalinAgent(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
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
        
        # creating sections here
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

        # if action is stop then set the feature stop               
        if action == Directions.STOP: features['stop'] = 1
        
        # checking the food and splitting the maze into two for the team 
        if len(foodList) > 0:  
            for foodX, foodY in foodList:
                #based on the horizontal distribution of food, dividing the maze for agents into two
                #and forcing them to take different route 
                if (foodY > section * walls.height / 2 and foodY < (section + 1) * walls.height / 2):
                    appendFood.append((foodX,foodY))
            if len(appendFood) == 0: 
                appendFood = foodList
            if min([self.getMazeDistance(myPos, food) for food in appendFood]) is not None:
                features['distanceToFood'] = float(min([self.getMazeDistance(myPos, food) for food in appendFood]))/(walls.width * walls.height)  
 
        # check the scared time for the ghosts and if zero attacks the invaders
        if myState.scaredTimer == 0:
            if len(invaders) > 0:
                # finds the min distance to attack the invader
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['attackPacMan'] = min(dists)
        else:
            for g in opponents:
                if g.getPosition() != None:
                    if (nextX, nextY) == g.getPosition:
                        features['attackInvader'] = -20
                    elif (nextX, nextY) in Actions.getLegalNeighbors(g.getPosition(), walls):
                        features['invaderAhead'] += -10
         
        '''
        checking if there is are chasers around
        '''        
        for ghosts in chasers:
            if isPacman and \
               ghosts.scaredTimer > 0:
                    '''
                    for pacman finds the shortest path to eat edible ghost
                    '''
                    dists = [self.getMazeDistance(myPos,a.getPosition()) for a in chasers]
                    features['eatGhosts'] = min(dists)
                    print "searching for ghosts", min(dists)
            
            elif isPacman:
                '''
                eat the pill if it is step ahead of pacman
                '''
                for powerPillX, powerPillY in gameState.getCapsules():
                    if nextX == powerPillX and nextY == powerPillY:
                        features['eatsPowerPill'] = 1
                        print "PowerPill"
                
                '''
                checks if the next position leads to ghosts position and 
                avoid them by taking the maximum distance
                '''
                
                if (nextX,nextY) in Actions.getLegalNeighbors(ghosts.getPosition(), walls) or \
                   (nextX,nextY) == ghosts.getPosition():
                    dists = [self.getMazeDistance(myPos,a.getPosition()) for a in chasers]
                    features['stepBack'] = max(dists)
                    print "Go back"
            else:
                '''
                in ghost mode always try to attack pacman if nearby by finding
                the minimum distance
                '''
                print "ghosts position", ghosts.getPosition()
                features['attackPacMan'] = min([self.getMazeDistance(myPos,a.getPosition()) for a in chasers])
        
        features.divideAll(10)       
         
        return features
        
    def getWeights(self, gameState, action):
        return {'distanceToFood':-1, 'attackPacMan':-20 , 'stop': -5, 'stepBack':-40, 'eatGhosts': -30, 
                'attackInvader': -5,'invaderAhead': 5,'eatPowerPill': -30, 'eatFood': 1}

