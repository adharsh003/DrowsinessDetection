import cv2
import dlib
import webbrowser
from scipy.spatial import distance

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()

# Use the correct path for the predictor file
predictor_path = r"C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

# Function to calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    if len(eye) != 6:
        return 1.0  # Return a high EAR if detection fails to avoid false triggers

    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Indices for eyes landmarks
(lStart, lEnd) = (42, 48)  # Right eye
(rStart, rEnd) = (36, 42)  # Left eye

# Start video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access camera!")
    exit()

frame_count = 0
DROWSINESS_THRESHOLD = 3  # Number of frames to trigger an alert

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Camera not detected!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = detector(gray)
    for face in faces:
        landmarks = predictor(gray, face)
        
        leftEye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(lStart, lEnd)]
        rightEye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(rStart, rEnd)]
        
        if len(leftEye) != 6 or len(rightEye) != 6:
            continue  # Skip if landmark detection fails
        
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        avg_EAR = (leftEAR + rightEAR) / 2.0

        # If EAR is below threshold, increase frame count
        if avg_EAR < 0.25:
            frame_count += 1
            if frame_count >= DROWSINESS_THRESHOLD:
                print("Drowsiness detected! Sending SOS...")
                webbrowser.open(r"C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\loc.html")  # Open alert
                frame_count = 0  # Reset frame count after sending alert
        else:
            frame_count = 0  # Reset counter if eyes are open

    cv2.imshow("Drowsiness Detection", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
