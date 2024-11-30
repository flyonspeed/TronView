#!/usr/bin/env python

#################################################
# Module: Hud Horizon
# Topher 2021.
# Adapted from F18 HUD Screen code by Brian Chesteen.

from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
import pygame
import math
from lib.common import shared
from lib.common.dataship.dataship import Dataship


class horizon_v2(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "HUD Horizon V2"  # set name
        self.flight_path_color = (255, 0, 255)  # Default color, can be changed via settings
        self.show_targets = True
        self.target_distance_threshold = 10
        self.fov_x = hud_utils.readConfigInt("HUD", "fov_x", 13.942) # Field of View X in degrees
        self.fov_y = hud_utils.readConfigInt("HUD", "fov_y", 13.942) # Field of View y in degrees
        self.target_positions = {}  # Store smoothed positions for each target
        self.target_smoothing = 0.2  # Default smoothing factor (0-1), lower = smoother

        # Add new settings for horizon line
        self.horizon_line_color = (255, 165, 0)  # Default default to orange
        self.horizon_line_thickness = 4  # Default thickness
        self.horizon_line_length = 0.8  # Percentage of screen width
       
        self.source_imu_index_name = ""  # name of the primary imu. used to the aircraft heading, pitch, roll
        self.source_imu_index = 0  # index of the primary imu.
        self.source_imu_index2_name = "NONE"  # name of the secondary imu. (optional)
        self.source_imu_index2 = None  # index of the secondary imu. (optional)
        self.camera_head_imu = None  # IMU object for camera head. Human Head view.
               

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = pygamescreen.get_width() # default width
        if height is None:
            height = 640 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        target_font_size = hud_utils.readConfigInt("HUD", "target_font_size", 12)

        # fonts
        self.font = pygame.font.SysFont(None, 30)
        self.font_target = pygame.font.SysFont("monospace", target_font_size, bold=False)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.ahrs_bg_width = self.surface.get_width()
        self.ahrs_bg_height = self.surface.get_height()
        self.ahrs_bg_center = (self.ahrs_bg_width / 2 + 160, self.ahrs_bg_height / 2)
        self.MainColor = (0, 255, 0)  # main color of hud graphics
        self.line_thickness = hud_utils.readConfigInt("HUD", "line_thickness", 2)
        self.ahrs_line_deg = hud_utils.readConfigInt("HUD", "vertical_degrees", 5)
        self.pxy_div = hud_utils.readConfigInt("HUD", "vertical_pixels_per_degree", 30)  # Y axis number of pixels per degree divisor
        self.y_offset = hud_utils.readConfigInt("HUD", "Horizon_Offset", 0)  #  Horizon/Waterline Pixel Offset from HUD Center Neg Numb moves Up, Default=0

        self.line_mode = hud_utils.readConfigInt("HUD", "line_mode", 1)
        self.caged_mode = 1 # default on
        self.center_circle_mode = hud_utils.readConfigInt("HUD", "center_circle", 4)

        # sampling for flight path.
        self.readings = []  # Setup moving averages to smooth a bit
        self.max_samples = 30 # FPM smoothing
        self.readings1 = []  # Setup moving averages to smooth a bit
        self.max_samples1 = 30 # Caged FPM smoothing

        self.x_offset = 0
        self.xCenter = self.width // 2
        self.yCenter = self.height // 2


    #############################################
    ## Function: generateHudReferenceLineArray
    ## create array of horz lines based on pitch, roll, etc.
    def generateHudReferenceLineArray(
        self,screen_width, screen_height, ahrs_center, pxy_div, pitch=0, roll=0, deg_ref=0, line_mode=1,
    ):

        if line_mode == 1:
            if deg_ref == 0:
                length = screen_width * 0.9
            elif (deg_ref % 10) == 0:
                length = screen_width * 0.49
            elif (deg_ref % 5) == 0:
                length = screen_width * 0.25
            else:
                length = screen_width * 0.10
        else:
            if deg_ref == 0:
                length = screen_width * 0.5
            elif (deg_ref % 10) == 0:
                length = screen_width * 0.25
            elif (deg_ref % 5) == 0:
                length = screen_width * 0.11
            else:
                length = screen_width * 0.5

        ahrs_center_x, ahrs_center_y = ahrs_center
        px_per_deg_y = screen_height / pxy_div
        pitch_offset = px_per_deg_y * (-pitch + deg_ref)

        center_x = ahrs_center_x - (pitch_offset * math.cos(math.radians(90 - roll)))
        center_y = ahrs_center_y - (pitch_offset * math.sin(math.radians(90 - roll)))

        x_len = length * math.cos(math.radians(roll))
        y_len = length * math.sin(math.radians(roll))

        start_x = center_x - (x_len / 2)
        end_x = center_x + (x_len / 2)
        start_y = center_y + (y_len / 2)
        end_y = center_y - (y_len / 2)

        xRot = center_x + math.cos(math.radians(-10)) * (start_x - center_x) - math.sin(math.radians(-10)) * (start_y - center_y)
        yRot = center_y + math.sin(math.radians(-10)) * (start_x - center_x) + math.cos(math.radians(-10)) * (start_y - center_y)
        xRot1 = center_x + math.cos(math.radians(+10)) * (end_x - center_x) - math.sin(math.radians(+10)) * (end_y - center_y)
        yRot1 = center_y + math.sin(math.radians(+10)) * (end_x - center_x) + math.cos(math.radians(+10)) * (end_y - center_y)

        xRot2 = center_x + math.cos(math.radians(-10)) * (end_x - center_x) - math.sin(math.radians(-10)) * (end_y - center_y)
        yRot2 = center_y + math.sin(math.radians(-10)) * (end_x - center_x) + math.cos(math.radians(-10)) * (end_y - center_y)
        xRot3 = center_x + math.cos(math.radians(+10)) * (start_x - center_x) - math.sin(math.radians(+10)) * (start_y - center_y)
        yRot3 = center_y + math.sin(math.radians(+10)) * (start_x - center_x) + math.cos(math.radians(+10)) * (start_y - center_y)

        return [[xRot, yRot],[start_x, start_y],[end_x, end_y],[xRot1, yRot1],[xRot2, yRot2],[xRot3, yRot3]]


    #############################################
    ## Function: draw_dashed_line
    def draw_dashed_line(self,surf, color, start_pos, end_pos, width=1, dash_length=10):
        origin = Point(start_pos)
        target = Point(end_pos)
        displacement = target - origin
        length = len(displacement)
        slope = Point((displacement.x / length, displacement.y/length))

        for index in range(0, length // dash_length, 2):
            start = origin + (slope * index * dash_length)
            end = origin + (slope * (index + 1) * dash_length)
            pygame.draw.line(surf, color, start.get(), end.get(), width)

    def draw_circle(self,surface,color,center,radius,width):
        pygame.draw.circle(
            surface,
            color,
            (int(center[0]),int(center[1])),
            radius,
            width,
        )

    #############################################
    ## Function draw horz lines
    def draw_horz_lines(
        self,
        width,
        height,
        ahrs_center,
        ahrs_line_deg,
        aircraft,
        color,
        line_thickness,
        line_mode,
        font,
        pxy_div,
        pos
    ):
        # Calculate camera yaw offset relative to aircraft heading
        camera_yaw_offset = 0
        if self.camera_head_imu is not None:
            camera_yaw_offset = ((self.camera_head_imu.yaw - aircraft.mag_head + 180) % 360) - 180
        
        # Calculate pixel offset based on yaw difference
        pixels_per_degree = width / self.fov_x
        x_offset = -camera_yaw_offset * pixels_per_degree
        
        # Adjust center point based on camera yaw
        center_x = width // 2 + x_offset
        center_y = height // 2
        adjusted_center = (center_x, center_y)

        # Draw lines centered on the screen
        for l in range(-60, 61, ahrs_line_deg):
            line_coords = self.generateHudReferenceLineArray(
                width,
                height,
                adjusted_center,
                pxy_div,
                pitch=aircraft.pitch,
                roll=aircraft.roll,
                deg_ref=l,
                line_mode=line_mode,
            )

            # Check if any part of the line is within the visible area
            # Convert line endpoints to screen-relative coordinates
            screen_x1 = line_coords[1][0] - x_offset
            screen_x2 = line_coords[2][0] - x_offset
            
            # Calculate visible bounds based on FOV
            left_bound = (width // 2) - (width // 2)  # 0
            right_bound = (width // 2) + (width // 2)  # width
            
            # Skip if line is completely outside visible area
            if (screen_x1 < left_bound and screen_x2 < left_bound) or \
               (screen_x1 > right_bound and screen_x2 > right_bound):
                continue

            if abs(l) > 45:
                if l % 5 == 0 and l % 10 != 0:
                    continue

            # Draw lines
            if l < 0:
                self.draw_dashed_line(
                    self.surface,
                    color,
                    line_coords[1],
                    line_coords[2],
                    width=line_thickness,
                    dash_length=5,
                )
                # Only draw end markers if they're within view
                if left_bound <= screen_x2 <= right_bound:
                    pygame.draw.lines(
                        self.surface,
                        color,
                        False,
                        (line_coords[2], line_coords[4]),
                        line_thickness
                    )
                if left_bound <= screen_x1 <= right_bound:
                    pygame.draw.lines(
                        self.surface,
                        color,
                        False,
                        (line_coords[1], line_coords[5]),
                        line_thickness
                    )
            else:
                visible_points = []
                for point in [line_coords[0], line_coords[1], line_coords[2], line_coords[3]]:
                    screen_x = point[0] - x_offset
                    if left_bound <= screen_x <= right_bound:
                        visible_points.append(point)
                
                if len(visible_points) >= 2:
                    pygame.draw.lines(
                        self.surface,
                        color,
                        False,
                        visible_points,
                        line_thickness
                    )

            # Draw degree text if within view
            if l != 0 and l % 5 == 0:
                text = font.render(str(l), False, color)
                text_width, text_height = text.get_size()
                text_x = int(line_coords[1][0]) - (text_width + int(width / 100))
                text_screen_x = text_x - x_offset
                
                if left_bound <= text_screen_x <= right_bound:
                    self.surface.blit(text, (text_x, int(line_coords[1][1]) - text_height / 2))


    def draw_center(self,smartdisplay, x_offset, y_offset):
        '''
        Draw the center circle.
        '''
        center_x = x_offset + self.width // 2
        center_y = y_offset + self.height // 2

        if self.center_circle_mode == 1:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                3,
                1,
            )
        elif self.center_circle_mode == 2:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                15,
                1,
            )
        # draw center + Gun Cross
        elif self.center_circle_mode == 3:
            pygame.draw.circle(
                self.surface,
                self.MainColor,
                (center_x, center_y),
                50,
                1,
            )
        # draw water line center.
        elif self.center_circle_mode == 5:
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 10, center_y + 20],
                [center_x, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 10, center_y + 20],
                [center_x - 20, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x - 35, center_y],
                [center_x - 20, center_y],
                3,
            )
            pygame.draw.line(
                self.surface,
                self.MainColor,
                [center_x + 10, center_y + 20],
                [center_x, center_y],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [center_x + 10, center_y + 20],
                [center_x + 20, center_y],
                3,
            )
            pygame.draw.line(
                smartdisplay.pygamescreen,
                self.MainColor,
                [center_x + 35, center_y],
                [center_x + 20, center_y],
                3,
            )

    def draw_flight_path(self,aircraft,smartdisplay, x_offset, y_offset):
        '''
        Draw the flight path indicator.
        '''
        def mean(nums):
            return int(sum(nums)) / max(len(nums), 1)

        # flight path indicator  Default Caged Mode
        if self.caged_mode == 1:
            fpv_x = 0.0
        else:  #  changed the  "- (aircraft.turn_rate * 5" to a "+ (aircraft.turn_rate * 5" 
            fpv_x = ((((aircraft.mag_head - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  + (
                aircraft.turn_rate * 5
            )
            self.readings.append(fpv_x)
            fpv_x = mean(self.readings)  # Moving average to smooth a bit
            if len(self.readings) == self.max_samples:
                self.readings.pop(0)
        
        use_heading = aircraft.mag_head
        if aircraft.mag_head is None and aircraft.gndtrack is not None:
            use_heading = aircraft.gndtrack
        gfpv_x = ((((use_heading - aircraft.gndtrack) + 180) % 360) - 180) * 1.5  + (
            aircraft.turn_rate * 5
        )
        self.readings1.append(gfpv_x)
        gfpv_x = mean(self.readings1)  # Moving average to smooth a bit
        if len(self.readings1) == self.max_samples1:
            self.readings1.pop(0)

        center_x = self.width // 2
        center_y = self.height // 2

        self.draw_circle(
            self.surface,
            self.flight_path_color,  # Use flight_path_color instead of hardcoded color
            (
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2),
            ),
            15,
            4,
        )
        
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5) - 15,
                center_y - (aircraft.vsi / 2),
            ],
            [
                center_x - (int(fpv_x) * 5) - 30,
                center_y - (aircraft.vsi / 2),
            ],
            2,
        )
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5) + 15,
                center_y - (aircraft.vsi / 2),
            ],
            [
                center_x - (int(fpv_x) * 5) + 30,
                center_y - (aircraft.vsi / 2),
            ],
            2,
        )
        pygame.draw.line(
            self.surface,
            self.flight_path_color,  # Use flight_path_color
            [
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2) - 15,
            ],
            [
                center_x - (int(fpv_x) * 5),
                center_y - (aircraft.vsi / 2) - 30,
            ],
            2,
        )
        if self.caged_mode == 1:
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5) - 15,
                    center_y - (aircraft.vsi / 2),
                ],
                [
                    center_x - (int(gfpv_x) * 5) - 30,
                    center_y - (aircraft.vsi / 2),
                ],
                2,
            )
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5) + 15,
                    center_y - (aircraft.vsi / 2),
                ],
                [
                    center_x - (int(gfpv_x) * 5) + 30,
                    center_y - (aircraft.vsi / 2),
                ],
                2,
            )
            pygame.draw.line(
                self.surface,
                self.flight_path_color,  # Use flight_path_color
                [
                    center_x - (int(gfpv_x) * 5),
                    center_y - (aircraft.vsi / 2) - 15,
                ],
                [
                    center_x - (int(gfpv_x) * 5),
                    center_y - (aircraft.vsi / 2) - 30,
                ],
                2,
            )

            aircraft.flightPathMarker_x = fpv_x # save to aircraft object for other modules to use.


    # called every redraw for this screen module
    def draw(self, aircraft, smartdisplay, pos=(0, 0)):
        '''
        Draw method to draw all the elements of the horizon.
        '''
        x, y = pos
        
        # Clear the surface before drawing
        self.surface.fill((0, 0, 0, 0))

        if aircraft.roll is None or aircraft.pitch is None:
            # draw a red X on the screen.
            pygame.draw.line(self.surface, (255,0,0), (0,0), (self.width,self.height), 4)
            pygame.draw.line(self.surface, (255,0,0), (self.width,0), (0,self.height), 4)
        else:
            # Calculate camera head offsets if present
            camera_pitch = 0
            camera_roll = 0
            camera_yaw = 0
            
            if self.camera_head_imu is not None:
                camera_pitch = -self.camera_head_imu.pitch
                camera_roll = self.camera_head_imu.roll
                camera_yaw = ((self.camera_head_imu.yaw - aircraft.mag_head + 180) % 360) - 180

                # Draw the horizon line from camera perspective
                self.draw_horizon_line(aircraft, camera_yaw, camera_pitch, camera_roll)

                # Apply camera offsets to aircraft attitude for the rest of the display
                adjusted_pitch = aircraft.pitch - camera_pitch
                adjusted_roll = aircraft.roll - camera_roll
            else:
                adjusted_pitch = aircraft.pitch
                adjusted_roll = aircraft.roll   

            # Draw horizon lines with adjusted angles
            self.draw_horz_lines(
                self.width,
                self.height,
                ((self.width // 2), self.height // 2),
                self.ahrs_line_deg,
                type('AdjustedAircraft', (), {
                    'pitch': adjusted_pitch,
                    'roll': adjusted_roll,
                    'mag_head': aircraft.mag_head,
                    'turn_rate': aircraft.turn_rate,
                    'vsi': aircraft.vsi,
                    'traffic': aircraft.traffic,
                    'gndtrack': aircraft.gndtrack
                }),
                self.MainColor,
                self.line_thickness,
                self.line_mode,
                self.font,
                self.pxy_div,
                (x, y)
            )

            # Only show targets if camera is roughly aligned with aircraft heading
            if self.show_targets and abs(camera_yaw) < 45:
                list(map(lambda t: self.draw_target(t, aircraft), 
                        filter(lambda t: t.dist is not None and t.dist < self.target_distance_threshold and t.brng is not None, 
                                aircraft.traffic.targets)))

            # Draw center and flight path
            self.draw_center(smartdisplay, x, y)
            if abs(camera_yaw) < 45:  # Only show flight path when looking forward
                self.draw_flight_path(aircraft, smartdisplay, x, y)

        # Blit the entire surface to the screen at the specified position
        smartdisplay.pygamescreen.blit(self.surface, pos)

    def draw_target(self, t, aircraft):
        '''
        Draw a target on the screen.
        '''
        heading_to_use = aircraft.mag_head
        # if aircraft.mag_head is None then check if aircraft.gndtrack is not None
        if aircraft.mag_head is None and aircraft.gndtrack is not None:
            heading_to_use = aircraft.gndtrack
        else:
            # else can't use either so don't draw it.
            return

        # Calculate the relative bearing to the target
        relative_bearing = (t.brng - heading_to_use + 180) % 360 - 180

        # Check if the target is within the field of view
        if abs(relative_bearing) > self.fov_x / 2:
            return  # Target is outside the field of view, don't draw it

        if t.altDiff is not None and aircraft.pitch is not None and aircraft.roll is not None:
            # Convert distances to meters
            alt_diff_meters = t.altDiff * 0.3048
            dist_meters = t.dist * 1609.34
            # Calculate the angle to the target relative to the horizon in radians
            angle_to_target = math.atan2(alt_diff_meters, dist_meters)
            # Adjust for aircraft pitch
            adjusted_angle = angle_to_target - math.radians(aircraft.pitch)
            # Calculate the vertical position on the screen
            vertical_position = self.yCenter - (math.tan(adjusted_angle) * (self.height / 2))
            # Adjust for aircraft roll
            roll_radians = math.radians(aircraft.roll)
            
            xx = self.xCenter + relative_bearing * (self.width / self.fov_x)
            
            rotated_x = (xx - self.xCenter) * math.cos(roll_radians) - (vertical_position - self.yCenter) * math.sin(roll_radians) + self.xCenter
            rotated_y = (xx - self.xCenter) * math.sin(roll_radians) + (vertical_position - self.yCenter) * math.cos(roll_radians) + self.yCenter

            # Apply smoothing
            target_key = t.callsign
            current_pos = (rotated_x, rotated_y)
            
            if target_key not in self.target_positions:
                self.target_positions[target_key] = current_pos
            else:
                # Interpolate between old and new positions
                old_x, old_y = self.target_positions[target_key]
                smooth_x = old_x + (rotated_x - old_x) * self.target_smoothing
                smooth_y = old_y + (rotated_y - old_y) * self.target_smoothing
                self.target_positions[target_key] = (smooth_x, smooth_y)

            # Use smoothed position for drawing
            xx, yy = self.target_positions[target_key]

            # Draw target using smoothed positions
            pygame.draw.circle(self.surface, (200,255,255), (int(xx), int(yy)), 6, 0)
            labelCallsign = self.font_target.render(t.callsign, False, (200,255,255), (0,0,0))
            labelCallsign_rect = labelCallsign.get_rect()
            self.surface.blit(labelCallsign, (int(xx) + 10, int(yy)))
            labelAngle = self.font_target.render(f"angle: {adjusted_angle:.2f}", False, (200,255,255), (0,0,0))
            self.surface.blit(labelAngle, (int(xx) + 10, int(yy) + labelCallsign_rect.height))


    # cycle through the modes.
    def cyclecaged_mode(self):
        self.caged_mode = self.caged_mode + 1
        if self.caged_mode > 1:
            self.caged_mode = 0

    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        print("clear")

    # return a dict of objects that are used to configure the module.
    def get_module_options(self):
        imu_list = shared.Dataship.imus
        self.imu_ids = []
        for imu_index, imu in imu_list.items(): # populate the list of ids of IMUs
            self.imu_ids.append(str(imu.id))
        if len(self.source_imu_index_name) == 0: # if primary imu name is not set.
            self.source_imu_index_name = self.imu_ids[self.source_imu_index]  # select first one.
        self.imu_ids2 = self.imu_ids.copy()  # duplicate the list for the secondary imu.
        self.imu_ids2.append("NONE")

        # each item in the dict represents a configuration option.  These are variable in this class that are exposed to the user to edit.
        options = {
            "source_imu_index_name": {
                "type": "dropdown",
                "label": "Primary IMU",
                "description": "IMU to use for the 3D object.",
                "options": self.imu_ids,
                "post_change_function": "changeSource1IMU"
            },
            "source_imu_index": {
                "type": "int",
                "hidden": True,  # hide from the UI, but save to json screen file.
                "default": 0
            },
            "source_imu_index2_name": {
                "type": "dropdown",
                "label": "Secondary IMU (Camera Head)",
                "description": "If selected then 2nd IMU will be position camera. As if it was mounted on the Primary IMU.",
                "options": self.imu_ids2,
                "post_change_function": "changeSource2IMU"
            },
            "source_imu_index2": {
                "type": "int",
                "hidden": True,  # hide from the UI, but save to json screen file.
                "default": 0
            },
            "line_mode": {
                "type": "bool",
                "default": False,
                "label": "Line Mode",
                "description": ""
            },
            "line_thickness": {
                "type": "int",
                "default": 2,
                "min": 1,
                "max": 4,
                "label": "Line Thickness",
                "description": ""
            },
            "MainColor": {
                "type": "color",
                "default": (255, 255, 255),
                "label": "Line Color", 
            },
            "flight_path_color": {
                "type": "color",
                "default": (255, 0, 255),
                "label": "Flight Path Color",
            },
            "show_targets": {
                "type": "bool",
                "default": True,
                "label": "Show Targets",
                "description": ""
            },
            "target_distance_threshold": {
                "type": "int",
                "default": self.target_distance_threshold,
                "min": 1,
                "max": 150,
                "label": "Target Dist Thres",
                "description": ""
            },
            "fov_x": {
                "type": "int",
                "default": self.fov_x,
                "min": 5,
                "max": 60,
                "label": "FOV X",
                "description": "Field of View X in degrees"
            },
            "target_smoothing": {
                "type": "float",
                "default": 0.2,
                "min": 0.01,
                "max": 1.0,
                "label": "Target Smoothing",
                "description": "Target position smoothing (0.01-1.0, lower = smoother)"
            },
            "horizon_line_color": {
                "type": "color",
                "default": (255, 165, 0),  # Orange
                "label": "Horizon Line Color",
                "description": "Color of the true horizon reference line"
            },
            "horizon_line_thickness": {
                "type": "int",
                "default": 4,
                "min": 1,
                "max": 10,
                "label": "Horizon Line Thickness",
                "description": "Thickness of the horizon reference line"
            }
        }
        
        return options

    def update_flight_path_color(self, new_color):
        self.flight_path_color = new_color

    def changeSource1IMU(self):
        '''
        Change the primary IMU.
        '''
        # source_imu_index_name got changed. find the index of the imu id in the imu list.
        self.source_imu_index = self.imu_ids.index(self.source_imu_index_name)
        shared.Dataship.imus[self.source_imu_index].home(delete=True) 

    def changeSource2IMU(self):
        if self.source_imu_index2_name == "NONE":
            self.source_imu_index2 = None
            self.camera_head_imu = None
        else:
            self.source_imu_index2 = self.imu_ids2.index(self.source_imu_index2_name)
            shared.Dataship.imus[self.source_imu_index2].home(delete=True)
            self.camera_head_imu = shared.Dataship.imus[self.source_imu_index2]

    def draw_horizon_line(self, aircraft, camera_yaw=0, camera_pitch=0, camera_roll=0):
        """
        Draw a single line representing the true horizon from the camera's perspective.
        Takes into account both aircraft attitude and camera head position.
        """
        # Screen center coordinates
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Convert all angles to radians
        pitch_rad = math.radians(aircraft.pitch)
        roll_rad = math.radians(aircraft.roll)
        cam_yaw_rad = math.radians(camera_yaw)
        cam_pitch_rad = math.radians(camera_pitch) 
        cam_roll_rad = math.radians(camera_roll)

        # Calculate effective pitch angle (how far horizon appears from center)
        # When looking straight ahead, aircraft pitch directly affects horizon position
        # When looking to the side, pitch effect diminishes with cos of yaw angle
        effective_pitch = aircraft.pitch * math.cos(cam_yaw_rad) - camera_pitch
        
        # Calculate vertical offset in pixels
        pixels_per_degree = self.height / self.pxy_div
        pitch_offset = effective_pitch * pixels_per_degree
        
        # Calculate effective roll angle
        # When looking straight ahead, use aircraft roll minus camera roll
        # When looking to the side (90°), horizon appears level regardless of aircraft roll
        effective_roll = (aircraft.roll - camera_roll) * math.cos(cam_yaw_rad)
        
        # When looking up/down, horizon line should curve
        # This creates the effect of horizon curvature when looking up/down
        pitch_induced_curve = camera_pitch * math.sin(cam_yaw_rad) * 0.5
        effective_roll += pitch_induced_curve
        
        # Calculate line endpoints based on effective roll
        roll_rad = math.radians(effective_roll)
        line_length = self.width * self.horizon_line_length / 2
        
        # Calculate endpoints with roll rotation
        x1 = center_x - (line_length * math.cos(roll_rad))
        y1 = (center_y + pitch_offset) - (line_length * math.sin(roll_rad))
        x2 = center_x + (line_length * math.cos(roll_rad))
        y2 = (center_y + pitch_offset) + (line_length * math.sin(roll_rad))

        # Draw the horizon line
        pygame.draw.line(
            self.surface,
            self.horizon_line_color,
            (x1, y1),
            (x2, y2),
            self.horizon_line_thickness
        )

#############################################
## Class: Point
## used for graphical points.
class Point:
    # constructed using a normal tupple
    def __init__(self, point_t=(0, 0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])

    # define all useful operators
    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __mul__(self, scalar):
        return Point((self.x * scalar, self.y * scalar))

    def __div__(self, scalar):
        return Point((self.x / scalar, self.y / scalar))

    def __len__(self):
        return int(math.sqrt(self.x ** 2 + self.y ** 2))

    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python


