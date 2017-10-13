# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from searchAgents import mazeDistance
from util import manhattanDistance
from game import Directions

import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()
    # print legalMoves

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    "*** YOUR CODE HERE ***"
    # Calculate distance from ghosts
    ghost_d = 1000
    ghost_i = 0
    for i, ghost in enumerate(newGhostStates):
      d = manhattanDistance(newPos, ghost.getPosition())
      if d < ghost_d:
        ghost_d = d
        ghost_i = i

    danger = False
    if ghost_d < 3:
      danger = True

    if newScaredTimes[ghost_i] > ghost_d:
      ghost_d = -ghost_d + 20
      danger = False
    else:
      ghost_d = 0

    # Calculate distance from closest food
    food_d = 1000
    food_i = -1
    for i, food_pos in enumerate(newFood.asList()):
      d = manhattanDistance(newPos, food_pos)
      if d < food_d:
        food_d = d
        food_i = i

    if food_d > 999:
      food_d = 0
    maze_d = 1000
    if food_i > -1:
      maze_d = mazeDistance(newPos, newFood.asList()[food_i], successorGameState)

    # Get change in score for visiting the new position
    score_bonus = successorGameState.getScore() - currentGameState.getScore()

    if score_bonus >= 0:
      food_d = food_d / 10
      maze_d = maze_d / 10

    score = -food_d + score_bonus - maze_d + ghost_d

    if danger:
      return ghost_d - 100

    return score

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

def do_action(gameState, agentIndex, allActions):
    if len(allActions) <= 0:
      return [gameState], []
    if gameState.isLose() or gameState.isWin():
      return [gameState], [[Directions.SOUTH]]
    indexs = list(agentIndex)
    all_actions = list(allActions)
    actions = all_actions.pop()
    index = indexs.pop()
    final_states = []
    final_actions = []
    for action in actions:
      successor = gameState.generateSuccessor(index, action)
      score = do_action(successor, indexs, all_actions)
      final_states = final_states + score[0]
      if len(score[1]) <= 0:
        final_actions.append([action])
      for prev_action in score[1]:
        final_actions.append([action] + prev_action)
    return final_states, final_actions

def max_value(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v = -float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  if depth <= 0:
    return evalFn(gameState), Directions.STOP
  if gameState.isWin():
    return evalFn(gameState), Directions.STOP
  depth -= 1

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = min_value(successor, adversaryIndex, agentIndex, depth, evalFn)
    if (v < succ[0]):
      v = succ[0]
      best_action = successors[1][i]

  return v, best_action

def min_value(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v = float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = max_value(successor, adversaryIndex, agentIndex, depth, evalFn)
    if (v > succ[0]):
      v = succ[0]
      best_action = successors[1][i]
  return v, best_action

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    reward, action = max_value(gameState, [0], range(1, gameState.getNumAgents()), self.depth, self.evaluationFunction)
    return action[0]

def max_value_prune(gameState, agentIndex, adversaryIndex, depth, evalFn, alfa, beta):
  v = -float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  if depth <= 0:
    return evalFn(gameState), Directions.STOP
  if gameState.isWin():
    return evalFn(gameState), Directions.STOP
  depth -= 1

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = min_value_prune(successor, adversaryIndex, agentIndex, depth, evalFn, alfa, beta)
    if (v < succ[0]):
      v = succ[0]
      best_action = successors[1][i]
      if v >= beta:
        return v, best_action
      alfa = max(alfa, v)
  return v, best_action

def min_value_prune(gameState, agentIndex, adversaryIndex, depth, evalFn, alfa, beta):
  v = float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = max_value_prune(successor, adversaryIndex, agentIndex, depth, evalFn, alfa, beta)
    if (v > succ[0]):
      v = succ[0]
      best_action = successors[1][i]
      if v <= alfa:
        return v, best_action
      beta = min(beta, v)
  return v, best_action

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    reward, action = max_value_prune(gameState, [0], range(1, gameState.getNumAgents()), self.depth, self.evaluationFunction, -float("inf"), float("inf"))
    return action[0]

def max_value_exp(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v = -float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  if depth <= 0:
    return evalFn(gameState), Directions.STOP
  if gameState.isWin():
    return evalFn(gameState), Directions.STOP
  depth -= 1

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = exp_value(successor, adversaryIndex, agentIndex, depth, evalFn)
    if (v < succ[0]):
      v = succ[0]
      best_action = successors[1][i]

  return v, best_action

def exp_value(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v = 0
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  p = 1.0 / len(successors[0])
  for i, successor in enumerate(successors[0]):
    succ = max_value_exp(successor, adversaryIndex, agentIndex, depth, evalFn)
    v += succ[0] * p

  return v, best_action

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    reward, action = max_value_exp(gameState, [0], range(1, gameState.getNumAgents()), self.depth, self.evaluationFunction)
    return action[0]

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    Nothing too fancy
  """
  "*** YOUR CODE HERE ***"

  newPos = currentGameState.getPacmanPosition()
  newFood = currentGameState.getFood()
  newGhostStates = currentGameState.getGhostStates()
  newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

  "*** YOUR CODE HERE ***"
  # Calculate distance from closest food
  food_d = 1000
  for i, food_pos in enumerate(newFood.asList()):
    d = manhattanDistance(newPos, food_pos)
    if d < food_d:
      food_d = d

  if food_d > 999:
    food_d = 0

  # Get change in score for visiting the new position
  score_bonus = currentGameState.getScore()

  score = -food_d + score_bonus

  return score

# Abbreviation
better = betterEvaluationFunction

heuristicInfo = {}

def bestEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    Nothing too fancy
  """
  "*** YOUR CODE HERE ***"

  newPos = currentGameState.getPacmanPosition()
  newFood = currentGameState.getFood()
  food_list = newFood.asList()
  newGhostStates = currentGameState.getGhostStates()
  newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
  newCapsules = currentGameState.getCapsules()

  # Calculate distance from closest food
  food_min = 1000
  food_d = []
  food_i = []
  food_num = len(food_list)  # number food
  food_avg = 0  # avg food dist
  for i, food_pos in enumerate(food_list):
    d = manhattanDistance(newPos, food_pos)
    food_d.append(d)
    food_avg += d
    if d < food_min:
      food_min = d
      food_i = [i]
    elif d == food_min:
      food_i.append(i)

  # Calculate real distance from closest food
  food_maze_min = 0
  if food_num > 0:
    food_avg /= food_num
    food_maze_min = 1000
    for i in food_i:
      # This is so we remember the mazeDistance already computed
      try:
         d = heuristicInfo[newPos + food_list[i]]
      except KeyError:
        d = mazeDistance(newPos, food_list[i], currentGameState)
        heuristicInfo[newPos + food_list[i]] = d
        heuristicInfo[food_list[i] + newPos] = d
      food_maze_min = min(food_maze_min, d)

  # Calculate distance from capsules
  capsule_min = 1000
  capsule_i = []
  capsule_num = len(newCapsules)  # number capsules
  for i, capsule_pos in enumerate(newCapsules):
    d = manhattanDistance(newPos, capsule_pos)
    if d < capsule_min:
      capsule_min = d
      capsule_i = [i]
    elif d == capsule_min:
      capsule_i.append(i)

  # Calculate real distance from closest capsules
  capsule_maze_min = 0
  if capsule_num > 0:
    capsule_maze_min = 1000
    for i in capsule_i:
      # This is so we remember the mazeDistance already computed
      try:
        d = heuristicInfo[newPos + newCapsules[i]]
      except KeyError:
        d = mazeDistance(newPos, newCapsules[i], currentGameState)
        heuristicInfo[newPos + newCapsules[i]] = d
        heuristicInfo[newCapsules[i] + newPos] = d
      capsule_maze_min = min(capsule_maze_min, d)

  # Calculate real distance from ghosts
  ghosts_maze_min = 1000
  ghosts_avg = 0
  ghosts_num = len(newGhostStates)
  scared_maze_min = 1000
  scared_avg = 0
  scared_num = 0
  for i, ghost in enumerate(newGhostStates):
    ghost_pos = ghost.getPosition()
    # This is so we remember the mazeDistance already computed
    try:
      d = heuristicInfo[newPos + ghost_pos]
    except KeyError:
      d = mazeDistance(newPos, ghost_pos, currentGameState)
      heuristicInfo[newPos + ghost_pos] = d
      heuristicInfo[ghost_pos + newPos] = d
    # Scared and close
    if (newScaredTimes[i] > 0):
      scared_num += 1
      scared_avg += d
      scared_maze_min = min(scared_maze_min, d)
    else:
      ghosts_avg += 1
      ghosts_maze_min = min(ghosts_maze_min, d)

  scared_score = -10
  if scared_num > 0:
    scared_avg /= scared_num
    scared_score = scared_maze_min*2 + scared_num * 2

  ghosts_score = 10
  if ghosts_num - scared_num > 0:
    ghosts_avg /= (ghosts_num - scared_num)
    ghosts_score = ghosts_maze_min + ghosts_avg/2.0

  # Get change in score for visiting the new position
  score_bonus = currentGameState.getScore()
  if ghosts_num == scared_num:
    score_bonus += 20

  food_score = food_maze_min + food_num * 2
  capsule_score = capsule_maze_min*4 - capsule_num*2

  score = score_bonus - food_maze_min*2 - food_num - capsule_maze_min - scared_num

  return score


class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest

    Simple, expectimax with betterEvaluationFunction
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    gameState.getFood()
    "*** YOUR CODE HERE ***"
    reward, action = max_value_exp_smart(gameState, [0], range(1, gameState.getNumAgents()), 3, bestEvaluationFunction)
    return action[0]


def max_value_exp_smart(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v = -float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      actions = gameState.getLegalActions()
      try:
        actions.remove(Directions.STOP)
      except ValueError:
        pass
      all_actions.append(actions)

  if depth <= 0:
    return evalFn(gameState), Directions.STOP
  if gameState.isWin():
    return evalFn(gameState), Directions.STOP
  depth -= 1

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    succ = min_value_exp_smart(successor, adversaryIndex, agentIndex, depth, evalFn)
    if (v < succ[0]):
      v = succ[0]
      best_action = successors[1][i]
  return v, best_action


def min_value_exp_smart(gameState, agentIndex, adversaryIndex, depth, evalFn):
  v_avg = 0
  v_min = float("inf")
  all_actions = []
  for index in agentIndex:
    if index > 0:
      all_actions.append(gameState.getLegalActions(index))
    else:
      all_actions.append(gameState.getLegalActions())

  successors = do_action(gameState, agentIndex, all_actions)
  best_action = Directions.STOP
  p = 1.0 / len(successors[0])
  pacman_actions = []
  best_pacman_action = Directions.STOP
  for i, successor in enumerate(successors[0]):
    # if depth <= 0:
    #   print successor
    succ = max_value_exp_smart(successor, adversaryIndex, agentIndex, depth, evalFn)
    v_avg += succ[0] * p
    if v_min > succ[0]:
      best_pacman_action = succ[1]
    v_min = min(v_min, succ[0])
    pacman_actions.append(succ[1])
  prob_attack = 0.8
  v = prob_attack * v_min + (1-prob_attack) * v_avg
  return v, best_action