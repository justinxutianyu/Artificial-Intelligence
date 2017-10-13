# searchAgents.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
This file contains all of the agents that can be selected to
control Pacman.  To select an agent, use the '-p' option
when running pacman.py.  Arguments can be passed to your agent
using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a searchFunction=depthFirstSearch

Commands to invoke other search strategies can be found in the
project description.

Please only change the parts of the file you are asked to.
Look for the lines that say

"*** YOUR CODE HERE ***"

The parts you fill in start about 3/4 of the way down.  Follow the
project description for details.

Good luck and happy searching!
"""
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search

class GoWestAgent(Agent):
    "An agent that goes West until it can't."

    def getAction(self, state):
        "The agent receives a GameState (defined in pacman.py)."
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search algorithm for a
    supplied search problem, then returns actions to follow that path.

    As a default, this agent runs DFS on a PositionSearchProblem to find location (1,1)

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs


    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError, fn + ' is not a search function in search.py.'
        func = getattr(search, fn)
        if 'heuristic' not in func.func_code.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError, heuristic + ' is not a function in searchAgents.py or search.py.'
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError, prob + ' is not a search problem type in SearchAgents.py.'
        self.searchType = globals()[prob]
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game board. Here, we
        choose a path to the goal.  In this phase, the agent should compute the path to the
        goal and store it in a local variable.  All of the work is done in this method!

        state: a GameState object (pacman.py)
        """
        if self.searchFunction == None: raise Exception, "No search function provided for SearchAgent"
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state):
        """
        Returns the next action in the path chosen earlier (in registerInitialState).  Return
        Directions.STOP if there is no further action to take.

        state: a GameState object (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test,
    successor function and cost function.  This search problem can be
    used to find paths to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print 'Warning: this does not look like a regular search maze'

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1

        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class graphProblem(search.SearchProblem):
    """
    @Author: Daniel
    """

    def __init__(self, goal, start):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.startState = start  # Initial door
        self.goal = goal  # Target door

    def getStartState(self):
        print "Start"
        return self.startState

    def isGoalState(self, state):
        print "Goal " + str(state[0] == self.goal)
        print state[0]
        return state[0] == self.goal

    def getSuccessors(self, state):
        # state = [door, doormap, doorVisited]
        # raw_input("Press Enter")

        successors = []
        for i, action in enumerate(state[1][state[0]]):
            if state[1][state[0]][i] is not None:
                visitedMatrix = list(state[2])
                nextState = (i, state[1], visitedMatrix)
                cost = 0
                if not visitedMatrix[state[0]][i]:
                    visitedMatrix[state[0]][i] = True
                    cost = state[1][state[0]][i][1]
                    print "Cost " + str(i) + " " + str(cost)
                successors.append( ( nextState, (state[0], cost), cost) )
        return successors

class StayEastSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the West side of the board.

    The cost function for stepping into a position (x,y) is 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

class StayWestSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the East side of the board.

    The cost function for stepping into a position (x,y) is 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "The Manhattan distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "The Euclidean distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, startingGameState):
        """
        Stores the walls, pacman's starting position and corners.
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print 'Warning: no food in corner ' + str(corner)
        self._expanded = 0 # Number of search nodes expanded

        "*** YOUR CODE HERE ***"

    def getStartState(self):
        "Returns the start state (in your state space, not the full Pacman state space)"
        "*** YOUR CODE HERE ***"
        # Position and as many corners as visited
        return  (self.startingPosition[0], self.startingPosition[1]) + (False,)*len(self.corners)

    def isGoalState(self, state):
        "Returns whether this search state is a goal state of the problem"
        "*** YOUR CODE HERE ***"
        # Check if all corners have been visited or if pacman's position is on a not visited corner
        for i, visited in enumerate(state[2:]):
            if visited or (state[0] == self.corners[i][0] and state[1] == self.corners[i][1]):
                continue
            return False
        return True

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            # Add a successor state to the successor list if the action is legal
            # Here's a code snippet for figuring out whether a new position hits a wall:
            #   x,y = currentPosition
            #   dx, dy = Actions.directionToVector(action)
            #   nextx, nexty = int(x + dx), int(y + dy)
            #   hitsWall = self.walls[nextx][nexty]

            "*** YOUR CODE HERE ***"
            x, y = state[0:2]
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if dx == 0 and dy == 0:
                continue
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                for i, visited in enumerate(state[2:]):
                    nextState = nextState + ((visited or (x == self.corners[i][0] and y == self.corners[i][1])),)
                cost = 1
                successors.append((nextState, action, cost))

        self._expanded += 1
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state, problem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound
    on the shortest path from the state to a goal of the problem; i.e.
    it should be admissible (as well as consistent).
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)

    "*** YOUR CODE HERE ***"
    myCorners = list(state[2:])
    myPosition = [state[0], state[1]]
    totalDist = 0
    while (not myCorners[0]) or (not myCorners[1]) or (not myCorners[2]) or (not myCorners[3]):
        closestCorner = -1
        distCorner = None
        for i, visited in enumerate(myCorners):
            if not visited:
                dist = abs(myPosition[0] - corners[i][0]) + abs(myPosition[1] - corners[i][1])
                if distCorner is None or dist < distCorner:
                    distCorner = dist
                    closestCorner = i

        if distCorner is not None:
            totalDist += distCorner
        if closestCorner >= 0:
            myCorners[closestCorner] = True
            myPosition = [corners[closestCorner][0], corners[closestCorner][1]]

    # # Not admissible, but way faster
    # distCentroid = 0
    # for i, visited in enumerate(state[2:]):
    #     if not visited:
    #         distCentroid += abs(state[0] - corners[i][0]) + abs(state[1] - corners[i][1])

    return totalDist

class AStarCornersAgent(SearchAgent):
    "A SearchAgent for CornersProblem using A* and your cornersHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game.

    A search state in this problem is a tuple ( pacmanPosition, foodGrid ) where
      pacmanPosition: a tuple (x,y) of integers specifying Pacman's position
      foodGrid:       a Grid (see game.py) of either True or False, specifying remaining food
    """
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come up
    with an admissible heuristic; almost all admissible heuristics will be consistent
    as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the other hand,
    inadmissible or inconsistent heuristics may find optimal solutions, so be careful.

    The state is a tuple ( pacmanPosition, foodGrid ) where foodGrid is a
    Grid (see game.py) of either True or False. You can call foodGrid.asList()
    to get a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the problem.
    For example, problem.walls gives you a Grid of where the walls are.

    If you want to *store* information to be reused in other calls to the heuristic,
    there is a dictionary called problem.heuristicInfo that you can use. For example,
    if you only want to count the walls once and store that value, try:
      problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access problem.heuristicInfo['wallCount']
    """
    position, foodGrid = state
    "*** YOUR CODE HERE ***"

    "TO DO: see if I can get something useful from this giant chunck of commented code"
    "Theoretically, it divides the maze in rooms and doors, but once I tried it, it made the algorithm run even" \
    "slower than my original idea, which is already a slow (although apparently is fast enough to get the max grade)"
    # # Crazy idea begin
    # problem.heuristicInfo["rooms"] = 0
    # if not "rooms" in problem.heuristicInfo:
    #     w  = problem.walls.width
    #     h = problem.walls.height
    #     problem.heuristicInfo["w"] = w
    #     problem.heuristicInfo["h"] = h
    #     walls = problem.walls.deepCopy()
    #
    #     # Save map as 0, 1 and 2 (walls:0, 1:spaces, 2:food)
    #     for x in range(w):
    #         for y in range(h):
    #             if walls[x][y]:
    #                 walls[x][y] = 0
    #             elif foodGrid[x][y]:
    #                 walls[x][y] = 2
    #             else:
    #                 walls[x][y] = 1
    #
    #     # Detect doors and spaces. Spaces are now negative
    #     for x in range(w):
    #         for y in range(h):
    #             if walls[x][y] > 0:
    #                 exitsNum = 0
    #                 if walls[x][y - 1] != 0:
    #                     exitsNum += 1
    #                 if walls[x][y + 1] != 0:
    #                     exitsNum += 1
    #                 if walls[x - 1][y] != 0:
    #                     exitsNum += 1
    #                 if walls[x + 1][y] != 0:
    #                     exitsNum += 1
    #                 if exitsNum == 1 or exitsNum == 2:
    #                     walls[x][y] = -1 * walls[x][y]
    #                 elif exitsNum == 0:
    #                     # We erase unaccessible cells
    #                     walls[x][y] = 0
    #     # Create graph map
    #     roomsGraph = []
    #     doorsGraph = []
    #     for x in range(1, w-1):
    #         for y in range(1, h-1):
    #             if walls[x][y] < 0:
    #                 spacesNum = 0
    #                 if walls[x][y - 1] < 0:
    #                     spacesNum += 1
    #                 if walls[x][y + 1] < 0:
    #                     spacesNum += 1
    #                 if walls[x - 1][y] < 0:
    #                     spacesNum += 1
    #                 if walls[x + 1][y] < 0:
    #                     spacesNum += 1
    #                 if spacesNum < 2:
    #                     endOfPath = False
    #                     graphNode = {"path": [], "doors": [], "food": 0}
    #                     auxx = x
    #                     auxy = y
    #                     while not endOfPath:
    #                         graphNode["path"].append([x, y])
    #                         graphNode["food"] += -walls[x][y] - 1
    #                         walls[x][y] = 0
    #                         xx = x
    #                         yy = y
    #                         if walls[x][y - 1] < 0:
    #                             yy = y - 1
    #                         elif walls[x][y + 1] < 0:
    #                             yy = y + 1
    #                         elif walls[x - 1][y] < 0:
    #                             xx = x - 1
    #                         elif walls[x + 1][y] < 0:
    #                             xx = x + 1
    #                         else:
    #                             endOfPath = True
    #                         if walls[x][y - 1] > 0:
    #                             if [[x, y - 1], []] not in doorsGraph:
    #                                 graphNode["doors"].append(len(doorsGraph))
    #                                 doorsGraph.append([[x, y - 1], []])
    #                             else:
    #                                 graphNode["doors"].append(doorsGraph.index([[x, y - 1], []]))
    #                         if walls[x][y + 1] > 0:
    #                             if [[x, y + 1], []] not in doorsGraph:
    #                                 graphNode["doors"].append(len(doorsGraph))
    #                                 doorsGraph.append([[x, y + 1], []])
    #                             else:
    #                                 graphNode["doors"].append(doorsGraph.index([[x, y + 1], []]))
    #                         if walls[x - 1][y] > 0:
    #                             if [[x - 1, y], []] not in doorsGraph:
    #                                 graphNode["doors"].append(len(doorsGraph))
    #                                 doorsGraph.append([[x - 1, y], []])
    #                             else:
    #                                 graphNode["doors"].append(doorsGraph.index([[x - 1, y], []]))
    #                         if walls[x + 1][y] > 0:
    #                             if [[x + 1, y], []] not in doorsGraph:
    #                                 graphNode["doors"].append(len(doorsGraph))
    #                                 doorsGraph.append([[x + 1, y], []])
    #                             else:
    #                                 graphNode["doors"].append(doorsGraph.index([[x + 1, y], []]))
    #                         x = xx
    #                         y = yy
    #                     roomsGraph.append(graphNode)
    #                     x = auxx
    #                     y = auxy
    #     problem.heuristicInfo["rooms"] = roomsGraph
    #
    #     for j, door in enumerate(doorsGraph):
    #         for i, room in enumerate(roomsGraph):
    #             for aDoor in room["doors"]:
    #                 if aDoor == j:
    #                     doorsGraph[j][1] = doorsGraph[j][1] + [i]
    #     problem.heuristicInfo["doors"] = doorsGraph
    #
    #     doorsDistance = []
    #     print
    #     for dist in doorsDistance:
    #         print dist
    #     for i, door in enumerate(doorsGraph):
    #         doorsRow = [None] * len(doorsGraph)
    #         for room in door[1]:
    #             for neighborDoor in roomsGraph[room]["doors"]:
    #                 if neighborDoor != i:
    #                     doorsRow[neighborDoor] = [roomsGraph[room]["food"], len(roomsGraph[room]["path"])]
    #         doorsDistance.append(doorsRow)
    #     problem.heuristicInfo["doorsD"] = doorsDistance
    #
    #     print
    #     for room in roomsGraph:
    #         print room
    #     print
    #     for door in doorsGraph:
    #         print door
    #     print
    #     for dist in doorsDistance:
    #         print dist
    #
    #     roomsVisited = []
    #     for ii in doorsDistance:
    #         roomsVisited.append([False]*len(ii))
    #
    #     gProblem = graphProblem(0, [1, doorsDistance, roomsVisited])
    #     from search import serchUsingFringeWithCost
    #     pathGraph = serchUsingFringeWithCost(gProblem, util.PriorityQueue())
    #     for i, p in enumerate(pathGraph):
    #         for j, pp in enumerate(pathGraph[i+1:]):
    #             if pp[0] == p[0]:
    #                 pathGraph[j + i + 1] = (p[0], p[1])
    #
    #     for i, p in enumerate(pathGraph):
    #         if pathGraph.count(p) > 1:
    #             j = max(loc for loc, val in enumerate(pathGraph) if val == p)
    #             pathGraph = pathGraph[:i] + pathGraph[j:]
    #     print
    #     print pathGraph
    #     ##### Crazy Idea End
    #
    #
    #
    #
    #         print ""
    #         print walls
    #         deadEndFound = True
    #         while deadEndFound:
    #             deadEndFound = False
    #             for x in range(1, w-1):
    #                 for y in range(1, h-1):
    #                     if walls[x][y][0] > 0:
    #                         numPaths = 0
    #                         numFood = walls[x][y][0] - 1
    #                         lastPath = None
    #                         for i in [-1, 1]:
    #                             xi = x + i
    #                             yi = y + i
    #                             if walls[xi][y][0] > 0:
    #                                 # I can probably use this to speed up
    #                                 numExits = 0
    #                                 if walls[xi+i][y][0] > 0:
    #                                     numExits += 1
    #                                 if walls[xi][y+1][0] > 0:
    #                                     numExits += 1
    #                                 if walls[xi][y-1][0] > 0:
    #                                     numExits += 1
    #                                 numPaths += 1
    #                                 if numExits == 1:
    #                                     lastPath = [xi, y]
    #                             if walls[xi][y][0] > 1:
    #                                 numFood += walls[xi][y][0] - 1
    #                             if walls[x][yi][0] > 0:
    #                                 # I can probably use this to speed up
    #                                 numExits = 0
    #                                 if walls[x][yi+i][0] > 0:
    #                                     numExits += 1
    #                                 if walls[x+1][yi][0] > 0:
    #                                     numExits += 1
    #                                 if walls[x-1][yi][0] > 0:
    #                                     numExits += 1
    #                                 numPaths += 1
    #                                 if numExits == 1:
    #                                     lastPath = [x, yi]
    #                             if walls[x][yi][0] > 1:
    #                                 numFood += walls[x][yi][0] - 1
    #                         if lastPath is not None and numPaths == 1:
    #                             walls[x][y][0] = -1
    #                             walls[lastPath[0]][lastPath[1]][0] = numFood + 1
    #                             walls[lastPath[0]][lastPath[1]][1] = walls[x][y][1] + 1
    #                             deadEndFound = True
    #
    #     for x in range(w):
    #         for y in range(h):
    #             if not walls[x][y]:
    #                 # Vertical door
    #                 if not walls[x][y-1] and not walls[x][y+1] and walls[x-1][y] and walls[x+1][y]:
    #                     south = 0
    #                     if not walls[x-1][y-1]:
    #                         south += 1
    #                     if not walls[x+1][y-1]:
    #                         south += 1
    #                     if y-2>=0 and not walls[x][y-2]:
    #                         south += 1
    #                     north = 0
    #                     if not walls[x-1][y+1]:
    #                         north += 1
    #                     if not walls[x+1][y+1]:
    #                         north += 1
    #                     if y+2<h and not walls[x][y+2]:
    #                         north += 1
    #                     if (north > 1 and south > 0) or (north > 0 and south > 1):
    #                         # Vertical door found
    #                         problem.heuristicInfo["map"][x][y] = 'V'
    #                 # Horizontal door
    #                 if not walls[x-1][y] and not walls[x+1][y] and walls[x][y-1] and walls[x][y+1]:
    #                     west = 0
    #                     if not walls[x-1][y-1]:
    #                         west += 1
    #                     if not walls[x-1][y+1]:
    #                         west += 1
    #                     if x-2>=0 and not walls[x-2][y]:
    #                         west += 1
    #                     east = 0
    #                     if not walls[x+1][y-1]:
    #                         east += 1
    #                     if not walls[x+1][y+1]:
    #                         east += 1
    #                     if y+2<w and not walls[x+2][y]:
    #                         east += 1
    #                     if (east > 1 and west > 0) or (west > 0 and east > 1):
    #                         # Horizontal door found
    #                         problem.heuristicInfo["map"][x][y] = 'H'
    #             else:
    #                 problem.heuristicInfo["map"][x][y] = '#'
    #     for i in problem.heuristicInfo["map"]:
    #         print i
    #
    # # This is ko, but almost
    # myFood = [False] * len(foodGrid.asList())
    # myPosition = [position[0], position[1]]
    # food = foodGrid.asList()
    # totalDist = 0
    # while not all(item == True for item in myFood):  # Check if all elements are True
    #     closestFood = -1
    #     distFood = None
    #     wentTooFar = False
    #     for i, visited in enumerate(myFood):
    #         if not visited:
    #             dist = abs(myPosition[0] - food[i][0]) + abs(myPosition[1] - food[i][1])
    #             distPacman = abs(position[0] - food[i][0]) + abs(position[1] - food[i][1])
    #             if distFood is None or dist < distFood:
    #                 distFood = min(dist, distPacman)
    #                 closestFood = i
    #                 wentTooFar = distPacman < dist
    #
    #     if distFood is not None:
    #         totalDist += distFood
    #     if wentTooFar:
    #         break
    #     if closestFood >= 0:
    #         myFood[closestFood] = True
    #         myPosition = [food[closestFood][0], food[closestFood][1]]
    #
    # # This is slow but works
    # numFood = 0
    # for i in foodGrid:
    #     for j in i:
    #         if j:
    #             numFood += 1


    myPosition = (position[0], position[1])
    food = foodGrid.asList()
    if len(food) == 0:
        return 0

    # Get cost to closest food
    distFood = None
    closestFood = -1
    if not "history" in problem.heuristicInfo:
        problem.heuristicInfo["history"] = {}
    for i, foodPosition in enumerate(food):
        try:
            dist = problem.heuristicInfo["history"][myPosition + foodPosition]
        except KeyError:
            dist = mazeDistance(myPosition, foodPosition, problem.startingGameState)
            problem.heuristicInfo["history"][myPosition + foodPosition] = dist
            problem.heuristicInfo["history"][foodPosition + myPosition] = dist

        if distFood is None or dist < distFood:
            distFood = dist
            closestFood = i
    totalDist = distFood

    fringe = util.PriorityQueue()
    myFoodPosition = food.pop(closestFood)
    while len(food) > 0:
        # Find all paths from my food to other food and push them into the fringe
        for foodPosition in food:
            try:
                dist = problem.heuristicInfo["history"][myFoodPosition + foodPosition]
            except KeyError:
                dist = mazeDistance(myFoodPosition, foodPosition, problem.startingGameState)
                problem.heuristicInfo["history"][myFoodPosition + foodPosition] = dist
                problem.heuristicInfo["history"][foodPosition + myFoodPosition] = dist
            fringe.push((foodPosition, dist), dist)

        # Pop every element from the fringe not bringing us to food until we get one that does (with lowest cost)
        while not fringe.isEmpty():
            myFoodPosition, dist = fringe.pop()
            if myFoodPosition in food:
                food.remove(myFoodPosition)
                totalDist += dist
                break
    return totalDist

class ClosestDotSearchAgent(SearchAgent):
    "Search for all food using a sequence of searches"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception, 'findPathToClosestDot returned an illegal move: %s!\n%s' % t
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print 'Path found with cost %d.' % len(self.actions)

    def findPathToClosestDot(self, gameState):
        "Returns a path (a list of actions) to the closest dot, starting from gameState"
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        "*** YOUR CODE HERE ***"
        from search import aStarSearch
        return aStarSearch(problem)

class AnyFoodSearchProblem(PositionSearchProblem):
    """
      A search problem for finding a path to any food.

      This search problem is just like the PositionSearchProblem, but
      has a different goal test, which you need to fill in below.  The
      state space and successor function do not need to be changed.

      The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
      inherits the methods of the PositionSearchProblem.

      You can use this search problem to help you fill in
      the findPathToClosestDot method.
    """

    def __init__(self, gameState):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test
        that will complete the problem definition.
        """
        x,y = state

        "*** YOUR CODE HERE ***"
        return self.food[x][y]

##################
# Mini-contest 1 #
##################

class ApproximateSearchAgent(Agent):
    "Implement your contest entry here.  Change anything but the class name."

    def registerInitialState(self, state):
        "This method is called before any moves are made."
        "*** YOUR CODE HERE ***"

    def getAction(self, state):
        """
        From game.py:
        The Agent will receive a GameState and must return an action from
        Directions.{North, South, East, West, Stop}
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def mazeDistance(point1, point2, gameState):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built.  The gameState can be any game state -- Pacman's position
    in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + point1
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False)
    return len(search.bfs(prob))
