
def genInitConstants(gameState) :
    
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    (cpi, cpj) = gameState.getPacmanPosition()

    constants = []

    # This populates the left, right, up, down without walls
    # Also populates the onLeftSide list
    for i in range(1,width) :
        for j in range(1,height) :
            
            if i - 1 > 0 and not gameState.hasWall(i - 1, j) :
                l = PDDLPredicate("left", ["n" + str(i),"n"+ str(j), "n" + str(i - 1),"n" + str(j)])
                constants.append(l)
            if i + 1 < width and not gameState.hasWall(i + 1, j) :
                r = PDDLPredicate("right", ["n" + str(i), "n" + str(j), "n" + str(i + 1), "n" + str(j)])
                constants.append(r)
            if j - 1 > 0 and not gameState.hasWall(i, j - 1) :
                d = PDDLPredicate("down", ["n" + str(i), "n" + str(j), "n" + str(i), "n" + str(j - 1)])
                constants.append(d)
            if j + 1 < height and not gameState.hasWall(i, j + 1) :
                u = PDDLPredicate("up", ["n" + str(i), "n" + str(j), "n" + str(i), "n" + str(j + 1)])
                constants.append(u)
            if i < width / 2 :
                on = PDDLPredicate("LeftSideSqaure", ["n" + str(i), "n" + str(j)])
                constants.append(on)

    # Populating constant booleans - TODO Fix this
    if cpi < width / 2 :
        ol = PDDLPredicate("isLeftSide")
        constants.append(ol)

    return  constants

def genPredicates(self, gameState) :
    
    predicates = []
    (cpi, cpj) = gameState.getAgentPosition(self.index)
    predicates.append("curLoc", ["n" + str(cpi), "n" + str(cpj)])

    agentPos = []
    enemyList = []

    for item in self.getTeam(gameState):
        apos = gameState.getAgentPosition(item)
        if apos != (cpi,cpj) :
            agentPos.append(apos)
    for item in self.getOpponents(gameState) :
        epos = gameState.getAgentPosition(item)
        enemyList.append(epos)


    # Produce food location predicates
    foodGrid = self.getFood(gameState).asList()

    for (f1,f2) in foodGrid :
        f = PDDLPredicate("locF", ["n" + str(f1), "n" + str(f2)])
        predicates.append(f)

    # Produce capsule location predicates
    for (p1,p2) in self.getCapsules(gameState) :
        c = PDDLPredicate("locP", ["n" + str(p1), "n" + str(p2)])
        predicates.append(c)
    
    # Produce agent location predicates
    for (a1, a2) in agentPos :
        a = PDDLPredicate("locA", ["n" + str(a1), "n" + str(a2)])
        predicates.append(a)

    # Produce enemy locations
    for (e1,e2) in enemyList :
        e = PDDLPredicate("locE", ["n" + str(e1), "n" + str(e2)])
        predicates.append(e)
            
