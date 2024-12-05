#!/usr/bin/env python
import os
import re
import pygame

COLOR_INACTIVE = (100, 100, 100)
COLOR_ACTIVE = (255, 255, 255)
COLOR_LIST_INACTIVE = (100, 100, 100)
COLOR_LIST_ACTIVE = (255, 255, 255)

############################################################################################
############################################################################################
# DropDown class used to pick the module from the list of modules.
class DropDownOption:
    def __init__(self, text, submenu=None):
        self.text = text
        self.submenu = submenu  # List of DropDownOption objects or None
        self.rect = None  # Will store the pygame.Rect for this option
        self.is_expanded = False  # Track if submenu is expanded

class DropDown():
    def __init__(self, color_menu=[COLOR_INACTIVE, COLOR_ACTIVE],
                color_option=[COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
                x=0, y=0, w=140, h=30, 
                font=None, 
                main="Select Option", 
                options=[], 
                menuTitle=None,
                callback=None,
                showButton=False,
                storeObject=[]):
        
        self.menuTitle = menuTitle
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font if font else pygame.font.SysFont(None, 25)
        self.main = main
        self.options = self._convert_options(options)  # Convert plain options to DropDownOption objects
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.value = None
        self.visible = False
        self.option_rects = []  # Store rectangles for each option
        self.callback = callback
        self.showButton = showButton
        self.storeObject = storeObject
        self.submenu_indicator = ">"  # Symbol to indicate submenu presence
        self.expanded_indicator = ""  # Symbol to indicate expanded submenu

    def _convert_options(self, options):
        """Convert plain options to DropDownOption objects"""
        converted = []
        for opt in options:
            if isinstance(opt, (list, tuple)):
                # If option is a list/tuple, first item is text, second is submenu
                converted.append(DropDownOption(opt[0], self._convert_options(opt[1])))
            elif isinstance(opt, str):
                converted.append(DropDownOption(opt))
            elif isinstance(opt, DropDownOption):
                converted.append(opt)
        return converted

    def draw(self, surf):
        screen_width = surf.get_width()
        screen_height = surf.get_height()
        eachOptionHeight = 20
        
        if self.showButton:
            pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
            msg = self.font.render(self.main, 1, (0, 0, 0))
            surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            self._draw_menu_options(surf, self.options, self.rect.x, self.rect.y + self.rect.height)

    def _draw_menu_options(self, surf, options, start_x, start_y, level=0):
        """Recursively draw menu options and their submenus"""
        screen_width = surf.get_width()
        screen_height = surf.get_height()
        current_y = start_y
        current_x = start_x
        indent = level * 20  # Indentation for submenu items
        
        # Draw menu title if it exists and we're at the top level
        if self.menuTitle and level == 0:
            title_surface = self.font.render(self.menuTitle, True, (255, 255, 255))
            title_rect = title_surface.get_rect()
            title_rect.midtop = (start_x + self.rect.width // 2, start_y - 25)
            # Draw a background for the title
            bg_rect = title_rect.inflate(20, 10)
            pygame.draw.rect(surf, self.color_menu[0], bg_rect)
            surf.blit(title_surface, title_rect)
            
        # First check if menu would go off right edge of screen
        if start_x + self.rect.width > screen_width - 10:
            # Move menu to the left of the click position
            start_x = screen_width - self.rect.width - 10
            current_x = start_x
        
        # Calculate total height needed
        total_height = len(options) * self.rect.height
        available_height = screen_height - 20  # Leave 10px margin top and bottom
        
        # If menu would go off bottom of screen
        if start_y + total_height > screen_height - 10:
            # First try to move the menu up
            new_start_y = screen_height - total_height - 10
            
            # If moving up would put us above top margin, use columns
            if new_start_y < 10:
                # Use columns since we can't fit vertically
                max_items_per_column = (screen_height - 20) // self.rect.height
                if max_items_per_column < 1:
                    max_items_per_column = 1
                total_columns = (len(options) + max_items_per_column - 1) // max_items_per_column
                total_width = total_columns * self.rect.width
                
                # Adjust start_x if multi-column menu would go off right edge
                if start_x + total_width > screen_width:
                    start_x = screen_width - total_width - 10
                current_x = start_x
                start_y = 10  # Start at top margin when using columns
            else:
                # We can fit by moving up
                start_y = new_start_y
            current_y = start_y
        
        # Ensure we don't go off the top
        if start_y < 10:
            start_y = 10
            current_y = start_y
        
        for i, option in enumerate(options):
            # Start new column only if we're using columns and reached max items
            if total_height > available_height and i > 0 and i % max_items_per_column == 0:
                current_y = start_y
                current_x += self.rect.width
            
            # Create rectangle for this option
            option_rect = pygame.Rect(current_x + indent, current_y, self.rect.width - indent, self.rect.height)
            option.rect = option_rect
            
            # Draw option background
            is_active = self.active_option == (level, i)
            pygame.draw.rect(surf, self.color_option[1 if is_active else 0], option_rect, 0)
            
            # Draw option text
            text = option.text
            if option.submenu:
                text = f"{text} {self.expanded_indicator if option.is_expanded else self.submenu_indicator}"
            
            msg = self.font.render(text, 1, (0, 0, 0))
            surf.blit(msg, msg.get_rect(midleft=(option_rect.left + 5, option_rect.centery)))
            
            # If this option has a submenu and is expanded, draw it
            if option.submenu and option.is_expanded:
                submenu_x = current_x + self.rect.width - indent
                
                # If submenu would go off right edge, draw it to the left instead
                if submenu_x + self.rect.width > screen_width:
                    submenu_x = current_x - self.rect.width + indent
                
                next_y = self._draw_menu_options(surf, option.submenu, 
                                             submenu_x, current_y + self.rect.height, 
                                             level + 1)
                # Only update current_y if we're in the same column
                if total_height > available_height and i % max_items_per_column == max_items_per_column - 1:
                    current_y = start_y
                else:
                    current_y = next_y
            else:
                current_y += self.rect.height
                
        return current_y

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        # Update active option based on mouse position
        self.active_option = self._find_active_option(mpos, self.options)
        
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                    self.visible = not self.visible
                elif self.draw_menu:
                    clicked_option = self._handle_click(mpos, self.options)
                    if clicked_option is not None:
                        if not clicked_option.submenu:  # Only close menu if leaf option selected
                            self.draw_menu = False
                            self.visible = False
                            # get the index number of the clicked option
                            index = self.options.index(clicked_option)
                            if self.callback:
                                self.callback(index, clicked_option.text)
                            return index,clicked_option.text
                    else:
                        self.draw_menu = False
                        self.visible = False
        return -1, None

    def _find_active_option(self, pos, options, level=0):
        """Recursively find which option the mouse is hovering over"""
        for i, option in enumerate(options):
            if option.rect and option.rect.collidepoint(pos):
                return (level, i)
            if option.submenu and option.is_expanded:
                submenu_active = self._find_active_option(pos, option.submenu, level + 1)
                if submenu_active != -1:
                    return submenu_active
        return -1

    def _handle_click(self, pos, options):
        """Handle click on menu options, returns clicked option or None"""
        for option in options:
            if option.rect and option.rect.collidepoint(pos):
                if option.submenu:
                    option.is_expanded = not option.is_expanded
                return option
            if option.submenu and option.is_expanded:
                submenu_result = self._handle_click(pos, option.submenu)
                if submenu_result:
                    return submenu_result
        return None

    def add_submenu(self, parent_text, submenu_options):
        """Add a submenu to an existing option"""
        for option in self.options:
            if option.text == parent_text:
                option.submenu = self._convert_options(submenu_options)
                break

    def load_file_dir_as_options(self, path, ignore_regex=None, sort=True):
        # Get file names and convert them to DropDownOption objects
        self.options = [
            DropDownOption(os.path.splitext(os.path.basename(f))[0])
            for f in os.listdir(path) 
            if os.path.isfile(os.path.join(path, f)) 
            and (not ignore_regex or not re.match(ignore_regex, f))
        ]
        if sort:
            self.options.sort(key=lambda x: x.text)

    def insert_option(self, option, index):
        self.options.insert(index, DropDownOption(option))
        self.option_rects.insert(index, pygame.Rect(0, 0, self.rect.width, self.rect.height))

    def is_option_clicked(self, pos):
        """Check if mouse position is inside any option rectangle"""
        if not self.draw_menu:
            return -1
            
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                return i
        return -1

    def toggle(self):
        self.draw_menu = not self.draw_menu
        self.visible = not self.visible


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python