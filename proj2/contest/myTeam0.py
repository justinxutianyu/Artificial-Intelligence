# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
#from captureAgents import AgentFactory
import random, time, util, math
from game import Directions, Actions
import game
from util import nearestPoint
import distanceCalculator
#from numpy import array, float32
#import copy
#import collections
#import tensorflow as tf
#import regularMutation

from util import Counter
from distanceCalculator import manhattanDistance

SIGHT_RANGE = 5

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
    first = 'TimidAgent', second = 'MCTSDefendAgent'):
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

class TimidAgent(CaptureAgent):
    """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.escapepath = []
        self.eaten = 0
        self.height = 0
        self.width = 0
        self.plan = [[], []]

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
        self.eaten = 0

        self.height = len(gameState.getWalls()[0])
        for w in gameState.getWalls().asList():
            if w[1] == 0:
                self.width += 1

        #print self.height
        #print self.width


        '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
    Your initialization code goes here, if you need any.
    '''

    def chooseAction(self, gameState):
        """
    Picks among actions randomly.
    """
        start = time.time()

        mypos = gameState.getAgentPosition(self.index)

        if self.getPreviousObservation() is not None:
            if self.getPreviousObservation().hasFood(mypos[0], mypos[1]):
                self.eaten += 1

        nearestFood = self.nearestFood(gameState)
        nearestEnemy = self.getNearestEnemy(gameState)

        if not gameState.getAgentState(self.index).isPacman:
            self.eaten = 0
            while len(self.plan[0]) == 0:
                y = random.choice(range(0, self.height, 1))
                if not gameState.hasWall(int(self.width / 2), y):
                    self.plan = [[int(self.width / 2) + 1, y],
                                 self.bfs(gameState, self.width, self.height, nearestEnemy,
                                          [int(self.width / 2), y])]
            if len(self.plan[1]) == 0:
                if not len(self.plan[0]) == 0:
                    self.plan[1] = self.bfs(gameState, self.width, self.height, nearestEnemy, self.plan[0])
            self.escapepath = self.plan[1]
        else:
            self.plan = [[], []]
            if len(nearestEnemy) > 0:
                if nearestEnemy[1] < 4 : #and len(self.escapepath) == 0:
                    self.escapepath = self.bfs(gameState, self.width, self.height, nearestEnemy, [self.width / 2 - 4])
                    #print "RUN!!!"
            else:
                self.escapepath = []
                if self.eaten == 5:
                    self.escapepath = self.bfs(gameState, 36, 17, nearestEnemy, [self.width / 2 - 1])

        # self.debugDraw(self.escapepath, [1.0, 1.0, 1.0], True)
        # print self.escapepath

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, nearestFood, nearestEnemy, self.escapepath, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        action = random.choice(bestActions)
        return action

    def escapePath(self, game_state, width, height, enemy):

        stack = util.Stack()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        stack.push([myPos[0], myPos[1]])
        path = []

        while not stack.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                stack.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                stack.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                stack.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                stack.push(left)
                visited.append(left)
            if left in visited: loop.append(left)

            if len(loop) > 0:
                for i in reversed(path):
                    if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                        path.remove(i)
                    else:
                        break

            if myPos[0] == 1 and myPos[1] == 2:
                # self.debugDraw(path, [1.0, 1.0, 1.0], True)
                # print path
                return path

            myPos = stack.pop()

            for i in reversed(path):
                if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                    path.remove(i)
                else:
                    break
            path.append(myPos)
        return path

    def nearestFood(self, gameState):

        food = self.getFood(gameState).asList()
        distance = [self.getMazeDistance(gameState.getAgentPosition(self.index), a) for a in food]

        if len(food) < 3:
            previous = self.getFoodYouAreDefending(gameState).asList()[0]
            return [previous, self.getMazeDistance(gameState.getAgentPosition(self.index), previous)]
        nearestFood = food[0]
        nearestDstance = distance[0]

        for i in range(len(distance)):
            if distance[i] < nearestDstance:
                nearestFood = food[i]
                nearestDstance = distance[i]

        return [nearestFood, nearestDstance]

    def getNearestEnemy(self, gameState):
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes distance to invaders we can see
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        scare = 0
        if len(invaders) == 0:
            return []
        else:
            nearestEnemy = invaders[0].getPosition()
            isPacman = invaders[0].isPacman
            nearestDstance = dists[0]
            for i in range(len(dists)):
                if dists[i] < nearestDstance:
                    nearestEnemy = invaders[i].getPosition()
                    nearestDstance = dists[i]
                    scare = invaders[i].scaredTimer
        # print scare
        # self.debugDraw(nearestEnemy, [1.0, 0.5, 0.5], True)
        return [nearestEnemy, nearestDstance, scare, isPacman]

    def evaluate(self, gameState, nearestFood, nearestEnemy, escapepath, action):

        score = 0
        scorelist = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        next = gameState.generateSuccessor(self.index, action)
        nextpos = next.getAgentPosition(self.index)
        nextscore = next.getScore()

        if nextscore > gameState.getScore():
            score += 2
            scorelist[0] = 2

        # if len(nearestEnemy) > 0 > nearestEnemy[2] and nearestEnemy[1] < 3:
        #     score -= 2 * (self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
        #     scorelist[1] -= 2 * (
        #         self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])

        # if len(nearestEnemy) == 0 or nearestEnemy[1:
        if self.getMazeDistance(next.getAgentPosition(self.index), nearestFood[0]) < nearestFood[1]:
            score += 1
            scorelist[2] = 1

        pre = self.getPreviousObservation()
        if pre != None:
            if self.getPreviousObservation().getAgentPosition(self.index) == nextpos:
                score -= 5
                scorelist[3] = -5

        if len(nearestEnemy) > 0 and nearestEnemy[1] < 4:
            if next.getAgentState(self.index).isPacman:
                score += (self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
                scorelist[4] = (
                    self.getMazeDistance(next.getAgentPosition(self.index), nearestEnemy[0]) - nearestEnemy[1])
                nextActions = next.getLegalActions(self.index)
                if len(nextActions) == 2:
                    score -= 100
                    scorelist[5] = -100
        else:
            score += 2
            scorelist[6] = 2

        if len(escapepath) > 0:
            if [nextpos[0], nextpos[1]] in escapepath:
                if not (len(nearestEnemy) > 0 > nearestEnemy[2] and nearestEnemy[1] < 3):
                    score += 10
                    scorelist[7] = 10
        if action == Directions.STOP:
            score = -10
            scorelist[8] = -10

        return score

    def dfs(self, game_state, width, height, enemy):

        stack = util.Stack()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        stack.push([myPos[0], myPos[1]])
        path = []

        while not stack.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                stack.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                stack.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                stack.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                stack.push(left)
                visited.append(left)
            if left in visited: loop.append(left)

            if len(loop) > 0:
                for i in reversed(path):
                    if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                        path.remove(i)
                    else:
                        break

            if myPos[0] == 1 and myPos[1] == 2:
                # self.debugDraw(path, [1.0, 1.0, 1.0], True)
                # print path
                return path

            myPos = stack.pop()

            for i in reversed(path):
                if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
                    path.remove(i)
                else:
                    break
            path.append(myPos)
        return path

    def bfs(self, game_state, width, height, enemy, point):

        queue = util.Queue()
        myState = game_state.getAgentState(self.index)
        myPos = myState.getPosition()

        visited = []
        if len(enemy) > 0:
            visited = [[enemy[0][0], enemy[0][1]]]
        queue.push([myPos[0], myPos[1]])

        path = []

        while not queue.isEmpty():

            myPos = [int(myPos[0]), int(myPos[1] + 0.5)]
            psize = len(visited)
            loop = []

            right = [myPos[0] - 1, myPos[1]]
            if right[0] >= 0 and right not in visited and not game_state.hasWall(right[0], right[1]):
                queue.push(right)
                visited.append(right)
            if right in visited: loop.append(right)

            up = [myPos[0], myPos[1] + 1]
            if up[1] < height and up not in visited and not game_state.hasWall(up[0], up[1]):
                queue.push(up)
                visited.append(up)
            if up in visited:  loop.append(up)

            down = [myPos[0], myPos[1] - 1]
            if down[1] >= 0 and down not in visited and not game_state.hasWall(down[0], down[1]):
                queue.push(down)
                visited.append(down)
            if down in visited: loop.append(down)

            left = [myPos[0] + 1, myPos[1]]
            if left[0] < width and left not in visited and not game_state.hasWall(left[0], left[1]):
                queue.push(left)
                visited.append(left)

            if left in visited: loop.append(left)

            # if len(loop) > 0:
            #     for i in reversed(path):
            #         if abs(i[0] - myPos[0]) + abs(i[1] - myPos[1]) > 1:
            #             path.remove(i)
            #         else:
            #             break
            myPos = queue.pop()
            path.append(myPos)

            # print path
            if len(point) == 1:
                if myPos[0] == point[0]:
                    a = myPos
                    f = []
                    for i in reversed(path):
                        if abs(a[0] - i[0]) + abs(a[1] - i[1]) <= 1:
                            f.append(i)
                            a = i
                            # self.debugDraw(f, [1.0, 1.0, 1.0], True)
                    return f
            else:

                if myPos[0] == point[0] and myPos[1] == point[1]:
                    a = myPos
                    f = []
                    for i in reversed(path):
                        if abs(a[0] - i[0]) + abs(a[1] - i[1]) <= 1:
                            f.append(i)
                            a = i
                            # self.debugDraw(f, [1.0, 1.0, 1.0], True)
                    return f

        return []

class MCTSDefendAgent(CaptureAgent):
  "Gera Monte, o agente defensivo."
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







