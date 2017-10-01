# qlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *
import traceback
import random,util,math




class QLearningAgent(ReinforcementAgent):
  """
    Q-Learning Agent

    Functions you should fill in:
      - getQValue
      - getAction
      - getValue
      - getPolicy
      - update

    Instance variables you have access to
      - self.epsilon (exploration prob)
      - self.alpha (learning rate)
      - self.discount (discount rate)

    Functions you should use
      - self.getLegalActions(state)
        which returns legal actions
        for a state
  """
  def __init__(self, **args):
    "You can initialize Q-values here..."
    ReinforcementAgent.__init__(self, **args)

    "*** YOUR CODE HERE ***"
    self.qValues = util.Counter()
    print "ALPHA", self.alpha
    print "DISCOUNT", self.discount
    print "EXPLORATION", self.epsilon

  def getQValue(self, state, action):
    """
      Returns Q(state,action)
      Should return 0.0 if we never seen
      a state or (state,action) tuple
    """
    "*** YOUR CODE HERE ***"
    return self.qValues[(state, action)]


  def getValue(self, state):
    """
      Returns max_action Q(state,action)
      where the max is over legal actions.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return a value of 0.0.
    """
    "*** YOUR CODE HERE ***"
    possibleStateQValues = util.Counter()
    for action in self.getLegalActions(state):
    	possibleStateQValues[action] = self.getQValue(state, action)
    
    return possibleStateQValues[possibleStateQValues.argMax()]

  def getPolicy(self, state):
    """
      Compute the best action to take in a state.  Note that if there
      are no legal actions, which is the case at the terminal state,
      you should return None.
    """
    "*** YOUR CODE HERE ***"
    possibleStateQValues = util.Counter()
    possibleActions = self.getLegalActions(state)
    if len(possibleActions) == 0:
    	return None
    
    for action in possibleActions:
    	possibleStateQValues[action] = self.getQValue(state, action)
    
    if possibleStateQValues.totalCount() == 0:
    	return random.choice(possibleActions)
    else:
    	return possibleStateQValues.argMax()

  def getAction(self, state):
    """
      Compute the action to take in the current state.  With
      probability self.epsilon, we should take a random action and
      take the best policy action otherwise.  Note that if there are
      no legal actions, which is the case at the terminal state, you
      should choose None as the action.

      HINT: You might want to use util.flipCoin(prob)
      HINT: To pick randomly from a list, use random.choice(list)
    """
    # Pick Action
    legalActions = self.getLegalActions(state)
    action = None
    "*** YOUR CODE HERE ***"
    if len(legalActions) > 0:
    	if util.flipCoin(self.epsilon):
    		action = random.choice(legalActions)
    	else:
			action = self.getPolicy(state)

    return action

  def update(self, state, action, nextState, reward):
    """
      The parent class calls this to observe a
      state = action => nextState and reward transition.
      You should do your Q-Value update here

      NOTE: You should never call this function,
      it will be called on your behalf
    """
    "*** YOUR CODE HERE ***"
    print "State: ", state, " , Action: ", action, " , NextState: ", nextState, " , Reward: ", reward
    print "QVALUE", self.getQValue(state, action)
    print "VALUE", self.getValue(nextState)
    self.qValues[(state, action)] = self.getQValue(state, action) + self.alpha * (reward + self.discount * self.getValue(nextState) - self.getQValue(state, action))

class PacmanQAgent(QLearningAgent):
  "Exactly the same as QLearningAgent, but with different default parameters"

  def __init__(self, epsilon=0.05,gamma=0.9,alpha=0.2, numTraining=0, **args):
    """
    These default parameters can be changed from the pacman.py command line.
    For example, to change the exploration rate, try:
        python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

    alpha    - learning rate
    epsilon  - exploration rate
    gamma    - discount factor
    numTraining - number of training episodes, i.e. no learning after these many episodes
    """
    args['epsilon'] = epsilon
    args['gamma'] = gamma
    args['alpha'] = alpha
    args['numTraining'] = numTraining
    self.index = 0  # This is always Pacman
    QLearningAgent.__init__(self, **args)

  def getAction(self, state):
    """
    Simply calls the getAction method of QLearningAgent and then
    informs parent of action for Pacman.  Do not change or remove this
    method.
    """
    action = QLearningAgent.getAction(self,state)
    self.doAction(state,action)
    return action


class ApproximateQAgent(PacmanQAgent):
  """
     ApproximateQLearningAgent

     You should only have to overwrite getQValue
     and update.  All other QLearningAgent functions
     should work as is.
  """
  def __init__(self, extractor='IdentityExtractor', **args):
    self.featExtractor = util.lookup(extractor, globals())()
    PacmanQAgent.__init__(self, **args)

    # You might want to initialize weights here.
    "*** YOUR CODE HERE ***"
    self.weights = util.Counter()

  def getQValue(self, state, action):
    """
      Should return Q(state,action) = w * featureVector
      where * is the dotProduct operator
    """
    "*** YOUR CODE HERE ***"
    qValue = 0.0
    features = self.featExtractor.getFeatures(state, action)
    for key in features.keys():
    	qValue += (self.weights[key] * features[key])
    return qValue


  def update(self, state, action, nextState, reward):
    """
       Should update your weights based on transition
    """
    "*** YOUR CODE HERE ***"
    features = self.featExtractor.getFeatures(state, action)
    for key in features.keys():
    	self.weights[key] += self.alpha * (reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)) * features[key]

  def final(self, state):
    "Called at the end of each game."
    # call the super-class final method
    PacmanQAgent.final(self, state)

    # did we finish training?
    if self.episodesSoFar == self.numTraining:
      # you might want to print your weights here for debugging
      "*** YOUR CODE HERE ***"
      pass

import numpy as np
class DeepQAgent(PacmanQAgent):
  """
     ApproximateQLearningAgent

     You should only have to overwrite getQValue
     and update.  All other QLearningAgent functions
     should work as is.
  """

  def __init__(self, extractor='IdentityExtractor', **args):
    self.featExtractor = util.lookup(extractor, globals())()
    PacmanQAgent.__init__(self, **args)

    # You might want to initialize weights here.
    "*** YOUR CODE HERE ***"
    self.weights = util.Counter()

    self.globalvar = 1

    # Define NN
    self.model = Sequential()
    self.model.add(Dense(300, init='lecun_uniform', input_shape=(5,)))
    self.model.add(Activation('relu'))

    self.model.add(Dense(300, init='lecun_uniform'))
    self.model.add(Activation('relu'))

    self.model.add(Dense(300, init='lecun_uniform'))
    self.model.add(Activation('relu'))

    self.model.add(Dense(5, init='lecun_uniform'))
    self.model.add(Activation('linear'))

    rms = RMSprop()
    self.model.compile(loss='mse', optimizer=rms)

    self.atoi = {'North': 0, 'South': 1, 'East': 2, 'West': 3, 'Stop': 4}

  def getQValue(self, state, action):
    """
      Should return Q(state,action) = w * featureVector
      where * is the dotProduct operator
    """
    "*** YOUR CODE HERE ***"
    qValue = 0.0
    features = self.featExtractor.getFeatures(state, action)
    #print(features)
    #state = np.array(features.values())
    qval = self.model.predict(np.array(features.values()).reshape(1,5), batch_size=1)
    #print(qval)
    #for key in features.keys():
           #qValue += (self.weights[key] * features[key])
    #print(qValue)
    #print(np.max(qval))
    return np.max(qval)


  def update(self, state, action, nextState, reward):
    """
       Should update your weights based on transition
    """
    "*** YOUR CODE HERE ***"
    features = self.featExtractor.getFeatures(nextState, action)
    of = self.featExtractor.getFeatures(state, action)
    #print(features)
    #for key in features.keys():
   # 	self.weights[key] += self.alpha * (reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)) * features[key]
    #print("r: " + reward)
    #myReward = self.getValue(nextState)
    #print(reward, myReward)

    #print(self.numTraining)
    y = np.zeros((1,5))
    print features.keys
    newQ = self.model.predict(np.array(features.values()).reshape(1,5), batch_size=1)
    print self.model.predict(np.array(features.values()).reshape(1,5), batch_size=1)
    maxQ = np.max(newQ)

    self.globalvar += 1
    if self.globalvar >= 3975:
      print(self.globalvar)
      traceback.print_stack()
    update = (reward + (self.discount * maxQ))
    print "reward"
    print reward
    print "maq * discount"
    print (self.discount * maxQ)
    y[0][self.atoi[action]] = update
    if self.episodesSoFar <= self.numTraining:
        self.model.fit(np.array(of.values()).reshape(1,5), y, batch_size=1, nb_epoch=1, verbose=0)

        self.model.save_weights('test.h5', overwrite=True)
    if  self.discount > 0.1:
        self.discount -= (1/self.numTraining)
    
  def final(self, state):
    "Called at the end of each game."
    # call the super-class final method
    PacmanQAgent.final(self, state)

    # did we finish training?
    if self.episodesSoFar == self.numTraining:
      # you might want to print your weights here for debugging
      "*** YOUR CODE HERE ***"
      pass


