import cv2
import dlib
import pygame
import threading
import time
import webbrowser
import requests
from scipy.spatial import distance as dist
from collections import deque

# Initialize Pygame for car simulation and alarm
pygame.init()
pygame.mixer.init()

# Constants for car simulation
WIDTH, HEIGHT = 400, 600
CAR_WIDTH, CAR_HEIGHT = 50, 80
SPEED = 5
MAX_SPEED = 60
MIN_SPEED = 20  # Minimum speed when alarm is ringing
ROAD_SPEED_FACTOR = 0.2  # Multiplier for road movement speed
FONT = pygame.font.Font(None, 36)

# Load assets for car simulation
player_car_image = pygame.image.load("player_car.png")
player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))

road_image = pygame.image.load("road.png")
road_image = pygame.transform.scale(road_image, (WIDTH, HEIGHT))

# Set up the display for car simulation
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Simulator with Drowsiness Detection")

# Load player's car
player_car = pygame.Rect(WIDTH // 2 - CAR_WIDTH // 2, HEIGHT - CAR_HEIGHT - 20, CAR_WIDTH, CAR_HEIGHT)

# Road position for looping
y1 = 0
y2 = -HEIGHT

# Road boundaries (Assuming road width is the same as screen width)
road_left = 50
road_right = WIDTH - CAR_WIDTH - 50

# Game variables
running = True
clock = pygame.time.Clock()

# Shared variables for car speed
car_speed = MAX_SPEED  # Default speed
speed_lock = threading.Lock()  # Lock for thread-safe access to car_speed
alarm_on = False  # Shared variable to track alarm state

# Function to update car speed
def update_car_speed(new_speed):
    global car_speed
    with speed_lock:
        car_speed = new_speed

# Function to run the car simulation
def car_simulation():
    global running, y1, y2, car_speed, alarm_on

    while running:
        screen.fill((0, 0, 0))  # Clear screen

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movement control
        keys = pygame.key.get_pressed()
        
        # Left/Right movement
        if keys[pygame.K_LEFT] and player_car.x > road_left:
            player_car.x -= SPEED
        if keys[pygame.K_RIGHT] and player_car.x < road_right:
            player_car.x += SPEED

        # Adjust car speed based on alarm state
        with speed_lock:
            if alarm_on:
                # Gradually reduce speed to MIN_SPEED
                if car_speed > MIN_SPEED:
                    car_speed -= 1  # Reduce speed gradually
            else:
                # Gradually increase speed to MAX_SPEED
                if car_speed < MAX_SPEED:
                    car_speed += 1  # Increase speed gradually

            road_speed = car_speed * ROAD_SPEED_FACTOR  # Adjust road movement speed

        # Move road
        y1 += road_speed
        y2 += road_speed
        if y1 >= HEIGHT:
            y1 = y2 - HEIGHT
        if y2 >= HEIGHT:
            y2 = y1 - HEIGHT

        # Draw road
        screen.blit(road_image, (0, y1))
        screen.blit(road_image, (0, y2))

        # Draw the player's car
        screen.blit(player_car_image, (player_car.x, player_car.y))

        # Display speedometer
        with speed_lock:
            speed_text = FONT.render(f"Speed: {int(car_speed)} km/h", True, (255, 255, 255))
        screen.blit(speed_text, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

# Drowsiness detection code from main.py
# Load dlib predictor for facial landmarks
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()

# Twilio Flask Server URL
TWILIO_SERVER_URL = "http://127.0.0.1:5000/send_alert"

# Function to calculate the Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Function to calculate the Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])
    B = dist.euclidean(mouth[4], mouth[8])
    C = dist.euclidean(mouth[0], mouth[6])
    return (A + B) / (2.0 * C)

# Function to send SMS
def send_sms():
    global sms_sent
    if not sms_sent:
        try:
            data = {"alert_type": "🚨 Drowsiness detected! Emergency Alert!"}
            webbrowser.open(r'C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\loc.html')
            time.sleep(5)  
            response = requests.post(TWILIO_SERVER_URL, json=data)
            print(f"📩 Sending SMS: {data}")
            print(f"✅ SMS Sent! Response: {response.json()}")
            sms_sent = True  
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")

# Function to send "Driver is awake" message
def send_awake_message():
    try:
        response = requests.post("http://127.0.0.1:5000/send_awake_alert", json={})  
        print("📩 Sending Awake Message...")
        print(f"✅ Awake Message Sent! Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error sending awake message: {e}")

# Function to play alarm sound in a separate thread
def play_alarm():
    global alarm_on, alarm_triggered_time, sms_sent, waiting_for_reset

    alarm_path = r'C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\audio\alarm.mp3'
    pygame.mixer.music.load(alarm_path)

    alarm_triggered_time = time.time()
    waiting_for_reset = True  

    while alarm_on:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        
        # Check if 5 seconds have passed since the alarm was triggered
        if time.time() - alarm_triggered_time >= 5 and not sms_sent:
            send_sms()  
            sms_sent = True  

            # Switch to alarm2.mp3 after message is sent
            pygame.mixer.music.stop()
            new_alarm_path = r'C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\audio\alarm2.mp3'
            pygame.mixer.music.load(new_alarm_path)
            pygame.mixer.music.play()
        
        time.sleep(1)

# Thresholds
EAR_THRESHOLD = 0.22
MAR_THRESHOLD = 0.50  
EYE_CLOSED_TIME_THRESHOLD = 2.0  
DETECTION_GAP_SECONDS = 5  
COOLDOWN_SECONDS = 60  
YAWN_HOLD_TIME = 1  # Mouth must stay open for 2 seconds to count as a yawn

# Initialize variables
eye_closed_start_time = None
sms_sent = False
waiting_for_reset = False
detection_times = deque(maxlen=2)  
yawn_start_time = None  # Initialize yawn_start_time globally
face_missing_start_time = None  # Initialize face_missing_start_time globally
face_missing_threshold = 3  # Send SMS if face is not detected for 3 seconds

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Function to run drowsiness detection
def drowsiness_detection():
    global alarm_on, eye_closed_start_time, sms_sent, waiting_for_reset, yawn_start_time, face_missing_start_time

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Pause detection until 'O' is pressed
        if waiting_for_reset:
            cv2.putText(frame, "Press 'O' to reset detection", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Drowsiness Detection", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('o'):
                waiting_for_reset = False  
                alarm_on = False  
                sms_sent = False  
                pygame.mixer.music.stop()
                print("✅ System Reset. Ready for new detection.")
            continue  

        # Detect faces
        faces = detector(gray)
        
        # Ensure a face is detected before checking for drowsiness
        if len(faces) == 0:
            eye_closed_start_time = None  # Reset eye closure time when face disappears
            sms_sent = False  # Reset SMS flag

            # Start face missing timer
            if face_missing_start_time is None:
                face_missing_start_time = time.time()  # Start timer when face disappears
            
            face_missing_duration = time.time() - face_missing_start_time
            
            # Display face missing timer on-screen
            cv2.putText(frame, f"Face not detected: {face_missing_duration:.1f}s", (10, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # If face is missing for more than 3 seconds, trigger alarm and send SMS
            if face_missing_duration >= face_missing_threshold:
                if not alarm_on:  # Play alarm only if it's not already playing
                    alarm_on = True
                    pygame.mixer.music.load(r'C:\Users\EDUMALL\OneDrive\Desktop\DrowsinessDetection\audio\alarm.mp3')
                    pygame.mixer.music.play(-1)  # Play alarm in a loop
                    print("🚨 Alarm triggered: Face missing for more than 3 seconds!")
                
                send_sms()  # Send SMS alert
                face_missing_start_time = None  # Reset timer after sending SMS

        else:
            face_missing_start_time = None  # Reset timer if face is detected
            if alarm_on:  # Stop alarm if face is detected again
                alarm_on = False
                pygame.mixer.music.stop()
                print("✅ Alarm stopped: Face detected.")

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
                mar = mouth_aspect_ratio(mouth)  # Restore MAR Calculation

                # Eye Closure Detection
                if ear < EAR_THRESHOLD:
                    if eye_closed_start_time is None:
                        eye_closed_start_time = time.time()
                    elif time.time() - eye_closed_start_time >= EYE_CLOSED_TIME_THRESHOLD:
                        print("Eyes closed for too long! Playing alarm...")

                        if not alarm_on:
                            alarm_on = True
                            threading.Thread(target=play_alarm, daemon=True).start()

                        current_time = time.time()
                        
                        # Ensure a 5-second gap before adding to detection queue
                        if not detection_times or (current_time - detection_times[-1] >= DETECTION_GAP_SECONDS):
                            detection_times.append(current_time)
                            print(f"⚠️ Drowsiness detected! Total detections: {len(detection_times)}")
                            print(f"Detection Times: {detection_times}")

                        # If two detections happen within 1 minute, send SMS
                        if len(detection_times) == 2:
                            time_diff = detection_times[-1] - detection_times[0]
                            print(f"Time difference between detections: {time_diff:.2f} seconds")
                            if time_diff <= 60:  
                                send_sms()
                                detection_times.clear()  

                else:
                    eye_closed_start_time = None
                    if alarm_on:  # Stop alarm if eyes are open again
                        alarm_on = False
                        pygame.mixer.music.stop()
                        print("✅ Alarm stopped: Eyes open.")

                # Yawn Detection Based on MAR
                if mar > MAR_THRESHOLD:
                    if yawn_start_time is None:
                        yawn_start_time = time.time()
                    elif time.time() - yawn_start_time >= YAWN_HOLD_TIME:
                        print("Yawning detected! Playing alarm...")
                        if not alarm_on:
                            alarm_on = True
                            threading.Thread(target=play_alarm, daemon=True).start()

                        # Add detection time
                        current_time = time.time()
                        if not detection_times or (current_time - detection_times[-1] >= DETECTION_GAP_SECONDS):
                            detection_times.append(current_time)
                            print(f"⚠️ Drowsiness detected due to yawning! Total detections: {len(detection_times)}")

                        # Send SMS if two detections happen within 60 seconds
                        if len(detection_times) == 2 and (detection_times[-1] - detection_times[0] <= 60):
                            send_sms()
                            detection_times.clear()

                else:
                    yawn_start_time = None  # Reset if mouth closes before YAWN_HOLD_TIME

                # Draw face landmarks and metrics on the frame
                for (x, y) in landmarks:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                # EAR, MAR, and Eye Closure Duration Display
                eye_close_time = time.time() - eye_closed_start_time if eye_closed_start_time else 0
                cv2.putText(frame, f"EAR: {ear:.2f} MAR: {mar:.2f} Eye Closed: {eye_close_time:.1f}s",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Display the frame
        cv2.imshow("Drowsiness Detection", frame)

        # Exit condition
        key = cv2.waitKey(1) & 0xFF  # Wait for key press
        
        if key == ord('q'):  
            break  # Exit the loop if 'q' is pressed

        elif key == ord('o'):  
            waiting_for_reset = False  
            alarm_on = False  
            sms_sent = False  
            pygame.mixer.music.stop()
            print("✅ System Reset. Ready for new detection.")
        elif key == ord('l'):  # Send "Driver is awake" message
            send_awake_message()

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# Start the car simulation in a separate thread
car_thread = threading.Thread(target=car_simulation)
car_thread.start()

# Start the drowsiness detection in the main thread
drowsiness_detection()

# Wait for the car simulation thread to finish
car_thread.join()