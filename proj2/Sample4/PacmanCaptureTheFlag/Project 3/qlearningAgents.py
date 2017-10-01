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
    self.Q = util.Counter()

  def getQValue(self, state, action):
    """
      Returns Q(state,action)
      Should return 0.0 if we've never seen
      a state or (state,action) tuple
    """
    "*** YOUR CODE HERE ***"
    "Case we haven't seen this state yet, so add a dictionary to hold its Q-values which will be indexed by legal actions"
    if state not in self.Q:
        self.Q[state] = util.Counter()
        
    return self.Q[state][action]

  def getValue(self, state):
    """
      Returns max_action Q(state,action)
      where the max is over legal actions.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return a value of 0.0.
    """
    "*** YOUR CODE HERE ***"
    maxQstate = -100000000
    maxAction = None
    
    for action in self.getLegalActions(state):
      Qstate = self.getQValue(state,action)
      if Qstate > maxQstate:
          maxQstate = Qstate
          maxAction = action
      elif Qstate == maxQstate:
          [maxQstate,maxAction] = random.choice([[maxQstate,maxAction],[Qstate,action]])
    
    if maxQstate == -100000000:
        maxQstate = 0.0
            
    return maxQstate

  def getPolicy(self, state):
    """
      Compute the best action to take in a state.  Note that if there
      are no legal actions, which is the case at the terminal state,
      you should return None.
    """
    "*** YOUR CODE HERE ***"
    maxQstate = -100000000
    maxAction = None
    
    for action in self.getLegalActions(state):
      Qstate = self.getQValue(state,action)
      if Qstate > maxQstate:
          maxQstate = Qstate
          maxAction = action
      elif Qstate == maxQstate:
          [maxQstate,maxAction] = random.choice([[maxQstate,maxAction],[Qstate,action]])
        
    return maxAction

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
    legalActions = self.getLegalActions(state)
    action = None
    "*** YOUR CODE HERE ***"
    "If there are no legal actions available, return None"
    if len(legalActions) <= 0:
        return None
    
    "Case we should randomly pick an action from all legal actions at this state"
    if util.flipCoin(self.epsilon) == True:
        return random.choice(legalActions)
    
    "Case we should consult the policy to choose the best action at this state"
    return self.getPolicy(state)

  def update(self, state, action, nextState, reward):
    """
      The parent class calls this to observe a
      state = action => nextState and reward transition.
      You should do your Q-Value update here

      NOTE: You should never call this function,
      it will be called on your behalf
    """
    "*** YOUR CODE HERE ***"
    gamma = self.discount
    alpha = self.alpha
    
    "Case we haven't seen this state yet, so add a dictionary to hold its Q-values which will be indexed by legal actions"
    if state not in self.Q:
        self.Q[state] = util.Counter()
        
    self.Q[state][action] = (1-alpha)*self.getQValue(state,action) + alpha*(reward+gamma*self.getValue(nextState))

class PacmanQAgent(QLearningAgent):
  "Exactly the same as QLearningAgent, but with different default parameters"

  def __init__(self, epsilon=0.05,gamma=0.8,alpha=0.2, numTraining=0, **args):
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
    self.featureExtractor = util.lookup(extractor, globals())()
    PacmanQAgent.__init__(self, **args)

    # You might want to initialize weights here.
    "*** YOUR CODE HERE ***"
    self.f = util.Counter()
    self.w = util.Counter()
    
  def getQValue(self, state, action):
    """
      Should return Q(state,action) = w * featureVector
      where * is the dotProduct operator
    """
    "*** YOUR CODE HERE ***"
    if state not in self.f:
        self.f[state] = util.Counter()
    
    if action not in self.f[state]:
        self.f[state][action] = util.Counter()
    
    self.f[state][action] = self.featureExtractor.getFeatures(state,action)
    
    "Q=<f,w> where f is the feature vector and w is the vector of scalar weights"
    Q = 0
    for key,value in self.f[state][action].items():
        Q += value*self.w[key]
        
    return Q

  def update(self, state, action, nextState, reward):
    """
       Should update your weights based on transition
    """
    "*** YOUR CODE HERE ***"
    alpha = self.alpha
    gamma = self.discount
    
    if state not in self.f:
        self.f[state] = util.Counter()
        
    if action not in self.f[state]:
        self.f[state][action] = util.Counter()
    
    for key,value in self.f[state][action].items():
        correction = reward+gamma*self.getValue(nextState)-self.getQValue(state,action)
        self.w[key] += alpha*correction*value
        
  def final(self, state):
    "Called at the end of each game."
    # call the super-class final method
    PacmanQAgent.final(self, state)

    # did we finish training?
    if self.episodesSoFar == self.numTraining:
      # you might want to print your weights here for debugging
      "*** YOUR CODE HERE ***"
