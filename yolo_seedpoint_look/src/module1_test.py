#!/usr/bin/env python
# the line above is for launch file to read

from std_msgs.msg import String, Int16
import rospy
from time import sleep
import time

loop_count = 0
rospy.init_node('Module1_ROS')

def SeedFeeding():
    pub0 = rospy.Publisher('Mod1_cmd_SF', String, queue_size=1) # call arduino roll the seed
    time.sleep(0.3)
    pub0_command = "Feed"
    pub0.publish(pub0_command)
    print("Mod1 Feeding...")
    try:
        data0 = rospy.wait_for_message("/Ard_SF1", String, timeout=1) # timeout value base on the time need to feed one seed, if over this time then publish again
        length0 = len(data0.data)
        if length0 > 4:
            print("Mod1 Feeded\n")
            return 1
    except rospy.ROSException:
        pass

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Mod1_cmd_SR', Int16, queue_size=1) # call arduino roll the seed
    time.sleep(0.3)
    pub_command = 1
    pub.publish(pub_command)
    print("Mod1 Rolling...")

    try: 
        data1 = rospy.wait_for_message("/Ard_SR1", String, timeout=1) # timeout value base on the time need to roll the seed
        length1 = len(data1.data)
        if length1 > 4:
            print("Mod1 Rolled\n")
            time.sleep(0.3)
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Mod1_cmd_SP', String, queue_size=1) # seed position is right, call arduino plant it
    pub2_command = "Plant"
    pub2.publish(pub2_command)
    print("Planting...")

    try:
        data2 = rospy.wait_for_message("/Ard_Plant", String, timeout=1) # timeout value base on the time need to plant one seed
        length2 = len(data2.data)
        if length2 > 4:
            print("Seed Planted\n")
            # exit()
            return 1
    except rospy.ROSException:
        pass

def main(stat):
    
    try: 
        seed_sub = rospy.wait_for_message("Mod1_yoloseed", Int16) # timeout value base on the time need to roll the seed
        seedpoint_sub = rospy.wait_for_message("Mod1_yoloseedpoint", Int16) # timeout value base on the time need to roll the seed
    except rospy.ROSException:
        print("Camera not open yet!")
        exit()
    
    seed_stats = seed_sub.data
    roll_cmd = seedpoint_sub.data

    # feed_stats, cmd = yolo_detect(yolo_input) # feed_stats = 1 means found seed, the seed drop successfully on fanzhuan
                                                # this  function is also use to proceed the cmd to decide whether roll or plant the seed
    if seed_stats == 1: # or seed_temp == 1:
        while True:
            seedpoint_sub = rospy.wait_for_message("Mod1_yoloseedpoint", Int16) # timeout value base on the time need to roll the seed
            roll_cmd = seedpoint_sub.data
            if roll_cmd == 1:                # if detected seed point
                print("芽點朝上")
                while True:             
                        roll_stats = SeedRoll()  # roll the seed
                        if roll_stats == 1:      # if seed roll done then break
                            break

            elif roll_cmd == 0:
                print("芽點朝下")
                while True:
                    plant_stats = SeedPlanting() # plant the seed
                    if plant_stats == 1:         # if plant done then break
                        # print("############ END ############\n")
                        exit()
                        break
                seed_temp = 0
                exit()
        # time.sleep(3)

    elif seed_stats == 0: 
        print("NO SEED")
        while True:             
            feed_stats = SeedFeeding()  # feed the seed
            if feed_stats == 1:      # if seed feeded then break
                break # break seedfeeding publish loop

def wait_for_Init():
    while True:
        try:
            print("System Initializing\n")
            data3 = rospy.wait_for_message("/Ard_Init", String, timeout=5) # timeout value base on the time need to plant one seed
            length3 = len(data3.data)
            if length3 > 4:
                print("System Init-ed\n")
                # exit()
                return 1
        except rospy.ROSException:
            pass


wait_for_Init() # only do once, which is wait for arduino initialized the system
try:
    while True:
        loop_count = loop_count + 1
        main(loop_count)
        # print(loop_count)

except KeyboardInterrupt:
    exit()