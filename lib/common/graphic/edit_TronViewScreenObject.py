import pygame
import random
import string
from lib.common.graphic.edit_EditToolBar import EditToolBar
import time
from lib.common.graphic.edit_find_module import find_module
from lib.common import shared
class TronViewScreenObject:
    def __init__(self, pgscreen, type, title, module=None, x=0, y=0, width=100, height=100, id=None):
        self.pygamescreen = pgscreen
        self.type = type
        self.title = title
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False
        self.id = id or 'M_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        self.showBounds = False
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        self.showOptions = False
        self.debug_font = pygame.font.SysFont("monospace", 25, bold=False)
        
        if type == 'group':
            self.childScreenObjects = []
            self.module = None
        else:
            # create a module object
            if module is not None:
                self.setModule(module)
            else:
                self.module = None

        self.edit_toolbar = EditToolBar(self)

    def isClickInside(self, mx, my):
        return self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def setShowBounds(self, show):
        self.showBounds = show
        if self.type == 'group':
            for module in self.childScreenObjects:
                module.showBounds = self.showBounds

    def draw(self, aircraft, smartdisplay):
        if self.module is None and self.type == 'module':
            boxColor = (140, 0, 0)
            if self.selected:
                boxColor = (255, 255, 0)
            # draw a rect for the module with a x through it.
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x, self.y, self.width, self.height), 1)
            #text = pygame.font.SysFont("monospace", 25, bold=False).render("X", True, (255, 255, 255))
            #self.pygamescreen.blit(text, (self.x + self.width/2 - 5, self.y + self.height/2 - 5))
            # draw a little resize handle in the bottom right corner
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            return
        
        if self.type == 'group':
            if len(self.childScreenObjects) == 0:
                # draw a rect for the group with a gray background
                pygame.draw.rect(self.pygamescreen, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)
                return
            # Draw group outline
            if self.showBounds:
                min_x = min(m.x for m in self.childScreenObjects)
                min_y = min(m.y for m in self.childScreenObjects)
                max_x = max(m.x + m.width for m in self.childScreenObjects)
                max_y = max(m.y + m.height for m in self.childScreenObjects)
                pygame.draw.rect(self.pygamescreen, (255, 150, 0), (min_x-5, min_y-5, max_x-min_x+10, max_y-min_y+10), 2)

            # Draw contained modules
            for module in self.childScreenObjects:
                module.draw(aircraft, smartdisplay)
        else:
            start_time = time.time()
            self.module.draw(aircraft, smartdisplay, (self.x, self.y))
            end_time = time.time()
            self.draw_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Draw selection box and title
        if self.selected:
            color = (0, 255, 0)
            pygame.draw.rect(self.pygamescreen, color, (self.x, self.y, self.width, self.height), 1)
            pygame.draw.rect(self.pygamescreen, color, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            self.edit_toolbar.draw(self.pygamescreen)
        elif self.showBounds:
            pygame.draw.rect(self.pygamescreen, (70, 70, 70), (self.x-5, self.y-5, self.width+10, self.height+10), 2)

        # At the end of the draw method
        if aircraft.show_FPS and hasattr(self, 'draw_time'):
            time_text = f"{self.draw_time:.2f}ms"
            time_surface = self.debug_font.render(time_text, True, (255, 255, 255))
            time_rect = time_surface.get_rect(bottomleft=(self.x + 5, self.y + self.height - 5))
            self.pygamescreen.blit(time_surface, time_rect)

    def resize(self, width, height):
        if self.type != 'group':
            if width < 40: width = 40
            if height < 40: height = 40
            self.width = width
            self.height = height
            if hasattr(self.module, "initMod"):
                self.module.initMod(self.pygamescreen, width, height)
            if hasattr(self.module, "setup"):
                self.module.setup()
            if hasattr(self.module, "resize"):
                self.module.resize(width, height)
        if self.type == 'group':
            print("Resizing group: %s to %d, %d (old size %d, %d)" % (self.title, width, height, self.width, self.height))
            # resize all modules in the group by difference
            dx = width - self.width
            dy = height - self.height
            for module in self.childScreenObjects:
                module.resize(module.width + dx, module.height + dy)
            self.generateBounds()
    
    def move(self, x, y):
        # figure out the difference in x and y from the current position to the new position
        if self.type != 'group':
            self.x = x
            self.y = y
        if self.type == 'group': # move all children of the group
            dx = x - self.x
            dy = y - self.y
            self.x = x
            self.y = y
            for childSObj in self.childScreenObjects:
                childSObj.move(childSObj.x + dx, childSObj.y + dy) # move the module
            self.generateBounds()

    def setModule(self, module, showOptions = True, width = None, height = None):
        if self.type == 'group':
            print("Cannot set module for a group type ScreenObject")
            return
        self.type = 'module'
        self.module = module
        self.title = module.name
        if width is None or height is None:
            self.module.initMod(self.pygamescreen) # use default width and height
        else:
            self.module.initMod(self.pygamescreen, width, height)
        self.width = self.module.width # then get the actual width and height from the module. it may have changed.
        self.height = self.module.height
        if hasattr(self.module, "setup"):
            self.module.setup()
        self.edit_toolbar = EditToolBar(self)
        if showOptions:
            self.showOptions = True

    def addChildScreenObject(self, sObject):
        if self.type != 'group':
            raise ValueError("Cannot add screen object to a non-group type screenObject")
        if sObject not in self.childScreenObjects:
            self.childScreenObjects.append(sObject)
        self.generateBounds()

    def removeChildScreenObject(self, sObject):
        if self.type != 'group':
            raise ValueError("Cannot remove screen object from a non-group type")
        self.childScreenObjects.remove(sObject)
        self.generateBounds()

    def generateBounds(self): # generate bounds for the group (the smallest rectangle that contains all the child modules)
        if self.type != 'group':
            return
        # generate bounds for the group
        self.x = min(m.x for m in self.childScreenObjects)
        self.y = min(m.y for m in self.childScreenObjects)
        # find the module that is the furthest to the right and down
        modMostRight = None
        modMostDown = None
        for childSObj in self.childScreenObjects:
            if modMostRight is None or childSObj.x + childSObj.width > modMostRight.x + modMostRight.width:
                modMostRight = childSObj
            if modMostDown is None or childSObj.y + childSObj.height > modMostDown.y + modMostDown.height:
                modMostDown = childSObj
        self.width = modMostRight.x + modMostRight.width - self.x
        self.height = modMostDown.y + modMostDown.height - self.y
        #print("Generated bounds for group: %s x:%d y:%d w:%d h:%d" % (self.title, self.x, self.y, self.width, self.height))

    def to_dict(self):
        # save everything about this object to json. modules, 
        data = {
            "type": self.type,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
        if self.module:
            data["module"] = {
                "name": self.module.name,
                "options": []
            }
            if hasattr(self.module, "get_module_options"):
                options = self.module.get_module_options()
                for option, details in options.items():
                    data["module"]["options"].append({
                    "name": option,
                    "value": getattr(self.module, option)
                })

        if self.type == 'group' and self.childScreenObjects:
            data["screenObjects"] = []
            for childSObj in self.childScreenObjects:
                data["screenObjects"].append(childSObj.to_dict())
        if self.id:
            data["id"] = self.id

        return data
    def from_dict(self, data):
        self.type = data['type']
        self.title = data['title']
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        if self.type == 'group' and data['screenObjects']:
            self.childScreenObjects = []
            for childSObj in data['screenObjects']:
                new_childSObj = TronViewScreenObject(
                    self.pygamescreen,
                    childSObj['type'],
                    childSObj['title'],
                )
                new_childSObj.from_dict(childSObj)
                self.addChildScreenObject(new_childSObj)
        if self.type == 'module':
            # load the module and options
            newModules, titles  = find_module(self.title)
            self.setModule(newModules[0], showOptions = False, width = data['width'], height = data['height'])
            
            # now load the options
            if hasattr(self.module, "get_module_options"):
                for option in data['module']['options']:
                    try:
                        setattr(self.module, option['name'], option['value'])
                        # if the option has a post_change_function, call it. check newModules[0].get_module_options()
                        if 'post_change_function' in newModules[0].get_module_options()[option['name']]:
                            post_change_function = getattr(self.module, newModules[0].get_module_options()[option['name']]['post_change_function'], None)
                            if post_change_function:
                                post_change_function()
                    except Exception as e:
                            print("Error setting module (%s) option (%s): %s" % (self.module.name, option['name'], e))

    def center(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

    def align_left(self):
        self.x = 0
    def align_right(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = screen_width - self.width
