
from std_msgs.msg import String
import rospy
import numpy as np
import cv2 as cv
from time import sleep
import os
import time

loop_count = 0

#define a node then publish topic 'chatter' and also can subscribe topic
rospy.init_node('YOLO')

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Arduino_cmd_SR', String, queue_size=10) # call arduino roll the seed
    pub_command = "Roll"
    pub.publish(pub_command)

    try:
        data = rospy.wait_for_message("/Arduino_SeedRolling", String, timeout = 1)
        print(data)
        length = len(data.data)
        if length > 4:
            return 1
    except rospy.ROSException:
        pass

    rate = rospy.Rate(1000) #10hz
    rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Arduino_cmd_SP', String, queue_size=10) # seed position is right, call arduino plant it
    pub2_command = "Plant"
    print("Planting")
    pub2.publish(pub2_command)

    try:
        data2 = rospy.wait_for_message("/Arduino_SeedPlanting", String, timeout = 1)
        print(data2)
        length2 = len(data2.data)
        if length2 > 4:
            return 1
    except rospy.ROSException:
        pass

    rate = rospy.Rate(1000) #10hz
    rate.sleep()

def yolo_detect():
    roll_cmd = 0
    # get the label names that named by us
    labelsPath = "yolov4/seed.names"
    LABELS = None
    with open(labelsPath,'rt') as f:
        LABELS = f.read().rstrip('\n').split("\n")

    # random get a color, it will use to define the color of the box of label later
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8") 

    weightsPath = "yolov4/yolov4_best.weights"
    configPath = "yolov4/yolov4.cfg"
    net = cv.dnn.readNetFromDarknet(configPath, weightsPath)

    #import image and define the height and weight
    image = cv.imread("test4.jpg")
    #imS = cv.resize(image, (960, 540))  #resize the window size of image show
    (H, W) = image.shape[:2]


    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()] # the reason here giv out error is because using python2, change to python 3 then solved
    blob = cv.dnn.blobFromImage(image, 1 / 255.0, (416, 416),swapRB=True, crop=False)
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
            if confidence > 0.8:
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
                cv.rectangle(image, (x, y), (x + w, y + h), color, 2)
                center_X = int(boxes[i][0] + (boxes[i][2] / 2))
                center_Y = int(boxes[i][1] + (boxes[i][3] / 2))
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                cv.putText(image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX,0.5, color, 2)
                if classIDs[i] == 1:
                    roll_cmd = 1

                
    #cv.imshow("Image", image)
    #cv.waitKey(0)
    return roll_cmd


def main():
    # while True:
    #     feed_stats = SeedFeeding()
    #     if feed_stats == 1:
    #         break
    
    cmd = yolo_detect()         # first we detect the seed first
    # cmd = 0 # to test plant
    
    if cmd == 1:                # if detected seed point
        while True:             
                roll_stats = SeedRoll()  # roll the seed
                if roll_stats == 1:      # if seed roll done then break
                    break

    elif cmd == 0:
        while True:
            plant_stats = SeedPlanting() # plant the seed
            if plant_stats == 1:         # if plant done then break
                break
    
while True:
    main()
    loop_count = loop_count+ 1
    print(loop_count)