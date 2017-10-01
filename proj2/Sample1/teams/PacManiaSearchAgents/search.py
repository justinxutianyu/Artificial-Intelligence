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
           

def tinyMazeSearch(problem):
  """
  Returns a sequence of moves that solves tinyMaze.  For any other
  maze, the sequence of moves will be incorrect, so only use this for tinyMaze
  """
  from game import Directions
  s = Directions.SOUTH
  w = Directions.WEST
  return  [s,s,w,s,w,w,s,w]

def genericSearch(problem, frontier):
  '''
  A generic search function which all other use.
    
    frontier: A data structure from util.py which has push() and pop().
  '''

  from game import Directions, Configuration, Actions

  # Stores the states which are already visited.
  visited_states = set()
  # Stores the states which are expanded (but not necessarily visited yet).
  explored_states = set()
  # The actions travelled during the search.
  actions = []

  start_state = problem.getStartState()
  node = [start_state, None, 0, 0, None]
  frontier.push(node)

  while not frontier.isEmpty():
    node = frontier.pop()
    state = node[0] # state, _, _, _ = node
    visited_states.add(state)

    # Found a goal state, follow previous node links to return chain of actions
    if problem.isGoalState(state):
      curr_node = node
      while curr_node is not None:
        action = curr_node[1] # _, action, _, prev = curr_node
        prev = curr_node[4]
        if action is not None:
          actions.append(action)
        curr_node = prev
      actions.reverse()
      return actions

    # Expand the current node
    successors = problem.getSuccessors(state)
    if successors is not None:
      for successor in successors:
        # Convert to lists since:
        #   1) we'll be referencing previous states and it's not as tractable to copy them each time.
        #   2) we'll be appending elements so a mutable data structure makes sense.
        #   3) we're using an imperative language and mutable data structures are available.
        # However, we could also implement this using immutable tuples in a functional style, or even a Node class.
        # Since it's not a requirement and using them will likely result in a performance loss due to exponential data growth we will use lists.
        successor = list(successor)
        # Add cost to total cost
        successor.append(node[3] + successor[2])
        # Reference to the previous node
        successor.append(node)
        s_state = successor[0] # s_state, _, _, _ = successor

        # Only add state for expansion if we haven't done so already and haven't visited this state before
        if s_state not in visited_states and s_state not in explored_states:
          frontier.push(successor)
          explored_states.add(s_state)

  # No paths found, return no actions.
  return []

def depthFirstSearch(problem):
  """
  Search the deepest nodes in the search tree first [p 85].
  
  Your search algorithm needs to return a list of actions that reaches
  the goal.  Make sure to implement a graph search algorithm [Fig. 3.7].
  
  To get started, you might want to try some of these simple commands to
  understand the search problem that is being passed in:
  
  print "Start:", problem.getStartState()
  print "Is the start a goal?", problem.isGoalState(problem.getStartState())
  print "Start's successors:", problem.getSuccessors(problem.getStartState())
  """
  return genericSearch(problem, frontier = util.Stack())

def breadthFirstSearch(problem):
  "Search the shallowest nodes in the search tree first. [p 81]"
  return genericSearch(problem, frontier = util.Queue())
      
def uniformCostSearch(problem):
  "Search the node of least total cost first. "
  return genericSearch(problem, frontier = util.PriorityQueueWithFunction(lambda s: s[3]))

def nullHeuristic(state, problem=None):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0

def aStarSearch(problem, heuristic=nullHeuristic):
  "Search the node that has the lowest combined cost and heuristic first."
  return genericSearch(problem, frontier = util.PriorityQueueWithFunction(lambda s: s[3] + heuristic(s[0], problem)))

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
