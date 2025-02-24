from typing import Callable, Optional, Dict, List
import time
from dataclasses import dataclass
from enum import Enum
import pygame

class GrowlPosition(Enum):
    TOP_LEFT = "topL"
    TOP_MIDDLE = "topM"
    TOP_RIGHT = "topR"
    MIDDLE_LEFT = "midL"
    CENTER = "center"
    MIDDLE_RIGHT = "midR"
    BOTTOM_LEFT = "botL"
    BOTTOM_MIDDLE = "botM"
    BOTTOM_RIGHT = "botR"

@dataclass
class GrowlMessage:
    message: str
    created_at: float
    duration: float
    position: GrowlPosition
    color: tuple[int, int, int] = (255, 255, 255)  # Default white
    background_color: tuple[int, int, int] = (0, 0, 0)  # Default black
    on_click_callback: Optional[Callable] = None
    height: int = 0  # Add height field to track message box height

class GrowlManager:
    def __init__(self):
        self.messages: List[GrowlMessage] = []
        self._position_offsets: Dict[GrowlPosition, tuple[float, float]] = {
            GrowlPosition.TOP_LEFT: (0.0, 0.1),      # Changed x to 0.0 for left alignment
            GrowlPosition.TOP_MIDDLE: (0.5, 0.1),
            GrowlPosition.TOP_RIGHT: (0.9, 0.1),
            GrowlPosition.MIDDLE_LEFT: (0.0, 0.5),   # Changed x to 0.0 for left alignment
            GrowlPosition.CENTER: (0.5, 0.5),
            GrowlPosition.MIDDLE_RIGHT: (0.9, 0.5),
            GrowlPosition.BOTTOM_LEFT: (0.0, 0.9),   # Changed x to 0.0 for left alignment
            GrowlPosition.BOTTOM_MIDDLE: (0.5, 0.9),
            GrowlPosition.BOTTOM_RIGHT: (0.9, 0.9),
        }
        self.padding = 10
        self.message_spacing = 5  # Space between stacked messages
        self.totalMessages = 0

    def initScreen(self):
        self.font = pygame.font.SysFont("monospace", 25, bold=False)

    def clear(self):
        self.messages = []
        self.totalMessages = 0

    def add_message(
        self,
        message: str,
        duration: float = 3.0,
        position: GrowlPosition = GrowlPosition.TOP_RIGHT,
        color: tuple[int, int, int] = (255, 255, 255),
        background_color: tuple[int, int, int] = (0, 0, 0),
        on_click_callback: Optional[Callable] = None,
    ) -> None:
        """
        Add a new message to the growl queue.
        
        Args:
            message: The text message to display
            duration: How long to show the message in seconds
            position: Screen position for the message
            color: Text color as RGB tuple
            background_color: Background color as RGB tuple
            on_click_callback: Optional function to call when message is clicked
        """
        growl_message = GrowlMessage(
            message=message,
            created_at=time.time(),
            duration=duration,
            position=position,
            color=color,
            background_color=background_color,
            on_click_callback=on_click_callback,
        )
        self.messages.append(growl_message)
        self.totalMessages += 1

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw all active messages. Should be called in the draw loop.
        """
        if self.totalMessages == 0:
            return

        current_time = time.time()
        screen_width = screen.get_width()
        
        # Remove expired messages
        self.messages = [
            msg for msg in self.messages 
            if (current_time - msg.created_at) < msg.duration
        ]

        # Group messages by position
        position_messages: Dict[GrowlPosition, List[GrowlMessage]] = {}
        for msg in self.messages:
            if msg.position not in position_messages:
                position_messages[msg.position] = []
            position_messages[msg.position].append(msg)

        # Sort messages in each position by creation time (newest first)
        for pos in position_messages:
            position_messages[pos].sort(key=lambda x: x.created_at, reverse=True)

        # Draw messages
        for position, messages in position_messages.items():
            x_ratio, y_ratio = self._position_offsets[position]
            base_x = screen.get_width() * x_ratio
            base_y = screen.get_height() * y_ratio
            
            total_height = 0
            for msg in messages:
                # Render text to get dimensions
                text_surface = self.font.render(msg.message, True, msg.color)
                text_rect = text_surface.get_rect()
                
                # Create background surface
                background = pygame.Surface((text_rect.width + self.padding * 2, 
                                          text_rect.height + self.padding * 2))
                background.fill(msg.background_color)
                background_rect = background.get_rect()
                
                # Calculate alpha
                time_elapsed = current_time - msg.created_at
                alpha = 255
                if time_elapsed > (msg.duration - 0.5):
                    alpha = int(255 * (1 - (time_elapsed - (msg.duration - 0.5)) / 0.5))
                
                # Set alpha
                text_surface.set_alpha(alpha)
                background.set_alpha(alpha)
                
                # Calculate positions
                if position in [GrowlPosition.TOP_LEFT, GrowlPosition.MIDDLE_LEFT, GrowlPosition.BOTTOM_LEFT]:
                    # Left align with padding
                    background_rect.left = base_x + self.padding
                    text_rect.left = base_x + self.padding * 2
                elif position in [GrowlPosition.TOP_RIGHT, GrowlPosition.MIDDLE_RIGHT, GrowlPosition.BOTTOM_RIGHT]:
                    # Right align to screen edge
                    background_rect.right = screen_width - self.padding
                    text_rect.right = screen_width - (self.padding * 2)
                else:
                    # Center aligned positions
                    background_rect.centerx = base_x
                    text_rect.centerx = base_x

                # Adjust vertical position based on stacking
                if position in [GrowlPosition.TOP_LEFT, GrowlPosition.TOP_MIDDLE, GrowlPosition.TOP_RIGHT]:
                    background_rect.top = base_y + total_height
                    text_rect.top = base_y + total_height + self.padding
                elif position in [GrowlPosition.BOTTOM_LEFT, GrowlPosition.BOTTOM_MIDDLE, GrowlPosition.BOTTOM_RIGHT]:
                    background_rect.bottom = base_y - total_height
                    text_rect.bottom = base_y - total_height - self.padding
                else:  # Center positions
                    # Stack from the center position upwards
                    half_height = background_rect.height / 2
                    background_rect.centery = base_y - total_height + half_height
                    text_rect.centery = base_y - total_height + half_height

                # Draw background and text
                screen.blit(background, background_rect)
                screen.blit(text_surface, text_rect)

                # Update total height for next message
                total_height += background_rect.height + self.message_spacing
                msg.height = background_rect.height  # Store height for hit detection
            
            # calculate total shown messages
            self.totalShownMessages = len(messages)

    def handle_click(self, mouse_x: float, mouse_y: float, screen: pygame.Surface) -> None:
        """
        Handle mouse clicks on messages.
        """
        # Group messages by position
        position_messages: Dict[GrowlPosition, List[GrowlMessage]] = {}
        for msg in self.messages:
            if msg.position not in position_messages:
                position_messages[msg.position] = []
            position_messages[msg.position].append(msg)

        # Check clicks for each position group
        for position, messages in position_messages.items():
            x_ratio, y_ratio = self._position_offsets[position]
            base_x = screen.get_width() * x_ratio
            base_y = screen.get_height() * y_ratio
            
            total_height = 0
            for msg in messages:
                if msg.on_click_callback:
                    text_surface = self.font.render(msg.message, True, msg.color)
                    text_rect = text_surface.get_rect()
                    
                    # Calculate hit rect position
                    if position in [GrowlPosition.TOP_LEFT, GrowlPosition.MIDDLE_LEFT, GrowlPosition.BOTTOM_LEFT]:
                        hit_rect = pygame.Rect(
                            base_x + self.padding,
                            base_y + total_height,
                            text_rect.width + self.padding * 2,
                            msg.height
                        )
                    else:
                        hit_rect = pygame.Rect(
                            base_x - (text_rect.width + self.padding * 2) / 2,
                            base_y + total_height,
                            text_rect.width + self.padding * 2,
                            msg.height
                        )

                    if hit_rect.collidepoint(mouse_x, mouse_y):
                        msg.on_click_callback()
                
                total_height += msg.height + self.message_spacing

