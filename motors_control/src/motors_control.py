
from std_msgs.msg import String
import rospy
import serial
from time import sleep

s=serial.Serial("COM8",9600)
s.timeout = 0.5

def SeedFeeding():
    rospy.init_node('motors', anonymous=True)
    pub = rospy.Publisher('SeedFeedDone',String)
    rospy.Subscriber('LookForSeed', int, callback)
    rate = rospy.Rate(10)
    rate.sleep()

    # publish seed feeding done to yolo
    news = "Seed Feeding Done"
    pub.publish(news)

    # wait yolo to check if there are seed


def callback(msg):
    rospy.loginfo("Seed info from yolo: %i", msg.data)

while not rospy.is_shutdown():

    s.write('T'.encode()) # because what send is str, use encode to transform str to bytes
    sleep(0.1)

    msg = s.readline().decode() # because what receive is bytes, use decode to transform bytes to str
    print(msg)
    if msg == "Seed Feeding Motor Runned Finish":
        while True:
            SeedFeeding()

    else:
        pass
