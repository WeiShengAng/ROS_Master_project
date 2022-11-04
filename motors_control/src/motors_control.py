
from std_msgs.msg import String
import rospy
import serial
from time import sleep

s=serial.Serial("COM8",9600)

def SeedFeeding_Node():
    rospy.init_node('motors', anonymous=True)
    pub = rospy.Publisher('chatter',String)
    rospy.Subscriber('chatter', String, callback)
    rate = rospy.Rate(10)
    rate.sleep()

def callback(msg):
    rospy.loginfo(rospy.get_caller_id() + "i heard %s", msg.data)

while not rospy.is_shutdown():
    Motors_Node()
    while True:
        s.write('T'.encode()) # because what send is str, use encode to transform str to bytes
        sleep(0.1)
