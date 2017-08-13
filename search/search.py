# search.py
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def genericSearch (problem, queue, flag):
    """
        implemetn a generic search for search algorithm
    """
    visited = []
    cost = 0
    start = (problem.getStartState(), cost, [])
    supFunc(problem, queue, start, cost, flag)

    while not queue.isEmpty():
        temp = queue.pop()
        if problem.isGoalState(temp[0]):
            return temp[2]

        if temp[0] not in visited:
            visited.append(temp[0])

            for successor, action, stepCost in problem.getSuccessors(temp[0]): # successor, action, stepCost
                if successor not in visited:
                    new_cost = temp[1] + stepCost
                    new_path = temp[2] + [action]
                    new_state = (successor, new_cost, new_path)
                    supFunc(problem, queue, new_state, new_cost, flag)

def supFunc(problem, queue, state, cost, flag):
    if flag == 0:
        queue.push(state)
    elif flag == 1:
        queue.push(state, cost)
    else:
        queue.push(state, cost + heuristic(state[0], problem))


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    stack = util.Stack()
    initial_cost = 0
    initial_state = (problem.getStartState(), [])
    stack.push(initial_state)
    visited = []


    while not stack.isEmpty():
        temp = stack.pop()
        if problem.isGoalState(temp[0]):
            return temp[1]
        if temp[0] not in visited:
            visited.append(temp[0])
            for successor, action, stepCost in problem.getSuccessors(temp[0]): # successor, action, stepCost
                if successor not in visited:
                    new_path = temp[1] + [action]
                    new_state = (successor, new_path)
                    stack.push(new_state)

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    queue = util.Queue()
    initial_state = (problem.getStartState(), [])
    queue.push(initial_state)
    visited = []


    while not queue.isEmpty():
        temp = queue.pop()
        if problem.isGoalState(temp[0]):
            return temp[1]

        if temp[0] not in visited:
            visited.append(temp[0])
            for successor, action, stepCost in problem.getSuccessors(temp[0]): # successor, action, stepCost
                if successor not in visited:
                    new_path = temp[1] + [action]
                    new_state = (successor, new_path)
                    queue.push(new_state)

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    pqueue = util.PriorityQueue()
    initial_cost = 0
    initial_state = (problem.getStartState(), initial_cost, [])
    pqueue.push(initial_state, initial_cost)
    visited = []

    while not pqueue.isEmpty():
        temp = pqueue.pop()
        if problem.isGoalState(temp[0]):
            return temp[2]

        if temp[0] not in visited:
            visited.append(temp[0])
            for successor, action, stepCost in problem.getSuccessors(temp[0]): # successor, action, stepCost
                if successor not in visited:
                    new_cost = temp[1] + stepCost
                    new_path = temp[2] + [action]
                    new_state = (successor, new_cost, new_path)
                    pqueue.push(new_state, new_cost)

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    pqueue = util.PriorityQueue()
    visited = []
    initial_cost = 0
    initial_state = (problem.getStartState(), initial_cost, [])
    pqueue.push(initial_state, initial_cost + heuristic(initial_state[0], problem))

    while not pqueue.isEmpty():
        temp = pqueue.pop()
        if problem.isGoalState(temp[0]):
            return temp[2]
        if temp[0] not in visited:
            visited.append(temp[0])

            for successor, action, stepCost in problem.getSuccessors(temp[0]): # successor, action, stepCost
                if successor not in visited:
                    new_cost = temp[1]  + stepCost
                    new_path = temp[2] + [action]
                    new_state = (successor, new_cost, new_path)
                    pqueue.push(new_state, new_cost + heuristic(new_state[0], problem))


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
