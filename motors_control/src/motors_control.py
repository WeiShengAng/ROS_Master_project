
from std_msgs.msg import String
import rospy

def Motors_Node():
    rospy.init_node('motors', anonymous=True)
    rospy.Subscriber('chatter', String, callback)
    rate = rospy.Rate(10)
    rate.sleep()

def callback(msg):
    rospy.loginfo(rospy.get_caller_id() + "i heard %s", msg.data)

while not rospy.is_shutdown():
    Motors_Node()