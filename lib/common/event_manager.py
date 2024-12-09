from typing import List, Dict, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import time

class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    id: str
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    delay: float = 0.0  # Delay in seconds before executing
    created_at: float = 0.0
    repeat: bool = False
    repeat_interval: float = 0.0  # Time between repeats in seconds
    last_run: float = 0.0
    conditions: Dict = None  # Optional conditions that must be met

class EventManager:
    def __init__(self):
        self.events: List[Event] = []
        self.running = True
        
    def add_event(
        self,
        id: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        delay: float = 0.0,
        repeat: bool = False,
        repeat_interval: float = 0.0,
        conditions: Dict = None
    ) -> None:
        """
        Add a new event to the manager.
        
        Args:
            id: Unique identifier for the event
            callback: Function to call when event is processed
            priority: Priority level for the event
            delay: Time to wait before first execution
            repeat: Whether the event should repeat
            repeat_interval: Time between repeats
            conditions: Dictionary of conditions that must be met for event to run
        """
        event = Event(
            id=id,
            callback=callback,
            priority=priority,
            delay=delay,
            created_at=time.time(),
            repeat=repeat,
            repeat_interval=repeat_interval,
            conditions=conditions
        )
        self.events.append(event)
        # Sort events by priority
        self.events.sort(key=lambda x: x.priority.value, reverse=True)

    def remove_event(self, event_id: str) -> None:
        """Remove an event by its ID."""
        self.events = [e for e in self.events if e.id != event_id]

    def check_conditions(self, conditions: Dict) -> bool:
        """
        Check if all conditions for an event are met.
        Override this method to implement custom condition checking logic.
        """
        if not conditions:
            return True
        # Implement your condition checking logic here
        return True

    def process_events(self) -> None:
        """
        Process all pending events based on their priority and timing.
        Should be called regularly from the main loop.
        """
        if not self.running:
            return

        current_time = time.time()
        processed_events = []

        for event in self.events:
            # Skip if delay hasn't elapsed yet
            if current_time - event.created_at < event.delay:
                continue

            # For repeating events, check if enough time has passed since last run
            if event.repeat and event.last_run > 0:
                if current_time - event.last_run < event.repeat_interval:
                    continue

            # Check if conditions are met
            if not self.check_conditions(event.conditions):
                continue

            try:
                event.callback()
                event.last_run = current_time

                # If event is not repeating, mark it for removal
                if not event.repeat:
                    processed_events.append(event)

            except Exception as e:
                print(f"Error processing event {event.id}: {str(e)}")
                processed_events.append(event)  # Remove failed events

        # Remove processed non-repeating events
        for event in processed_events:
            self.events.remove(event)

    def clear_events(self) -> None:
        """Clear all events from the manager."""
        self.events.clear()

    def pause(self) -> None:
        """Pause event processing."""
        self.running = False

    def resume(self) -> None:
        """Resume event processing."""
        self.running = True

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by its ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None 