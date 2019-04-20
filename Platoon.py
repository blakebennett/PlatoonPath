#!/usr/bin/env python

#***************************************************************************************************************
#
#   Blake Bennett
#   Path Traversal Optimization
#   19 APR 2019
#
#***************************************************************************************************************

#*** DEPENDENCIES **********************************************************************************************

import math
import random

#*** PLATOON CLASSS ********************************************************************************************

#Platoon has added battery-related variables to try to introduce more realism
class Platoon:
    def __init__(self, sensor_range, sensor_reliability, detection_limit, detected_limit, sensor_battery_drain, passive_battery_drain, battery_capacity):
        self.sensor_range = sensor_range
        self.sensor_reliability = sensor_reliability
        self.detection = [False, 0]
        self.detection_limit = detection_limit
        
        self.detected = [False, 0]
        self.detected_limit = detected_limit
        self.lost_command_flag = False
        
        self.sensor_battery_drain = sensor_battery_drain
        self.passive_battery_drain = passive_battery_drain
        self.battery_capacity = battery_capacity
        self.dead_battery_flag = False
        
        self.position = [0, 0]
        
    #Battery drain due to time and detections    
    def battery_drain(self):
        self.battery_capacity = self.battery_capacity - self.passive_battery_drain
        if (self.detection[0] == True):
            self.battery_capacity = self.battery_capacity - (self.detection[1] * self.sensor_battery_drain)
        if (self.battery_capacity <= 0):
            self.dead_battery_flag = True
            
    #Consequences for being detected
    def detected_by_R2D2(self):
        if (self.detected[0] == True):
            self.detected_limit = self.detected_limit - (self.detected[1])
        if (self.detected_limit <= 0):
            self.lost_command_flag == True            

#R2D2s have a range of 5
class R2D2:
    def __init__(self, x_position, y_position):
        self.detection_range = 5
        self.x_position = x_position
        self.y_position = y_position

#Battlespace must be at least 2000x2000 (bound variables extend their value in the positive and negative direction...
# 1000, 1000 will create a 2000x2000 battlespace
class Battlespace:
    def __init__(self, x_bound, y_bound, num_R2D2):
        self.x_bound = x_bound
        if (x_bound < 1000):
            self.x_bound = 1000
        
        self.y_bound = y_bound
        if (y_bound < 1000):
            self.y_bound = 1000
            
        self.num_R2D2 = num_R2D2
        self.R2D2_list = []
        
    #Check if R2D2 position is invalid    
    def invalid_pos(self, x_pos, y_pos):
        if((abs(x_pos) + abs(y_pos)) <= 5):
            return False
        if(x_pos < 995 and x_pos > 1005 and y_pos < 995 and y_pos > 1005 and (abs(x_pos - y_pos) <= 5)): #check if R2D2 is on the safe zone
               return False
        for i in range(0, len(self.R2D2_list)):
            if (self.R2D2_list[i].x_position == x_pos and self.R2D2_list[i].y_position == y_pos):
                return False
        return True
    
    #Spawn the R2D2s
    def spawn_R2D2s(self):
        for i in range(0, self.num_R2D2):
            good_pos = False
            while(good_pos == False):
                x_pos = (int(random.random() * self.x_bound * 2) + (-1 * self.x_bound)) #selecting a random x position (from -x_bound to +x_bound) by finding a random number between 0 and x_bound*2 and adding it to the lower bound
                y_pos = (int(random.random() * self.y_bound * 2) + (-1 * self.y_bound)) #selecting a random y position (from -y_bound to +y_bound) by finding a random number between 0 and y_bound*2 and adding it to the lower bound
                good_pos = self.invalid_pos(x_pos, y_pos)     
            R2 = R2D2(x_pos, y_pos)
            self.R2D2_list.append(R2)


class Simulation:
    def __init__(self):
        self.battlespace = Battlespace(2000, 2000, 1000)
        self.platoon = Platoon(6, .90, 50, 30, 10, 1, 5000)
        self.baseline_platoon = self.platoon
        self.platoon_safe = False
        self.path = []
        self.fitness = 0
        self.following = False
        
        self.best_path = []
        
    #Generic movement that includes some randomness to *hopefully* introduce different paths and the potential to find more optimized paths    
    def random_move(self):
        prob_go_NS = float(abs(float(1000 - self.platoon.position[1])) / (float(abs(1000 - self.platoon.position[0]) + abs(1000 - self.platoon.position[1]))))
        prob_go_EW = float(abs(float(1000 - self.platoon.position[0])) / (float(abs(1000 - self.platoon.position[0]) + abs(1000 - self.platoon.position[1]))))
        if (random.random() > prob_go_NS):
            if (self.platoon.position[0] <= 1000):
                if(random.random() < 0.95):
                    self.platoon.position[0] = self.platoon.position[0] + 1
                    self.path.append("E")
                else:
                    self.platoon.position[0] = self.platoon.position[0] - 1
                    self.path.append("W")
            else:
                if(random.random() < 0.95):
                    self.platoon.position[0] = self.platoon.position[0] - 1
                    self.path.append("W")
                else:
                    self.platoon.position[0] = self.platoon.position[0] + 1
                    self.path.append("E")
        else:
            if (self.platoon.position[1] <= 1000):
                if(random.random() < 0.95):
                    self.platoon.position[1] = self.platoon.position[1] + 1
                    self.path.append("N")
                else:
                    self.platoon.position[1] = self.platoon.position[1] - 1
                    self.path.append("S")
            else:
                if(random.random() < 0.95):
                    self.platoon.position[1] = self.platoon.position[1] - 1
                    self.path.append("S")
                else:
                    self.platoon.position[1] = self.platoon.position[1] + 1
                    self.path.append("N")
                    
    #Fitness function (This could make or break the optimization of the path, and could probably use tweaking)
    def evaluate_fitness(self):
        fitness = 0
        fitness = fitness + float((2000.00 / float(len(self.path))))
        fitness = float(fitness + self.platoon.battery_capacity / 5000)#self.baseline_platoon.battery_capacity)
        fitness = float(fitness + self.platoon.detection_limit / 50)#self.baseline_platoon.detection_limit)
        fitness = float(fitness + self.platoon.detected_limit / 30)#self.baseline_platoon.detected_limit)
        fitness = float(fitness / 4)
        self.following = True
        print("path length = " +str(len(self.path)) +"      fitness:  " + str(fitness))
        return fitness
    
    
    #This function makes the platoon follow the best platoon's path as long as this function is used 
    def follow_best_path(self, time_tick):
        if (self.best_path[time_tick] == "N"):
            self.platoon.position[1] = self.platoon.position[1] + 1
            self.path.append("N")
        if (self.best_path[time_tick] == "S"):
            self.platoon.position[1] = self.platoon.position[1] -1
            self.path.append("S")
        if (self.best_path[time_tick] == "E"):
            self.platoon.position[0] = self.platoon.position[0] + 1
            self.path.append("E")
        else:
            self.platoon.position[0] = self.platoon.position[0] - 1
            self.path.append("W")
  
    #This function is used to move away from a detected R2D2 by moving out and away based on location in relation to the detected R2D2
    def move(self, direction1, steps1, direction2, steps2, time_tick):
        while(steps1 > 0 and steps2 > 0):
            if(steps1 > 0):
                steps1 = steps1-1
                if(direction1 =="N"):
                    self.platoon.position[1] = self.platoon.position[1] + 1
                    self.path.append("N")
                    time_tick = time_tick + 1
                if(direction1 == "S"):
                    self.platoon.position[1] = self.platoon.position[1] - 1
                    self.path.append("S")
                    time_tick = time_tick + 1
                if(direction1 =="E"):
                    self.platoon.position[0] = self.platoon.position[0] + 1
                    self.path.append("E")
                    time_tick = time_tick + 1
                else:
                    self.platoon.position[0] = self.platoon.position[0] - 1
                    self.path.append("W")
                    time_tick = time_tick + 1
            if(steps2 > 0):
                steps2 = steps2-1
                if(direction2 =="N"):
                    self.platoon.position[1] = self.platoon.position[1] + 1
                    self.path.append("N")
                    time_tick = time_tick + 1
                if(direction2 == "S"):
                    self.platoon.position[1] = self.platoon.position[1] - 1
                    self.path.append("S")
                    time_tick = time_tick + 1
                if(direction2 =="E"):
                    self.platoon.position[0] = self.platoon.position[0] + 1
                    self.path.append("E")
                    time_tick = time_tick + 1
                else:
                    self.platoon.position[0] = self.platoon.position[0] - 1
                    self.path.append("W")
                    time_tick = time_tick + 1
        return (time_tick -1)
    
    
    def start(self):
        
        #spawn the R2D2s within the battlespace
        self.battlespace.spawn_R2D2s()
        
        #maximum of 255 generations of platoons
        for generation in range(0, 256):
            #reset platoon
            self.platoon = Platoon(6, .90, 50, 30, 10, 1, 5000)
            
            time_tick = 0
            self.platoon_safe = False
            while(self.platoon_safe == False): 
                self.platoon.detected[0] = False
                self.platoon.detected[1] = 0
                
                #check if R2D2 detects platoon
                for i in range(0, self.battlespace.num_R2D2):
                    if ((abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[0]) + abs(self.battlespace.R2D2_list[i].y_position - self.platoon.position[1])) <= self.platoon.sensor_range):
                        self.platoon.detected[0] = True
                        self.platoon.detected[1] = self.platoon.detected[1] + 1
                self.platoon.detected_by_R2D2()
                
                #follow best path based on fitness value as percentage (currently platoons do not follow for very long
                #... this could use some refining to produce long following distances and prbably improving optimization. See evaluate_fitness()
                if (self.fitness > 0 and self.following == True and (len(self.best_path) > time_tick)):
                    
                    if(random.random() < self.fitness):
                        self.follow_best_path(time_tick)
                    else:
                        self.following = False
                        self.random_move()
                else:
                    self.following = False
                    found_R2D2 = False
                    
                    #check all R2D2s for potential detection
                    for i in range(0, self.battlespace.num_R2D2):
                        
                        #check if platoon detects R2D2 
                        if ((abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[0]) + abs(self.battlespace.R2D2_list[i].y_position - self.platoon.position[1])) <= self.platoon.sensor_range and random.random < self.platoon.sensor_reliability):
                            
                            found_R2D2 = True
                            self.platoon.detection[0] = True
                            self.platoon.detection[1] = 1
                            
                            #if detected and platoon detects R2D2 attempt to find closest way out of R2D2's range
                            if((abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[0]) + abs(self.battlespace.R2D2_list[i].y_position - self.platoon.position[1])) <= 5):
                                if(abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[0]) < abs(self.battlespace.R2D2_list[i].y_position - self.platoon.position[1])):
                                    if(self.battlespace.R2D2_list[i].x_position > self.platoon.position[0]):
                                        time_tick = move("W", self.battlespace.R2D2_list[i].x_position - self.platoon.position[0], "W", 0)
                                    else:
                                        time_tick = move("E", abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[0]), "E", 0)
                                else:
                                    if(self.battlespace.R2D2_list[i].y_position > self.platoon.position[1]):
                                        time_tick = move("S", self.battlespace.R2D2_list[i].x_position - self.platoon.position[1], "S", 0)
                                    else:
                                        time_tick = move("N", abs(self.battlespace.R2D2_list[i].x_position - self.platoon.position[1]), "N", 0)
                                
                            #Check whether safe zone is northest, northeast, southwest, or southeast of the R2D2
                            if( self.battlespace.R2D2_list[i].x_position < 1000):
                                if(self.battlespace.R2D2_list[i].y_position < 1000):
                                    target_quad = 1
                                else:
                                    target_quad = 4
                            else:
                                if(self.battlespace.R2D2_list[i].y_position < 1000):
                                    target_quad = 2
                                else:
                                    target_quad = 3
                            #check where the platoon is in relation to the R2D2 and move to an appropriate position to be better poised to move toward the safe zone
                            if( self.battlespace.R2D2_list[i].x_position < self.platoon.position[0]):
                                if ( self.battlespace.R2D2_list[i].y_position < self.platoon.position[1]):
                                    platoon_quad = 1
                                    if(platoon_quad == target_quad):
                                        self.random_move()
                                    if(target_quad == 4):
                                        time_tick = self.move("E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "S", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    if(target_quad == 2):
                                        time_tick = self.move("N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    else:
                                        time_tick = self.move("N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                                
                                else:
                                    platoon_quad = 4
                                    if(platoon_quad == target_quad):
                                        self.random_move()
                                    if(target_quad == 1):
                                        time_tick = self.move("E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    if(target_quad == 2):
                                        time_tick = self.move("E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    else:
                                        time_tick = self.move("S", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                            else:
                                if( self.battlespace.R2D2_list[i].y_position < self.platoon.position[1]):
                                    platoon_quad = 2
                                    if(platoon_quad == target_quad):
                                        self.random_move()
                                    if(target_quad == 4):
                                        time_tick = self.move("N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    if(target_quad == 3):
                                        time_tick = self.move("W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "S", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    else:
                                        time_tick = self.move("N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                else:
                                    platoon_quad = 3
                                    if(platoon_quad == target_quad):
                                        self.random_move()
                                    if(target_quad == 4):
                                        time_tick = self.move("S", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "E", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    if(target_quad == 2):
                                        time_tick = self.move("W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                                    else:
                                        time_tick = self.move("W", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position), "N", (abs(self.platoon.position[0] - self.battlespace.R2D2_list[i].x_position))), time_tick)
                            i = self.battlespace.num_R2D2
                    #if no R2D2 is detected, move as normal
                    if (found_R2D2 == False):   
                        self.random_move()
            
            
                
                #finish if platoon reaches the safe zone
                if(self.platoon.position == [1000,1000]):
                    
                    if (self.evaluate_fitness() > self.fitness):
                        self.best_path = self.path
                        self.fitness = self.evaluate_fitness()
                      
                    self.path = []
                    self.platoon_safe = True
                    break
                    
                    
                #drain battery and reset detection
                self.platoon.battery_drain()
                self.platoon.detection[0] = False
                self.platoon.detection[1] = 0
                
                #finish if battery is dead
                if(self.platoon.dead_battery_flag == True):
                    print("Battery Dead: Stay where you are")
                    self.platoon_safe = True
                    self.path = []
                    break
                
                #finish if platoon was detected too many times
                if(self.platoon.lost_command_flag == True):
                    print("You have been detected too many times. Command lost. Try again")
                    self.platoon_safe = True
                    self.path = []
                    break
                #increase time tick
                time_tick = time_tick + 1   
        
        platoon_file = "platoon_file.csv"
        file = open(platoon_file, "a+")
        for i in range(0, len(self.best_path)):
            file.write(str(self.best_path[i]) + "\n")
        print("Best Fitness Value: " + str(self.fitness))
        print("Best Path Length:   " + str(len(self.best_path)))
              
        
if __name__=="__main__":
    #run simulation
    sim = Simulation()
    sim.start()