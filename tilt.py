import cv2
import dlib
import numpy as np
from playsound import playsound
from collections import deque

# Parameters
TILT_THRESHOLD = 200  # Adjusted tilt threshold
FRAME_COUNT_THRESHOLD = 30  # Frames for consistent detection
DROWSINESS_COUNT_THRESHOLD = 10  # Frames of sustained drowsiness

# Buffers
tilt_buffer = deque(maxlen=FRAME_COUNT_THRESHOLD)
drowsy_frames = 0

# Initialize dlib's face detector and landmark predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate scaled tilt angle
def scaled_downward_head_tilt(landmarks):
    nose = np.array(landmarks[30])  # Nose tip
    left_eye = np.array(landmarks[36])  # Left eye corner
    right_eye = np.array(landmarks[45])  # Right eye corner

    eye_center = (left_eye + right_eye) / 2
    vector = nose - eye_center
    angle = np.arctan2(vector[1], vector[0]) * (180.0 / np.pi)

    # Scale the angle for better sensitivity control
    scaled_angle = abs(angle) * 2.5  # Example scaling factor
    return scaled_angle if vector[1] > 0 and scaled_angle > TILT_THRESHOLD else 0

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

        # Compute scaled tilt
        tilt = scaled_downward_head_tilt(landmarks)
        tilt_buffer.append(tilt)

        avg_tilt = np.mean(tilt_buffer)

        if avg_tilt > TILT_THRESHOLD:
            drowsy_frames += 1
            if drowsy_frames >= DROWSINESS_COUNT_THRESHOLD:
                print(f"Drowsiness Detected! Tilt Angle: {avg_tilt:.2f}")
                playsound("audio/alarm.mp3")
        else:
            drowsy_frames = 0  # Reset if tilt is no longer sustained
            print(f"Tilt Angle: {avg_tilt:.2f} - Driver is alert.")

    cv2.imshow("Tilt-Only Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
