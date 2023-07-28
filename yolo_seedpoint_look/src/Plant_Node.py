#!/usr/bin/env python

from std_msgs.msg import String, Int16
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time


rospy.init_node('Plant_ROS')

def Plant_msg_collect():
    while True:
        try:
            data2 = rospy.wait_for_message("/Mod1_cmd_SP", String, timeout=1)
            length2 = len(data2.data)
            data3 = rospy.wait_for_message("/Mod2_cmd_SP", String, timeout=1)
            length3 = len(data3.data)
            if length2 > 4:
                mod1 = 1
            if length3 > 4:
                mod2 = 1

            if mod1 == 1 and mod2 == 1:
                mod1 = 0
                mod2 = 0
                return 1
            else:
                pass
        except rospy.ROSException:
            pass


def Plant_Agent():
    pub = rospy.Publisher('cmd_Plant', String, queue_size=1) # seed position is right, call arduino plant it
    pub_command = "Plant"
    pub.publish(pub_command)
    print("Planting...")

    try:
        recv_msg = rospy.wait_for_message("/Ard_Recv", Int16, timeout=1) # timeout value base on the time need to plant one seed
        recv = recv_msg.data
        if recv == 1:
            print("msg recv")
            while True:
                try:
                    msg = rospy.wait_for_message("/Ard_Plant1", Int16, timeout=1) # timeout value base on the time need to plant one seed
                    data1 = msg.data
                    if data1 == 1:
                        print("Seed Planted\n")
                        exit()
                        # return 1
                except rospy.ROSException:
                    pass
    except rospy.ROSException:
            pass

try:
    while True:
        cmd = Plant_msg_collect()
        if cmd == 1:
            Plant_Agent()

except KeyboardInterrupt:
    exit()