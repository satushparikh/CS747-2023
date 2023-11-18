import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--opponent",required=True,help="Path to opponent policy file")
parser.add_argument("--p",required=True,default=0.1,help="Player param p")
parser.add_argument("--q",required=True,default=0.7,help="Player param q")

args = parser.parse_args()

opponent_policy_path = args.opponent


def load_opponent_policy(opponent_policy_path):
    opponent_policy ={}
    try:
        with open(opponent_policy_path,'r') as file:
            # Read Header line
            header = next(file)
            actions=header.strip().split()[1:]

            # Processing actions
            for line in file:
                # split the line into tokens
                tokens = line.strip().split()
                # state P(L) P(R) P(U) P(D)
                # extract state and probabilites
                state = int(tokens[0])
                probabilites=[float(prob) for prob in tokens[1:]]
                # store the key value pair in the dictionary
                opponent_policy[state]=probabilites
    except FileNotFoundError:
        print(f"Error: The opponent policy file '{opponent_policy_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the opponent policy file: {str(e)}")
    return opponent_policy
##### caution index of state is string and not integer
def indices_of_iterable_states():
    # Create a list to store the states
    states = []

    # Iterate over states of the form xyzw
    for x in range(1, 17):
        for y in range(1, 17):
            for z in range(1, 17):
                for w in [1, 2]:
                    state = int(f"{x:02}{y:02}{z:02}{w}")
                    ####################################
                    # Ensure that each state is represented as 7 bits
                    states.append(state)
    return states  
#  get coordinates function is tested and working correctly
def get_coordinates(state):
    formatted_string = f"{state:07}"
    B1 = formatted_string[:2]
    B1_int = int(B1)
    x1 = (B1_int - 1) % 4
    y1 = 3 - (B1_int - 1) // 4

    B2 = formatted_string[2:4]
    B2_int = int(B2)
    x2 = (B2_int - 1) % 4
    y2 = 3 - (B2_int - 1) // 4

    R = formatted_string[4:6]
    R_int = int(R)
    xr = (R_int - 1) % 4
    yr = 3 - (R_int - 1) // 4
    return x1, y1,x2,y2,xr,yr
# finding new coordinates after valid action
def isPlayerInBound(state,action):
    x1, y1,x2,y2,xr,yr = get_coordinates(state)
    a=int(action)
    
    B1_out =(x1==0 and a==0) or (x1==3 and a==1) or (y1==3 and a==2) or (y1==0 and a==3) 
    B2_out =(x2==0 and a==4) or (x2==3 and a==5) or (y2==3 and a==6) or (y2==0 and a==7)
    
    return B1_out or B2_out 

def get_state_from_coordinates(x1_f, y1_f, x2_f, y2_f, xr_f, yr_f, final_possession_with):
    # Convert coordinates and a value to the specified format
    B1_square = f"{(13 +x1_f - 4 * y1_f ):02}"
    B2_square = f"{(13 +x2_f - 4 * y2_f ):02}"
    R_square = f"{(13  +xr_f - 4 * yr_f ):02}"
    ball_possession = f"{final_possession_with}"

    # Create the final state      ####### string
    state = f"{B1_square}{B2_square}{R_square}{ball_possession}"

    return state

def nextState(state,action,action_opposition):   
    # finding nextState iff valid action ,action checked previously
    x1,y1,x2,y2,xr,yr = get_coordinates(state)
    x1_f,y1_f,x2_f,y2_f,xr_f,yr_f = x1,y1,x2,y2,xr,yr 
    final_possession_with = state%10
    # action = 0,1,2,3,4,5,6,7 possession is either lost or does not change
    # action = 8 attempt pass to teammate possession changed or lost
    # action = 9 goal scored or won
    if action==8:
        final_possession_with=3-final_possession_with
    # x1_f=0
# Define movement for B1 based on action (0, 1, 2, 3: L, R, U, D)
    if action == 0:  # Move B1 to the left (L)
        if x1 == 0:

            raise ValueError("Illegal move: B1 can't move left.")
        x1_f, y1_f = x1 - 1, y1
    elif action == 1:  # Move B1 to the right (R)
        if x1 == 3:
            raise ValueError("Illegal move: B1 can't move right.")
        x1_f, y1_f = x1 + 1, y1
    elif action == 2:  # Move B1 up (U)
        if y1 == 3:
            raise ValueError("Illegal move: B1 can't move up.")
        x1_f, y1_f = x1, y1 + 1
    elif action == 3:  # Move B1 down (D)
        if y1 == 0:
            raise ValueError("Illegal move: B1 can't move down.")
        x1_f, y1_f = x1, y1 - 1
    else:  #for the case of passing and shooting they stay where they are
        x1_f,y1_f = x1,y1
    # this is for opposition player
    if action_opposition == 0:  # Move Br to the left (L)
        if xr == 0:
            raise ValueError("Illegal move: Opponent can't move left.")
        xr_f, yr_f = xr - 1, yr
    elif action_opposition == 1:  # Move B1 to the right (R)
        if xr == 3:
            raise ValueError("Illegal move: Opponent can't move right.")
        xr_f, yr_f = xr + 1, yr
    elif action_opposition == 2:  # Move B1 up (U)
        if yr == 3:
            raise ValueError("Illegal move: Opponent can't move up.")
        xr_f, yr_f = xr, yr + 1
    elif action_opposition == 3:  # Move B1 down (D)
        if yr == 0:
            raise ValueError("Illegal move: Opponent can't move down.")
        xr_f, yr_f = xr, yr - 1

    # Define movement for B2 based on action_opposition (4, 5, 6, 7: L, R, U, D)
    if action == 4:  # Move B2 to the left (L)
        if x2 == 0:
            raise ValueError("Illegal move: B2 can't move left.")
        x2_f, y2_f = x2 - 1, y2
    elif action == 5:  # Move B2 to the right (R)
        if x2 == 3:
            raise ValueError("Illegal move: B2 can't move right.")
        x2_f, y2_f = x2 + 1, y2
    elif action == 6:  # Move B2 up (U)
        if y2 == 3:
            raise ValueError("Illegal move: B2 can't move up.")
        x2_f, y2_f = x2, y2 + 1
    elif action == 7:  # Move B2 down (D)
        if y2 == 0:
            raise ValueError("Illegal move: B2 can't move down.")
        x2_f, y2_f = x2, y2 - 1
    else:
        x2_f,y2_f =x2,y2
    
    return int(get_state_from_coordinates(x1_f, y1_f, x2_f, y2_f, xr_f, yr_f,final_possession_with))

# checks if one of the two cases of tackling
def tackling_case(state,action,action_opposition):
    x1, y1,x2,y2,xr,yr = get_coordinates(state)

    x1_f,y1_f,x2_f,y2_f,xr_f,yr_f = get_coordinates(nextState(state,action,action_opposition))
    if state%10 == 1: #it means ball was with player 1 initially
        # step in same square or swap adjacent squares
        if ((x1_f,y1_f)==(xr_f,yr_f)and action<4) or ((x1,y1)==(xr_f,yr_f) and (x1_f,y1_f)==(xr,yr))  :
            return True
        else:
            return False
    elif state%10==2:
        if ((x2_f,y2_f)==(xr_f,yr_f)and action>=4) or ((x2,y2)==(xr_f,yr_f) and (x2_f,y2_f)==(xr,yr)):
            return True
        else:
            return False
    else:
        raise ValueError("Invalid player number")
# for passing check if opposition player hinders movement
def b_blocks(state,action,action_opposition):
    x1,y1,x2,y2,xr,yr = get_coordinates(state)
    next_state= nextState(state,action,action_opposition)
    x1_f,y1_f,x2_f,y2_f,xr_f,yr_f = get_coordinates(next_state)

    # does opponent after taking action lies on same lines as both players
    # cases 
    # also R should be between the two players or be overlapping with them
    y_between= (y1<=yr_f<=y2) or (y1>=yr_f>=y2)       
    x_between= (x1<=xr_f<=x2) or (x1>=xr_f>=x2)     
    is_vertical = (x1 == x2 == xr_f) and (y_between )
    is_horizontal = (y1 == y2 == yr_f) and (x_between)
    is_diagonal_x_plus_y = (x1 + y1 == x2 + y2 == xr_f + yr_f ) and x_between and y_between
    is_diagonal_x_minus_y = (x1 - y1 == x2 - y2 == xr_f - yr_f) and x_between and y_between 
    
    obstructs = is_diagonal_x_minus_y or is_diagonal_x_plus_y or is_horizontal or is_vertical
    return obstructs

def encode_game_position(game_position):
    if len(game_position) != 7:
        return "Invalid input format"

    # Extract individual values
    B1_square = int(game_position[0:2])
    B2_square = int(game_position[2:4])
    R_square = int(game_position[4:6])
    ball_possession = int(game_position[6])

    # Encode the game position using the formula
    encoded_value = (B1_square-1) + 16 * (B2_square-1) + 16**2 * (R_square-1) + 16**3 * (ball_possession-1)

    return encoded_value


def printTransition(key,dictionary):
  if key in dictionary:
    (s1,a,s2) = key
    (r,p)     = dictionary[key]

    s1_encoded = str(s1).zfill(7)
    
    s1_enc = encode_game_position(s1_encoded)+2
    
    
    if s2 not in (0,1):
        s2_encoded = str(s2).zfill(7)    
        s2_enc = encode_game_position(s2_encoded)+2
    else:
        s2_enc = s2
    print(f"transition {s1_enc} {a} {s2_enc} {r} {p:.6f}")
# def printTransition(key,dictionary):
#   if key in dictionary:
#     (s1,a,s2) = key
#     (r,p)     = dictionary[key]

#     s1_encoded = str(s1).zfill(7)
#     s2_encoded = str(s2).zfill(7)

#     print(f"transition {s1_encoded} {a} {s2_encoded} {r} {p:.6f}")

    
def updateDictionary(key,dictionary,trans_val):
    if key not in dictionary :
        dictionary[key]=trans_val
    else:
        r,p=dictionary[key]
        # reward if zero remains zero,and if remains 1 for same final state
        updated_r = r
        updated_p = p + trans_val[1]
        dictionary[key]=(updated_r,updated_p)

def encode_game_to_mdp(opponent_file, p, q):
    # Load the opponent policy from the file (you may need to implement this)
    opponent_policy = load_opponent_policy(opponent_file)
    states = indices_of_iterable_states()       ##remember this is a string and not int

    # actually the number of states are 8192+2
    num_states = 8194  # Modify as needed
    num_actions = 10  # Modify as needed
    print("numStates",num_states)
    print("numActions",num_actions)
    print("end 0 1")
    # Define the discount factor (gamma) based on your game
    discount_factor = 1 # Modify as needed
 
    # Generate transitions, rewards, and probabilities based on the game rules
    # key : s1 a s2 
    # state 0 is a terminal state:episode ends without scoring goal
    # state 1 is a terminal state:episode ends with scoring goal reward 1
    transitions={}
    for state in states:
        for action in range(num_actions):
             if action <= 7 and not(isPlayerInBound(state,action)):
                # player in bound
                # check for tackling case
                # probability of opposition player to go left,right,up,down
                left,right,up,down = opponent_policy[state]
                directions =[0,1,2,3]
                for direction in directions:
                  prob = 0
                  if direction == 0:
                      prob = left  # Left
                  elif direction == 1:
                      prob = right  # Right
                  elif direction == 2:
                      prob = up  # Up
                  else:
                      prob = down  # Down     
                #   print(isPlayerInBound(state,action))
                #   print(state)
                #   print(action)
                  if prob>0:
                    if tackling_case(state,action,direction):
                        next_State=nextState(state,action,direction)
                        # continues
                        trans_key =(state,action,next_State)
                        trans_val = 0, (0.5-p)*(prob)
                        # transitions[trans_key]=trans_val
                        updateDictionary(trans_key,transitions,trans_val)
                        printTransition(trans_key,transitions)
                         # episode ends
                        trans_key =(state,action,0)
                        trans_val = 0, (0.5+p)*(prob)
                        # transitions[trans_key]=trans_val
                        updateDictionary(trans_key,transitions,trans_val)
                        # printTransition(trans_key,transitions)
                    else:
                        next_State=nextState(state,action,direction)
                        factor =0 
                        # condition below is of player moving with ball
                        if 4*(state%10-1) <= action and action <4*(state%10):
                            factor=2
                        else:
                            factor = 1
                        # success in desire direction
                        trans_key =(state,action,next_State)
                        trans_val = 0, (1-p*factor)*(prob)
                        # transitions[trans_key]=trans_val
                        updateDictionary(trans_key,transitions,trans_val)
                        printTransition(trans_key,transitions)
                        
                         # possession lost episode ends
                        trans_key =(state,action,0)
                        trans_val = 0, (p*factor)*(prob)
                        # transitions[trans_key]=trans_val
                        updateDictionary(trans_key,transitions,trans_val)
                        # printTransition(trans_key, transitions)
                trans_key=(state,action,0)
                printTransition(trans_key,transitions)             

             elif action == 8:
                #  passing
                left,right,up,down = opponent_policy[state]
                directions =[0,1,2,3]
                for direction in directions:
                  prob = 0
                  if direction == 0:
                      prob = left  # Left
                  elif direction == 1:
                      prob = right  # Right
                  elif direction == 2:
                      prob = up  # Up
                  else:
                      prob = down  # Down     
                  
                  if (prob >0):
                      
                      factor =0 
                      if b_blocks(state,action,direction):
                          factor =0.5
                      else:
                          factor=1
                      next_State=nextState(state,action,direction)
                      trans_key =(state,action,next_State)
                      x1,y1,x2,y2,xr,yr = get_coordinates(state)
                    #   successful pass
                      trans_val = 0, prob*(q-0.1*max(abs(x1-x2),abs(y1-y2)))*factor
                      updateDictionary(trans_key,transitions,trans_val)
                      printTransition(trans_key, transitions)
     
                    # unsuccessful pass episode ends
                      trans_key=(state,action,0)
                      trans_val = 0, prob*(1-(q-0.1*max(abs(x1-x2),abs(y1-y2)))*factor)
                      updateDictionary(trans_key,transitions,trans_val)
                    #   printTransition(trans_key, transitions)
                trans_key=(state,action,0)
                printTransition(trans_key, transitions)
           
             elif action==9:
                left,right,up,down = opponent_policy[state]
                directions =[0,1,2,3]
                for direction in directions:
                  prob = 0
                  if direction == 0:
                      prob = left  # Left
                  elif direction == 1:
                      prob = right  # Right
                  elif direction == 2:
                      prob = up  # Up
                  else:
                      prob = down  # Down    
                  if prob > 0:
                    x1,y1,x2,y2,xr,yr = get_coordinates(state)
                    next_state= nextState(state,action,direction)
                    x1_f,y1_f,x2_f,y2_f,xr_f,yr_f = get_coordinates(next_state)
                    factor =1
                    if xr_f==3 and (yr_f==1 or yr_f==2):
                        factor=0.5
                    x=0
                    if state%10 ==1 :
                        x=x1
                    else:
                        x=x2
                    # goal happens
                    trans_key =(state,action,1)
                    trans_val = 1, (q-0.2*(3-x))*(prob)*(factor)
                    updateDictionary(trans_key,transitions,trans_val)
                    # printTransition(trans_key, transitions)
     
                    # episode ends
                    trans_key =(state,action,0)
                    trans_val = 0,prob*(1 -(q-0.2*(3-x))*(factor) )
                    updateDictionary(trans_key,transitions,trans_val)
                    # printTransition(trans_key, transitions)
                trans_key=(state,action,1)
                printTransition(trans_key, transitions)
                trans_key=(state,action,0)
                printTransition(trans_key, transitions)
    
    print("mdptype episodic")
    print("discount 1")
   





    # # Add other MDP information (e.g., terminal states, mdptype, discount factor)
    # terminal_states = [0, 99]  # Modify as needed
    # mdp_data.append(f"end {' '.join(map(str, terminal_states))}")
    # mdp_data.append("mdptype episodic")  # Modify if it's a continuing MDP
    # mdp_data.append(f"discount {discount_factor}")

    # return mdp_data

 

# def calculate_reward_and_probability(state, action, next_state, p, q, opponent_policy):
#     # Implement this function to calculate the reward and probability
#     # based on the game's rules, the player's parameters (p and q), and the opponent policy
#     # Return the reward and probability as needed
#     pass

# def main():
parser = argparse.ArgumentParser()
parser.add_argument("--opponent", required=True, help="Path to opponent policy file")
parser.add_argument("--p", type=float, default=0.1, help="Player parameter p")
parser.add_argument("--q", type=float, default=0.7, help="Player parameter q")
args = parser.parse_args()

# mdp_data = encode_game_to_mdp(args.opponent, args.p, args.q)
# print(args.opponent)
# print(args.p)
# print(args.q)
encode_game_to_mdp(args.opponent, args.p, args.q)

#     # Print the MDP data
#     for line in mdp_data:
#         print(line)

# if __name__ == "__main__":
#     main()
