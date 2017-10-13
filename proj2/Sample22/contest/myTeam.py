# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from game import Actions
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    self.beliefs = {}
    self.alldir = [(-1,0),(1,0),(0,-1),(0,1)]
    self.isVisited = {} 
    self.closestDistance= util.Counter() 
    self.deadEnds = []
    self.step = 0
    self.eatenFoodAmount = 0
    self.goBack= False
    self.deadEndDepth = util.Counter()
    self.initialFood = self.getFood(gameState)
    self.findClosestExits(gameState)
    self.findDeadEnds(gameState,self.start)
    self.borderPoints = []
    if self.start[0] < gameState.data.layout.width/2:
     i = gameState.data.layout.width/2-1
     for j in range(gameState.data.layout.height):
      if gameState.hasWall(i,j) == False:
       self.borderPoints.append((i,j))
    else :
     i = gameState.data.layout.width/2
     for j in range(gameState.data.layout.height):
      if gameState.hasWall(i,j) ==False:
       self.borderPoints.append((i,j))  
    self.ateFood= False
    opponentIndexes = self.getTeam(gameState)
    # for key, value in self.deadEndDepth.items():
    #   print (key, value)
    # time.sleep(200)
    if self.index in opponentIndexes:
     opponentIndexes= self.getOpponents(gameState)
    self.opponentStart = gameState.getAgentPosition(opponentIndexes[0])
    for i in opponentIndexes:
      self.beliefs[i] = InferenceModule(self.index, i, gameState)
    CaptureAgent.registerInitialState(self, gameState)
  def findDeadEnds(self,gameState,cur):
    if cur in self.isVisited:
     return self.deadEndDepth[cur],(cur in self.deadEnds) 
    self.isVisited[cur]= True
    x,y = cur
    amount_of_deadSide =0
    depth = 0
    onlyWall= True
    for i,j in self.alldir:
      nx =i+x
      ny =j+y
      if gameState.hasWall(nx,ny):
       amount_of_deadSide+=1
      else:
       d,b = self.findDeadEnds(gameState,(nx,ny))
       if b==True:
        onlyWall=False
        amount_of_deadSide+=1
        depth = max(depth,d+1)
        
    if amount_of_deadSide==3:
     if onlyWall:
      depth+=1
     self.deadEnds.append(cur)
     self.deadEndDepth[cur] = depth
    else:
     depth = 0
    return depth,(amount_of_deadSide==3) 
     
     
  def findClosestExits(self,gameState):
   isVisited =[]
   queue = util.Queue()
   #Put the border points
   for i in range(gameState.data.layout.height):
    if self.index %2 ==0:
     j = gameState.data.layout.width/2-1
    else:
     j = gameState.data.layout.width/2
    if gameState.hasWall(j,i) ==False:
     queue.push((j,i))
   while  not queue.isEmpty():
    x,y = queue.pop()
    if (x,y) in isVisited:
     continue
    
    isVisited.append((x,y))
    val = self.closestDistance[(x,y)]
    for i,j in self.alldir:
      nx =i+x
      ny =j+y
      if (nx,ny) not in isVisited and gameState.hasWall(nx,ny) == False:
       queue.push( (nx,ny))
       self.closestDistance[(nx,ny)] = val+1
       
    
   
     
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    self.step +=1
    self.ateFood = False
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    foodLeft = len(self.getFood(gameState).asList())
    if self.index == self.getTeam(gameState)[0] :
     if foodLeft<=2:
      self.goBack=True
    for i in self.beliefs:
      self.beliefs[i].observe(gameState)

    ''' 
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction
    '''
    bestAct = random.choice(bestActions)
    if self.index == self.getTeam(gameState)[0]:
     nextState = gameState.generateSuccessor(self.index, bestAct)
     nextStatePosition = nextState.getAgentPosition(self.index)
     food = self.getFood(gameState)
     x,y = nextStatePosition
     if food[x][y]:
      self.eatenFoodAmount+=1
     if self.index%2==0:
      if x< gameState.data.layout.width/2:
       self.eatenFoodAmount=0
       self.goBack=False
     else:
      if x >=gameState.data.layout.width/2:
       self.eatenFoodAmount=0
       self.goBack=False

    return bestAct
  def dfs(self,gameState,pos):
   if pos == self.opponentStart:
    self.isOppTrapped =False
   if pos in self.isVisited:
    return
   self.isVisited.append(pos)
   x,y = pos
   for i,j in self.alldir:
    if self.newWalls[x+i][y+j] == False:
     self.dfs(gameState,(x+i,y+j))
    
  def isTrapped(self,gameState,pos,pacPos):
   self.isVisited = []
   self.newWalls = gameState.getWalls()
   self.newWalls[pos[0]][pos[1]] = True
   self.dfs(gameState,pacPos)
   b = self.isOppTrapped
   self.isOppTrapped=True
   self.newWalls[pos[0]][pos[1]]= False
   return b


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
    #time.sleep(0.05)
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
    food = self.getFood(gameState)
    foodList = self.getFood(successor).asList()    
    nextState = gameState.generateSuccessor(self.index, action)
    nextStatePosition = nextState.getAgentPosition(self.index)
    walls= gameState.getWalls()
    capsules=  gameState.getCapsules()
    x,y = gameState.getAgentState(self.index).getPosition()
    x=  int (x)
    y= int(y)
    vx,vy = Actions.directionToVector(action)
    nx = int(x+vx)
    ny = int(y+vy) 
    borderValues = util.Counter()
    currentPosition = (x, y)
      
    if self.step >270 and self.eatenFoodAmount>0:
     features['goBack'] = 1
    if self.goBack:
     features['goBack'] = 1
    if self.eatenFoodAmount >7:
     features['goBack'] =1 
    if self.closestDistance[(nx,ny)] <6 and self.eatenFoodAmount>2:
     features['goBack'] =1
    if features['goBack'] == 1:
     features['take'] = self.closestDistance[(nx,ny)] < self.closestDistance[(x,y)]
    #enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
    #invaders = [ a for a in enemies if not a.isPacman and a.getPosition() !=None]
    #defenders = [a for a in enemies if a.isPacman and a.getPosition() !=None]
    if capsules:
     for pos in capsules:
      if self.index %2==0:
       if pos[0] < gameState.data.layout.width/2:
        continue
      else:
       if pos[0] >= gameState.data.layout.width/2:
        continue
      dist = self.getMazeDistance(nextStatePosition,pos)
      #features['distCap'] = 100- dist
      if dist < 3:
       features['caps'] += 3-dist 
    # if action == Directions.STOP:
     # features['stop'] = 1
    features['eatFood'] = food[nx][ny]#self.getScore(successor)
    #mostBeliefLocation = [self.beliefs[i].belief.argMax() for i in self.beliefs if self.getAgentState[i].isPacman== False
    mostBeliefLocation = []
    for i in self.beliefs:
     if nextState.getAgentState(i).isPacman == False and nextState.getAgentState(i).scaredTimer==0 :
      mostBeliefLocation.append(self.beliefs[i].belief.argMax()) 
     
    #shortestDistanceOppo = min(mostBeliefLocation,key=lambda x:self.getMazeDistance(nextStatePosition,x))
    shortestDistanceOppo = [self.getMazeDistance(nextStatePosition,pos) for pos in mostBeliefLocation]
    if shortestDistanceOppo:
     if min(shortestDistanceOppo) <= 1:
      print 'EATEN'
      features['eaten'] = 5 - 4 * min(shortestDistanceOppo)

     if self.start[0] < gameState.data.layout.width/2:
      if x < gameState.data.layout.width/2:
       features= util.Counter()
       if nx >= gameState.data.layout.width/2 and shortestDistanceOppo[0] >8:
        features['enter'] = 1
       if shortestDistanceOppo[0] < 10:
        features['dangerousEntry'] = 10-shortestDistanceOppo[0] 
       features['entryDis'] = self.closestDistance[nextStatePosition]
       return features
     else:
      if x >= gameState.data.layout.width/2:
       features=util.Counter()
       if nx< gameState.data.layout.width/2 and shortestDistanceOppo[0] >8:
        features['enter'] = 1
       if shortestDistanceOppo[0] < 10:
        features['dangerousEntry'] = 10-shortestDistanceOppo[0]
       features['entryDis'] = self.closestDistance[nextStatePosition]
       return features
    if shortestDistanceOppo:
     features['distGhost'] = min(shortestDistanceOppo)
     if min(shortestDistanceOppo) <= (self.deadEndDepth[nextStatePosition] + 1) * 2 and nextStatePosition in self.deadEnds:
      print 'DEADEND'
      print nextStatePosition
      # time.sleep(4)
      features['deadEnd'] = 1

     # if min(shortestDistanceOppo) < 6:
     #  print 'DANGER'
      # if (self.deadEndDepth[(nx,ny)] > self.deadEndDepth[(x,y)] and self.deadEndDepth[(x,y)] !=0) or (self.deadEndDepth[(nx,ny)] ==0 and self.deadEndDepth[(x,y)] !=0):
      #  print 'SAVE'
      #  features['save'] = 1
      #  features['deadEnd'] = 0
      # if features['save'] !=1:
      #  #print 'DANGER DETECTED'
      #  features['closestGhost'] = 9-min(shortestDistanceOppo)
    # if self.eatenFoodAmount == 0 and self.closestDistance[nextStatePosition] < 10:
     #features['closestGhost'] = 0
     # g = 4  # lol
    '''
    for invader in invaders:
        pos = invader.getPosition()
        neighbors = Actions.getLegalNeighbors(pos,walls)
        if (nx,ny) == pos:
            if invader.scaredTimer == 0:
                features["eatenByGhost"] = 1 
            else:
                features["AteAGhost"] = 1
        elif  (nx,ny) in neighbors:
            if invader.scaredTimer ==0:
                features["scaredGhost"] +=1
            else:
                features["normalGhost"] +=1 
    '''
    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
     myPos = successor.getAgentState(self.index).getPosition()
     minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
     features['distanceToFood'] = minDistance
     if minDistance<4:
      features['closeFood']= 1
    return features

  def getWeights(self, gameState, action):
    return {'dangerousEntry':-1000,'entryDis':-500,'enter':1000000,'caps':3000,'eatFood': 50000, \
    'closeFood':800,'take': 1000000,'save':999999999,'distanceToFood': -300, 'eaten': -9999999999999, \
    'distCap':100, 'eatenByGhost' : -100000,'AteAGhost' : 5000, 'scaredGhost':10,'normalGhost':-10000,'deadEnd': -10000000000}

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
    nextState = gameState.generateSuccessor(self.index, action)
    nextStatePosition = nextState.getAgentPosition(self.index)
    x,y = gameState.getAgentState(self.index).getPosition()
    x=  int (x)
    y= int(y)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
        # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    #enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    #invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    #features['numInvaders'] = len(invaders)
    #for i in self.beliefs:
    #  self.beliefs[i].observe(gameState)

    #if len(invaders) > 0:
    #  dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    #  features['invaderDistance'] = min(dists)
    scaredTime = nextState.getAgentState(self.index).scaredTimer
    
    mostBeliefLocation= []
    for i in self.beliefs:
     if nextState.getAgentState(i).isPacman == True:
      mostBeliefLocation.append(self.beliefs[i].belief.argMax()) 
    #shortestDistanceOppo = min(mostBeliefLocation,key=lambda x:self.getMazeDistance(nextStatePosition,x))
    if len(mostBeliefLocation) > 0:
     b = self.isTrapped(gameState,nextStatePosition,mostBeliefLocation[0]) 
     if b==True:
      #print 'TRAP' 
      features['trap'] =1 
    shortestDistanceOppo = [self.getMazeDistance(nextStatePosition,pos) for pos in mostBeliefLocation]
    if len(shortestDistanceOppo) > 0:
     features['PacmanDist'] = min(shortestDistanceOppo)  
     if min(shortestDistanceOppo) ==0:
      #print action
      if features['trap'] != 1:
       features['capture'] = 1
    else:
     features['distToBorder'] = self.closestDistance[nextStatePosition]
     if self.closestDistance[nextStatePosition] < self.closestDistance[(x,y)]:
      features['take'] = 1
    if len(shortestDistanceOppo)> 0:
     if scaredTime > shortestDistanceOppo[0] and shortestDistanceOppo[0] < 5:
      #print 'GGGG'
      features['trap'] =0 
      features['PacmanDist'] = -1 * features['PacmanDist']
      if nextStatePosition in self.deadEnds:
       features['danger'] =1
    return features

  def getWeights(self, gameState, action):
    return {'capture':100000,'danger': -100000000,'trap':1000000000,'take':5000,'numInvaders': -1000, 'onDefense': 100,'PacmanDist':-100000,'distToBorder':-2000, 'invaderDistance': -10}
class InferenceModule:
  def __init__(self, index, opponentIndex, gameState):
    self.index = index
    self.opponentIndex= opponentIndex
    self.belief = util.Counter()
    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          self.belief[(i,j)] = 0
        else:
          self.belief[(i,j)] = 1.0
    self.belief.normalize()

  def initializeUniformaly(self, gameState):
    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          self.belief[(i,j)] = 0
        else:
          self.belief[(i,j)] = 1.0
    self.belief.normalize()

  def observe(self, gameState):
    opponentPos = gameState.getAgentPosition(self.opponentIndex)
    myPos = gameState.getAgentPosition(self.index)
    noisyDist = gameState.getAgentDistances()[self.opponentIndex]
    if opponentPos:
      for pos in self.belief:
        self.belief[pos] = 0
      self.belief[opponentPos] = 1.0
    else:
      for pos in self.belief:
        dist = util.manhattanDistance(myPos, pos)
        self.belief[pos] *= gameState.getDistanceProb(dist, noisyDist)
      
      self.belief.normalize()

    update = util.Counter()
    for pos in self.belief:
      if self.belief[pos] > 0:
        successors = []
        x,y = pos
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST, Directions.STOP]: 
          dx, dy = Actions.directionToVector(action)
          nextx, nexty = int(x + dx), int(y + dy)
          if (nextx, nexty) not in gameState.getWalls():
           successors.append((nextx,nexty))
        posProb = 1.0/len(successors)

        for poss in successors:
          update[poss] += posProb * self.belief[pos]

    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          update[(i,j)] = 0
    
    update.normalize()
    self.belief = update

    if self.belief.totalCount() <= 0:
      self.initializeUniformaly(gameState)
