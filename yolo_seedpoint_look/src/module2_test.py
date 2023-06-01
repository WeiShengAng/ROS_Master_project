#module 2 ros arduino test

from std_msgs.msg import String, Int16
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time

cam_port = 4
cam = cv.VideoCapture(cam_port)

loop_count = 0
feed_stats = 2
#define a node then publish topic 'chatter' and also can subscribe topic
rospy.init_node('Module2_ROS')

def SeedFeeding():
    pub0 = rospy.Publisher('Mod2_cmd_SF', String, queue_size=5) # call arduino roll the seed
    time.sleep(0.3)
    pub0_command = "Feed"
    pub0.publish(pub0_command)
    print("Mod2 Feeding...")
    try:
        data0 = rospy.wait_for_message("/Ard_SF2", String, timeout = 5) # timeout value base on the time need to feed one seed, if over this time then publish again
        length0 = len(data0.data)
        if length0 > 4:
            print("Mod2 Feeded\n")
            return 1
    except rospy.ROSException:
        pass

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Mod2_cmd_SR', String, queue_size=5) # call arduino roll the seed
    time.sleep(0.3)
    pub_command = "Roll"
    pub.publish(pub_command)
    print("Mod2 Rolling...")

    try: 
        data1 = rospy.wait_for_message("/Ard_SR2", String, timeout=5) # timeout value base on the time need to roll the seed
        length1 = len(data1.data)
        if length1 > 4:
            print("Mod2 Rolled\n")
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Mod2_cmd_SP', String, queue_size=5) # seed position is right, call arduino plant it
    time.sleep(0.3)
    pub2_command = "Plant"
    pub2.publish(pub2_command)
    print("Planting...")

    try:
        data2 = rospy.wait_for_message("/Ard_Plant", String, timeout=60) # timeout value base on the time need to plant one seed
        length2 = len(data2.data)
        if length2 > 4:
            print("Seed Planted\n")
            # exit()
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()



def main(stat):
    # while True:
    #     feed_stats = SeedFeeding()
    #     if feed_stats == 1:
    #         break
    
    # while True: # yolo detect while loop
        
    '''
    # to use diff picture as example, change this whole section to camera when in real usage #
    if stat == 1:
        print("############ START ############\n")
        feed_stats, cmd = 0,0
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    elif stat == 2:    
        feed_stats, cmd = 1,1
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    elif stat == 3:
        feed_stats, cmd = 1,0
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    '''

    try: 
        seed_sub = rospy.wait_for_message("Mod2_yoloseed", Int16) # timeout value base on the time need to roll the seed
        seedpoint_sub = rospy.wait_for_message("Mod2_yoloseedpoint", Int16) # timeout value base on the time need to roll the seed
    except rospy.ROSException:
        print("Camera not open yet!")
        exit()

    seed_stats = seed_sub.data
    roll_cmd = seedpoint_sub.data
    
    # feed_stats, cmd = yolo_detect(yolo_input) # feed_stats = 1 means found seed, the seed drop successfully on fanzhuan
                                                # this  function is also use to proceed the cmd to decide whether roll or plant the seed
    if seed_stats == 0: 
        print("NO SEED")
        # while True:             
        #     feed_stats = SeedFeeding()  # feed the seed
        #     if feed_stats == 1:      # if seed feeded then break
        #         break # break seedfeeding publish loop
    elif seed_stats == 1: 

        if roll_cmd == 1:                # if detected seed point
            print("芽點朝上")
            # while True:             
            #         roll_stats = SeedRoll()  # roll the seed
            #         if roll_stats == 1:      # if seed roll done then break
            #             break

        elif roll_cmd == 0:
            print("芽點朝下")
            # while True:
            #     plant_stats = SeedPlanting() # plant the seed
            #     if plant_stats == 1:         # if plant done then break
            #         print("############ END ############\n")
            #         exit()
            #         break
    time.sleep(3)

try:
    while True:
        loop_count = loop_count + 1
        main(loop_count)
        # print(loop_count)

except KeyboardInterrupt:
    pass