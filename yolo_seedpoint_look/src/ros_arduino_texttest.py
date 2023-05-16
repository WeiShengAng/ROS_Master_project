
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

# def SeedFeeding():
#     try:
#         data0 = rospy.wait_for_message("/Arduino_SeedFeeding", String, timeout = 1)
#         print(data0)
#         length0 = len(data0.data)
#         if length0 > 4:
#             return 1
#     except rospy.ROSException:
#         pass

def SeedRoll():
    #if run only once fail, then use for loop and run few more times
    pub = rospy.Publisher('Arduino_cmd_SR', String, queue_size=10) # call arduino roll the seed
    pub_command = "Roll"
    print("Rolling Seed...")
    pub.publish(pub_command)

    try: 
        data1 = rospy.wait_for_message("/Arduino_SeedRolling", String, timeout=1) # timeout = 1 deleted
        length1 = len(data1.data)
        if length1 > 4:
            print("Seed Rolled\n")
            return 1
    except rospy.ROSException:
        pass

    rate = rospy.Rate(10) #10hz
    rate.sleep()

def SeedPlanting():
    #if run only once fail, then use for loop and run few more times
    pub2 = rospy.Publisher('Arduino_cmd_SP', String, queue_size=10) # seed position is right, call arduino plant it
    pub2_command = "Plant"
    print("Planting...")
    pub2.publish(pub2_command)
    
    try:
        data2 = rospy.wait_for_message("/Arduino_SeedPlanting", String, timeout=1) # timeout = 1 deleted
        length2 = len(data2.data)
        if length2 > 4:
            print("Seed Planted\n")
            exit()
            return 1
    except rospy.ROSException:
        pass

    rate = rospy.Rate(10) #10hz
    rate.sleep()

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
    
    while True: # yolo detect while loop
        
        #"""
        # to use diff picture as example #

        if stat % 2 != 0:
            print("############ START ############\n")
            yolo_input = "test4.jpg" # have seed point
        else:
            yolo_input = "test.jpg" # dont have see point

        # to use diff picture as example #
        #"""

        # use real time seed photo

        #result, image = cam.read()

        
        # feed_stats,cmd = yolo_detect(image)
        # print(feed_stats,cmd)
        # cv.waitKey(0)
        # cv.destroyWindow("Image")

        # use real time seed photo

        stat =~ stat # =~ means not, which let 1 become 0, 0 become 1
        
        feed_stats, cmd = yolo_detect(yolo_input) # feed_stats = 1 means found seed, the seed drop successfully on fanzhuan
                                                  # this  function is also use to proceed the cmd to decide whether roll or plant the seed
        print(feed_stats,cmd)
        if feed_stats == 1: 
            break # if got seed (feed_stats) break this while loop, cont to do the code under
                  # if dont have seed, keep running this yolo detect while loop
    
    # cmd = yolo_detect()         # first we detect the seed first
    # cmd = 0 # to test plant

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
                #exit()
                break

try:
    while True:
        loop_count = loop_count + 1
        main(loop_count)
        # print(loop_count)

except KeyboardInterrupt:
    pass