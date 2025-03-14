#!/usr/bin/env python
# edit_dropdown.py
# Topher 2025
# A dropdown menu.  supports submenus and lambda callbacks.
############################################################################################
############################################################################################
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
'''
Example of submenu structure:
                        options = [
                            "Option 1",
                            ["Submenu 1", [
                                "Submenu 1.1",
                                "Submenu 1.2",
                                ["Submenu 1.3", [
                                    "Submenu 1.3.1",
                                    "Submenu 1.3.2"
                                ]]
                            ]],
                            "Option 2",
                            ["Submenu 2", [
                                "Submenu 2.1",
                                "Submenu 2.2"
                            ]]
                        ]

'''
class DropDownOption:
    def __init__(self, text, submenu=None):
        self.text = text
        self.submenu = submenu  # List of DropDownOption objects or None
        self.rect = None  # Will store the pygame.Rect for this option
        self.is_expanded = False  # Track if submenu is expanded

class DropDown():
    def __init__(self, 
                 id,
                color_menu=[COLOR_INACTIVE, COLOR_ACTIVE],
                color_option=[COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
                x=0, y=0, w=140, h=30, 
                font=None, 
                main="Select Option", 
                options=[], 
                menuTitle=None,
                callback=None,
                showButton=False,
                storeObject=[]):

        self.id = id # id of the dropdown
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
        self.current_path = []  # Track the current submenu path
        self.last_mouse_pos = pygame.mouse.get_pos()  # Track last mouse position
        self.keyboard_navigation_active = False  # Track if keyboard navigation is active

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
        
        # Calculate maximum width needed for this level
        max_width = self.rect.width
        for option in options:
            text = option.text
            if option.submenu:
                text = f"{text} {self.submenu_indicator}"
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_width = text_surface.get_width() + 10  # Add padding
            max_width = max(max_width, text_width + indent)
        
        # Draw menu title if it exists and we're at the top level
        if self.menuTitle and level == 0:
            title_surface = self.font.render(self.menuTitle, True, (255, 255, 255))
            title_width = title_surface.get_width() + 20  # Add padding
            max_width = max(max_width, title_width)
            title_rect = title_surface.get_rect()
            title_rect.midtop = (start_x + max_width // 2, start_y - 25)
            # Draw a background for the title
            bg_rect = title_rect.inflate(20, 10)
            pygame.draw.rect(surf, self.color_menu[0], bg_rect)
            surf.blit(title_surface, title_rect)
        
        # First check if menu would go off right edge of screen
        if start_x + max_width > screen_width - 10:
            # Move menu to the left of the click position
            start_x = screen_width - max_width - 10
            current_x = start_x
        
        # Calculate total height needed for this level only
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
                current_x += max_width
            
            # Create rectangle for this option using the calculated max_width
            option_rect = pygame.Rect(current_x + indent, current_y, max_width - indent, self.rect.height)
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
                submenu_x = current_x + max_width - indent
                
                # If submenu would go off right edge, draw it to the left instead
                if submenu_x + max_width > screen_width:
                    submenu_x = current_x - max_width + indent
                
                self._draw_menu_options(surf, option.submenu, 
                                      submenu_x, option_rect.y,  # Start submenu at same Y as parent
                                      level + 1)
            
            # Always increment current_y for next item in this level
            current_y += self.rect.height
                
        return current_y

    def _handle_keyboard_navigation(self, event):
        """Handle keyboard navigation for dropdown menu"""
        if not self.draw_menu:
            return
            
        if event.key == pygame.K_UP:
            # Handle tuple structure of active_option
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                if index > 0:
                    self.active_option = (level, index - 1)
                    self.keyboard_navigation_active = True
            elif self.active_option == -1 and self.options:
                # If no option is active, select the last option
                self.active_option = (0, len(self.options) - 1)
                self.keyboard_navigation_active = True
                
        elif event.key == pygame.K_DOWN:
            # Handle tuple structure of active_option
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                # Need to check if we're at the end of the current level's options
                current_options = self.options
                for _ in range(level):
                    if not current_options:
                        break
                    # Navigate to the correct submenu level
                    for opt in current_options:
                        if opt.is_expanded and opt.submenu:
                            current_options = opt.submenu
                            break
                if current_options and index < len(current_options) - 1:
                    self.active_option = (level, index + 1)
                    self.keyboard_navigation_active = True
            elif self.active_option == -1 and self.options:
                # If no option is active, select the first option
                self.active_option = (0, 0)
                self.keyboard_navigation_active = True
                
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Select the current option
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                # Find the option at this level/index
                current_options = self.options
                for _ in range(level):
                    if not current_options:
                        break
                    # Navigate to the correct submenu level
                    for opt in current_options:
                        if opt.is_expanded and opt.submenu:
                            current_options = opt.submenu
                            break
                
                if current_options and 0 <= index < len(current_options):
                    option = current_options[index]
                    if not option.submenu:  # Only close menu if leaf option selected
                        self.draw_menu = False
                        self.visible = False
                        if self.callback:
                            # Build the index path
                            index_path = self._build_index_path(level, index)
                            self.callback(self.id, index_path, option.text)
                            return index_path, option.text
                    else:
                        # Toggle submenu expansion
                        option.is_expanded = not option.is_expanded

    def _build_index_path(self, level, index):
        """Build an index path for a given level and index"""
        # This is a simplified implementation - for a complete solution,
        # you would need to track the full path during navigation
        return [index]

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        # Check if mouse has moved more than 10 pixels
        mouse_moved = False
        if self.keyboard_navigation_active:
            dx = mpos[0] - self.last_mouse_pos[0]
            dy = mpos[1] - self.last_mouse_pos[1]
            distance = (dx*dx + dy*dy) ** 0.5  # Pythagorean distance
            if distance > 10:
                mouse_moved = True
                self.keyboard_navigation_active = False
        
        # Only update active option based on mouse position if keyboard navigation is not active
        if not self.keyboard_navigation_active:
            self.active_option, hovered_option = self._find_active_option(mpos, self.options)
        
        # Update last mouse position
        self.last_mouse_pos = mpos
        
        # Expand/collapse submenus based on hover (only if keyboard navigation is not active)
        if not self.keyboard_navigation_active:
            self._update_submenu_states(mpos, self.options)
        
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                self.keyboard_navigation_active = False  # Disable keyboard navigation on mouse click
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                    self.visible = not self.visible
                elif self.draw_menu:
                    clicked_option, index_path = self._handle_click(mpos, self.options)
                    if clicked_option is not None:
                        if not clicked_option.submenu:  # Only close menu if leaf option selected
                            self.draw_menu = False
                            self.visible = False
                            if self.callback:
                                self.callback(self.id, index_path, clicked_option.text)
                            return index_path, clicked_option.text
                    else:
                        self.draw_menu = False
                        self.visible = False
            # Handle keyboard navigation
            if event.type == pygame.KEYDOWN:
                result = self._handle_keyboard_navigation(event)
                if result:
                    return result
                
        return -1, None

    def _find_active_option(self, pos, options, level=0):
        """Recursively find which option the mouse is hovering over"""
        for i, option in enumerate(options):
            if option.rect and option.rect.collidepoint(pos):
                return (level, i), option
            if option.submenu and option.is_expanded:
                submenu_active, submenu_option = self._find_active_option(pos, option.submenu, level + 1)
                if submenu_active != -1:
                    return submenu_active, submenu_option
        return -1, None

    def _update_submenu_states(self, pos, options, current_path=None):
        """Update submenu expansion states based on hover"""
        if current_path is None:
            current_path = []
            
        for i, option in enumerate(options):
            current_option_path = current_path + [i]
            
            # Check if this option or any of its children are being hovered
            is_hovered = option.rect and option.rect.collidepoint(pos)
            has_hovered_child = False
            
            if option.submenu:
                # Recursively check children
                child_hovered = self._update_submenu_states(pos, option.submenu, current_option_path)
                has_hovered_child = child_hovered
                
                # Expand if this option or any of its children are hovered
                option.is_expanded = is_hovered or has_hovered_child
            
            # If we're not hovering over this branch, collapse it
            if not is_hovered and not has_hovered_child:
                option.is_expanded = False
                
            if is_hovered or has_hovered_child:
                return True
                
        return False

    def _handle_click(self, pos, options, current_path=None):
        """Handle click on menu options, returns (clicked_option, index_path) or (None, None)"""
        if current_path is None:
            current_path = []
            
        for i, option in enumerate(options):
            if option.rect and option.rect.collidepoint(pos):
                if option.submenu:
                    # Don't toggle expansion on click anymore since it's handled by hover
                    return None, None
                return option, current_path + [i]
            if option.submenu and option.is_expanded:
                submenu_result, submenu_path = self._handle_click(pos, option.submenu, current_path + [i])
                if submenu_result:
                    return submenu_result, submenu_path
        return None, None

    def add_submenu_by_text(self, parent_text, submenu_options):
        """Add a submenu to an existing option"""
        for option in self.options:
            if option.text == parent_text:
                option.submenu = self._convert_options(submenu_options)
                break
    
    def add_submenu_by_index_path(self, parent_index_path, submenu_options):
        """Add a submenu to an existing option by index path
        
        Args:
            parent_index_path (list): List of indices to traverse to reach target option
            submenu_options (list): List of options to add as submenu
        """
        if not parent_index_path:
            return
            
        # Start at the root options
        current_options = self.options
        target_option = None
        
        # Traverse the path except for the last index
        for index in parent_index_path[:-1]:
            if index >= len(current_options):
                return
            current_options = current_options[index].submenu
            if not current_options:  # Stop if we hit a dead end
                return
                
        # Get the final target option
        final_index = parent_index_path[-1]
        if final_index >= len(current_options):
            return
            
        # Add the submenu to the target option
        current_options[final_index].submenu = self._convert_options(submenu_options)

    def load_file_dir_as_options(self, path, ignore_regex=None, sort=True, append=False, index_path=None):
        """
        Load files from a directory as options
        index_path is a list of indices to traverse to reach the target location
        if index_path is not None, the new options will be inserted at the target location
        """
        # Create new options from files in directory
        new_options = [
            DropDownOption(os.path.splitext(os.path.basename(f))[0])
            for f in os.listdir(path) 
            if os.path.isfile(os.path.join(path, f)) 
            and (not ignore_regex or not re.match(ignore_regex, f))
        ]
        
        if sort:
            new_options.sort(key=lambda x: x.text)

        if index_path:
            # Navigate to the target location using index_path
            current_options = self.options
            for index in index_path[:-1]:
                if index >= len(current_options):
                    return
                if not current_options[index].submenu:
                    current_options[index].submenu = []
                current_options = current_options[index].submenu
            
            # Add the new options at the specified location
            final_index = index_path[-1]
            if final_index >= len(current_options):
                return
            
            # Set the submenu directly
            current_options[final_index].submenu = new_options
        else:
            # If no index_path, handle root level
            if append:
                self.options.extend(new_options)
            else:
                self.options = new_options

    def insert_option(self, option, index=None):
        if index is None: # add to the end
            index = len(self.options)
        self.options.insert(index, DropDownOption(option))
        self.option_rects.insert(index, pygame.Rect(0, 0, self.rect.width, self.rect.height))

    def insert_option_by_index_path(self, index_path, option, index=None):
        """Insert an option at a specific index path"""
        if not index_path:
            if index is None:
                index = len(self.options)
            self.options.insert(index, DropDownOption(option))
            self.option_rects.insert(index, pygame.Rect(0, 0, self.rect.width, self.rect.height))
            return
        
        # Navigate to the target location using index_path
        current_options = self.options
        for index in index_path[:-1]:
            if index >= len(current_options):
                return
            if not current_options[index].submenu:
                current_options[index].submenu = []
            current_options = current_options[index].submenu
        
        # Insert at the final location
        final_index = index_path[-1]
        if final_index >= len(current_options):
            return
        if not current_options[final_index].submenu:
            current_options[final_index].submenu = []
        
        # Insert the new option into the submenu
        if isinstance(option, str):
            option = DropDownOption(option)
        if index is None:
            current_options[final_index].submenu.append(option)
        else:
            current_options[final_index].submenu.insert(index, option)

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