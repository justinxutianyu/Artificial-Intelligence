from captureAgents import AgentFactory
from captureAgents import CaptureAgent
#from distanceCalculator import manhattanDistance
from game import Directions, Actions
from util import Counter
from util import nearestPoint
from sets import Set
import distanceCalculator

import capture
import distanceCalculator
import game
import keyboardAgents
import random, time, util, math
import search
import searchAgents


NUM_KEYBOARD_AGENTS = 0

LOG_MODE = False
def printMaybe(*msg):
    """
    Prints if the LOG_MODE constant is True.
    """
    if LOG_MODE:
        print ' '.join([str(i) for i in msg])

class PacManiaSearchAgents(AgentFactory):
    '''
    Create the new PacManiaSearchAgents
    '''

    def __init__(self, isRed, first='offence', second = 'defence', rest = 'offence'):
        AgentFactory.__init__(self, isRed)
        self.agents = [first, second]
        self.rest = rest
        self.red = isRed

    def getAgent(self, index):
         if len(self.agents) > 0:
             return self.choose(self.agents.pop(0), index)
         else:
             return self.choose(self.rest, index)

    def choose(self, agentStr, index): 
        printMaybe(agentStr)
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
            printMaybe("didn't find thing for", agentStr)
            raise Exception("No PacMania agent identified by " + agentStr)

class MetriculatedSearchAgent(CaptureAgent):
    '''
    Defines the basic agent and the metrics it assesses when deciding on a course
    of action. Some of the code is copied from the provided BaselineAgents code.
    '''
    # TODO(aramk) if these are magic, make them ALL_CAPS
    nextZone = 0
    deadCells = Set() # Cells that are part of a dead end. Avoid these when fleeing
    deadCellValue = {}

    def __init__(self, index, isOffensive = True):
        CaptureAgent.__init__(self, index)
        self.zone = MetriculatedSearchAgent.nextZone
        MetriculatedSearchAgent.nextZone += 1
        self.isOffensive = isOffensive
        self.nextPatrolPos = None
        self.lastTeamPos = None
        self.maxOurFoodNumber = None

    def getAdjacentWallCount(self, pos, gameState):
        (i, j) = pos
        grid = gameState.getWalls()
        count = 0
        for k in range(-1, 1):
            if grid[i+k][j]:
                count += 1
            if grid[i][j+k]:
                count += 1
        return count

    def getAdjacentFreeCells(self, pos, gameState):
        (i, j) = pos
        grid = gameState.getWalls()
        freeCells = []
        for k in range(-1, 1):
            if not grid[i+k][j]:
                freeCells.append((i+k, j))
            if not grid[i][j+k]:
                freeCells.append((i, j+k))
        return freeCells

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.distancer = distanceCalculator.Distancer(gameState.data.layout)
        self.distancer.getMazeDistances()
        printMaybe("INITIALISED DISTANCE CALCULATORN")

        self.deadCells = Set()

        grid = gameState.getWalls()
        grid.height * grid.width
        printMaybe("About to find dead cells")
        numThings = 0
        for i in range(1, grid.width-1):
            for j in range(1, grid.height-1):
                if not grid[i][j]:
                    numThings += 1
                count = self.getAdjacentWallCount((i, j), gameState)
                if count >= 3:
                    # We're in a dead end cell
                    printMaybe("Found dead cell at (", i, j, ")")
                    self.deadCells.update([(i,j)])

        printMaybe("FREE CELLS:",numThings)

        toCheck = Set(self.deadCells)
        checked = Set()
        depth = 0

        # While there are still cells to check
        while toCheck:
            depth += 1
            thisCell = toCheck.pop()
            self.deadCellValue[thisCell] = depth
            checked.update([thisCell])
            adjacentFree = self.getAdjacentFreeCells(thisCell, gameState)
            if (len(adjacentFree) <= 2):
                # Leads to a bad cell
                self.deadCells.update([thisCell])
                for cell in adjacentFree:
                    if not cell in checked:
                        toCheck.update([cell])

        printMaybe("Found ", len(self.deadCells), " dead cells:", self.deadCells)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        obs = self.getCurrentObservation()

        if self.maxOurFoodNumber is None:
            self.maxOurFoodNumber = len(self.getFoodYouAreDefending(obs).asList())

        teamIndex = [i for i in self.getTeam(gameState)]
        team = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
        teamPos = [i.getPosition() for i in team]
        # Change the strategy dynamically when a team member is killed.
        # Detects this by checking for movement of team members.
        if self.lastTeamPos is not None:
            for i in range(0, len(teamPos)):
                agentIndex = teamIndex[i]
                if self.lastTeamPos[i] is not None and teamPos[i] is not None:
                    x1, y1 = self.lastTeamPos[i]
                    x2, y2 = teamPos[i]
                    diffPos = (x2-x1, y2-y1)
                    isAdvancing = False
                    if self.red:
                        isAdvancing = self.getScore(obs) >= 0
                    else:
                        isAdvancing = self.getScore(obs) <= 0
                    # Here we're assuming that agents cannot teleport. Any change in movement greater than 1 means they were eaten.
                    if abs(y2-y1) > 1 or abs(x2-x1) > 1:
                        if agentIndex == self.index:
                            printMaybe('We have been eaten. Becoming defensive.', diffPos, self.index)
                            # TODO(aramk) we should probably switch our role to the role of the eaten agent?
                            self.isOffensive = False
                        else:
                            printMaybe('Other team member has been eaten. Becoming offensive.', diffPos, self.index)
                            self.isOffensive = True

        self.lastTeamPos = teamPos
        myPos = obs.getAgentPosition(self.index)
        actions = gameState.getLegalActions(self.index)
        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # printMaybe('eval time for agent %d: %.4f' % (self.index, time.time() - start))
        maxValue = max(values)
        # Fuzzy randomisation for action to a small degree of sensitivity
        bestActions = [a for a, v in zip(actions, values) if abs(v - maxValue) <= 0.05]
        printMaybe('    bestActions for ', self.index, [a + ':' + str(v) for a,v in zip(actions, values)])

        if myPos == obs.getInitialAgentPosition(self.index):
          self.nextPatrolPos = None

        # If we have no better actions, start patrolling.
        # The minimum score for maxValue needed to start patrolling. Anything higher cancels the patrol.
        minPatrolScore = 0
        if maxValue <= minPatrolScore:
            ourFood = self.getFoodYouAreDefending(obs)
            ourFoodList = ourFood.asList()

            if self.nextPatrolPos is None and len(ourFoodList) > int(self.maxOurFoodNumber * 0.8):
              self.nextPatrolPos = self.findPatrolPos3()
              printMaybe(self.index,'initial', self.nextPatrolPos)
              actions = mazeActions(myPos, self.nextPatrolPos, obs)
              return actions[0]

            if self.nextPatrolPos == myPos or (self.nextPatrolPos is None and len(ourFoodList) <= int(self.maxOurFoodNumber * 0.8)):
                our_capsules = self.getCapsulesYouAreDefending(obs)

                if our_capsules != []:
                  if self.nextPatrolPos not in our_capsules:
                    self.nextPatrolPos = random.choice(our_capsules)   
                    self.nextPatrolPos = our_capsules[0]
                    printMaybe(self.index,'to superfood', self.nextPatrolPos)
                    return actions[0]
            
                self.nextPatrolPos = self.findPatrolPos4()
                printMaybe(self.index,"to rich pos", self.nextPatrolPos)

            actions = mazeActions(myPos, self.nextPatrolPos, obs)
            if len(actions) > 0:
                return actions[0]
        
        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentPosition(self.index)
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def getMazeDistance(self, pos1, pos2):
        self.distancer.getMazeDistances()
        return CaptureAgent.getMazeDistance(self, pos1, pos2)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of metrics and metric weights
        """
        metrics = self.getMetrics(gameState, action)
        weights = self.getWeights(gameState, action)
        scores = [k + ':' + str(float(metrics[k])*float(weights[k])) for k in metrics]
        printMaybe("  Evaluate for", self.index, action, ':', ', '.join(scores))
        return metrics * weights

    def getMetrics(self, gameState, action):
        """
        Returns a counter of metrics for the state
        """
        metrics = util.Counter()
        successor = self.getSuccessor(gameState, action)
        x, y = myPos = gameState.getAgentPosition(self.index)
        dx, dy = Actions.directionToVector(action)
        nextX, nextY = int(x + dx), int(y + dy)
        if (int(nextX) != nextX or int(nextY) != nextY):
            printMaybe("next", (nextX, nextY))

        # Query the state
        isPacman = successor.getAgentState(self.index).isPacman
        foods = self.getFood(gameState)
        capsules = self.getCapsules(gameState)
        grid = gameState.getWalls()
        # This is an approximation used for standardisation, not the theoretical limit.
        maxDistInGrid = float(math.sqrt((grid.height ** 2) + (grid.width ** 2)))

        theirs = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ours = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
        friends = [gameState.getAgentState(i) for i in self.getTeam(gameState) if i != self.index]
        theirGhosts = [a for a in theirs if not a.isPacman and a.getPosition() is not None]
        theirPacmans = [a for a in theirs if a.isPacman and a.getPosition() is not None]

        # If the closest point near the border is a wall, use the coordinate of the gent
        borderX, borderY = (grid.width / 2 - 1) if self.red else (grid.width / 2), nextY
        distFromBorder = borderX - x if self.red else x - borderX

        # Ghost metrics
        if not isPacman:
            distanceToPacmans = [self.getMazeDistance((nextX, nextY), p.getPosition()) for p in theirPacmans if p.getPosition() is not None]
            closestPacman = min(distanceToPacmans) if len(distanceToPacmans) > 0 else None

            for i in self.getOpponents(gameState):
                state = gameState.getAgentState(i)
                if state is not None and state.configuration is not None:
                    distBorderX, distBorderY = int(x), int(y)
                    enemyDist = self.getMazeDistance((distBorderX, distBorderY), state.getPosition())
                    printMaybe('Reached border', self.index, x, nextX, borderX, self.red, action, enemyDist, distFromBorder)

                    if enemyDist <= 6 and distFromBorder <= 0:
                        printMaybe('Waiting for the kill', myPos, state.getPosition(), self.red, action)
                        if (self.red and action == Directions.EAST) or (not self.red and action == Directions.WEST):
                            metrics['border-wait'] = 1
            
            if closestPacman is not None:
                closestPacmanRatio = closestPacman / maxDistInGrid
                if closestPacmanRatio == 0:
                    closestPacmanRatio = 0.0001
                # This grows as we approach the closest PacMan
                inverseRatio = 2 / closestPacmanRatio
                isGhostBeingChased = successor.getAgentState(self.index).scaredTimer > 0
                if not isGhostBeingChased:
                    # printMaybe("A pacman, yum!")
                    metrics['seen-edible-pacman'] = inverseRatio
                else:
                    # This distance means we are at risk of being eaten
                    riskyDist = 4
                    if closestPacman <= riskyDist:
                        # Run away, too close!
                        printMaybe('1 ghost is scared', closestPacman, closestPacmanRatio)
                        metrics['seen-scary-pacman'] = inverseRatio
                    else:
                        # Follow the scary PacMan
                        printMaybe('2 ghost is scared, but chasing', closestPacman, closestPacmanRatio)
                        metrics['chase-scary-pacman'] = inverseRatio

        # Pacman metrics
        if isPacman:
            if capsules:
                # Help a brother out
                inDanger = False
                for ghost in theirGhosts:
                    for brother in ours:
                        printMaybe("brotherpos ", brother.getPosition(), " ghostpos ", ghost.getPosition())
                        if brother.getPosition() and self.withinMoves(3, brother.getPosition(), ghost.getPosition(), gameState):
                            inDanger = True
                            break
                    if inDanger:
                        break
            
                if inDanger:
                    minSuperDist = min([self.getMazeDistance((nextX,nextY), superFood) for superFood in capsules])
                    metrics['help-a-brother'] = 2 - (float(minSuperDist) / maxDistInGrid)

            for ghost in theirGhosts:
                # Pacman has run into a ghost
                if (nextX, nextY) == ghost.getPosition():
                    printMaybe("timer", ghost.scaredTimer)
                    if ghost.scaredTimer <= 0:
                        #printMaybe("Oh dear we're about to get eat")
                        metrics['collide-scary-ghosts'] += 1
                        # metrics['collide-edible-ghosts'] = 0
                    else:
                        #printMaybe("Time to feast on ectoplasm")
                        metrics['collide-edible-ghosts'] += 1
                # Pacman would be adjacent to a ghost
                elif self.withinMoves(3, (nextX, nextY), ghost.getPosition(), gameState):
                    # printMaybe("oh dear we're about to get eat")
                    if ghost.scaredTimer == 0:
                        metrics['adjacent-scary-ghosts'] += 1
                        # metrics['adjacent-edible-ghosts'] = 0
                    else:
                        printMaybe("Time to feast on ectoplasm")
                        metrics['adjacent-edible-ghosts'] += 1

            # If we're being chased, avoid going into dead zones if poss
            if (metrics['collide-scary-ghosts'] + metrics['adjacent-scary-ghosts']):
                if (nextX, nextY) in self.deadCells:
                    metrics['dead-cell'] = 2 + (float(1) / float(self.deadCellValue[(nextX, nextY)]))

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
                metrics['find-a-fud'] = 1 - float(minFoodDist) / maxDistInGrid

        # Attempts to separate friends from each other
        distanceToFriends = [self.getMazeDistance((nextX, nextY), p.getPosition()) for p in friends if p.getPosition() is not None]
        distanceToFriendsRatio = [i / maxDistInGrid for i in distanceToFriends]
        inverseDistanceToFriendsRatio = [1 / i for i in distanceToFriendsRatio if i != 0]
        metrics['distance-to-friends'] = sum(inverseDistanceToFriendsRatio) if len(inverseDistanceToFriendsRatio) > 0 else maxDistInGrid/0.5

        return metrics    

    def findPatrolPos4(self):
        obs = self.getCurrentObservation()
        grid = obs.getWalls()
        myPos = obs.getAgentPosition(self.index)

        myx, myy = myPos

        ourFood = self.getFoodYouAreDefending(obs)

        ourFoodList = ourFood.asList()

        # if we have less than half food left, we should patrol around these food.
        if len(ourFoodList) <= self.maxOurFoodNumber / 2:        
            result = ourFoodList[int(random.random() * len(ourFoodList))]
            return result

        x_y_list = [(x,y) for (x,y) in ourFoodList]

        min_x = min(x_y_list)[0]
        max_x = max(x_y_list)[0]

        reverse_x_y_list = [(y,x) for (x,y) in ourFoodList]

        min_y = min(reverse_x_y_list)[0]
        max_y = max(reverse_x_y_list)[0]

        # create R matrix which contains all food

        count = [0,0,0,0]
        food_pos_in_area = {0:[],1:[],2:[],3:[]}

        diff_y = max_y - min_y

        range_y = diff_y / 2
        
        if (diff_y + 1) % 2 == 0:
            bound_y = range_y + min_y + 1
        else:
            bound_y = range_y + min_y

        diff_x = max_x - min_x

        range_x = diff_x / 2

        if (diff_x + 1) % 2 == 0:
            bound_x = range_x + min_x + 1
        else:
            bound_x = range_x + min_x

        # food zones are shown as follow:
        # 0 1
        # 2 3

        for y in range(bound_y, max_y + 1):
            for x in range(min_x, bound_x):
                if (x,y) in ourFoodList:
                    #print '0', (x,y)
                    count[0] = count[0] + 1
                    food_pos_in_area[0].append((x,y))

            for x in range(bound_x, max_x + 1):
                if (x,y) in ourFoodList:
                    #print '1', (x,y)
                    count[1] = count[1] + 1
                    food_pos_in_area[1].append((x,y))

        for y in range(min_y, bound_y):
            for x in range(min_x, bound_x):
                if (x,y) in ourFoodList:
                    #print '2', (x,y)
                    count[2] = count[2] + 1
                    food_pos_in_area[2].append((x,y))

            for x in range(bound_x, max_x + 1):
                if (x,y) in ourFoodList:
                    #print '3', (x,y)
                    count[3] = count[3] + 1
                    food_pos_in_area[3].append((x,y))

        # find the zone which contains most of food
        area_has_most_food_index = count.index(max(count))
        area_has_most_food_list = food_pos_in_area[area_has_most_food_index]

        # pick a random food from the zone
        result = area_has_most_food_list[int(random.random() * len(area_has_most_food_list))]

        return result

    def findPatrolPos3(self):
        obs = self.getCurrentObservation()
        grid = obs.getWalls()
        myPos = obs.getAgentPosition(self.index)

        if self.red:
            l_bound = 0
            r_bound = grid.width / 2 - 1
            boundary = r_bound
        else:
            l_bound = grid.width / 2
            r_bound = grid.width - 1
            boundary = l_bound

        close_to_boundary_list = []

        for y in range(grid.height):
          for x in range(l_bound, r_bound):
            if grid[x][y] is False:
              abs_diff = abs(boundary - x)
              close_to_boundary_list.append((abs_diff, (x,y)))

        # create a list which contains all postions which can be visited
        # and sort it based on the distance between it and the mid-line 
        close_to_boundary_list.sort()
        
        list_len = len(close_to_boundary_list)
        
        # take the top five percent
        list_size = int(list_len * 0.05)

        # use all elements if the list is not large enough
        if list_len <= 4:
          list_size = list_len

        result_list = close_to_boundary_list[0:list_size]

        # pick one randomly from the list 
        result = result_list[int(random.random() * len(result_list))]

        return result[1]

    def getWeights(self, gameState, action):
        """
        Weights assigned to the metrics of successor state. These weights are
        assigned in the OffensiveSearchAgent and DefensiveSearchAgent.
        """
        # print 'isOffensive', self.index, self.isOffensive
        if self.isOffensive:
            return self.getOffensiveWeights(gameState,action)
        else:
            return self.getDefensiveWeights(gameState,action)

    def getDefensiveWeights(self, gameState, action):
        return {
            'dead-cell': -1.0,
            'seen-edible-pacman': 10.0,
            'seen-scary-pacman': -2.0,
            'chase-scary-pacman': 5.0,
            'collide-scary-ghosts': -10.0,
            'collide-edible-ghosts': -5.0,
            'adjacent-scary-ghosts': -10.0,
            'adjacent-edible-ghosts': -2.0,
            'eats-fud': 2.0,
            'find-a-fud': 0.0,
            'help-a-brother': 2.0,
            'stop': -1,
            'border-wait': -30,
            'distance-to-friends': -0.1
        }

    def getOffensiveWeights(self, gameState, action):
        return {
            'dead-cell': -1.0,
            'seen-edible-pacman': 5.0,
            'seen-scary-pacman': -5.0,
            'chase-scary-pacman': -5.0,
            'collide-scary-ghosts': -10.0,
            'collide-edible-ghosts': 5.0,
            'adjacent-scary-ghosts': -10.0,
            'adjacent-edible-ghosts': 2.0,
            'eats-fud': 10.0,
            'find-a-fud': 8.0,
            'help-a-brother': 2.0,
            'stop': -1,
            'border-wait': -30,
            'distance-to-friends': -0.1
        }
        
    def minDis(self, pos1, entities, gamestate):
        """
        Returns the number of moves required to reach the nearest entity in the
        given list of entities
        """
        # TODO(aramk) remove?
        None

    def withinMoves(self, moves, pos1, pos2, gameState):
        """
        Returns true if 'pos1' and 'pos2' are within 'moves' moves of each other
        """
        # Try and get from pos1 to pos2
        movesLeft = moves
        possiblePositions = Set([pos1])
        while movesLeft > 0:
            newPositions = Set()
            for position in possiblePositions:
                newPositions.update(Actions.getLegalNeighbors(pos1, gameState.getWalls()))
            possiblePositions.update(newPositions)
            movesLeft -= 1

        return pos2 in possiblePositions

    def findClosestPosBeyondBorder(self):
        """
        Finds the closest point on the other side of the boundary.
        """
        obs = self.getCurrentObservation()
        grid = obs.getWalls()
        x,y = obs.getAgentPosition(self.index)
        x, y = myPos = int(x), int(y)
        print 'myPos', myPos, x, y
        borderX = grid.width / 2 if self.red else grid.width / 2 - 1
        borderY = y
        alternator = 1
        while grid[borderX][borderY]:
            borderY += alternator
            alternator = -(abs(alternator) + 1)
        print 'found pos beyond border', borderX, borderY

class OffensiveSearchAgent(MetriculatedSearchAgent):
    '''
    Search agent that takes an offensive attitude
    '''
    def __init__(self, index):
        MetriculatedSearchAgent.__init__(self, index, True)

class DefensiveSearchAgent(MetriculatedSearchAgent):
    '''
    Search agent that takes a defensive attitude
    '''
    def __init__(self, index):
        MetriculatedSearchAgent.__init__(self, index, False)

# AUXILIARY FUNCTIONS

# TODO(aramk) this is rather slow
def mazeActions(point1, point2, gameState):
    """
    Returns the actions needed to travel between any two points on the maze.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    # NOTE: there is a bug in the code I think - getAgentPosition() returns float after the first step, so we cast to int.
    assert not walls[int(x1)][int(y1)], 'point1 is a wall: ' + point1
    assert not walls[int(x2)][int(y2)], 'point2 is a wall: ' + str(point2)
    prob = searchAgents.PositionSearchProblem(gameState, start=point1, goal=point2, warn=False)
    return search.bfs(prob)
