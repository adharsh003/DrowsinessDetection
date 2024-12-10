import cv2
import dlib
from scipy.spatial import distance as dist
from playsound import playsound
import numpy as np
from collections import deque

# Constants for thresholds and frame count
EAR_THRESHOLD = 0.25
MAR_THRESHOLD = 0.5
DOWNWARD_TILT_THRESHOLD = 20  # degrees (head looking downward)
FRAME_COUNT_THRESHOLD = 20  # Consecutive frames for confirmation

# Initialize dlib's face detector and facial landmark predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Buffers for multi-frame analysis
ear_buffer = deque(maxlen=FRAME_COUNT_THRESHOLD)
mar_buffer = deque(maxlen=FRAME_COUNT_THRESHOLD)
tilt_buffer = deque(maxlen=FRAME_COUNT_THRESHOLD)

# Functions to calculate EAR, MAR, and downward head tilt
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])
    B = dist.euclidean(mouth[4], mouth[8])
    C = dist.euclidean(mouth[0], mouth[6])
    return (A + B) / (2.0 * C)

def downward_head_tilt(landmarks):
    nose = np.array(landmarks[30])  # Nose tip
    left_eye = np.array(landmarks[36])  # Left eye corner
    right_eye = np.array(landmarks[45])  # Right eye corner

    # Calculate the horizontal eye line center
    eye_center = (left_eye + right_eye) / 2
    vector = nose - eye_center
    angle = np.arctan2(vector[1], vector[0]) * (180.0 / np.pi)
    
    # Downward tilt detection (negative angles indicate downward tilt)
    return angle if vector[1] > 0 else 0  # Only consider downward tilt

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray)

    for face in faces:
        landmarks = landmark_predictor(gray, face)
        landmarks = np.array([(p.x, p.y) for p in landmarks.parts()])

        # Compute EAR, MAR, and downward tilt
        left_eye = landmarks[42:48]
        right_eye = landmarks[36:42]
        mouth = landmarks[48:68]

        ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
        mar = mouth_aspect_ratio(mouth)
        tilt = downward_head_tilt(landmarks)

        # Buffer-based analysis
        ear_buffer.append(ear)
        mar_buffer.append(mar)
        tilt_buffer.append(tilt)

        avg_ear = np.mean(ear_buffer)
        avg_mar = np.mean(mar_buffer)
        avg_tilt = np.mean(tilt_buffer)

        # Detect drowsiness if thresholds are crossed
        if avg_ear < EAR_THRESHOLD or avg_mar > MAR_THRESHOLD or avg_tilt > DOWNWARD_TILT_THRESHOLD:
            if len(ear_buffer) == FRAME_COUNT_THRESHOLD:
                print("Drowsiness Detected!")
                playsound("audio/alarm.mp3")
        else:
            print("Driver is alert.")

    # Display the frame
    cv2.imshow("Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
