import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel, UITextEntryLine, UIDropDownMenu
from lib.common import shared
from lib.common.graphic.growl_manager import GrowlManager, GrowlPosition

class EditEventsWindow:
    def __init__(self, screen_object, pygame_gui_manager, smartdisplay):
        self.screen_object = screen_object
        self.pygame_gui_manager = pygame_gui_manager
        self.smartdisplay = smartdisplay
        self.visible = True
        self.ui_elements = []
        self.details_window = None

        window_width = 300
        window_height = 500

        x = min(screen_object.x + screen_object.width, smartdisplay.x_end - window_width)
        y = screen_object.y
        if y + window_height > smartdisplay.y_end:
            y = max(0, smartdisplay.y_end - window_height)

        self.window = UIWindow(
            pygame.Rect(x, y, window_width, window_height),
            self.pygame_gui_manager,
            window_display_title=f"Event Handlers: {screen_object.title}",
            object_id="#events_window",
            draggable=False 
        )

        self.add_button = UIButton(
            relative_rect=pygame.Rect(10, 10, 80, 25),
            text="Add",
            manager=self.pygame_gui_manager,
            container=self.window
        )

        self.scrollable_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 45, window_width, window_height - 85),
            manager=self.pygame_gui_manager,
            container=self.window,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
            allow_scroll_x=False,
            
        )

        self.build_ui()

    def build_ui(self):
        #print("EditEventsWindow build_ui %s" % self.screen_object.title)
        y_offset = 10
        for element in self.ui_elements:
            element.kill()
        self.ui_elements.clear()

        if not hasattr(self.screen_object, 'event_handlers'):
            self.screen_object.event_handlers = []

        for i, handler in enumerate(self.screen_object.event_handlers):
            label = UILabel(
                relative_rect=pygame.Rect(10, y_offset, 200, 20),
                text=f"Handler {handler['id']}",
                manager=self.pygame_gui_manager,
                container=self.scrollable_container
            )
            self.ui_elements.append(label)

            edit_button = UIButton(
                relative_rect=pygame.Rect(220, y_offset, 50, 20),
                text="Edit",
                manager=self.pygame_gui_manager,
                container=self.scrollable_container
            )
            edit_button.handler_index = i
            self.ui_elements.append(edit_button)

            y_offset += 30

        self.scrollable_container.set_scrollable_area_dimensions((280, max(y_offset, 360)))

    def handle_event(self, event):
        #print("EditEventsWindow handle_event %s type %s" % (self.screen_object.title, event.type))
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print("EditEventsWindow handle_event UI_BUTTON_PRESSED %s type %s" % (self.screen_object.title, event.ui_element))
            if self.details_window:
                self.details_window.handle_event(event) # pass the event to the details window
            elif event.ui_element == self.add_button:
                self.show_handler_details()
            else:
                # else it must be a button for a handler
                for element in self.ui_elements:
                    if isinstance(element, UIButton) and event.ui_element == element:
                        if hasattr(element, 'handler_index'):
                            self.show_handler_details(self.screen_object.event_handlers[element.handler_index])
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            print("Window closed:", event.ui_element)
            if event.ui_element == self.window:
                if self.details_window: 
                    self.details_window.window.kill()
                    self.details_window = None
                self.hide()
                return
            if self.details_window and event.ui_element == self.details_window.window:
                self.details_window = None

    def show_handler_details(self, handler=None):
        self.details_window = HandlerDetailsWindow(self.screen_object, handler, self.pygame_gui_manager, self.smartdisplay, self)

    def close_handler_details(self):
        #print("EditEventsWindow close_handler_details")
        self.details_window = None

    def update_position(self):
        window_width = self.window.get_abs_rect().width
        window_height = self.window.get_abs_rect().height
        screen_width, screen_height = pygame.display.get_surface().get_size()

        x = min(self.screen_object.x + self.screen_object.width, screen_width - window_width)
        y = self.screen_object.y
        if y + window_height > screen_height:
            y = max(0, screen_height - window_height)

        self.window.set_position((x, y))

    def update(self, time_delta):
        if self.visible:
            self.update_position()
            self.pygame_gui_manager.update(time_delta)

    def draw(self, screen):
        if self.visible:
            self.pygame_gui_manager.draw_ui(screen)

    def show(self):
        self.visible = True
        self.window.show()

    def hide(self):
        self.visible = False
        self.window.hide()

    def remove_ui(self):
        self.window.kill()
        self.ui_elements.clear()
    
    def is_busy(self):
        return self.details_window is not None

class HandlerDetailsWindow:
    def __init__(self, screen_object, handler, pygame_gui_manager, smartdisplay, parent_EditEventsWindow):
        self.screen_object = screen_object
        self.handler = handler
        self.pygame_gui_manager = pygame_gui_manager
        self.smartdisplay = smartdisplay
        self.parent_EditEventsWindow = parent_EditEventsWindow

        window_width = 300
        window_height = 300

        x = (smartdisplay.x_end - window_width) // 2
        y = (smartdisplay.y_end - window_height) // 2

        self.window = UIWindow(
            pygame.Rect(x, y, window_width, window_height),
            self.pygame_gui_manager,
            window_display_title="Event Handler Details",
            object_id="#handler_details_window"
        )

        self.build_ui()

    def build_ui(self):
        #print("HandlerDetailsWindow build_ui %s" % self.screen_object.title)
        y_offset = 10

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="ID:",
                manager=self.pygame_gui_manager,
                container=self.window)
        self.id_entry = UITextEntryLine(relative_rect=pygame.Rect(100, y_offset, 180, 20),
                                        manager=self.pygame_gui_manager,
                                        container=self.window)
        y_offset += 30

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="Field:",
                manager=self.pygame_gui_manager,
                container=self.window)
        self.field_entry = UITextEntryLine(relative_rect=pygame.Rect(100, y_offset, 180, 20),
                                           manager=self.pygame_gui_manager,
                                           container=self.window)
        y_offset += 30

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="Operator:",
                manager=self.pygame_gui_manager,
                container=self.window)
        starting_option = '<'
        if self.handler:
            starting_option = self.handler['operator']
        self.operator_dropdown = UIDropDownMenu(options_list=['<', '<=', '>', '>=', '==', '!='],
                                                starting_option=starting_option,
                                                relative_rect=pygame.Rect(100, y_offset, 180, 20),
                                                manager=self.pygame_gui_manager,
                                                container=self.window)
        y_offset += 30

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="Value:",
                manager=self.pygame_gui_manager,
                container=self.window)
        self.value_entry = UITextEntryLine(relative_rect=pygame.Rect(100, y_offset, 180, 20),
                                           manager=self.pygame_gui_manager,
                                           container=self.window)
        y_offset += 30

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="Action:",
                manager=self.pygame_gui_manager,
                container=self.window)
        starting_option = 'hide'
        if self.handler:
            starting_option = self.handler['action']        
        self.action_dropdown = UIDropDownMenu(options_list=['hide', 'show', 'move', 'resize'],
                                              starting_option=starting_option,
                                              relative_rect=pygame.Rect(100, y_offset, 180, 25),
                                              manager=self.pygame_gui_manager,
                                              container=self.window)
        y_offset += 30

        UILabel(relative_rect=pygame.Rect(10, y_offset, 80, 20),
                text="Target ID:",
                manager=self.pygame_gui_manager,
                container=self.window)
        self.target_id_entry = UITextEntryLine(relative_rect=pygame.Rect(100, y_offset, 180, 20),
                                               manager=self.pygame_gui_manager,
                                               container=self.window)
        y_offset += 40

        self.save_button = UIButton(relative_rect=pygame.Rect(10, y_offset, 80, 30),
                                    text="Save",
                                    manager=self.pygame_gui_manager,
                                    container=self.window)
        
        # if we are editing an existing handler, add a delete button
        if self.handler:
            self.delete_button = UIButton(relative_rect=pygame.Rect(100, y_offset, 80, 30),
                                      text="Delete",
                                      manager=self.pygame_gui_manager,
                                      container=self.window)

        # update the UI with the current handler data (if any)
        if self.handler:
            self.id_entry.set_text(self.handler['id'])
            self.field_entry.set_text(self.handler['field'])
            self.value_entry.set_text(str(self.handler['value']))
            self.target_id_entry.set_text(self.handler['target_id'])

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print("HandlerDetailsWindow handle_event UI_BUTTON_PRESSED %s type %s" % (self.screen_object.title, event.ui_element))
            if event.ui_element == self.save_button:
                self.save_handler()
            elif self.handler and event.ui_element == self.delete_button:
                self.delete_handler()

    def save_handler(self):
        # make sure the id is unique
        new_id = self.id_entry.get_text()
        # if editing an existing handler, don't allow the same id
        if (new_id in [handler['id'] for handler in self.screen_object.event_handlers]):
            if self.handler and new_id == self.handler['id']:   
                pass
            else:
                shared.GrowlManager.add_message("Existing Event Handler found with this ID: %s" % new_id,position=GrowlPosition.CENTER)
                return
        if new_id == '':
            shared.GrowlManager.add_message("ID cannot be blank",position=GrowlPosition.CENTER)
            return

        # save the new handler
        new_handler = {
            'id': self.id_entry.get_text(),
            'field': self.field_entry.get_text(),
            'operator': self.operator_dropdown.selected_option[0], # only the first tuple
            'value': self.value_entry.get_text(),
            'action': self.action_dropdown.selected_option[0], # only the first tuple
            'target_id': self.target_id_entry.get_text()
        }

        # if we are editing an existing handler, replace it
        if self.handler:
            index = self.screen_object.event_handlers.index(self.handler)
            self.screen_object.event_handlers[index] = new_handler
        else:
            self.screen_object.event_handlers.append(new_handler)

        self.parent_EditEventsWindow.build_ui()
        self.window.kill()
        self.parent_EditEventsWindow.close_handler_details()


    def delete_handler(self):
        if self.handler:
            self.screen_object.event_handlers.remove(self.handler)
            self.parent_EditEventsWindow.build_ui()
        self.window.kill()
        self.parent_EditEventsWindow.close_handler_details()

# Add this function to save event handlers to JSON
def save_event_handlers_to_json(screen_object):
    if hasattr(screen_object, 'event_handlers'):
        return screen_object.event_handlers
    return []

# Add this function to load event handlers from JSON
def load_event_handlers_from_json(screen_object, event_handlers):
    screen_object.event_handlers = event_handlers
