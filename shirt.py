import os
from flask import request
import cvzone
import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(0)
detector = PoseDetector()

#shirt_path = "C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/shirt_images/s2.png"
shirt_path = ""

with open("shirt_path.txt", "r") as file:
    shirt_path = file.read().strip()

print(shirt_path)

# print(listShirts)
fixedRatio = 262 / 190  # widthOfShirt/widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440

while True:
    success, img = cap.read()
    img = detector.findPose(img, draw=False)
    # img = cv2.flip(img,1)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)
    if lmList:
        # center = bboxInfo["center"]
        lm11 = lmList[11][1:3]
        lm12 = lmList[12][1:3]
        imgShirt = cv2.imread(shirt_path, cv2.IMREAD_UNCHANGED)
        try:
            widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)
            print(widthOfShirt)
            imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
            currentScale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * currentScale), int(48 * currentScale)


            img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
        except:
            pass

    cv2.imshow("Virtual Shirt Try-On", img)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty('Virtual Shirt Try-On', cv2.WND_PROP_VISIBLE) < 1:
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
