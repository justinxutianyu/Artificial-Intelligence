# baselineAgents.py
# -----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import capture
from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import distanceCalculator
import random, time, util
from game import Directions
import keyboardAgents
import game
from util import nearestPoint
import regularMutation
import inference
from qLearningAgents import LearningAgent
import adversarialSearch
import math
import copy

RED = 0
ORANGE = 2
YELLOW = 4
#
BLUE = 1
TEAL = 3
PURPLE = 5

#############
# FACTORIES #
#############

class TestReflexAgent(CaptureAgent):
    
  def __init__(self,index):
    CaptureAgent.__init__(self,index)
    self.firstMove = True
    self.visitedPositions = util.Counter()
    self.numEnemiesEaten = 0
    self.firstTurnComplete = False
    self.scaredEnemies = []
    
    # Create a new QLearning Agent
    self.learning = LearningAgent("testReflexAgent_" + str(self.index) + ".p")
    
    # Flag indicating if the enemy's capsule has been eaten
    self.eatenEnemyCapsule = False
    
    # Flag indicating if enemy has been scared before
    self.beenScaredBefore = False
    
    # Timers used to calculate when we are no longer scared
    self.enemyScaredTimer = 0

    self.learning.setWeights()#self.getWeights())
    self.lastFoodList = util.Counter()
    self.numDeaths = 0
      
  def getWeights(self):
      weights = util.Counter()
      weights['minFoodDist'] = 5
      weights['mazeDistToClosestEnemyOnTeamSide'] = 2
      weights['mazeDistToClosestEnemyOnEnemySide'] = -1
      weights['isNewState'] = 1
      weights['numFoodLeft']= -20
      weights['numTeamFoodLeft']= 20
      weights['numNewStatesLeft'] = -10
      weights['numEnemiesEaten'] = 10
      weights['mazeDistToClosestEnemyCapsule'] = 15
      weights['mazeDistToClosestAlly'] = -5
      return weights
  
  def chooseAction(self, gameState):
    
    # Initializing Stage
    if not self.firstTurnComplete:
      self.RED_START_POSITION = (1,1)
      self.BLUE_START_POSITION = (self.getLayoutWidth(gameState)-2,self.getLayoutHeight(gameState)-2)
      if self.isRed():
        self.teamStartPosition = self.RED_START_POSITION
        self.enemyStartPosition = self.BLUE_START_POSITION
      else:
        self.teamStartPosition = self.BLUE_START_POSITION
        self.enemyStartPosition = self.RED_START_POSITION
        
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
      self.willEatFood = False
      self.lastPosition = gameState.getAgentPosition(self.index)
      self.MAX_MAZE_DIST = float(self.getMazeDistance(self.RED_START_POSITION,self.BLUE_START_POSITION))
      self.lastClosestEnemyIndex = None
      self.numEnemyStartingFood = len(self.getFood(gameState).asList())
      self.numTeamStartingFood = len(self.getFoodYouAreDefending(gameState).asList())
      
      numWallLocations = 0
      walls = gameState.getWalls()
      for loc in walls.asList():
          if walls[int(loc[0])][int(loc[1])] == True:
              numWallLocations += 1
      self.numStartUnvisitedStates = self.BLUE_START_POSITION[0]*self.BLUE_START_POSITION[1]-numWallLocations
      
      "Each agent has a distribution module for each of its enemies"
      self.inferenceModules = []
      self.enemyBeliefs = []
      self.enemyLocations = []
      for enemy in self.getOpponents(gameState):
        inf = inference.ExactInference(self.index,enemy)
        inf.initializeUniformly(gameState)
        self.inferenceModules.append(inf)
        self.enemyBeliefs.append(inf.getBeliefDistribution())
        self.enemyLocations.append((0,0))
    
      self.lastNumCapsulesRemaining = len(self.getCapsules(gameState))
      
    "Update inference model and pick most likely location of each enemy"
    closestEnemyDist = 100000
    position = gameState.getAgentPosition(self.index)
    distr = [util.Counter(), util.Counter(), util.Counter(), util.Counter(), util.Counter(), util.Counter()]
    for index, inf in enumerate(self.inferenceModules):
      if not self.firstMove: inf.elapseTime(gameState)
      self.firstMove = False
      inf.observeState(gameState)
      "The estimated locations of each of the enemies"
      self.enemyLocations[index] = inf.getEnemyPosition()
      enemyDist = self.getMazeDistance(self.enemyLocations[index],position)
      if enemyDist < closestEnemyDist:
          closetEnemyLocation = self.enemyLocations[index]
          closestEnemyDist = enemyDist
          closestEnemyIndex = index
      distr[index] = self.inferenceModules[index].getBeliefDistribution()
    
    ''' if self.index == YELLOW:
        self.displayDistributionsOverPositions(distr)'''
        
    "Choose the best action using a minimax lookahead strategy (only if we're within SIGHT_RANGE of an enemy)"
    (a,qVal,feature) = self.selectAction(gameState)
    
    if self.firstTurnComplete:
      reward = self.getReward(gameState)
      
      "Update the scared status of the agent's team and the enemy's team"    
      self.updateEnemyIsScared(gameState)
      
      if self.getMazeDistance(position,self.teamStartPosition) < 2.0:
          if qVal != 0:
              gamma = self.lastQVal/qVal
          else:
              gamma = self.learning.gamma
      else:
          gamma = self.learning.gamma
      self.learning.update(self.lastQVal, qVal, reward, self.lastFeature,gamma)
    
    # For checking deaths, food eaten, and retroactive Qval updating
    self.lastQVal = qVal
    self.lastFeature = copy.deepcopy(feature)
    self.lastGameState = copy.deepcopy(gameState)
    self.lastClosestEnemyIndex = closestEnemyIndex
    self.lastPosition = copy.deepcopy(position)
    self.lastEnemyLocations = copy.deepcopy(self.enemyLocations)
    self.firstTurnComplete = True
    
    # Make the move that we computed to max QVal
    return a

  def selectAction(self,gameState):
    "Find the closest enemy to self"
    minVal = 100000
    minLocation = None
    position = gameState.getAgentPosition(self.index)
    index = 0
    for loc in self.enemyLocations:
        dist = self.getMazeDistance(position,loc)
        if dist < minVal:
            minVal = dist
            minLocation = loc
            enemyIndex = index
        index+=1
    
    "A depth search of DEPTH_SEARCH_LEVEL indicates that the agent will look ahead for (DEPTH_SEARCH_LEVEL+1)"
    "of its own moves intertwined with DEPTH_SEARCH_LEVEL of its nearest enemy's moves"
    "e.g. (DEPTH_SEARCH_LEVEL = 1) --> (agent moves),(enemy moves),(agent moves) resulting in"
    "                                  4^(2*DEPTH_SEARCH_LEVEL+1) moves if each level has 4 moves on average"
    DEPTH_SEARCH_LEVEL = 1
    if minVal <= DEPTH_SEARCH_LEVEL+2:
      "Only run adversarial search if we're within DEPTH_SEARCH_LEVEL+1 of an enemy"
      adversarialSearcher = adversarialSearch.AdversarialSearch(self,gameState,position,minLocation,self.index,self.isEnemyScared(enemyIndex),
                                                                self.visitedPositions,self.teamStartPosition,self.enemyStartPosition,
                                                                self.getLayoutHeight(gameState),self.getLayoutWidth(gameState))
      (qVal,a) = adversarialSearcher.startSearch(DEPTH_SEARCH_LEVEL)
      (qVal,feature) = self.evaluate(gameState,a)
      
    else:
      "Otherwise, compute the best action without lookahead"
      position = gameState.getAgentPosition(self.index)
      actions = gameState.getLegalActions(self.index)
      actions.remove(Directions.STOP)
    
      qValsAndFeatures = []
        
      for a in actions:
        qValAndFeature = self.evaluate(gameState,a)
        qValsAndFeatures.append(qValAndFeature)
    
      # This is the value of V(s) the QValue on the next step
      maxQValue = -100000
      maxFeature = None
      for qValAndFeature in qValsAndFeatures:
        if qValAndFeature[0] > maxQValue:
            maxQValue = qValAndFeature[0]
            maxFeature = qValAndFeature[1]
    
      # Select a random action out of the best actions available
      bestActions = [a for a, v in zip(actions, qValsAndFeatures) if v[0] == maxQValue]
      qVal = maxQValue
      feature = maxFeature
      a = random.choice(bestActions)
    return (a,qVal,feature)
      
  def getReward(self,gameState):
    reward = 0
    position = gameState.getAgentPosition(self.index)
    "Provide a small reward for exploring previously unseen territory"
    if position not in self.visitedPositions:
       reward += 0.5/(self.numDeaths+1)
       self.visitedPositions[position] = True 
    "Case this agent just eat some food"
    if self.hadEnemyFood(self.lastGameState,gameState):
       reward += 7.5
    "Check for kills and deaths for this agent"
    if self.lastClosestEnemyIndex != None:
        if self.getMazeDistance(gameState.getAgentPosition(self.index),self.lastPosition) > 2:
            "Case the nearest enemy is in the position where this agent just was -> this agent just got eaten"
            self.visitedPositions = util.Counter()
            self.numDeaths += 1
            reward -= 5
        elif self.lastEnemyLocations[self.lastClosestEnemyIndex] == gameState.getAgentPosition(self.index):
            "Case this agent is in the position where the nearest enemy just was -> this agent just ate its nearest enemy"
            if self.lastClosestEnemyIndex in self.scaredEnemies:
                self.scaredEnemies.remove(self.lastClosestEnemyIndex)
            self.numEnemiesEaten += 1
            reward += 5
        
    return reward
    
  def getFeatures(self, gameState, action, adversarialSearchFlag=False):
    features = util.Counter()
    if not adversarialSearchFlag:
        "Food list"
        teamFood = self.getFoodYouAreDefending(gameState)
        enemyFood = self.getFood(gameState)
        enemyCapsules = self.getCapsules(gameState)
        lastPosition = gameState.getAgentPosition(self.index)
        
        gameState = self.getSuccessor(gameState, action)
        position = self.getPosition(gameState)
        
        "First, check to see if the agent would die in this successor.  If so, this agent's successor position can be inferred as the position of the last nearest enemy"
        if self.getMazeDistance(position,lastPosition) > 2.0:
            nearestEnemyDist = 0
            if action == Directions.NORTH:
                position = (lastPosition[0],lastPosition[1]+1)
            elif action == Directions.SOUTH:
                position = (lastPosition[0],lastPosition[1]-1)
            elif action == Directions.EAST:
                position = (lastPosition[0]+1,lastPosition[1])
            elif action == Directions.WEST:
                position = (lastPosition[0]-1,lastPosition[1])
            else:
                position = lastPosition
        
        "Maze distance to closest enemy"
        nearestEnemyDist = 100000
        nearestEnemyPos = None
        sumMazeDist = 0
        index = 0
        for ep in self.enemyLocations:
            mazeDist = self.getMazeDistance(ep, position)
            sumMazeDist += mazeDist
            if mazeDist < nearestEnemyDist:
                nearestEnemyDist = mazeDist
                nearestEnemyPos = ep
                nearestEnemyIndex = index
            index+=1
        agentInTeamTerritory = self.isPositionInTeamTerritory(gameState,position)
        nearestEnemyInTeamTerritory = self.isPositionInTeamTerritory(gameState,nearestEnemyPos)
        agentDistToBorder = abs(position[0]-15.5)
        enemyDistToBorder = abs(nearestEnemyPos[0]-15.5)
        
        "Is an unvisited position"
        if position not in self.visitedPositions:
            isNewState = 0.25
            numNewStatesLeft = 1.0-float(len(self.visitedPositions)-1.0)/float(self.numStartUnvisitedStates)
        else:
            isNewState = 0
            numNewStatesLeft = 1.0-float(len(self.visitedPositions))/float(self.numStartUnvisitedStates)
        features['isNewState'] = isNewState
        features['numNewStatesLeft'] = numNewStatesLeft
        features['numEnemiesEaten'] = self.numEnemiesEaten
        
        "Distance to capsule"  
        closestCapsuleDist = 100000
        closestCapsuleLoc = None
        for capsulePos in enemyCapsules:
            dist = self.getMazeDistance(capsulePos, position)
            if dist < closestCapsuleDist:
                closestCapsuleDist = dist
                closestCapsuleLoc = capsulePos
        if len(enemyCapsules) == 0:
            "Case all enemy capsules are eaten"
            features['mazeDistToClosestEnemyCapsule'] = 0
        elif not self.isPositionInTeamTerritory(gameState, closestCapsuleLoc):
            features['mazeDistToClosestEnemyCapsule'] = 1.0-1.0/(1.0+math.exp(4.5-closestCapsuleDist))
                    
        "Maze distance to closest ally"
        minDistance = 100000
        for id,tpos in self.getIdAndPositionOfTeam(gameState):
            distance = self.getMazeDistance(position,tpos)
            if distance < minDistance and id!=self.index:
                minDistance = distance
        features['mazeDistToClosestAlly'] = 0.25*(1.0-1.0/(1.0+math.exp(4.0-minDistance)))*(1.0/(1.0+math.exp(4.0-0.5*position[0])))
        
    else:
        position = gameState.maxPosition
        agentInTeamTerritory = gameState.isMaxPositionInMaxTerritory()
        if gameState.maxAteMin == True:
            nearestEnemyPos = gameState.maxPosition
            nearestEnemyInTeamTerritory = gameState.isMaxPositionInMaxTerritory()
        else:
            nearestEnemyPos = gameState.minPosition
            nearestEnemyInTeamTerritory = not gameState.isMinPositionInMinTerritory()
        nearestEnemyIndex = None
        nearestEnemyDist = self.getMazeDistance(position,nearestEnemyPos)
        enemyFood = gameState.minFood
        teamFood = gameState.maxFood
        agentDistToBorder = abs(position[0]-15.5)
        "Is an unvisited position"
        isNewState = 0
        if position not in gameState.maxVisitedStates:
            isNewState = 0.25
            numNewStatesLeft = 1.0-float(len(gameState.maxVisitedStates)-1.0)/float(self.numStartUnvisitedStates)
        else:
            isNewState = 0
            numNewStatesLeft = 1.0-float(len(gameState.maxVisitedStates))/float(self.numStartUnvisitedStates)
        features['isNewState'] = isNewState
        features['numNewStatesLeft'] = numNewStatesLeft
        features['numEnemiesEaten'] = gameState.timesMinEaten + self.numEnemiesEaten
    
    "Border distance factors"
    growthFactorMin = 0.85
    decayFactorMax = 1.0-growthFactorMin
    growthFactor = decayFactorMax*(1.0-1.0/pow(agentDistToBorder+1.0,1.5))+growthFactorMin;
    decayFactor = 1.0-growthFactor
    
    "Enemy distance factor"
    distanceFactor = y2 = 1.0-1.0/(1.0+math.exp(7.0-2.5*nearestEnemyDist))
    
    if agentInTeamTerritory and nearestEnemyInTeamTerritory:
        if not adversarialSearchFlag:
            if not self.isTeamScared(gameState):
                "On this team's side and not scared"
                features['mazeDistToClosestEnemyOnTeamSide'] = distanceFactor*growthFactor
                features['mazeDistToClosestEnemyOnEnemySide'] = distanceFactor*decayFactor
            else:
                "On this team's side and scared"
                features['mazeDistToClosestEnemyOnTeamSide'] = -distanceFactor*growthFactor
                features['mazeDistToClosestEnemyOnEnemySide'] = distanceFactor*decayFactor
        else:
            features['mazeDistToClosestEnemyOnTeamSide'] = distanceFactor*growthFactor
            features['mazeDistToClosestEnemyOnEnemySide'] = distanceFactor*decayFactor
    elif not agentInTeamTerritory and not nearestEnemyInTeamTerritory:
        "On the enemy's side and enemy not scared"
        if not self.isEnemyScared(nearestEnemyIndex):
          features['mazeDistToClosestEnemyOnTeamSide'] = distanceFactor*decayFactor
          features['mazeDistToClosestEnemyOnEnemySide'] = distanceFactor*growthFactor
        else:
          "On the enemy's side and enemy scared"
          features['mazeDistToClosestEnemyOnTeamSide'] = distanceFactor*decayFactor
          features['mazeDistToClosestEnemyOnEnemySide'] = -distanceFactor*growthFactor
          
    else:
        "When they're on different sides"
        if agentInTeamTerritory:
            "Case this agent is on his team's side"
            features['mazeDistToClosestEnemyOnTeamSide'] = distanceFactor*decayFactor
            features['mazeDistToClosestEnemyOnEnemySide'] = distanceFactor*decayFactor
        else:
            "Case this agent is on the enemy's side"
            features['mazeDistToClosestEnemyOnTeamSide'] = 0.5*distanceFactor*decayFactor
            features['mazeDistToClosestEnemyOnEnemySide'] = 1.5*distanceFactor*decayFactor
            
    "Distance to nearest food"
    minFoodDist = 100000
    minFoodLoc = None
    if len(enemyFood.asList()) > 0: # This should always be True,  but better safe than sorry
      for food in enemyFood.asList():
          dist = self.getMazeDistance(position, food)
          if dist < minFoodDist:
              minFoodDist = dist
              minFoodLoc = food
    features['minFoodDist'] = 1.0-math.sqrt(minFoodDist/self.MAX_MAZE_DIST);
    
    "Number food left on board"
    numTeamFoodTrue = 0
    for food in teamFood.asList():
        if teamFood[int(food[0])][int(food[1])] == True:
            numTeamFoodTrue += 1
    numEnemyFoodTrue = 0
    for food in enemyFood.asList():
        if enemyFood[int(food[0])][int(food[1])] == True:
            numEnemyFoodTrue += 1
            
    features['numFoodLeft'] = float(numEnemyFoodTrue)/float(self.numEnemyStartingFood)
    features['numTeamFoodLeft'] = float(numTeamFoodTrue)/float(self.numTeamStartingFood)
    
    "Agent is in allied terrain"
    '''features['isInTeamTerrain'] = self.isPositionInTeamTerritory(successorState,successorPosition)
    '''
    
    "Sum of maze distances to all enemies"
    '''features['mazeDistToAllEnemies'] = sumMazeDist;
    
    "Distance from start of maze"
    features['distFromStart'] = self.getMazeDistance(self.BLUE_START_POSITION,successorPosition)
    
    "Is a food state"
    #features['isFood'] = self.hasEnemyFood(gameState)'''
    
    "Number of legal actions in a state"
    '''features['numLegalActions'] = len(successorState.getLegalActions(self.index))/5.0'''
 
    return features

  def evaluate(self, gameState, action, adversarialSearchFlag=False):
    """
    Computes a linear combination of features and feature weights
    """ 
    features = self.getFeatures(gameState, action, adversarialSearchFlag)
    Q = features*self.learning.getWeights()
        
    return (Q,features)

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

  def hasEnemyFood(self,gameState):
    position = gameState.getAgentPosition(self.index)
    food = self.getFood(gameState)
    return food[int(position[0])][int(position[1])]

  def hadEnemyFood(self,lastGameState,gameState):
    position = gameState.getAgentPosition(self.index)
    food = self.getFood(lastGameState)
    return food[int(position[0])][int(position[1])]
      
  def updateEnemyIsScared(self,gameState):   
    capLocations = self.getCapsules(gameState)
    "Case a capsule has been eaten since the last time this function has been called"
    if len(capLocations) < self.lastNumCapsulesRemaining:
        self.enemyScaredTimer = capture.SCARED_TIME
        self.scaredEnemies = range(1,len(self.enemyLocations))
    
    "Continually decrement the timer with every move"
    if self.enemyScaredTimer > 0:
        self.enemyScaredTimer -= 1
    
    self.lastNumCapsulesRemaining = len(capLocations)

  def isEnemyScared(self,enemyIndex):
    "If the timer hasn't expired"
    return (self.enemyScaredTimer > 0) and (enemyIndex in self.scaredEnemies)

  def isTeamScared(self,gameState):
    "If the timer hasn't expired"
    return self.getScaredTimer(gameState) > 0
    
      
  def isRed(self):
      "Case we have an even index, so we're on the blue team"
      return (self.index % 2) == 0
  
  def getIdAndPositionOfTeam(self, gameState):
    idAndPos = []
    for ally in self.getTeam(gameState):
        idAndPos.append([ally,gameState.getAgentPosition(ally)])
    return idAndPos




