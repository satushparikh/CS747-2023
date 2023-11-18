import numpy as np
import argparse
import pulp
parser=argparse.ArgumentParser()

# --mdp followed by a path to the input MDP file
parser.add_argument("--mdp",required=True,
                    help="Path to input MDP file")
# --algorithm followed by one of vi, hpi, and lp. You must
# assign a default value out of vi, hpi, and lp to allow the
# code to run without this argument
parser.add_argument("--algorithm",
                    default="lp",
                    choices=["vi","hpi","lp"],
                    help="MDP solving algorithm")
# --policy (optional) followed by a policy file, for which the
# value function V^π is to be evaluated
parser.add_argument("--policy", help="Path to the policy file")

args = parser.parse_args()
 
mdp_file_path = args.mdp
algo      = args.algorithm
pol_file  = args.policy
""" 
to access transitions based on their attributes 
(e.g., finding a transition with specific (s1, a, s2) values),
 using a dictionary is more efficient than list
"""
# transitions = dict()
transitions ={}     #same syntax
with open(mdp_file_path,"r") as file:
    for line in file:
        line =line.strip()
        if  line.startswith("numStates"):
            numStates = int(line.split()[1])
        elif line.startswith("numActions"):
            numActions=int(line.split()[1])
        elif line.startswith("end"):
            terminal_states = list(map(int, line.split()[1:]))
        elif line.startswith("transition"):
             parts = line.split()
             s1 = int(parts[1])
             ac = int(parts[2])
             s2 = int(parts[3])
             r = float(parts[4])
             p = float(parts[5])
             
             trans_key =(s1,ac,s2)
             trans_val =(r,p)
             transitions[trans_key]= trans_val

        elif line.startswith("mdptype"):
            mdptype = line.split()[1]

        elif line.startswith("discount"):
            discount = float(line.split()[1])     
# refereed Robbins and Munro I mean sutton and munro
 
def PolicyEvaluation(numStates, numActions, terminal, transition, mdptype, discount_factor, pi):
    gamma = discount_factor
    # epsilon to reach desired level of  Accuracy
    tolerance = 1.0e-9
    # V0 ← Arbitrary, element-wise bounded, n-length vector
    value = np.zeros(numStates)

    while True:
        delta = 0
        for state in range(numStates):
            if state not in terminal:
                v_state = 0
                action = int(pi[state])
                for dest_state in range(numStates):
                    if (state, action, dest_state) in transition:
                        r, p = transition[(state, action, dest_state)]
                        v_state += p * (r + gamma * value[dest_state])
                delta = max(delta, abs(v_state - value[state]))
                value[state] = v_state
        if delta < tolerance:
            break

    return value
 
def ValueIteration(numStates,numActions,terminal,transition,mdptype,discount_factor):
    gamma =discount_factor
    # epsilon to reach desired level of  Accuracy
    tolerance    = 1.0e-9        
    # V0 ← Arbitrary, element-wise bounded, n-length vector
    value = np.zeros(numStates)       #initialize with zeros

    # either should be initialised randomly among the number of actions availabe 
    # or to 0 which deals with edge case of only one action availabe
    policy = np.random.randint(0, numActions, numStates)
    # policy = np.zeros(numStates)    
    
 
    while True :
        delta = 0
        for state in range(numStates):

            if state not in terminal:
                v = value[state]
                max_v = float('-inf')
                best_action = None
                
                for act in range(numActions):   #Value function for  a
                    v_act=0
                    for dest_state in range(numStates):
                        if((state,act,dest_state)in transition):
                            r,p = transition[(state,act,dest_state)]
                            v_act+=p*(r+gamma*value[dest_state])
                    if    v_act > max_v:
                        max_v = v_act
                        best_action = act
                value[state] = max_v
                policy[state]=best_action
                delta = max(delta, abs(v-value[state]))
        
        if delta < tolerance:
            break
 
    for i in range(numStates):
       value_str = f"{value[i]:.6f}"
       action_str = str(int(policy[i]))
       print(f"{value_str} \t {action_str}\n", end="")
 
 

def HPI(n, a, terminal, transitions, mdptype, g):
 
    v = np.zeros(n)
    pi = np.zeros(n)
    possible_trans = transitions.keys()
    isImprovable = True
    
    while isImprovable:
        v = PolicyEvaluation(n, a, terminal, transitions, mdptype,g, pi)
        isImprovable = False
        
        for i in range(n):
            if (i in terminal):
                continue
            improvable = list()
            for j in range(a):
                sumq = 0
                for k in range(n):
                    if((i,j,k) in possible_trans):
                        # Transition (i,j,k) has non-zero probability
                        r = transitions[(i,j,k)][0]
                        t = transitions[(i,j,k)][1]
                        sumq += t*(r + g*v[k])
                if(sumq-v[i]>1e-6):
                    improvable.append(j)
                    
            if(len(improvable) > 0):
                pi[i] = np.random.choice(improvable)
                isImprovable = True
    
    for i in range(n):
        value = str("{:.6f}".format(v[i]))
        action = str(int(pi[i]))
        print(value + "\t" + action + "\n", end = "")  
        



 
def LinearProgramming(numStates,numActions,terminal,transition,mdptype,discount_factor):
    gamma =discount_factor
         
    # V0 ← Arbitrary, element-wise bounded, n-length vector
    value = np.zeros(numStates) 
    policy = np.zeros(numStates)
    
    lp = pulp.LpProblem("MDP",pulp.LpMinimize)
    # Creating value function for each state
    V = {s: pulp.LpVariable(f"V_{s}") for s in range(numStates)}

    # Objective function
    lp  += pulp.lpSum([V[s] for s in range(numStates)])

    # adding Bellman equation constraints for each state action pair
    for state in range(numStates):
        if(state in terminal):
            lp += V[state] == 0
            # lp += V[state] >= 0
            # lp += V[state] <= 0
            continue 

        for act in range(numActions):
            constraint =0 
            for dest_state in range(numStates):
                if((state,act,dest_state)in transition):
                            r,p = transition[(state,act,dest_state)]
                            constraint += p*(r+gamma*V[dest_state])
            lp += V[state] >= constraint          
    
    status = lp.solve(pulp.PULP_CBC_CMD(msg=0))
    value_function = {s: pulp.value(V[s]) for s in range(numStates)}

    # Now find actions which maximise Bellman equations
    for i in range(numStates):
        action='0'
        if(i in terminal):
            action = '0'
        else:
            prev_max=0
            for act in range(numActions):
                sum=0
                for dest in range(numStates):
                    if((i,act,dest) in transition):
                        r,p = transition[trans_key]
                        sum += p*(r+gamma*value_function[dest])
                if(sum > prev_max):
                    action = str(act)
                    prev_max = sum 
 
        value_str = f"{value_function[i]:.6f}"
        action_str= str(int(action))
        print(f"{value_str} \t {action_str}\n", end="")
 
if pol_file is not None:
    with open(pol_file,'r') as read:
        policy = read.readlines()
    value = PolicyEvaluation(numStates,numActions,terminal_states,transitions,mdptype,discount,policy)
    for i in range(numStates):
       value_str = f"{value[i]:.6f}"
       action_str = str(int(policy[i]))
       print(f"{value_str} \t {action_str}\n", end="")

        # value = str("{:.6f}".format(val[i]))
        # action = str(int(policy[i]))
        # print(val + "\t" + action + "\n", end = "")
else:
    if(algo=="vi"):
        ValueIteration(numStates,numActions,terminal_states,transitions,mdptype,discount)
        # VI(numStates,numActions,terminal_states,transitions,mdptype,discount)
    elif(algo=="hpi"):
        HPI(numStates,numActions,terminal_states,transitions,mdptype,discount)
    elif(algo=="lp"):
        LinearProgramming(numStates,numActions,terminal_states,transitions,mdptype,discount)

#(numStates,numActions,terminal,transition,mdptype,discount_factor):
  