import os
import sys 
import matplotlib.pyplot as plt

if __name__ == "__main__":
    p = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    q = 0.7
    q2 = [0.6, 0.7, 0.8, 0.9, 1]
    p2 = 0.3
    val1 = []
    val2 = []
    for i in p:
            command = "python3 encoder.py --opponent data/football/test-1.txt --p "  +(str)(i) + " --q " + (str)(q) + " > football_mdp.txt" 
            os.system(command)
            command2 = "python3 planner.py --mdp football_mdp.txt > value.txt"
            os.system(command2)
            command3 = "python3 decoder.py --value-policy value.txt --opponent data/football/test-1.txt > policyfile.txt"
            os.system(command3)
            with open('policyfile.txt', 'r') as file:  
                for line in file:
                    words = line.split()
                    if words[0] == "0509081":
                        val1.append((float)(words[2]))
                        break
    for i in q2:
            command = "python3 encoder.py --opponent data/football/test-1.txt --p "  +(str)(p2) + " --q " + (str)(i) + " > football_mdp.txt" 
            os.system(command)
            command2 = "python3 planner.py --mdp football_mdp.txt > value.txt"
            os.system(command2)
            command3 = "python3 decoder.py --value-policy value.txt --opponent data/football/test-1.txt > policyfile.txt"
            os.system(command3)
            with open('policyfile.txt', 'r') as file:  
                for line in file:
                    words = line.split()
                    if words[0] == "0509081":
                        val2.append((float)(words[2]))
                        break
    plt.plot(p, val1, marker='o', linestyle='-')

# Add labels and a title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Goal Scoring vs p')

# Display the plot
    plt.savefig("Firstplot.png")
    plt.clf()
    plt.plot(q2, val2, marker='o', linestyle='-')

# Add labels and a title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Goal Scoring vs q')

# Display the plot
    
    plt.savefig("Secondplot.png")
    print(val1)
    print(val2)
    
    
            
                              
            
     