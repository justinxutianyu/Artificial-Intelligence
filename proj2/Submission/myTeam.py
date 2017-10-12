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
    #"eval_total_reward": False,  # otherwise eval state. It controls whether add up values.

    "enable_stop_action": False,  # used in many agents, whether enable STOP action.
    "enable_stop_transition": False,  # used in position inference, enable this to allow STOP transition
}


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed, first='RandomOffensiveAgent', second='OffensiveReflexAgent',
            maxDepth=None,
            maxPosition=None,
            actionTimeLimit=None,
            considerationDistanceFactor=None,

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
    if maxDepth is not None: default_params["max_depth"] = int(maxDepth)
    if maxPosition is not None: default_params["max_position"] = int(maxPosition)
    if actionTimeLimit is not None: default_params["action_time_limit"] = float(actionTimeLimit)
    #if fullyObserved is not None: default_params["fully_observed"] = bool(fullyObserved)
    if considerationDistanceFactor is not None: default_params["consideration_distance_factor"] = int(
        considerationDistanceFactor)




    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class InferenceModule(CaptureAgent):
    """
    An inference module tracks a belief distribution over a ghost's location.
    This is an abstract class, which you should not modify.
    """
    num_particles = None
    particles = None
    width = None
    height = None
    walls = None

    def registerInitialState(self, gameState):
        "Sets the ghost agent for later access"
        CaptureAgent.registerInitialState(self, gameState)
        #self.index = self.agent.index

        #InferenceModule.num_particles = None
        #InferenceModule.particles = []  # most recent observation position
        self.initialize(gameState)
        self.beliefDistributions = []

    def initialize(self, gameState):
        # "Initializes beliefs to a uniform distribution over all positions."
        # The legal positions do not include the ghost prison cells in the bottom left.
        if InferenceModule.num_particles is None:
            self.initializeParam(gameState)
            InferenceModule.particles = [None for _ in range(gameState.getNumAgents())]

            for index in self.getOpponents(gameState):
                self.initializeParticles(index)

    def initializeParam(self, gameState):
        """
        Initialize global parameters
        """
        InferenceModule.width = gameState.data.layout.width
        InferenceModule.height = gameState.data.layout.height
        InferenceModule.walls = gameState.getWalls()
        InferenceModule.num_particles = 3000

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


    ############################################
    # Useful methods for all inference modules #
    ############################################

    def setNumParticles(self, numParticles):
        InferenceModule.num_particles = numParticles

    def updateBeliefDistribution(self):
        self.beliefDistributions = [particle.copy() if particle is not None else None for particle in
        InferenceModule.particles]
        
        for particle in self.beliefDistributions: particle.normalize() if particle is not None else None



    # Get Particle Distributions
    def getParticlesDistributions(self):
        particles = util.Counter()

        sum = 0
        for x in range(1, InferenceModule.width - 1):
            for y in range(1, InferenceModule.height - 1):
                if not InferenceModule.walls[x][y]:
                    sum = sum + 1
        for x in range(1, InferenceModule.width - 1):
            for y in range(1, InferenceModule.height - 1):
                if not InferenceModule.walls[x][y]:
                    particles[(x, y)] = InferenceModule.num_particles/sum

        return particles

    # Set Particles For Each Opponent
    def initializeParticles(self, index):
        if self.red:
            count = 0

            for x in range(InferenceModule.width - 2, InferenceModule.width - 1):
                for y in range(InferenceModule.height/2, InferenceModule.height - 1):
                    if not InferenceModule.walls[x][y]:
                        count = count + 1

            InferenceModule.particles[index] = util.Counter()
            for x in range(InferenceModule.width - 2, InferenceModule.width - 1):
                for y in range(InferenceModule.height/2, InferenceModule.height - 1):
                    if not InferenceModule.walls[x][y]:
                        InferenceModule.particles[index][(x, y)] = InferenceModule.num_particles/count
        else:
            count = 0

            for x in range(1, 2):
                for y in range(1 / 2, InferenceModule.height/2):
                    if not InferenceModule.walls[x][y]:
                        count = count + 1

            InferenceModule.particles[index] = util.Counter()
            for x in range(InferenceModule.width - 2, InferenceModule.width - 1):
                for y in range(InferenceModule.height / 2, InferenceModule.height - 1):
                    if not InferenceModule.walls[x][y]:
                        InferenceModule.particles[index][(x, y)] = InferenceModule.num_particles / count

    def update(self, gameState, particle, sonar_distance, index):
        if index == self.index - 1 or (index == (self.index + gameState.getNumAgents() - 1)):
            temp_particles = util.Counter()
            #print(result)
            for position, value in particle.items():
                x, y = position
                candidates = [] # not enable stop
                if not InferenceModule.walls[x][y + 1]: 
                    candidates.append((x, y + 1))
                if not InferenceModule.walls[x][y - 1]: 
                    candidates.append((x, y - 1))
                if not InferenceModule.walls[x - 1][y]: 
                    candidates.append((x - 1, y))
                if not InferenceModule.walls[x + 1][y]: 
                    candidates.append((x + 1, y))
                for i in candidates:
                    temp_particles[i] = temp_particles[i] + value/len(candidates)
                remaining = value % len(candidates)
                #print(value, remaining)
                #print(remaining)
                for i in range(remaining):
                    # random choose a candidate
                    temp = random.choice(candidates)
                    temp_particles[temp] = temp_particles[temp] + 1
        else:
            temp_particles = particle
        agent_position = gameState.getAgentPosition(self.index)
        agentX, agentY = agent_position
        # Get agent Position
        new_particles = util.Counter()
        for position, value in temp_particles.items():
            x, y = position
            #print(position[0],position[1])
            dis = abs(agent_position[0] - position[0]) + abs(agent_position[1] - position[1])
            #distance = abs(agentX - x) + abs(agentY - y)
            prob = gameState.getDistanceProb(dis, sonar_distance) * value
            if prob > 0:
                new_particles[position] += prob

        if len(new_particles) > 0:
            result = util.Counter()
            for i in range(InferenceModule.num_particles):
                temp_pos = self.explore(new_particles)
                result[temp_pos] += 1
            return result
        else:
            #print("Lost Target")
            return self.getParticlesDistributions()    


    def explore(self, particles):
        total_value = 0.0

        weight = [particles[i] for i in particles]
        candidates = [i for i in particles]
        temp = random.uniform(0, sum(weight))
        for i in range(len(weight)):
            total_value = total_value + weight[i]
            if total_value >= temp:
                return candidates[i]
        #raise Exception("Could not reach there")

                    

    # Update Inference from the noisy distance
    def updateParticles(self, gameState):
        agentPosition = gameState.getAgentPosition(self.index)
        #position = gameState.getAgentPosition(self.index)
        enemies = self.getOpponents(gameState)

        for index in range(gameState.getNumAgents()):
            if index in enemies:
                sonar_distance = gameState.agentDistances[index]
                temp_particles = InferenceModule.particles[index]

                #flag = True
                if index == self.index - 1 or (index == (self.index + gameState.getNumAgents() - 1)):
                    flag = False
                else:
                    flag = True
                # self.log("Opponent Agent %d is %s" % (agentIndex, "STAY" if isStay else "MOVE"))
                #InferenceModule.particles[index] = update(temp_particles, sonar_distance, flag)
                InferenceModule.particles[index] = self.update(gameState, temp_particles, sonar_distance, index)



class TimeoutException(Exception):
    """A custom exception for truncating search."""
    pass


class ExpectimaxAgent(InferenceModule):

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
        self.initialize(gameState)
        self.beliefDistributions = []
        self.start = gameState.getAgentPosition(self.index)
        self.maxDepth = default_params["max_depth"]
        self.maxInferencePositionCount = default_params["max_position"]
        #PositionInferenceAgent.isFullyObserved = default_params["fully_observed"]
        #self.initPositionInference(gameState)

        #self.width = gameState.data.layout.width
        #self.height = gameState.data.layout.height
        #self.walls = gameState.getWalls()


        #self.model = InferenceModule(self, gameState)
        #self.model.__init__(self, gameState)
        #self.model.__init__(self, gameState)
        #self.beliefDistributions = []

    # choose the best action and update global variables
    def chooseAction(self, gameState):
        #print ("Agent %d:" % (self.index,))
        self.record = {"START": time.time()}
        #action = self.takeAction(gameState)
    
        self.record["BEFORE_POSITION_INFERENCE"] = time.time()
        self.updateParticles(gameState)
        #self.checkPositionInference(gameState)
        for index in range(gameState.getNumAgents()):
            if index in self.getOpponents(gameState):  # postion of teammates are always available
                # Eating an enemy, reinitialize the particles
                if self.getPreviousObservation() is not None:
                    if self.getPreviousObservation().getAgentPosition(index) is not None:
                        prev_position =  self.getPreviousObservation().getAgentPosition(index)
                        if prev_position == gameState.getAgentPosition(self.index):
                            self.initializeParticles(index)

                # Opponent is insight
                position = gameState.getAgentPosition(index)
                if position is not None:
                    InferenceModule.particles[index] = util.Counter()
                    InferenceModule.particles[index][position] = InferenceModule.num_particles


        # Update global belief distributions
        self.updateBeliefDistribution()

        # #print distributions
        self.displayDistributionsOverPositions(self.beliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.record["AFTER_POISITION_INFERENCE"] = time.time()

        # select action with highest Q value
        # bestAction = self.selectAction(gameState)
        # foodLeft = len(self.getFood(gameState).asList())
        best_action = None
        if len(self.getFood(gameState).asList()) <= 2:
            best_distance = 9999
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                temp_distance = self.getMazeDistance(self.start, successor.getAgentPosition(self.index))
                if temp_distance < best_distance:
                    best_action = action
                    best_distance = temp_distance
            #return bestAction
        else:
            #self.record["BEFORE_REFLEX"] = time.time()
            #bestAction = self.pickAction(gameState)
            self.record["BEFORE_SEARCH"] = time.time()
            best_score, best_action = self.searchTop(gameState)
            self.record["AFTER_SEARCH"] = time.time()

            #self.record["AFTER_REFLEX"] = time.time()

        self.record["END"] = time.time()
        self.#printTimes()
        return best_action

    def selectAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        foodLeft = len(self.getFood(gameState).asList())
        best_action = None
        if foodLeft <= 2:
            best_distance = 9999
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, self.index, action)
                #pos2 = successor.getAgentPosition(self.index)
                temp_distance = self.getMazeDistance(self.start, successor.getAgentPosition(self.index))
                if temp_distance < best_distance:
                    best_action = action
                    best_distance = temp_distance
        else:
            #bestAction = self.pickAction(gameState)
            self.record["BEFORE_SEARCH"] = time.time()
            best_score, best_action = self.searchTop(gameState)
            self.record["AFTER_SEARCH"] = time.time()

        return best_action



    def evaluate(self, gameState, agent_index, action):
        """
          Should return heuristic(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.getFeatures(gameState, agent_index, action)
        weights  = self.getWeights(gameState, agent_index, action)

        sum = 0.0
        for feature, value in features.iteritems():
            sum += weights[feature] * value
        return sum

 
    # recursive simulate the game process and use alpha-beta pruning
    # Expectimax with Alpha-Beta Pruning
    def getValue(self, gameState, index, searchAgentIndices, depth, alpha=float("-inf"), beta=float("inf")):
        actions = gameState.getLegalActions(index)
        best_score = None
        best_action = None

        if index in self.getTeam(gameState):
            best_score = float("-inf")
        else:
            best_score = float("inf")

        if gameState.isOver():
            #result = self.searchWhenGameOver(gameState)
            best_score = self.evaluate(gameState, self.index, Directions.STOP)
            best_action = Directions.STOP
            result = (best_score, best_action)
        # When search start
        elif depth == 0:
            #result = self.searchWhenZeroDepth(gameState, index)
            assert  index == self.index # can be deleted
            #legalActions = gameState.getLegalActions(index)
            actions.remove(Directions.STOP)  # STOP is not allowed, to avoid the problem of discontinuous evaluation function
            for action in actions:
                value = self.evaluate(gameState, index, action)
                if (index in self.getTeam(gameState) and value > best_score) \
                        or (not index in self.getTeam(gameState) and value < best_score):
                    best_score = value
                    best_action = action
            result = (best_score, best_action)
        else:
        # Recursively search the state tree
        # Time resource is consumed
            # self.timeRemain()
            # Check time left
            self.checkTime()

            next_agent, next_depth = self.getNextSearchableAgentIndexAndDepth(gameState, searchAgentIndices,index,depth)
            """
            next_agent = index
            next_depth = depth
            while True:
                next_agent = self.getNextAgentIndex(gameState, next_agent)
                if next_agent == self.index:
                    next_depth = next_depth - 1 
                if next_agent in searchAgentIndices: 
                    break
            """

            best_action = None
            if index == self.index:  # no team work, is better
                best_score = float("-inf")
                possible_actions = gameState.getLegalActions(index)
                if not default_params["enable_stop_action"]:
                    possible_actions.remove(Directions.STOP)  # STOP is not allowed
                for action in possible_actions:
                    successor = gameState.generateSuccessor(index, action)
                    new_alpha = self.getValue(successor, next_agent, searchAgentIndices, next_depth, alpha,
                                                beta)[0]
                    # currentReward = self.getQValue(gameState, index, action) if default_params["eval_total_reward"] else 0
                    # newAlpha += currentReward
                    if new_alpha > best_score:
                        best_score = new_alpha
                        best_action = action
                    # update alpha
                    if new_alpha > alpha: 
                        alpha = new_alpha
                    if alpha >= beta: 
                        break
            else:
                best_score = float("inf")
                for action in gameState.getLegalActions(index):
                    successor = gameState.generateSuccessor(index, action)
                    new_beta = self.getValue(successor, next_agent, searchAgentIndices, next_depth, alpha, beta)[0]
                    if new_beta < best_score:
                        best_score = new_beta
                        best_action = action
                    # update beta
                    if new_beta < beta: 
                        beta = new_beta
                    if alpha >= beta: 
                        break
            #best_score,best_action = self.searchWhenNonTerminated(gameState, index, searchAgentIndices, depth, alpha, beta)

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
                    #print("Take agents %s in to consideration" % searchAgentIndices)
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
                #print("Failed when search max depth [%d]" % (searchDepth,))
                break
        #print("Take action [%s] with evaluation [%.6f]" % (bestAction, bestValue))
        return bestValue, bestAction

    #########
    # utils #
    #########

    def checkTime(self):
        if self.timeLeft() < 0.1:
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

    def timeConsumed(self):
        return time.time() - self.record["START"]

    def timeLeft(self):
        return self.actionTimeLimit - self.timeConsumed()

    def timePast(self):
        return time.time() - self.record["START"]

    def timePastPercent(self):
        return self.timePast() / self.actionTimeLimit

    def timeRemain(self):
        return self.actionTimeLimit - self.timePast()

    def timeRemainPercent(self):
        return self.timeRemain() / self.actionTimeLimit
    
    def ifTimeoutRaiseTimeoutException(self):
        if self.timeRemainPercent() < default_params["truncate_remain_time_percent"]:
            raise TimeoutException()

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
        #print(prefix + str(relativeTimeList))

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


class OffensiveReflexAgent(ReflexCaptureAgent):
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

