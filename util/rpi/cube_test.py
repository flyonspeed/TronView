import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import board
import busio
from adafruit_bno055 import BNO055_I2C
import math

# Initialize the IMU
i2c = busio.I2C(board.SCL, board.SDA)
sensor = BNO055_I2C(i2c)

# Initialize pygame
pygame.init()

# Set display
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Cube with IMU Control (Yaw, Pitch, Roll Mapped) + Fixed Axis Arrows")

# Set up OpenGL perspective
gluPerspective(45, (800 / 600), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)  # Move the cube back
glRotatef(0, 0, 0, 0)  # Start with no rotation

# Initial rotation values
x_rotation = 0
y_rotation = 0
z_rotation = 0

# IMU offsets for zeroing out
roll_offset, pitch_offset, yaw_offset = 0, 0, 0

# Angle limits
PITCH_LIMIT = 45
ROLL_LIMIT = 30

# Initialize pygame clock
clock = pygame.time.Clock()
clock_tick_value = 10  # Initial clock tick (frame rate)

# Vertices of the cube
vertices = [
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),  # Back face
    (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)       # Front face
]

# Edges connecting the vertices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back face edges
    (4, 5), (5, 7), (7, 6), (6, 4),  # Front face edges
    (0, 4), (1, 5), (2, 7), (3, 6)   # Connecting edges
]

# Filtering threshold values (adjustable)
threshold_value = 5.0   # Initial threshold value in degrees
filtering_enabled = True  # Filtering is enabled by default

# Store previous values to compare jumps
prev_roll, prev_pitch, prev_yaw = 0.0, 0.0, 0.0

# Filter counters
roll_filter_counter = 0
pitch_filter_counter = 0
yaw_filter_counter = 0

# Function to filter roll data
def filter_roll(roll):
    global prev_roll, roll_filter_counter
    if abs(roll - prev_roll) > threshold_value:
        print(f"Large jump detected in Roll: {roll}, replacing with previous value {prev_roll}")
        roll = prev_roll
        roll_filter_counter += 1
    else:
        prev_roll = roll
    return roll

# Function to filter pitch data
def filter_pitch(pitch):
    global prev_pitch, pitch_filter_counter
    if abs(pitch - prev_pitch) > threshold_value:
        print(f"Large jump detected in Pitch: {pitch}, replacing with previous value {prev_pitch}")
        pitch = prev_pitch
        pitch_filter_counter += 1
    else:
        prev_pitch = pitch
    return pitch

# Function to filter yaw data
def filter_yaw(yaw):
    global prev_yaw, yaw_filter_counter
    if abs(yaw - prev_yaw) > threshold_value:
        print(f"Large jump detected in Yaw: {yaw}, replacing with previous value {prev_yaw}")
        yaw = prev_yaw
        yaw_filter_counter += 1
    else:
        prev_yaw = yaw
    return yaw

# Function to draw the cube with transparent sides
def draw_cube():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1, 1, 1, 0.1)  # Very light transparent white

    glBegin(GL_QUADS)
    for surface in [[0, 1, 2, 3], [4, 5, 7, 6], [0, 4, 6, 3], [1, 5, 7, 2], [3, 2, 7, 6]]:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

    glColor3f(0, 0, 0)  # Black edges
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Function to draw the X, Y, and Z axes with arrows
def draw_axes():
    # Draw X-axis (Red)
    glColor3f(1, 0, 0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(2, 0, 0)
    glEnd()
    glPushMatrix()
    glTranslatef(2, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.1, 0.05, 0)
    glVertex3f(0.1, -0.05, 0)
    glVertex3f(0.2, 0, 0)
    glEnd()
    glPopMatrix()

    # Draw Y-axis (Green)
    glColor3f(0, 1, 0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 2, 0)
    glEnd()
    glPushMatrix()
    glTranslatef(0, 2, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.05, 0.1, 0)
    glVertex3f(-0.05, 0.1, 0)
    glVertex3f(0, 0.2, 0)
    glEnd()
    glPopMatrix()

    # Draw Z-axis (Blue)
    glColor3f(0, 0, 1)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 2)
    glEnd()
    glPushMatrix()
    glTranslatef(0, 0, 2)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.05, 0, 0.1)
    glVertex3f(-0.05, 0, 0.1)
    glVertex3f(0, 0, 0.2)
    glEnd()
    glPopMatrix()

# Function to convert quaternion to Euler angles (roll, pitch, yaw)
def quaternion_to_euler(w, x, y, z):
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    roll = math.degrees(roll)

    pitch_raw = 2.0 * (w * y - z * x)
    pitch = math.asin(max(-1.0, min(1.0, pitch_raw)))  # Clamp value within -1 and 1
    pitch = math.degrees(pitch)

    yaw = -math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    yaw = math.degrees(yaw)

    if yaw > 180:
        yaw -= 360
    elif yaw < -180:
        yaw += 360

    return roll, pitch, yaw

# Function to render text as a surface
def render_text(text, font):
    text_surface = font.render(text, True, (0, 0, 0))  # Black text
    return pygame.image.tostring(text_surface, "RGBA", True), text_surface.get_size()

# Function to display text on the OpenGL screen
def display_text(text, x, y, font):
    text_data, text_size = render_text(text, font)
    glWindowPos2d(x, y)
    glDrawPixels(text_size[0], text_size[1], GL_RGBA, GL_UNSIGNED_BYTE, text_data)

# Main loop
running = True
font = pygame.font.Font(None, 36)  # Font for on-screen text

while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Reset the IMU offsets based on the current orientation
                    quat = sensor.quaternion
                    if quat and None not in quat:
                        roll_offset, pitch_offset, yaw_offset = quaternion_to_euler(*quat)
                        print("New zero reference set")
                elif event.key == pygame.K_t:
                    filtering_enabled = not filtering_enabled  # Toggle filtering
                    print(f"Filtering {'enabled' if filtering_enabled else 'disabled'}")
                elif event.key == pygame.K_LEFT:
                    threshold_value -= 0.1  # Decrease threshold value
                elif event.key == pygame.K_RIGHT:
                    threshold_value += 0.1  # Increase threshold value
                elif event.key == pygame.K_UP:
                    clock_tick_value += 1  # Increase clock tick value (frame rate)
                elif event.key == pygame.K_DOWN:
                    clock_tick_value = max(1, clock_tick_value - 1)  # Decrease clock tick value (min 1)

        # Get IMU quaternion and convert to Euler angles
        quat = sensor.quaternion
        if quat and None not in quat:
            # Convert quaternion to Euler angles (roll, pitch, yaw)
            roll, pitch, yaw = quaternion_to_euler(*quat)

            # Apply offsets for zeroing out
            roll -= roll_offset
            pitch -= pitch_offset
            yaw -= yaw_offset

            # Wrap yaw to within -180 to +180 after applying offsets
            if yaw > 180:
                yaw -= 360
            elif yaw < -180:
                yaw += 360

            # Filter each axis
            roll = filter_roll(roll)
            pitch = filter_pitch(pitch)
            yaw = filter_yaw(yaw)

            # Update cube rotation values:
            z_rotation = roll  # Roll rotates around the Z-axis
            y_rotation = yaw   # Yaw rotates around the Y-axis
            x_rotation = -pitch  # Pitch rotates around the X-axis, reverse the input

            # Debug logging
            sys_cal, gyro_cal, accel_cal, mag_cal = sensor.calibration_status
            print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}, System Cal: {sys_cal}, Gyro Cal: {gyro_cal}, Accel Cal: {accel_cal}, Mag Cal: {mag_cal}")

        # Clear the screen and depth buffer
        glClearColor(1, 1, 1, 1)  # Set background to white
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Apply IMU-based rotations
        glPushMatrix()
        glRotatef(z_rotation, 0, 0, 1)  # Rotate around Z-axis (Roll)
        glRotatef(x_rotation, 1, 0, 0)  # Rotate around X-axis (Pitch)
        glRotatef(y_rotation, 0, 1, 0)  # Rotate around Y-axis (Yaw)

        # Draw the cube and fixed axes
        draw_cube()
        draw_axes()

        # Restore the original matrix
        glPopMatrix()

        # Display the current X, Y, Z degrees used to rotate the cube at the top of the screen
        display_text(f"X (Roll): {z_rotation:.1f}°", 20, 550, font)
        display_text(f"Y (Pitch): {x_rotation:.1f}°", 300, 550, font)
        display_text(f"Z (Yaw): {y_rotation:.1f}°", 600, 550, font)

        # Display the filter counters at the bottom
        display_text(f"Roll Filter Count: {roll_filter_counter}", 20, 50, font)
        display_text(f"Pitch Filter Count: {pitch_filter_counter}", 20, 80, font)
        display_text(f"Yaw Filter Count: {yaw_filter_counter}", 20, 110, font)

        # Update the display
        pygame.display.flip()
        clock.tick(clock_tick_value)  # Update based on clock tick value

    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        break

# Quit pygame
pygame.quit()
