
"""
problem : yolov4 tiny without pretrain seems like overfitting with the seed,becuz its precision was nearly 100%
and in testing session, it cant detect them precisely
"""
import cv2 as cv
import numpy as np
import time


cam_port = 7
cam = cv.VideoCapture(cam_port)

def yolo_detect(img_input):
    roll_cmd = 0
    start_cmd = 0
    # get the label names that named by us
    labelsPath = "yolov4/seed.names"
    LABELS = None
    with open(labelsPath,'rt') as f:
        LABELS = f.read().rstrip('\n').split("\n")

    # random get a color, it will use to define the color of the box of label later
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8") 

    weightsPath = "yolov4/yolov4-tiny-obj_final.weights"
    configPath = "yolov4/yolov4-tiny-obj.cfg"
    net = cv.dnn.readNetFromDarknet(configPath, weightsPath)

    #import image and define the height and weight

    #image1 = cv.imread(img_input) # use this line when using jpg file as example
    #imS = cv.resize(image1, (960, 540))  #resize the window size of image1 show

    image1 = img_input # use this line when using camera to take photo

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
                cv.rectangle(image1, (x, y), (x + w, y + h), color, 2)
                center_X = int(boxes[i][0] + (boxes[i][2] / 2))
                center_Y = int(boxes[i][1] + (boxes[i][3] / 2))
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                cv.putText(image1, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX,0.5, color, 2)

                if classIDs[i] == 0:
                    start_cmd = 1

                if classIDs[i] == 1:
                    roll_cmd = 1

                
    cv.imshow("Image", image1)
    
    return start_cmd, roll_cmd

def main():
    result, image = cam.read()

    if result:
        start,cmd = yolo_detect(image)
        print(start,cmd)
        cv.waitKey(0)
        cv.destroyWindow("Image")

    else:
        print("no image")

main()