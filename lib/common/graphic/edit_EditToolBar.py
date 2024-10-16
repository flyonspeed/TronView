import pygame

class EditToolBarButton:
    def __init__(self, text=None, icon=None, id=None, state=False):
        self.text = text
        self.icon = icon
        self.state = state  # is this button turned on or off? (color changed)
        self.font = pygame.font.Font(None, 25)  # Changed to 30pt
        self.width = self.calculate_width()
        self.height = 40  # Increased height to accommodate larger text
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.id = id

    def calculate_width(self):
        if self.text:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            return max(text_surface.get_width() + 20, 40)  # Increased padding and minimum width
        return 40  # Default width for icon buttons

    def set_text(self, text):
        self.text = text
        self.width = self.calculate_width()

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        color = (0, 0, 255) if self.state else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        if self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            # draw a light gray rect around the inside of the button
            pygame.draw.rect(surface, (150, 150, 150), self.rect.inflate(-10, -10), 1)
            surface.blit(text_surf, text_rect)
        elif self.icon:
            # Draw icon (placeholder)
            pygame.draw.rect(surface, (255, 255, 255), self.rect.inflate(-10, -10))

class EditToolBar:
    def __init__(self, screen_object):
        self.screen_object = screen_object
        self.buttons = [
            EditToolBarButton(text=screen_object.title, id="title"),
            EditToolBarButton(text="|", id="center"),
            EditToolBarButton(text="<", id="align_left"),
            EditToolBarButton(text=">", id="align_right"),
            EditToolBarButton(text="+", id="move_up"),
            EditToolBarButton(text="-", id="move_down"),
            EditToolBarButton(text="O", id="edit_options", state=screen_object.showOptions)
        ]
        self.width = sum(button.width for button in self.buttons)
        self.height = 40  # Increased to match button height
        self.position = "top"  # Default to top

    def draw(self, surface):
        x, y = self.get_position()
        self.buttons[6].state = self.screen_object.showOptions # set the state of the edit options button
        for button in self.buttons:
            button.draw(surface, x, y)
            x += button.width

    def get_position(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Always try to position at the top first
        x = self.screen_object.x
        y = self.screen_object.y - self.height - 5

        # Adjust if off-screen to the right
        if x + self.width > screen_width:
            x = screen_width - self.width

        # Adjust if off-screen to the left
        if x < 0:
            x = 0

        # If there's not enough space at the top, move to the bottom
        if y < 0:
            y = self.screen_object.y + self.screen_object.height + 5
            
            # If it's still off-screen at the bottom, keep it at the top
            if y + self.height > screen_height:
                y = 0

        return x, y

    def handle_click(self, pos):
        # get the id of the button that was clicked
        button_id = None
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                button_id = button.id
                break
        if button_id:
            print("Button clicked: %s" % button_id)
            return button_id        
        return None
