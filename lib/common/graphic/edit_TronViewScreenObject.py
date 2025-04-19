import pygame
import random
import string
from lib.common.graphic.edit_EditToolBar import EditToolBar
import time
from lib.common.graphic.edit_find_module import find_module
from lib.common import shared
class TronViewScreenObject:
    def __init__(self, pgscreen, type, title, module=None, x=0, y=0, width=100, height=100, id=None):
        self.pygamescreen = shared.pygamescreen
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
        self.showEvents = False
        self.debug_font = pygame.font.SysFont("monospace", 15, bold=False)
        
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

    def click(self, aircraft, mx, my):
        #print("Click on %s at %d, %d" % (self.title, mx, my))
        if hasattr(self.module, "processClick"):
            self.module.processClick(aircraft, mx, my)
    
    def mouseWheel(self, aircraft, mx, my, wheel_position):
        if hasattr(self.module, "processMouseWheel"):
            self.module.processMouseWheel(aircraft, mx, my, wheel_position)

    def setShowBounds(self, show):
        self.showBounds = show
        if self.type == 'group':
            for module in self.childScreenObjects:
                module.showBounds = self.showBounds

    def draw(self, dataship, smartdisplay, showToolBar = True):
        # if no module then draw a red box around the screen object
        if self.module is None and self.type == 'module':
            boxColor = (140, 0, 0)
            if self.selected:
                boxColor = (255, 255, 0)
            # draw a rect for the module
            pygame.draw.rect(self.pygamescreen, boxColor, (self.x, self.y, self.width, self.height), 1)
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
                module.draw(dataship, smartdisplay)
        else:
            if shared.CurrentScreen.show_FPS:
                start_time = time.time()
                self.module.draw(dataship, smartdisplay, (self.x, self.y))
                end_time = time.time()
                self.draw_time = (end_time - start_time) * 1000  # Convert to milliseconds
                time_text = f"{self.draw_time:.2f}ms"
                time_surface = self.debug_font.render(time_text, True, (255, 255, 255), (0, 0, 0, 0), pygame.SRCALPHA)
                time_rect = time_surface.get_rect(bottomleft=(self.x + 5, self.y + self.height - 5))
                self.pygamescreen.blit(time_surface, time_rect)
            else:
                self.module.draw(dataship, smartdisplay, (self.x, self.y))


        # Draw selection box and title
        if self.selected:
            color = (0, 255, 0)
            pygame.draw.rect(self.pygamescreen, color, (self.x, self.y, self.width, self.height), 1)
            pygame.draw.rect(self.pygamescreen, color, (self.x + self.width - 10, self.y + self.height - 10, 10, 10), 1)
            if showToolBar:
                self.edit_toolbar.draw(self.pygamescreen)
        elif self.showBounds:
            pygame.draw.rect(self.pygamescreen, (70, 70, 70), (self.x-5, self.y-5, self.width+10, self.height+10), 2)


    def resize(self, width, height):
        if self.type != 'group':
            if width < 10: width = 10
            if height < 10: height = 10
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

    # save everything about this object to json. modules, 
    def to_dict(self):
        # save everything about this object to json. modules, 
        # get the grid position
        anchor_manager = GridAnchorManager(self.pygamescreen, self.pygamescreen.get_size()[0], self.pygamescreen.get_size()[1])
        anchor_manager.set_object_grid_position(self)
        data = {
            "type": self.type,
            "title": self.title,
            "x": self.x,
            "y": int(self.y),
            "width": int(self.width),
            "height": int(self.height),
            "grid_position": self.grid_position,
            "grid_percentage_x": self.grid_percentage_x,
            "grid_percentage_y": self.grid_percentage_y,
        }
        if self.module:
            data["module"] = {
                "name": self.module.name,
                "options": []
            }
            if hasattr(self.module, "get_module_options"):
                options = self.module.get_module_options()
                for option, details in options.items():
                    value = getattr(self.module, option)
                    # Handle custom objects that have to_dict method
                    if hasattr(value, 'to_dict') and callable(value.to_dict):
                        option_value = value.to_dict()
                    else:
                        option_value = value
                    data["module"]["options"].append({
                        "name": option,
                        "value": option_value
                    })

        if self.type == 'group' and self.childScreenObjects:
            data["screenObjects"] = []
            for childSObj in self.childScreenObjects:
                data["screenObjects"].append(childSObj.to_dict())
        if self.id:
            data["id"] = self.id

        if hasattr(self, 'event_handlers'):
            data["event_handlers"] = self.event_handlers

        return data
    
    # load the data from the json file
    def from_dict(self, data, load_grid_position = True):
        self.type = data['type']
        self.title = data['title']
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        
        if self.type == 'module':
            # Load the module first
            newModules, titles = find_module(self.title)
            self.setModule(newModules[0], showOptions=False, width=self.width, height=self.height)
            
            # Batch process all options before calling initMod again
            if 'module' in data and 'options' in data['module'] and hasattr(self.module, "get_module_options"):
                module_options = self.module.get_module_options()
                post_change_functions = []  # Store functions to call after all options are set
                
                for option in data['module']['options']:
                    try:
                        option_name = option['name']
                        option_value = option['value']
                        
                        # Set the option value directly
                        setattr(self.module, option_name, option_value)
                        
                        # Store post_change_function if it exists
                        if (option_name in module_options and 
                            'post_change_function' in module_options[option_name]):
                            func_name = module_options[option_name]['post_change_function']
                            post_func = getattr(self.module, func_name, None)
                            if post_func and post_func not in post_change_functions:
                                post_change_functions.append(post_func)
                                
                    except Exception as e:
                        print(f"NOTICE: setting module ({self.module.name}) option ({option_name}): {str(e)}")
                
                # Initialize module with final dimensions
                self.module.initMod(self.pygamescreen, self.width, self.height)
                
                # Call post-change functions once after all options are set
                for func in post_change_functions:
                    try:
                        #check if function can take a argument
                        if hasattr(func, '__call__'):
                            func()
                        else:
                            func("on_load")  # tell the function we are loading the module from a json file
                    except Exception as e:
                        print(f"NOTICE: error calling post_change_function: {str(e)}")

        if self.type == 'group' and data['screenObjects']:
            self.childScreenObjects = []
            for childSObj in data['screenObjects']:
                new_childSObj = TronViewScreenObject(
                    self.pygamescreen,
                    childSObj['type'],
                    childSObj['title'],
                )
                new_childSObj.from_dict(childSObj, load_grid_position = False) # don't load the grid position for the children
                self.addChildScreenObject(new_childSObj)
        
        # now set the position based on the grid position
        # we want to do this after all the other child modules are loaded (for groups..)  So a group can be positioned correctly based off the total size.
        if load_grid_position:
            if 'grid_position' in data:  # if the grid position is in the json, then calculate the x,y
                self.grid_position = data['grid_position']
                self.grid_percentage_x = data['grid_percentage_x']
                self.grid_percentage_y = data['grid_percentage_y']
                # calculate the grid position using AnchorManager.calculate_grid_position()
                anchor_manager = GridAnchorManager(self.pygamescreen, self.pygamescreen.get_size()[0], self.pygamescreen.get_size()[1])
                x_diff, y_diff = anchor_manager.set_object_position_from_grid_percentage(self)
                #print("%s Calculated Grid position: %s" % (self.title, self.grid_position))
                if self.type == 'group':
                    print("Group %s calculated grid position: %s x:%d y:%d" % (self.title, self.grid_position, self.x, self.y))
                    self.move(self.x + x_diff, self.y + y_diff) # move the group to the new position

        if 'event_handlers' in data:
            self.event_handlers = data['event_handlers']

    def center(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

    def align_left(self):
        self.x = 0
    def align_right(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = screen_width - self.width


class GridAnchorManager:
    def __init__(self, pgscreen, screen_width, screen_height):
        self.pgscreen = pgscreen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grids = []
        self.grid_labels = [
            "TopL", "TopM", "TopR",
            "MidL", "MidM", "MidR",
            "BotL", "BotM", "BotR"
        ]

        grid_width = screen_width / 3
        grid_height = screen_height / 3
        
        for i, label in enumerate(self.grid_labels):
            x = (i % 3) * grid_width
            y = (i // 3) * grid_height
            self.grids.append({
                'rect': pygame.Rect(x, y, grid_width, grid_height),
                'label': label
            })
                
        #print("Anchor grid set: %d grids" % len(self.grids), self.screen_width, self.screen_height)
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

    # set the grid position and percentage based on the screen object's x,y
    def set_object_grid_position(self, screen_object):
        # generate the grid_position and grid_percentage_x and grid_percentage_y
        for grid in self.grids:
            if grid['rect'].collidepoint(screen_object.x + screen_object.width/2, screen_object.y + screen_object.height/2):
                screen_object.grid_position = grid['label']
                screen_object.grid_percentage_x = (screen_object.x + screen_object.width/2 - grid['rect'].x) / (grid['rect'].width/2)
                screen_object.grid_percentage_y = (screen_object.y + screen_object.height/2 - grid['rect'].y) / (grid['rect'].height/2)
        
        # if no grid position then use the center of the screen. and find the grid_percentage_x and grid_percentage_y based on that.
        if not hasattr(screen_object, 'grid_position'):
            screen_object.grid_position = 'MidM'
            screen_object.grid_percentage_x = (screen_object.x + screen_object.width/2 - self.screen_width/2) / (self.screen_width/2)
            screen_object.grid_percentage_y = (screen_object.y + screen_object.height/2 - self.screen_height/2) / (self.screen_height/2)

    def set_object_position_from_grid_percentage(self, screen_object):
        # based on screen_object.grid_postion and grid_percentage_x and grid_percentage_y
        #print("checking grid position: %s" % screen_object.grid_position)
        x_diff = 0
        y_diff = 0
        x_original = screen_object.x
        y_original = screen_object.y
        if hasattr(screen_object, 'grid_position'):
            for grid in self.grids:
                if grid['label'] == screen_object.grid_position:
                    center_object_x = screen_object.width/2
                    center_object_y = screen_object.height/2
                    # use the percentage to move the screen object. use the center of the screen object and the center of the grid
                    screen_object.x = int(grid['rect'].x + (screen_object.grid_percentage_x * grid['rect'].width/2) - screen_object.width/2)
                    screen_object.y = int(grid['rect'].y + (screen_object.grid_percentage_y * grid['rect'].height/2) - screen_object.height/2)
                    #print("size updated:%s %s x:%d y:%d" % (screen_object.title, screen_object.grid_position, screen_object.x, screen_object.y))
                    #screen_object.move(screen_object.x, screen_object.y)
                    if screen_object.x < 0: # don't let the screen object go off the left side of the screen
                        screen_object.x = 0
                    if screen_object.y < 0: # don't let the screen object go off the top of the screen
                        screen_object.y = 0
                    x_diff = screen_object.x - x_original
                    y_diff = screen_object.y - y_original

        return x_diff, y_diff

    def anchor_draw(self, selected_screen_objects):
        # draw the grid lines
        for grid in self.grids:
            pygame.draw.rect(self.pgscreen, (70, 70, 70), grid['rect'], 1)
                    
        in_grid = None

        # draw the grid box around the selected screen object
        for selected_screen_object in selected_screen_objects:
            for grid in self.grids:
                if grid['rect'].collidepoint(selected_screen_object.x + selected_screen_object.width/2, selected_screen_object.y + selected_screen_object.height/2):
                    pygame.draw.rect(self.pgscreen, (60, 255, 40), grid['rect'], 2)
                    in_grid = grid
                    # draw the grid label in the center of the grid
                    label_surface = self.font.render(in_grid['label'], True, (200, 200, 200, 60))
                    label_rect = label_surface.get_rect(center=in_grid['rect'].center)
                    self.pgscreen.blit(label_surface, label_rect)
        
        # get the percentage of distance from center of screen object to center of selected grid
        # and draw a line from the screen object to the grid
        for selected_screen_object in selected_screen_objects:
            for grid in self.grids:
                if grid == in_grid:
                    center_object_x = selected_screen_object.width/2
                    center_object_y = selected_screen_object.height/2
                    distance_x = (selected_screen_object.x + center_object_x) - grid['rect'].center[0]
                    distance_y = (selected_screen_object.y + center_object_y) - grid['rect'].center[1]
                    percentage_x = distance_x / (grid['rect'].width/2)
                    percentage_y = distance_y / (grid['rect'].height/2)

                    # draw a line from the screen object to the grid
                    pygame.draw.line(self.pgscreen, (200, 200, 200), (selected_screen_object.x + selected_screen_object.width/2, selected_screen_object.y + selected_screen_object.height/2), grid['rect'].center, 1)
                    # draw the percentage on the line
                    percentage_text = self.font.render(f"x:{percentage_x:.0%} y:{percentage_y:.0%}", True, (200, 200, 200))
                    percentage_rect = percentage_text.get_rect(center=((selected_screen_object.x + selected_screen_object.width/2 + grid['rect'].center[0])/2, (selected_screen_object.y + selected_screen_object.height/2 + grid['rect'].center[1])/2))
                    self.pgscreen.blit(percentage_text, percentage_rect)
