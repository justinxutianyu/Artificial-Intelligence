# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called
by Pacman agents (in searchAgents.py).
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
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()

def serchUsingFringeWithoutCost(problem, fringe):
    """
    Author: Daniel
    :param problem: problem to be solved
    :param fringe: depending on the type (Stack, Queue), one or another algorithm will be implemented
    :return: return a list of actions
    """

    # Push initial state to fringe
    fringe.push((problem.getStartState(), []))
    # Create states array to check if a state has been already visited
    closed = {}
    # Infinite loop until goal or until we run out of states
    while True:
        # Check if there are more paths in fringe
        if fringe.isEmpty():
            return []
        # Remove first element from fringe, and get current state and action
        myState, myActions = fringe.pop()
        # Check if we are in goal state
        if problem.isGoalState(myState):
            return myActions
        # Expand state if this is a new state
        if myState not in closed:
            # Append state to closed
            closed[myState] = 0
            # Get new states and form new paths
            for successor in problem.getSuccessors(myState):
                # Duplicate actions array
                newActions = list(myActions)
                # Append new action to actions
                newActions.append(successor[1])
                # Add new path to fringe
                fringe.push((successor[0], newActions))
    return []

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first
    [2nd Edition: p 75, 3rd Edition: p 87]

    Your search algorithm needs to return a list of actions that reaches
    the goal.  Make sure to implement a graph search algorithm
    [2nd Edition: Fig. 3.18, 3rd Edition: Fig 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    # Create fringe with a stack
    fringe = util.Stack()
    # Calculate search
    return serchUsingFringeWithoutCost(problem, fringe)

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first.
    [2nd Edition: p 73, 3rd Edition: p 82]
    """
    "*** YOUR CODE HERE ***"
    # Create fringe with a queue
    fringe = util.Queue()
    # Calculate search
    aux = serchUsingFringeWithoutCost(problem, fringe)
    return aux

def serchUsingFringeWithCost(problem, fringe, heuristic=None):
    """
    Author: Daniel
    :param problem: problem to be solved
    :param fringe: depending on the type (Stack, Queue), one or another algorithm will be implemented
    :return: return a list of actions
    """
    # Create states array to check if a state has been already visited
    closed = {}
    # Push initial state to fringe
    fringe.push((problem.getStartState(), [], 0), 0)
    # Infinite loop until goal or until we run out of states
    while True:
        # Check if there are more paths in fringe
        if fringe.isEmpty():
            return []
        # Remove first element from fringe, and get current state, action and priority
        myState, myActions, myPriority = fringe.pop()
        # Check if we are in goal state
        if problem.isGoalState(myState):
            return myActions
        # Expand state if this is a new state
        if myState not in closed:
            # Append state to closed
            closed[myState] = 0
            # Get new states and form new paths
            for successor in problem.getSuccessors(myState):
                #Duplicate actions array
                newActions = list(myActions)
                # Append new action to actions
                newActions.append(successor[1])
                # Calculate new priorities
                newPriority = myPriority + successor[2]
                heuristicPriority = 0
                if heuristic is not None:
                    heuristicPriority = heuristic(successor[0], problem)
                # Add new path to fringe
                fringe.push((successor[0], newActions, newPriority), newPriority + heuristicPriority)
    return []

def uniformCostSearch(problem):
    "Search the node of least total cost first. "
    "*** YOUR CODE HERE ***"
    # Create fringe with a PriorityQueue
    fringe = util.PriorityQueue()
    print "UCS Started"
    return serchUsingFringeWithCost(problem, fringe)

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    "Search the node that has the lowest combined cost and heuristic first."
    "*** YOUR CODE HERE ***"
    # Create fringe with a priority queue, where we pass it the heuristic
    fringe = util.PriorityQueue()
    # Calculate search
    return serchUsingFringeWithCost(problem, fringe, heuristic)

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
