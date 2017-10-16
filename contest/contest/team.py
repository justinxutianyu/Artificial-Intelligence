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

######################################################################
#
#  This is our entry to the Adversarial PACMAN contest for our AI 
#  Planning for Autopnomy Subject, 2016 sem 2. This is extended from 
#  code that has been provided to us by UC Berkley. Please refer to 
#  statement above. 
#
#  Tim Chen was in charge of the Attacking Agent.
#  Wilkins Leong was in charge of the Defensive Agent. (Line 432).
#  
######################################################################

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AStarAgent', second = 'DefensiveAStarAgent'):
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

##########
# Agents #
##########

class AStarAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.start = gameState.getAgentPosition(self.index)
    # self.currentFooad=len(self.getFood(gameState).asList())
    self.stepOfFood1=1
    self.stepOfFood2=2
    self.stepOfFood3=3
    self.foodEachTime=1
    self.totalFood=len(self.getFood(gameState).asList())
    # self.ifReturnFood

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    #get succuessor's game state
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    # actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    foodLeft = len(self.getFood(gameState).asList())
    # self.ScoreThreshold-=self.getScore(gameState)
    # You can profile your evaluation time by uncommenting these lines

    # if self.getScore(gameState)>0:
    #   self.foodEachTime+=self.foodEachTime

    if self.getScore(gameState)>0:
      self.foodEachTime=1
    else:
      self.foodEachTime=1

    # start = time.time()

    #getting food
    # self.currentFooad=len(self.getFood(gameState).asList())
    # if foodLeft==18 or 19:
    # if (self.totalFood-len(self.getFood(gameState).asList())-self.getScore(gameState))!=1:
    if gameState.getAgentState(self.index).numCarrying<self.foodEachTime:


      actions= self.aStartSearch(gameState)
      # print "actions: "
      # print actions

      # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    else:
      # print "going back"
      actions=self.aStarSearchBackToSaveDot(gameState,self.start)
      # save dots in shortest path
      # backactions=gameState.getLegalActions(self.index)
      # bestDist = 9999
      # for action in backactions:
      #   successor = self.getSuccessor(gameState, action)
      #   pos2 = successor.getAgentPosition(self.index)
      #   dist = self.getMazeDistance(self.start,pos2)
      #   if dist < bestDist:
      #     bestAction = action
      #     bestDist = dist
      # return bestAction

    
    # print "actions length:" 
    # print len(actions)
    # print "action :"
    # print  actions[0]

    # unslovable, random actions
    if len(actions)==0:
      unslovable = gameState.getLegalActions(self.index)
      return random.choice(unslovable)

    return actions[0]

    # need to be changed 
    # return random.choice(actions)

  def retrieveActionListFromPath(self,stateChange_path):
    actions=list()
    for i in range(1,len(stateChange_path)):
        actions.append(stateChange_path[i][1])

    return actions

  def aStartSearch(self,startState):
  # goal state can be defined as food left 2 or how many has taken
     # print "old search" 
     priority_queue=util.PriorityQueue()

     start_state=startState

     start_Form=(start_state,"no action",-1,0)
     stateChange_path=list()
     stateChange_path.append(start_Form)
     priority_queue.push(stateChange_path,0+self.heuristicForFood(start_state))

     visited_list=dict()
   
     start = time.time()
     # depth=0;
     while (not priority_queue.isEmpty()):
      # depth+=1     
      # print "counter 1111111111"
      current_list=priority_queue.pop()
      # print "current_list: "
      # print current_list
      end_of_list=len(current_list)-1
      current_state=current_list[end_of_list][0]
      current_cost=current_list[end_of_list][3]
      # print "current state:"
      # print current_state
      if time.time() - start >0.9 :

          if self.foodEachTime>1:
            self.foodEachTime-=self.foodEachTime


          # print "ends in depth"
          return self.retrieveActionListFromPath(current_list)
          # depthActions = startState.getLegalActions(self.index)
          # randomActions=list()
          # randomActions.append(random.choice(depthActions))
          # return randomActions       

      if self.ifAchieveFoodGoal(current_state) is True:
        # print "retrieve goal !!!!!!!!!!!!!!!!!!!"
        # print "szie of the queue: "
        # print  priority_queue.count
        return self.retrieveActionListFromPath(current_list)
      if current_state not in visited_list or current_cost<visited_list.get(current_state,-1):

          # visited_list[current_state]=current_cost
          visited_list[current_state]=current_cost
          # j=0;
          for new_node in self.getAllSuccessorInFormat(current_state):
           
              accumulated=current_cost+new_node[2]
              successors_list=list(current_list)
              form=(new_node[0],new_node[1],new_node[2],accumulated)
              successors_list.append(form)
              priority_queue.push(successors_list,accumulated+self.heuristicForFood(new_node[0]))
      # print "-----------------"
      # if depth==400 :
      #     # return self.retrieveActionListFromPath(current_list)
      #     depthActions = current_state.getLegalActions(self.index)
      #     return random.choice(depthActions)    
      # it cannot find a path
     return list()
       
  def ifAchieveFoodGoal(self,gameState):
    """
    This function just define how much food it take and it should return to save point 
    """
    foodLeft = len(self.getFood(gameState).asList())
    # print "check food left: "
    # print foodLeft
    # if foodLeft<=self.currentFooad-1:
    # if (self.totalFood-len(self.getFood(gameState).asList())-self.getScore(gameState))==1:
    if gameState.getAgentState(self.index).numCarrying==self.foodEachTime:
      return True
    else:
      return False

  def getAllSuccessorInFormat(self,startState):
     actions = startState.getLegalActions(self.index)
     actions.remove(Directions.STOP)

     reversed_direction = Directions.REVERSE[startState.getAgentState(self.index).configuration.direction]
    
     if reversed_direction in actions and len(actions) > 1:
        actions.remove(reversed_direction)

     successor_list=list()

     # print "actions: "
     # print actions

     #assume that action cost is 1
     for action in actions:
      successor = self.getSuccessor(startState, action)
      #calculate action cost
      successor_position=successor.getAgentPosition(self.index)

      action_cost = self.getMazeDistance(startState.getAgentPosition(self.index),successor_position)
      # action_cost = 1

      format=(successor,action,action_cost)
      # print "heuristic in food "
      # print self.heuristicForFood(successor)
      successor_list.append(format)

     return successor_list

  def heuristicForFood(self,gameState):
    """
    define the heuristic of a specified game state
    """
    
    heuristic=0

    capsuleList=self.getCapsules(gameState)

    foodList = self.getFood(gameState).asList()
    foodList+=capsuleList
    foodLeft=len(foodList)

    myPos = gameState.getAgentState(self.index).getPosition()
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])

    # if there are enemies
    enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(invaders)>0:
      # print "meet enemies"
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      # heuristic+=float("inf")

      return len(invaders)*999999
      # print "find enemies: "
      # print max(dists)*100
    

    heuristic=foodLeft+minDistance

    return heuristic

  def heuristic2(self,gameState):
    heuristic=0;
    foodList = self.getFood(gameState).asList()
    myPos = gameState.getAgentState(self.index).getPosition()

    maxDistance = max([self.getMazeDistance(myPos, food) for food in foodList])

    maxDist=0
    for food in foodList:
      dist=self.getMazeDistance(myPos, food)
      if maxDist<dist:
        maxDist=dist
        maxPos1=food
    foodList.remove(maxPos1)
    maxDist=0
    for food in foodList:
      dist=self.getMazeDistance(myPos, food)
      if maxDist<dist:
        maxDist=dist
        maxPos2=food
    maxPosList=list()
    maxPosList.append(maxPos1)
    maxPosList.append(maxPos2) 
    x=self.getMazeDistance(maxPos1, maxPos2)
    y=min([self.getMazeDistance(myPos, food) for food in maxPosList])

    return x+y
  def aStarSearchBackToSaveDot(self, gameState, goalCoord):
      """Search the node that has the lowest combined cost and heuristic first."""

      start = time.time()

      frontier = util.PriorityQueue()
      # maybe look at this.... DOES PRIORITY QUEUE DO WHAT YO UTHINK ITS DOING
      startState = gameState
      start_coord = startState.getAgentPosition(self.index)
      #print "this is startState: "
      #print startState
      #print "this is our starting coord: "
      #print start_coord

      frontier.push((startState, []), self.heuristicForGoingBack(startState,start_coord, goalCoord))
   

      visited = []

      while not frontier.isEmpty():
          node = frontier.pop()

          coord = node[0].getAgentPosition(self.index)
          actions = node[1]

          #print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

          if time.time() - start >= 0.8:
            # print "returned actions early in saving dots!"
            return actions


          if coord == goalCoord:# if coord == goalCoord # so we really need to define the goal coords
              #print "we are at goal state now"
              return actions

          if coord not in visited:
              #print "okay we are not at goal yet, we are cotinuing on.."
              visited.append(coord)
              #print "this is visi ted: "
              #print visited

              for successor in self.getAllSuccessorInFormat(node[0]):

                  nextCoord = successor[0].getAgentPosition(self.index)
                  nextDirection = successor[1]



                  if not nextCoord in visited:
                      new_actions = actions + [nextDirection]
                      #print "this is new actions: " 
                      #print new_actions
                      #print "this is length of new actions: "
                      #print len(new_actions)
                      score = len(new_actions) + self.heuristicForGoingBack(successor[0],nextCoord, goalCoord)
                      frontier.push((successor[0], new_actions), score)

      return []

  def heuristicForGoingBack(self, currentState,nextCoord, goalCoord):

    heuristic=0;
    heuristic=self.getMazeDistance(nextCoord,goalCoord)

    myPos = currentState.getAgentState(self.index).getPosition()
    enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(currentState)]
    invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(invaders)>0:
      # print "meet enemies"
      # print "enemies in going back"
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      # heuristic+=float("inf")

      return len(invaders)*999999

    return heuristic


#####################defensive##########################################

class DefensiveAStarAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        self.start = gameState.getAgentPosition(self.index)
        # self.currentFooad=len(self.getFood(gameState).asList())
        self.foodEachTime = 1
        self.totalFood = len(self.getFood(gameState).asList())
        # self.ifReturnFood

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        # get succuessor's game state
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def cluster_finder_list(self, gameState):
        sizes_dict = {}
        sizes_list = []
        defensefoodmatrix = self.getFoodYouAreDefending(gameState)


        i = 0
        j = 0
        for row in defensefoodmatrix:
            for element in defensefoodmatrix[i]:

                # print defensefoodmatrix[i][j]

                if defensefoodmatrix[i][j] == True:
                    count = self.cluster_counter(defensefoodmatrix, i, j, 0)
                    sizes_list.append(count)
                    sizes_dict[str(count)] = (i,j)

                j += 1
            i += 1
            j = 0
        #print sizes_list
        #print sizes_dict

        return sizes_dict

    def cluster_counter(self, array, i, j, count):
        if array[i][j] == True:
            array[i][j] = False

            if array[i - 1][j] == True:
                    # count += 1
                array[i - 1][j] = False
                count += self.cluster_counter(array, i - 1, j, count)

            elif array[i][j - 1] == True:
                # count += 1
                array[i - 1][j] = False
                count += self.cluster_counter(array, i, j - 1, count)

            elif array[i + 1][j] == True:
                    # count += 1
                array[i - 1][j] = False
                count += self.cluster_counter(array, i + 1, j, count)

            elif array[i][j + 1] == True:
                    # count += 1
                array[i - 1][j] = False
                count += self.cluster_counter(array, i, j + 1, count)

        return count + 1

    def chooseAction(self, gameState):
        # chooses among actions, that will be based on what my AStar
        # returns to bring us nearer to the goal, based on heauristics
        
        #values = [self.evaluate(gameState, a) for a in actions]
        #print values

        #start = time.time()

        goalCoord = self.goalDefiner(gameState)

        actions = self.aStarSearchDEF(gameState, goalCoord)       

        #print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
        #astar is not returning actions properly so FIX THIS PLEASE

        if actions == []:
          #print "empty actions list!"
          actions = gameState.getLegalActions(self.index)
          return random.choice(actions)

        #exit()

        return actions[0]

    def goalDefiner(self, gameState):

        #if an enemy is in sight!

        #print "this is the opponenet position: "
        enemies = self.getOpponents(gameState)
        #print enemies

        enemy1State = gameState.getAgentState(enemies[0])
        enemy2State = gameState.getAgentState(enemies[1])

        enemy1Pos = enemy1State.getPosition()
        enemy2Pos = enemy2State.getPosition()


        if enemy1Pos != None and enemy1State.isPacman:
          return enemy1Pos
        if enemy2Pos != None and enemy1State.isPacman:
          return enemy2Pos


        #if no enemies, but capsules are still there!

        capsule_coords = self.getCapsulesYouAreDefending(gameState)        

        #two capsules! return the furthest one (ie closest to the enemy!)
        if len(capsule_coords) == 2:
          if self.red:
            #print "I AM RED!"
            #here you want to return the one with the highest x value
            if capsule_coords[0][0] > capsule_coords[1][0]:
              return capsule_coords[0]
            else:              
              return capsule_coords[1]
          
          else:
            #print "I AM BLUE!"
            #here you want to return the one with the lowest x value
            if capsule_coords[0][0] < capsule_coords[1][0]:
              return capsule_coords[0]
            else:
              return capsule_coords[1]

        #one capsule only!
        if len(capsule_coords) == 1:
          return capsule_coords[0]

        #if no enemies in sight, and no more capsules left, lets find the biggest dam cluster we can find!
               
        cluster_dict = self.cluster_finder_list(gameState)

        temp_max = 0
        for cluster in cluster_dict.keys():
          if cluster > temp_max:
            temp_max = cluster

        cluster_of_interest = temp_max

        return cluster_dict[str(cluster_of_interest)]   


    def heuristic(self, a, b):
        
        #print "this is maze distance: "
        #print self.getMazeDistance(a,b)
        return self.getMazeDistance(a,b)  

        """
        (x1, y1) = a
        (x2, y2) = b
        print "this is manhattan distance to the goal: "
        print abs(x1 - x2) + abs(y1 - y2)
        return abs(x1 - x2) + abs(y1 - y2)
        """
        #manhattan distance, the estimate for coord tuple a and b


    def aStarSearchDEF(self, gameState, goalCoord):
        """Search the node that has the lowest combined cost and heuristic first."""

        start = time.time()

        frontier = util.PriorityQueue()
        # maybe look at this.... DOES PRIORITY QUEUE DO WHAT YO UTHINK ITS DOING
        startState = gameState
        start_coord = startState.getAgentPosition(self.index)
        #print "this is startState: "
        #print startState
        #print "this is our starting coord: "
        #print start_coord

        frontier.push((startState, []), self.heuristic(start_coord, goalCoord))
        # pushes the initial gameState, with no actions, and then the
        # heuristic evaluation of the gameState

        #print "this is the frontier: "

        #print frontier

        visited = []

        while not frontier.isEmpty():
            node = frontier.pop()

            coord = node[0].getAgentPosition(self.index)
            actions = node[1]

            """
            print "this is where we are now: "
            print coord
            print "this is the actions to get there: "
            print actions
            print "this is the goal_coord: "
            print goalCoord
            """


            #print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

            if time.time() - start >= 0.8:
              # print "returned actions early!"
              return actions


            if coord == goalCoord:# if coord == goalCoord # so we really need to define the goal coords
                #print "we are at goal state now"
                return actions

            if coord not in visited:
                #print "okay we are not at goal yet, we are cotinuing on.."
                visited.append(coord)
                #print "this is visi ted: "
                #print visited

                for successor in self.getAllSuccessorInFormat(node[0]):

                    #NEED TO UPDATE THE POSITION TO GAMESTATE! otherwise its just getting the succesors of your start state only!
                    #print "this is successor: "
                    #print successor


                    nextCoord = successor[0].getAgentPosition(self.index)
                    nextDirection = successor[1]



                    #print "this is nextCoord: "
                    #print nextCoord
                    #print "this is next Direction: "
                    #print nextDirection


                    if not nextCoord in visited:
                        new_actions = actions + [nextDirection]
                        #print "this is new actions: " 
                        #print new_actions
                        #print "this is length of new actions: "
                        #print len(new_actions)
                        score = len(new_actions) + self.heuristic(nextCoord, goalCoord)
                        frontier.push((successor[0], new_actions), score)

        return []

    def getAllSuccessorInFormat(self, startState):
        actions = startState.getLegalActions(self.index)
        actions.remove(Directions.STOP)

        successor_list = list()

        # print "actions: "
        # print actions

        # assume that action cost is 1
        for action in actions:
            successor = self.getSuccessor(startState, action)
            # calculate action cost
            successor_position = successor.getAgentPosition(self.index)
            action_cost = self.getMazeDistance(self.start, successor_position)

            format = (successor, action, action_cost)
            # print "heuristic in food "
            # print self.heuristicForFood(successor)
            successor_list.append(format)

        return successor_list


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
