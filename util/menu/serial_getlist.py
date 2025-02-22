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
    
    return ports

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

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "select_port", "Select", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Center():
            yield Static("Select Serial Port", id="title")
            yield ListView(id="port-list", classes="port-list")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        list_view = self.query_one("#port-list")
        for port in self.app.ports:
            display_text = f"{port['port']} - {port['description']}"
            list_view.append(ListItem(Label(display_text)))

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
    }

    Center {
        width: 40%;
        height: auto;
        border: solid green;
        background: $surface;
        padding: 1;
    }

    #title {
        text-align: center;
        padding: 1;
        background: $accent;
        color: $text;
        width: 100%;
    }

    .port-list {
        width: 100%;
        height: auto;
        max-height: 20;
        border: solid $accent;
        padding: 0 1;
    }
    """
    
    def __init__(self, ports: List[Dict[str, str]]):
        super().__init__()
        self.ports = ports
        self.selected_port = None

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.push_screen(PortSelectScreen())

def select_serial_port() -> Optional[Dict[str, str]]:
    """
    Show an interactive menu to select a serial port.
    
    Returns:
        Optional[Dict[str, str]]: Selected port information or None if no selection made
    """
    ports = get_serial_ports()
    if not ports:
        print("No serial ports found.")
        return None
        
    app = SerialPortSelector(ports)
    app.run()
    return app.selected_port

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List available serial ports and save to file')
    parser.add_argument('-o', '--output', 
                       default='available_serial_ports.json',
                       help='Output file path (default: available_serial_ports.json)')
    parser.add_argument('--select', 
                       action='store_true',
                       help='Show interactive selection menu')
    
    args = parser.parse_args()
    
    if args.select:
        selected = select_serial_port()
        if selected:
            print(f"\nSelected port: {selected['port']}")
            print(f"Description: {selected['description']}")
    
    # if output file is provided, save to file
    if args.output:
        save_ports_to_file(args.output)
