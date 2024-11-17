import cv2


cap = cv2.VideoCapture(0)
camera_url = "http://192.168.1.4:8080/video"
cap.open(camera_url)

if not cap.isOpened():
    print("Error: Could not connect to the camera.")
    exit()

print("Successfully connected to the camera.")
cap.release()
