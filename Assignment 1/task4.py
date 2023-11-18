"""
NOTE: You are only allowed to edit this file between the lines that say:
    # START EDITING HERE
    # END EDITING HERE

This file contains the MultiBanditsAlgo class. Here are the method details:
    - __init__(self, num_arms, horizon): This method is called when the class
        is instantiated. Here, you can add any other member variables that you
        need in your algorithm.
    
    - give_pull(self): This method is called when the algorithm needs to
        select an arm to pull. The method should return the index of the arm
        that it wants to pull (0-indexed).
    
    - get_reward(self, arm_index, set_pulled, reward): This method is called 
        just after the give_pull method. The method should update the 
        algorithm's internal state based on the arm that was pulled and the 
        reward that was received.
        (The value of arm_index is the same as the one returned by give_pull 
        but set_pulled is the set that is randomly chosen when the pull is 
        requested from the bandit instance.)
"""

import numpy as np

# START EDITING HERE
# You can use this space to define any helper functions that you need
# END EDITING HERE


class MultiBanditsAlgo:
    def __init__(self, num_arms, horizon):
        # You can add any other variables you need here
        self.num_arms = num_arms
        self.horizon = horizon
        # START EDITING HERE
        self.successes = np.zeros(num_arms)
        self.failures = np.zeros(num_arms)
        self.values = np.zeros(num_arms)
        self.beta      = np.zeros(num_arms)
        self.set0 =0
        self.set1 =0
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        # raise NotImplementedError
        self.beta = np.random.beta(self.successes+1,self.failures+1)
        return np.argmax(self.beta)
        # END EDITING HERE
    
    def get_reward(self, arm_index, set_pulled, reward):
        # START EDITING HERE
        # raise NotImplementedError
        # END EDITING HERE
        if reward==1:  self.successes[arm_index]+=1
        else :         self.failures[arm_index]+=1
        
        self.set0 += 1-set_pulled
        self.set1 += set_pulled