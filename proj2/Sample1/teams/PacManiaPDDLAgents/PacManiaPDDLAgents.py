# ffAgents.py
# -----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
# This code have been adapted by Nir Lipvetzky and Toby Davies at Unimelb to run FF planner

from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import distanceCalculator
import random, time, util
from game import Directions
import keyboardAgents
import game
from util import nearestPoint
import os
import sys
import math

LOG_MODE = False
def printMaybe(*msg):
    if LOG_MODE:
        print ' '.join([str(i) for i in msg])

NUM_KEYBOARD_AGENTS = 0
class PacManiaPDDLAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, isRed, first='offense', second='defense', rest='offense'):
    AgentFactory.__init__(self, isRed)
    self.agents = [first, second]
    self.rest = rest
    # TODO(aramk) change to isRed
    self.red = isRed

  def getAgent(self, index):
    # TODO(aramk) determine the best starting strategy - perhaps both offensive is better?
    # return self.choose('offense' if index < 2 else 'defense', index)
    if len(self.agents) > 0:
     return self.choose(self.agents.pop(0), index)
    else:
     return self.choose(self.rest, index)

  def choose(self, agentStr, index):
    printMaybe('CHOOSE!!! ', agentStr, index)
    if agentStr == 'keys':
      global NUM_KEYBOARD_AGENTS
      NUM_KEYBOARD_AGENTS += 1
      if NUM_KEYBOARD_AGENTS == 1:
        return keyboardAgents.KeyboardAgent(index)
      elif NUM_KEYBOARD_AGENTS == 2:
        return keyboardAgents.KeyboardAgent2(index)
      else:
        raise Exception('Max of two keyboard agents supported')
    elif agentStr == 'offense':
      return OffensiveReflexAgent(index)
    elif agentStr == 'defense':
      return DefensiveReflexAgent(index)
    else:
      raise Exception("No staff agent identified by " + agentStr)

class AllOffenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)

  def getAgent(self, index):
    return OffensiveReflexAgent(index)

class OffenseDefenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)
    self.offense = False

  def getAgent(self, index):
    self.offense = not self.offense
    if self.offense:
      return OffensiveReflexAgent(index)
    else:
      return DefensiveReflexAgent(index)

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  def __init__( self, index, isOffensive, timeForComputing = .1 ):
    CaptureAgent.__init__( self, index, timeForComputing)
    printMaybe("created")
    self.nextPos = None
    self.visibleAgents = []
    # TODO(aramk) Hybrid agent ability so we can switch between strategies. A better way would be Strategy objects which we can swap at runtime since it still encapsulates each strategy.
    self.isOffensive = isOffensive
    #self.subGoal = (-1,-1)

  def createPDDLobjects(self):
    """
    Return a list of objects describing grid positions of the layout
    This list is used in the PDDL problem file 
    """    
    
    obs = self.getCurrentObservation()
    grid = obs.getWalls()
    locations = grid.asList(False);

    result = '';
    for (x,y) in locations:
      result += 'p_%d_%d '%(x,y)

    return result

  def createPDDLfluents(self):
    """
    Return a list of fluents describing the state space This list is
    used in the PDDL domain file
    """
    
    result = ''
    obs = self.getCurrentObservation()

    #Example: adds a fluent to describe our agent position
    # """
    (myx,myy) = obs.getAgentPosition( self.index )
    # if obs.getAgentState( self.index ).isPacman is True:
    #   result += '(AGENT_AT p_%d_%d) '%(myx,myy)
    # else:
    result += '(AGENT_AT p_%d_%d) '%(myx,myy)
      # """

    # food = self.getFood( obs ).asList(True)
    # result += '(= (cheese-count) %d) ' % len(food)

    #
    # Model opponent team if visible and store them in an array
    #
    
    # """
    self.visibleAgents = []
    other_team = self.getOpponents( obs )
    distances = obs.getAgentDistances()
    for i in other_team:
      
      if obs.getAgentPosition(i) is None: continue
      
      (x,y) = obs.getAgentPosition(i)

      if obs.getAgentState(i).isPacman is False:
        result += '(ENEMY_PHANTOM_AT p_%d_%d) '%(x,y)
      else:
        result += '(ENEMY_PACMAN_AT p_%d_%d) '%(x,y)
        # stores an array with visible agents in current state

      # TODO(yichang) moved this here since we want to keep visible agents for both types of enemies
      # TODO(aramk) should this be called visibleEnemy?
      self.visibleAgents.append(i)
        # """

    #
    # Model teammate agents if visible
    #

    # """
    team = self.getTeam( obs )
    teamPos = []
    for i in team: # Remember: There is no i in team.
      if obs.getAgentPosition(i) is None: continue
      # if i == self.index: continue
      (x,y) = obs.getAgentPosition(i)
      teamPos.append( (x,y) )
      
      if obs.getAgentState(i).isPacman is False:
        result += '(PHANTOM_AT p_%d_%d) '%(x,y)
      else:
        result += '(PACMAN_AT p_%d_%d) '%(x,y)
        # """


    #
    # Food. 
    #    
    # """
    food = self.getFood( obs ).asList(True)
    for (x,y) in food:
      result += '(CHEESE_AT p_%d_%d) '%(x,y)
      # """       

    #
    # Capsule
    #
    # """
    capsule = self.getCapsules( obs )
    for (x,y) in capsule:
      result += '(CHEER_AT p_%d_%d) '%(x,y)
      # """

    #
    # Describe where the agent can move
    #
    # """
    grid = obs.getWalls()
    for y in range(grid.height):
      for x in range(grid.width):
        if grid[x][y] is False:
          if grid[x+1][y] is False:
            result += '(CAN_GO p_%d_%d p_%d_%d) '%(x,y,x+1,y)
          if grid[x-1][y] is False:
            result += '(CAN_GO p_%d_%d p_%d_%d) '%(x,y,x-1,y)
          if grid[x][y+1] is False:
            result += '(CAN_GO p_%d_%d p_%d_%d) '%(x,y,x,y+1)
          if grid[x][y-1] is False:
            result += '(CAN_GO p_%d_%d p_%d_%d) '%(x,y,x,y-1)
       # """   
    return result

  def createPDDLgoal( self ):
    """
    Return a list of fluents describing the goal states
    This list is used in the PDDL problem file 
    """

    # TODO(aramk) since we plan to only return a single goal at a time (usually), perhaps it's better if we replace instead of return in self.createOffensivePDDLgoal()?
    result = ''
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    legalActions = obs.getLegalActions(self.index)
    # TODO(aramk) are we abusing the PDDL planner if we only set the goal to a position one cell away?

    if self.nextPos == myPos:
      # Reached next position

      if self.index > 2:
        printMaybe('Reached')

      self.nextPos = None

    isPacman = obs.getAgentState(self.index).isPacman
    # We are a Pacman and can see an enemy Ghost
    isVulnerablePacman = isPacman and self.canSeeEnemyGhost() # TODO replace False with correct boolean
    # We are an edible ghost and can see an enemy Pacman
    isVulnerableGhost = not isPacman and False # TODO replace False with correct boolean
 
    # TODO(aramk) what if there are more than one enemy? Perhaps this is a good time to use weighed costs with the evaluate function for each possible action?
    if isVulnerablePacman:
      # TODO(aramk) Move away from the enemy ghost
      # enemyGhostPos = self.getEnemyGhostPos()
      # actionCosts = []
      # for i in range(len(enemyGhostPos)):
      #   actionCosts[i] = 
      # printMaybe('actionCosts', enemyGhostPos, actionCosts)
      # self.moveAwayFromPos()


      values = [(self.evaluate(obs, a), a) for a in legalActions]
      # printMaybe('eval time for agent %d: %.4f' % (self.index, time.time() - start))

      maxValue = max(values)
      cost, action = maxValue

      myaction = game.Actions.getSuccessor(myPos, action)

      self.nextPos = myaction

      printMaybe('vulnerable pacman', myPos, maxValue, values, self.nextPos)

      # bestActions = [a for a, v in zip(actions, values) if v >= maxValue-13 or v >= maxValue+13]

      
    elif isVulnerableGhost:
      # TODO(aramk) Move away from enemy pacmen (maybe change tactics if we are actively seeking pacmen)
      pass
    else:
      if self.isOffensive:
        result = self.createOffensivePDDLgoal(result)
      else:
        result = self.createDefensivePDDLgoal(result)

    if self.nextPos:

      if self.index > 2:
        printMaybe('goal', self.nextPos)

      x,y = self.nextPos
      result = '(VISITED_AT p_%d_%d) ' % (x,y)
    return result

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    if self.isOffensive:
      features = self.getOffensiveFeatures(gameState, action)
      weights = self.getOffensiveWeights(gameState, action)
    else:
      features = self.getDefensiveFeatures(gameState, action)
      weights = self.getDefensiveWeights(gameState, action)
    return features * weights

  def getOffensiveFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
      # printMaybe(action, features, successor)
    return features

  def getOffensiveWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

  def getDefensiveFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getDefensiveWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

  def createOffensivePDDLgoal(self, result):
    """
    When a PacMan: Seeks food.
    When a Ghost: Tries to become a PacMan.
    """
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    #if obs.getAgentState(self.index).isPacman:
    if self.nextPos is None or not self.hasFoodAt(self.nextPos):
      self.nextPos = self.findClosestFoodPos() or self.findPatrolPos(True)
    #elif self.nextPos is None:
      # TODO(aramk) only set if we haven't already
      # TODO move to other side using findClosestPosBeyondBoundary DONE
      #self.nextPos = self.findClosestPosBeyondBoundary()

  def createDefensivePDDLgoal(self, result):
    """
    When a PacMan: Tries to become a Ghost.
    When a Ghost: Seeks enemy PacMen.
    """
    # TODO(aramk) make use of getFoodYouAreDefending() and getOpponents()
    # TODO(aramk) this is very similar, can we refactor more with offensive createOffensivePDDLgoal()?
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    #if obs.getAgentState(self.index).isPacman and this.nextPos is None:
      # TODO move to other side using findClosestPosBeyondBoundary DONE
      #this.nextPos = self.findClosestPosBeyondBoundary()
    #else:
    #if self.nextPos is None or not self.hasEnemyPacManAt(self.nextPos):
    if self.nextPos is None:
      if not self.canSeeEnemyPacman():
        self.nextPos = self.findPatrolPos(False)
      else:
        self.nextPos = self.findClosestPacManPos()
    else:
      if self.canSeeEnemyPacman():
        self.nextPos = self.findClosestPacManPos()

  def hasFoodAt(self, pos):
    obs = self.getCurrentObservation()
    x,y = pos
    food = self.getFood(obs)
    return food[int(x)][int(y)] == True

  def hasEnemyAt(self, pos):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    return len([i for i in enemies if obs.getAgentPosition(i) == pos]) >0

  def hasEnemyPacManAt(self, pos):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    result = len([i for i in enemies if obs.getAgentPosition(i) == pos and obs.getAgentState(i).isPacman])
    return result > 0

  def hasEnemyGhostAt(self, pos):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    return len([i for i in enemies if obs.getAgentPosition(i) == pos and not obs.getAgentState(i).isPacman]) >0

  def canSeeEnemyGhost(self):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    result = len([i for i in enemies if not obs.getAgentState(i).isPacman and obs.getAgentPosition(i) != None])
    return result > 0

  def canSeeEnemyPacman(self):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    result = len([i for i in enemies if obs.getAgentState(i).isPacman and obs.getAgentPosition(i) != None])
    return result > 0

  def getEnemyPos(self):
    obs = self.getCurrentObservation()
    enemies = self.getOpponents(obs)
    printMaybe('enemies', enemies)
    # TODO(aramk) this gives None even thouguh we know the current position
    return [obs.getAgentPosition(i) for i in enemies]

  def getEnemyGhostPos(self):
    obs = self.getCurrentObservation()
    pos = self.getEnemyPos()
    printMaybe('getEnemyPos', pos)
    return [i for i in self.getEnemyPos() if not obs.getAgentState(i).isPacman]

  def isOnleftSide(self):
    """
    True if the agent is on the left side of the grid.
    """
    obs = self.getCurrentObservation()
    x, y = obs.getAgentPosition(self.index)
    grid = obs.getWalls()
    return x < grid.width / 2

  def findClosestPosBeyondBoundary(self):
    """
    Finds the closest position beyond the boundary (on the opposite side given).
    isleftSide is true if the agent is on the left side
    """
    #TODO (yichang) use self.isOnleftSide() to distinguish DONE 
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    grid = obs.getWalls()
    tempList = []
    myx, myy = myPos
    if self.isOnleftSide():
      closest_bound_x = grid.width / 2
    else:
      closest_bound_x = grid.width / 2 - 1
    for y in range(grid.height):
      if grid[closest_bound_x][y] is False:
        tempList.append((closest_bound_x,y))
    minDistance, minPos = min([(self.getMazeDistance(myPos, aPos), aPos) for aPos in tempList])
    return minPos

  def findClosestFoodPos(self):
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    # TODO(aramk) asList() already accepts True as the default value, no need for this?
    foodList = self.getFood(obs).asList(True)
    minPos = None
    if len(foodList):
      tmpList = [(self.getMazeDistance(myPos, food), food) for food in foodList]
      minDistance, minPos = min(tmpList)
      # x,y = minPos
      # printMaybe(tmpList, minPos)
      # result += '(VISITED_AT p_%d_%d) '%(x,y)
    return minPos

  def findClosestPacManPos(self):
    pacmen = []
    obs = self.getCurrentObservation()
    myPos = obs.getAgentPosition(self.index)
    minPos = None
    for i in self.visibleAgents:
      if obs.getAgentState(i).isPacman:
        pacmen.append(obs.getAgentPosition(i))
    if len(pacmen):
      minDistance, minPos = min([(self.getMazeDistance(myPos, pacman), pacman) for pacman in pacmen])
    return minPos

  def findPatrolPos(self, isOffensive):
    obs = self.getCurrentObservation()
    grid = obs.getWalls()
    myPos = obs.getAgentPosition(self.index)
    myx, myy = myPos

    if (self.red and isOffensive) or (not self.red and not isOffensive):
      limit_west = grid.width / 2
      limit_east = grid.width - 2
    elif (self.red and not isOffensive) or (not self.red and isOffensive):
      limit_west = 1
      limit_east = grid.width / 2 - 1

    random_list = []

    close_to_west_pos = []
    close_to_east_pos = []

    for y in range(grid.height):
      for x in range(limit_west, limit_east):
        if grid[x][y] is False:
          if abs(x - limit_west) > abs(x - limit_east):
            close_to_east_pos.append((x,y))
          else:
            close_to_west_pos.append((x,y))

    dist_to_west = abs(myx - limit_west)
    dist_to_east = abs(myx - limit_east)

    if dist_to_west > dist_to_east:
      random_list = close_to_west_pos
    else:
      random_list = close_to_east_pos

    result = random_list[int(random.random() * len(random_list))]

    return result

  def generatePDDLproblem(self):
    """
    outputs a file called problem.pddl describing the initial and
    the goal state
    """

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(cur_dir, "problem%d.pddl"%self.index),"w");
    lines = list();
    lines.append("(define (problem pacman-problem)\n");
    lines.append("   (:domain pacman-strips)\n");
    lines.append("   (:objects \n");
    lines.append( self.createPDDLobjects() + "\n");
    lines.append(")\n");
    lines.append("   (:init \n");
    lines.append("   ;primero objetos \n");
    lines.append( self.createPDDLfluents() + "\n");
    lines.append(")\n");
    lines.append("   (:goal \n");          
    lines.append("  ( and  \n");
    lines.append( self.createPDDLgoal() + "\n");
    lines.append("  )\n");
    lines.append("   )\n");
    lines.append(")\n");

    f.writelines(lines);
    f.close();  

  def runPlanner( self ):
    """
    runs the planner with the generated problem.pddl. The domain.pddl
    in our case is always the same, as we simply describe once all
    possible bestActions. The output is redirected into a text file.
    """
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(cur_dir)
    os.system("./ff -o ./domain.pddl -f ./problem%d.pddl > solution%d.txt"%(self.index,self.index) );

  def parseSolution( self ):
    """
    Parse the solution file of FF, and selects the first action of the
    plan. Note that you could get  all the actions, not only the first
    one, and call the planner just  when an action in the plan becomes
    unapplicable or the some new  relevant information of the state of
    the game has changed.
    """

    f = open("solution%d.txt"%self.index,"r");
    lines = f.readlines();
    f.close();

    for line in lines:
      pos_exec = line.find("0: "); #First action in solution file
      if pos_exec != -1: 
        command = line[pos_exec:];
        command_splitted = command.split(' ')
       
        x = int(command_splitted[3].split('_')[1])
        y = int(command_splitted[3].split('_')[2])

        return (x,y)

      #
      # Empty Plan, Use STOP action, return current Position
      #
      if line.find("ff: goal can be simplified to TRUE. The empty plan solves it") != -1:
        return  self.getCurrentObservation().getAgentPosition( self.index )


  def chooseAction(self, gameState):
    """
    Generate the PDDL problem representing the state of the problem and the goals of the agent.
    Run the planner.
    Parse the solution.
    Send the first action of the plan.
    """
    actions = gameState.getLegalActions(self.index)

    # TODO(aramk) we may end up being able to use many PDDL executions and take the first action of each into a list and then use the best out of this list

    # # You can profile your evaluation time by uncommenting these lines
    # # start = time.time()
    # values = [self.evaluate(gameState, a) for a in actions]
    # # printMaybe('eval time for agent %d: %.4f' % (self.index, time.time() - start))

    bestAction = 'Stop'
    
    self.generatePDDLproblem()
    self.runPlanner()
    soln = self.parseSolution()
    if soln:
      (newx,newy) = soln

      for a in actions:
        succ = self.getSuccessor(gameState, a)
        if succ.getAgentPosition( self.index ) == (newx, newy):
          bestAction = a
          break

    return bestAction
 
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

class OffensiveReflexAgent(ReflexCaptureAgent):
  def __init__(self, index):
    ReflexCaptureAgent.__init__(self, index, True)

class DefensiveReflexAgent(ReflexCaptureAgent):
  def __init__(self, index):
    ReflexCaptureAgent.__init__(self, index, False)
