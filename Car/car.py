import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 600
CAR_WIDTH, CAR_HEIGHT = 50, 80
SPEED = 5
MAX_SPEED = 60
ROAD_SPEED = 5
FONT = pygame.font.Font(None, 36)

# Load assets
player_car_image = pygame.image.load("player_car.png")
player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))

road_image = pygame.image.load("road.png")
road_image = pygame.transform.scale(road_image, (WIDTH, HEIGHT))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Simulator")

# Load player's car
player_car = pygame.Rect(WIDTH//2 - CAR_WIDTH//2, HEIGHT - CAR_HEIGHT - 20, CAR_WIDTH, CAR_HEIGHT)

# Road position for looping
y1 = 0
y2 = -HEIGHT

# Game loop
running = True
clock = pygame.time.Clock()
speedometer = 0

while running:
    # Increase speed but limit it to MAX_SPEED
    if speedometer < MAX_SPEED:
        speedometer += 0.1  

    # Adjust road speed based on speedometer
    road_speed = 5 + (speedometer / 3)

    # Move road
    y1 += road_speed
    y2 += road_speed
    if y1 >= HEIGHT:
        y1 = -HEIGHT
    if y2 >= HEIGHT:
        y2 = -HEIGHT

    # Draw road
    screen.blit(road_image, (0, y1))
    screen.blit(road_image, (0, y2))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_car.x > 50:
        player_car.x -= SPEED
    if keys[pygame.K_RIGHT] and player_car.x < WIDTH - CAR_WIDTH - 50:
        player_car.x += SPEED

    # Draw the player's car
    screen.blit(player_car_image, (player_car.x, player_car.y))

    # Display speedometer
    speed_text = FONT.render(f"Speed: {int(speedometer)} km/h", True, (255, 255, 255))
    screen.blit(speed_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
