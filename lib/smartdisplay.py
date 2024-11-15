#!/usr/bin/env python


import pygame
import math
import moderngl
from array import array

#############################################
## Class: smartdisplay
## Store display information for viewable display.
##
class SmartDisplay(object):

    LEFT = 7
    LEFT_TOP = 8
    LEFT_MID = 9
    LEFT_MID_UP = 10
    LEFT_MID_DOWN = 11
    LEFT_BOTTOM = 12

    RIGHT = 30
    RIGHT_TOP = 31
    RIGHT_MID = 32
    RIGHT_MID_UP = 33
    RIGHT_MID_DOWN = 34
    RIGHT_BOTTOM = 35

    TOP = 50
    TOP_MID = 51
    TOP_RIGHT = 52

    BOTTOM = 70
    BOTTOM_MID = 71
    BOTTOM_RIGHT = 72

    CENTER_LEFT = 80
    CENTER_CENTER = 81
    CENTER_RIGHT = 82
    CENTER_CENTER_UP = 83
    CENTER_CENTER_DOWN = 84

    def __init__(self):
        #print("SmartDisplay Init")
        self.org_width = 0
        self.org_height = 0
        self.x_start = 0
        self.y_start = 0
        self.x_end = 0
        self.y_end = 0
        self.x_center = 0
        self.y_center = 0
        self.width = 0
        self.height = 0
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2)
        self.pygamescreen = 0
        self.drawBorder = True

        self.pos_next_left_up = 0
        self.pos_next_left_down = 0

        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0

        self.pos_next_bottom_padding = 0

        self.pos_horz_padding = 15
        
    
    def set_ctx(self, ctx):
        self.ctx = ctx
        # Enable blending
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.text_program = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                in vec2 in_texcoord;
                out vec2 v_texcoord;

                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D texture0;
                in vec2 v_texcoord;
                out vec4 f_color;

                void main() {
                    vec4 texel = texture(texture0, v_texcoord);
                    if(texel.a < 0.1) discard;
                    f_color = texel;
                }
            '''
        )

    def gl_tv_text(self, text, x, y, font=None, color=(255,255,255)):
        """
        Render text at given x,y coordinates using ModernGL
        
        Args:
            text (str): Text to render
            x (int): X coordinate in screen space
            y (int): Y coordinate in screen space 
            font (pygame.font.Font, optional): Font to use. Defaults to self.font
            color (tuple, optional): RGB color tuple. Defaults to white
        """
        if font is None:
            font = self.font
        
        # Create text surface with alpha
        text_surface = font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        
        # Create surface with alpha channel
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((0,0,0,0))  # Fill with transparent black
        alpha_surface.blit(text_surface, (0,0))
        
        # Convert screen coordinates to OpenGL coordinates (-1 to 1)
        x_norm = (x / self.width) * 2 - 1
        y_norm = -((y / self.height) * 2 - 1)  # Flip Y coordinate
        
        width_norm = (text_width / self.width) * 2
        height_norm = (text_height / self.height) * 2

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
        texture = self.ctx.texture(
            size=alpha_surface.get_size(),
            components=4,
            data=texture_data
        )
        texture.use(location=0)  # Bind to texture unit 0
        
        # Create vertex buffer and vertex array object
        vbo = self.ctx.buffer(vertices)
        vao = self.ctx.vertex_array(
            self.text_program, 
            [(vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Draw the text
        vao.render(mode=self.ctx.TRIANGLE_FAN)
        
        # Clean up
        vbo.release()
        texture.release()

    def gl_tv_rect(self, color, rect, thickness=0):
        """
        Draw a rectangle using ModernGL
        
        Args:
            color (tuple): RGB color tuple
            rect (tuple): (x, y, width, height) in screen coordinates
            thickness (int): Border thickness. 0 means filled rectangle
        """
        x, y, width, height = rect
        
        # Convert screen coordinates to OpenGL coordinates (-1 to 1)
        x_norm = (x / self.width) * 2 - 1
        y_norm = -((y / self.height) * 2 - 1)
        width_norm = (width / self.width) * 2
        height_norm = (height / self.height) * 2

        if thickness == 0:
            # Filled rectangle
            program = self.ctx.program(
                vertex_shader='''
                    #version 330
                    in vec2 in_position;
                    void main() {
                        gl_Position = vec4(in_position, 0.0, 1.0);
                    }
                ''',
                fragment_shader='''
                    #version 330
                    uniform vec3 color;
                    out vec4 f_color;
                    void main() {
                        f_color = vec4(color, 1.0);
                    }
                '''
            )
            
            vertices = array('f', [
                x_norm, y_norm,
                x_norm + width_norm, y_norm,
                x_norm + width_norm, y_norm - height_norm,
                x_norm, y_norm - height_norm,
            ])
            
            program['color'].write(array('f', [c/255 for c in color]))
            vbo = self.ctx.buffer(vertices)
            vao = self.ctx.vertex_array(program, [(vbo, '2f', 'in_position')])
            vao.render(mode=self.ctx.TRIANGLE_FAN)
            vbo.release()
        else:
            # Outlined rectangle
            program = self.ctx.program(
                vertex_shader='''
                    #version 330
                    in vec2 in_position;
                    void main() {
                        gl_Position = vec4(in_position, 0.0, 1.0);
                    }
                ''',
                fragment_shader='''
                    #version 330
                    uniform vec3 color;
                    out vec4 f_color;
                    void main() {
                        f_color = vec4(color, 1.0);
                    }
                '''
            )

            t = (thickness / self.width) * 2  # Convert thickness to normalized coordinates
            
            # Create vertices for 4 rectangles (top, right, bottom, left borders)
            vertices = array('f', [
                # Top
                x_norm, y_norm,
                x_norm + width_norm, y_norm,
                x_norm + width_norm, y_norm - t,
                x_norm, y_norm - t,
                # Right
                x_norm + width_norm - t, y_norm,
                x_norm + width_norm, y_norm,
                x_norm + width_norm, y_norm - height_norm,
                x_norm + width_norm - t, y_norm - height_norm,
                # Bottom
                x_norm, y_norm - height_norm + t,
                x_norm + width_norm, y_norm - height_norm + t,
                x_norm + width_norm, y_norm - height_norm,
                x_norm, y_norm - height_norm,
                # Left
                x_norm, y_norm,
                x_norm + t, y_norm,
                x_norm + t, y_norm - height_norm,
                x_norm, y_norm - height_norm,
            ])

            program['color'].write(array('f', [c/255 for c in color]))
            vbo = self.ctx.buffer(vertices)
            vao = self.ctx.vertex_array(program, [(vbo, '2f', 'in_position')])
            vao.render(mode=self.ctx.TRIANGLES)
            vbo.release()

    def gl_tv_circle(self, color, center, radius, thickness=0):
        """
        Draw a circle using ModernGL
        
        Args:
            color (tuple): RGB color tuple
            center (tuple): (x, y) center point in screen coordinates
            radius (float): radius in pixels
            thickness (int): Border thickness. 0 means filled circle
        """
        x, y = center
        segments = 32  # Number of segments to approximate circle
        
        # Convert screen coordinates to OpenGL coordinates (-1 to 1)
        x_norm = (x / self.width) * 2 - 1
        y_norm = -((y / self.height) * 2 - 1)
        radius_norm_x = (radius / self.width) * 2
        radius_norm_y = (radius / self.height) * 2

        program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(color, 1.0);
                }
            '''
        )

        vertices = []
        if thickness == 0:
            # Filled circle
            vertices.append(x_norm)
            vertices.append(y_norm)
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                vertices.append(x_norm + math.cos(angle) * radius_norm_x)
                vertices.append(y_norm + math.sin(angle) * radius_norm_y)
            render_mode = self.ctx.TRIANGLE_FAN
        else:
            # Outlined circle
            t_norm_x = (thickness / self.width) * 2
            t_norm_y = (thickness / self.height) * 2
            for i in range(segments):
                angle1 = 2 * math.pi * i / segments
                angle2 = 2 * math.pi * (i + 1) / segments
                
                # Outer vertices
                vertices.extend([
                    x_norm + math.cos(angle1) * (radius_norm_x + t_norm_x),
                    y_norm + math.sin(angle1) * (radius_norm_y + t_norm_y),
                    x_norm + math.cos(angle2) * (radius_norm_x + t_norm_x),
                    y_norm + math.sin(angle2) * (radius_norm_y + t_norm_y),
                    x_norm + math.cos(angle1) * radius_norm_x,
                    y_norm + math.sin(angle1) * radius_norm_y,
                    
                    x_norm + math.cos(angle2) * radius_norm_x,
                    y_norm + math.sin(angle2) * radius_norm_y,
                    x_norm + math.cos(angle2) * (radius_norm_x + t_norm_x),
                    y_norm + math.sin(angle2) * (radius_norm_y + t_norm_y),
                    x_norm + math.cos(angle1) * radius_norm_x,
                    y_norm + math.sin(angle1) * radius_norm_y,
                ])
            render_mode = self.ctx.TRIANGLES

        program['color'].write(array('f', [c/255 for c in color]))
        vbo = self.ctx.buffer(array('f', vertices))
        vao = self.ctx.vertex_array(program, [(vbo, '2f', 'in_position')])
        vao.render(mode=render_mode)
        vbo.release()

    def gl_tv_line(self, color, start_pos, end_pos, thickness=1):
        """
        Draw a line using ModernGL
        
        Args:
            color (tuple): RGB color tuple
            start_pos (tuple): (x, y) start point in screen coordinates
            end_pos (tuple): (x, y) end point in screen coordinates
            thickness (int): Line thickness in pixels
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Convert screen coordinates to OpenGL coordinates (-1 to 1)
        x1_norm = (x1 / self.width) * 2 - 1
        y1_norm = -((y1 / self.height) * 2 - 1)
        x2_norm = (x2 / self.width) * 2 - 1
        y2_norm = -((y2 / self.height) * 2 - 1)
        
        # Calculate normal vector to line
        dx = x2_norm - x1_norm
        dy = y2_norm - y1_norm
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
        
        nx = -dy/length * (thickness/self.width) * 2
        ny = dx/length * (thickness/self.height) * 2

        program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(color, 1.0);
                }
            '''
        )

        vertices = array('f', [
            x1_norm + nx, y1_norm + ny,
            x2_norm + nx, y2_norm + ny,
            x2_norm - nx, y2_norm - ny,
            x1_norm - nx, y1_norm - ny,
        ])

        program['color'].write(array('f', [c/255 for c in color]))
        vbo = self.ctx.buffer(vertices)
        vao = self.ctx.vertex_array(program, [(vbo, '2f', 'in_position')])
        vao.render(mode=self.ctx.TRIANGLE_FAN)
        vbo.release()

    ###################################################################

    def setDisplaySize(self,width,height):
        self.org_width = width
        self.org_height = height
        self.font = pygame.font.SysFont(
            "monospace", 22
        )  # default font
        self.fontBig = pygame.font.SysFont(
            "monospace", 40
        )  # default font


    def setDrawableArea(self,x_start,y_start,x_end,y_end):
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end
        self.width = x_end - x_start
        self.height = y_end - y_start
        self.widthCenter = (self.width / 2) 
        self.heightCenter = (self.height / 2) 

        self.x_center = x_start + self.widthCenter
        self.y_center = y_start + self.heightCenter

        print(("SmartDisplay drawable offset: %d,%d to %d,%d"%(self.x_start,self.y_start,self.x_end,self.y_end)))
        print(("SmartDisplay New screen width/height: %d,%d"%(self.width,self.height)))
        print(("SmartDisplay center x/y: %d,%d"%(self.widthCenter,self.heightCenter)))
        print(("SmartDisplay real center x/y: %d,%d"%(self.x_center,self.y_center)))

    def setPyGameScreen(self,pygamescreen):
        self.pygamescreen = pygamescreen

    # this resets the counters in this object to keep track of where to draw things.
    def draw_loop_start(self):
        self.pos_next_left_up = 0
        self.pos_next_left_down = 0
        self.pos_next_right_up = 0
        self.pos_next_right_down = 0
        self.pos_next_right_padding = 0
        self.pos_next_bottom_padding = 0
        self.pos_next_center_center_up = 0
        self.pos_next_center_center_down = 0

    # called last after the draw loop is done.
    def draw_loop_done(self):
        # draw a border if it's smaller.
        if(self.drawBorder==True):
            pygame.draw.rect(self.pygamescreen, (255,255,255), (self.x_start, self.y_start, self.width, self.height), 1)
 

    # smart blit the next surface to the display given a location.
    # this automatically pads space from the last item that was displayed.
    def blit_next(self,surface,drawAtPos,posAdjustment=(0,0)):

        posAdjustmentX, posAdjustmentY = posAdjustment

        # LEFT SIDE
        if drawAtPos == SmartDisplay.LEFT_MID:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter-(surface.get_height()/2)+self.y_start+posAdjustmentY)))
            self.pos_next_left_up += surface.get_height()/2
            self.pos_next_left_down += surface.get_height()/2

        elif drawAtPos == SmartDisplay.LEFT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter-surface.get_height()+self.y_start-self.pos_next_left_up+posAdjustmentY) ))
            self.pos_next_left_up += surface.get_height() # first get the new postion..

        elif drawAtPos == SmartDisplay.LEFT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_start + self.pos_horz_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_left_down+posAdjustmentY) ))
            self.pos_next_left_down += surface.get_height()

        # RIGHT SIDE
        elif drawAtPos == SmartDisplay.RIGHT_MID:
            self.pos_next_right_padding = surface.get_width() + self.pos_horz_padding
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter-(surface.get_height()/2)+self.y_start+posAdjustmentY)))
            self.pos_next_right_up += surface.get_height()/2
            self.pos_next_right_down += surface.get_height()/2

        elif drawAtPos == SmartDisplay.RIGHT_MID_UP:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter-surface.get_height()+self.y_start-self.pos_next_right_up+posAdjustmentY) ))
            self.pos_next_right_up += surface.get_height() # first get the new postion..

        elif drawAtPos == SmartDisplay.RIGHT_MID_DOWN:
            self.pygamescreen.blit(surface, (self.x_end - self.pos_next_right_padding+posAdjustmentX, (self.heightCenter+self.y_start+self.pos_next_right_down+posAdjustmentY) ))
            self.pos_next_right_down += surface.get_height()

        # TOP
        elif drawAtPos == SmartDisplay.TOP:
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_start+posAdjustmentY))

        elif drawAtPos == SmartDisplay.TOP_MID:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start+posAdjustmentY ))

        elif drawAtPos == SmartDisplay.TOP_RIGHT:
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_start+posAdjustmentY) ))

        # BOTTOM
        elif drawAtPos == SmartDisplay.BOTTOM:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding))

        elif drawAtPos == SmartDisplay.BOTTOM_MID:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_end+posAdjustmentY-self.pos_next_bottom_padding ))

        elif drawAtPos == SmartDisplay.BOTTOM_RIGHT:
            self.pos_next_bottom_padding = surface.get_height()
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_end+posAdjustmentY)-self.pos_next_bottom_padding ))

        # CENTER
        elif drawAtPos == SmartDisplay.CENTER_LEFT:
            self.pygamescreen.blit(surface, (self.x_start+posAdjustmentX, self.y_start+self.heightCenter-(surface.get_height()/2)+posAdjustmentY))

        elif drawAtPos == SmartDisplay.CENTER_CENTER:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start + self.heightCenter - (surface.get_height()/2) + posAdjustmentY  ))
            self.pos_next_center_center_down = self.pos_next_center_center_up = surface.get_height()/2

        elif drawAtPos == SmartDisplay.CENTER_CENTER_UP:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start + self.heightCenter - (surface.get_height()/2) + self.pos_next_center_center_up + posAdjustmentY  ))
            self.pos_next_center_center_up = surface.get_height()/2

        elif drawAtPos == SmartDisplay.CENTER_CENTER_DOWN:
            self.pygamescreen.blit(surface, (self.x_start+self.widthCenter-(surface.get_width()/2)+posAdjustmentX, self.y_start + self.heightCenter - (surface.get_height()/2) + self.pos_next_center_center_down + posAdjustmentY  ))
            self.pos_next_center_center_down = surface.get_height()/2

        elif drawAtPos == SmartDisplay.CENTER_RIGHT:
            self.pygamescreen.blit(surface, (self.x_end-surface.get_width()+posAdjustmentX, (self.y_start+self.heightCenter-(surface.get_height()/2)+posAdjustmentY) ))


    # draw box with text in it.
    # drawPos = DrawPos on screen.. example smartdisplay.RIGHT_MID for right middle of display.
    # width,height of box.
    # justify: 0=left justify text, 1=right, 2= center in box.
    def draw_box_text( self, drawAtPos, font, text, textcolor, width, height, linecolor, thickness,posAdjustment=(0,0),justify=0):
        newSurface = pygame.Surface((width, height))
        if(font==None): font = self.font
        label = font.render(text, 1, textcolor)
        pygame.draw.rect(newSurface, linecolor, (0, 0, width, height), thickness)
        if justify==0:
            newSurface.blit(label, (0,0))
        elif justify==1:
            newSurface.blit(label, (newSurface.get_width()-label.get_width(),0))
        elif justify==2:
            newSurface.blit(label, (newSurface.get_width()/2-label.get_width()/2,0))
        self.blit_next(newSurface,drawAtPos,posAdjustment)

    # draw box with text in it. with padding
    # using the font size to determine the box size.
    # and padding to automaticaly pad the left if needed. padding 4 means it will always be 4 chars wide.
    def draw_box_text_padding( self, drawAtPos, font, text, textcolor, padding , linecolor, thickness,posAdjustment=(0,0)):
        text = text.rjust(padding)
        if(font==None): font = self.font
        label = font.render(text, 1, textcolor, (0,0,0)) # use a black background color
        newSurface = pygame.Surface((label.get_width(), label.get_height()-label.get_height()/6)) # trim height of font.
        newSurface.blit(label,(0,0))
        if(thickness==1):
            pygame.draw.rect(newSurface, linecolor, (0, 0, newSurface.get_width(), newSurface.get_height()), 1)
        else:
            offset = thickness/2
            pygame.draw.rect(newSurface, linecolor, (offset, offset, newSurface.get_width()-thickness, newSurface.get_height()-thickness), thickness)
        #newSurface.blit(label, (0,0))
        self.blit_next(newSurface,drawAtPos,posAdjustment)

    # draw box with text in it. with padding
    # using the font size to determine the box size.
    # and padding to automaticaly pad the left if needed. padding 4 means it will always be 4 chars wide.
    def draw_box_text_with_big_and_small_text( self, drawAtPos, font1, font2, text, charLenToUseForRight, textcolor, padding , linecolor, thickness,posAdjustment=(0,0)):
        strlen = len(text)
        if(font1==None): font1 = self.fontBig
        if(font2==None): font2 = self.font
        # split the string up
        if(strlen>charLenToUseForRight):
            rightText = text[strlen-charLenToUseForRight:strlen]
            leftText = text[0:strlen-charLenToUseForRight].rjust(padding-charLenToUseForRight)
        else:
            rightText = text.rjust(charLenToUseForRight)
            leftText = " ".rjust(padding-charLenToUseForRight)
        # render the labels
        label1 = font1.render(leftText, 1, textcolor, (0,0,0)) # use a black background color
        label2 = font2.render(rightText, 1, textcolor, (0,0,0)) # use a black background color
        # add them to a new surface.  trim the height down a bit cause the font seems to add extra space..
        newSurface = pygame.Surface((label1.get_width()+label2.get_width(), label1.get_height()-label1.get_height()/6)) # remove extra padding
        newSurface.blit(label1, (0,0))
        newSurface.blit(label2, (label1.get_width(),newSurface.get_height()-label2.get_height() ))
        # draw a box if we want.
        if(thickness==0):
            pass
        elif(thickness==1):
            pygame.draw.rect(newSurface, linecolor, (0, 0, newSurface.get_width(), newSurface.get_height()), 1)
        else:
            offset = thickness/2
            pygame.draw.rect(newSurface, linecolor, (offset, offset, newSurface.get_width()-thickness, newSurface.get_height()-thickness), thickness)
        self.blit_next(newSurface,drawAtPos,posAdjustment)


    # smart draw text.
    def draw_text(self, drawAtPos, font, text, color,posAdjustment=(0,0),justify=0):
        backgroundcolor = (0,0,0)
        if(font==None): font = self.font
        if justify==0:
            self.blit_next(font.render(text, 1, color,backgroundcolor), drawAtPos,posAdjustment)
        elif justify==1:
            label = font.render(text, 1, color,backgroundcolor)
            self.blit_next(label, drawAtPos, (label.get_width(),0))
        elif justify==2:
            label = font.render(text, 1, color,backgroundcolor)
            self.blit_next(label, drawAtPos, (label.get_width()/2,0))

    # draw a circle.
    def draw_circle(self,color,center,radius,thickness):
        pygame.draw.circle(
            self.pygamescreen,
            color,
            (int(center[0]),int(center[1])),
            radius,
            thickness,
        )

    # draw circle with text in it.
    # drawPos = postion example smartdisplay.RIGHT_MID for right middle of display.
    # radius of circle.
    # justify (the text): 0=left justify text, 1=right, 2= center in circle.
    def draw_circle_text( self, pos, font, text, textcolor, radius , linecolor, thickness,posAdjustment=(0,0),justify=0):
        newSurface = pygame.Surface((radius*2, radius*2))
        if(font==None): font = self.font
        label = font.render(text, 1, textcolor)
        ylabelStart = (radius) - label.get_height() /2
        pygame.draw.circle(
            newSurface,
            linecolor,
            (radius,radius),
            radius,
            thickness,
        )
        if justify==0:
            newSurface.blit(label, (0,ylabelStart))
        elif justify==1:
            newSurface.blit(label, (newSurface.get_width()-label.get_width(),ylabelStart))
        elif justify==2:
            newSurface.blit(label, (newSurface.get_width()/2-label.get_width()/2,ylabelStart))
        self.blit_next(newSurface,pos,posAdjustment)

    def init_batch_programs(self):
        """Initialize shader programs for batch rendering"""
        # Program for colored primitives (lines, rects)
        self.color_program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                in vec3 in_color;
                out vec3 v_color;
                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(v_color, 1.0);
                }
            '''
        )

        # Keep existing text_program for text rendering

        # Initialize batch buffers
        self.batch_lines = []
        self.batch_rects = []
        self.batch_texts = []

    def gl_tv_line_batch(self, color, start_pos, end_pos, thickness=1):
        """Add line to batch"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        color_norm = [c/255 for c in color]
        
        # Store normalized coordinates and color
        self.batch_lines.append({
            'pos': (x1, y1, x2, y2),
            'color': color_norm,
            'thickness': thickness
        })

    def gl_tv_rect_batch(self, color, rect, thickness=0):
        """Add rectangle to batch"""
        self.batch_rects.append({
            'rect': rect,
            'color': [c/255 for c in color],
            'thickness': thickness
        })

    def gl_tv_text_batch(self, text, x, y, font=None, color=(255,255,255)):
        """Add text to batch"""
        if font is None:
            font = self.font
        
        self.batch_texts.append({
            'text': text,
            'pos': (x, y),
            'font': font,
            'color': color
        })

    def render_batches(self):
        """Render all batched elements efficiently"""
        
        # 1. Render filled rectangles
        filled_rects = [r for r in self.batch_rects if r['thickness'] == 0]
        if filled_rects:
            vertices = []
            colors = []
            for rect in filled_rects:
                x, y, width, height = rect['rect']
                x_norm = (x / self.width) * 2 - 1
                y_norm = -((y / self.height) * 2 - 1)
                width_norm = (width / self.width) * 2
                height_norm = (height / self.height) * 2
                
                # Add vertices for rectangle
                quad = [
                    (x_norm, y_norm),
                    (x_norm + width_norm, y_norm),
                    (x_norm + width_norm, y_norm - height_norm),
                    (x_norm, y_norm - height_norm),
                ]
                vertices.extend([coord for point in quad for coord in point])
                colors.extend(rect['color'] * 4)  # Same color for all 4 vertices

            # Create and bind buffers
            vbo = self.ctx.buffer(array('f', vertices))
            cbo = self.ctx.buffer(array('f', colors))
            vao = self.ctx.vertex_array(
                self.color_program, 
                [
                    (vbo, '2f', 'in_position'),
                    (cbo, '3f', 'in_color'),
                ]
            )
            vao.render(mode=self.ctx.TRIANGLE_FAN)
            vbo.release()
            cbo.release()

        # 2. Render all lines
        if self.batch_lines:
            vertices = []
            colors = []
            for line in self.batch_lines:
                x1, y1, x2, y2 = line['pos']
                thickness = line['thickness']
                
                # Convert to normalized coordinates
                x1_norm = (x1 / self.width) * 2 - 1
                y1_norm = -((y1 / self.height) * 2 - 1)
                x2_norm = (x2 / self.width) * 2 - 1
                y2_norm = -((y2 / self.height) * 2 - 1)
                
                # Calculate normal vector for thickness
                dx = x2_norm - x1_norm
                dy = y2_norm - y1_norm
                length = math.sqrt(dx*dx + dy*dy)
                if length == 0:
                    continue
                    
                nx = -dy/length * (thickness/self.width) * 2
                ny = dx/length * (thickness/self.height) * 2
                
                # Add vertices for thick line
                quad = [
                    (x1_norm + nx, y1_norm + ny),
                    (x2_norm + nx, y2_norm + ny),
                    (x2_norm - nx, y2_norm - ny),
                    (x1_norm - nx, y1_norm - ny),
                ]
                vertices.extend([coord for point in quad for coord in point])
                colors.extend(line['color'] * 4)

            # Create and bind buffers
            vbo = self.ctx.buffer(array('f', vertices))
            cbo = self.ctx.buffer(array('f', colors))
            vao = self.ctx.vertex_array(
                self.color_program, 
                [
                    (vbo, '2f', 'in_position'),
                    (cbo, '3f', 'in_color'),
                ]
            )
            vao.render(mode=self.ctx.TRIANGLE_FAN)
            vbo.release()
            cbo.release()

        # 3. Render all text
        # Sort texts by font to minimize texture switches
        sorted_texts = sorted(self.batch_texts, key=lambda x: id(x['font']))
        current_font = None
        current_vertices = []
        current_colors = []
        
        for text_obj in sorted_texts:
            if text_obj['font'] != current_font:
                # Render accumulated text with previous font
                if current_vertices:
                    self._render_text_batch(current_vertices, current_colors, current_font)
                    current_vertices = []
                    current_colors = []
                current_font = text_obj['font']
                
            # Add text vertices and colors to current batch
            text_surface = current_font.render(text_obj['text'], True, text_obj['color'])
            # Add vertices and texture coordinates...
            # (Similar to existing gl_tv_text implementation)

        # Render final text batch
        if current_vertices:
            self._render_text_batch(current_vertices, current_colors, current_font)

        # Clear batches
        self.batch_lines = []
        self.batch_rects = []
        self.batch_texts = []

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python

