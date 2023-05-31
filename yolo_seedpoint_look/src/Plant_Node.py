
from std_msgs.msg import String
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time


rospy.init_node('Plant_Node')

def Plant_Agent():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('cmd_SP', String, queue_size=5) # seed position is right, call arduino plant it
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