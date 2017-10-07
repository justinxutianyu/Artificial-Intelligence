# myTeam.py
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
debug = False
#python capture.py -r myTeam -redOpts first=ShuaiAgent,second=ShuaiAgent
from game import Agent
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from util import nearestPoint
import sys
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
			   first = 'ShuaiAgent', second = 'ShuaiAgent'):
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

class ShuaiAgent(CaptureAgent):
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
	# Blue index = 1,3,   red = 0,2
	start = time.time()
	CaptureAgent.registerInitialState(self, gameState)
	self.dieCount = 0
	if self.index < 2:	#one attacker and one defender at the beginning
		self.is_attacker = True
	else:
		self.is_attacker = False
	self.opponents = self.getOpponents(gameState)
	self.teammate = self.getTeammate()
	f = open('data/input_data','r')
	self.factors = [int(i) for i in f.read().replace('\n','').split(' ')]
	self.is_ghost = True
	self.carryingFood = 0 #food you are carrying

	if self.red:
	  self.middle_line = gameState.data.layout.width/2-1
	else:
	  self.middle_line = gameState.data.layout.width/2
	self.dangerousness = self.getDangerousness(gameState)
	if debug:
		print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
	
  def chooseAction(self, gameState):
	start = time.time()
	self.pos = gameState.getAgentPosition(self.index)
	if debug:
		print "\npresent State",gameState.getAgentState(self.index)
	actions = gameState.getLegalActions(self.index) #available actions
	if not self.is_attacker and self.pos[0] == self.middle_line and self.red:	#defender should never cross the line
		actions.remove('East')
	elif not self.is_attacker and self.pos[0] == self.middle_line and not self.red:
		actions.remove('West')
	if str(gameState.getAgentState(self.index)).split(':')[0] == 'Ghost':
	  self.is_ghost = True
	else:
	  self.is_ghost = False
	lastState = self.getPreviousObservation()
	if lastState and self.pos == (1,1) and self.distancer.getDistance(lastState.getAgentPosition(self.index),self.pos) > 1: 	#died....return to starting position
		self.carryingFood = 0
		self.dieCount += 1
	elif self.pos[0] == self.middle_line and lastState.getAgentPosition(self.index)[0]>self.middle_line:	#come back with food!
		self.carryingFood = 0
		if not self.moreAttackInTime(gameState,gameState.data.timeleft):	#turn defender if not enought time left for attack
			self.is_attacker = False
	elif self.at_home(gameState) and self.getScore(gameState) > 0:
		self.is_attacker = False
	values = [self.evaluate(gameState, a) for a in actions]
	maxValue = max(values)
	bestActions = [a for a, v in zip(actions, values) if v == maxValue]
	if self.getPreviousObservation():	#if not first step,
		self.updateGotfood(self.getCurrentObservation(), self.getPreviousObservation())	
	foodLeft = len(self.getFood(gameState).asList())
	if debug:
		print 'step time for agent %d: %.4f' % (self.index, time.time() - start)
	return random.choice(bestActions)

  def evaluate(self, gameState, action):	#evaluate each successor
	futureState = self.getSuccessor(gameState,action)
	weights = self.getWeights(gameState,futureState)
	features = self.getFeatures(gameState,futureState)
	state_score = 0
	for item_name in features:
		state_score += weights[item_name] * features[item_name]
	if debug:
		print "@",futureState.getAgentPosition(self.index)
		print "attack?", self.is_attacker
		print "actioon=",action
  		print "weights~",weights
  		print 'FEATURES~',features
  		print "Score",state_score,"\n"
		print "died %d times" % self.dieCount
	return state_score

  def getWeights(self,gameState,futureState):
  	Weights = {}
	if self.is_attacker:
		if self.at_home(futureState):
			Weights['op_dist'] = 0
			Weights['op_dist2'] = 0
		else:
			Weights['op_dist'] = self.factors[0]  					#xx
			Weights['op_dist2'] = self.factors[1] 					#xx
		Weights['food_dist'] = self.factors[2]						#xx
		Weights['food_dist2'] = self.factors[3]						#xx
		Weights['dangerousness'] = self.factors[4] 					#xx
		if not self.is_attacker:
			Weights['mid'] = 0
		elif self.at_home(futureState):
			Weights['mid'] = self.factors[5]						#xx
		elif self.beingChased() > 3:					#if being chased, go home quickly
			if self.factors[7] != 0:
				Weights['mid'] = self.beingChased() * self.factors[6] + (gameState.data.timeleft/self.factors[7])	#xx  xx
			else:
				Weights['mid'] = self.beingChased() * self.factors[6]
		else:
			if self.factors[9] != 0:
				Weights['mid'] = self.carryingFood * self.factors[8] + (gameState.data.timeleft/self.factors[9])  #xx  xx
			else: 
				Weights['mid'] = self.carryingFood * self.factors[8]
			
		Weights['foodNextStep'] = self.factors[10] * 50				#xx
		Weights['dieNextStep'] = self.factors[11] * 50				#xx
		Weights['conFood'] = self.factors[12]						#xx
		Weights['killNext'] = 0
	else:
		Weights['conFood'] = 0
		Weights['killNext'] = self.factors[13] * 500					#xx xx
		Weights['op_dist'] = self.factors[14] * 50 					#xx
		Weights['op_dist2'] = self.factors[15]						#xx
		Weights['food_dist'] = 0
		Weights['food_dist2'] = 0
		if self.getMidfeature(gameState,futureState) > 3:
			Weights['mid'] = self.factors[16] * 50						#xx
		else:
			Weights['mid'] = 0
		Weights['foodNextStep'] = 0
		Weights['dieNextStep'] = 0
		Weights['dangerousness'] = 0
  	return Weights 	
     
  def getFeatures(self,gameState,futureState):
  	features = {}
  	features['op_dist'] = self.getOpponentDist(futureState,futureState.getAgentPosition(self.index))
  	features['op_dist2'] = features['op_dist'] * features['op_dist'] 
  	features['food_dist'] = self.getNextFoodDis(futureState,features['op_dist'])	
  	features['food_dist2'] = features['food_dist'] * features['food_dist']
  	features['mid'] = self.getMidfeature(gameState,futureState)
	features['dangerousness'] = self.dangerousness[(self.pos[1],self.pos[0])]
  	features['foodNextStep'] = self.FoodNext(gameState,futureState)
  	features['dieNextStep'] = self.dieNext(gameState,futureState)
  	features['conFood'] = self.consecutiveFood(gameState)
  	features['killNext'] = self.killNext(gameState,futureState)
  	return features
	
  def getNextFoodDis(self,gameState,oppenent_dist):
	target = self.getFood(gameState)
	min_dis, min_coord = 9999, (0,0)
	for i in range(gameState.data.layout.height):
		for j in range(gameState.data.layout.width):
			if target[j][i]:
				food_dis = self.distancer.getDistance(gameState.getAgentPosition(self.index),(j,i))
				if self.dangerousness[(i,j)] < oppenent_dist + 2 and food_dis < min_dis:
					min_dis = food_dis
					min_coord = (i,j)
				return min_dis
				
  def getMidfeature(self,gameState,futureState):
  	return min([self.distancer.getDistance(futureState.getAgentPosition(self.index), (self.middle_line,i)) for i in range(1,futureState.data.layout.height-1)] )

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def killNext(self,gameState,futureState):
  	if gameState.getAgentPosition(self.opponents[0]) == futureState.getAgentPosition(self.index) or gameState.getAgentPosition(self.opponents[1]) == futureState.getAgentPosition(self.index):
  		return 1
  	return 0

  def at_home(self,gameState):	#see if the agent is at home in this gameState
  	if self.red and self.pos[0] <= self.middle_line:
  		return True
  	elif not self.red and self.pos[0] >= self.middle_line:
  		return True
  	return False
	
  def beingChased(self):
	chased_count_rev = 1
	while len(self.observationHistory) > chased_count_rev and chased_count_rev < 10 :
		his_obj = self.observationHistory[-chased_count_rev]
		if self.getOpponentDist(his_obj,his_obj.getAgentPosition(self.index)) > 5:
			break
		chased_count_rev += 1
	if chased_count_rev < 3:
		return 0
	return chased_count_rev
		
  def getOpponentDist(self,gameState, selfPos):  #might not be precise
	op1 = self.opponents[0]
	op2 = self.opponents[1]
	pos = []
	if gameState.getAgentPosition(op1) != None:
		pos.append(self.distancer.getDistance(gameState.getAgentPosition(op1) , selfPos))
	else :
		pos.append(gameState.getAgentDistances()[op1])
	if gameState.getAgentPosition(op2) != None:
	  pos.append(self.distancer.getDistance(gameState.getAgentPosition(op2) , selfPos))
	else:
	  pos.append(gameState.getAgentDistances()[op2])
	return min(pos)

  def consecutiveFood(self,gameState):
	target = self.getFood(gameState)
	food_dis = {}
	for i in range(gameState.data.layout.height):
		for j in range(gameState.data.layout.width):
			if target[j][i]:
				food_dis[(j,i)] = (self.distancer.getDistance(self.pos,(j,i)))
	sorted(food_dis.items(), key=lambda x:x[1])
	for i in food_dis.keys():
		if food_dis[i] > 7:	#x
			del food_dis[i]
	con_sum = 0
	for i in food_dis.keys():
		for j in food_dis.keys():
			if i!=j and self.nextToEachOther(i,j):
				con_sum += 1	#x
	return con_sum
	
  def getnMinFoodDis(self,gameState,n):	#return the sum of the n food with least dist
	target = self.getFood(gameState)
	food_dis = []
	for i in range(gameState.data.layout.height):
		for j in range(gameState.data.layout.width):
			if target[j][i]:
				food_dis.append(self.distancer.getDistance(self.pos,(j,i)))
	min_n_dis_sum = 0
	sorted(food_dis)
	for i in range(n):
		min_n_dis_sum += food_dis[i]
	return min_n_dis_sum
  
  def nextToEachOther(self,pos1,pos2):
	x1,y1 = pos1
	x2,y2 = pos2
	return ((x1==x2+1 or x1 == x2-1) and y1==y2) or ((y1==y2-1 or y1==y2+1) and x1==x2)
	
  def updateGotfood(self,now,past): 
  #see if we got food last step  	
  	if str(self.getFood(now)) != str(self.getFood(past)):
  		self.carryingFood += 1
  	return 

  def FoodNext(self,gameState,futureState):
  	(x,y) = futureState.getAgentPosition(self.index)
  	if self.getFood(gameState)[x][y]:
  		return 1
  	return 0

  def dieNext(self,gameState,futureState):
  	if self.getOpponentDist(futureState,futureState.getAgentPosition(self.index))< 2:
  		return 1
  	return 0

  def moreAttackInTime(self,gameState,timeleft):
	if timeleft/4 < self.getnMinFoodDis(gameState,1) + 5:
		return False
  	return True

#------------below is for initializer, which runs once only--------------------

  def getDangerousness(self, gameState):
	width,height = gameState.data.layout.width, gameState.data.layout.height
	map_state = gameState.getWalls()
	ret = {}
	junctions = set()
	for i in range(0,height):
	  for j in range(0,width):
		if map_state[j][i]:
		  ret[(i,j)] = -1
		elif self.if_three_wall(map_state,(i,j)):
		  ret[(i,j)] = -2
		else:
		  ret[(i,j)] = 0		
	end_points = set()
	for i in range(0,height):
	  for j in range(0,width):
		if ret[(i,j)] == -2:
		  end_points.add(self.mark_until_junction(ret,(i,j)))
	mini_end = set()  
	for p in end_points:
	  tmp = self.find_min(p,ret)
	  mini_end.add(tmp)
	for i in mini_end:
	  if ret[i] < -1:
		self.mod_value(i,0,ret)
	for i in mini_end:
	  if ret[i] == 0:
	  	self.mod_value2(i,ret)
	return ret
	
  def mod_value(self,p,v,ret):
	ret[p] = v
	i,j = p
	if ret[(i+1,j)]<= -2:
	  self.mod_value((i+1,j),v+1,ret)
	if ret[(i-1,j)]<= -2:
	  self.mod_value((i-1,j),v+1,ret)
	if ret[(i,j+1)]<= -2:
	  self.mod_value((i,j+1),v+1,ret)
	if ret[(i,j-1)]<= -2:
	  self.mod_value((i,j-1),v+1,ret)
	return 

  def mod_value2(self,p,ret):	#to balance and avoid stuck
  	i,j = p
  	tot = 0
  	counter = 0
  	if ret[(i+1,j)] > 0:
	  tot += ret[(i+1,j)]
	  counter+=1
	if ret[(i-1,j)] > 0:
	  tot += ret[(i-1,j)]
	  counter+=1
	if ret[(i,j+1)]<= -2:
	  tot += ret[(i,j+1)]
	  counter+=1
	if ret[(i,j-1)]<= -2:
	  tot += ret[(i,j-1)]
	  counter+=1
	if counter:
		ret[i,j] = tot/counter
	return 

  def find_min(self,p,ret):
	i,j = p
	if ret[(i+1,j)] < ret[p]:
	  return self.find_min((i+1,j),ret)
	elif ret[(i-1,j)] < ret[p]:
	  return self.find_min((i-1,j),ret)
	elif ret[(i,j+1)] < ret[p]:
	  return self.find_min((i,j+1),ret)
	elif ret[(i,j-1)] < ret[p]:
	  return self.find_min((i,j-1),ret)
	return p

  def mark_until_junction(self, state, p):
	walker = p
	directions = self.my_getLegalAction(state,p,None)
	flag = True
	while len(directions) == 1 or flag:
	  flag = False
	  next = self.my_walk(walker, directions[0])
	  if state[next] != 0:  #two deadend converge on a same junction 
		if state[next] < state[walker]-1:
		  state[next] = state[walker]-1 
		i,j = next
		directions = []
		if state[(i,j+1)] == 0:
		  directions.append('E')
		if state[(i,j-1)] == 0:
		  directions.append('W')
		if state[(i+1,j)] == 0:
		  directions.append('N')
		if state[(i-1,j)] == 0:
		  directions.append('S')
		if len(directions) == 1:
		  flag = True
		  walker = next
		  continue
	  elif state[next] == 0:
		state[next] = state[walker]-1 
	  walker = next
	  if len(directions) == 0:
	  	break
	  elif directions[0] == 'N':
		dir_from = 'S'
	  elif directions[0] == 'S':
		dir_from = 'N'
	  elif directions[0] == 'W':
		dir_from = 'E'
	  else:
		dir_from = 'W'
	  directions = self.my_getLegalAction(state,walker,dir_from)
	return walker

  def if_three_wall(self, state, p):  #check if there are three walls around p
	i,j = p
	counter = 0
	if state[j][i+1]:
	  counter += 1 
	if state[j][i-1]:
	  counter += 1
	if state[j+1][i]:
	  counter += 1 
	if state[j-1][i]:
	  counter += 1
	return counter == 3

  def getTeammate(self):
	if self.index == 0:
	  return 2
	elif self.index == 1:
	  return 3
	elif self.index == 2:
	  return 0
	elif self.index == 3:
	  return 1
	else:
	  raise ValueError('Teammate error!')

  def my_getLegalAction(self, state, p, exclude):  #get legal action for a point, state is walls
	ret = []
	if state[p] == -1:
	 return []
	i,j = p
	if not state[(i+1,j)] == -1 and not exclude == 'N':	   
	  ret.append('N') 
	if not state[(i-1,j)] == -1 and not exclude == 'S':
	 ret.append('S')
	if not state[(i,j+1)] == -1 and not exclude == 'E':
	  ret.append('E')
	if not state[(i,j-1)] == -1 and not exclude == 'W':
	  ret.append('W')
	return ret

  def my_walk(self, p, direction):
	i,j = p
	if direction == 'N':
	  return (i+1,j)
	elif direction == 'S':
	  return (i-1,j)
	elif direction == 'E':
	  return (i,j+1)
	else:
	  return (i,j-1)

class RandomAgent( Agent ):
  """
  A random agent that abides by the rules.
  """
  def __init__( self, index ):
    self.index = index

  def getAction( self, state ):
    return random.choice( state.getLegalActions( self.index ) )
