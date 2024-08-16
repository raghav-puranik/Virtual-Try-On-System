import cv2
import numpy as np
import dlib

# Load the pre-trained facial landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

glass_path = ""

with open("glass_path.txt", "r") as file:
    glass_path = file.read().strip()

# glass_path = "C:/Users/ragha/PycharmProjects/virtual_tryon_website/static/glass_images/glass_5.png"

# Load the image of the glasses
glasses_img = cv2.imread(glass_path, cv2.IMREAD_UNCHANGED)

# Ensure the glasses image has an alpha channel

if glasses_img.shape[2] == 3:
    # If the glasses image doesn't have an alpha channel, create one
    alpha_channel = np.ones_like(glasses_img[:, :, 0]) * 255
    glasses_img = np.dstack((glasses_img, alpha_channel))

# Capture video from the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    try:
        faces = detector(gray)

        for face in faces:
            # Get facial landmarks
            landmarks = predictor(gray, face)

            if landmarks is not None:
                # Extract coordinates of the relevant facial landmarks (nose and eyes)
                nose_bridge = (landmarks.part(27).x, landmarks.part(27).y)
                left_eye = (landmarks.part(37).x, landmarks.part(37).y)
                right_eye = (landmarks.part(46).x, landmarks.part(46).y)

                # Calculate the width of the glasses based on the distance between the eyes
                glasses_width = int(np.linalg.norm(np.array(left_eye) - np.array(right_eye)) * 1.5) + 35

                # Resize the glasses image to match the calculated width
                glasses_resized = cv2.resize(glasses_img, (glasses_width, int(glasses_width / glasses_img.shape[1] * glasses_img.shape[0])))

                # Calculate the position to place the glasses on the nose
                glasses_x = int(nose_bridge[0] - glasses_width / 2)
                glasses_y = int(nose_bridge[1] - glasses_resized.shape[0] / 2) + 10

                # Overlay the glasses on the frame
                for c in range(0, 3):
                    frame[glasses_y:glasses_y + glasses_resized.shape[0], glasses_x:glasses_x + glasses_resized.shape[1], c] \
                        = glasses_resized[:, :, c] * (glasses_resized[:, :, 3] / 255.0) + \
                          frame[glasses_y:glasses_y + glasses_resized.shape[0], glasses_x:glasses_x + glasses_resized.shape[1], c] * (1.0 - glasses_resized[:, :, 3] / 255.0)
    except:
        pass
    # Display the result
    cv2.imshow('Virtual Glasses Try-On', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty('Virtual Glasses Try-On', cv2.WND_PROP_VISIBLE) < 1:
        break

# Release the webcam and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
