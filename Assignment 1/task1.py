"""
NOTE: You are only allowed to edit this file between the lines that say:
    # START EDITING HERE
    # END EDITING HERE

This file contains the base Algorithm class that all algorithms should inherit
from. Here are the method details:
    - __init__(self, num_arms, horizon): This method is called when the class
        is instantiated. Here, you can add any other member variables that you
        need in your algorithm.
    
    - give_pull(self): This method is called when the algorithm needs to
        select an arm to pull. The method should return the index of the arm
        that it wants to pull (0-indexed).
    
    - get_reward(self, arm_index, reward): This method is called just after the 
        give_pull method. The method should update the algorithm's internal
        state based on the arm that was pulled and the reward that was received.
        (The value of arm_index is the same as the one returned by give_pull.)

We have implemented the epsilon-greedy algorithm for you. You can use it as a
reference for implementing your own algorithms.
"""

import numpy as np
import math
# Hint: math.log is much faster than np.log for scalars

class Algorithm:
    def __init__(self, num_arms, horizon):
        self.num_arms = num_arms
        self.horizon = horizon
    
    def give_pull(self):
        raise NotImplementedError
    
    def get_reward(self, arm_index, reward):
        raise NotImplementedError

# Example implementation of Epsilon Greedy algorithm
class Eps_Greedy(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # calls parent class constructor
        # Extra member variables to keep track of the state
        self.eps = 0.1
        # explortation param
        self.counts = np.zeros(num_arms)
# NumPy array that keeps track #x each arm is pulled
        self.values = np.zeros(num_arms)
# stores estimated(expected) rewards for each arm
    
    def give_pull(self):
# wp e sample an arm uniformly at random otherwise explore
        if np.random.random() < self.eps:
            return np.random.randint(self.num_arms)
# sampling arm uniformly
        else:
#selects arm with highest empirical probability
            return np.argmax(self.values)
    
    def get_reward(self, arm_index, reward):
        self.counts[arm_index] += 1
# increasing the count of arm to be pulled
        n = self.counts[arm_index]
        value = self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value

# START EDITING HERE
# You can use this space to define any helper functions that you need
# END EDITING HERE

class UCB(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # Initialize counts for each arm to 1 (starting value)
        self.counts = np.ones(num_arms)
        # Initialize Empirical probability for each arm with random values between 0 and 1
        self.values = np.random.rand(num_arms)
        self.ucb    = np.zeros(num_arms)
 
    def give_pull(self):
        TotalPulls = np.sum(self.counts)
        # updating UCB 
        self.ucb= self.values + np.sqrt(2*(math.log(TotalPulls))/self.counts)      
        return np.argmax(self.ucb)
  
    def get_reward(self, arm_index, reward):
        # updating empirical probability
        self.counts[arm_index] += 1
        n     =  self.counts[arm_index]
        value =  self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value
 

def kl(x,y):
    ep =1.0e-6
    ans= x*math.log(x/(y+ep) +1.0e-6)+(1-x)*math.log((1-x)/(1-y+ep)+1.0e-6)
    return ans

class KL_UCB(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # START EDITING HERE
        self.counts = np.ones(num_arms)
        self.values = np.random.rand(num_arms)
        self.klucb  = np.ones(num_arms)-0.01
        self.t      = num_arms
        self.num    = num_arms
         # END EDITING HERE

    def give_pull(self):
       ti =self.t 
       num    = (math.log(ti))
       iter =0
       for i in range(self.num):
           target = num/self.counts[i]
           iter=0
           left = self.values[i]
           right=0.999
           mid =0       
           klpq=1  
           while ( abs(klpq)>0.01 and iter<=5) :
              mid =(left+right)/2
              iter+=1
              klpq = kl(self.values[i],mid)-target 
              if( klpq >0):
                  right=mid
              else :
                  left = mid 
           self.klucb[i]=mid

       self.t +=1
       return np.argmax(self.klucb)
        # raise NotImplementedError
        # END EDITING HERE
    
    def get_reward(self, arm_index, reward):
       self.counts[arm_index] += 1
       n     =  self.counts[arm_index]
       value =  self.values[arm_index]
       new_value = ((n - 1) / n) * value + (1 / n) * reward
       self.values[arm_index] = new_value  

       


              
class Thompson_Sampling(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # You can add any other variables you need here
        # START EDITING HERE
        self.successes = np.ones(num_arms)
        self.failures  = np.zeros(num_arms)
        self.values    = np.random.rand(num_arms)
        self.beta      = np.zeros(num_arms)
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        self.beta = np.random.beta(self.successes+1,self.failures+1)
        return np.argmax(self.beta)
        # raise NotImplementedError
        # END EDITING HERE
    
    def get_reward(self, arm_index, reward):
        # START EDITING HERE
        if reward==1:  self.successes[arm_index]+=1
        else :         self.failures[arm_index]+=1
        
        n     =  self.successes[arm_index]+self.failures[arm_index]
        value =  self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value

        # raise NotImplementedError
        # END EDITING HERE
