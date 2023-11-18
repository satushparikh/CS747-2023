import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--value-policy",type=str,default="/")
parser.add_argument("--opponent",type=str,default="/")

args = parser.parse_args()

opponent_file = args.opponent
value_file = args.value_policy
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
def decode_game_position(encoded_value):
    # Calculate the values
    ball_possession = (encoded_value // (16**3)) + 1
    encoded_value %= (16**3)

    R_square = (encoded_value // (16**2)) + 1
    encoded_value %= (16**2)

    B2_square = (encoded_value // 16) + 1
    B1_square = (encoded_value % 16) + 1

    # Format the values with leading zeros if necessary
    B1_square_str = str(B1_square).zfill(2)
    B2_square_str = str(B2_square).zfill(2)
    R_square_str = str(R_square).zfill(2)

    # Create the original string format
    original_string = B1_square_str + B2_square_str + R_square_str + str(ball_possession)

    return original_string

def read_value_policy_file(file_path):
    value_policy = {}
    with open(file_path, 'r') as file:
        i=0
        for line in  file:
            line = line.strip().split()
            value = float(line[0])
            action=int(line[1])
            value_policy[i]=(value,action)
            i+=1
    return value_policy

value_policy = read_value_policy_file(value_file)

with open(opponent_file, 'r') as file:
    # Skip the header line if there is one
    next(file)
    for line in file:
        msg = line.strip().split()[0]
        state = str(msg)
        num = encode_game_position(state)+2

        if num in value_policy:
            (value, action) = value_policy[num]
            # Print the line value action
            print(f"{msg} {action} {value}")
        else:
            print(f"Invalid input format: {msg}")


def decode_game_position(encoded_value):
    # Calculate the values
    ball_possession = encoded_value // (16**3)
    encoded_value %= (16**3)

    R_square = encoded_value // (16**2)
    encoded_value %= (16**2)

    B2_square = encoded_value // 16
    B1_square = encoded_value % 16

    # Format the values with leading zeros if necessary
    B1_square_str = str(B1_square).zfill(2)
    B2_square_str = str(B2_square).zfill(2)
    R_square_str = str(R_square).zfill(2)

    # Create the original string format
    original_string = B1_square_str + B2_square_str + R_square_str + str(ball_possession)

    return original_string
 