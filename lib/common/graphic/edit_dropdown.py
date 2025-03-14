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


class menu_item:
    def __init__(self, text, submenu=None):
        self.text = text
        self.submenus = []
        
        # Handle different types of submenu input
        if submenu is not None:
            if isinstance(submenu, list):
                for item in submenu:
                    if isinstance(item, menu_item):
                        # Already a menu_item, add directly
                        self.submenus.append(item)
                    elif isinstance(item, (list, tuple)) and len(item) == 2:
                        # It's a [title, submenu_list] format
                        title = item[0]
                        submenu_list = item[1]
                        self.submenus.append(menu_item(title, submenu_list))
                    else:
                        # Simple string or other item
                        self.submenus.append(menu_item(item))
            elif isinstance(submenu, str):
                # Single string submenu
                self.submenus.append(menu_item(submenu))
            elif isinstance(submenu, menu_item):
                # Single menu_item
                self.submenus.append(submenu)
                
    def add_submenu(self, submenu):
        """Add a submenu item"""
        if isinstance(submenu, menu_item):
            self.submenus.append(submenu)
        elif isinstance(submenu, str):
            self.submenus.append(menu_item(submenu))
        elif isinstance(submenu, (list, tuple)):
            for item in submenu:
                self.add_submenu(item)
                
    def has_submenus(self):
        """Check if this menu item has submenus"""
        return len(self.submenus) > 0

    @staticmethod
    def create_from_list_format(options):
        """
        Create menu_item objects from the list format used in the dropdown
        Example:
            [
                "Option 1",
                ["Submenu 1", [
                    "Submenu 1.1",
                    "Submenu 1.2"
                ]]
            ]
        """
        result = []
        for opt in options:
            if isinstance(opt, (list, tuple)) and len(opt) == 2:
                # It's a [title, submenu_list] format
                title = opt[0]
                submenu_list = opt[1]
                submenu_items = menu_item.create_from_list_format(submenu_list)
                item = menu_item(title, submenu_items)
                result.append(item)
            else:
                # Simple string or other item
                result.append(menu_item(opt))
        return result

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
        # if font is a number, use it as the font size
        if isinstance(font, int):
            self.font = pygame.font.SysFont(None, font)
        else:
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
        self.submenu_indicator = "->"  # Symbol to indicate submenu presence
        self.expanded_indicator = "v"  # Symbol to indicate expanded submenu
        self.current_path = []  # Track the current submenu path
        self.last_mouse_pos = pygame.mouse.get_pos()  # Track last mouse position
        self.keyboard_navigation_active = False  # Track if keyboard navigation is active
        
        # Debug options
        self.debug_mode = False  # Ensure debug mode is enabled
        self.debug_rects = []  # Store rectangles to draw for debugging
        self.debug_texts = []  # Store text to display for debugging
        
        # Debug colors
        self.debug_colors = {
            'hover': (0, 255, 0),           # Green for hovered items
            'buffer': (100, 100, 255),      # Light blue for buffer zones
            'submenu': (255, 100, 100),     # Red for submenu areas
            'submenu_buffer': (255, 150, 150), # Light red for submenu buffer zones
            'connector': (255, 255, 0),     # Yellow for connectors
            'active_path': (200, 200, 255), # Light blue for parent hierarchy
            'children': (255, 200, 200)     # Pink for child items
        }

    def _convert_options(self, options):
        """Convert plain options to DropDownOption objects"""
        converted = []
        
        if not isinstance(options, (list, tuple)):
            return converted
            
        for opt in options:
            # Handle menu_item objects
            if isinstance(opt, menu_item):
                # Convert menu_item to DropDownOption
                submenu_options = None
                if opt.submenus:
                    # Recursively convert submenu items
                    submenu_options = self._convert_options(opt.submenus)
                converted.append(DropDownOption(opt.text, submenu_options))
            elif isinstance(opt, (list, tuple)) and len(opt) == 2:
                # Get the title (first element)
                title = opt[0]
                # Get the submenu items (second element)
                submenu_items = opt[1]
                
                # Recursively convert submenu items
                if isinstance(submenu_items, (list, tuple)):
                    # Create the submenu options
                    submenu_options = self._convert_options(submenu_items)
                    # Create option with title and submenu
                    menu_option = DropDownOption(title, submenu_options)
                    # Add to converted options
                    converted.append(menu_option)
                else:
                    # Handle case where second element isn't a list (shouldn't happen)
                    converted.append(DropDownOption(title))
            elif isinstance(opt, str):
                # Simple string option
                converted.append(DropDownOption(opt))
            elif isinstance(opt, DropDownOption):
                # Already a DropDownOption
                converted.append(opt)
                
        # For debugging
        # if len(converted) > 0:
        #     has_submenu = sum(1 for opt in converted if opt.submenu)
        #     #print(f"Converted {len(converted)} options, {has_submenu} with submenus")
            
        return converted

    def draw(self, surf):
        screen_width = surf.get_width()
        screen_height = surf.get_height()
        eachOptionHeight = 20
        
        # Clear debug data for this frame
        self.debug_rects = []
        self.debug_texts = []
        
        if self.showButton:
            pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
            msg = self.font.render(self.main, 1, (0, 0, 0))
            surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            self._draw_menu_options(surf, self.options, self.rect.x, self.rect.y + self.rect.height)
            
            # Draw debug information if debug mode is enabled
            if self.debug_mode:
                self._draw_debug_info(surf)

    def _draw_debug_info(self, surf):
        """Draw debug information for troubleshooting hover detection"""
        # Draw all collected debug rectangles
        for rect, color, width in self.debug_rects:
            pygame.draw.rect(surf, color, rect, width)
            
        # Draw all collected debug texts
        for text, pos, color in self.debug_texts:
            text_surf = self.font.render(text, True, color)
            surf.blit(text_surf, pos)
            
        # Draw mouse position
        mouse_pos = pygame.mouse.get_pos()
        pos_text = f"Mouse: {mouse_pos[0]}, {mouse_pos[1]}"
        pos_surf = self.font.render(pos_text, True, (255, 255, 255))
        surf.blit(pos_surf, (10, 10))
        
        # Draw active option info
        if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
            level, index = self.active_option
            active_text = f"Active: L{level} I{index}"
            active_surf = self.font.render(active_text, True, (255, 255, 0))
            surf.blit(active_surf, (10, 30))
            
            # Find and display the text of the active item
            option_text = self._get_option_text_at_level_index(level, index)
            if option_text:
                item_text = f"Hovering: {option_text}"
                item_surf = self.font.render(item_text, True, (0, 255, 255))
                surf.blit(item_surf, (10, 50))
                
                # Display parent hierarchy
                parent_path = self._get_full_parent_path(level, index)
                if parent_path:
                    path_text = f"Path: {' > '.join(parent_path)}"
                    path_surf = self.font.render(path_text, True, self.debug_colors['active_path'])
                    surf.blit(path_surf, (10, 70))
                
                # Display child items if any
                has_children = self._has_submenu_at_level_index(level, index)
                if has_children:
                    child_items = self._get_child_items_text(level, index)
                    children_text = f"Children: {', '.join(child_items)}"
                    children_surf = self.font.render(children_text, True, self.debug_colors['children'])
                    surf.blit(children_surf, (10, 90))
            
        # Draw legend for debug colors
        legend_y = 120
        legend_items = [
            ("Green border", self.debug_colors['hover'], "Hovered menu item"),
            ("Light blue border", self.debug_colors['buffer'], "Buffer zone around menu item"),
            ("Red border", self.debug_colors['submenu'], "Submenu area"),
            ("Light red border", self.debug_colors['submenu_buffer'], "Submenu buffer zone"),
            ("Yellow border", self.debug_colors['connector'], "Connector between parent and submenu"),
            ("Cyan text", (0, 255, 255), "Currently hovered item"),
            ("Light blue text", self.debug_colors['active_path'], "Parent hierarchy path"),
            ("Pink text", self.debug_colors['children'], "Child items of hovered item")
        ]
        
        # Draw a semi-transparent background for the legend
        legend_height = len(legend_items) * 20
        legend_bg = pygame.Rect(5, 115, 400, legend_height + 10)
        legend_bg_surface = pygame.Surface((legend_bg.width, legend_bg.height), pygame.SRCALPHA)
        pygame.draw.rect(legend_bg_surface, (20, 20, 20, 180), legend_bg_surface.get_rect())
        surf.blit(legend_bg_surface, legend_bg)
        
        for text, color, desc in legend_items:
            # Draw color sample
            color_rect = pygame.Rect(15, legend_y, 20, 12)
            pygame.draw.rect(surf, color, color_rect)
            pygame.draw.rect(surf, (255, 255, 255), color_rect, 1)  # White border
            
            # Draw description
            legend_text = f"{text}: {desc}"
            legend_surf = self.font.render(legend_text, True, (255, 255, 255))
            surf.blit(legend_surf, (40, legend_y - 3))
            
            legend_y += 20
            
        # Draw debug mode status
        debug_status = f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}"
        status_surf = self.font.render(debug_status, True, (0, 255, 0) if self.debug_mode else (255, 0, 0))
        surf.blit(status_surf, (10, legend_y + 10))
            
    def _get_option_text_at_level_index(self, level, index):
        """Get the text of an option at a specific level and index"""
        options = self._get_options_at_level(level)
        if options and 0 <= index < len(options):
            return options[index].text
        return None

    def _has_submenu_at_level_index(self, level, index):
        """Check if an option at the given level and index has a submenu"""
        options = self._get_options_at_level(level)
        if options and 0 <= index < len(options):
            return options[index].submenu is not None and len(options[index].submenu) > 0
        return False

    def _get_child_items_text(self, level, index):
        """Get a list of child item texts for the option at the given level and index"""
        options = self._get_options_at_level(level)
        if options and 0 <= index < len(options) and options[index].submenu:
            return [opt.text for opt in options[index].submenu]
        return []

    def _get_full_parent_path(self, level, index):
        """Get the full path of parent item texts leading to this item"""
        if level == 0:
            # Top level item has no parents
            return []
            
        path = []
        current_level = level
        current_index = index
        
        while current_level > 0:
            # Find the parent
            parent_info = self._find_parent(current_level, current_index)
            if not parent_info:
                break
                
            parent_level, parent_index = parent_info
            
            # Get the parent's text
            parent_options = self._get_options_at_level(parent_level)
            if parent_options and 0 <= parent_index < len(parent_options):
                path.insert(0, parent_options[parent_index].text)
            
            # Move up to the parent's level
            current_level = parent_level
            current_index = parent_index
            
        return path

    def _draw_menu_options(self, surf, options, start_x, start_y, level=0):
        """Recursively draw menu options and their submenus"""
        screen_width = surf.get_width()
        screen_height = surf.get_height()
        current_y = start_y
        current_x = start_x
        indent = level * 5  # Reduced indentation for submenu items
        
        # Calculate maximum width needed for this level
        max_width = max(self.rect.width, 120)  # Ensure minimum width
        for option in options:
            text = option.text
            if option.submenu:
                indicator = self.expanded_indicator if option.is_expanded else self.submenu_indicator
                text = f"{text} {indicator}"
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_width = text_surface.get_width() + 20  # Add padding
            max_width = max(max_width, text_width + indent)
        
        # Draw menu title if it exists and we're at the top level
        if self.menuTitle and level == 0:
            title_surface = self.font.render(self.menuTitle, True, (255, 255, 255))
            title_width = title_surface.get_width() + 20  # Add padding
            max_width = max(max_width, title_width)
            title_rect = title_surface.get_rect()
            title_rect.midtop = (start_x + max_width // 2, start_y - 20)  # Reduced gap (was -25)
            # Draw a background for the title
            bg_rect = title_rect.inflate(20, 6)  # Reduced vertical inflation (was 10)
            pygame.draw.rect(surf, self.color_menu[0], bg_rect)
            surf.blit(title_surface, title_rect)
        
        # First check if menu would go off right edge of screen
        if start_x + max_width > screen_width - 5:  # Reduced margin (was -10)
            # Move menu to the left of the click position
            start_x = screen_width - max_width - 5  # Reduced margin (was -10)
            current_x = start_x
        
        # Calculate total height needed for this level only
        total_height = len(options) * self.rect.height
        
        # Keep track of available screen height with reduced margins
        available_height = screen_height - 10  # Reduced margin (was -20)
        
        # If menu would go off bottom of screen
        if start_y + total_height > screen_height - 5:  # Reduced margin (was -10)
            # First try to move the menu up
            new_start_y = screen_height - total_height - 5  # Reduced margin (was -10)
            
            # If moving up would put us above top margin, use scrolling or columns
            if new_start_y < 5:  # Reduced margin (was 10)
                # Use columns since we can't fit vertically
                max_items_per_column = (screen_height - 10) // self.rect.height  # Reduced margin (was -20)
                if max_items_per_column < 1:
                    max_items_per_column = 1
                
                # Calculate number of columns needed
                total_columns = (len(options) + max_items_per_column - 1) // max_items_per_column
                
                # Adjust start_x if multi-column menu would go off right edge
                if start_x + total_columns * max_width > screen_width - 5:  # Reduced margin (was -10)
                    start_x = max(5, screen_width - total_columns * max_width - 5)  # Reduced margins (was 10 and -10)
                
                current_x = start_x
                start_y = 5  # Reduced margin (was 10)
            else:
                # We can fit by moving up
                start_y = new_start_y
            
            current_y = start_y
        
        # Ensure we don't go off the top
        if start_y < 5:  # Reduced margin (was 10)
            start_y = 5  # Reduced margin (was 10)
            current_y = start_y
        
        # Variables for column management
        current_column = 0
        item_in_column = 0
        max_items_per_column = max(1, (screen_height - 10) // self.rect.height)  # Reduced margin (was -20)
        
        # Draw a background for the entire menu at this level
        # Use different colors for different levels for better visual hierarchy
        bg_colors = [(70, 70, 70), (80, 80, 80), (90, 90, 90), (100, 100, 100)]
        bg_color = bg_colors[min(level, len(bg_colors)-1)]
        menu_bg_rect = pygame.Rect(start_x, start_y, max_width, total_height)
        pygame.draw.rect(surf, bg_color, menu_bg_rect)  # Background
        pygame.draw.rect(surf, (150, 150, 150), menu_bg_rect, 1)  # Border
        
        # Track which option index is active at this level
        active_index_at_this_level = -1
        if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
            active_level, active_index = self.active_option
            if active_level == level:
                active_index_at_this_level = active_index
        
        for i, option in enumerate(options):
            # Start new column when needed
            if total_height > available_height and item_in_column >= max_items_per_column:
                current_column += 1
                item_in_column = 0
                current_y = start_y
                current_x = start_x + current_column * max_width
            
            # Create rectangle for this option using the calculated max_width
            option_rect = pygame.Rect(current_x, current_y, max_width, self.rect.height)
            option.rect = option_rect
            
            # Draw option background
            # Only highlight this option if it's active at this level
            is_active = i == active_index_at_this_level
            hover_color = (120, 120, 250) if option.is_expanded and option.submenu else self.color_option[1 if is_active else 0]
            pygame.draw.rect(surf, hover_color, option_rect, 0)
            
            # Draw option text
            text = option.text
            if option.submenu:
                indicator = self.expanded_indicator if option.is_expanded else self.submenu_indicator
                text = f"{text} {indicator}"
            
            msg = self.font.render(text, 1, (0, 0, 0))
            surf.blit(msg, msg.get_rect(midleft=(option_rect.left + 5 + indent, option_rect.centery)))
            
            # If this option has a submenu and is expanded, draw it
            if option.submenu and option.is_expanded:
                # Position submenu to the right of the parent
                submenu_x = option_rect.right + 2  # Small gap between parent and submenu
                submenu_y = option_rect.y  # Align with parent, no vertical offset
                
                # If submenu would go off right edge of screen, draw it to the left instead
                if submenu_x + max_width > screen_width - 5:  # Reduced margin (was -10)
                    submenu_x = max(5, option_rect.left - max_width - 2)  # Reduced margin (was 10)
                
                # Draw submenu
                self._draw_menu_options(surf, option.submenu, 
                                        submenu_x, submenu_y,  
                                        level + 1)
            
            # Always increment current_y for next item in this level
            current_y += self.rect.height
            item_in_column += 1
                
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
                
        elif event.key == pygame.K_RIGHT:
            # Expand submenu if available
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                current_options = self._get_options_at_level(level)
                if current_options and 0 <= index < len(current_options):
                    option = current_options[index]
                    if option.submenu:
                        option.is_expanded = True
                        # Move selection to first item in submenu
                        self.active_option = (level + 1, 0)
                        self.keyboard_navigation_active = True
        
        elif event.key == pygame.K_LEFT:
            # Collapse current submenu or go to parent
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                if level > 0:
                    # Find the current submenu we're in
                    current_options = self._get_options_at_level(level)
                    
                    # Navigate to parent menu
                    parent_path = self._find_parent(level, index)
                    if parent_path:
                        parent_level, parent_index = parent_path
                        
                        # Get the parent menu item that contains our submenu
                        parent_options = self._get_options_at_level(parent_level)
                        if parent_options and 0 <= parent_index < len(parent_options):
                            # Collapse the submenu we're leaving
                            parent_options[parent_index].is_expanded = False
                            
                        # Move selection to parent
                        self.active_option = (parent_level, parent_index)
                        self.keyboard_navigation_active = True
                
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Select the current option
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                # Find the option at this level/index
                current_options = self._get_options_at_level(level)
                
                if current_options and 0 <= index < len(current_options):
                    option = current_options[index]
                    if option.submenu:  
                        # Toggle submenu expansion
                        option.is_expanded = not option.is_expanded
                    else:
                        # Only close menu if leaf option selected
                        self.draw_menu = False
                        self.visible = False
                        if self.callback:
                            # Build the index path
                            index_path = self._build_index_path(level, index)
                            self.callback(self, self.id, index_path, option.text)
                            return index_path, option.text

    def _get_options_at_level(self, level):
        """Get options at a specific nesting level"""
        if level == 0:
            return self.options
            
        # Start from root and traverse down based on expanded state
        current_options = self.options
        current_level = 0
        
        while current_level < level:
            # Look for the first expanded submenu at this level
            found_expanded = False
            for opt in current_options:
                if opt.is_expanded and opt.submenu:
                    current_options = opt.submenu
                    found_expanded = True
                    break
            
            if not found_expanded:
                return None  # Couldn't find a path to the target level
                
            current_level += 1
            
        return current_options

    def _find_parent(self, level, index):
        """Find the parent menu item for a given level and index"""
        if level <= 0:
            return None
            
        # This is a simplified approach - a full implementation would require
        # tracking the complete path during navigation
        parent_level = level - 1
        
        # For demonstration purposes, return the first expanded option at parent level
        # In a real implementation, you'd track the full path during navigation
        parent_options = self._get_options_at_level(parent_level)
        if parent_options:
            for i, opt in enumerate(parent_options):
                if opt.is_expanded and opt.submenu:
                    # Check if this parent contains the current submenu item
                    current_options = self._get_options_at_level(level)
                    if current_options and 0 <= index < len(current_options):
                        # Check if this expanded parent contains our current submenu
                        # We need to verify that the current_options is actually opt.submenu
                        if current_options == opt.submenu:
                            return (parent_level, i)
            
            # Fallback: if we couldn't find the exact parent, still return the first expanded option
            for i, opt in enumerate(parent_options):
                if opt.is_expanded and opt.submenu:
                    return (parent_level, i)
        
        return None

    def _build_index_path(self, level, index):
        """Build an index path for a given level and index"""
        if level == 0:
            return [index]
            
        # Find the expanded options at each level to build the path
        path = []
        current_level = 0
        current_options = self.options
        
        while current_level < level:
            found = False
            for i, opt in enumerate(current_options):
                if opt.is_expanded and opt.submenu:
                    path.append(i)
                    current_options = opt.submenu
                    found = True
                    break
            
            if not found:
                # Couldn't determine the exact path, use the active_option information
                if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                    active_level, active_index = self.active_option
                    # If we're at the requested level, return what we have plus the target index
                    if active_level == level:
                        return path + [index]
                
                # Fallback if we can't determine the exact path
                return [index]
                
            current_level += 1
            
        path.append(index)
        return path

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
            # Store previous active option to detect changes
            prev_active = self.active_option
            self.active_option, hovered_option = self._find_active_option(mpos, self.options)
            
            # If active option changed and we're not hovering over a submenu of the previous active option,
            # then we should close unrelated menus
            if self.draw_menu and prev_active != self.active_option:
                # Only reset menus selectively
                self._selectively_reset_expanded_states(mpos)
        
        # Update last mouse position
        self.last_mouse_pos = mpos
        
        # Expand/collapse submenus based on hover (only if keyboard navigation is not active)
        if not self.keyboard_navigation_active and self.draw_menu:
            self._update_submenu_states(mpos, self.options)
        
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                self.keyboard_navigation_active = False  # Disable keyboard navigation on mouse click
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                    self.visible = not self.visible
                    
                    # Reset all expanded states when closing the menu
                    if not self.draw_menu:
                        self._reset_all_expanded_states(self.options)
                elif self.draw_menu:
                    clicked_option, index_path = self._handle_click(mpos, self.options)
                    
                    # Only process leaf item selections (items without submenus)
                    if clicked_option is not None:
                        # Close menu and execute callback only if it's a leaf item (no submenu)
                        self.draw_menu = False
                        self.visible = False
                        # Reset all expanded states when closing menu
                        self._reset_all_expanded_states(self.options)
                        if self.callback:
                            # Make sure we're passing the correct format to the callback
                            self.callback(self, self.id, index_path, clicked_option.text)
                            return index_path, clicked_option.text
                    else:
                        # If click wasn't on a menu item, check if it was outside all menus
                        if not self._is_click_inside_any_menu(mpos, self.options):
                            self.draw_menu = False
                            self.visible = False
                            # Reset all expanded states
                            self._reset_all_expanded_states(self.options)
            # Handle keyboard navigation
            if event.type == pygame.KEYDOWN:
                result = self._handle_keyboard_navigation(event)
                if result:
                    return result
                
        return -1, None

    def _selectively_reset_expanded_states(self, pos):
        """
        Intelligently reset expanded states, keeping open only menus relevant to current mouse position.
        This allows navigation to children while closing unrelated menus.
        """
        # Find if we're hovering over a menu item or in a buffer/connector area
        in_active_area = False
        
        # Start with top-level options
        for i, option in enumerate(self.options):
            # Check if mouse is directly over this option
            if option.rect and option.rect.collidepoint(pos):
                in_active_area = True
                break
                
            # If this option has a submenu, check buffer area and submenu
            if option.submenu and option.is_expanded:
                # Check buffer around the option
                if option.rect and option.rect.inflate(40, 40).collidepoint(pos):
                    in_active_area = True
                    break
                    
                # Check the submenu area
                submenu_rect = self._get_submenu_rect(option.submenu)
                if submenu_rect:
                    # Check submenu and its buffer
                    if submenu_rect.collidepoint(pos) or submenu_rect.inflate(40, 40).collidepoint(pos):
                        in_active_area = True
                        break
                        
                    # Check connector between parent and submenu
                    if option.rect and self._is_moving_toward_submenu(pos, option.rect, submenu_rect):
                        in_active_area = True
                        break
                        
                # Check if mouse is inside any item in the submenu (recursive)
                if self._is_hovering_over_submenu(pos, option.submenu):
                    in_active_area = True
                    break
        
        # If not in any active area, close unrelated menus at the top level
        if not in_active_area:
            # Keep track of active path
            active_path = []
            if isinstance(self.active_option, tuple) and len(self.active_option) == 2:
                level, index = self.active_option
                active_path = self._get_path_indices(level, index)
            
            # Only close top-level menus that aren't in the active path
            for i, option in enumerate(self.options):
                if option.submenu and option.is_expanded:
                    # If this isn't the first item in active path, close it
                    if not active_path or i != active_path[0]:
                        option.is_expanded = False

    def _update_submenu_states(self, pos, options, current_path=None, depth=0):
        """Update submenu expansion states based on hover"""
        if current_path is None:
            current_path = []
            
        # Track if any option at this level is being hovered
        any_hovered = False
        
        # Find which option is hovered at this level
        hovered_index = -1
        for i, option in enumerate(options):
            if option.rect and option.rect.collidepoint(pos):
                hovered_index = i
                any_hovered = True
                
                # Add debug rectangle for the hovered option
                if self.debug_mode:
                    # Draw a thicker, more noticeable highlight for the current hovered item
                    self.debug_rects.append((option.rect, self.debug_colors['hover'], 3))  # Thicker green for hovered
                    
                    # Add text label directly above the hovered item
                    if depth > 0:  # Only for submenu items
                        label_text = f"Level {depth}, Item {i}: {option.text}"
                        self.debug_texts.append((label_text, 
                                              (option.rect.left, option.rect.top - 15), 
                                              (0, 255, 255)))  # Cyan for hover label
                break
        
        # If we're hovering over a specific option
        if hovered_index != -1:
            # Get the hovered option
            option = options[hovered_index]
            
            # If it has a submenu, expand it
            if option.submenu:
                # Expand this submenu
                option.is_expanded = True
                
                # Add debug info for expanded submenu
                if self.debug_mode:
                    path_str = ' > '.join([str(p) for p in current_path + [hovered_index]])
                    self.debug_texts.append((f"Expanded: {path_str}", 
                                           (option.rect.right + 5, option.rect.top), 
                                           (255, 200, 0)))
                
                # Close sibling submenus that aren't being hovered
                for i, sibling in enumerate(options):
                    if i != hovered_index and sibling.submenu and sibling.is_expanded:
                        # Only close if we're not hovering over it or its children
                        if not self._is_hovering_over_submenu(pos, sibling.submenu):
                            # Also check if we're in the buffer or connector
                            keep_open = False
                            
                            if sibling.rect:
                                # Check buffer around sibling
                                buffer_rect = sibling.rect.inflate(40, 20)  # Reduced vertical inflation
                                if buffer_rect.collidepoint(pos):
                                    keep_open = True
                                
                                # Add debug visualization for buffer
                                if self.debug_mode:
                                    self.debug_rects.append((buffer_rect, self.debug_colors['buffer'], 1))
                            
                            # Check sibling's submenu area
                            submenu_rect = self._get_submenu_rect(sibling.submenu)
                            if submenu_rect:
                                # Check buffer around submenu
                                submenu_buffer = submenu_rect.inflate(40, 20)  # Reduced vertical inflation
                                if submenu_buffer.collidepoint(pos):
                                    keep_open = True
                                
                                # Add debug visualization for submenu and its buffer
                                if self.debug_mode:
                                    self.debug_rects.append((submenu_rect, self.debug_colors['submenu'], 1))
                                    self.debug_rects.append((submenu_buffer, self.debug_colors['submenu_buffer'], 1))
                                
                                # Check connector
                                if sibling.rect and self._is_moving_toward_submenu(pos, sibling.rect, submenu_rect):
                                    keep_open = True
                                    
                                    # Add debug visualization for connector
                                    if self.debug_mode:
                                        self._debug_draw_connector(pos, sibling.rect, submenu_rect, current_path + [i])
                            
                            # Close if not in any active area
                            if not keep_open:
                                sibling.is_expanded = False
            
            # Check if any submenu is being hovered
            if option.submenu and option.is_expanded:
                # Check children of this option
                child_hovered = self._update_submenu_states(
                    pos, option.submenu, current_path + [hovered_index], depth+1
                )
                # Expand this option since its submenu is being checked
                option.is_expanded = True
                
                # If a child is hovered, propagate upward
                any_hovered = any_hovered or child_hovered
        else:
            # No option is hovered at this level, check for hover in expanded submenus
            for i, option in enumerate(options):
                if option.submenu and option.is_expanded:
                    # Check if any child is hovered
                    child_hovered = self._update_submenu_states(
                        pos, option.submenu, current_path + [i], depth+1
                    )
                    
                    # If a child is hovered, keep this menu expanded
                    if child_hovered:
                        option.is_expanded = True
                        any_hovered = True
                    else:
                        # Check if we should keep this submenu open
                        keep_open = False
                        
                        if option.rect:
                            # Check buffer around parent
                            buffer_rect = option.rect.inflate(40, 20)  # Reduced vertical inflation
                            if buffer_rect.collidepoint(pos):
                                keep_open = True
                            
                            # Add debug for buffer
                            if self.debug_mode:
                                self.debug_rects.append((buffer_rect, self.debug_colors['buffer'], 1))
                                
                                buffer_status = "yes" if buffer_rect.collidepoint(pos) else "no"
                                path_str = ' > '.join([str(p) for p in current_path + [i]])
                                self.debug_texts.append((f"In buffer {path_str}: {buffer_status}", 
                                                     (option.rect.left, option.rect.bottom + 15),
                                                     (100, 255, 100)))
                        
                        # Check submenu area
                        submenu_rect = self._get_submenu_rect(option.submenu)
                        if submenu_rect:
                            # Check submenu and buffer
                            submenu_buffer = submenu_rect.inflate(40, 20)  # Reduced vertical inflation
                            if submenu_rect.collidepoint(pos) or submenu_buffer.collidepoint(pos):
                                keep_open = True
                            
                            # Add debug for submenu and buffer
                            if self.debug_mode:
                                self.debug_rects.append((submenu_rect, self.debug_colors['submenu'], 1))
                                self.debug_rects.append((submenu_buffer, self.debug_colors['submenu_buffer'], 1))
                                
                                submenu_status = "yes" if submenu_rect.collidepoint(pos) else "no"
                                buffer_status = "yes" if submenu_buffer.collidepoint(pos) else "no"
                                path_str = ' > '.join([str(p) for p in current_path + [i]])
                                self.debug_texts.append((f"In submenu {path_str}: {submenu_status}", 
                                                     (option.rect.left, option.rect.bottom + 30),
                                                     self.debug_colors['submenu']))
                                self.debug_texts.append((f"In submenu buffer {path_str}: {buffer_status}", 
                                                     (option.rect.left, option.rect.bottom + 45),
                                                     self.debug_colors['submenu_buffer']))
                            
                            # Check connector
                            if option.rect and self._is_moving_toward_submenu(pos, option.rect, submenu_rect):
                                keep_open = True
                                
                                # Add debug for connector
                                if self.debug_mode:
                                    self._debug_draw_connector(pos, option.rect, submenu_rect, current_path + [i])
                        
                        # Close if not in any active area
                        option.is_expanded = keep_open
        
        return any_hovered
    
    def _is_moving_toward_submenu(self, pos, parent_rect, submenu_rect):
        """Check if mouse movement is in the general direction of the submenu"""
        # Safety check for None rects
        if not parent_rect or not submenu_rect:
            return False
            
        # Create a detection area between parent and submenu with reduced vertical padding
        if parent_rect.right < submenu_rect.left:  # Submenu is to the right
            connector = pygame.Rect(
                parent_rect.right, 
                min(parent_rect.top, submenu_rect.top) - 5,  # Reduced vertical padding (was -30)
                submenu_rect.left - parent_rect.right,
                max(parent_rect.bottom, submenu_rect.bottom) - min(parent_rect.top, submenu_rect.top) + 10  # Reduced vertical padding (was +60)
            )
            return connector.collidepoint(pos)
        elif parent_rect.left > submenu_rect.right:  # Submenu is to the left
            connector = pygame.Rect(
                submenu_rect.right,
                min(parent_rect.top, submenu_rect.top) - 5,  # Reduced vertical padding (was -30)
                parent_rect.left - submenu_rect.right,
                max(parent_rect.bottom, submenu_rect.bottom) - min(parent_rect.top, submenu_rect.top) + 10  # Reduced vertical padding (was +60)
            )
            return connector.collidepoint(pos)
        # If submenu is above or below parent
        elif parent_rect.bottom < submenu_rect.top:  # Submenu is below
            connector = pygame.Rect(
                min(parent_rect.left, submenu_rect.left) - 5,  # Reduced horizontal padding (was -30)
                parent_rect.bottom,
                max(parent_rect.right, submenu_rect.right) - min(parent_rect.left, submenu_rect.left) + 10,  # Reduced horizontal padding (was +60)
                submenu_rect.top - parent_rect.bottom
            )
            return connector.collidepoint(pos)
        elif parent_rect.top > submenu_rect.bottom:  # Submenu is above
            connector = pygame.Rect(
                min(parent_rect.left, submenu_rect.left) - 5,  # Reduced horizontal padding (was -30)
                submenu_rect.bottom,
                max(parent_rect.right, submenu_rect.right) - min(parent_rect.left, submenu_rect.left) + 10,  # Reduced horizontal padding (was +60)
                parent_rect.top - submenu_rect.bottom
            )
            return connector.collidepoint(pos)
        return False
    
    def _is_hovering_over_submenu(self, pos, submenu_options):
        """Check if mouse is hovering over any item in a submenu or its children"""
        for option in submenu_options:
            if option.rect and option.rect.collidepoint(pos):
                return True
            if option.submenu and option.is_expanded:
                if self._is_hovering_over_submenu(pos, option.submenu):
                    return True
                    
            # Also check buffer areas for a more forgiving hover detection - with reduced vertical buffer
            if option.rect and option.rect.inflate(40, 20).collidepoint(pos):  # Reduced vertical inflation (was 40)
                return True
                
        # Check the entire submenu area too
        submenu_rect = self._get_submenu_rect(submenu_options)
        if submenu_rect and submenu_rect.inflate(40, 20).collidepoint(pos):  # Reduced vertical inflation (was 40)
            return True
            
        return False

    def _get_submenu_rect(self, submenu_options):
        """Get a rect that encompasses all items in a submenu"""
        if not submenu_options:
            return None
            
        # Find the bounds of all visible submenu options
        rects = [opt.rect for opt in submenu_options if opt.rect]
        if not rects:
            return None
            
        # Get the union of all rects
        union_rect = rects[0].copy()
        for rect in rects[1:]:
            union_rect.union_ip(rect)
            
        return union_rect

    def _debug_draw_connector(self, pos, parent_rect, submenu_rect, path):
        """Draw debug visualization for connector area"""
        if parent_rect.right < submenu_rect.left:  # Submenu is to the right
            connector = pygame.Rect(
                parent_rect.right, 
                min(parent_rect.top, submenu_rect.top) - 5,  # Reduced vertical padding (was -20)
                submenu_rect.left - parent_rect.right,
                max(parent_rect.bottom, submenu_rect.bottom) - min(parent_rect.top, submenu_rect.top) + 10  # Reduced vertical padding (was +40)
            )
            self.debug_rects.append((connector, self.debug_colors['connector'], 1))  # Yellow for connector
        elif parent_rect.left > submenu_rect.right:  # Submenu is to the left
            connector = pygame.Rect(
                submenu_rect.right,
                min(parent_rect.top, submenu_rect.top) - 5,  # Reduced vertical padding (was -20)
                parent_rect.left - submenu_rect.right,
                max(parent_rect.bottom, submenu_rect.bottom) - min(parent_rect.top, submenu_rect.top) + 10  # Reduced vertical padding (was +40)
            )
            self.debug_rects.append((connector, self.debug_colors['connector'], 1))  # Yellow for connector
        elif parent_rect.bottom < submenu_rect.top:  # Submenu is below
            connector = pygame.Rect(
                min(parent_rect.left, submenu_rect.left) - 5,  # Reduced horizontal padding (was -20)
                parent_rect.bottom,
                max(parent_rect.right, submenu_rect.right) - min(parent_rect.left, submenu_rect.left) + 10,  # Reduced horizontal padding (was +40)
                submenu_rect.top - parent_rect.bottom
            )
            self.debug_rects.append((connector, self.debug_colors['connector'], 1))  # Yellow for connector
        elif parent_rect.top > submenu_rect.bottom:  # Submenu is above
            connector = pygame.Rect(
                min(parent_rect.left, submenu_rect.left) - 5,  # Reduced horizontal padding (was -20)
                submenu_rect.bottom,
                max(parent_rect.right, submenu_rect.right) - min(parent_rect.left, submenu_rect.left) + 10,  # Reduced horizontal padding (was +40)
                parent_rect.top - submenu_rect.bottom
            )
            self.debug_rects.append((connector, self.debug_colors['connector'], 1))  # Yellow for connector
            
        # Add debug text for connector
        path_str = ' > '.join([str(p) for p in path])
        in_connector = connector.collidepoint(pos) if 'connector' in locals() else False
        self.debug_texts.append((f"In connector {path_str}: {in_connector}", 
                             (parent_rect.left, parent_rect.bottom + 15),  # Reduced vertical offset (was +30)
                             self.debug_colors['connector']))
    
    def _get_path_indices(self, target_level, target_index):
        """Get the path of indices leading to the target item"""
        if target_level == 0:
            return [target_index]
            
        path = []
        current_level = target_level
        current_index = target_index
        
        # Work backwards from the target item
        while current_level >= 0:
            if current_level == 0:
                path.insert(0, current_index)
                break
                
            parent_info = self._find_parent(current_level, current_index)
            if not parent_info:
                break
                
            parent_level, parent_index = parent_info
            
            if current_level > parent_level:
                # Add the current index to the path
                path.insert(0, current_index)
                
            # Move up to parent
            current_level = parent_level
            current_index = parent_index
            
        # Add the top level parent
        if len(path) < target_level + 1 and current_level == 0:
            path.insert(0, current_index)
            
        return path

    def _handle_click(self, pos, options, current_path=None):
        """Handle click on menu options, returns (clicked_option, index_path) or (None, None)"""
        if current_path is None:
            current_path = []
            
        for i, option in enumerate(options):
            if option.rect and option.rect.collidepoint(pos):
                if option.submenu:
                    # Toggle expansion on click for parent items
                    new_state = not option.is_expanded
                    option.is_expanded = new_state
                    
                    # Collapse all other open submenu items at this level (siblings)
                    if new_state:  # Only if expanding
                        for j, sibling in enumerate(options):
                            if j != i and sibling.submenu and sibling.is_expanded:
                                sibling.is_expanded = False
                    
                    # Return the parent option and its path for tracking
                    return None, None
                else:
                    # For leaf options (no submenu), construct the full path including all parent indices
                    full_path = current_path + [i]
                    return option, full_path
                    
        # If click wasn't on an option at this level, check expanded submenus recursively
        for i, option in enumerate(options):
            if option.submenu and option.is_expanded:
                # Check if click was in submenu
                sub_clicked, sub_path = self._handle_click(pos, option.submenu, current_path + [i])
                if sub_clicked is not None:
                    return sub_clicked, sub_path
        
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

    def load_menu_items(self, items):
        """Load menu_item objects as options"""
        if isinstance(items, list):
            self.options = self._convert_options(items)
        elif isinstance(items, menu_item):
            self.options = self._convert_options([items])
        else:
            print("Warning: Invalid items provided to load_menu_items. Expected list or menu_item.")
            
    @staticmethod
    def create_menu_item_structure(options):
        """
        Convert the list format to menu_item objects
        
        Example:
            [
                "Option 1",
                ["Submenu 1", [
                    "Submenu 1.1",
                    "Submenu 1.2"
                ]]
            ]
        """
        return menu_item.create_from_list_format(options)

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

    def _is_click_inside_any_menu(self, pos, options):
        """Check if a click position is inside any menu item or submenu"""
        # First check if the position is inside any option at this level
        for option in options:
            if option.rect and option.rect.collidepoint(pos):
                return True
                
            # If this option has a submenu and it's expanded, check that too
            if option.submenu and option.is_expanded:
                if self._is_click_inside_any_menu(pos, option.submenu):
                    return True
                    
                # Also check the submenu area as a whole
                submenu_rect = self._get_submenu_rect(option.submenu)
                if submenu_rect and submenu_rect.collidepoint(pos):
                    return True
        
        # If we get here, the position is not inside any menu item
        return False
        
    def _reset_all_expanded_states(self, options):
        """Reset all submenu expansion states recursively"""
        for option in options:
            if option.submenu:
                # Reset child submenus first (recursive)
                self._reset_all_expanded_states(option.submenu)
            # Then reset this option
            option.is_expanded = False


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python