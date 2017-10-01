from game import *

import random,util,math

class newGameState:
    def __init__(self, state, agentIndex):
        
        # Copy walls
        self.walls = state.getWalls()
        
        # Check your color
        self.isRed = state.isOnRedTeam(agentIndex)
        
        # Copy in your food
        if self.isRed == True:
            self.food = state.getRedFood()
        else:
            self.food = state.getBlueFood()
     
    def setEnemyPosition(self, position):
        self.enemyPosition = position
        
    def setCurrentPosition(self, position):
        self.agentPosition = position
        
    def getEnemyPosition(self):
        return self.enemyPosition
    
    def getCurrentPosition(self):
        return self.enemyPosition
    
    def updateEnemyPosition(self, state, action):
        # Get the position of enemies   
        for epos in self.getOpponentPositions(successor):
          if epos is not None:
            if (action == Directions.WEST):
                newEpos[0] = epos[0] - 1
                newEpos[1] = epos[1]
            elif (action == Directions.EAST):
                newEpos[0] = epos[0] + 1
                newEpos[1] = epos[1]
            elif (action == Directions.SOUTH):
                newEpos[0] = epos[0] 
                newEpos[1] = epos[1] - 1
            elif (action == Directions.NORTH):
                newEpos[0] = epos[0] 
                newEpos[1] = epos[1] + 1
            
            # Check validity of move
            if checkWalls(newEpos) and checkWithinBoundary(newEpos):
                self.enemyPosition = newEpos
    
    # Check if a given position is within the game map
    def checkWithinBoundary(self, enemyPose):
        # Check if within X Boundaries (1 <= x <= 30)
        if enemyPose[0] <= 30 and enemyPose[0] >= 1:
            # Check if within Y boundaries (1 <= y <= 14)
            if enemyPose[1] <= 14 and enemyPose[1] >= 1:
                return True
            else:
                return False
        else:
            return False
        
    # Check if a given position has a wall
    def checkWalls(self, enemyPose):
        return self.walls[enemyPose[0]][enemyPose[1]]
     
class adverseSearchClass:
    def __init__(self, state, agentIndex):
        self.newState = newGateState(state,agentIndex)
        
        
        
        