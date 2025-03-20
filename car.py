import pygame
import threading


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 600
CAR_WIDTH, CAR_HEIGHT = 50, 80
SPEED = 5
MAX_SPEED = 60
MIN_SPEED = 10  # Lower limit when drowsiness is detected
ROAD_SPEED_FACTOR = 0.2  # Multiplier for road movement speed
FONT = pygame.font.Font(None, 36)

# Shared variables
car_speed = MAX_SPEED  # Default speed
speed_lock = threading.Lock()  # Lock for thread-safe access to car_speed

# Load assets
player_car_image = pygame.image.load("player_car.png")
player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))

road_image = pygame.image.load("road.png")
road_image = pygame.transform.scale(road_image, (WIDTH, HEIGHT))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Simulator")

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

def update_car_speed(new_speed):
    global car_speed
    with speed_lock:
        car_speed = new_speed

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

    # Adjust road speed based on car_speed
    with speed_lock:
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