# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


#numOfStatesExpanded = 0

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
import game

numOfExpandedStates = 0





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
        oldFood = currentGameState.getFood()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        #print "In scoring function"

        #return betterEvaluationFunction(currentGameState)

        # print ("Width" + str(oldFood.width))
        # print ("Height" + str(oldFood.height))
        # print ("Before " + str(oldFood))
        foodList=oldFood.asList()
        # print ("After " + str(foodList))
        # print("New pos " + str(newPos))

        foodList.sort(lambda x,y: util.manhattanDistance(newPos, x)-util.manhattanDistance(newPos, y))
        #print ("After sorting.." + str(foodList))
        foodScore=util.manhattanDistance(newPos, foodList[0])
        #print(dir(newGhostStates[0]))

        GhostPositions=[Ghost.getPosition() for Ghost in newGhostStates]
        if len(GhostPositions) ==0 :
            GhostScore=0
        else:
            GhostPositions.sort(lambda x,y: disCmp(x,y,newPos))
        if util.manhattanDistance(newPos, GhostPositions[0])==0: return -99
        else:
            GhostScore=2*-1.0/util.manhattanDistance(newPos, GhostPositions[0])

        numOfCapsulesLeft = len(successorGameState.getCapsules())
        numofFoodsLeft = len(newFood.asList())

        if foodScore==0:
            returnScore=2.0+GhostScore-4*numOfCapsulesLeft-2*numofFoodsLeft
            #returnScore=2.0+GhostScore
        else:
            returnScore=GhostScore+1.0/float(foodScore)-4*numOfCapsulesLeft-2*numofFoodsLeft
            #returnScore=GhostScore+1.0/float(foodScore)



        numOfCapsulesLeft = len(successorGameState.getCapsules())
        numofFoodsLeft = len(newFood.asList())

        print('GhostScore')
        print(GhostScore)
        print('FoodScore')
        print(foodScore)
        print('ReturnScore:')
        print(returnScore)
        return returnScore

def disCmp(x,y,newPos):
    if (util.manhattanDistance(newPos, x)-util.manhattanDistance(newPos, y))<0: return -1
    else:
        if (util.manhattanDistance(newPos, x)-util.manhattanDistance(newPos, y))>0: return 1
        else:
            return 0

        "*** YOUR CODE HERE ***"
        #return successorGameState.getScore()

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

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"


        numOfAgent=gameState.getNumAgents();
        #true depth is because that each agent plays one in a total move.
        trueDepth=numOfAgent*self.depth
        LegalActions=gameState.getLegalActions(0)
        if Directions.STOP in LegalActions:
            LegalActions.remove(Directions.STOP)
        listNextStates=[gameState.generateSuccessor(0,action) for action in LegalActions ]
        #print(self.MiniMax_Value(numOfAgent,0,gameState,trueDepth))

        #get the minimax value as a
        v=[self.MiniMax_Value(numOfAgent,1,nextGameState,trueDepth-1) for nextGameState in listNextStates]
        MaxV=max(v)
        listMax=[]
        for i in range(0,len(v)):
            if v[i]==MaxV:
                 listMax.append(i)
        i = random.randint(0,len(listMax)-1)

        #print(LegalActions)
        #print(MaxV)
        #print(listMax)
        action=LegalActions[listMax[i]]
        #print("Action is " + action)
        #print("In get actions")

        return action

    def MiniMax_Value(self,numOfAgent,agentIndex, gameState, depth):

        global numOfExpandedStates

        LegalActions=gameState.getLegalActions(agentIndex)
        listNextStates=[gameState.generateSuccessor(agentIndex,action) for action in LegalActions ]
        numOfExpandedStates += len(listNextStates)
        print ("Number of states expanded = " + str(numOfExpandedStates))
        if (gameState.isLose() or gameState.isWin() or depth==0):
                  return self.evaluationFunction(gameState)
        else:

            if (agentIndex==0):


                return max([self.MiniMax_Value(numOfAgent,(agentIndex+1)%numOfAgent,nextState,depth-1) for nextState in listNextStates] )
            else :


                return min([self.MiniMax_Value(numOfAgent,(agentIndex+1)%numOfAgent,nextState,depth-1) for nextState in listNextStates])

        util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        numOfAgent=gameState.getNumAgents();
        trueDepth=numOfAgent*self.depth
        LegalActions=gameState.getLegalActions(0)

    # remove stop action from list of legal actions
        if Directions.STOP in LegalActions:
            LegalActions.remove(Directions.STOP)

        listNextStates = [gameState.generateSuccessor(0,action) for action in LegalActions ]

    # check whether minimax value for -l minimaxClassic are 9, 8 , 7, -492
    # print(self.Alpha_Beta_Value(numOfAgent,0,gameState,trueDepth))

    # as long as beta is above the upper bound of the eval function
        v = [self.Alpha_Beta_Value(numOfAgent,1,nextGameState,trueDepth-1, -1e308, 1e308) for nextGameState in listNextStates]
        MaxV=max(v)
        listMax=[]
        for i in range(0,len(v)):
            if v[i]==MaxV:
                 listMax.append(i)
        i = random.randint(0,len(listMax)-1)

        print(LegalActions)
        print(v)
        print(listMax)
        action=LegalActions[listMax[i]]
        return action




        util.raiseNotDefined()


    def Alpha_Beta_Value(self, numOfAgent, agentIndex, gameState, depth, alpha, beta):

          global numOfExpandedStates


          LegalActions=gameState.getLegalActions(agentIndex)
          if (agentIndex==0):
             if Directions.STOP in LegalActions:
                 LegalActions.remove(Directions.STOP)
          listNextStates=[gameState.generateSuccessor(agentIndex,action) for action in LegalActions ]
          numOfExpandedStates += len(listNextStates)
          print ("Number of states expanded = " + str(numOfExpandedStates))


          # terminal test
          if (gameState.isLose() or gameState.isWin() or depth==0):
                  return self.evaluationFunction(gameState)
          else:
              # if Pacman
              if (agentIndex == 0):
                  v=-1e308
                  for nextState in listNextStates:
                      v = max(self.Alpha_Beta_Value(numOfAgent, (agentIndex+1)%numOfAgent, nextState, depth-1, alpha, beta), v)
                      if (v >= beta):
                          return v
                      alpha = max(alpha, v)
                  return v
              # if Ghost
              else:
                  v=1e308
                  for nextState in listNextStates:
                      v = min(self.Alpha_Beta_Value(numOfAgent, (agentIndex+1)%numOfAgent, nextState, depth-1, alpha, beta), v)
                      if (v <= alpha):
                          return v
                      beta = min(beta, v)
                  return v

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
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):

    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """



    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.

          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

