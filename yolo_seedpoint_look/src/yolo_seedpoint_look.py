from std_msgs.msg import String
import rospy
import numpy as np
import cv2 as cv
import time
import os

#define a node then publish topic 'chatter' and also can subscribe topic
def YOLO_node():
    rospy.init_node('YOLO')

    pub = rospy.Publisher('Seed_Detect_to_SF', String) #s end msg to seed feeding and let him know it have seed
    pub_command = "have seed point"
    pub.publish(pub_command)

    pub2 = rospy.Publisher('Seed_Detect_to_SR', String) # send msg to seed rolling
    pub2_command = "Roll the Seed"
    pub2.publish(pub2_command)

    rate = rospy.Rate(10) #10hz
    rate.sleep

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
ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
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
    
    YOLO_node() #execute yolo node because there are seed


cv.imshow("Image", image)
cv.waitKey(0)
