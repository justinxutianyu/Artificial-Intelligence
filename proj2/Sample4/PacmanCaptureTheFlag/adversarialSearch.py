import game
import copy
from game import Directions
import random,util,math
import yourAgent

RED = 0
ORANGE = 2
YELLOW = 4
#
BLUE = 1
TEAL = 3
PURPLE = 5

class adversarialSearchState:
	def __init__(self, gameState, maxLocation, minLocation, maxIndex, newMinIsScared, newVisitedStates, maxStartPosition, minStartPosition, layoutHeight, layoutWidth):
		
		# Copy walls
		self.walls = gameState.getWalls()
		
		# Check your color
		self.maxIsRed = gameState.isOnRedTeam(maxIndex)
		self.minIsRed = not self.maxIsRed
		
		self.maxStartPosition = maxStartPosition
		self.minStartPosition = minStartPosition
		
		self.layoutHeight = layoutHeight
		self.layoutWidth = layoutWidth
		
		# Copy in your food
		if self.maxIsRed == True:
			self.maxFood = gameState.getRedFood()
			self.minFood = gameState.getBlueFood()
		else:
			self.maxFood = gameState.getBlueFood()
			self.minFood = gameState.getRedFood()

		self.lastMaxFood = copy.deepcopy(self.maxFood)
		self.lastMinFood = copy.deepcopy(self.minFood)
		
		self.maxVisitedStates = copy.deepcopy(newVisitedStates)
		
		self.timesMinEaten = 0
		
		# Max's position
		self.maxPosition = maxLocation
		
		# Min's position
		self.minPosition = minLocation
		
		self.minIsScared = newMinIsScared
		
		self.index = maxIndex
		
	def isMaxPositionInMaxTerritory(self):
		return not self.maxIsPacman()
	
	def isMinPositionInMinTerritory(self):
		return not self.minIsPacman()
		
	def maxIsPacman(self):
   		isPacman = True
   		if self.maxIsRed and self.maxPosition[0] < 15.5:
   		 	isPacman = False
   	  	elif not self.maxIsRed and self.maxPosition[0] >= 15.5:
   	  	 	isPacman = False
   		return isPacman
   		
	def minIsPacman(self):
   		isPacman = True
   		if self.minIsRed and self.minPosition[0] < 15.5:
   			isPacman = False
   	  	elif not self.minIsRed and self.minPosition[0] >=15.5:
   	  		isPacman = False
   		return isPacman
   	   
	def applyMaxAction(self,action):
   		newState = copy.deepcopy(self)
		if (action == Directions.WEST):
			newState.maxPosition = (self.maxPosition[0] - 1,self.maxPosition[1])
		elif (action == Directions.EAST):
			newState.maxPosition = (self.maxPosition[0] + 1,self.maxPosition[1])
		elif (action == Directions.SOUTH):
			newState.maxPosition = (self.maxPosition[0],self.maxPosition[1]-1)
		elif (action == Directions.NORTH):
			newState.maxPosition = (self.maxPosition[0],self.maxPosition[1]+1)
		return newState
	   
	def applyMinAction(self,action):
   		newState = copy.deepcopy(self)
		if (action == Directions.WEST):
			newState.minPosition = (self.minPosition[0] - 1,self.minPosition[1])
		elif (action == Directions.EAST):
			newState.minPosition = (self.minPosition[0] + 1,self.minPosition[1])
		elif (action == Directions.SOUTH):
			newState.minPosition = (self.minPosition[0],self.minPosition[1]-1)
		elif (action == Directions.NORTH):
			newState.minPosition = (self.minPosition[0],self.minPosition[1]+1)
		  
		return newState
		
	def isValid(self):
   		# Check validity of move
   		result = False
   		if self.checkWalls(self.maxPosition) and self.checkWithinBoundary(self.maxPosition) and self.checkWalls(self.minPosition) and self.checkWithinBoundary(self.minPosition) and not self.maxMinCollision():
			result = True
			
		return result
	
	# Check if a given position is within the game map
	def checkWithinBoundary(self, enemyPose):
		# Check if within X Boundaries (1 <= x <= 30)
		if enemyPose[0] <= self.layoutWidth and enemyPose[0] >= 1:
			# Check if within Y boundaries (1 <= y <= 14)
			if enemyPose[1] <= self.layoutHeight and enemyPose[1] >= 1:
				return True
			else:
				return False
		else:
			return False
		
	# Check if a given position has a wall
	def checkWalls(self, pos):
		return not self.walls[int(pos[0])][int(pos[1])]
	
	# It's only considered an invalid collision if we're on top of min, on min's side, and min is not scared -> this state won't be considered then
	def maxMinCollision(self):
		return (self.minPosition == self.maxPosition) and not self.isMaxPositionInMaxTerritory() and not self.minIsScared
	 
class AdversarialSearch:
	def __init__(self, newAgent, gameState, maxLoc, minLoc, maxIndex, minIsScared, visitedStates,maxStartLoc,minStartLoc,layoutHeight,layoutWidth):
		self.agent = newAgent
		self.state = adversarialSearchState(gameState,maxLoc,minLoc,maxIndex,minIsScared,visitedStates,maxStartLoc,minStartLoc,layoutHeight,layoutWidth)
		
	def startSearch(self, newMaxDepth):
		self.maxDepth = newMaxDepth
		QvalActionPair = self.maxAdversarial(self.state,0) 
		if QvalActionPair[1]  == None:
			QvalActionPair = (QvalActionPair[0],Directions.STOP)
		return QvalActionPair
		
	"Minimax methods"
	def maxAdversarial(self,state,n):
		n = n+1
		state.maxVisitedStates[state.maxPosition] = True
	 	
	 	legalA = self.getMaxLegalActions(state)
	 	vals = []
	 	maxQval = -100000
	 	maxAction = None
	 	for a in legalA:
	 		succState = self.getMaxSuccessorState(state,a)
	 		"Case this results in an invalid state"
			if succState is None:
			  continue
			
			"Case we've reached the end of the recursion"
			if n > self.maxDepth:
	 			(Q,feature) = self.agent.evaluate(succState,a,True)
	 			QvalActionPair = (Q,a)
	 				
  			if n <= self.maxDepth:
	 		 	QvalActionPair = self.minAdversarial(succState,n)
	 		
	 		QvalActionPair = (QvalActionPair[0],a)
	 		if (QvalActionPair[1] != None):
				vals.append(QvalActionPair)
	 		
	 		if (QvalActionPair[0] > maxQval) and (QvalActionPair[1] != None):
	 			maxQval = QvalActionPair[0]
	 			maxAction = QvalActionPair[1]
	 		
	 	"Return the tuple with the max Qval"
	 	return (maxQval,maxAction)

 	def minAdversarial(self,state,n):
 		
 		"Case min is a pacman so let it eat max's food"
 		if state.minIsPacman():
			state.maxFood[int(state.minPosition[0])][int(state.minPosition[1])] = False
 		 	
 		legalA = self.getMinLegalActions(state)
		vals = []
		minQval = 100000
		minAction = None
		for a in legalA:
			succState = self.getMinSuccessorState(state,a)
			"Case this results in an invalid state"
			if succState is None:
			  continue
	 			
			QvalActionPair = self.maxAdversarial(succState,n)
			QvalActionPair = (QvalActionPair[0],a)
			if (QvalActionPair[1] != None):
				vals.append(QvalActionPair)
			
			if (QvalActionPair[0] < minQval) and (QvalActionPair[1] != None):
	 			minQval = QvalActionPair[0]
	 			minAction = QvalActionPair[1]
			
	   	"Return the tuple with the min Qval"
	 	return (minQval,minAction)   

	"Helper methods"
	def getMaxLegalActions(self,state):
		actions = []
		for a in [Directions.WEST, Directions.EAST, Directions.NORTH, Directions.SOUTH]:
			newState = state.applyMaxAction(a)
			if newState.isValid():
			 	actions.append(a)
		return actions
	   
	def getMinLegalActions(self,state):
		actions = []
		for a in [Directions.WEST, Directions.EAST, Directions.NORTH, Directions.SOUTH]:
			newState = state.applyMinAction(a)
			if newState.isValid():
			 	actions.append(a)
		return actions
	   
	def getMaxSuccessorState(self,state,action):		
		"Move maxPosition"
		newState = state.applyMaxAction(action)
		newState.maxAteMin = False
		
		if not newState.isValid():
			return None
		
		"Case max is a pacman, so let it eat min's food"
		if state.maxIsPacman():
			newState.minFood[int(newState.maxPosition[0])][int(newState.maxPosition[1])] = False

		if not newState.maxIsPacman():
			"Case max is a ghost"
			if newState.maxPosition == newState.minPosition:
				newState.minPosition = newState.minStartPosition
				newState.maxAteMin = True
				newState.timesMinEaten += 1
		
		return newState
	   
	def getMinSuccessorState(self,state,action):
		"Move minPosition"
		newState = state.applyMinAction(action)
		newState.maxAteMin = False
		
		if not newState.isValid():
			return None
			
		"Case max is a ghost"
		if not newState.maxIsPacman():
			if newState.maxPosition == newState.minPosition:
				newState.minPosition = newState.minStartPosition
				newState.maxAteMin = True
				newState.timesMinEaten += 1
			
		return newState
	 
		
		
		