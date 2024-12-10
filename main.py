#latest

import cv2
from playsound import playsound
import dlib
from scipy.spatial import distance as dist
import threading
import time

# Load the Haar cascades for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load dlib predictor for facial landmarks
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()

# Function to calculate the Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function to calculate the Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])
    B = dist.euclidean(mouth[4], mouth[8])
    C = dist.euclidean(mouth[0], mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

# Function to play alarm sound in a separate thread
def play_alarm():
    playsound(r'C:\Users\91859\DrowsinessDetection\audio\alarm.mp3')

# Thresholds
EAR_THRESHOLD = 0.22  # Lower for stricter eye closure detection
MAR_THRESHOLD = 0.55  # Higher to avoid triggering on normal talking
CONSEC_FRAMES = 5  # Increase for better stability
COOLDOWN_SECONDS = 10  # Alarm cooldown duration

# Initialize variables
ear_counter = 0
alarm_on = False
last_alarm_time = time.time()

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)
    for face in faces:
        shape = predictor(gray, face)
        landmarks = [(p.x, p.y) for p in shape.parts()]

        # Extract eye and mouth landmarks
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        mouth = landmarks[48:68]

        # Calculate EAR and MAR
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        mar = mouth_aspect_ratio(mouth)

        # Combine into drowsiness score
        drowsiness_score = (1 - ear) * 0.7 + mar * 0.3

        # Check for drowsiness
        current_time = time.time()
        if ear < EAR_THRESHOLD or mar > MAR_THRESHOLD:
            ear_counter += 1
            if ear_counter >= CONSEC_FRAMES and not alarm_on and (current_time - last_alarm_time > COOLDOWN_SECONDS):
                print("Drowsiness detected!")
                alarm_on = True
                last_alarm_time = current_time
                threading.Thread(target=play_alarm, daemon=True).start()
        else:
            ear_counter = 0
            alarm_on = False

        # Draw face landmarks and metrics on the frame
        for (x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
        cv2.putText(frame, f"EAR: {ear:.2f} MAR: {mar:.2f} Score: {drowsiness_score:.2f}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Display the frame
    cv2.imshow("Drowsiness Detection", frame)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
