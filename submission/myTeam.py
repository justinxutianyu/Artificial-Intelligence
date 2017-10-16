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
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed, first='RandomOffensiveAgent', second='RandomDefensiveAgent'
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

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

"""
class QLearningAgent(CaptureAgent):
    
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    
    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)

        self.values = util.Counter()


    def getQValue(self, state, action):
        
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
    
        return self.values[(state, action)]


    def computeValueFromQValues(self, state):
        
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        
        maxQ = float('-inf')
        for action in self.getLegalActions(state):
            maxQ = max(maxQ, self.getQValue(state, action))
        return maxQ if maxQ != float('-inf') else 0.0


    def computeActionFromQValues(self, state):
        
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        
        if len(self.getLegalActions(state)) == 0:
            return None

        bestQ = self.computeValueFromQValues(state)
        bestActions = []
        for action in self.getLegalActions(state):
            if bestQ == self.getQValue(state, action):
                bestActions.append(action)

        return random.choice(bestActions)


    def getAction(self, state):
        
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        
        # Pick Action
        legalActions = self.getLegalActions(state)
        action = None

        if util.flipCoin(self.epsilon):
            action = random.choice(legalActions)
        else:
            action = self.computeActionFromQValues(state)

        return action

    def update(self, state, action, nextState, reward):
        
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        
        oldValue = self.values[(state, action)]
        newValue = reward + (self.discount * self.computeValueFromQValues(nextState))

        self.values[(state, action)] = (1 - self.alpha) * oldValue + self.alpha * newValue


    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)
"""

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
    
    # Utility Functions

    def isPacman(self, gameState, index):
        return gameState.getAgentState(index).isPacman

    def isGhost(self, gameState, index):
        return not self.isPacman(gameState, index)

    def isScared(self, gameState, index):
        return gameState.data.agentStates[index].scaredTimer > 0
    
    def isInvader(self, gameState, index):
        return index in self.getOpponents(gameState) and self.isPacman(gameState, index)

    def isHarmfulInvader(self, gameState, index):
        return self.isInvader(gameState, index) and self.isScared(gameState, self.index)

    def isHarmlessInvader(self, gameState, index):
        return self.isInvader(gameState, index) and not self.isScared(gameState, self.index)
    
    def isHarmfulGhost(self, gameState, index):
        return self.index in self.getOpponents(gameState) and self.isGhost(gameState, index) and not self.isScared(gameState, index)

    def isHarmlessGhost(self, gameState, index):
        return index in self.getOpponents(gameState) and self.isGhost(gameState) and self.isScared(gameState, index)

class ParticleFilter(InferenceModule):
    """
    A particle filter for approximately tracking a single ghost.

    Useful helper functions will include random.choice, which chooses an element
    from a list uniformly at random, and util.sample, which samples a key from a
    Counter by treating its values as probabilities.
    """

    def __init__(self, ghostAgent, numParticles=300):
        InferenceModule.__init__(self, ghostAgent);
        self.setNumParticles(numParticles)

    def setNumParticles(self, numParticles):
        self.numParticles = numParticles

    def initializeUniformly(self, gameState):
        """
        Initializes a list of particles. Use self.numParticles for the number of
        particles. Use self.legalPositions for the legal board positions where a
        particle could be located.  Particles should be evenly (not randomly)
        distributed across positions in order to ensure a uniform prior.

        Note: the variable you store your particles in must be a list; a list is
        simply a collection of unweighted variables (positions in this case).
        Storing your particles as a Counter (where there could be an associated
        weight with each position) is incorrect and may produce errors.
        """
        self.beliefs = util.Counter()
        self.l = []
        self.particles = [random.choice(self.legalPositions) for i in range(self.numParticles)]

    def observe(self, observation, gameState):
        """
        Update beliefs based on the given distance observation. Make sure to
        handle the special case where all particles have weight 0 after
        reweighting based on observation. If this happens, resample particles
        uniformly at random from the set of legal positions
        (self.legalPositions).

        A correct implementation will handle two special cases:
          1) When a ghost is captured by Pacman, all particles should be updated
             so that the ghost appears in its prison cell,
             self.getJailPosition()

             As before, you can check if a ghost has been captured by Pacman by
             checking if it has a noisyDistance of None.

          2) When all particles receive 0 weight, they should be recreated from
             the prior distribution by calling initializeUniformly. The total
             weight for a belief distribution can be found by calling totalCount
             on a Counter object

        util.sample(Counter object) is a helper method to generate a sample from
        a belief distribution.

        You may also want to use util.manhattanDistance to calculate the
        distance between a particle and Pacman's position.
        """
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        beliefs = util.Counter()
        if noisyDistance == None:
            self.particles = [self.getJailPosition() for i in range(self.numParticles)]
        else:
            for particle in self.particles:
                beliefs[particle] += emissionModel[util.manhattanDistance(particle, pacmanPosition)]
        if beliefs.totalCount() != 0:
            self.particles = [util.sample(beliefs) for i in range(self.numParticles)]
        else:
            self.initializeUniformly(gameState)

    def elapseTime(self, gameState):
        """
        Update beliefs for a time step elapsing.

        As in the elapseTime method of ExactInference, you should use:

          newPosDist = self.getPositionDistribution(self.setGhostPosition(gameState, oldPos))

        to obtain the distribution over new positions for the ghost, given its
        previous position (oldPos) as well as Pacman's current position.

        util.sample(Counter object) is a helper method to generate a sample from
        a belief distribution.
        """
        self.l = [util.sample(self.getPositionDistribution(self.setGhostPosition(gameState, particle))) for particle in
                  self.l]
        for i in self.l:
            self.beliefs[i] += 1
            self.beliefs.normalize()

    def getBeliefDistribution(self):
        """
        Return the agent's current belief state, a distribution over ghost
        locations conditioned on all evidence and time passage. This method
        essentially converts a list of particles into a belief distribution (a
        Counter object)
        """
        # return self.beliefs
        # util.raiseNotDefined()
        dist = util.Counter()
        for part in self.particles:
            dist[part] += 1
        dist.normalize()
        return dist

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
        InferenceModule.registerInitialState(self, gameState)

        # Set the traverse action time limit to ensure each action is chosen within 1 second 
        self.actionTimeLimit = 0.8 
        self.initialize(gameState)
        self.beliefDistributions = []
        self.start = gameState.getAgentPosition(self.index)
        self.maxDepth = 4 # Set the traverse max depth
        self.maxInferencePositionCount = 1 # Set the max inference position


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

        # print distributions
        #self.displayDistributionsOverPositions(self.beliefDistributions)
        self.getCurrentAgentPostions(self.getTeam(gameState)[0])
        self.record["AFTER_POISITION_INFERENCE"] = time.time()

        # select action with highest heuristic value
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
            self.record["BEFORE_Traverse"] = time.time()
            best_action = self.traverse(gameState)
            self.record["AFTER_Traverse"] = time.time()
            #self.record["AFTER_REFLEX"] = time.time()

        self.record["END"] = time.time()
        #self.printTimes()
        return best_action


    def evaluate(self, gameState, index, action):
        """
          Should return heuristic(state,action) = w * featureVector
        """
        features = self.getFeatures(gameState, index, action)
        weights  = self.getWeights(gameState, index, action)
 
        return features * weights

 
    # recursive simulate the game process and use alpha-beta pruning
    # Expectimax with Alpha-Beta Pruning
    def simulateGame(self, gameState, index, searchAgentIndices, depth, alpha=float("-inf"), beta=float("inf")):
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

            #next_agent, next_depth = self.getNextSearchableAgentIndexAndDepth(gameState, searchAgentIndices,index,depth)
            
            next_agent = index
            next_depth = depth
            while True:
                #next_agent = self.getNextAgentIndex(gameState, next_agent)
                next_agent = next_agent + 1
                if next_agent >= gameState.getNumAgents():
                    next_agent = 0 

                if next_agent == self.index:
                    next_depth = next_depth - 1 
                if next_agent in searchAgentIndices: 
                    break
            

            best_action = None
            if index == self.index:  # no team work, is better
                best_score = float("-inf")
                possible_actions = gameState.getLegalActions(index)
                # Here we remove the stop action
                possible_actions.remove(Directions.STOP)  # STOP is not allowed
                for action in possible_actions:
                    successor = gameState.generateSuccessor(index, action)
                    new_alpha = self.simulateGame(successor, next_agent, searchAgentIndices, next_depth, alpha,
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
                    new_beta = self.simulateGame(successor, next_agent, searchAgentIndices, next_depth, alpha, beta)[0]
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

    def backwardTrace():
        new_index = None
        minimum = 9999
        for index in range(gameState.getNumAgents()):
            if pointers[index] + 1 < upLimits[index] and pointers[index] < minimum:
                minPointer = pointers[index]
                new_index = index
        if new_index is not None:
            pointers[new_index] += 1
            return True
        else:
            return False

    def getNearAgents(self, gameState, position, max_distance):
        near_agents = []

        for index in range(gameState.getNumAgents()):
            agentPosition = gameState.getAgentPosition(index)
            #if gameState.getAgentPosition(index) is not None and self.manhattanDistance(agentPosition, position) <= max_distance:           
            if gameState.getAgentPosition(index) is not None and self.getMazeDistance(agentPosition, position) <= max_distance:
                near_agents.append(index)

        return near_agents


    def getAgentPossibility(self, origin, inference, possibility_distributions, pointers):
        agent_possibility = 1.0

        for index in range(origin.getNumAgents()):
            if origin.getAgentState(index).configuration is None:
                temp = possibility_distributions[index][pointers[index]]
                prob = temp[1]
                inference.data.agentStates[index].configuration = game.Configuration(temp[0], Directions.STOP)
            else:
                prob = 1.0
            agent_possibility = agent_possibility * prob
        return agent_possibility


    def traverse(self, gameState):
        inferenceState = gameState.deepCopy()
        legalActions = gameState.getLegalActions(self.index)
        possibility_distributions = [self.getPositionBeliefs(agentIndex) for agentIndex in range(gameState.getNumAgents())]
        agentInferencePositions = [self.getCurrentAgentPostions(agentIndex) for agentIndex in range(gameState.getNumAgents())]
        init_tree = [0 for _ in range(gameState.getNumAgents())]
        search_tree = None
        upLimits = [min(self.maxInferencePositionCount, len(possibility_distributions[agentIndex])) for agentIndex in range(gameState.getNumAgents())]
        myPosition = inferenceState.getAgentPosition(self.index)
        
        best_action = None
        best_score = float("-inf")
        for searchDepth in range(self.maxDepth + 1):
            flag = False
            temp_score = None
            temp_action = None
            try:
                expected_value = 0.0
                possibility = 1.0
                candidates = []
                # Consider the distance effect
                traverse_distance = int(searchDepth * 2.0)
                # print(traverse_distance)
                search_tree = init_tree
                while True:
                    # get possibility and get newar agents
                    prob = self.getAgentPossibility(gameState, inferenceState, possibility_distributions, search_tree)
                    searchAgentIndices = self.getNearAgents(inferenceState, myPosition, traverse_distance)

                    
                    # update the current best value
                    temp_result = self.simulateGame(inferenceState, self.index, searchAgentIndices, searchDepth)
                    #candidates.append([value, action])
                    candidates.append(temp_result)
                    possibility = possibility * prob
                    expected_value = expected_value +  prob * temp_result[0]
                    
                    # update the index list
                    #if not changePointer(): 
                    min_index = None
                    min_value = 9999
                    for index in range(gameState.getNumAgents()):
                        if search_tree[index] + 1 < upLimits[index] and search_tree[index] < min_value:
                            min_value = search_tree[index]
                            min_index = index
                    if min_index is not None:
                        search_tree[min_index] += 1
                    else:
                        break

                expected_value = expected_value / possibility
                min_regret = float("inf")
                for value, action in candidates:
                    temp = abs(value - expected_value)
                    if temp < min_regret:
                        min_regret = temp
                        temp_action = action
                        temp_score = value
                flag = True
            except TimeoutException:
                pass
            # except multiprocessing.TimeoutError: pass  # Coment this line if you want to use keyboard interrupt
            # if complete the search 
            if flag:
                best_score = temp_score
                best_action = temp_action
            else:
                break
        return best_action


    ##############
    # interfaces #
    ##############

    def timeConsumed(self):
        return time.time() - self.record["START"]

    def timeLeft(self):
        return self.actionTimeLimit - self.timeConsumed()

    def checkTime(self):
        if self.timeLeft() < 0.1:
            raise TimeoutException()
    
    def getFeatures(self, gameState, index, action):
        util.raiseNotDefined()

    def getWeights(self, gameState, index, action):
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

    def getPositionBeliefs(self, agentIndex):
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
        result = self.getPositionBeliefs(agentIndex)
        result = [i[0] for i in result]
        return result

    def getCurrentMostLikelyPosition(self, agentIndex):
        return self.getCurrentAgentPostions(agentIndex)[0]


class RandomOffensiveAgent(ExpectimaxAgent):
    """
    Offensive Agent Class for offensive which overlaod getFeatures() and getWeights()
    to calculate the heuristic value of current gamestate
    """

    def getFeatures(self, gameState, actionAgentIndex, action):
        #assert actionAgentIndex == self.index
        features = util.Counter()

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

        # Used for normalizing the MazeDistance 
        map_size = InferenceModule.height * InferenceModule.width
        
        
        if stopped:
            features["stopped"] = 1 
        else:
            features["stopped"] = 0

        if reversed:
            features["reversed"] = 1
        else:
            features["reversed"] = 0

        if self.isScared(successor, self.index):
            features["scared"] = 1
        else:
            features["scared"] = 0

        features["food_returned"] = successor.getAgentState(self.index).numReturned

        features["food_carrying"] = successor.getAgentState(self.index).numCarrying

        features["food_defend"] = len(defendFoodList)

        if len(foodList) > 0:
            features["nearest_food_distance_factor"] = float(self.getMazeDistance(position, foodList[0]))/map_size
        else:
            features["nearest_food_distance_factor"] = 0


        if len(capsulesList) > 0:
            features["nearest_capsules_distance_factor"] = \
                float(self.getMazeDistance(position, capsulesList[0]))/map_size
        else:
            features["nearest_capsules_distance_factor"] = 0


        if self.red:
            central_position = InferenceModule.width/2 - 1
        else:
            central_position = InferenceModule.width/2



        closest_return_distance = 9999
        for i in range(InferenceModule.height):
            if not InferenceModule.walls[central_position][i]:
                temp_distance = float(self.getMazeDistance(position, (central_position, i)))
                if temp_distance < closest_return_distance:
                    closest_return_distance = temp_distance

        features["return_food_factor"] = closest_return_distance/map_size * features["food_carrying"]

        # check the opponents situation
        peace_invaders = []
        evil_invaders = []
        peace_ghosts = []
        evil_ghosts = []
        for opponent in self.getOpponents(successor):
            if self.isPacman(successor, opponent) and not self.isScared(successor, self.index):
                peace_invaders.append(opponent)
            if self.isPacman(successor, opponent) and self.isScared(successor, self.index):
                evil_invaders.append(opponent)
            if self.isGhost(successor, opponent) and self.isScared(successor, opponent):
                peace_ghosts.append(opponent)
            if self.isHarmfulGhost(successor, opponent) and not self.isScared(successor, opponent):
                evil_ghosts.append(opponent)


        if len(peace_invaders) > 0:
            peace_invaders_factor = 9999
            for invader in peace_invaders:
                temp_distance = self.getMazeDistance(position, successor.getAgentPosition(invader))
                temp_food = successor.getAgentState(invader).numCarrying + 5
                temp_factor = float(temp_distance)/map_size * temp_food
                if temp_factor < peace_invaders_factor:
                    peace_invaders_factor = temp_factor

            features["harmless_invader_distance_factor"] = peace_invaders_factor
        else:
            features["harmless_invader_distance_factor"] = 0


        if len(evil_invaders) > 0:
            evil_invaders_factor = 9999
            for invader in evil_invaders:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(invader)))/map_size
                if temp_distance < evil_invaders_factor:
                    evil_invaders_factor = temp_distance
            features["harmful_invader_distance_factor"] = evil_invaders_factor
        else:
            features["harmful_invader_distance_factor"] = 0


        if len(peace_ghosts) > 0:
            ghosts_factor = 9999
            for ghost in peace_ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance < ghosts_factor:
                    ghosts_factor = temp_distance
            features["harmless_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmless_ghost_distance_factor"] = 0

        # add new features
        #features["harmful_ghost_distance_factor"] = min(
        #    [getPositionFactor(getDistance(getPosition(successor, i))) for i in harmful_ghost]) if len(
        #    harmful_ghost) > 0 else 0
        if len(evil_ghosts) > 0:
            ghosts_factor = 9999
            for ghost in evil_ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance < ghosts_factor:
                    ghosts_factor = temp_distance
            features["harmful_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmful_ghost_distance_factor"] = 0


        return features


    def getWeights(self, gameState, actionAgentIndex, action):
        return {
            "stopped": -2.0,"reversed": -1.0,"scared": -2.0,"food_returned": 10.0,"food_carrying": 8.0,"food_defend": 0.0,"nearest_food_distance_factor": -1.0,
            "nearest_capsules_distance_factor": -1.0, "return_food_factor": -0.5, # 1.5# "team_distance": 0.5,
            "harmless_invader_distance_factor": -0.1,
            "harmful_invader_distance_factor": 0.1,
            "harmless_ghost_distance_factor": -0.2,
            "harmful_ghost_distance_factor": 1.5, # harmful ghost
        }

"""
Defensive functions, overload the features and weights
Paying more attension to defense (higher food defend weights)
"""
class RandomDefensiveAgent(ExpectimaxAgent):



    def getFeatures(self, gameState, actionAgentIndex, action):
        #assert actionAgentIndex == self.index

        features = util.Counter()

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
        map_size = InferenceModule.height * InferenceModule.width


        if action == Directions.STOP:
                features["stopped"] = 1 
        else:
            features["stopped"] = 0


        if reversed:
            features["reversed"] = 1
        else:
            features["reversed"] = 0

        if self.isScared(successor, self.index):
            features["scared"] = 1
        else:
            features["scared"] = 0

        features["food_returned"] = successor.getAgentState(self.index).numReturned

        features["food_carrying"] = successor.getAgentState(self.index).numCarrying

        features["food_defend"] = len(defendFoodList)

        if len(foodList) > 0:
            features["nearest_food_distance_factor"] = float(self.getMazeDistance(position, foodList[0]))/map_size
        else:
            features["nearest_food_distance_factor"] = 0


        if len(capsulesList) > 0:
            features["nearest_capsules_distance_factor"] = \
                float(self.getMazeDistance(position, capsulesList[0]))/map_size
        else:
            features["nearest_capsules_distance_factor"] = 0


        if self.red:
            central_position = InferenceModule.width/2 - 1
        else:
            central_position = InferenceModule.width/2

        #features["team_distance"] = float([self.getMazeDistance(position, successor.getAgentPosition(i)) 
        #for i in teamIndices if i != self.index]) / map_size


        closest_return_distance = 9999
        for i in range(InferenceModule.height):
            if not InferenceModule.walls[central_position][i]:
                temp_distance = float(self.getMazeDistance(position, (central_position, i)))
                if temp_distance < closest_return_distance:
                    closest_return_distance = temp_distance

        features["return_food_factor"] = closest_return_distance/map_size * features["food_carrying"]

        # check the opponents situation
        peace_invaders = []
        evil_invaders = []
        peace_ghosts = []
        evil_ghosts = []
        for opponent in self.getOpponents(successor):
            if self.isPacman(successor, opponent) and not self.isScared(successor, self.index):
                peace_invaders.append(opponent)
            if self.isPacman(successor, opponent) and self.isScared(successor, self.index):
                evil_invaders.append(opponent)
            if self.isGhost(successor, opponent) and self.isScared(successor, opponent):
                peace_ghosts.append(opponent)
            if self.isHarmfulGhost(successor, opponent) and not self.isScared(successor, opponent):
                evil_ghosts.append(opponent)


        if len(peace_invaders) > 0:
            peace_invaders_factor = 9999
            for invader in peace_invaders:
                temp_distance = self.getMazeDistance(position, successor.getAgentPosition(invader))
                temp_food = successor.getAgentState(invader).numCarrying + 5
                temp_factor = float(temp_distance)/map_size * temp_food
                if temp_factor < peace_invaders_factor:
                    peace_invaders_factor = temp_factor

            features["harmless_invader_distance_factor"] = peace_invaders_factor
        else:
            features["harmless_invader_distance_factor"] = 0


        if len(evil_invaders) > 0:
            evil_invaders_factor = 9999
            for invader in evil_invaders:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(invader)))/map_size
                if temp_distance < evil_invaders_factor:
                    evil_invaders_factor = temp_distance
            features["harmful_invader_distance_factor"] = evil_invaders_factor
        else:
            features["harmful_invader_distance_factor"] = 0


        if len(peace_ghosts) > 0:
            ghosts_factor = 9999
            for ghost in peace_ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance < ghosts_factor:
                    ghosts_factor = temp_distance
            features["harmless_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmless_ghost_distance_factor"] = 0

        # add new features
        if len(evil_ghosts) > 0:
            ghosts_factor = 9999
            for ghost in evil_ghosts:
                temp_distance = float(self.getMazeDistance(position, successor.getAgentPosition(ghost)))/map_size
                if temp_distance < ghosts_factor:
                    ghosts_factor = temp_distance
            features["harmful_ghost_distance_factor"] = ghosts_factor
        else:
            features["harmful_ghost_distance_factor"] = 0


        return features
            

    def getWeights(self, gameState, actionAgentIndex, action):
        return {
            "stopped": -2.0, "reversed": -1.0, "scared": -2.0, "food_returned": 1.0, "food_carrying": 0.5,"food_defend": 5.0,
            "nearest_food_distance_factor": -1.0, "nearest_capsules_distance_factor": -1.0,
            "return_food_factor": 1.5, "team_distance": 0.1, 
            "harmless_invader_distance_factor": -3.0, # -1.0
            "harmful_invader_distance_factor": 4.0,
            "harmless_ghost_distance_factor": -2.0,
            "harmful_ghost_distance_factor": -4.0 # harmful ghost
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



"""
class ApproximateQAgent(PacmanQAgent):

       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    
    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        
        features = self.featExtractor.getFeatures(state, action)

        sum = 0
        for feature, value in features.iteritems():
            sum += self.weights[feature] * value
        return sum

    def update(self, state, action, nextState, reward):
        
           Should update your weights based on transition
        
        newValue = reward + self.discount * self.computeValueFromQValues(nextState)
        oldValue = self.getQValue(state, action)
        difference = newValue - oldValue

        features = self.featExtractor.getFeatures(state, action)
        for feature, value in features.iteritems():
          self.weights[feature] += self.alpha * difference * features[feature]

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"
            pass
"""