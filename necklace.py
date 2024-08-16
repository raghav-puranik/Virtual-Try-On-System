# necklace.py
import cv2
import numpy as np
import sys
import mediapipe as mp
import cvzone

#C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/necklace_images/necklace_g4.png
necklace_path = "C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/necklace_images/necklace_b10.png"

necklace_path = ""

with open("necklace_path.txt", "r") as file:
    necklace_path = file.read().strip()

print(f"Processing image at path: {necklace_path}")

# Load the virtual necklace image with alpha channel
necklace_img = cv2.imread(necklace_path, cv2.IMREAD_UNCHANGED)
necklace_rgb = necklace_img[:, :, :3]
necklace_alpha = necklace_img[:, :, 3] / 255.0

# Load the face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open the webcam
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/f.mp4")

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    try:
        for (x, y, w, h) in faces:
            # Resize the virtual necklace image to fit the face
            resized_necklace_rgb = cv2.resize(necklace_rgb, (w, h))
            resized_necklace_alpha = cv2.resize(necklace_alpha, (w, h))

            # Adjust the 'y' coordinate by subtracting 10 pixels to lower the necklace
            y_offset = 185

            # Create a mask from the alpha channel
            mask = resized_necklace_alpha[:, :, np.newaxis]

            # Blend the virtual necklace with the face using the mask
            roi_color = frame[y + y_offset:y + h + y_offset, x:x + w, :3]
            frame[y + y_offset:y + h + y_offset, x:x + w, :3] = (
                    (1 - mask) * roi_color + mask * resized_necklace_rgb
            )
    except:
        pass

    # Display the frame
    cv2.imshow('Virtual Necklace Try-On', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty('Virtual Necklace Try-On', cv2.WND_PROP_VISIBLE) < 1:
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
