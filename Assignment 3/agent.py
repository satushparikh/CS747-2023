import os
import sys
import random 
import json
import math
import utils
import time
import config
import numpy as np
random.seed(73)
# random.seed(63)

class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()
        self.ball_coordinates = {}

    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        self.ball_radius = radius

    def point_distance(self,p1, p2):
        # dist_diff = p1 - p2
        # return np.hypot(*dist_diff)
        x_diff = p1[0] - p2[0]
        y_diff = p1[1] - p2[1]
        dist_diff = math.sqrt(x_diff**2 + y_diff**2)
        return dist_diff
# finds euclidean distance in norm 2
    def hole_to_target(self,key):
        x_w, y_w = self.ball_coordinates[0]
        x_b, y_b = self.ball_coordinates[key]
        # Calculate the angle in radians
        # theta1 is the angle between the targeted ball and the cue ball
        theta1 = math.atan2(y_b - y_w, x_b - x_w)
                # Iterate through the holes and compare angles  
        results = []
        # finding the angle(theta2) between the targeted ball and the hole
        # if theta2 and theta1 are in the same quadrant then the ball can be potted
        atleast_one_valid = False
        for hole_x,hole_y in self.holes:
            x_hole, y_hole = hole_x, hole_y
            theta2 = math.atan2(y_hole - y_b, x_hole - x_b)
            sameQuadrant = False
            # Now check if theta2 and theta1 are in the same quadrant
            first_quadrant = (0 <= theta1 <= math.pi/2 and 0 <= theta2 <= math.pi/2)
            second_quadrant = (math.pi/2 <= theta1 <= math.pi and math.pi/2 <= theta2 <= math.pi)
            third_quadrant = (-math.pi <= theta1 <= -math.pi/2 and -math.pi <= theta2 <= -math.pi/2)
            fourth_quadrant = (-math.pi/2 <= theta1 <= 0 and -math.pi/2 <= theta2 <= 0)
            if first_quadrant or second_quadrant or third_quadrant or fourth_quadrant:
                sameQuadrant= True
                atleast_one_valid=True
            # finding distance from white ball to targeted ball
                d_w_b = self.point_distance(self.ball_coordinates[0],self.ball_coordinates[key])
            # finding distance from targeted ball to hole
            # d_b_h = self.point_distance(self.ball_coordinates[key],hole_coordinates)
            # finding angle at which the cue ball should be hit
                alpha = math.atan2(d_w_b * math.sin(theta1) - 2 * self.ball_radius * math.sin(theta2), d_w_b * math.cos(theta1) - 2 * self.ball_radius * math.cos(theta2))
            # find distance between targeted ball and hole
                hole_coordinates = np.array([x_hole,y_hole])
                d_b_h = self.point_distance(self.ball_coordinates[key],hole_coordinates)
            # append the results
                results.append((alpha,d_w_b,d_b_h,theta2))
            # print(f"alpha: {alpha:.3f} cos {math.cos(alpha):.3f}   ")
            else :
                continue
        # if results list is return some default values
        if not results:
            return 0,1000,1000
        else:
            max_cos_alpha_tupple=max(results,key=lambda x: math.cos(x[0]))
            # alpha1=max_cos_alpha_tupple[0]
            # print(f"alpha: {alpha1:.3f} cos {math.cos(alpha1):.3f}   ")
            return max_cos_alpha_tupple

    def billiardAngle(self,angle):
#  if angle in first quadrant change it to -pi/2-theta
        if 0 <= angle <= math.pi/2:
            angle = -math.pi/2 - angle  
# if angle in second quadrant change it to 3*pi/2-theta
        elif math.pi/2 <= angle <= math.pi:
            angle = 3*math.pi/2 - angle
# if angle in third quadrant change it to -pi/2-theta
        elif -math.pi <= angle <= -math.pi/2:
            angle = -math.pi/2 - angle
# if angle in fourth quadrant change it to -pi/2-theta
        elif -math.pi/2 <= angle <= 0:
            angle = -math.pi/2 - angle
# else raise error exception
        else:
            raise Exception("angle is not in the range [-pi,pi]")
        return angle
    def action(self, ball_pos=None):
        ## Code you agent here ##
        # call hole_to_targer function for all the balls which are not potted
        # find the ball which has the maximum cos(alpha) value
        # first storing the holes coordinates in the dictionary
 
        #  for key, value in ball_pos.items():
        #     key_data_type = type(key)
        #     value_data_type = type(value)
        #     print(f"Key: {key} (Data Type: {key_data_type}), Value: {value} (Data Type: {value_data_type})")
        self.ball_coordinates = {}
        if ball_pos is not None:
            for key, value in ball_pos.items():
                self.ball_coordinates[key] = value
                # print(f"Storing key: {key}, Value: {value} in self.balls_coordinates")

        else:
            raise Exception("ball_pos is None. You should provide valid ball positions.")
        # now we have stored the positions of the ball when they are at rest
        # we will now find the ball which has the maximum cos(alpha) value
        compare_with =-1 
        target_ball =  0
        d_w_b_max = 0
        d_b_h_max = 0
        angle_for_hitting_cue=0
        for key in self.ball_coordinates.keys():
            if key == 0 or key == "white":   
                continue    
            alpha,d_w_b,d_b_h,theta2 = self.hole_to_target(key)
            cos_alpha_theta2 = math.cos(alpha-theta2)
            total_distance = d_w_b + d_b_h
            # print(f"cos alpha: {cos_alpha}   d_w_b: {d_w_b}   d_b_h: {d_b_h}   d_w_b + d_b_h: {total_distance}")
            # print(f"Ball: {key}  alpha:{alpha:.3f} ")
            # print(f"cos: {cos_alpha_theta2:.3f}   d_w_b: {d_w_b:.3f}   d_b_h: {d_b_h:.3f}   sum: {total_distance:.3f}")
            # print(f"DIFF: {alpha-theta2:.3f}   d_w_b: {d_w_b:.3f}   d_b_h: {d_b_h:.3f}   sum: {total_distance:.3f}")
            # condition of hitting nearer ball
            if cos_alpha_theta2>0.8 and d_b_h <100:
            # if cos_alpha_theta2>0.8 and d_b_h <160:
                compare_with=cos_alpha_theta2
                angle_for_hitting_cue=alpha
                # print(f"Alpha (Radians): {alpha:.3f}, Alpha (Degrees): {math.degrees(alpha):.3f}, cos(alpha): {math.cos(alpha):.3f}")  
                diff = alpha-theta2 
                # print(f"diff (Radians): {diff:.3f}, diff (Degrees): {math.degrees(diff):.3f}, cos(diff): {math.cos(diff):.3f}")   
                target_ball=key
                d_w_b_max=d_w_b
                d_b_h_max=d_b_h
                break
            if cos_alpha_theta2>compare_with:
                compare_with=cos_alpha_theta2
                angle_for_hitting_cue=alpha
                
                # print(f"Alpha (Radians): {alpha:.3f}, Alpha (Degrees): {math.degrees(alpha):.3f}, cos(alpha): {math.cos(alpha):.3f}")  
                diff = alpha-theta2 
                # print(f"diff (Radians): {diff:.3f}, diff (Degrees): {math.degrees(diff):.3f}, cos(diff): {math.cos(diff):.3f}")   
                target_ball=key
                d_w_b_max=d_w_b
                d_b_h_max=d_b_h
        # print(f"Checking over")
        # now we have the ball which has the maximum cos(alpha) value
        # angle returned was by atan2, we are given a differnt coordinate convention
        normalised_Angle = self.billiardAngle(angle_for_hitting_cue)/math.pi
        # raise force to the 1/3 power of (d_w_b_max|d_b_h_max)/1011
        force = ((d_w_b_max+d_b_h_max)/1011)**(1.2/1)
        # print("Target Ball:", target_ball)
        # print("Normalised Angle:", normalised_Angle)
        # print("Force:", force)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        # self.ns.get_next_state(ball_pos,(0,0),73)
        return normalised_Angle,max(min(force,0.75),0.32)
        # return normalised_Angle,max(min(force,0.85),0.3)
"""         self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        self.ns.get_next_state(ball_pos,(0,0),73)
        return (-0.52,0.55) """

        ## You can access data from config.py for geometry of the table, configuration of the levels, etc.
        ## You are NOT allowed to change the variables of config.py (we will fetch variables from a different file during evaluation)
        ## Do not use any library other than those that are already imported.
        # : The action()function has to return a tuple of normalised angle
# and force (angle in range [-1,1], force in range [0, 1])
        # return (2*random.random() - 1, random.random())
