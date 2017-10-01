# valueIterationAgents.py
# -----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import mdp, util, random

from learningAgents import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
  """
      * Please read learningAgents.py before reading this.*

      A ValueIterationAgent takes a Markov decision process
      (see mdp.py) on initialization and runs value iteration
      for a given number of iterations using the supplied
      discount factor.
  """
  def __init__(self, mdp, discount = 0.9, iterations = 100):
    """
      Your value iteration agent should take an mdp on
      construction, run the indicated number of iterations
      and then act according to the resulting policy.
    
      Some useful mdp methods you will use:
          mdp.getStates()
          mdp.getPossibleActions(state)
          mdp.getTransitionStatesAndProbs(state, action)
          mdp.getReward(state, action, nextState)
    """
    self.mdp = mdp
    self.discount = discount
    self.iterations = iterations
     
    "*** YOUR CODE HERE ***"
    "value at each state"
    self.V = util.Counter()
    self.tempV = util.Counter()
    "Q for each state,action pair"
    self.Q = util.Counter()
    "policy for each state = best action to take"
    self.P = util.Counter()
    gamma = self.discount

    for iter in range(1,self.iterations+1):
      for state in mdp.getStates():
        "There is a Q for each (state,action) pair, so index this by state and keep a list of all actions"
        self.Q[state] = util.Counter()
        "Cycle through each possible action for the given state"
        for action in mdp.getPossibleActions(state):
          for neighborStateAndTransitionProb in mdp.getTransitionStatesAndProbs(state,action):
            [neighborState, T_s_a_sp] = neighborStateAndTransitionProb  
            "Compute the Q values for this state and the available actions"
            R_s_a_sp = mdp.getReward(state,action,neighborState)
            self.Q[state][action] += T_s_a_sp*(R_s_a_sp+gamma*self.V[neighborState])
            
        "As long as there were actions at this state, find the one that produces the largest Q value"
        if len(self.Q[state]) > 0:
          maxQstate = -1000000
          maxQAction = None
          for key,value in self.Q[state].items():
            if value > maxQstate:
                maxQstate = value
                maxQAction = key
            elif value == maxQstate:
                [maxQstate,maxQAction] = random.choice([[maxQstate,maxQAction],[value,key]])
          if maxQstate == -10000000:
            maxQstate = 0.0
                
          "Find the policy (or best action) that corresponds to the best Q value"
          self.P[state] = maxQAction
          "Choose the value of the state to be the max Q value that the state has"
          self.tempV[state] = self.Q[state][maxQAction]

      "After all states have been updated, store tempV in V before the next iteration"
      self.V = self.tempV.copy()
    
  def getValue(self, state):
    """
      Return the value of the state (computed in __init__).
    """
    return self.V[state]


  def getQValue(self, state, action):
    """
      The q-value of the state action pair
      (after the indicated number of value iteration
      passes).  Note that value iteration does not
      necessarily create this quantity and you may have
      to derive it on the fly.
    """
    "*** YOUR CODE HERE ***"
    return self.Q[state][action]

  def getPolicy(self, state):
    """
      The policy is the best action in the given state
      according to the values computed by value iteration.
      You may break ties any way you see fit.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return None.
    """
    "*** YOUR CODE HERE ***"
    return self.P[state]

  def getAction(self, state):
    "Returns the policy at the state (no exploration)."
    return self.getPolicy(state)
  
