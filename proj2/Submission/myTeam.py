# RandomTeam
# ---------------
# 2017 Semester 2 COMP90054 AI For Autonomy
# Tianyu Xu, Junwen Zhang, Ziyi Zhang
# This is the source code for second project Pacman.
#
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
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint

#################
#     Params    #
#################

default_params = {
    "particle_sum": 3000,  # used in position inference
    "max_depth": 50,  # used in expectimax agents, it can be very large, but will be limited by actionTimeLimit
    "max_position": 1,
# used in expectimax agents. How many inferenced positions for each agent are used to evaluate state/reward.
    "action_time_limit": 0.9,  # higher if you want to search deeper
    "fully_observed": False,  # not ready yet
    "consideration_distance_factor": 1.5,  # agents far than (search_distance * factor) will be considered stay still
    "expand_factor": 1.0,  # factor to balance searial and parallel work load, now 1.0 is okay
    "truncate_remain_time_percent": 0.1,  #
    "eval_total_reward": False,  # otherwise eval state. It controls whether add up values.

    "enable_stay_inference_optimization": True,  # used in position inference
    "enable_stop_action": False,  # used in many agents, whether enable STOP action.
    "enable_stop_transition": False,  # used in position inference, enable this to allow STOP transition
    "enable_print_log": True ,  # print or not
    "enable_coarse_partition": True,  # used in parallel agents, coarse partition or fine partition.

}


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='RandomOffensiveAgent',
               second='MCTSOffensiveAgent',
               particleSum=None,
               maxDepth=None,
               maxPosition=None,
               actionTimeLimit=None,
               #fullyObserved=None,
               considerationDistanceFactor=None,
               expandFactor=None,
               truncateRemainTimePercent=None,
               evalTotalReward=None,
               enableStayInferenceOptimization=None,
               enableStopAction=None,
               enableStopTransition=None,
               enablePrintLog=None,
               enableCoarsePartition=None,

               ):
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
    # initialize parameters
    if particleSum is not None: default_params["particle_sum"] = int(particleSum)
    if maxDepth is not None: default_params["max_depth"] = int(maxDepth)
    if maxPosition is not None: default_params["max_position"] = int(maxPosition)
    if actionTimeLimit is not None: default_params["action_time_limit"] = float(actionTimeLimit)
    #if fullyObserved is not None: default_params["fully_observed"] = bool(fullyObserved)
    if considerationDistanceFactor is not None: default_params["consideration_distance_factor"] = int(
        considerationDistanceFactor)
    if expandFactor is not None: default_params["expand_factor"] = float(expandFactor)
    if truncateRemainTimePercent is not None: default_params["truncate_remain_time_percent"] = float(
        truncateRemainTimePercent)
    if evalTotalReward is not None: default_params["eval_total_reward"] = bool(evalTotalReward)
    if enableStayInferenceOptimization is not None: default_params[
        "enable_stay_inference_optimization"] = enableStayInferenceOptimization.lower() == "true"
    if enableStopAction is not None: default_params["enable_stop_action"] = enableStopAction.lower() == "true"
    if enableStopTransition is not None: default_params[
        "enable_stop_transition"] = enableStopTransition.lower() == "true"
    if enablePrintLog is not None: default_params["enable_print_log"] = enablePrintLog.lower() == "true"
    if enableCoarsePartition is not None: default_params[
        "enable_coarse_partition"] = enableCoarsePartition.lower() == "true"

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


# print log information

class LogClassification:
    """A class(enum) representing log levels."""
    DETAIL = "Detail"
    INFOMATION = "Infomation"
    WARNING = "Warning"
    ERROR = "Error"


# inference agent positions using particle filtering

class PositionInferenceAgent(CaptureAgent):

    # overload functions
    #isFullyObserved = None

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.actionTimeLimit = default_params["action_time_limit"]
        #PositionInferenceAgent.isFullyObserved = default_params["fully_observed"]
        self.initPositionInference(gameState)
        self.beliefDistributions = []
        self.starting_point = gameState.getAgentPosition(self.index)

    def chooseAction(self, gameState):
        self.log("Agent %d:" % (self.index,))
        self.record = {"START": time.time()}
        #action = self.takeAction(gameState)

        # choose the best action
        self.record["BEFORE_POSITION_INFERENCE"] = time.time()
        self.updatePositionInference(gameState)
        self.checkPositionInference(gameState)
        self.updateBeliefDistribution()
        self.displayDistributionsOverPositions(self.beliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.record["AFTER_POISITION_INFERENCE"] = time.time()
        # for index in range(gameState.getNumAgents()): self.log("AGENT", index, "STATE", gameState.data.agentStates[index], "CONF", gameState.data.agentStates[index].configuration)
        bestAction = self.selectAction(gameState)

        self.record["END"] = time.time()
        self.printTimes()
        return bestAction
    """"
    def takeAction(self, gameState):
        self.time["BEFORE_POSITION_INFERENCE"] = time.time()
        self.updatePositionInference(gameState)
        self.checkPositionInference(gameState)
        self.updateBeliefDistribution()
        self.displayDistributionsOverPositions(self.bliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.time["AFTER_POISITION_INFERENCE"] = time.time()
        # for index in range(gameState.getNumAgents()): self.log("AGENT", index, "STATE", gameState.data.agentStates[index], "CONF", gameState.data.agentStates[index].configuration)
        bestAction = self.selectAction(gameState)
        return bestAction
    """

    def selectAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.starting_point, successor.getAgentPosition(self.index))
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        self.record["BEFORE_REFLEX"] = time.time()
        bestAction = self.pickAction(gameState)
        self.record["AFTER_REFLEX"] = time.time()

        return bestAction

    def pickAction(self, gameState):
        bestValue = float("-inf")
        bestAction = None
        for action in gameState.getLegalActions(self.index):
            value = self.getQValue(gameState, self.index, action)
            if value > bestValue:
                bestValue = value
                bestAction = action
        return bestAction

    def final(self, gameState):
        PositionInferenceAgent.particleSum = None
        CaptureAgent.final(self, gameState)

    def getQValue(self, gameState, agent_index, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.getFeatures(gameState, agent_index, action)
        weights  = self.getWeights(gameState, agent_index, action)

        sum = 0.0
        for feature, value in features.iteritems():
            sum += weights[feature] * value
        return sum

    def evaluate(self, gameState, actionAgentIndex, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, actionAgentIndex, action)
        weights = self.getWeights(gameState, actionAgentIndex, action)
        return features * weights
    ##############
    # interfaces #
    ##############

    def log(self, content, classification=LogClassification.INFOMATION):
        if default_params["enable_print_log"]:
            print(str(content))
        pass

    def timePast(self):
        return time.time() - self.record["START"]

    def timePastPercent(self):
        return self.timePast() / self.actionTimeLimit

    def timeRemain(self):
        return self.actionTimeLimit - self.timePast()

    def timeRemainPercent(self):
        return self.timeRemain() / self.actionTimeLimit

    def printTimes(self):
        timeList = list(self.record.items())
        timeList.sort(key=lambda x: x[1])
        relativeTimeList = []
        startTime = self.record["START"]
        totalTime = timeList[len(timeList) - 1][1] - startTime
        reachActionTimeLimit = totalTime >= self.actionTimeLimit
        for i in range(1, len(timeList)):
            j = i - 1
            k, v = timeList[i]
            _, lastV = timeList[j]
            records = v - lastV
            if records >= 0.0001:
                relativeTimeList.append("%s:%.4f" % (k, records))
        prefix = "O " if not reachActionTimeLimit else "X "
        prefix += "Total %.4f " % (totalTime,)
        self.log(prefix + str(relativeTimeList))

    def getFeatures(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    def getWeights(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    def getSuccessor(self, gameState, actionAgentIndex, action):
        """Finds the next successor which is a grid position (location tuple)."""
        successor = gameState.generateSuccessor(actionAgentIndex, action)
        pos = successor.getAgentState(actionAgentIndex).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(actionAgentIndex, action)
        else:
            return successor

    def getCurrentAgentPositionsAndPosibilities(self, agentIndex):
        '''get inference positions and posibilities'''
        gameState = self.getCurrentObservation()
        if agentIndex in self.getTeam(gameState):
            result = [(gameState.getAgentPosition(agentIndex), 1.0)]
        else:
            result = self.beliefDistributions[agentIndex].items()
            result.sort(key=lambda x: x[1], reverse=True)
        return result

    def getCurrentAgentPostions(self, agentIndex):
        '''get inference positions'''
        result = self.getCurrentAgentPositionsAndPosibilities(agentIndex)
        result = [i[0] for i in result]
        return result

    def getCurrentMostLikelyPosition(self, agentIndex):
        return self.getCurrentAgentPostions(agentIndex)[0]

    #############
    # inference #
    #############

    width = None
    height = None
    particleSum = None
    particleDicts = None
    walls = None

    def initPositionInference(self, gameState):
        if PositionInferenceAgent.particleSum is None:
            PositionInferenceAgent.width = gameState.data.layout.width
            PositionInferenceAgent.height = gameState.data.layout.height
            PositionInferenceAgent.particleSum = default_params["particle_sum"]
            PositionInferenceAgent.particleDicts = [None for _ in range(gameState.getNumAgents())]
            PositionInferenceAgent.walls = gameState.getWalls()

            for agentIndex in self.getOpponents(gameState):
                self.initParticleDict(agentIndex)

    def updatePositionInference(self, gameState):
        def update(particleDict, sonarDistance, isStay):
            if isStay and default_params["enable_stay_inference_optimization"]:
                transferedParticleDict = particleDict
            else:
                transferedParticleDict = util.Counter()
                for tile, sum in particleDict.items():
                    x, y = tile
                    available = [tile] if default_params["enable_stop_transition"] else []
                    if not PositionInferenceAgent.walls[x][y + 1]: available.append((x, y + 1))
                    if not PositionInferenceAgent.walls[x][y - 1]: available.append((x, y - 1))
                    if not PositionInferenceAgent.walls[x - 1][y]: available.append((x - 1, y))
                    if not PositionInferenceAgent.walls[x + 1][y]: available.append((x + 1, y))
                    # assume equal trans prob
                    for newTile in available:
                        transferedParticleDict[newTile] += sum / len(available)
                    remainSum = sum % len(available)
                    for _ in range(remainSum):
                        newTile = random.choice(available)
                        transferedParticleDict[newTile] += 1
            agentX, agentY = agentPosition
            candidateParticleDict = util.Counter()
            for tile, sum in transferedParticleDict.items():
                x, y = tile
                distance = abs(agentX - x) + abs(agentY - y)
                newProbability = gameState.getDistanceProb(distance, sonarDistance) * sum
                if newProbability > 0:
                    candidateParticleDict[tile] += newProbability
            if len(candidateParticleDict) > 0:
                newPariticleDict = util.Counter()
                for _ in range(PositionInferenceAgent.particleSum):
                    tile = self.weightedRandomChoice(candidateParticleDict)
                    newPariticleDict[tile] += 1
                return newPariticleDict
            else:
                self.log("Lost target", classification=LogClassification.WARNING)
                return self.getFullParticleDict()

        agentPosition = gameState.getAgentPosition(self.index)

        for agentIndex in range(gameState.getNumAgents()):
            if agentIndex in self.getOpponents(gameState):
                particleDict = PositionInferenceAgent.particleDicts[agentIndex]
                sonarDistance = gameState.agentDistances[agentIndex]
                isStay = not (agentIndex == self.index - 1 or agentIndex == self.index + gameState.getNumAgents() - 1)
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))
                PositionInferenceAgent.particleDicts[agentIndex] = update(particleDict, sonarDistance, isStay)

    def checkPositionInference(self, gameState):
        for agentIndex in range(gameState.getNumAgents()):
            if agentIndex in self.getOpponents(gameState):  # postion of teammates are always available
                # when eat pacman (not for sure)
                def eatPacmanJudge():
                    previous = self.getPreviousObservation()
                    if previous is not None:
                        previousOppoPos = previous.getAgentPosition(agentIndex)
                        if previousOppoPos is not None:
                            if previousOppoPos == gameState.getAgentPosition(self.index):
                                return True
                    return False

                if eatPacmanJudge():
                    self.initParticleDict(agentIndex)

                # when observed
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None:
                    PositionInferenceAgent.particleDicts[agentIndex] = util.Counter()
                    PositionInferenceAgent.particleDicts[agentIndex][agentPosition] = PositionInferenceAgent.particleSum

    def updateBeliefDistribution(self):
        self.beliefDistributions = [dict.copy() if dict is not None else None for dict in
                                   PositionInferenceAgent.particleDicts]
        for dict in self.beliefDistributions: dict.normalize() if dict is not None else None

    #########
    # utils #
    #########

    def getFullParticleDict(self):
        result = util.Counter()
        xStart = 1
        xEnd = PositionInferenceAgent.width - 1
        yStart = 1
        yEnd = PositionInferenceAgent.height - 1
        total = 0
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    total += 1
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    result[(x, y)] = PositionInferenceAgent.particleSum / total
        return result

    def initParticleDict(self, opponentAgentIndex):
        if self.red:
            xStart = PositionInferenceAgent.width - 2
            xEnd = PositionInferenceAgent.width - 1
            yStart = PositionInferenceAgent.height / 2
            yEnd = PositionInferenceAgent.height - 1
        else:
            xStart = 1
            xEnd = 2
            yStart = 1
            yEnd = PositionInferenceAgent.height / 2
        total = 0
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    total += 1
        PositionInferenceAgent.particleDicts[opponentAgentIndex] = util.Counter()
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    PositionInferenceAgent.particleDicts[opponentAgentIndex][
                        (x, y)] = PositionInferenceAgent.particleSum / total

    def weightedRandomChoice(self, weightDict):
        weights = []
        elems = []
        for elem in weightDict:
            weights.append(weightDict[elem])
            elems.append(elem)
        total = sum(weights)
        key = random.uniform(0, total)
        runningTotal = 0.0
        chosenIndex = None
        for i in range(len(weights)):
            weight = weights[i]
            runningTotal += weight
            if runningTotal >= key:
                chosenIndex = i
                return elems[chosenIndex]
        raise Exception('Should not reach here')



class ReflexAgent(PositionInferenceAgent):
    """A virtual agent class. Basiclly same with ReflexAgent in baselineTeam.py, but inherited from PositionInferenceAgent."""

    ######################
    # overload functions #
    ######################

    def registerInitialState(self, gameState):
        PositionInferenceAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)

    def selectAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(gameState.getAgentPosition(self.index), successor.getAgentPosition(self.index))
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        self.record["BEFORE_REFLEX"] = time.time()
        bestAction = self.pickAction(gameState)
        self.record["AFTER_REFLEX"] = time.time()

        return bestAction

    #####################
    # virtual functions #
    #####################

    def getFeatures(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    def getWeights(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    ######################
    # linear combination #
    ######################

    def pickAction(self, gameState):
        bestValue = float("-inf")
        bestAction = None
        for action in gameState.getLegalActions(self.index):
            value = self.getQValue(gameState, self.index, action)
            if value > bestValue:
                bestValue = value
                bestAction = action
        return bestAction

    #########
    # utils #
    #########

    def evaluate(self, gameState, actionAgentIndex, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, actionAgentIndex, action)
        weights = self.getWeights(gameState, actionAgentIndex, action)
        return features * weights


class TimeoutException(Exception):
    """A custom exception for truncating search."""
    pass


class ExpectimaxAgent(CaptureAgent):
    """A virtual agent class. It uses depth first search to find the best action. It can stop before time limit."""

    ######################
    # overload functions #
    ######################

    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """
    def registerInitialState(self, gameState):
        #PositionInferenceAgent.registerInitialState(self, gameState)
        CaptureAgent.registerInitialState(self, gameState)
        self.actionTimeLimit = default_params["action_time_limit"]
        #PositionInferenceAgent.isFullyObserved = default_params["fully_observed"]
        self.initPositionInference(gameState)
        self.beliefDistributions = []
        #self.starting_point = gameState.getAgentPosition(self.index)

        self.starting_point = gameState.getAgentPosition(self.index)
        self.maxDepth = default_params["max_depth"]
        self.maxInferencePositionCount = default_params["max_position"]

    def pickAction(self, gameState):
        self.record["BEFORE_SEARCH"] = time.time()
        _, bestAction = self.searchTop(gameState)
        self.record["AFTER_SEARCH"] = time.time()
        return bestAction

    def chooseAction(self, gameState):
        self.log("Agent %d:" % (self.index,))
        self.record = {"START": time.time()}
        #action = self.takeAction(gameState)

        # choose the best action
        self.record["BEFORE_POSITION_INFERENCE"] = time.time()
        self.updatePositionInference(gameState)
        self.checkPositionInference(gameState)
        self.updateBeliefDistribution()
        self.displayDistributionsOverPositions(self.beliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.record["AFTER_POISITION_INFERENCE"] = time.time()
        # for index in range(gameState.getNumAgents()): self.log("AGENT", index, "STATE", gameState.data.agentStates[index], "CONF", gameState.data.agentStates[index].configuration)
        bestAction = self.selectAction(gameState)

        self.record["END"] = time.time()
        self.printTimes()
        return bestAction

    def selectAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.starting_point, successor.getAgentPosition(self.index))
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        self.record["BEFORE_REFLEX"] = time.time()
        bestAction = self.pickAction(gameState)
        self.record["AFTER_REFLEX"] = time.time()

        return bestAction

    def final(self, gameState):
        ExpectimaxAgent.particleSum = None
        CaptureAgent.final(self, gameState)

    def getQValue(self, gameState, agent_index, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.getFeatures(gameState, agent_index, action)
        weights  = self.getWeights(gameState, agent_index, action)

        sum = 0.0
        for feature, value in features.iteritems():
            sum += weights[feature] * value
        return sum

    ##########
    # search #
    ##########

    def getCurrentReward(self, gameState, agentIndex, action):
        if default_params["eval_total_reward"]:
            return self.getQValue(gameState, agentIndex, action)
        else:
            return 0

    def searchWhenGameOver(self, gameState):
        return self.getQValue(gameState, self.index, Directions.STOP), Directions.STOP

    def searchWhenZeroDepth(self, gameState, agentIndex):
        isTeam = agentIndex in self.getTeam(gameState)
        bestValue = float("-inf") if isTeam else float("inf")
        bestAction = None
        assert agentIndex == self.index
        legalActions = gameState.getLegalActions(agentIndex)
        legalActions.remove(
            Directions.STOP)  # STOP is not allowed, to avoid the problem of discontinuous evaluation function
        for action in legalActions:
            value = self.getQValue(gameState, agentIndex, action)
            if (isTeam and value > bestValue) or (not isTeam and value < bestValue):
                bestValue = value
                bestAction = action
        return bestValue, bestAction

    def searchWhenNonTerminated(self, gameState, agentIndex, searchAgentIndices, depth, alpha=float("-inf"),
                                beta=float("inf")):
        nextAgentIndex, nextDepth = self.getNextSearchableAgentIndexAndDepth(gameState, searchAgentIndices, agentIndex,
                                                                             depth)
        bestAction = None
        # if agentIndex in self.getTeam(gameState):  # team work
        if agentIndex == self.index:  # no team work, is better
            bestValue = float("-inf")
            legalActions = gameState.getLegalActions(agentIndex)
            if not default_params["enable_stop_action"]:
                legalActions.remove(Directions.STOP)  # STOP is not allowed
            for action in legalActions:
                successorState = gameState.generateSuccessor(agentIndex, action)
                newAlpha, _ = self.searchRecursive(successorState, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                                   beta)
                currentReward = self.getQValue(gameState, agentIndex, action) if default_params[
                    "eval_total_reward"] else 0
                newAlpha += currentReward
                if newAlpha > bestValue:
                    bestValue = newAlpha
                    bestAction = action
                if newAlpha > alpha: alpha = newAlpha
                if alpha >= beta: break
        else:
            bestValue = float("inf")
            for action in gameState.getLegalActions(agentIndex):
                successorState = gameState.generateSuccessor(agentIndex, action)
                newBeta, _ = self.searchRecursive(successorState, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                                  beta)
                if newBeta < bestValue:
                    bestValue = newBeta
                    bestAction = action
                if newBeta < beta: beta = newBeta
                if alpha >= beta: break
        return bestValue, bestAction

    def searchRecursive(self, gameState, agentIndex, searchAgentIndices, depth, alpha=float("-inf"), beta=float("inf")):
        if gameState.isOver():
            result = self.searchWhenGameOver(gameState)
        elif depth == 0:
            result = self.searchWhenZeroDepth(gameState, agentIndex)
        else:
            self.ifTimeoutRaiseTimeoutException()
            result = self.searchWhenNonTerminated(gameState, agentIndex, searchAgentIndices, depth, alpha, beta)
        return result

    def searchTop(self, gameState):
        inferenceState = gameState.deepCopy()
        legalActions = gameState.getLegalActions(self.index)
        agentInferencePositionsAndPosibilities = [self.getCurrentAgentPositionsAndPosibilities(agentIndex) for
                                                  agentIndex in range(gameState.getNumAgents())]
        agentInferencePositions = [self.getCurrentAgentPostions(agentIndex) for agentIndex in
                                   range(gameState.getNumAgents())]
        initPointers = [0 for _ in range(gameState.getNumAgents())]
        pointers = None
        upLimits = [min(self.maxInferencePositionCount, len(agentInferencePositionsAndPosibilities[agentIndex])) for
                    agentIndex in range(gameState.getNumAgents())]
        myPosition = inferenceState.getAgentPosition(self.index)

        def changePointer():
            changeAgentIndex = None
            minPointer = 9999
            for agentIndex in range(gameState.getNumAgents()):
                if pointers[agentIndex] + 1 < upLimits[agentIndex] and pointers[agentIndex] < minPointer:
                    minPointer = pointers[agentIndex]
                    changeAgentIndex = agentIndex
            if changeAgentIndex is not None:
                pointers[changeAgentIndex] += 1
                return True
            else:
                return False

        def setConfigurations(origionState, inferenceState):
            totalPosibility = 1.0
            for agentIndex in range(origionState.getNumAgents()):
                if origionState.getAgentState(agentIndex).configuration is None:
                    position, posibility = agentInferencePositionsAndPosibilities[agentIndex][pointers[agentIndex]]
                    inferenceState.data.agentStates[agentIndex].configuration = game.Configuration(position,
                                                                                                   Directions.STOP)
                else:
                    posibility = 1.0
                totalPosibility *= posibility
            return totalPosibility

        def getSearchAgentIndices(gameState, myPosition, searchMaxDistance):
            searchAgentIndices = []
            for agentIndex in range(gameState.getNumAgents()):
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None and self.getMazeDistance(agentPosition,
                                                                      myPosition) <= searchMaxDistance:  # the origion is mahattan distance
                    searchAgentIndices.append(agentIndex)
            return searchAgentIndices

        bestAction = None
        bestValue = float("-inf")
        for searchDepth in range(self.maxDepth + 1):
            searchSuccess = False
            localBestValue = None
            localBestAction = None
            try:
                localAverageBestValue = 0.0
                totalPosibility = 1.0
                localResults = []
                considerationDistance = int(searchDepth * default_params["consideration_distance_factor"])
                # self.log("Search depth [%d], consideration distance is [%d]" % (searchDepth, considerationDistance))
                pointers = initPointers
                while True:
                    posibility = setConfigurations(gameState, inferenceState)
                    searchAgentIndices = getSearchAgentIndices(inferenceState, myPosition, considerationDistance)
                    self.log("Take agents %s in to consideration" % searchAgentIndices)
                    value, action = self.searchRecursive(inferenceState, self.index, searchAgentIndices, searchDepth)
                    localResults.append([value, action])
                    totalPosibility *= posibility
                    localAverageBestValue += posibility * value
                    if not changePointer(): break
                localAverageBestValue /= totalPosibility
                minDifference = float("inf")
                for value, action in localResults:
                    difference = abs(value - localAverageBestValue)
                    if difference < minDifference:
                        minDifference = difference
                        localBestAction = action
                        localBestValue = value
                searchSuccess = True
            except TimeoutException:
                pass
            # except multiprocessing.TimeoutError: pass  # Coment this line if you want to use keyboard interrupt
            if searchSuccess:
                bestValue = localBestValue
                bestAction = localBestAction
            else:
                self.log("Failed when search max depth [%d]" % (searchDepth,))
                break
        self.log("Take action [%s] with evaluation [%.6f]" % (bestAction, bestValue))
        return bestValue, bestAction

    #########
    # utils #
    #########

    def ifTimeoutRaiseTimeoutException(self):
        if self.timeRemainPercent() < default_params["truncate_remain_time_percent"]:
            raise TimeoutException()

    def getNextAgentIndex(self, gameState, currentAgentIndex):
        nextAgentIndex = currentAgentIndex + 1
        nextAgentIndex = 0 if nextAgentIndex >= gameState.getNumAgents() else nextAgentIndex
        return nextAgentIndex

    def getNextSearchableAgentIndexAndDepth(self, gameState, searchAgentIndices, currentAgentIndex, currentDepth):
        nextAgentIndex = currentAgentIndex
        nextDepth = currentDepth
        while True:
            nextAgentIndex = self.getNextAgentIndex(gameState, nextAgentIndex)
            nextDepth = nextDepth - 1 if nextAgentIndex == self.index else nextDepth
            if nextAgentIndex in searchAgentIndices: break
        return nextAgentIndex, nextDepth

    ##############
    # interfaces #
    ##############

    def log(self, content, classification=LogClassification.INFOMATION):
        if default_params["enable_print_log"]:
            print(str(content))
        pass

    def timePast(self):
        return time.time() - self.record["START"]

    def timePastPercent(self):
        return self.timePast() / self.actionTimeLimit

    def timeRemain(self):
        return self.actionTimeLimit - self.timePast()

    def timeRemainPercent(self):
        return self.timeRemain() / self.actionTimeLimit

    def printTimes(self):
        timeList = list(self.record.items())
        timeList.sort(key=lambda x: x[1])
        relativeTimeList = []
        startTime = self.record["START"]
        totalTime = timeList[len(timeList) - 1][1] - startTime
        reachActionTimeLimit = totalTime >= self.actionTimeLimit
        for i in range(1, len(timeList)):
            j = i - 1
            k, v = timeList[i]
            _, lastV = timeList[j]
            records = v - lastV
            if records >= 0.0001:
                relativeTimeList.append("%s:%.4f" % (k, records))
        prefix = "O " if not reachActionTimeLimit else "X "
        prefix += "Total %.4f " % (totalTime,)
        self.log(prefix + str(relativeTimeList))

    def getFeatures(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    def getWeights(self, gameState, actionAgentIndex, action):
        util.raiseNotDefined()

    def getSuccessor(self, gameState, actionAgentIndex, action):
        """Finds the next successor which is a grid position (location tuple)."""
        successor = gameState.generateSuccessor(actionAgentIndex, action)
        pos = successor.getAgentState(actionAgentIndex).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(actionAgentIndex, action)
        else:
            return successor

    def getCurrentAgentPositionsAndPosibilities(self, agentIndex):
        '''get inference positions and posibilities'''
        gameState = self.getCurrentObservation()
        if agentIndex in self.getTeam(gameState):
            result = [(gameState.getAgentPosition(agentIndex), 1.0)]
        else:
            result = self.beliefDistributions[agentIndex].items()
            result.sort(key=lambda x: x[1], reverse=True)
        return result

    def getCurrentAgentPostions(self, agentIndex):
        '''get inference positions'''
        result = self.getCurrentAgentPositionsAndPosibilities(agentIndex)
        result = [i[0] for i in result]
        return result

    def getCurrentMostLikelyPosition(self, agentIndex):
        return self.getCurrentAgentPostions(agentIndex)[0]

    #############
    # inference #
    #############

    width = None
    height = None
    particleSum = None
    particleDicts = None
    walls = None

    def initPositionInference(self, gameState):
        if PositionInferenceAgent.particleSum is None:
            PositionInferenceAgent.width = gameState.data.layout.width
            PositionInferenceAgent.height = gameState.data.layout.height
            PositionInferenceAgent.particleSum = default_params["particle_sum"]
            PositionInferenceAgent.particleDicts = [None for _ in range(gameState.getNumAgents())]
            PositionInferenceAgent.walls = gameState.getWalls()

            for agentIndex in self.getOpponents(gameState):
                self.initParticleDict(agentIndex)

    def updatePositionInference(self, gameState):
        def update(particleDict, sonarDistance, isStay):
            if isStay and default_params["enable_stay_inference_optimization"]:
                transferedParticleDict = particleDict
            else:
                transferedParticleDict = util.Counter()
                for tile, sum in particleDict.items():
                    x, y = tile
                    available = [tile] if default_params["enable_stop_transition"] else []
                    if not PositionInferenceAgent.walls[x][y + 1]: available.append((x, y + 1))
                    if not PositionInferenceAgent.walls[x][y - 1]: available.append((x, y - 1))
                    if not PositionInferenceAgent.walls[x - 1][y]: available.append((x - 1, y))
                    if not PositionInferenceAgent.walls[x + 1][y]: available.append((x + 1, y))
                    # assume equal trans prob
                    for newTile in available:
                        transferedParticleDict[newTile] += sum / len(available)
                    remainSum = sum % len(available)
                    for _ in range(remainSum):
                        newTile = random.choice(available)
                        transferedParticleDict[newTile] += 1
            agentX, agentY = agentPosition
            candidateParticleDict = util.Counter()
            for tile, sum in transferedParticleDict.items():
                x, y = tile
                distance = abs(agentX - x) + abs(agentY - y)
                newProbability = gameState.getDistanceProb(distance, sonarDistance) * sum
                if newProbability > 0:
                    candidateParticleDict[tile] += newProbability
            if len(candidateParticleDict) > 0:
                newPariticleDict = util.Counter()
                for _ in range(PositionInferenceAgent.particleSum):
                    tile = self.weightedRandomChoice(candidateParticleDict)
                    newPariticleDict[tile] += 1
                return newPariticleDict
            else:
                self.log("Lost target", classification=LogClassification.WARNING)
                return self.getFullParticleDict()

        agentPosition = gameState.getAgentPosition(self.index)

        for agentIndex in range(gameState.getNumAgents()):
            if agentIndex in self.getOpponents(gameState):
                particleDict = PositionInferenceAgent.particleDicts[agentIndex]
                sonarDistance = gameState.agentDistances[agentIndex]
                isStay = not (agentIndex == self.index - 1 or agentIndex == self.index + gameState.getNumAgents() - 1)
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))
                PositionInferenceAgent.particleDicts[agentIndex] = update(particleDict, sonarDistance, isStay)

    def checkPositionInference(self, gameState):
        for agentIndex in range(gameState.getNumAgents()):
            if agentIndex in self.getOpponents(gameState):  # postion of teammates are always available
                # when eat pacman (not for sure)
                def eatPacmanJudge():
                    previous = self.getPreviousObservation()
                    if previous is not None:
                        previousOppoPos = previous.getAgentPosition(agentIndex)
                        if previousOppoPos is not None:
                            if previousOppoPos == gameState.getAgentPosition(self.index):
                                return True
                    return False

                if eatPacmanJudge():
                    self.initParticleDict(agentIndex)

                # when observed
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None:
                    PositionInferenceAgent.particleDicts[agentIndex] = util.Counter()
                    PositionInferenceAgent.particleDicts[agentIndex][agentPosition] = PositionInferenceAgent.particleSum

    def updateBeliefDistribution(self):
        self.beliefDistributions = [dict.copy() if dict is not None else None for dict in
                                   PositionInferenceAgent.particleDicts]
        for dict in self.beliefDistributions: dict.normalize() if dict is not None else None

    #########
    # utils #
    #########

    def getFullParticleDict(self):
        result = util.Counter()
        xStart = 1
        xEnd = PositionInferenceAgent.width - 1
        yStart = 1
        yEnd = PositionInferenceAgent.height - 1
        total = 0
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    total += 1
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    result[(x, y)] = PositionInferenceAgent.particleSum / total
        return result

    def initParticleDict(self, opponentAgentIndex):
        if self.red:
            xStart = PositionInferenceAgent.width - 2
            xEnd = PositionInferenceAgent.width - 1
            yStart = PositionInferenceAgent.height / 2
            yEnd = PositionInferenceAgent.height - 1
        else:
            xStart = 1
            xEnd = 2
            yStart = 1
            yEnd = PositionInferenceAgent.height / 2
        total = 0
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    total += 1
        PositionInferenceAgent.particleDicts[opponentAgentIndex] = util.Counter()
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not PositionInferenceAgent.walls[x][y]:
                    PositionInferenceAgent.particleDicts[opponentAgentIndex][
                        (x, y)] = PositionInferenceAgent.particleSum / total

    def weightedRandomChoice(self, weightDict):
        weights = []
        elems = []
        for elem in weightDict:
            weights.append(weightDict[elem])
            elems.append(elem)
        total = sum(weights)
        key = random.uniform(0, total)
        runningTotal = 0.0
        chosenIndex = None
        for i in range(len(weights)):
            weight = weights[i]
            runningTotal += weight
            if runningTotal >= key:
                chosenIndex = i
                return elems[chosenIndex]
        raise Exception('Should not reach here')



class RandomOffensiveAgent(ExpectimaxAgent):
    """An agent class. Optimized for offense. You can use it directly."""

    ######################
    # overload functions #
    ######################

    def getFeatures(self, gameState, actionAgentIndex, action):
        assert actionAgentIndex == self.index
        successor = self.getSuccessor(gameState, actionAgentIndex, action)

        walls = successor.getWalls()
        position = successor.getAgentPosition(self.index)
        teamIndices = self.getTeam(successor)
        opponentIndices = self.getOpponents(successor)
        foodList = self.getFood(successor).asList()
        foodList.sort(key=lambda x: self.getMazeDistance(position, x))
        defendFoodList = self.getFoodYouAreDefending(successor).asList()
        capsulesList = self.getCapsules(successor)
        capsulesList.sort(key=lambda x: self.getMazeDistance(position, x))
        defendCapsulesList = self.getCapsulesYouAreDefending(successor)
        scaredTimer = successor.getAgentState(self.index).scaredTimer
        foodCarrying = successor.getAgentState(self.index).numCarrying
        foodReturned = successor.getAgentState(self.index).numReturned
        stopped = action == Directions.STOP
        reversed = action != Directions.STOP and Actions.reverseDirection(
            successor.getAgentState(self.index).getDirection()) == gameState.getAgentState(self.index).getDirection()
        map_size = walls.height * walls.width

        def isPacman(state, index):
            return state.getAgentState(index).isPacman

        def isGhost(state, index):
            return not isPacman(state, index)

        def isScared(state, index):
            return state.data.agentStates[index].scaredTimer > 0  # and isGhost(state, index)

        def isInvader(state, index):
            return index in opponentIndices and isPacman(state, index)

        def isHarmfulInvader(state, index):
            return isInvader(state, index) and isScared(state, self.index)

        def isHarmlessInvader(state, index):
            return isInvader(state, index) and not isScared(state, self.index)

        def isHarmfulGhost(state, index):
            return index in opponentIndices and isGhost(state, index) and not isScared(state, index)

        def isHarmlessGhost(state, index):
            return index in opponentIndices and isGhost(state, index) and isScared(state, index)

        def getDistance(pos):
            return self.getMazeDistance(position, pos)

        def getPosition(state, index):
            return state.getAgentPosition(index)

        def getScaredTimer(state, index):
            return state.getAgentState(index).scaredTimer

        def getFoodCarrying(state, index):
            return state.getAgentState(index).numCarrying

        def getFoodReturned(state, index):
            return state.getAgentState(index).numReturned

        def getPositionFactor(distance):
            return (float(distance) / (walls.width * walls.height))

        features = util.Counter()

        features["stopped"] = 1 if stopped else 0

        features["reversed"] = 1 if reversed else 0

        features["scared"] = 1 if isScared(successor, self.index) else 0

        features["food_returned"] = successor.getAgentState(self.index).numReturned

        features["food_carrying"] = successor.getAgentState(self.index).numCarrying

        features["food_defend"] = len(defendFoodList)

        #features["nearest_food_distance_factor"] = float(getDistance(foodList[0])) / (
        #walls.height * walls.width) if len(foodList) > 0 else 0

        if len(foodList) > 0:
            features["nearest_food_distance_factor"] = float(self.getMazeDistance(position, foodList[0]))/map_size
        else:
            features["nearest_food_distance_factor"] = 0

        #features["nearest_capsules_distance_factor"] = float(getDistance(capsulesList[0])) / (
        #    walls.height * walls.width) if len(capsulesList) > 0 else 0
        if len(capsulesList) > 0:
            features["nearest_capsules_distance_factor"] = \
                float(self.getMazeDistance(position, capsulesList[0]))/map_size
        else:
            features["nearest_capsules_distance_factor"] = 0

        #returnFoodX = walls.width / 2 - 1 if self.red else walls.width / 2
        if self.red:
            central_position = walls.width/2 - 1
        else:
            central_position = walls.width/2

        #nearestFoodReturnDistance = min(
        #    [getDistance((returnFoodX, y)) for y in range(walls.height) if not walls[returnFoodX][y]])
        #features["return_food_factor"] = float(nearestFoodReturnDistance) / (walls.height * walls.width) * foodCarrying


        closest_return_distance = 9999
        for i in range(walls.height):
            if not walls[central_position][i]:
                temp_distance = float(self.getMazeDistance(position, (central_position, i)))
                if temp_distance < closest_return_distance:
                    closest_return_distance = temp_distance

        features["return_food_factor"] = closest_return_distance/map_size * features["food_carrying"]

        # check the opponents situation
        peace_invaders = []
        evil_invaders = []
        ghosts = []
        for opponent in opponentIndices:
            if isHarmlessInvader(successor, opponent):
                peace_invaders.append(opponent)
            if isHarmfulInvader(successor, opponent):
                evil_invaders.append(opponent)
            if isHarmlessGhost(successor, opponent):
                ghosts.append(opponent)



        #harmlessInvaders = [i for i in opponentIndices if isHarmlessInvader(successor, i)]
        #features["harmless_invader_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) * (getFoodCarrying(successor, i) + 5)
        #       for i in peace_invaders]) if len(peace_invaders) > 0 else 0

        #harmfullInvaders = [i for i in opponentIndices if isHarmfulInvader(successor, i)]
        #features["harmful_invader_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) for i in evil_invaders]) \
        #    if len(evil_invaders) > 0 else 0

        #harmlessGhosts = [i for i in opponentIndices if isHarmlessGhost(successor, i)]
        #features["harmless_ghost_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) for i in ghosts]) if len(
        #    ghosts) > 0 else 0

        if len(peace_invaders) > 0:
            peace_invaders_factor = -9999
            for invader in peace_invaders:
                temp_distance = self.getMazeDistance(position, successor.getAgentPosition(invader))
                temp_food = successor.getAgentState(invader).numCarrying + 5
                temp_factor = float(temp_distance)/map_size * temp_food
                if temp_factor > peace_invaders_factor:
                    peace_invaders_factor = temp_factor

            features["harmless_invader_distance_factor"] = peace_invaders_factor
        else:
            features["harmless_invader_distance_factor"] = 0


        if len(evil_invaders) > 0:
            evil_invaders_factor = -9999
            for invader in evil_invaders:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(invader)))/map_size
                if temp_distance > evil_invaders_factor:
                    evil_invaders_factor = temp_distance
            features["harmful_invader_distance_factor"] = evil_invaders_factor
        else:
            features["harmful_invader_distance_factor"] = 0


        if len(ghosts) > 0:
            ghosts_factor = -9999
            for ghost in ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance > ghosts_factor:
                    max_distance = temp_distance
            features["harmless_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmless_ghost_distance_factor"] = 0



        return features

    def getWeights(self, gameState, actionAgentIndex, action):
        return {
            "stopped": -2.0,
            "reversed": -1.0,
            "scared": -2.0,
            "food_returned": 10.0,
            "food_carrying": 8.0,
            "food_defend": 0.0,
            "nearest_food_distance_factor": -1.0,
            "nearest_capsules_distance_factor": -1.0,
            "return_food_factor": -0.5,  # 1.5
             "team_distance": 0.5,
            "harmless_invader_distance_factor": -0.1,
            "harmful_invader_distance_factor": 0.1,
            "harmless_ghost_distance_factor": -0.2,
        }


class RandomDefensiveAgent(ExpectimaxAgent):
    """An agent class. Optimized for defence. You can use it directly."""

    ######################
    # overload functions #
    ######################`

    def getFeatures(self, gameState, actionAgentIndex, action):
        assert actionAgentIndex == self.index
        successor = self.getSuccessor(gameState, actionAgentIndex, action)

        walls = successor.getWalls()
        position = successor.getAgentPosition(self.index)
        teamIndices = self.getTeam(successor)
        opponentIndices = self.getOpponents(successor)
        foodList = self.getFood(successor).asList()
        foodList.sort(key=lambda x: self.getMazeDistance(position, x))
        defendFoodList = self.getFoodYouAreDefending(successor).asList()
        capsulesList = self.getCapsules(successor)
        capsulesList.sort(key=lambda x: self.getMazeDistance(position, x))
        defendCapsulesList = self.getCapsulesYouAreDefending(successor)
        scaredTimer = successor.getAgentState(self.index).scaredTimer
        foodCarrying = successor.getAgentState(self.index).numCarrying
        foodReturned = successor.getAgentState(self.index).numReturned
        stopped = action == Directions.STOP
        reversed = action != Directions.STOP and Actions.reverseDirection(
            successor.getAgentState(self.index).getDirection()) == gameState.getAgentState(self.index).getDirection()
        map_size = walls.height * walls.width

        def isPacman(state, index):
            return state.getAgentState(index).isPacman

        def isGhost(state, index):
            return not isPacman(state, index)

        def isScared(state, index):
            return state.data.agentStates[index].scaredTimer > 0  # and isGhost(state, index)

        def isInvader(state, index):
            return index in opponentIndices and isPacman(state, index)

        def isHarmfulInvader(state, index):
            return isInvader(state, index) and isScared(state, self.index)

        def isHarmlessInvader(state, index):
            return isInvader(state, index) and not isScared(state, self.index)

        def isHarmfulGhost(state, index):
            return index in opponentIndices and isGhost(state, index) and not isScared(state, index)

        def isHarmlessGhost(state, index):
            return index in opponentIndices and isGhost(state, index) and isScared(state, index)

        def getDistance(pos):
            return self.getMazeDistance(position, pos)

        def getPosition(state, index):
            return state.getAgentPosition(index)

        def getScaredTimer(state, index):
            return state.getAgentState(index).scaredTimer

        def getFoodCarrying(state, index):
            return state.getAgentState(index).numCarrying

        def getFoodReturned(state, index):
            return state.getAgentState(index).numReturned

        def getPositionFactor(distance):
            return (float(distance) / (walls.width * walls.height))

        features = util.Counter()

        features["stopped"] = 1 if stopped else 0

        features["reversed"] = 1 if reversed else 0

        features["scared"] = 1 if isScared(successor, self.index) else 0

        features["food_returned"] = successor.getAgentState(self.index).numReturned

        features["food_carrying"] = successor.getAgentState(self.index).numCarrying

        features["food_defend"] = len(defendFoodList)

        #features["nearest_food_distance_factor"] = float(getDistance(foodList[0])) / (
        #walls.height * walls.width) if len(foodList) > 0 else 0

        if len(foodList) > 0:
            features["nearest_food_distance_factor"] = float(self.getMazeDistance(position, foodList[0]))/map_size
        else:
            features["nearest_food_distance_factor"] = 0

        #features["nearest_capsules_distance_factor"] = float(getDistance(capsulesList[0])) / (
        #    walls.height * walls.width) if len(capsulesList) > 0 else 0
        if len(capsulesList) > 0:
            features["nearest_capsules_distance_factor"] = \
                float(self.getMazeDistance(position, capsulesList[0]))/map_size
        else:
            features["nearest_capsules_distance_factor"] = 0

        #returnFoodX = walls.width / 2 - 1 if self.red else walls.width / 2
        if self.red:
            central_position = walls.width/2 - 1
        else:
            central_position = walls.width/2

        #nearestFoodReturnDistance = min(
        #    [getDistance((returnFoodX, y)) for y in range(walls.height) if not walls[returnFoodX][y]])
        #features["return_food_factor"] = float(nearestFoodReturnDistance) / (walls.height * walls.width) * foodCarrying


        closest_return_distance = 9999
        for i in range(walls.height):
            if not walls[central_position][i]:
                temp_distance = float(self.getMazeDistance(position, (central_position, i)))
                if temp_distance < closest_return_distance:
                    closest_return_distance = temp_distance

        features["return_food_factor"] = closest_return_distance/map_size * features["food_carrying"]

        # check the opponents situation
        peace_invaders = []
        evil_invaders = []
        ghosts = []
        for opponent in opponentIndices:
            if isHarmlessInvader(successor, opponent):
                peace_invaders.append(opponent)
            if isHarmfulInvader(successor, opponent):
                evil_invaders.append(opponent)
            if isHarmlessGhost(successor, opponent):
                ghosts.append(opponent)



        #harmlessInvaders = [i for i in opponentIndices if isHarmlessInvader(successor, i)]
        #features["harmless_invader_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) * (getFoodCarrying(successor, i) + 5)
        #       for i in peace_invaders]) if len(peace_invaders) > 0 else 0

        #harmfullInvaders = [i for i in opponentIndices if isHarmfulInvader(successor, i)]
        #features["harmful_invader_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) for i in evil_invaders]) \
        #    if len(evil_invaders) > 0 else 0

        #harmlessGhosts = [i for i in opponentIndices if isHarmlessGhost(successor, i)]
        #features["harmless_ghost_distance_factor"] = max(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) for i in ghosts]) if len(
        #    ghosts) > 0 else 0

        if len(peace_invaders) > 0:
            peace_invaders_factor = -9999
            for invader in peace_invaders:
                temp_distance = self.getMazeDistance(position, successor.getAgentPosition(invader))
                temp_food = successor.getAgentState(invader).numCarrying + 5
                temp_factor = float(temp_distance)/map_size * temp_food
                if temp_factor > peace_invaders_factor:
                    peace_invaders_factor = temp_factor

            features["harmless_invader_distance_factor"] = peace_invaders_factor
        else:
            features["harmless_invader_distance_factor"] = 0


        if len(evil_invaders) > 0:
            evil_invaders_factor = -9999
            for invader in evil_invaders:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(invader)))/map_size
                if temp_distance > evil_invaders_factor:
                    evil_invaders_factor = temp_distance
            features["harmful_invader_distance_factor"] = evil_invaders_factor
        else:
            features["harmful_invader_distance_factor"] = 0


        if len(ghosts) > 0:
            ghosts_factor = -9999
            for ghost in ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance > ghosts_factor:
                    max_distance = temp_distance
            features["harmless_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmless_ghost_distance_factor"] = 0



        return features

    def getWeights(self, gameState, actionAgentIndex, action):
        return {
            "stopped": -2.0,
            "reversed": -1.0,
            "scared": -2.0,
            "food_returned": 1.0,
            "food_carrying": 0.5,
            "food_defend": 5.0,
            "nearest_food_distance_factor": -1.0,
            "nearest_capsules_distance_factor": -0.5,
            "return_food_factor": 1.5,
             "team_distance": 0.5,
            "harmless_invader_distance_factor": -1.0,
            "harmful_invader_distance_factor": 2.0,
            "harmless_ghost_distance_factor": -0.1,
        }

class MCTSDefendAgent(CaptureAgent):
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

class ReflexCaptureAgent(CaptureAgent):
    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 1.0}


class MCTSOffensiveAgent(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        features['successorScore'] = self.getScore(successor)

        foodList = self.getFood(successor).asList()
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        myPos = successor.getAgentState(self.index).getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
        if len(inRange) > 0:
            positions = [agent.getPosition() for agent in inRange]
            closest = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
            closestDist = self.getMazeDistance(myPos, closest)
            if closestDist <= 5:
                features['distanceToGhost'] = closestDist

        features['isPacman'] = 1 if successor.getAgentState(self.index).isPacman else 0

        return features

    def getWeights(self, gameState, action):
        if self.inactiveTime > 80:
            return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 1000}

        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentState(self.index).getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
        if len(inRange) > 0:
            positions = [agent.getPosition() for agent in inRange]
            closestPos = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
            closestDist = self.getMazeDistance(myPos, closestPos)
            closest_enemies = filter(lambda x: x[0] == closestPos, zip(positions, inRange))
            for agent in closest_enemies:
                if agent[1].scaredTimer > 0:
                    return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 0, 'isPacman': 0}

        return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 0}

    def randomSimulation(self, depth, gameState):
        new_state = gameState.deepCopy()
        while depth > 0:
            actions = new_state.getLegalActions(self.index)
            actions.remove(Directions.STOP)
            current_direction = new_state.getAgentState(self.index).configuration.direction
            reversed_direction = Directions.REVERSE[new_state.getAgentState(self.index).configuration.direction]
            if reversed_direction in actions and len(actions) > 1:
                actions.remove(reversed_direction)
            a = random.choice(actions)
            new_state = new_state.generateSuccessor(self.index, a)
            depth -= 1
        return self.evaluate(new_state, Directions.STOP)

    def takeToEmptyAlley(self, gameState, action, depth):
        if depth == 0:
            return False
        old_score = self.getScore(gameState)
        new_state = gameState.generateSuccessor(self.index, action)
        new_score = self.getScore(new_state)
        if old_score < new_score:
            return False
        actions = new_state.getLegalActions(self.index)
        actions.remove(Directions.STOP)
        reversed_direction = Directions.REVERSE[new_state.getAgentState(self.index).configuration.direction]
        if reversed_direction in actions:
            actions.remove(reversed_direction)
        if len(actions) == 0:
            return True
        for a in actions:
            if not self.takeToEmptyAlley(new_state, a, depth - 1):
                return False
        return True

    def __init__(self, index):
        CaptureAgent.__init__(self, index)
        self.numEnemyFood = "+inf"
        self.inactiveTime = 0

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.distancer.getMazeDistances()

    def chooseAction(self, gameState):
        currentEnemyFood = len(self.getFood(gameState).asList())
        if self.numEnemyFood != currentEnemyFood:
            self.numEnemyFood = currentEnemyFood
            self.inactiveTime = 0
        else:
            self.inactiveTime += 1
        if gameState.getInitialAgentPosition(self.index) == gameState.getAgentState(self.index).getPosition():
            self.inactiveTime = 0

        all_actions = gameState.getLegalActions(self.index)
        all_actions.remove(Directions.STOP)
        actions = []
        for a in all_actions:
            if not self.takeToEmptyAlley(gameState, a, 5):
                actions.append(a)
        if len(actions) == 0:
            actions = all_actions

        fvalues = []
        for a in actions:
            new_state = gameState.generateSuccessor(self.index, a)
            value = 0
            for i in range(1, 31):
                value += self.randomSimulation(10, new_state)
            fvalues.append(value)

        best = max(fvalues)
        ties = filter(lambda x: x[0] == best, zip(fvalues, actions))
        toPlay = random.choice(ties)[1]

        return toPlay
