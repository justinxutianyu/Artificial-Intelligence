from captureAgents import AgentFactory
from captureAgents import CaptureAgent
#from distanceCalculator import manhattanDistance
from game import Directions, Actions
from util import Counter
from util import nearestPoint
import distanceCalculator

import capture
import distanceCalculator
import game
import keyboardAgents
import random, time, util





class PacManiaSearchAgentsv1(AgentFactory):
    '''
    Create the new PacManiaSearchAgents
    '''

    def __init__(self, isRed, first='offence', second = 'defence', rest = 'offence'):
        AgentFactory.__init__(self, isRed)
        self.agents = [first, second]
        self.rest = rest

    def getAgent(self, index):

        # index = index/2
        # if (index == 0):
        #     self.choose('offence', index)
        # elif (index == 1):
        #     self.choose('defence', index)
        # else:
        #     self.choose('offence', index)
         if len(self.agents) > 0:
             return self.choose(self.agents.pop(0), index)
         else:
             return self.choose(self.rest, index)

    def choose(self, agentStr, index): 

        if agentStr == 'keys':
             global NUM_KEYBOARD_AGENTS
             NUM_KEYBOARD_AGENTS += 1
             if NUM_KEYBOARD_AGENTS == 1:
                 return keyboardAgents.KeyboardAgent(index)
             elif NUM_KEYBOARD_AGENTS == 2:
                 return keyboardAgents.KeyboardAgent2(index)
             else:
                 raise Exception('Max of two keyboard agents supported')
        elif agentStr == 'offence' or agentStr == 'offense':
            return OffensiveSearchAgent(index)
        elif agentStr == 'defence' or agentStr == 'defense':
            return DefensiveSearchAgent(index)
        else:

            raise Exception("No PacMania agent identified by " + agentStr)


class MetriculatedSearchAgent(CaptureAgent):
    '''
    Defines the basic agent and the metrics it assesses when deciding on a course
    of action. Some of the code is copied from the provided BaselineAgents code.
    '''
    nextZone = 0

    def __init__(self, index):
        CaptureAgent.__init__(self, index)
        self.zone = MetriculatedSearchAgent.nextZone
        self.firstMove = True
        MetriculatedSearchAgent.nextZone += 1
        #self.distancer = distanceCalculator.Distancer(gameState.data.layout)
        #self.distancer.getMazeDistances()


    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.distancer = distanceCalculator.Distancer(gameState.data.layout)
        self.distancer.getMazeDistances()



    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        
        if self.firstMove:
            self.firstMove = False
            return Directions.STOP

        actions = gameState.getLegalActions(self.index)
        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]

        maxValue = max(values)

        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)
    # end def


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
    # end def

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of metrics and metric weights
        """
        metrics = self.getMetrics(gameState, action)
        weights = self.getWeights(gameState, action)

        #for k in metrics.keys():



        return metrics * weights
    # end def

    def getMetrics(self, gameState, action):
        """
        Returns a counter of metrics for the state
        """
        metrics = util.Counter()
        successor = self.getSuccessor(gameState, action)
        x, y = gameState.getAgentState(self.index).getPosition()
        dx, dy = Actions.directionToVector(action)
        nextX, nextY = int(x + dx), int(y + dy)

        # Query the state
        isPacman = successor.getAgentState(self.index).isPacman
        foods = self.getFood(gameState)
        capsules = self.getCapsules(gameState)
        grid = gameState.getWalls()

        theirs = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        theirGhosts = [ghost for ghost in theirs if not ghost.isPacman and ghost.getPosition() != None ]
        theirPacmans = [pacman for pacman in theirs if pacman.isPacman and pacman.getPosition() != None ]

        # Ghost metrics
        if not isPacman:
            # Find distance to nearest seen pacman
            distanceToPacmans = [self.getMazeDistance((nextX, nextY), p.getPosition()) for p in theirGhosts if not p.getPosition() == None]
            closestPacman = min(distanceToPacmans + [6])
            # Can we eat it?
            if distanceToPacmans != None:
                if successor.getAgentState(self.index).scaredTimer == 0:

                    metrics['seen-edible-pacman'] = max(0, 6 - closestPacman)
                else:
                    metrics['seen-scary-pacman'] = 1 * closestPacman
                # TODO(bpstudds): What about potential pacmans?
        # end if


        # Pacman metrics
        if isPacman:
            for ghost in theirGhosts:
                twomoves = Actions.getLegalNeighbors(ghost.getPosition(), gameState.getWalls())
                twomovesNew = []
                twomovesNew.extend(twomoves)
                for pos in twomoves:
                    twomovesNew.extend(Actions.getLegalNeighbors(pos, gameState.getWalls()))
                twomoves.extend(twomovesNew)

                # Pacman has run into a ghost
                if (nextX, nextY) == ghost.getPosition():

                    if ghost.scaredTimer <= 0:

                        metrics['collide-scary-ghosts'] += 1
                        metrics['collide-edible-ghosts'] = 0
                    else:

                        metrics['collide-edible-ghosts'] += 1
                # Pacman would be adjacent to a ghost
                #elif (nextX, nextY) in Actions.getLegalNeighbors(ghost.getPosition(), gameState.getWalls()):
                elif (nextX, nextY) in twomoves:

                    if ghost.scaredTimer == 0:
                        metrics['adjacent-scary-ghosts'] += 1
                        metrics['adjacent-edible-ghosts'] = 0
                    else:

                        metrics['adjacent-edible-ghosts'] += 1

        # Go for food if we aren't close to an enemy
        if not metrics['adjacent-scary-ghosts'] and not metrics['collide-scary-ghosts']:
            if foods[nextX][nextY]:
                metrics['eats-fud'] = 1
                metrics['find-a-fud'] = 0
            else:
                # split food up according to horizontal zones
                thisFoods = []
                for food in foods.asList():
                    x, y = food
                    if y > self.zone*grid.height/2 and y < (self.zone+1)*grid.height / 2:
                        thisFoods.append(food)
                if len(thisFoods) == 0:
                    thisFoods = foods.asList()
                minFoodDist = min([self.getMazeDistance((nextX,nextY), food) for food in thisFoods])
                #metrics['find-a-fud'] = max(1, 100 - minFoodDist) # 10 chosen by fair dice roll
                metrics['find-a-fud'] = 1 - (float(minFoodDist) / float(grid.width * grid.height))

        # TODO this is a hack to prevent things from not moving....
        if (dx == dy):
            metrics['find-a-fud'] = 0.0

        return metrics
    # end def


    def getWeights(self, gameState, action):
        """
        Weights assigned to the metrics of successor state. These weights are
        assigned in the OffensiveSearchAgent and DefensiveSearchAgent.
        """
        return {
            'seen-edible-pacman': 2.0,
            'seen-scary-pacman': -5.0,
            'collide-scary-ghosts': 1.0,
            'collide-edible-ghosts': 5.0,
            'adjacent-scary-ghosts': -10.0,
            'adjacent-edible-ghosts': 2.0,
            'eats-fud': 2.0,
            'find-a-fud': 1.0
        }
    # end def


class OffensiveSearchAgent(MetriculatedSearchAgent):
    '''
    Search agent that takes an offensive attitude
    '''
    def __init__(self, index):
        MetriculatedSearchAgent.__init__(self, index)
# end class


class DefensiveSearchAgent(MetriculatedSearchAgent):
    '''
    Search agent that takes a defensive attitude
    '''
    def __init__(self, index):
        MetriculatedSearchAgent.__init__(self, index)
# end class
