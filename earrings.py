import cv2
import numpy as np
import dlib

# Load the pre-trained facial landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Load the images of the earrings for left and right ears
# left_earrings_img = cv2.imread("C:/Users/ragha/PycharmProjects/Trial/Resources/Earings/12-removebg-preview.png", cv2.IMREAD_UNCHANGED)
# right_earrings_img = cv2.imread("C:/Users/ragha/PycharmProjects/Trial/Resources/Earings/12-removebg-preview.png", cv2.IMREAD_UNCHANGED)

#C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/earring_images/earrings_1.png

earrings_path = ""

with open("earrings_path.txt", "r") as file:
    earrings_path = file.read().strip()

# earrings_path = "C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/earring_images/earrings_14.png"

left_earrings_img = cv2.imread(earrings_path, cv2.IMREAD_UNCHANGED)
right_earrings_img = cv2.imread(earrings_path, cv2.IMREAD_UNCHANGED)

# Ensure the earrings images have an alpha channel
if left_earrings_img.shape[2] == 3:
    left_alpha_channel = np.ones_like(left_earrings_img[:, :, 0]) * 255
    left_earrings_img = np.dstack((left_earrings_img, left_alpha_channel))

if right_earrings_img.shape[2] == 3:
    right_alpha_channel = np.ones_like(right_earrings_img[:, :, 0]) * 255
    right_earrings_img = np.dstack((right_earrings_img, right_alpha_channel))

# Capture video from the webcam
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/f.mp4")

# Define a scaling factor for the earrings size
earrings_scaling_factor = 0.2  # Adjust this value to control the size of the earrings

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = detector(gray)
    try:


        for face in faces:
            # Get facial landmarks
            landmarks = predictor(gray, face)

            if landmarks is not None:
                # Extract coordinates of the relevant facial landmarks (ear positions)
                left_ear_top = (landmarks.part(0).x, landmarks.part(0).y)
                right_ear_top = (landmarks.part(13).x, landmarks.part(13).y)

                # Calculate the width of the earrings based on the distance between ears
                earrings_width = int(np.linalg.norm(np.array(left_ear_top) - np.array(right_ear_top)) * 1.5 * earrings_scaling_factor)

                # Resize the earrings images to match the calculated width
                left_earrings_resized = cv2.resize(left_earrings_img, (earrings_width, int(earrings_width / left_earrings_img.shape[1] * left_earrings_img.shape[0])))
                right_earrings_resized = cv2.resize(right_earrings_img, (earrings_width, int(earrings_width / right_earrings_img.shape[1] * right_earrings_img.shape[0])))

                # Calculate the position to place the earrings for each ear
                left_earrings_x = int(left_ear_top[0] - earrings_width / 2) + 3
                left_earrings_y = int(left_ear_top[1] - left_earrings_resized.shape[0] / 2) +68

                right_earrings_x = int(right_ear_top[0] - earrings_width / 2) + 10
                right_earrings_y = int(
                    right_ear_top[1] - right_earrings_resized.shape[0] / 2) + 20# Lower the position by 3 pixels

                # Overlay the earrings on the frame for each ear
                for c in range(0, 3):
                    frame[left_earrings_y:left_earrings_y + left_earrings_resized.shape[0],
                    left_earrings_x:left_earrings_x + left_earrings_resized.shape[1], c] \
                        = left_earrings_resized[:, :, c] * (left_earrings_resized[:, :, 3] / 255.0) + \
                          frame[left_earrings_y:left_earrings_y + left_earrings_resized.shape[0],
                          left_earrings_x:left_earrings_x + left_earrings_resized.shape[1], c] * (
                                      1.0 - left_earrings_resized[:, :, 3] / 255.0)

                    frame[right_earrings_y:right_earrings_y + right_earrings_resized.shape[0],
                    right_earrings_x:right_earrings_x + right_earrings_resized.shape[1], c] \
                        = right_earrings_resized[:, :, c] * (right_earrings_resized[:, :, 3] / 255.0) + \
                          frame[right_earrings_y:right_earrings_y + right_earrings_resized.shape[0],
                          right_earrings_x:right_earrings_x + right_earrings_resized.shape[1], c] * (
                                      1.0 - right_earrings_resized[:, :, 3] / 255.0)
    except:
        pass
    # Display the result
    cv2.imshow('Virtual Earrings Try-On', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty('Virtual Earrings Try-On', cv2.WND_PROP_VISIBLE) < 1:
        break
# Release the webcam and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
