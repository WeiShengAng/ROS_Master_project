
from std_msgs.msg import String, Int8
import rospy
import numpy as np
import cv2
from time import sleep
import os
import time

cam_port = "/dev/video2"
cam = cv2.VideoCapture(cam_port)
rospy.init_node('Mod2_YOLOv4')

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
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x +x, y + h), color, 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), font, 0.5, color, 2)

            if class_ids[i] == 0:
                seed = 1
            
            if class_ids[i] == 1:
                seed_point = 1

    cv2.imshow("Module-2 Yolov4-tiny Real-time Detection", frame)

    pub = rospy.Publisher('Mod2_yoloseed', Int8, queue_size=5) # call arduino roll the seed
    pub_command = seed
    pub.publish(pub_command)

    pub = rospy.Publisher('Mod2_yoloseedpoint', Int8, queue_size=5) # call arduino roll the seed
    pub_command = seed_point
    pub.publish(pub_command)

    if cv2.waitKey(1) == ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        break