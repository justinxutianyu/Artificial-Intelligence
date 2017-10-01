from learningAgents import ReinforcementAgent
import util
import pickle

class LearningAgent(ReinforcementAgent):
    
  def __init__(self,filename):
    "For saving the weights at each iteration"
    self.filename = filename
    self.w = util.Counter()
    
    # Set up default alpha and gamma TUNE THESE
    self.alpha = 0.1
    self.gamma = 0.85
    
  def setWeights(self,newWeights=None):
    if newWeights == None:
        newWeights = pickle.load(open(self.filename,"rb"))
    self.w = newWeights
      
  # This function takes in a state, action and features and returns the QVal
  def getQValue(self, features):
    self.feature = features
    """
      Should return Q(state,action) = w * featureVector
      where * is the dotProduct operator
    """
    Q = 0
    for key,value in self.w.items():
        Q += features[key]*self.w[key]
    return Q

  def getWeights(self):
      return self.w
  
  # This updates the new weights using currentQVal, nextQVal, reward and features
  def update(self, currentQVal, nextQVal, reward, feature, gamma = None):
    """
       Should update your weights based on transition
    """
    "*** YOUR CODE HERE ***"
    alpha = self.alpha
    if gamma == None:
        gamma = self.gamma

    for key,value in self.w.items():
        correction = reward+gamma*nextQVal-currentQVal
        self.w[key] += alpha*correction*feature[key]
        
  def getPolicy(self, state, featureVectorsForAllActionsAtGivenState):
    """
      Compute the best action to take in a state.  Note that if there
      are no legal actions, which is the case at the terminal state,
      you should return None.
    """
    "*** YOUR CODE HERE ***"
    maxQstate = -100000000
    maxAction = None
    
    for action in self.getLegalActions(state):
      Qstate = self.getQValue(state,action,featureVectorsForAllActionsAtGivenState)
      if Qstate > maxQstate:
          maxQstate = Qstate
          maxAction = action
      elif Qstate == maxQstate:
          [maxQstate,maxAction] = random.choice([[maxQstate,maxAction],[Qstate,action]])
        
    return maxAction
      
  "Given a state and its feature vector, return the best action to take"  
  def getAction(self, state, featureVectorsForAllActionsAtGivenState):
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
    return self.getPolicy(state,featureVectorsForAllActionsAtGivenState)

  def __del__(self):
      pickle.dump(self.w, open(self.filename, "wb"))



