#!/usr/bin/env python

#################################################
# Module: text
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
from array import array
import moderngl


class text(Module):
    # called only when object is first created.
    def __init__(self):
        Module.__init__(self)
        self.name = "Text"  # set name
        self.font_name = "monospace"
        self.font_size = 20
        self.font_bold = False
        self.text = "text"
        self.text_color = (200,255,255)
        self.text_bg_color = (0,0,0)
        self.box_color = (255,255,255)
        self.box_weight = 0
        self.box_radius = 0
        self.template = ""
    # called once for setup
    def initMod(self, pygamescreen, width=None, height=None):
        if width is None:
            width = 200 # default width
        if height is None:
            height = 50 # default height
        Module.initMod(
            self, pygamescreen, width, height
        )  # call parent init screen.
        if shared.Dataship.debug_mode > 0:
            print(("Init Mod: %s %dx%d"%(self.name,self.width,self.height)))
        # does the self.font_name variable exist?
            
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.font_bold)
        # does the self.text variable exist?
        self.surface2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface2.fill((0,0,0,0))
        # Remove the self.surface creation and fill

    def parse_text(self, aircraft):
        def get_nested_attr(obj, attr):
            parts = attr.split('.')
            for part in parts:
                if part.endswith('()'):
                    # It's a function call
                    func_name = part[:-2]
                    obj = getattr(obj, func_name)()
                elif part.endswith('<obj>'):
                    # It's an object
                    obj = getattr(obj, part[:-5])
                else:
                    obj = getattr(obj, part)
            return obj
    
        def format_object(obj):
            # check if None
            if obj is None:
                obj = "None"
            else:
                sub_vars = obj.__dict__
                final_value = ""
                for sub_var in sub_vars:
                    # check if it starts with _ then skip it.
                    if sub_var.startswith('_'):
                        continue
                    # check if it has a __dict__.. if so skip it cause it's probably a child object. (for now...)
                    if hasattr(sub_vars[sub_var], '__dict__'):
                        continue
                    final_value += f"{sub_var}: {sub_vars[sub_var]}\n"
                obj = final_value
            return obj

        words = self.text.split()
        result = self.text
        for word in words:
            if "{" in word and "}" in word:
                variable_name = word[1:-1]
                if "%" in variable_name:
                    variable_name, format_specifier = variable_name.split("%")
                elif ":" in variable_name:
                    variable_name, format_specifier = variable_name.split(":")
                else:
                    format_specifier = None

                try:
                    if variable_name == "self":
                        variable_value = format_object(aircraft)
                    else:
                        variable_value = get_nested_attr(aircraft, variable_name)
                    # check if variable_name is a object if so get the object vars

                    # check if its a string, int, float, list, tuple, dict. and if format_specifier is not None then format it.
                    if format_specifier:
                        variable_value = f"{variable_value:{format_specifier}}"
                    elif isinstance(variable_value, (str, int, float, tuple, dict)):
                        variable_value = f"{variable_value}"
                    
                    elif isinstance(variable_value, list):
                        # go through each item in the list and format it by calling this function recursively.
                        final_value = ""
                        for item in variable_value:
                            final_value += f"\n{format_object(item)}\n======================="
                        variable_value = final_value

                    elif isinstance(variable_value, object):
                        variable_value = format_object(variable_value)
                    else:
                        variable_value = str(variable_value)
                except Exception as e:
                    variable_value = f"Error: {str(e)}"

                result = result.replace(word, variable_value)
            else:
                # this is a normal word
                result = result.replace(word, word)
        return result

    # called every redraw for the mod
    def draw(self, aircraft, smartdisplay, pos=(None,None)):
        if pos[0] is None:
            x = smartdisplay.x_center
        else:
            x = pos[0] 
        if pos[1] is None:
            y = smartdisplay.y_center
        else:
            y = pos[1] 

        # Parse text
        text = self.parse_text(aircraft)
        
        # Create text surface with alpha
        text_surface = self.font.render(text, True, self.text_color)
        text_width, text_height = text_surface.get_size()
        
        # Create surface with alpha channel
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((0,0,0,0))  # Fill with transparent black
        alpha_surface.blit(text_surface, (0,0))
        
        # Convert screen coordinates to OpenGL coordinates (-1 to 1)
        x_norm = (x / smartdisplay.width) * 2 - 1
        y_norm = -((y / smartdisplay.height) * 2 - 1)  # Flip Y coordinate
        
        width_norm = (text_width / smartdisplay.width) * 2
        height_norm = (text_height / smartdisplay.height) * 2

        # Create vertices with positions and texture coordinates
        vertices = array('f', [
            # positions       # texture coords
            x_norm, y_norm,               0.0, 1.0,  # Bottom left
            x_norm + width_norm, y_norm,  1.0, 1.0,  # Bottom right
            x_norm + width_norm, y_norm - height_norm, 1.0, 0.0,  # Top right
            x_norm, y_norm - height_norm, 0.0, 0.0,  # Top left
        ])
        
        # Convert pygame surface to ModernGL texture
        texture_data = pygame.image.tostring(alpha_surface, 'RGBA', True)
        texture = smartdisplay.ctx.texture(
            size=alpha_surface.get_size(),
            components=4,
            data=texture_data
        )
        texture.use(location=0)  # Bind to texture unit 0
        
        # Create vertex buffer and vertex array object
        vbo = smartdisplay.ctx.buffer(vertices)
        vao = smartdisplay.ctx.vertex_array(
            smartdisplay.text_program, 
            [(vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Draw the text
        vao.render(mode=smartdisplay.ctx.TRIANGLE_FAN)
        
        # Clean up
        vbo.release()
        texture.release()

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
            "template": {
                "type": "dropdown",
                "default": "template",
                "options": data_fields,
                "label": "Value",
                "description": "Select a predefined value",
                "post_change_function": "update_text"
            },
            "text": {
                "type": "text",
                "default": self.text,
                "label": "Custom",
                "description": "Text to display"
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
            # "text_bg_color": {
            #     "type": "color",
            #     "default": self.text_bg_color,
            #     "label": "Text Background Color",
            #     "description": "Color of the text background to use"
            # },
            "box_color": {
                "type": "color",
                "default": self.box_color,
                "label": "Box Color",
                "description": "Color of the box to use"
            },
            "box_weight": {
                "type": "int",
                "default": self.box_weight,
                "min": 0,
                "max": 10,
                "label": "Box Weight",
                "description": "Weight of the box to use"
            }, 
            "box_radius": {
                "type": "int",
                "default": self.box_radius,
                "min": 0,
                "max": 10,
                "label": "Box Radius",
                "description": "Radius of the box to use"
            }
        }

    def update_text(self):
        self.text = "{"+self.template+"}"
        #self.buildFont()

    # handle events
    def processEvent(self,event,aircraft,smartdisplay):

        pass



# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
