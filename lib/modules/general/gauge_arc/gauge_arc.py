#!/usr/bin/env python

#################################################
# Module: gauge_arc
# A gauge is a module that displays a value on a gauge.
# It is a circular display of a value within a range.
# The gauge can be filled with a color that represents the value.
# The gauge can also have a border and a label.
# The gauge can be used to display a variety of values such as fuel level, oil pressure, temperature, etc.
# Topher 2024.
# 

import inspect
from lib.modules._module import Module
from lib import hud_graphics
from lib import hud_utils
from lib import smartdisplay
from lib.common.dataship import dataship
from lib.common import shared
import pygame
import math


class gauge_arc(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Gauge Arc"  # set name
        self.font_name = "monospace"
        self.font_size = 20
        self.font_bold = False
        self.text = "text"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)
        self.outline_color = (255,255,255)
        self.outline_weight = 0
        self.outline_radius = 0
        self.value_color = (0,150,255)  # Changed to a modern blue

        self.data_field = ""
        self.minValue = 0
        self.maxValue = 100
        self.step = 10
        self.show_text = True
        self.text_offset = 7
        self.pointer_distance = 15

        self.arc_mode = 0 # 0 = normal, 1 = 3d, 2 = 3d with highlight

        # ranges
        self.range1 = (0, 0)
        self.range1_color = (0, 255, 0)  # Default to green
        self.range1_label = ""
        self.range2 = (0, 0)
        self.range2_color = (255, 0, 0)  # Default to red
        self.range2_label = ""
        self.range3 = (0, 0)
        self.range3_color = (0, 0, 255)  # Default to blue
        self.range3_label = ""

        # Add new attributes for gauge drawing
        self.startAngle = 225  # Start angle in degrees (bottom left)
        self.sweepAngle = 270  # Total sweep angle in degrees
        self.arcRadius = 0  # Will be calculated in initMod
        self.pointer_width = 0  # Will be calculated in initMod
        self.arcCenter = None  # Will be set in initMod

        # Add smoothing variables
        self.current_smooth_value = 0  # Current interpolated value
        self.smooth_factor = 0.15  # How quickly to move to target (0.1 = slow, 0.9 = fast)

        # Cache for expensive calculations
        self._cached_tick_positions = []
        self._cached_text_positions = []
        self._cached_surfaces = {}
        self._cached_gradients = {}

    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200
        if height is None:
            height = 200  # Make it square by default
            
        Module.initMod(self, pygamescreen, width, height)
        
        # Calculate gauge dimensions
        self.arcRadius = min(self.width, self.height) * 0.4
        self.pointer_width = self.arcRadius * 0.1
        self.arcCenter = (self.width // 2, self.height // 2)
        
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Pre-calculate tick and text positions
        self._precalculate_positions()

    def _precalculate_positions(self):
        """Pre-calculate tick and text positions for better performance"""
        self._cached_tick_positions = []
        self._cached_text_positions = []
        
        for i in range(self.minValue, self.maxValue + 1, self.step):
            angle = math.radians(self.startAngle - 
                               (i - self.minValue) * self.sweepAngle / 
                               (self.maxValue - self.minValue))
            
            inner_x = self.arcCenter[0] + (self.arcRadius - 15) * math.cos(angle)
            inner_y = self.arcCenter[1] - (self.arcRadius - 15) * math.sin(angle)
            outer_x = self.arcCenter[0] + (self.arcRadius - 5) * math.cos(angle)
            outer_y = self.arcCenter[1] - (self.arcRadius - 5) * math.sin(angle)
            
            text_x = self.arcCenter[0] + (self.arcRadius - 35) * math.cos(angle)
            text_y = self.arcCenter[1] - (self.arcRadius - 35) * math.sin(angle)
            
            self._cached_tick_positions.append(((inner_x, inner_y), (outer_x, outer_y)))
            self._cached_text_positions.append((text_x, text_y, str(i)))

    def _get_cached_text_surface(self, text, color):
        """Cache and return text surfaces"""
        # Convert color tuple to string for hashing
        key = (text, str(color))
        if key not in self._cached_surfaces:
            text_surface = self.font.render(text, True, color)
            self._cached_surfaces[key] = text_surface
        return self._cached_surfaces[key]

    def _create_gradient_surface(self, radius, color):
        """Create a radial gradient surface"""
        if (radius, str(color)) in self._cached_gradients:
            return self._cached_gradients[(radius, str(color))]
            
        # Convert radius to integer for the surface creation
        radius_int = int(radius)
        surface = pygame.Surface((radius_int * 2, radius_int * 2), pygame.SRCALPHA)
        center = (radius_int, radius_int)
        
        for i in range(radius_int, -1, -1):
            alpha = int(255 * (i / radius_int) ** 0.5)  # Square root for smoother gradient
            current_color = (*color[:3], alpha)
            pygame.draw.circle(surface, current_color, center, i)
            
        self._cached_gradients[(radius, str(color))] = surface
        return surface

    def _draw_range_band(self, range_values, range_color):
        """Draw a colored band for a given range on the gauge
        Args:
            range_values (tuple): (min, max) values for the range
            range_color (tuple): (r,g,b) color for the range band
        """
        if not range_values or range_values[0] == range_values[1]:
            return

        # Find the angles for the range start and end
        start_angle = math.radians(self.startAngle - 
                                 (range_values[0] - self.minValue) * self.sweepAngle / 
                                 (self.maxValue - self.minValue))
        end_angle = math.radians(self.startAngle - 
                               (range_values[1] - self.minValue) * self.sweepAngle / 
                               (self.maxValue - self.minValue))

        # Draw the arc with a semi-transparent color
        band_color = (*range_color[:3], 80)  # Add alpha for semi-transparency
        band_radius = self.arcRadius - 10  # Slightly smaller than the main arc
        band_width = 8

        if self.arc_mode == 1:  # 3D mode
            # Create a more pronounced 3D effect for the band
            for offset in range(3):
                current_alpha = 80 - (offset * 20)
                current_color = (*range_color[:3], current_alpha)
                pygame.draw.arc(self.surface2, current_color,
                              (self.arcCenter[0] - band_radius + offset,
                               self.arcCenter[1] - band_radius + offset,
                               band_radius * 2, band_radius * 2),
                              end_angle, start_angle, band_width - offset)
        else:
            # Standard mode
            pygame.draw.arc(self.surface2, band_color,
                          (self.arcCenter[0] - band_radius,
                           self.arcCenter[1] - band_radius,
                           band_radius * 2, band_radius * 2),
                          end_angle, start_angle, band_width)

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None,None)):
        x = pos[0] if pos[0] is not None else smartdisplay.x_center
        y = pos[1] if pos[1] is not None else smartdisplay.y_center

        # Clear the surface
        self.surface2.fill((0,0,0,0))
        
        # Get and smooth value
        target_value = self.get_data_field(aircraft, self.data_field, default_value=0, default_value_on_error="Error")
        actual_value = target_value
        
        if actual_value == "Error" or not isinstance(actual_value, (float, int)):
            # Draw modern error state
            error_color = (255, 50, 50)
            glow_surface = self._create_gradient_surface(self.arcRadius + 5, (*error_color, 30))
            self.surface2.blit(glow_surface, 
                             (self.arcCenter[0] - glow_surface.get_width()//2,
                              self.arcCenter[1] - glow_surface.get_height()//2))

            # Draw gauge background with error tint
            pygame.draw.circle(self.surface2, (40, 10, 10), self.arcCenter, self.arcRadius)
            pygame.draw.circle(self.surface2, (60, 15, 15), self.arcCenter, self.arcRadius - 2)
            
            error_font = pygame.font.SysFont(self.font_name, int(self.font_size * 1.2), True)
            error_surface = error_font.render("ERROR", True, error_color)
            error_rect = error_surface.get_rect(center=self.arcCenter)
            
            # Draw error text with glow
            glow_size = 2
            for offset in range(glow_size, 0, -1):
                glow_surface = error_font.render("ERROR", True, (*error_color, 50))
                glow_rect = glow_surface.get_rect(center=self.arcCenter)
                self.surface2.blit(glow_surface, (glow_rect.x - offset, glow_rect.y - offset))
            
            self.surface2.blit(error_surface, error_rect)
            
            self.pygamescreen.blit(self.surface2, (x, y))
            return
        
        if target_value is not None:
            # make sure target_value is a float or int.. if not return 0
            if not isinstance(target_value, (float, int)):
                target_value = 0
            
            self.current_smooth_value += (target_value - self.current_smooth_value) * self.smooth_factor
            value = max(self.minValue, min(self.maxValue, self.current_smooth_value))
        else:
            value = None

        # Create and apply background glow
        glow_color = (*self.value_color, 30)  # Semi-transparent glow
        glow_surface = self._create_gradient_surface(self.arcRadius + 5, glow_color)
        self.surface2.blit(glow_surface, 
                          (self.arcCenter[0] - glow_surface.get_width()//2,
                           self.arcCenter[1] - glow_surface.get_height()//2))

        # Draw modern bezel with gradient
        for i in range(4):
            color = tuple(max(0, c - 40 + i * 10) for c in self.outline_color)
            alpha = 255 - i * 40
            color = (*color[:3], alpha)
            
            if self.arc_mode == 1:  # 3D mode
                # Create a more pronounced bevel effect
                bevel_width = 4
                for j in range(bevel_width):
                    # Top light reflection
                    light_alpha = int(200 * (1 - j/bevel_width))
                    light_color = tuple(min(255, c + 100) for c in self.outline_color[:3])
                    pygame.draw.circle(self.surface2, (*light_color, light_alpha),
                                    (self.arcCenter[0], self.arcCenter[1] - 2),
                                    self.arcRadius - j, 1)
                    
                    # Bottom shadow
                    shadow_alpha = int(200 * (j/bevel_width))
                    shadow_color = tuple(max(0, c - 100) for c in self.outline_color[:3])
                    pygame.draw.circle(self.surface2, (*shadow_color, shadow_alpha),
                                    (self.arcCenter[0], self.arcCenter[1] + 2),
                                    self.arcRadius - j, 1)
            
            pygame.draw.circle(self.surface2, color, self.arcCenter, 
                             self.arcRadius - i, max(1, self.outline_weight))

        # Draw modern dial face with gradient background
        base_color = (30, 30, 35)  # Slightly blue-tinted dark background
        if self.arc_mode == 1:  # 3D mode
            # Create a metallic-looking surface with gradient
            for i in range(int(self.arcRadius - 4)):
                progress = i / (self.arcRadius - 4)
                # Create a subtle metallic effect
                intensity = 35 + int(20 * math.sin(progress * math.pi * 2))
                color = (intensity, intensity, intensity + 5)
                alpha = 255 - int(progress * 50)
                pygame.draw.circle(self.surface2, (*color, alpha),
                                self.arcCenter, self.arcRadius - 4 - i)
        else:
            for i in range(3):
                alpha = 255 - i * 20
                pygame.draw.circle(self.surface2, (*base_color, alpha), 
                                 self.arcCenter, self.arcRadius - 4 - i)

        # Draw modern tick marks
        for (inner_pos, outer_pos), (text_x, text_y, text) in zip(
            self._cached_tick_positions, self._cached_text_positions):
            
            if self.arc_mode == 1:  # 3D mode
                # Create 3D effect for tick marks
                tick_length = 8
                tick_angle = math.atan2(outer_pos[1] - inner_pos[1],
                                      outer_pos[0] - inner_pos[0])
                
                # Draw tick shadow
                shadow_offset = 2
                shadow_start = (inner_pos[0] + shadow_offset,
                              inner_pos[1] + shadow_offset)
                shadow_end = (outer_pos[0] + shadow_offset,
                            outer_pos[1] + shadow_offset)
                pygame.draw.line(self.surface2, (0, 0, 0, 100),
                               shadow_start, shadow_end, 2)
                
                # Draw main tick with highlight
                tick_color = (*self.outline_color[:3], 180)
                highlight_color = tuple(min(255, c + 70) for c in self.outline_color[:3])
                pygame.draw.line(self.surface2, tick_color, inner_pos, outer_pos, 2)
                pygame.draw.line(self.surface2, (*highlight_color, 100),
                               inner_pos, 
                               (inner_pos[0] + tick_length * 0.3 * math.cos(tick_angle),
                                inner_pos[1] + tick_length * 0.3 * math.sin(tick_angle)), 1)
            else:
                # Original tick drawing
                tick_color = (*self.outline_color[:3], 180)
                pygame.draw.line(self.surface2, tick_color, inner_pos, outer_pos, 1)
            
            # Draw text with 3D effect if in 3D mode
            if self.arc_mode == 1:
                # Draw text shadow
                shadow_surface = self._get_cached_text_surface(text, (0, 0, 0, 100))
                shadow_rect = shadow_surface.get_rect()
                self.surface2.blit(shadow_surface,
                                 (text_x - shadow_rect.width/2 + 2,
                                  text_y - shadow_rect.height/2 + 2))
                
                # Draw text highlight
                highlight_surface = self._get_cached_text_surface(text, (*self.text_color[:3], 255))
                highlight_rect = highlight_surface.get_rect()
                self.surface2.blit(highlight_surface,
                                 (text_x - highlight_rect.width/2 - 1,
                                  text_y - highlight_rect.height/2 - 1))
            
            # Draw main text
            text_surface = self._get_cached_text_surface(text, (*self.text_color[:3], 200))
            text_rect = text_surface.get_rect()
            self.surface2.blit(text_surface,
                             (text_x - text_rect.width/2,
                              text_y - text_rect.height/2))

        # Draw range1 band if defined
        if self.range1 and self.range1[0] != self.range1[1]:
            self._draw_range_band(self.range1, self.range1_color)

        # Draw range2 band if defined
        if self.range2 and self.range2[0] != self.range2[1]:
            self._draw_range_band(self.range2, self.range2_color)

        # Draw range3 band if defined
        if self.range3 and self.range3[0] != self.range3[1]:
            self._draw_range_band(self.range3, self.range3_color)
        
        # Draw modern pointer with gradient and glow
        if value is not None:
            value_angle = math.radians(self.startAngle -
                                     (value - self.minValue) * self.sweepAngle /
                                     (self.maxValue - self.minValue))

            # Calculate pointer dimensions
            pointer_length = self.arcRadius * 0.7
            pointer_width = self.arcRadius * 0.04
            center_offset = self.arcRadius * 0.15

            # Calculate pointer points
            tip_x = self.arcCenter[0] + pointer_length * math.cos(value_angle)
            tip_y = self.arcCenter[1] - pointer_length * math.sin(value_angle)
            
            base_left_x = self.arcCenter[0] + center_offset * math.cos(value_angle + math.pi/2)
            base_left_y = self.arcCenter[1] - center_offset * math.sin(value_angle + math.pi/2)
            
            base_right_x = self.arcCenter[0] + center_offset * math.cos(value_angle - math.pi/2)
            base_right_y = self.arcCenter[1] - center_offset * math.sin(value_angle - math.pi/2)
            
            pointer_points = [(tip_x, tip_y),
                            (base_left_x, base_left_y),
                            (base_right_x, base_right_y)]

            if self.arc_mode == 1:  # 3D mode
                # Draw pointer shadow
                shadow_offset = 3
                shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in pointer_points]
                pygame.draw.polygon(self.surface2, (0, 0, 0, 80), shadow_points)
                
                # Draw pointer base (gives depth)
                base_color = tuple(max(0, c - 40) for c in self.value_color[:3])
                pygame.draw.circle(self.surface2, (*base_color, 200),
                                self.arcCenter, center_offset + 2)
                
                # Draw pointer with 3D lighting effect
                light_angle = value_angle + math.pi/4  # Light source angle
                light_intensity = abs(math.cos(light_angle))
                highlight_color = tuple(min(255, int(c + 70 * light_intensity)) 
                                     for c in self.value_color[:3])
                
                # Draw main pointer body
                pygame.draw.polygon(self.surface2, self.value_color, pointer_points)
                
                # Draw highlight edge
                highlight_points = [
                    pointer_points[0],
                    (pointer_points[1][0] * 0.95 + self.arcCenter[0] * 0.05,
                     pointer_points[1][1] * 0.95 + self.arcCenter[1] * 0.05),
                    (pointer_points[2][0] * 0.95 + self.arcCenter[0] * 0.05,
                     pointer_points[2][1] * 0.95 + self.arcCenter[1] * 0.05)
                ]
                pygame.draw.polygon(self.surface2, (*highlight_color, 150), highlight_points)
            else:
                # Original pointer drawing
                glow_color = (*self.value_color[:3], 30)
                for i in range(3):
                    offset = 2 - i
                    offset_points = [(x + offset, y + offset) for x, y in pointer_points]
                    pygame.draw.polygon(self.surface2, glow_color, offset_points)

                pygame.draw.polygon(self.surface2, self.value_color, pointer_points)
                
                highlight_points = [
                    pointer_points[0],
                    (pointer_points[1][0] * 0.9 + self.arcCenter[0] * 0.1,
                     pointer_points[1][1] * 0.9 + self.arcCenter[1] * 0.1),
                    (pointer_points[2][0] * 0.9 + self.arcCenter[0] * 0.1,
                     pointer_points[2][1] * 0.9 + self.arcCenter[1] * 0.1)
                ]
                highlight_color = tuple(min(255, c + 70) for c in self.value_color[:3])
                pygame.draw.polygon(self.surface2, (*highlight_color, 150), highlight_points)

        # Draw value text with modern styling
        if self.show_text and actual_value is not None:
            value_str = f"{actual_value:.1f}"
            value_font = pygame.font.SysFont(self.font_name, 
                                           int(self.font_size * 1.2), 
                                           self.font_bold)
            
            # Draw text with glow effect
            glow_color = (*self.value_color[:3], 30)
            for offset in range(2, 0, -1):
                glow_surface = value_font.render(value_str, True, glow_color)
                glow_rect = glow_surface.get_rect()
                text_x = self.arcCenter[0] - glow_rect.width / 2
                text_y = self.arcCenter[1] + self.arcRadius * (self.text_offset/10)
                self.surface2.blit(glow_surface, (text_x + offset, text_y + offset))
            
            # Draw main text
            value_surface = value_font.render(value_str, True, self.text_color)
            text_rect = value_surface.get_rect()
            text_x = self.arcCenter[0] - text_rect.width / 2
            text_y = self.arcCenter[1] + self.arcRadius * (self.text_offset/10)
            self.surface2.blit(value_surface, (text_x, text_y))

        # Final blit to screen
        self.pygamescreen.blit(self.surface2, (x, y))

    # called before screen draw.  To clear the screen to your favorite color.
    def clear(self):
        #self.ahrs_bg.fill((0, 0, 0))  # clear screen
        #print("clear")
        pass

    def buildFont(self):
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
    
    # return a dict of objects that are used to configure the module.
    def get_module_options(self):

        data_fields = shared.Dataship._get_all_fields()
        #print(f"templates: {data_fields}")

        return {
            "data_field": {
                "type": "dataship_var",
                "default": self.data_field,
                "label": "Data Field",
                "description": "Select a data field to display",
                "post_change_function": "update_cached_positions"
            },
            "minValue": {
                "type": "int",
                "default": self.minValue,
                "label": "Min Value",
                "min": -1000,
                "max": 1000,
                "description": "Minimum value to display",
                "post_change_function": "update_cached_positions"
            },
            "maxValue": {
                "type": "float",
                "default": self.maxValue,
                "label": "Max Value",
                "description": "Maximum value to display",
                "post_change_function": "update_cached_positions"
            },
            "arc_mode": {
                "type": "int",
                "default": self.arc_mode,
                "min": 0,
                "max": 2,
                "label": "Arc Mode",
                "description": "Mode of the arc to use",
                "options": ["Normal", "3D", "Test"],
                "post_change_function": "update_arc_mode"
            },

            "step": {
                "type": "int",
                "default": self.step,
                "min": 1,
                "max": 1000,
                "label": "Step Size",
                "description": "Step size to use",
                "post_change_function": "update_cached_positions"
            },
            "show_text": {
                "type": "bool",
                "default": self.show_text,
                "label": "Show Value",
                "description": "Show the current value next to the gauge"
            },
            "text_offset": {
                "type": "int",
                "default": self.text_offset,
                "min": 1,
                "max": 10,
                "label": "Text Offset",
                "description": "Offset of the text from the center",
                "post_change_function": "update_cached_positions"
            },            
            "value_color": {
                "type": "color",
                "default": self.value_color,
                "label": "Value Color",
                "description": "Color of the value to use"
            },
            "font_name": {
                "type": "dropdown",
                "default": self.font_name,
                "options": ["monospace", "sans-serif", "serif","arial","courier","times","helvetica"],
                "label": "Font Name",
                "description": "Name of the font to use",
                "post_change_function": "buildFont"
            },
            "font_size": {
                "type": "int",
                "default": self.font_size,
                "min": 10,
                "max": 300,
                "label": "Font Size",
                "description": "Size of the font to use",
                "post_change_function": "buildFont"
            },
            "font_bold": {
                "type": "bool",
                "default": False,
                "label": "Font Bold",
                "description": "Use bold font",
                "post_change_function": "buildFont"
            },
            "text_color": {
                "type": "color",
                "default": self.text_color,
                "label": "Text Color",
                "description": "Color of the text to use"
            }, 
            "outline_color": {
                "type": "color",
                "default": self.outline_color,
                "label": "Outline Color",
                "description": "Color of the outline to use"
            },
            "outline_weight": {
                "type": "int",
                "default": self.outline_weight,
                "min": 0,
                "max": 10,
                "label": "Outline Weight",
                "description": "Weight of the outline to use"
            }, 
            "pointer_distance": {
                "type": "int",
                "default": self.pointer_distance,
                "min": 1,
                "max": 15,
                "label": "Pointer Distance",
                "description": "Distance of the pointer from the center"
            },
            "smooth_factor": {
                "type": "float",
                "default": self.smooth_factor,
                "min": 0.01,
                "max": 1.0,
                "label": "Smooth Factor",
                "description": "How quickly the pointer moves to new values (0.01=slow, 1.0=instant)"
            },
            "range1": {
                "type": "tuple_int",
                "default": self.range1,
                "labels": ["Min", "Max"],
                "label": "Range 1",
                "description": "Range 1 to use",
                "post_change_function": "update_range"
            },
            "range1_label": {
                "type": "text",
                "default": self.range1_label,
                "label": "Range 1 Label",
                "description": "Label of the range 1 to use"
            },
            "range1_color": {
                "type": "color",
                "default": self.range1_color,
                "label": "Range 1 Color",
                "description": "Color of the range 1 to use"
            },
            "range2": {
                "type": "tuple_int",
                "default": self.range2,
                "labels": ["Min", "Max"],
                "label": "Range 2",
                "description": "Range 2 to use",
                "post_change_function": "update_range"
            },
            "range2_label": {
                "type": "text",
                "default": self.range2_label,
                "label": "Range 2 Label",
                "description": "Label of the range 2 to use"
            },
            "range2_color": {
                "type": "color",
                "default": self.range2_color,
                "label": "Range 2 Color",
                "description": "Color of the range 2 to use"
            },
            "range3": {
                "type": "tuple_int",
                "default": self.range3,
                "labels": ["Min", "Max"],
                "label": "Range 3",
                "description": "Range 3 to use",
                "post_change_function": "update_range"
            },
            "range3_label": {
                "type": "text",
                "default": self.range3_label,
                "label": "Range 3 Label",
                "description": "Label of the range 3 to use"
            },
            "range3_color": {
                "type": "color",
                "default": self.range3_color,
                "label": "Range 3 Color",
                "description": "Color of the range 3 to use"
            }
        }
    
    def update_cached_positions(self):
        self._precalculate_positions()

    def update_arc_mode(self):
        self._precalculate_positions()
    
    def update_range(self):
        print(f"range1: {self.range1}")

    # def update_option(self, option, value):
    #     print(f"update_option: {option} = {value}")

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
