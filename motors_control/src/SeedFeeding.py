
from std_msgs.msg import String
import rospy
import serial
from time import sleep

s=serial.Serial("COM8",9600)
s.timeout = 0.5
step = 0

def SeedFeeding_node():
    rospy.init_node('Seed_Feeding_Motor', anonymous=True)

    pub = rospy.Publisher('Seed_Feed',String) #publisher define
    rospy.Subscriber('Seed_Detect_to_SF', String, callback) #subscriber define

    rate = rospy.Rate(10)
    rate.sleep()

    news = "Seed Feeding Done"
    pub.publish(news) #publish the news about seed feeding done

    rospy.spin() #stop at this line and wait for Seed_Detect callback msg
    # wait yolo to check if there are seed


def callback(msg):
    rospy.loginfo(msg.data)
    step = 3
    s.close()


#def Gripper_sub():

while not rospy.is_shutdown():

    if step == 0:
        while True:
            resp = s.readline().decode() # because what receive is bytes, use decode to transform bytes to str
            if resp == "Reset Done":
                print(resp)
                step = 1
                break        
            else:
                pass

    elif step == 1:
        while True:
            s.write('A'.encode()) # because what send is str, use encode to transform str to bytes
            sleep(0.1)
            resp = s.readline().decode() # because what receive is bytes, use decode to transform bytes to str
            if resp == "Seed Feeding Done":
                print(resp)
                step = 2
                break
            else:
                pass

    elif step == 2:
        SeedFeeding_node()

    elif step == 3:
        while True:
            print("stop at step = 3")
