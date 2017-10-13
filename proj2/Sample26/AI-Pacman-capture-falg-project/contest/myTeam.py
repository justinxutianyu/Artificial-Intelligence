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


import random

import util
from captureAgents import CaptureAgent
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='AttackAgent', second='DefenceAgent'):
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

        if foodLeft <= 20:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
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

    def getMyScore(self, gameState):
        enemyFood = self.getFood(gameState)
        myFood = self.getFoodYouAreDefending(gameState)
        return len(myFood.asList()) - len(enemyFood.asList())

    def isPacman(self, gameState):
        myState = gameState.getAgentState(self.index)
        return myState.isPacman


class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

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
        actions = gameState.getLegalActions(self.index)
        '''
        You should change this in your own agent.
        '''
        return random.choice(actions)


class DefenceAgent(ReflexCaptureAgent):
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
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


class AttackAgent(ReflexCaptureAgent):
    def __init__(self, index, timeForComputing=.1):
        """
        Lists several variables you can query:
        self.index = index for this agent
        self.red = true if you're on the red team, false otherwise
        self.agentsOnTeam = a list of agent objects that make up your team
        self.distancer = distance calculator (contest code provides this)
        self.observationHistory = list of GameState objects that correspond
            to the sequential order of states that have occurred so far this game
        self.timeForComputing = an amount of time to give each turn for computing maze distances
            (part of the provided distance calculator)
        """
        # Agent index for querying state
        self.index = index

        # Whether or not you're on the red team
        self.red = None

        # Agent objects controlling you and your teammates
        self.agentsOnTeam = None

        # Maze distance calculator
        self.distancer = None

        # A history of observations
        self.observationHistory = []

        # Time to spend each turn on computing maze distances
        self.timeForComputing = timeForComputing

        # Access to the graphics
        self.display = None

        self.attackIsValid = True
        self.lastEnemyFood = 0
        self.unFormalScore = 0
        self.lastScore = -1
        self.MIN_VALID_SCORE = 4
        self.defenceMode = False

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        score = self.getMyScore(gameState)
        officialScore = self.getScore(gameState)
        if (officialScore > self.lastScore):
            self.attackIsValid = True
            self.lastScore = officialScore
            self.unFormalScore = 0
        newEnemyFood = len(self.getFood(gameState).asList())
        if (newEnemyFood < self.lastEnemyFood):
            self.unFormalScore += self.lastEnemyFood - newEnemyFood
            self.lastEnemyFood = newEnemyFood
            if (self.unFormalScore >= 1):
                self.attackIsValid = False
        elif (newEnemyFood > self.lastEnemyFood):
            self.unFormalScore = 0
            self.lastEnemyFood = newEnemyFood
            self.attackIsValid = True
        # else:
        #   print "nothing happens"
        if (self.defenceMode):
            features['onDefense'] = 1
            myState = successor.getAgentState(self.index)
            myPos = myState.getPosition()
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
        else:
            if (score <= self.MIN_VALID_SCORE and self.attackIsValid):
                foodList = self.getFood(successor).asList()
            else:
                foodList = self.getFoodYouAreDefending(successor).asList()
            features['successorScore'] = -len(foodList)  # self.getScore(successor)
            # Compute distance to the nearest food

            if len(foodList) > 0:  # This should always be True,  but better safe than sorry
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1}

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        score = self.getScore(gameState)
        if score > self.MIN_VALID_SCORE:
            if (not self.isPacman(gameState)):
                self.defenceMode = True
                for i in range(0, len(actions) - 1):
                    successor = self.getSuccessor(gameState, actions[i])
                    myState = successor.getAgentState(self.index)
                    if myState.isPacman:
                        actions.remove(actions[i])
                bestActions = [a for a, v in zip(actions, values) if v == maxValue]
                return random.choice(bestActions)
            else:
                bestDist = 9999
                for action in actions:
                    successor = self.getSuccessor(gameState, action)
                    pos2 = successor.getAgentPosition(self.index)
                    dist = self.getMazeDistance(self.start, pos2)
                    if dist < bestDist:
                        bestAction = action
                        bestDist = dist
                bestActions = [a for a, v in zip(actions, values) if v == maxValue]
                return bestAction

        self.defenceMode = False
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)
