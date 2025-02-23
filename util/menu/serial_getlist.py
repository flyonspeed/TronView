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
            'hwid': port.hwid
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
    for port in ports:
        print(f"Port: {port['port']}")
        print(f"Description: {port['description']}")
        print(f"Hardware ID: {port['hwid']}")
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
            #yield Static(self.title, id="title", shrink=True, classes="title")
            yield Label(self.title, id="title")
            yield ListView(id="port-list", classes="port-list")

    def load_ascii_art(self) -> str:
        """Load ASCII art from file."""
        try:
            with open('docs/imgs/logo_txt_small.txt', 'r') as f:
                return f.read()
        except:
            return ""  # Return empty string if file not found

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        list_view = self.query_one("#port-list")
        for port in self.app.ports:
            display_text = f"{port['port']} - {port['description']}"
            list_view.append(ListItem(Label(display_text)))
        
        # Select the first item if ports exist
        if self.app.ports:
            list_view.index = 0

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def on_key(self, event) -> None:
        """Handle key press events."""
        if event.key == "enter":
            list_view = self.query_one("#port-list")
            if list_view.index is not None:
                self.app.selected_port = self.app.ports[list_view.index]
                self.app.exit()

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
        /*background: $accent;*/
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
    """
    
    def __init__(self, ports: List[Dict[str, str]], title: str = None):
        super().__init__()
        self.ports = ports
        self.selected_port = None
        self.title = title
    def on_mount(self) -> None:
        """Called when app is mounted."""
        portSelectScreen = PortSelectScreen()
        portSelectScreen.title = self.title
        self.push_screen(portSelectScreen)

def select_serial_port(title: str = None) -> Optional[Dict[str, str]]:
    """
    Show an interactive menu to select a serial port.
    
    Returns:
        Optional[Dict[str, str]]: Selected port information or None if no selection made
    """
    ports = get_serial_ports()
    if not ports:
        print("No serial ports found.")
        return None
        
    app = SerialPortSelector(ports,title=title)
    app.run()
    return app.selected_port

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List available serial ports and save to file')
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: available_serial_ports.json)')
    parser.add_argument('--select', 
                       action='store_true',
                       help='Show interactive selection menu')
    
    args = parser.parse_args()
    
    if args.select:
        selected = select_serial_port(title="Available Serial Ports")
        if selected:
            print(f"\nSelected port: {selected['port']}")
            print(f"Description: {selected['description']}")
    
    # if output file is provided, save to file
    if args.output:
        save_ports_to_file(args.output)
