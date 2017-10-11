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
    "action_time_limit": 0.97,  # higher if you want to search deeper
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
               second='RandomDefensiveAgent',
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

class InferenceModule(CaptureAgent):
    """
    An inference module tracks a belief distribution over a ghost's location.
    This is an abstract class, which you should not modify.
    """

    def registerInitialState(self, gameState):
        "Sets the ghost agent for later access"
        CaptureAgent.registerInitialState(self, gameState)
        #self.index = self.agent.index

        self.num_particles = None
        self.particles = []  # most recent observation position
        self.width = gameState.data.layout.width
        self.height = gameState.data.layout.height
        self.walls = gameState.getWalls()
        InferenceModule.walls = gameState.getWalls()
        #self.initializeInference(gameState)
        self.setNumParticles(default_params["particle_sum"])
        self.particles = [None for _ in range(gameState.getNumAgents())]
        for index in self.getOpponents(gameState):
            self.initializeParticles(index)
            #print("initial success")
        #print(self.particles)


    width = None
    height = None
    particleSum = None
    particles = None
    walls = None


    def getJailPosition(self):
        return (2 * self.ghostAgent.index - 1, 1)

    def getPositionDistribution(self, gameState):
        """
        Returns a distribution over successor positions of the ghost from the
        given gameState.

        You must first place the ghost in the gameState, using setGhostPosition
        below.
        """
        ghostPosition = gameState.getGhostPosition(self.index)  # The position you set
        actionDist = self.ghostAgent.getDistribution(gameState)
        dist = util.Counter()
        for action, prob in actionDist.items():
            successorPosition = game.Actions.getSuccessor(ghostPosition, action)
            dist[successorPosition] = prob
        return dist

    def setGhostPosition(self, gameState, ghostPosition):
        """
        Sets the position of the ghost for this inference module to the
        specified position in the supplied gameState.

        Note that calling setGhostPosition does not change the position of the
        ghost in the GameState object used for tracking the true progression of
        the game.  The code in inference.py only ever receives a deep copy of
        the GameState object which is responsible for maintaining game state,
        not a reference to the original object.  Note also that the ghost
        distance observations are stored at the time the GameState object is
        created, so changing the position of the ghost will not affect the
        functioning of observeState.
        """
        conf = game.Configuration(ghostPosition, game.Directions.STOP)
        gameState.data.agentStates[self.index] = game.AgentState(conf, False)
        return gameState

    def observeState(self, gameState):
        "Collects the relevant noisy distance observation and pass it along."
        distances = gameState.getNoisyGhostDistances()
        if len(distances) >= self.index:  # Check for missing observations
            obs = distances[self.index - 1]
            self.obs = obs
            self.observe(obs, gameState)


    """
    def initialize(self, gameState):
        "Initializes beliefs to a uniform distribution over all positions."
        # The legal positions do not include the ghost prison cells in the bottom left.
        self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
        self.initializeUniformly(gameState)
    """

    def initializeInference(self, gameState):
        if self.num_particles is None:
            self.width = gameState.data.layout.width
            self.height = gameState.data.layout.height
            self.setNumParticles(default_params["particle_sum"])
            self.particles = [None for _ in range(gameState.getNumAgents())]
            self.walls = gameState.getWalls()

            for index in self.getOpponents(gameState):
                self.initializeParticles(index)


    ############################################
    # Useful methods for all inference modules #
    ############################################

    def setNumParticles(self, numParticles):
        self.num_particles = numParticles

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
                    self.particles(agentIndex)

                    # when observed
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None:
                    self.particles[agentIndex] = util.Counter()
                    self.particles[agentIndex][
                    agentPosition] = self.num_particles

     # Initialize the particles

    def getFullParticleDict(self):
        result = util.Counter()
        xStart = 1
        xEnd = self.width - 1
        yStart = 1
        yEnd = self.height - 1
        total = 0
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not self.walls[x][y]:
                    total += 1
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                if not self.walls[x][y]:
                    result[(x, y)] = self.num_particles / total
        return result

    def getParticles(self):
        particles = util.Counter()

        sum = 0
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if not self.walls[x][y]:
                    sum = sum + 1
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if not self.walls[x][y]:
                    particles[(x, y)] = self.num_particles/sum

        return particles

    # Set Particles For Each Opponent
    def initializeParticles(self, index):

        if self.red:
            count = 0

            for x in range(self.width - 2, self.width - 1):
                for y in range(self.height/2, self.height - 1):
                    if not self.walls[x][y]:
                        count = count + 1

            self.particles[index] = util.Counter()
            for x in range(self.width - 2, self.width - 1):
                for y in range(self.height/2, self.height - 1):
                    if not self.walls[x][y]:
                        self.particles[index][(x, y)] = self.num_particles/count
        else:
            count = 0

            for x in range(1, 2):
                for y in range(1 / 2, self.height/2):
                    if not self.walls[x][y]:
                        count = count + 1

            self.particles[index] = util.Counter()
            for x in range(self.width - 2, self.width - 1):
                 for y in range(self.height / 2, self.height - 1):
                    if not self.walls[x][y]:
                        self.particles[index][(x, y)] = self.num_particles / count

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


    # Update Inference from the noisy distance
    def updateParticles(self, state):
        def update(particleDict, sonarDistance, isStay):
            if isStay and default_params["enable_stay_inference_optimization"]:
                transferedParticleDict = particleDict
            else:
                transferedParticleDict = util.Counter()
                #print(particleDict)
                for tile, sum in particleDict.items():
                    x, y = tile
                    available = [tile] if default_params["enable_stop_transition"] else []
                    if not self.walls[x][y + 1]: available.append((x, y + 1))
                    if not self.walls[x][y - 1]: available.append((x, y - 1))
                    if not self.walls[x - 1][y]: available.append((x - 1, y))
                    if not self.walls[x + 1][y]: available.append((x + 1, y))
                    # assume equal trans prob
                    for newTile in available:
                        transferedParticleDict[newTile] += sum / len(available)
                    remainSum = sum % len(available)
                    #print sum, len(available)
                    #print(remainSum)
                    for _ in range(remainSum):
                        newTile = random.choice(available)
                        transferedParticleDict[newTile] += 1
            agentX, agentY = agentPosition
            candidateParticleDict = util.Counter()
            for tile, sum in transferedParticleDict.items():
                x, y = tile
                distance = abs(agentX - x) + abs(agentY - y)
                newProbability = state.getDistanceProb(distance, sonarDistance) * sum
                if newProbability > 0:
                    candidateParticleDict[tile] += newProbability
            if len(candidateParticleDict) > 0:
                newPariticleDict = util.Counter()
                for _ in range(self.num_particles):
                    tile = self.weightedRandomChoice(candidateParticleDict)
                    newPariticleDict[tile] += 1
                return newPariticleDict
            else:
                #self.log("Lost target", classification=LogClassification.WARNING)
                #return self.getFullParticleDict()
                return self.getParticles()

        agentPosition = state.getAgentPosition(self.index)
        #position = state.getAgentPosition(self.index)
        enemies = self.getOpponents(state)

        for index in range(state.getNumAgents()):
            if index in enemies:
                noise_distance = state.agentDistances[index]
                temp_particles = self.particles[index]

                #flag = True
                #isStay = not (index == self.index - 1 or index == self.index + state.getNumAgents() - 1)
                if index == self.index - 1 or (index == (self.index + state.getNumAgents() - 1)):
                    flag = False
                else:
                    flag = True
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))

                self.particles[index] = update(temp_particles, noise_distance, flag)

        """"
        agentPosition = state.getAgentPosition(self.index)

        for agentIndex in range(state.getNumAgents()):
            if agentIndex in self.getOpponents(state):
                particleDict = self.particles[agentIndex]
                sonarDistance = state.agentDistances[agentIndex]
                isStay = not (agentIndex == self.index - 1 or agentIndex == self.index + state.getNumAgents() - 1)
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))
                PositionInferenceAgent.particleDicts[agentIndex] = update(particleDict, sonarDistance, isStay)
        """

    def updatePositionInference(self, gameState):
        def update(particleDict, sonarDistance, isStay):
            if isStay and default_params["enable_stay_inference_optimization"]:
                transferedParticleDict = particleDict
            else:
                transferedParticleDict = util.Counter()
                for tile, sum in particleDict.items():
                    x, y = tile
                    available = [tile] if default_params["enable_stop_transition"] else []
                    if not self.walls[x][y + 1]: available.append((x, y + 1))
                    if not self.walls[x][y - 1]: available.append((x, y - 1))
                    if not self.walls[x - 1][y]: available.append((x - 1, y))
                    if not self.walls[x + 1][y]: available.append((x + 1, y))
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
                for _ in range(self.num_particles):
                    tile = self.weightedRandomChoice(candidateParticleDict)
                    newPariticleDict[tile] += 1
                print(newPariticleDict)
                return newPariticleDict
            else:
                #self.log("Lost target", classification=LogClassification.WARNING)
                return self.getParticles()

        agentPosition = gameState.getAgentPosition(self.index)

        for agentIndex in range(gameState.getNumAgents()):
            if agentIndex in self.getOpponents(gameState):
                particleDict = self.particles[agentIndex]
                sonarDistance = gameState.agentDistances[agentIndex]
                isStay = not (agentIndex == self.index - 1 or agentIndex == self.index + gameState.getNumAgents() - 1)
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))
                #print(PositionInferenceAgent.particleDicts)
                self.particles[agentIndex] = update(particleDict, sonarDistance, isStay)





# Inference agent positions using Particle Filter Algorithm

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
        self.displayDistributionsOverPositions(self.beliefDistributions
                                               )
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
            bestAction = None
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


class ExpectimaxAgent(InferenceModule):
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

        InferenceModule.registerInitialState(self, gameState)
        self.actionTimeLimit = default_params["action_time_limit"]
        #PositionInferenceAgent.isFullyObserved = default_params["fully_observed"]
        #self.initPositionInference(gameState)

        #self.width = gameState.data.layout.width
        #self.height = gameState.data.layout.height
        #self.walls = gameState.getWalls()


        #self.model = InferenceModule(self, gameState)
        #self.model.__init__(self, gameState)
        #self.model.__init__(self, gameState)
        self.beliefDistributions = []
        #self.starting_point = gameState.getAgentPosition(self.index)

        self.starting_point = gameState.getAgentPosition(self.index)
        self.maxDepth = default_params["max_depth"]
        self.maxInferencePositionCount = default_params["max_position"]

    """
    def pickAction(self, gameState):
        self.record["BEFORE_SEARCH"] = time.time()
        _, bestAction = self.searchTop(gameState)
        self.record["AFTER_SEARCH"] = time.time()
        return bestAction
    """

    def chooseAction(self, gameState):
        self.log("Agent %d:" % (self.index,))
        self.record = {"START": time.time()}
        #action = self.takeAction(gameState)

        # choose the best action
        self.record["BEFORE_POSITION_INFERENCE"] = time.time()
        #self.updatePositionInference(gameState)
        print("Before")
        print(self.particles)
        #self.updateParticles(gameState)
        self.updateParticles(gameState)
        print ("After")
        print(self.particles)

        #self.checkPositionInference(gameState)

        for i in range(gameState.getNumAgents()):
            if i in self.getOpponents(gameState) :
                """"
                def eatPacmanJudge():
                    previous = self.getPreviousObservation()
                    if previous is not None:
                        previousOppoPos = previous.getAgentPosition(agentIndex)
                        if previousOppoPos is not None:
                            if previousOppoPos == gameState.getAgentPosition(self.index):
                                return True
                    return False
                """
                #if eatPacmanJudge():
                if self.getPreviousObservation() is not None:
                    if self.getPreviousObservation().getAgentPosition(i) is not None:
                        if self.getPreviousObservation().getAgentPosition(i) == gameState.getAgentPosition(self.index):
                            #self.initParticleDict(agentIndex)
                            print("particles have been set")
                            self.initializeParticles(i)

                """"
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None:
                    PositionInferenceAgent.particleDicts[agentIndex] = util.Counter()
                    PositionInferenceAgent.particleDicts[agentIndex][agentPosition] = PositionInferenceAgent.particleSum
                """
                # Opponents are in sight
                position = gameState.getAgentPosition(i)
                if position is not None:
                    self.particles[i] = util.Counter()
                    self.particles[i][position] = self.num_particles
        


        #self.updateBeliefDistribution()
        #self.beliefDistributions = [dict.copy() if dict is not None else None for dict in
        #                           PositionInferenceAgent.particleDicts]
        """"
        for particle in self.particles:
            if particle is not None:
                self.beliefDistributions.append(particle.copy())

        for dict in self.beliefDistributions: dict.normalize() if dict is not None else None
        """
        self.beliefDistributions = [dict.copy() if dict is not None else None for dict in self.particles]
        for dict in self.particles: dict.normalize() if dict is not None else None


        self.displayDistributionsOverPositions(self.beliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.record["AFTER_POISITION_INFERENCE"] = time.time()

        # select action with highest Q value
        #bestAction = self.selectAction(gameState)
        #foodLeft = len(self.getFood(gameState).asList())
        bestAction = None
        if len(self.getFood(gameState).asList()) <= 2:
            best_distance = 9999
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                temp_distance = self.getMazeDistance(self.starting_point, successor.getAgentPosition(self.index))
                if temp_distance < best_distance:
                    bestAction = action
                    best_distance = temp_distance
            #return bestAction
        else:
            self.record["BEFORE_REFLEX"] = time.time()
            #bestAction = self.pickAction(gameState)
            self.record["BEFORE_SEARCH"] = time.time()
            _, bestAction = self.searchTop(gameState)
            self.record["AFTER_SEARCH"] = time.time()
            self.record["AFTER_REFLEX"] = time.time()

        self.record["END"] = time.time()
        self.printTimes()
        return bestAction

    def selectAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        #actions = gameState.getLegalActions(self.index)
        foodLeft = len(self.getFood(gameState).asList())
        bestAction = None
        if foodLeft <= 2:
            best_distance = 9999
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                temp_distance = self.getMazeDistance(self.starting_point, successor.getAgentPosition(self.index))
                if temp_distance < best_distance:
                    bestAction = action
                    best_distance = temp_distance
            #return bestAction
        else:
            self.record["BEFORE_REFLEX"] = time.time()
            #bestAction = self.pickAction(gameState)
            self.record["BEFORE_SEARCH"] = time.time()
            _, bestAction = self.searchTop(gameState)
            self.record["AFTER_SEARCH"] = time.time()
            self.record["AFTER_REFLEX"] = time.time()

        return bestAction

    def final(self, gameState):
        ExpectimaxAgent.particleSum = None
        InferenceModule.final(self, gameState)

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


    # recursive simulate the game process and use alpha-beta pruning


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
                newAlpha, _ = self.getValue(successorState, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                                   beta)
                #currentReward = self.getQValue(gameState, agentIndex, action) if default_params["eval_total_reward"] else 0
                #newAlpha += currentReward
                if newAlpha > bestValue:
                    bestValue = newAlpha
                    bestAction = action
                if newAlpha > alpha: alpha = newAlpha
                if alpha >= beta: break
        else:
            bestValue = float("inf")
            for action in gameState.getLegalActions(agentIndex):
                successorState = gameState.generateSuccessor(agentIndex, action)
                newBeta, _ = self.getValue(successorState, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                                  beta)
                if newBeta < bestValue:
                    bestValue = newBeta
                    bestAction = action
                if newBeta < beta: beta = newBeta
                if alpha >= beta: break
        return bestValue, bestAction


    # minimax with Alpha-Beta pruning
    def getValue(self, gameState, agentIndex, searchAgentIndices, depth, alpha=float("-inf"), beta=float("inf")):
        actions = gameState.getLegalActions(agentIndex)
        best_score = None
        best_action = None

        if agentIndex in self.getTeam(gameState):
            best_score = float("-inf")
        else:
            best_score = float("inf")

        if gameState.isOver():
            #result = self.searchWhenGameOver(gameState)
            best_score = self.getQValue(gameState, self.index, Directions.STOP)
            best_action = Directions.STOP
            result = (best_score, best_action)
        elif depth == 0:
            #result = self.searchWhenZeroDepth(gameState, agentIndex)
            assert  agentIndex == self.index # can be deleted
            #legalActions = gameState.getLegalActions(agentIndex)
            actions.remove(
                Directions.STOP)  # STOP is not allowed, to avoid the problem of discontinuous evaluation function
            for action in actions:
                value = self.getQValue(gameState, agentIndex, action)
                if (agentIndex in self.getTeam(gameState) and value > best_score) \
                        or (not agentIndex in self.getTeam(gameState) and value < best_score):
                    best_score = value
                    best_action = action
            result = (best_score, best_action)
        else:
            self.ifTimeoutRaiseTimeoutException()

            nextAgentIndex, nextDepth = self.getNextSearchableAgentIndexAndDepth(gameState, searchAgentIndices,
                                                                                 agentIndex,
                                                                                 depth)
            best_action = None
            if agentIndex == self.index:  # no team work, is better
                best_score = float("-inf")
                possible_actions = gameState.getLegalActions(agentIndex)
                if not default_params["enable_stop_action"]:
                    possible_actions.remove(Directions.STOP)  # STOP is not allowed
                for action in possible_actions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    newAlpha, _ = self.getValue(successor, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                                beta)
                    # currentReward = self.getQValue(gameState, agentIndex, action) if default_params["eval_total_reward"] else 0
                    # newAlpha += currentReward
                    if newAlpha > best_score:
                        best_score = newAlpha
                        best_action = action
                    if newAlpha > alpha: alpha = newAlpha
                    if alpha >= beta: break
            else:
                best_score = float("inf")
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
                    newBeta, _ = self.getValue(successor, nextAgentIndex, searchAgentIndices, nextDepth, alpha,
                                               beta)
                    if newBeta < best_score:
                        best_score = newBeta
                        best_action = action
                    if newBeta < beta: beta = newBeta
                    if alpha >= beta: break
            #best_score,best_action = self.searchWhenNonTerminated(gameState, agentIndex, searchAgentIndices, depth, alpha, beta)

        return best_score, best_action


    def searchTop(self, gameState):
        inferenceState = gameState.deepCopy()
        legalActions = gameState.getLegalActions(self.index)
        agentInferencePositionsAndPosibilities = [self.getCurrentAgentPositionsAndPosibilities(agentIndex) for agentIndex in range(gameState.getNumAgents())]
        agentInferencePositions = [self.getCurrentAgentPostions(agentIndex) for agentIndex in range(gameState.getNumAgents())]
        initPointers = [0 for _ in range(gameState.getNumAgents())]
        pointers = None
        upLimits = [min(self.maxInferencePositionCount, len(agentInferencePositionsAndPosibilities[agentIndex])) for agentIndex in range(gameState.getNumAgents())]
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
                    inferenceState.data.agentStates[agentIndex].configuration = game.Configuration(position, Directions.STOP)
                else:
                    posibility = 1.0
                totalPosibility *= posibility
            return totalPosibility
        def getSearchAgentIndices(gameState, myPosition, searchMaxDistance):
            searchAgentIndices = []
            for agentIndex in range(gameState.getNumAgents()):
                agentPosition = gameState.getAgentPosition(agentIndex)
                if agentPosition is not None and self.getMazeDistance(agentPosition, myPosition) <= searchMaxDistance:  # the origion is mahattan distance
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
                    value, action = self.getValue(inferenceState, self.index, searchAgentIndices, searchDepth)
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
            #print("distributoins")
            #print self.beliefDistributions
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

    """"
    def initPositionInference(self, gameState):
        if PositionInferenceAgent.particleSum is None:
            PositionInferenceAgent.width = gameState.data.layout.width
            PositionInferenceAgent.height = gameState.data.layout.height
            PositionInferenceAgent.particleSum = default_params["particle_sum"]
            PositionInferenceAgent.particleDicts = [None for _ in range(gameState.getNumAgents())]
            PositionInferenceAgent.walls = gameState.getWalls()

            for agentIndex in self.getOpponents(gameState):
                self.initParticleDict(agentIndex)
    """

    """"
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
    """

    """"
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
    """

    """"
    def updateBeliefDistribution(self):
        self.beliefDistributions = [dict.copy() if dict is not None else None for dict in
                                   PositionInferenceAgent.particleDicts]
        for dict in self.beliefDistributions: dict.normalize() if dict is not None else None
    """
    #########
    # utils #
    #########

    """"
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

    """

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

