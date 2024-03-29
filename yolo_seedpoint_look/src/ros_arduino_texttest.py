
from std_msgs.msg import String
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time

cam_port = 4
cam = cv.VideoCapture(cam_port)

loop_count = 0
feed_stats = 2
#define a node then publish topic 'chatter' and also can subscribe topic
rospy.init_node('YOLO')

def SeedFeeding():
    pub0 = rospy.Publisher('Arduino_cmd_SF', String, queue_size=5) # call arduino roll the seed
    time.sleep(0.3)
    pub0_command = "Feed"
    pub0.publish(pub0_command)
    print("Feeding Seed...")
    try:
        data0 = rospy.wait_for_message("/Arduino_SeedFeeding", String, timeout = 5) # timeout value base on the time need to feed one seed, if over this time then publish again
        length0 = len(data0.data)
        if length0 > 4:
            print("Seed Feeded\n")
            return 1
    except rospy.ROSException:
        pass

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Arduino_cmd_SR', String, queue_size=5) # call arduino roll the seed
    time.sleep(0.3)
    pub_command = "Roll"
    pub.publish(pub_command)
    print("Rolling Seed...")

    try: 
        data1 = rospy.wait_for_message("/Arduino_SeedRolling", String, timeout=5) # timeout value base on the time need to roll the seed
        length1 = len(data1.data)
        if length1 > 4:
            print("Seed Rolled\n")
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Arduino_cmd_SP', String, queue_size=5) # seed position is right, call arduino plant it
    time.sleep(0.3)
    pub2_command = "Plant"
    pub2.publish(pub2_command)
    print("Planting...")

    try:
        data2 = rospy.wait_for_message("/Arduino_SeedPlanting", String, timeout=60) # timeout value base on the time need to plant one seed
        length2 = len(data2.data)
        if length2 > 4:
            print("Seed Planted\n")
            # exit()
            return 1
    except rospy.ROSException:
        pass

    # rate = rospy.Rate(1000) #10hz
    # rate.sleep()

def yolo_detect(img_input):
    roll_cmd = 0
    start_cmd = 0 # o means no seed
    # get the label names that named by us
    labelsPath = "yolov4/seed.names"
    LABELS = None
    with open(labelsPath,'rt') as f:
        LABELS = f.read().rstrip('\n').split("\n")

    # random get a color, it will use to define the color of the box of label later
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8") 

    # current weight version : overfit_solve #
    weightsPath = "yolov4/yolov4-tiny-obj_best.weights"
    configPath = "yolov4/yolov4-tiny-obj.cfg"
    net = cv.dnn.readNetFromDarknet(configPath, weightsPath)

    #import image and define the height and weight

    image1 = cv.imread(img_input) # use this line when using jpg file as example
    imS = cv.resize(image1, (960, 540))  #resize the window size of image1 show

    # image1 = img_input # use this line when using camera to take photo

    (H, W) = image1.shape[:2]


    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()] # the reason here giv out error is because using python2, change to python 3 then solved
    blob = cv.dnn.blobFromImage(image1, 1 / 255.0, (416, 416),swapRB=True, crop=False)
    net.setInput(blob)

    # record the time of start and end to detect the object
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))


    boxes = []
    confidences = []
    classIDs = [] 
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores) 
            confidence = scores[classID]
            if confidence > 0.75:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)


    idxs = cv.dnn.NMSBoxes(boxes, confidences, 0.5,0.4)
    if len(idxs) > 0: 
        for i in idxs.flatten(): 
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in COLORS[classIDs[i]]] 
                cv.rectangle(image1, (x, y), (x + w, y + h), color, 2)
                center_X = int(boxes[i][0] + (boxes[i][2] / 2))
                center_Y = int(boxes[i][1] + (boxes[i][3] / 2))
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                cv.putText(image1, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX,0.5, color, 2)

                if classIDs[i] == 0:
                    start_cmd = 1

                if classIDs[i] == 1:
                    roll_cmd = 1

                
    # cv.imshow("Image", image1)
    # cv.waitKey(0)
    return start_cmd, roll_cmd




def main(stat):
    # while True:
    #     feed_stats = SeedFeeding()
    #     if feed_stats == 1:
    #         break
    
    # while True: # yolo detect while loop
        
    #"""
    # to use diff picture as example, change this whole section to camera when in real usage #
    if stat == 1:
        print("############ START ############\n")
        feed_stats, cmd = 0,0
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    elif stat == 2:    
        feed_stats, cmd = 1,1
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    elif stat == 3:
        feed_stats, cmd = 1,0
        print("|{0:^10}|{1:^10}|".format("是否有種子", "是否有芽點"))
        print("|{:^15}|{:^15}|".format(feed_stats,cmd))
    #'''

    
    
    # feed_stats, cmd = yolo_detect(yolo_input) # feed_stats = 1 means found seed, the seed drop successfully on fanzhuan
                                                # this  function is also use to proceed the cmd to decide whether roll or plant the seed
    if feed_stats == 0: 
        print("NO SEED")
        while True:             
            roll_stats = SeedFeeding()  # feed the seed
            if roll_stats == 1:      # if seed feeded then break
                break # break seedfeeding publish loop
    elif feed_stats == 1: 

        if cmd == 1:                # if detected seed point
            print("芽點朝上")
            while True:             
                    roll_stats = SeedRoll()  # roll the seed
                    if roll_stats == 1:      # if seed roll done then break
                        break

        elif cmd == 0:
            print("芽點朝下")
            while True:
                plant_stats = SeedPlanting() # plant the seed
                if plant_stats == 1:         # if plant done then break
                    print("############ END ############\n")
                    exit()
                    break

try:
    while True:
        loop_count = loop_count + 1
        main(loop_count)
        # print(loop_count)

except KeyboardInterrupt:
    pass