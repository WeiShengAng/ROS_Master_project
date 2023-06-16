
from std_msgs.msg import String 
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time


rospy.init_node('Plant_ROS')

def Plant_Agent():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('cmd_Plant', String, queue_size=5) # seed position is right, call arduino plant it
    time.sleep(0.3)
    pub_command = "Plant"
    pub.publish(pub_command)
    print("Planting...")

    try:
        msg = rospy.wait_for_message("/Ard_Plant", String, timeout=30) # timeout value base on the time need to plant one seed
        length = len(msg.data)
        if length > 4:
            print("Seed Planted\n")
            # exit()
            return 1
    except rospy.ROSException:
        pass

try:
    while True:
        Plant_Agent()

except KeyboardInterrupt:
    exit()