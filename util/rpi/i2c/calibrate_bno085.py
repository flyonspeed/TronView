# calibrate_bno085.py

import time
import math
import board
import busio
import pygame
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
from digitalio import DigitalInOut

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('BNO085 Calibration')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

i2c = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D5)
bno = BNO08X_I2C(i2c, reset=reset_pin, debug=False)

bno.begin_calibration()

bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)
bno.enable_feature(adafruit_bno08x.BNO_REPORT_GAME_ROTATION_VECTOR)
#bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)


def quaternion_to_euler(x, y, z, w):
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    roll = round(math.degrees(roll), 3)

    pitch_raw = 2.0 * (w * y - z * x)
    pitch = math.asin(max(-1.0, min(1.0, pitch_raw)))
    pitch = round(math.degrees(pitch), 3)

    yaw = -math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    yaw = round(math.degrees(yaw), 3)

    if yaw > 180:
        yaw -= 360
    elif yaw < -180:
        yaw += 360

    return roll, pitch, yaw

def draw_text(text, position, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

calibration_good_at = None
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and calibration_good_at and (time.monotonic() - calibration_good_at > 5.0):
                bno.save_calibration_data()
                running = False

    screen.fill(BLACK)
    
    # Get sensor data
    mag_x, mag_y, mag_z = bno.magnetic
    game_quat_i, game_quat_j, game_quat_k, game_quat_real = bno.game_quaternion
    calibration_status = bno.calibration_status
    
    # Calculate Euler angles
    roll, pitch, yaw = quaternion_to_euler(game_quat_i, game_quat_j, game_quat_k, game_quat_real)
    
    # Display magnetometer data
    draw_text("Magnetometer (uT):", (20, 20))
    draw_text(f"X: {mag_x:0.6f}", (20, 60))
    draw_text(f"Y: {mag_y:0.6f}", (20, 100))
    draw_text(f"Z: {mag_z:0.6f}", (20, 140))
    
    # Display quaternion data
    draw_text("Game Rotation Vector Quaternion:", (20, 200))
    draw_text(f"I: {game_quat_i:0.6f}", (20, 240))
    draw_text(f"J: {game_quat_j:0.6f}", (20, 280))
    draw_text(f"K: {game_quat_k:0.6f}", (20, 320))
    draw_text(f"Real: {game_quat_real:0.6f}", (20, 360))
    
    # Display Euler angles
    draw_text("Euler Angles (degrees):", (20, 420))
    draw_text(f"Roll: {roll:0.3f}", (20, 460))
    draw_text(f"Pitch: {pitch:0.3f}", (20, 500))
    draw_text(f"Yaw: {yaw:0.3f}", (20, 540))
    
    # Display calibration status
    status_color = RED if calibration_status < 2 else YELLOW if calibration_status == 2 else GREEN
    draw_text(f"Calibration Status: {adafruit_bno08x.REPORT_ACCURACY_STATUS[calibration_status]} ({calibration_status})",
              (400, 20), status_color)
    
    if not calibration_good_at and calibration_status >= 2:
        calibration_good_at = time.monotonic()
    
    if calibration_good_at and (time.monotonic() - calibration_good_at > 5.0):
        draw_text("Press 'S' to save calibration", (400, 60), GREEN)
    
    pygame.display.flip()
    clock.tick(10)  # 10 FPS to match the sensor update rate

pygame.quit()
print("Calibration complete")