
from std_msgs.msg import String
import rospy
import serial
from time import sleep

s=serial.Serial("COM8",9600)
s.timeout = 0.5
step = 0

def SeedRolling_node():
    rospy.init_node('Seed_Rolling_Motor', anonymous=True)

    pub = rospy.Publisher('Arduino_cmd_SR',String) #publisher define
    rospy.Subscriber('Roll_it', String, callback) #subscriber define

    rate = rospy.Rate(10)
    rate.sleep()

    news = "Seed Rolling Done"
    pub.publish(news) #publish the news about seed feeding done

    rospy.spin() #stop at this line and wait for Seed_Detect callback msg
    # wait yolo to check if there are seed


def callback(msg):
    rospy.loginfo(msg.data)
    step = 0
    


#def Gripper_sub():

while not rospy.is_shutdown():

    if step == 0:
        while True:
            s.write('B'.encode()) # because what send is str, use encode to transform str to bytes
            sleep(0.1)
            resp = s.readline().decode() # because what receive is bytes, use decode to transform bytes to str
            if resp == "Roll Done":
                print(resp)
                step = 1
                break        
            else:
                pass

    elif step == 1:
        SeedRolling_node()