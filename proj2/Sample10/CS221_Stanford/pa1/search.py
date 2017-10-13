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

DEBUG = False

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

def depthFirstSearch(problem):
  return _searchHelper(problem, util.Stack())
  
  # Search the deepest nodes in the search tree first
  # [2nd Edition: p 75, 3rd Edition: p 87]
  
  # Your search algorithm needs to return a list of actions that reaches
  # the goal.  Make sure to implement a graph search algorithm 
  # [2nd Edition: Fig. 3.18, 3rd Edition: Fig 3.7].
  
  # To get started, you might want to try some of these simple commands to
  # understand the search problem that is being passed in:
  
  # print "Start:", problem.getStartState()
  # print "Is the start a goal?", problem.isGoalState(problem.getStartState())
  # print "Start's successors:", problem.getSuccessors(problem.getStartState())

def breadthFirstSearch(problem):
  """
  Search the shallowest nodes in the search tree first.
  [2nd Edition: p 73, 3rd Edition: p 82]
  """
  return _searchHelper(problem, util.Queue())

def uniformCostSearch(problem):
  """Search the node of least total cost first. """
  return _searchHelper(problem, util.PriorityQueue())

def nullHeuristic(state, problem=None):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0

def aStarSearch(problem, heuristic=nullHeuristic):
  "Search the node that has the lowest combined cost and heuristic first."
  return _searchHelper(problem, util.PriorityQueue(), heuristic)
  
def _searchHelper(problem, container, heuristic=nullHeuristic):
  # track which nodes have been expanded
  expanded_states = set()
  
  # track predecessors and directions
  predecessor = {}

  # track distances so far
  distance = {}

  # Initialization
  start_state = problem.getStartState()
  if isinstance(container, util.PriorityQueue):
    container.push(start_state, heuristic(start_state, problem))    
  else:
    container.push(start_state)
  distance[problem.getStartState()] = 0
  goal = None

  # search
  while not container.isEmpty():
    u = container.pop()
    if problem.isGoalState(u):
      goal = u
      break
    # this next check needed when priority queue enqueues something twice with 
    # different priorities. We shouldn't bother expanding anything twice
    if u in expanded_states: continue 
    expanded_states.add(u)
    
    successors = problem.getSuccessors(u)
    for (v, action, cost) in successors:
      if v in expanded_states: continue
      if v in distance and (distance[v] < distance[u] + cost):
        continue

      predecessor[v] = (u, action)
      distance[v] = distance[u] + cost

      if isinstance(container, util.PriorityQueue):
        if DEBUG:
          h_u = heuristic(u, problem)
          h_v = heuristic(v, problem)
          parent_priority = distance[u] + h_u
          child_priority = distance[v] + h_v
          if parent_priority > child_priority:
            print "INCONSISTENT"
            print "distance[parent] =", distance[u], "h = ", h_u
            print u[0],  u[1].asList()
            print "distance[child] =", distance[v], "h = ", h_v
            print v[0], v[1].asList()
        container.push(v, distance[v] + heuristic(v, problem))
      else:
        container.push(v)

  # build up directions list
  directions = []
  v = goal
  while v and v in predecessor:
    (u, action) = predecessor[v]
    directions.append(action)
    v = u
  directions.reverse()
  return directions


  
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
