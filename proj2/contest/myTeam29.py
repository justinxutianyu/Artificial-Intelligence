
##TEAM 1
##Alexander Pinkerton, Tabitha Bleil, Caleb Burkholder



from captureAgents import CaptureAgent
import random, time, util, math
from game import Directions
from random import randint
from util import nearestPoint
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ExploitationAgent', second = 'ExploitationAgent'):
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

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)

    #initialize food tracking for our food.
    self.startFood_team = self.getFoodYouAreDefending(gameState)
    self.carriedFood_team = self.startFood_team

    #initialize food tracking for enemy food.
    self.startFood_enemy = self.getFood(gameState)
    self.carriedFood_enemy = self.startFood_enemy

    self.redMidWidth = None
    self.redMidHeight = None
    self.blueMidWidth = None
    self.blueMidHeight = None

    self.recentDeath = 0
    self.safetySwitch = 0

    self.losing = False

    self.pastObservation = gameState

    CaptureAgent.registerInitialState(self, gameState)

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

    foodLeft = len(self.getFood(gameState).asList())

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


  # ===========================================================================================
  #======================================ADVANCED FEATURES=====================================
  # ===========================================================================================

  #This feature will check if it is safe to grab food using the enemy distance and the closest food.
  def isSafe(self, gameState, myPos, foodList):
      safetyThresh = 2
      enemyDist = self.getEnemyDistances(gameState)
      closestFood = min([self.getMazeDistance(myPos, food) for food in foodList])
      if enemyDist[0] > safetyThresh * closestFood and enemyDist[1] > safetyThresh * closestFood:
          canGetFood = True
      else:
          canGetFood = False
      return canGetFood

  #This feature will tell the agents to defend the power pills on our side.
  def campCapsule(self, position, successor):
      capLocations = self.getCapsulesYouAreDefending(successor)
      capDistances = 0

      if len(capLocations) > 0:
          for cx, cy in capLocations:
              capDistances = self.getMazeDistance(position, (cx, cy))

      if len(capLocations) > 1:
          if self.index == 0 or self.index == 1:
              capDistances = self.getMazeDistance(position, capLocations[0])
          else:
              capDistances = self.getMazeDistance(position, capLocations[1])

      return capDistances

  #This feature will return the distance of the closest power pill to grab.
  def enemyCapsuleDistance(self, position, successor):
      capLocations = self.getCapsules(successor)
      enemyCapDistance = 0

      if len(capLocations) == 1:
          for cx, cy in capLocations:
              enemyCapDistance = self.getMazeDistance(position, (cx, cy))

      if len(capLocations) > 1:
        enemyCapDistance = min(self.getMazeDistance(position, capLocations[0]),self.getMazeDistance(position, capLocations[1]))

      return enemyCapDistance


  #This feature will guide our agents to defending our weakest spot.
  #Initially this will be the edge of our side but will shift to the dots furthest out
  def defendFocusArea(self, gameState, myPos):
      middleValue = 0
      if self.red:
          yourFood = self.getFoodYouAreDefending(gameState)
          yourFoodList = [(x, y) for x in range(yourFood.width) for y in range(yourFood.height) if
                          yourFood[x][y] is True]
          redFocusFood = yourFoodList[0]
          for i in range(len(yourFoodList)):
              if (yourFoodList[i])[0] > redFocusFood[0]:
                  redFocusFood = yourFoodList[i]
          if myPos[0] <= redFocusFood[0]:
              middleValue = self.getMazeDistance(myPos, redFocusFood)
          elif myPos[0] > redFocusFood[0]:
              middleValue = 300 + self.getMazeDistance(myPos, redFocusFood)
      else:
          yourFood = self.getFoodYouAreDefending(gameState)
          yourFoodList = [(x, y) for x in range(yourFood.width) for y in range(yourFood.height) if
                          yourFood[x][y] is True]
          blueFocusFood = yourFoodList[0]
          for i in range(len(yourFoodList)):
              if (yourFoodList[i])[0] < blueFocusFood[0]:
                  blueFocusFood = yourFoodList[i]
          if myPos[0] >= blueFocusFood[0]:
              middleValue = self.getMazeDistance(myPos, blueFocusFood)
          elif myPos[0] < blueFocusFood[0]:
              middleValue = 300 + self.getMazeDistance(myPos, blueFocusFood)

      return middleValue


  def enemyRecentlyDied(self, gameState, pastObservation):
        o = self.getEnemyDistances(pastObservation)
        c = self.getEnemyDistances(gameState)
        for index in range(len(o)):
            print c[index] - o[index]

  #This feature is simply the distances to the enemies
  def getEnemyDistances(self, gameState):
    myPos = gameState.getAgentPosition(self.index)
    opponents = self.getOpponents(gameState)
    enemyDist = []
    if self.red:
        for i in opponents:
            enemyPos = gameState.getAgentPosition(i)
            if enemyPos is not None:
                enemyDist.append(self.getMazeDistance(myPos,enemyPos))
            else:
                enemyDist.append(gameState.agentDistances[i])
    else:
        for i in opponents:
            enemyPos = gameState.getAgentPosition(i)
            if enemyPos is not None:
                enemyDist.append(self.getMazeDistance(myPos,enemyPos))
            else:
                enemyDist.append(gameState.agentDistances[i])
    return enemyDist

  #This feature will return true if the enemy is carrying dots
  def isEnemyCarrying(self, gameState, pastObservation):
      currentFood = self.getFoodYouAreDefending(gameState)

      #If they are killed or capture the dots, reset the food tracker
      scoreChange = gameState.data.score - pastObservation.data.score

      enemyScored = 0
      if self.red:
          if scoreChange < 0:
              print "enemy Scored"
              enemyScored = 1
      else:
          if scoreChange > 0:
              print "enemy Scored"
              enemyScored = 1

      foodDropped = sum(x.count(1) for x in currentFood.data) > sum(x.count(1) for x in self.carriedFood_team.data)
      if foodDropped:
          print "They dropped our food"

      if foodDropped or enemyScored:
        self.startFood_team = currentFood
        self.carriedFood_team = currentFood
        self.recentDeath = 1
        #print "They dropped our food"
      #If there is less defended food than the start or last reset
      if sum(x.count(1) for x in currentFood.data) < sum(x.count(1) for x in self.startFood_team.data):
        self.carriedFood_team = currentFood
        return 1
      return 0

  #This feature will return true if our team is carrying dots
  def isTeamCarrying(self, gameState, pastObservation):
      currentFood = self.getFood(gameState)

      #If they are killed or capture the dots, reset the food tracker
      scoreChange = gameState.data.score - pastObservation.data.score

      teamScored = 0
      if self.red:
          if scoreChange > 0:
              #print "we Scored"
              teamScored = 1
      else:
          if scoreChange < 0:
              #print "we Scored"
              teamScored = 1

      foodDropped = sum(x.count(1) for x in currentFood.data) > sum(x.count(1) for x in self.carriedFood_enemy.data)
      if foodDropped or teamScored:
        self.startFood_enemy = currentFood
        self.carriedFood_enemy = currentFood
        self.recentDeath = 0
        #print "We dropped their food"
      #If there is less defended food than the start or last reset
      if sum(x.count(1) for x in currentFood.data) < sum(x.count(1) for x in self.startFood_enemy.data):
        self.carriedFood_enemy = currentFood
        self.safetySwitch = 0
        return 1
      return 0

#14533 as red is super loss
#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------

class ExploitationAgent(ReflexCaptureAgent):
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

    #Set the previous gamestate variable once there has been one.
    if gameState.data.timeleft < 1196:
        self.pastObservation = self.getPreviousObservation()


    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance


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

    features['successorScore'] = -len(foodList)

    features['middleDistance'] = self.defendFocusArea(gameState, myPos)

    features['enemyDistance'] = min(self.getEnemyDistances(gameState))

    features['capsuleCamp'] = self.campCapsule(myPos, gameState)

    features['capsuleGrab'] = self.enemyCapsuleDistance(myPos,gameState)

    self.safe = self.isSafe(gameState, myPos, foodList)
    if self.safe:
        self.safetySwitch = 1

    # Calculate if either team is carrying dots.
    self.enemyCarrying = self.isEnemyCarrying(gameState, self.pastObservation)
    self.teamCarrying = self.isTeamCarrying(gameState, self.pastObservation)

    #If there is a capsule within 10 blocks and closer than an enemy, go for the power pill
    if features['capsuleGrab'] < features['enemyDistance'] and features['capsuleGrab'] < 10 and features['capsuleGrab'] != 0:
        self.grabCapsule = 1
        #print "GET DAT CAPSULE"
    else:
        self.grabCapsule = 0


    return features

  def getWeights(self, gameState, action):

      #Switch distance to food based on if they are recently dead
      if self.safetySwitch:
      #if self.recentDeath:
          campSwitch = 0
      else:
          campSwitch = 1

      #Check if we are winning or not.
      self.losing = (self.red and gameState.data.score <= 0) or (not self.red and gameState.data.score >= 0)

      #If time is almost up, we are losing, and we arent holding --> GO AFTER DOTS
      if gameState.data.timeleft < 400 and not self.teamCarrying and self.losing:
          campSwitch = 0
          #print "GET DOTS BEFORE WE LOSE"

      #Grab a dot and peace out.
      if self.teamCarrying:
          self.recentDeath = 0


      #use binary switches to turn weights on and off
      #Use the switches to switch the weights on and off the adjust offense and defensive behavior
      return {'capsuleGrab':-500 * self.grabCapsule * campSwitch,
              'successorScore':-100 * (campSwitch-1),
              'distanceToFood':1 * (campSwitch-1),
              'numInvaders': -100 * campSwitch,
              'onDefense': 100 * (self.teamCarrying+1),
              'invaderDistance': -10 * self.enemyCarrying,
              'stop': -100,
              'reverse': -2,
              'middleDistance': -0.25 * campSwitch,
              'enemyDistance': -.55,
              'capsuleCamp': -.25 * campSwitch}

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
