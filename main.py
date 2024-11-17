import cv2
from playsound import playsound
import dlib
from scipy.spatial import distance as dist

# Load the Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Load the shape predictor for yawning detection
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()

# Function to calculate the mouth aspect ratio (MAR) for yawning detection
def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])
    B = dist.euclidean(mouth[4], mouth[8])
    C = dist.euclidean(mouth[0], mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

# Initialize the webcam (0 means the default webcam)
cap = cv2.VideoCapture(0)

# Check if the webcam is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()  # Capture frame-by-frame
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert the frame to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Detect yawning using dlib and calculate mouth aspect ratio
    gray_dlib = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_dlib = detector(gray_dlib)
    
    for face in faces_dlib:
        shape = predictor(gray_dlib, face)
        landmarks = [(p.x, p.y) for p in shape.parts()]
        mouth = landmarks[48:68]

        mar = mouth_aspect_ratio(mouth)
        if mar > 0.5:  # Threshold for detecting yawning
            print("Yawning detected!")
            playsound('audio/alarm.mp3')  # Play the alarm sound

    # Draw a rectangle around each face and detect eyes within the face region
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("Webcam Feed", frame)

    # Check if a key is pressed
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):  # Press 'q' to exit the loop
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
