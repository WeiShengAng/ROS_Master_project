#!/usr/bin/env python
#module 2 ros arduino test

from std_msgs.msg import String, Int16
import rospy
from time import sleep
import time


loop_count = 0
#define a node then publish topic 'chatter' and also can subscribe topic
rospy.init_node('Module2_ROS')

def SeedFeeding():
    pub0 = rospy.Publisher('Mod2_cmd_SF', String, queue_size=1) # call arduino roll the seed
    # time.sleep(0.3)
    pub0_command = "Feed"
    pub0.publish(pub0_command)
    print("Mod2 Feeding...")
    try:
        data0 = rospy.wait_for_message("/Ard_SF2", String, timeout=1) # timeout value base on the time need to feed one seed, if over this time then publish again
        length0 = len(data0.data)
        if length0 > 4:
            print("Mod2 Feeded\n")
            time.sleep(1.0)
            return 1
    except rospy.ROSException:
        pass

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Mod2_cmd_SR', String, queue_size=1) # call arduino roll the seed
    pub_command = "Roll"
    pub.publish(pub_command)
    print("Mod2 Rolling...")

    try: 
        data1 = rospy.wait_for_message("/Ard_SR2", String, timeout=0.5) # timeout value base on the time need to roll the seed
        length1 = len(data1.data)
        if length1 > 4:
            print("Mod2 Rolled\n")
            time.sleep(1.5)
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Mod2_cmd_SP', String, queue_size=1) # seed position is right, call arduino plant it
    time.sleep(0.3)
    pub2_command = "Plant"
    pub2.publish(pub2_command)
    print("Planting2")

    try:
        recv_msg = rospy.wait_for_message("/Ard_Recv", Int16, timeout=0.2) # timeout value base on the time need to plant one seed
        recv = recv_msg.data
    except rospy.ROSException:
        recv = 0
        pass

    if recv == 1:
        print("msg recv 2")
        while True:
            try:
                print("while 2")
                data2 = rospy.wait_for_message("/Ard_Plant", Int16, timeout=1) # timeout value base on the time need to plant one seed
                ard_resp = data2.data
                if ard_resp > 4:
                    end = rospy.get_rostime()
                    rospy.loginfo("2_End %i", end.secs)
                    print("Seed Planted\n")
                    # exit()
                    recv = 0
                    return 1
                else:
                    pass
            except rospy.ROSException:
                pass
    
    # --- problem ---#
    # this structure will have problem because 
    # (i) recv is unbounded 
    # (ii) /Ard_Plant return ROSExcept type error when arduino didnt pub, so it exit the while loop
    # --- problem ---#
    
    # try:
    #     recv_msg = rospy.wait_for_message("/Ard_Recv", Int16, timeout=0.2) # timeout value base on the time need to plant one seed
    #     recv = recv_msg.data
    #     print("msg recv 2")
    #     if recv == 1:
    #         print("here2")
    #         while True:
    #             print("while 2")
    #             data2 = rospy.wait_for_message("/Ard_Plant", Int16, timeout=1) # timeout value base on the time need to plant one seed
    #             ard_resp = data2.data
    #             if ard_resp > 4:
    #                 end = rospy.get_rostime()
    #                 rospy.loginfo("End time %i", end.secs)
    #                 print("Seed Planted\n")
    #                 # exit()
    #                 return 1
    #             else:
    #                 pass
    # except rospy.ROSException:
    #     pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()



def main(stat):

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
    if seed_stats == 1: # or seed_temp == 1: 
        _run = True
        while _run:
            seedpoint_sub = rospy.wait_for_message("Mod2_yoloseedpoint", Int16) # timeout value base on the time need to roll the seed
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
                        print("############ END ############\n")
                        _run = False
                        break
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
                time.sleep(1.5)
                # exit()
                return 1
        except rospy.ROSException:
            # exit()
            pass

wait_for_Init() # only do once, which is wait for arduino initialized the system
try:
    print("############ START ############\n")
    now = rospy.get_rostime()
    rospy.loginfo("Start time %i", now.secs)
    while True:
        loop_count = loop_count + 1
        main(loop_count)
        # print(loop_count)

except KeyboardInterrupt:
    exit()