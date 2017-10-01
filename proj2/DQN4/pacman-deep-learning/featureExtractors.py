# featureExtractors.py
# --------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:  
  def getFeatures(self, state, action):    
    """
      Returns a dict from features to counts
      Usually, the count will just be 1.0 for
      indicator functions.  
    """
    util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
  def getFeatures(self, state, action):
    feats = util.Counter()
    feats[(state,action)] = 1.0
    return feats

def closestFood(pos, food, walls):
  """
  closestFood -- this is similar to the function that we have
  worked on in the search project; here its all in one place
  """
  fringe = [(pos[0], pos[1], 0)]
  expanded = set()
  while fringe:
    pos_x, pos_y, dist = fringe.pop(0)
    if (pos_x, pos_y) in expanded:
      continue
    expanded.add((pos_x, pos_y))
    # if we find a food at this location then exit

    if food[pos_x][pos_y]:
      return dist
    # otherwise spread out from the location to its neighbours
    nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    for nbr_x, nbr_y in nbrs:
      fringe.append((nbr_x, nbr_y, dist+1))
  # no food found
  return None

def closestScaredGhost(pos, scaredGhostsOne, walls):

  fringe = [(pos[0], pos[1], 0)]
  expanded = set()

  while fringe:
    pos_x, pos_y, dist = fringe.pop(0)
    if (pos_x, pos_y) in expanded:
      continue
    expanded.add((pos_x, pos_y))
    # if we find a food at this location then exit

    if scaredGhostsOne == (pos_x,pos_y):
      return dist
    # if scaredGhostsOne == (pos_x - .5,pos_y - 0.5):
    #   return dist
    # if scaredGhostsOne == (pos_x + .5,pos_y + 0.5):
    #   return dist
    # if scaredGhostsOne == (pos_x + .5,pos_y):
    #   return dist
    # if scaredGhostsOne == (pos_x ,pos_y + 0.5):
    #   return dist
    # if scaredGhostsOne == (pos_x ,pos_y - 0.5):
    #   return dist
    # if scaredGhostsOne == (pos_x - .5,pos_y ):
    #   return dist
    # otherwise spread out from the location to its neighbours
    nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    for nbr_x, nbr_y in nbrs:
      fringe.append((nbr_x, nbr_y, dist+1))
  # no food found
  return None

class SimpleExtractor(FeatureExtractor):
  """
  Returns simple features for a basic reflex Pacman:
  - whether food will be eaten
  - how far away the next food is
  - whether a ghost collision is imminent
  - whether a ghost is one step away
  """
  
  def getFeatures(self, state, action):
    # extract the grid of food and wall locations and get the ghost locations
    food = state.getFood()
    walls = state.getWalls()
    ghosts = state.getGhostPositions()

    features = util.Counter()
    
    features["bias"] = 1.0
    
    # compute the location of pacman after he takes the action
    x, y = state.getPacmanPosition()
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)
    
    # count the number of ghosts 1-step away
    features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

    # if there is no danger of ghosts then add the food feature
    if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
      features["eats-food"] = 1.0
    
    dist = closestFood((next_x, next_y), food, walls)
    if dist is not None:
      # make the distance a number less than one otherwise the update
      # will diverge wildly
      features["closest-food"] = float(dist) / (walls.width * walls.height) 
    features.divideAll(10.0)
    return features

# class setnumberExtractor(FeatureExtractor):
#   """
#   Returns simple features for a basic reflex Pacman:
#   - whether food will be eaten
#   - how far away the next food is
#   - whether a ghost collision is imminent
#   - whether a ghost is one step away
#   """
#
#   def getFeatures(self, state, action):
#     # extract the grid of food and wall locations and get the ghost locations
#     # food = state.getFood()
#     # walls = state.getWalls()
#     # ghost = state.getGhostState()
#     # ghosts = state.getGhostPositions()
#     # scaredGhostsOne = state.getGhostState(1)
#     # scaredGhostsTwo = state.getGhostState(2)
#     # scaredGhostsOne.scaredTimer = state.getScaredGhostTimer(1)
#     # scaredGhostsTwo.scaredTimer = state.getScaredGhostTimer(2)
#     # features = util.Counter()
#     # print ghost
#     #
#     # features["#-of-ghosts-1-step-away"] = 0
#     # features["eats-food"] = 0
#     # features["closest-food"] = 0
#     # features["scared-ghosts"] = 0
#     #
#     # # compute the location of pacman after he takes the action
#     # x, y = state.getPacmanPosition()
#     # dx, dy = Actions.directionToVector(action)
#     # next_x, next_y = int(x + dx), int(y + dy)
#     #
#     # # count the number of ghosts 1-step away
#     # features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
#     #
#     # # if there is no danger of ghosts then add the food feature
#     # # if scaredGhostsOne.scaredTimer >= 1:
#     # #   eatGhostsOne = True
#     # # else:
#     # #   eatGhostsOne = False
#     # # if scaredGhostsTwo.scaredTimer >= 1:
#     # #   eatGhostsTwo = True
#     # # else:
#     # #   eatGhostsTwo = False
#     # # if eatGhostsOne and eatGhostsTwo:
#     # #
#     # #   ghost1 = state.getGhostPosition(1)
#     # #
#     # #   ghost2 = state.getGhostPosition(2)
#     # #
#     # #   dist1 = closestScaredGhost((next_x, next_y), ghost1, walls,food)
#     # #   dist2 = closestScaredGhost((next_x, next_y), ghost2, walls,food)
#     # #   if dist1 > dist2:
#     # #     features["scared-ghosts"] = float(dist1) / (walls.width * walls.height)
#     # #   elif dist2 > dist1:
#     # #     features["scared-ghosts"] = float(dist2) / (walls.width * walls.height)
#     # #   features["eats-food"] = 1.0
#     # #   features["closest-food"] = 1.0
#     # # elif eatGhostsOne:
#     # #
#     # #   features["scared-ghosts"] = 1.0
#     # #   features["eats-food"] = 1.0
#     # #   features["closest-food"] = 1.0
#     # # elif eatGhostsTwo:
#     # #   features["scared-ghosts"] = 1.0
#     # #   features["eats-food"] = 1.0
#     # #   features["closest-food"] = 1.0
#     # # else:
#     # if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
#     #  features["eats-food"] = 1.0
#     #  dist = closestFood((next_x, next_y), food, walls)
#     #  if dist is not None:
#     #    features["closest-food"] = float(dist) / (walls.width * walls.height)
#     food = state.getFood()
#     walls = state.getWalls()
#     ghosts = state.getGhostPositions()
#
#     features = util.Counter()
#
#     features["#-of-ghosts-1-step-away"] = 0
#     features["eats-food"] = 0
#     features["closest-food"] = 0
#
#
#     # compute the location of pacman after he takes the action
#     x, y = state.getPacmanPosition()
#     dx, dy = Actions.directionToVector(action)
#     next_x, next_y = int(x + dx), int(y + dy)
#
#     # count the number of ghosts 1-step away
#     features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
#
#     # if there is no danger of ghosts then add the food feature
#     if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
#       features["eats-food"] = 1.0
#
#     dist = closestFood((next_x, next_y), food, walls)
#     if dist is not None:
#       # make the distance a number less than one otherwise the update
#       # will diverge wildly
#       features["closest-food"] = float(dist) / (walls.width * walls.height)
#     features.divideAll(10.0)
#     return features
#
#
#
#
#     features.divideAll(10.0)
#     return features
class setnumberExtractor(FeatureExtractor):
  """
  Returns simple features for a basic reflex Pacman:
  - whether food will be eaten
  - how far away the next food is
  - whether a ghost collision is imminent
  - whether a ghost is one step away
  """

  def getFeatures(self, state, action):
    # extract the grid of food and wall locations and get the ghost locations
    food = state.getFood()
    walls = state.getWalls()
    ghosts = state.getGhostPositions()
    pacman = state.getPacmanPosition()
    #capsules = self.data.capsules

    scaredGhostsOne = state.getGhostState(1)
    scaredGhostsTwo = state.getGhostState(2)
    scaredGhostsOne.scaredTimer = state.getScaredGhostTimer(1)
    scaredGhostsTwo.scaredTimer = state.getScaredGhostTimer(2)
    features = util.Counter()
    eat_food = False
    eat_ghost = False

    ghost1 = state.getGhostPosition(1)
    #ghost1.Timer = state.getScaredGhostTimer(1)
    ghost2 = state.getGhostPosition(2)
    #ghost2.Timer = state.getScaredGhostTimer(2)
    dist = None

    features["#-of-ghosts-1-step-away"] = 0
    features["eats-food"] = 0
    features["closest-food"] = 0
    #features['closest-scared-ghost'] = 0
    #features['number-of-scared-ghost'] = 0
    #features['eats-ghost-1'] = 0
    features['eats-ghost'] = 0
    #features['closest-capsule'] = 0
    #features['eats-capsule'] = 0
    #features['distance-scared-ghost-one'] = 0
    features['distance-scared-ghost'] = 0

    firstitem = 1;
    for x in ghost1:
      if not x == int(x):
        x = x - 0.5

      if firstitem==1:
        ghost1_x = x
        firstitem+=1
      else:
        ghost1_y = round(x)
        firstitem = 1
    for x in ghost2:
      if not x == int(x):
        x = x - 0.5
      if firstitem==1:
       ghost2_x = round(x)
       firstitem+=1
      else:
       ghost2_y = round(x)
       firstitem=1


    # compute the location of pacman after he takes the action
    x, y = state.getPacmanPosition()
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)
    number_of_adjecent_ghosts = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

    if scaredGhostsOne.scaredTimer >=2  or scaredGhostsTwo.scaredTimer >= 2:

      if state.getScaredGhostTimer(1) >= 2:
        dist1 = closestScaredGhost((next_x, next_y), (ghost1_x,ghost1_y), walls)
        print (ghost1_x,ghost1_y)
        #print dist1
      else:
        dist1 = None
      if state.getScaredGhostTimer(2) >= 2:
        dist2 = closestScaredGhost((next_x, next_y), (ghost2_x,ghost2_y), walls)
        print (ghost2_x,ghost2_y)
        #print dist2
      else:
        dist2 = None
      if dist1 is not None and dist2 is not None:
        if dist1 <= dist2:
          dist = dist1
        if dist2 <= dist1:
          dist = dist2
      elif dist1 is None and dist2 is not None:
        dist = dist2
      elif dist1 is not None and dist2 is None:
        dist = dist1
      else:
        dist = None
      eat_ghost = True
    else:
      eat_food = True
      dist = closestFood((next_x, next_y), food, walls)



    #features["#-of-ghosts-1-step-away"] = number_of_adjecent_ghosts
    # count the number of ghosts 1-step away
    NoScaredGhosts = False
    if eat_ghost:
      if dist is not None:

              features['distance-scared-ghost'] = float(dist) / (walls.width * walls.height)
      if number_of_adjecent_ghosts>0:#if a ghost is adjecant
        for g in ghosts:
          if g ==  state.getGhostPosition(1):
            firstitem = 1;
            for x in state.getGhostPosition(1):
              if firstitem==1:
               x1 = round(x)
               firstitem+=1
              else:
                x2 = round(x)
                firstitem = 1
            print state.getGhostPosition(1)
            print next_y, next_x
            if state.getScaredGhostTimer(1)>=2 and (next_x,next_y) == (ghost1_x,ghost1_y):


              print "ghost timer blue "
              print state.getScaredGhostTimer(1)
              # print "pring g "
              # print g
              features["eats-ghost"] = 1
              # print "eats ghost 1"
            if dist is not None:

              features['distance-scared-ghost'] = float(dist) / (walls.width * walls.height)
          if g ==  state.getGhostPosition(2):
            if state.getScaredGhostTimer(2)>=2 and (next_x,next_y) == (ghost2_x,ghost2_y):
              print state.getGhostPosition(1)
              print "ghost timer orange "
              print state.getScaredGhostTimer(2)
              # print "pring g "
              # print  g
              # print "eats ghost 2"
              features['eats-ghost'] = 1
            if dist is not None:

              features['distance-scared-ghost'] = float(dist) / (walls.width * walls.height)



       # if scaredGhostsOne.scaredTimer >= 1 and scaredGhostsTwo.scaredTimer >=1:
       #   dist1 = closestScaredGhost((next_x, next_y), (ghost1_x,ghost1_y), walls)
       #   if dist1 >10:
       #     dist1 = 100
       #   dist2 = closestScaredGhost((next_x, next_y), (ghost2_x,ghost2_y), walls)
       #   if dist2 > 10:
       #     dist2 = 100
       #   if dist1 <= dist2:
       #     dist = dist1
       #   elif dist2<=dist1:
       #     dist = dist2
       #
       #   if dist <=10 and dist is not None:
       #   # make the distance a number less than one otherwise the update
       #   # will diverge wildly
       #     features['closest-scared-ghost'] = float(dist) / (walls.width * walls.height)
    #     #features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
    #     if number_of_adjecent_ghosts > 0 : #((round(ghost1_x),round(ghost1_y)) == (next_x,next_y) or (round(ghost2_x),round(ghost2_y)) == (next_x,next_y)) or (ghost1_x + 1, ghost1_y + 1)==(next_x,next_y) or (ghost2_x + 1, ghost2_y + 1)==(next_x,next_y) or (ghost1_x, ghost1_y + 1)==(next_x,next_y) or (ghost2_x, ghost2_y + 1)==(next_x,next_y):
    #
    #       features["eats-ghost"] = 1
    #       features["#-of-ghosts-1-step-away"] = 0
    #
    #       #features['eats-food'] = 0.01
    #   elif scaredGhostsOne.scaredTimer >= 1 and not scaredGhostsTwo.scaredTimer >=1:
    #     #number_of_adjecent_ghosts = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls)for g in ghost1)
    #     dist1 = closestScaredGhost((next_x, next_y), (ghost1_x,ghost1_y), walls)
    #     if dist1 is not None:
    #   # make the distance a number less than one otherwise the update
    #   # will diverge wildly
    #       features['closest-scared-ghost'] = float(dist1) / (walls.width * walls.height)
    #     #features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
    #     # if features["#-of-ghosts-1-step-away"] >=1:# and ((round(ghost1_x),round(ghost1_y)) == (next,next_y)):
    #     if number_of_adjecent_ghosts>0:#((round(ghost1_x),round(ghost1_y)) == (next,next_y)):
    #       for g in ghosts:
    #         if g == ghost1:
    #           features["eats-ghost"] = 1
    #         if g == ghost2:
    #           #features["eats-ghost"] = 0
    #           #features['closest-scared-ghost'] = -1
    #           features["#-of-ghosts-1-step-away"]  = 0
    #
    #       #features["#-of-ghosts-1-step-away"] = 0
    #   elif not scaredGhostsOne.scaredTimer >= 1 and scaredGhostsTwo.scaredTimer >=1:
    #     #number_of_adjecent_ghosts = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls)for g in ghost2)
    #     dist2 = closestScaredGhost((next_x, next_y),  (ghost2_x,ghost2_y), walls)
    #     if dist2 is not None:
    #   # make the distance a number less than one otherwise the update
    #   # will diverge wildly
    #       features['closest-scared-ghost'] = float(dist2) / (walls.width * walls.height)
    #     #features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
    #     if number_of_adjecent_ghosts>0:#((round(ghost1_x),round(ghost1_y)) == (next,next_y)):
    #       for g in ghosts:
    #         if g == ghost2:
    #           features["eats-ghost"] = 1
    #         if g == ghost1:
    #           #features["eats-ghost"] = 0
    #           #features['closest-scared-ghost'] = 0
    #           features["#-of-ghosts-1-step-away"]  = 0
    #      #features["#-of-ghosts-1-step-away"] = 0
    # else:
    if eat_food:
      features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
      if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
        features["eats-food"] = 0.1

      if dist is not None:
          # make the distance a number less than one otherwise the update
          # will diverge wildly
        features["closest-food"] = float(dist) / (walls.width * walls.height)


    # if there is no danger of ghosts then add the food feature

    # if scaredGhostsOne.scaredTimer >= 1 and state.getGhostPosition(1) == (next_x,next_y):
    #   features["closest-food"] = 1
    # if scaredGhostsTwo.scaredTimer >= 1 and state.getGhostPosition(2) == (next_x,next_y):
    #   features["closest-food"] = 1
    # if NoScaredGhosts:
    #   if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
    #     features["eats-food"] = 1.0
    #   dist = closestFood((next_x, next_y), food, walls)
    #   if dist is not None:
    #     # make the distance a number less than one otherwise the update
    #     # will diverge wildly
    #     features["closest-food"] = float(dist) / (walls.width * walls.height)
    features.divideAll(10.0)
    #print features
    return features
