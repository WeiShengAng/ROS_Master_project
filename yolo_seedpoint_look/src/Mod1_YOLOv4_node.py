
from std_msgs.msg import String, Int8
import rospy
import numpy as np
import cv2
from time import sleep
import os
import time

cam_port = "/dev/video1"
cam = cv2.VideoCapture(cam_port)
rospy.init_node('Mod1_YOLOv4')

weightsPath = "yolov4/yolov4-tiny-obj_best.weights"
configPath = "yolov4/yolov4-tiny-obj.cfg"
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

classes = []
with open("yolov4/seed.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

while True:
    ret, frame = cam.read()
    if not ret:
        break
    height, width, channels = frame.shape

    seed = 0 #reset this var
    seed_point = 0 #reset this var

    # 对图像进行预处理
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.75:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.75)

    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            confidence = confidences[i]
            color = (0, 255, 0)  # 边界框颜色（绿色）
            cv2.rectangle(frame, (x, y), (x +x, y + h), color, 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), font, 0.5, color, 2)

            if class_ids[i] == 0:
                seed = 1
            
            if class_ids[i] == 1:
                seed_point = 1

    cv2.imshow("Yolov4 Real-time Detection", frame)

    pub = rospy.Publisher('Mod1_yoloseed', Int8, queue_size=5) # call arduino roll the seed
    pub_command = seed
    pub.publish(pub_command)

    pub = rospy.Publisher('Mod1_yoloseedpoint', Int8, queue_size=5) # call arduino roll the seed
    pub_command = seed_point
    pub.publish(pub_command)

    if cv2.waitKey(1) == ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        break

    



# def yolo_detect(img_input):
#     roll_cmd = 0
#     start_cmd = 0 # o means no seed
#     # get the label names that named by us
#     labelsPath = "yolov4/seed.names"
#     LABELS = None
#     with open(labelsPath,'rt') as f:
#         LABELS = f.read().rstrip('\n').split("\n")

#     # random get a color, it will use to define the color of the box of label later
#     np.random.seed(42)
#     COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8") 

#     # current weight version : overfit_solve #
#     weightsPath = "yolov4/yolov4-tiny-obj_best.weights"
#     configPath = "yolov4/yolov4-tiny-obj.cfg"
#     net = cv.dnn.readNetFromDarknet(configPath, weightsPath)

#     #import image and define the height and weight

#     #image1 = cv.imread(img_input) # use this line when using jpg file as example
#     #imS = cv.resize(image1, (960, 540))  #resize the window size of image1 show

#     image1 = img_input # use this line when using camera to take photo

#     (H, W) = image1.shape[:2]


#     ln = net.getLayerNames()
#     ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()] # the reason here giv out error is because using python2, change to python 3 then solved
#     blob = cv.dnn.blobFromImage(image1, 1 / 255.0, (416, 416),swapRB=True, crop=False)
#     net.setInput(blob)

#     # record the time of start and end to detect the object
#     start = time.time()
#     layerOutputs = net.forward(ln)
#     end = time.time()
#     print("[INFO] YOLO took {:.6f} seconds".format(end - start))


#     boxes = []
#     confidences = []
#     classIDs = [] 
#     for output in layerOutputs:
#         for detection in output:
#             scores = detection[5:]
#             classID = np.argmax(scores) 
#             confidence = scores[classID]
#             if confidence > 0.75:
#                 box = detection[0:4] * np.array([W, H, W, H])
#                 (centerX, centerY, width, height) = box.astype("int")
#                 x = int(centerX - (width / 2))
#                 y = int(centerY - (height / 2))
#                 boxes.append([x, y, int(width), int(height)])
#                 confidences.append(float(confidence))
#                 classIDs.append(classID)


#     idxs = cv.dnn.NMSBoxes(boxes, confidences, 0.5,0.4)
#     if len(idxs) > 0: 
#         for i in idxs.flatten(): 
#                 (x, y) = (boxes[i][0], boxes[i][1])
#                 (w, h) = (boxes[i][2], boxes[i][3])
#                 color = [int(c) for c in COLORS[classIDs[i]]] 
#                 cv.rectangle(image1, (x, y), (x + w, y + h), color, 2)
#                 center_X = int(boxes[i][0] + (boxes[i][2] / 2))
#                 center_Y = int(boxes[i][1] + (boxes[i][3] / 2))
#                 text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
#                 cv.putText(image1, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX,0.5, color, 2)

#                 if classIDs[i] == 0:
#                     start_cmd = 1

#                 if classIDs[i] == 1:
#                     roll_cmd = 1

                
#     cv.imshow("Real Time Detection", image1)
#     cv.waitKey(0)
#     cv.destroyWindow()
#     cam.release()
#     # return start_cmd, roll_cmd
