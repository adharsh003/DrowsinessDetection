import cv2
from playsound import playsound
import dlib
import numpy as np
from collections import deque

# Load the Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Load the shape predictor for yawning detection
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()

# Function to calculate head tilt angle
def head_tilt_angle(landmarks):
    nose = np.array(landmarks[30])
    left_eye = np.array(landmarks[36])
    right_eye = np.array(landmarks[45])

    eye_center = (left_eye + right_eye) / 2
    vector = nose - eye_center
    angle = np.arctan2(vector[1], vector[0]) * (180.0 / np.pi)
    return angle

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Variables for tilt detection and drowsiness
TILT_THRESHOLD_LOW = 30   # Angle below which head is considered tilted downward
TILT_THRESHOLD_HIGH = 115  # Angle above which head is considered tilted backward
RESET_AFTER_ALERT = 50  # Frames to wait before resetting after drowsiness
tilt_buffer = deque(maxlen=5)  # Buffer for smoothing tilt angle
frame_count_since_alert = 0
drowsiness_detected = False
drowsy_frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using dlib
    faces_dlib = detector(gray)

    for face in faces_dlib:
        shape = predictor(gray, face)
        landmarks = [(p.x, p.y) for p in shape.parts()]

        # Calculate the head tilt angle
        tilt = head_tilt_angle(landmarks)

        # Smoothing the tilt value using moving average
        tilt_buffer.append(tilt)
        if len(tilt_buffer) > 0:
            smoothed_tilt = np.mean(tilt_buffer)

        # Check if drowsiness is detected (Tilt angle is either too low or too high)
        if smoothed_tilt < TILT_THRESHOLD_LOW or smoothed_tilt > TILT_THRESHOLD_HIGH:
            if not drowsiness_detected:
                drowsiness_detected = True
                drowsy_frames = 1  # Start counting drowsy frames
                print(f"Drowsiness Detected! Tilt Angle: {smoothed_tilt:.2f}")
                playsound("audio/alarm.mp3")  # Play alarm sound

        # Frame count since last drowsiness detection
        if drowsiness_detected:
            frame_count_since_alert += 1

            # If the tilt has been upright for a few frames, reset the detection
            if smoothed_tilt >= TILT_THRESHOLD_LOW and smoothed_tilt <= TILT_THRESHOLD_HIGH and frame_count_since_alert > RESET_AFTER_ALERT:
                drowsiness_detected = False
                frame_count_since_alert = 0
                print(f"Drowsiness Reset. Tilt Angle: {smoothed_tilt:.2f} - Driver is alert.")

        # Display tilt angle on the frame
        cv2.putText(frame, f"Tilt Angle: {smoothed_tilt:.2f}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow("Webcam Feed", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Press 'q' to exit the loop
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
