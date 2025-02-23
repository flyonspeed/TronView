#!/usr/bin/env python3

import serial.tools.list_ports
import json
from typing import List, Dict, Optional
import sys
import argparse
from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label
from textual.binding import Binding
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Static, Button
import re

def get_serial_ports() -> List[Dict[str, str]]:
    """
    Get a list of available serial ports with their descriptions.
    Ports with missing or "n/a" descriptions are sorted to the bottom.
    
    Returns:
        List[Dict[str, str]]: List of dictionaries containing port information
                             Each dict has 'port', 'description', and 'hwid' keys
    """
    ports = []
    
    # Iterate through all available serial ports
    for port in serial.tools.list_ports.comports():
        port_info = {
            'port': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'serial_number': port.serial_number,
            'interface': port.interface,
            'location': port.location,
            'manufacturer': port.manufacturer,
            'product': port.product,
            'vid': port.vid,
            'pid': port.pid,
        }
        ports.append(port_info)
    
    # Sort ports - putting ones with missing/n/a descriptions at the bottom
    def port_sort_key(port):
        desc = port['description'].lower()
        if not desc or desc == 'n/a':
            return (1, port['port'])  # Will sort after valid descriptions
        return (0, port['port'])      # Will sort before invalid descriptions
    
    return sorted(ports, key=port_sort_key)

def save_ports_to_file(output_file: str = 'available_serial_ports.json'):
    """
    Save the list of available serial ports to a JSON file.
    
    Args:
        output_file (str): Name of the output file (default: 'available_serial_ports.json')
    """
    ports = get_serial_ports()
    
    with open(output_file, 'w') as f:
        json.dump(ports, f, indent=4)
    
    print(f"Found {len(ports)} serial ports:")

def print_out():
    ports = get_serial_ports()
    for port in ports:
        print(f"Port: {port['port']}")
        print(f"Description: {port['description']}")
        print(f"Hardware ID: {port['hwid']}")
        print(f"Serial Number: {port['serial_number']}")
        print(f"Interface: {port['interface']}")
        print(f"Location: {port['location']}")
        print(f"Manufacturer: {port['manufacturer']}")
        print(f"Product: {port['product']}")
        print(f"VID: {port['vid']}")
        print(f"PID: {port['pid']}")
        print("-" * 50)

class PortSelectScreen(Screen):
    """A screen with a centered dialog for port selection."""
    title: str = None
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "select_port", "Select", show=True),
        Binding("escape", "quit", "Quit", show=False),  # Hidden binding for escape
    ]

    def compose(self) -> ComposeResult:
        if self.title is None:
            self.title = "Select Serial Port"
        yield Static(self.load_ascii_art(), id="background")
        with Center():
            yield Label(self.title, id="title")
            yield ListView(id="port-list", classes="port-list")
        if self.app._debug_mode:
            yield Static("", id="debug-log")

    def load_ascii_art(self) -> str:
        """Load ASCII art from file."""
        try:
            with open('docs/imgs/logo_txt_small.txt', 'r') as f:
                return f.read()
        except:
            return ""  # Return empty string if file not found

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.update_port_list()
        self.query_one("#port-list").index = 0
        
        # Set up periodic refresh every 2 seconds
        self.set_interval(2, self.refresh_ports)

    def update_port_list(self) -> None:
        """Update the port list display."""
        list_view = self.query_one("#port-list")
        current_ports = get_serial_ports()
        
        # Update app.ports first since it's used elsewhere
        self.app.ports = [p for p in current_ports if not self.app.known_ports.get(p['port'], {}).get('is_removed', False)]
        
        # Check if ports have changed
        ports_changed = False
        
        # Check for new or modified ports
        for port in current_ports:
            port_id = port['port']
            serial_num = port.get('serial_number', '')
            description = port.get('description', '')
            
            # Check if port exists by port ID, serial number, or description
            port_exists = False
            existing_port = None
            for known_port_id, known_port in self.app.known_ports.items():
                if (port_id == known_port_id or 
                    (serial_num and serial_num == known_port.get('serial_number', '')) or
                    (description and description != 'n/a' and 
                     description == known_port.get('description', ''))):
                    port_exists = True
                    existing_port = known_port
                    break
                    
            if not port_exists:
                # New port found
                ports_changed = True
                port['is_new'] = True
                port['is_removed'] = False
                self.app.known_ports[port_id] = port
            else:
                # Check if any port details have changed
                if existing_port['is_removed']:  # Port was previously marked as removed
                    ports_changed = True
                port['is_new'] = False
                port['is_removed'] = False
                self.app.known_ports[port_id]['is_removed'] = False

        # Check for removed ports
        for port_id, port in self.app.known_ports.items():
            serial_num = port.get('serial_number', '')
            description = port.get('description', '')
            # Check if port exists in current_ports by port ID, serial number, or description
            port_exists = any(
                p['port'] == port_id or 
                (serial_num and serial_num == p.get('serial_number', '')) or
                (description and description != 'n/a' and 
                 description == p.get('description', ''))
                for p in current_ports
            )
            
            if not port_exists:
                if not port.get('is_removed', False):  # Only mark as changed if newly removed
                    ports_changed = True
                port['is_removed'] = True
            
        # Force update on first run if there are ports
        if not list_view.children and current_ports:
            ports_changed = True

        # Only update display if ports have changed
        if ports_changed:
            list_view.clear()
            
            # Sort ports by name for consistent display order
            sorted_ports = sorted(self.app.known_ports.items(), key=lambda x: x[0])
            
            # Update display list
            position = 0
            for port_id, port in sorted_ports:

                if port['description'] == 'n/a':
                    display_text = f"{port['port']}"
                else:
                    display_text = f"{port['port']} ({port['description']})"

                if port['is_removed']:
                    display_text += " (removed)"
                    list_view.append(ListItem(Label(display_text, classes="removed-port")))
                elif port['is_new']:
                    list_view.append(ListItem(Label(display_text, classes="new-port")))
                else:
                    list_view.append(ListItem(Label(display_text)))
                
                # store the position of the port
                self.app.known_ports[port['port']]['position'] = position
                position += 1

    def log_debug(self, message: str) -> None:
        """Add message to debug log if debug mode is enabled."""
        if self.app._debug_mode:
            debug_log = self.query_one("#debug-log")
            current_text = debug_log.render().plain  # Use .plain to get the text content
            # Keep last 5 lines
            lines = (current_text.split('\n')[-4:] if current_text else []) + [message]
            debug_log.update('\n'.join(lines))

    def refresh_ports(self) -> None:
        """Refresh the port list while maintaining selection."""
        list_view = self.query_one("#port-list")
        
        # Store currently selected port ID if any
        selected_port_id = None
        if (list_view.index is not None and 
            len(self.app.ports) > 0 and 
            0 <= list_view.index < len(self.app.ports)):
            selected_port_id = self.app.ports[list_view.index]['port']
            #self.log_debug(f"Selected port ID: {selected_port_id}")
        
        # Update the port list
        self.update_port_list()
        
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def on_key(self, event) -> None:
        """Handle key press events."""
        if event.key == "enter":
            list_view = self.query_one("#port-list")
            if list_view.index is not None:
                # known_ports is a dictionary of port information, find the postion.
                #self.log_debug(f"Known ports: {self.app.known_ports}")
                for port in self.app.known_ports.values():
                    if port['position'] == list_view.index:
                        # check if the port is not removed
                        if not port['is_removed']:
                            self.app.selected_port = port
                            self.app.exit()
                        else:
                            self.log_debug(f"Port {port['port']} is removed")
                

class SerialPortSelector(App):
    """A Textual app to select a serial port."""
    
    CSS = """
    Screen {
        align: center middle;
        layers: base overlay;
    }

    #background {
        width: 100%;
        height: 100%;
        dock: top;
        content-align: center top;
        padding-top: 1;
        color: $primary-darken-2;
        layer: base;
    }

    Center {
        width: 65;
        height: auto;
        border: solid green;
        background: $surface;
        padding: 1;
        layer: overlay;
        margin-top: 0;
    }

    #title {
        text-align: center;
        padding: 0;
        color: $text;
        width: 100%;
    }

    .port-list {
        width: 100%;
        height: auto;
        max-height: 20;
        border: solid $accent;
        padding: 0 1;
        background: $surface;
    }

    .new-port {
        color: $success;
        /*background: $surface;*/
    }

    .removed-port {
        color: $primary-background;
        background: $surface;
    }

    #debug-log {
        dock: bottom;
        width: 100%;
        height: 35;
        background: $surface;
        color: $warning;
        border-top: solid $primary;
        padding: 0 1;
        overflow-y: hidden;
    }
    """
    
    def __init__(self, ports: List[Dict[str, str]], title: str = None, debug: bool = False):
        super().__init__()
        self.ports = ports
        self._debug_mode = debug
        # Initialize known_ports with status flags
        # known_ports is a dictionary of port information
        # the key is the port name
        # the value is a dictionary of port information
        # the dictionary contains the following keys:
        # 'port': the port name
        # 'is_new': a boolean flag to indicate if the port is new
        # 'is_removed': a boolean flag to indicate if the port is removed
        self.known_ports = {}
        for port in ports:
            port_info = port.copy()  # Create a copy to avoid modifying the original
            port_info['is_new'] = False
            port_info['is_removed'] = False
            self.known_ports[port['port']] = port_info
        self.selected_port = None
        self.title = title

    def on_mount(self) -> None:
        """Called when app is mounted."""
        portSelectScreen = PortSelectScreen()
        portSelectScreen.title = self.title
        self.push_screen(portSelectScreen)

def select_serial_port(title: str = None, debug: bool = False) -> Optional[Dict[str, str]]:
    """
    Show an interactive menu to select a serial port.
    
    Args:
        title (str, optional): Title for the selection window
        debug (bool, optional): Enable debug logging window
    
    Returns:
        Optional[Dict[str, str]]: Selected port information or None if no selection made
    """
    ports = get_serial_ports()
    if not ports:
        print("No serial ports found.")
        return None
        
    app = SerialPortSelector(ports, title=title, debug=debug)
    app.run()
    return app.selected_port

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List available serial ports and save to file')
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: available_serial_ports.json)')
    parser.add_argument('--select', 
                       action='store_true',
                       help='Show interactive selection menu')
    parser.add_argument('-d', '--debug',
                       action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.select:
        selected = select_serial_port(title="Available Serial Ports (Auto-refresh every 2 secs)", debug=args.debug)
        if selected:
            print(f"\nSelected port: {selected['port']}")
            print(f"Description: {selected['description']}")
    
    # if output file is provided, save to file
    if args.output:
        save_ports_to_file(args.output)
    
    # print out the ports
    print_out()