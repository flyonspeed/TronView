#!/usr/bin/env python
# -*-coding:utf-8 -*-
#
# NMEA GPS Data Monitor
# Topher. 2/1/2025
# command line options:
# -p <port> : specify the serial port
# -b <baud> : specify the baud rate
# -a : auto-detect the baud rate
# -h : show help
#
#
# Support for NMEA messages:
# RMC (Recommended Minimum Navigation Information)
# GSA (GPS DOP and Active Satellites)
# GLL (Geographic Position - Latitude/Longitude)
# ZDA (Time & Date)
# VTG (Track Made Good and Ground Speed)
# GSV (Satellites in View)
# GGA (Global Positioning System Fix Data)
# GNS (GPS Fix Data)
# additional support Dilution of Precision (DOP) PDOP, HDOP, VDOP
# magnetic variation
# date
# time
# signal type
# mode
# satellites in view


import serial
import pynmea2
import time
import os
from typing import Optional
import select
import sys
import termios
import tty
import argparse
from serial.tools import list_ports

# ANSI escape codes
CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"
BOLD = "\033[1m"
RESET = "\033[0m"
# Add color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RED = "\033[31m"
MAGENTA = "\033[35m"

def position_cursor(x: int, y: int) -> str:
    return f"\033[{y};{x}H"

def is_key_pressed():
    """Check if a key has been pressed without blocking."""
    if select.select([sys.stdin], [], [], 0)[0]:
        key = sys.stdin.read(1)
        return key
    return None

def get_key():
    """Get a single keypress without blocking or requiring Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_available_ports():
    """Get a list of available serial ports."""
    return list(list_ports.comports())

def choose_port():
    """Let user choose from available serial ports."""
    ports = get_available_ports()
    
    if not ports:
        print(RED + "No serial ports found!" + RESET)
        sys.exit(1)
    
    print(BLUE + "\nAvailable serial ports:" + RESET)
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    
    while True:
        try:
            choice = input(CYAN + "\nChoose port number (or 'q' to quit): " + RESET)
            if choice.lower() == 'q':
                sys.exit(0)
            
            port_num = int(choice) - 1
            if 0 <= port_num < len(ports):
                return ports[port_num].device
            else:
                print(RED + "Invalid choice. Please try again." + RESET)
        except ValueError:
            print(RED + "Please enter a number or 'q' to quit." + RESET)

def detect_baud_rate(port: str, total_timeout: int = 30, rate_timeout: int = 3) -> Optional[int]:
    """Auto-detect the baud rate by trying common rates.
    
    Args:
        port: Serial port to test
        total_timeout: Total seconds to spend trying all baud rates
        rate_timeout: Seconds to spend trying each baud rate
    """
    common_baud_rates = [4800,9600, 19200, 38400, 57600, 115200]
    
    print(BLUE + "\nAuto-detecting baud rate..." + RESET)
    start_time = time.time()
    
    for baud in common_baud_rates:
        # Check if we've exceeded total timeout
        if time.time() - start_time > total_timeout:
            print(RED + f"\nAuto-detection timed out after {total_timeout} seconds" + RESET)
            return None
            
        try:
            print(f"Trying {baud} baud...                    ", end='\r')
            # Set a very short timeout for the serial port itself
            with serial.Serial(port, baud, timeout=0.5) as ser:
                rate_start_time = time.time()
                
                while time.time() - rate_start_time < rate_timeout:
                    try:
                        line = ser.readline().decode('ascii', errors='replace')
                        if not line:  # If no data received, continue loop
                            continue
                        if line.startswith('$'):
                            try:
                                pynmea2.parse(line)
                                print(GREEN + f"\nFound valid NMEA messages at {baud} baud" + RESET)
                                return baud
                            except pynmea2.ParseError:
                                continue
                    except (serial.SerialException, UnicodeDecodeError):
                        continue
                
                print(f"No valid messages at {baud} baud        ", end='\r')
                
        except serial.SerialException:
            print(f"Failed to open port at {baud} baud        ", end='\r')
            continue
    
    print(RED + "\nCould not auto-detect baud rate" + RESET)
    return None

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='GPS NMEA Data Monitor')
    parser.add_argument('-p', '--port', 
                      help='Serial port (if not specified, will show available ports)')
    parser.add_argument('-b', '--baud', 
                      type=int,
                      help='Baud rate (default: auto-detect)')
    parser.add_argument('-a', '--auto',
                      action='store_true',
                      help='Auto-detect baud rate')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Check for available ports first
    available_ports = get_available_ports()
    if not available_ports:
        print(RED + "No serial ports were found on this system. Please check your connections and try again." + RESET)
        sys.exit(1)
    
    # If no port specified, let user choose
    if args.port is None:
        port = choose_port()
    else:
        port = args.port

    # Handle baud rate
    if args.baud is None or args.auto:
        detected_baud = detect_baud_rate(port, total_timeout=20, rate_timeout=2)
        if detected_baud:
            baudrate = detected_baud
        else:
            print(YELLOW + "Using default baud rate of 9600" + RESET)
            baudrate = 9600
    else:
        baudrate = args.baud

    # Initialize variables
    bytes_received = 0
    messages_received = 0
    line = ""
    unknown_messages = set()
    message_counts = {}
    gps_info = {
        'device': 'Unknown',
        'version': 'Unknown',
        'mode': 'Unknown',
        'signal_type': 'Unknown',
        'magnetic_variation': 'Unknown',
        'hdop': 'Unknown',
        'pdop': 'Unknown',
        'vdop': 'Unknown',
        'date': 'Unknown'
    }

    try:
        # Set stdin to non-blocking mode
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        
        # Open serial port
        print(f"Opening {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate)
        print(CLEAR_SCREEN + CURSOR_HOME)
        
        while True:
            # Check for 'q' keypress
            key = is_key_pressed()
            if key and key.lower() == 'q':
                print(position_cursor(2, 24) + GREEN + "Quitting..." + RESET)
                break
            
            try:
                # Debug information at bottom of screen
                print(position_cursor(2, 20) + BOLD + "Debug Information:" + RESET)
                print(position_cursor(2, 21) + f"Bytes received: {bytes_received}")
                print(position_cursor(2, 22) + f"Raw data: {line.strip()}")

                # Read line from serial port
                line = ser.readline().decode('ascii', errors='replace')
                bytes_received += len(line)
                
                if line.startswith('$'):
                    messages_received += 1
                    msg_type = line[3:6]  # Extract message type (e.g., GGA, RMC)
                    message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
                    
                    try:
                        msg = pynmea2.parse(line)
                    except pynmea2.ParseError as e:
                        print(position_cursor(2, 24) + RED + f"Parse error: {str(e)}" + RESET)
                        continue

                    # Update GPS device information based on message type
                    if isinstance(msg, pynmea2.RMC):
                        print(position_cursor(2, 13) + CYAN + f"Date: {msg.datestamp}" + RESET)
                        if msg.mag_variation is not None:
                            gps_info['magnetic_variation'] = f"{msg.mag_variation}° {msg.mag_var_dir}"

                    elif isinstance(msg, pynmea2.GSA):
                        print(position_cursor(50, 8) + BOLD + BLUE + "Dilution of Precision:" + RESET)
                        print(position_cursor(50, 9) + YELLOW + f"Mode: {msg.mode_fix_type}D {msg.mode}" + RESET)
                        print(position_cursor(50, 10) + CYAN + f"PDOP: {msg.pdop}" + RESET)
                        print(position_cursor(50, 11) + CYAN + f"HDOP: {msg.hdop}" + RESET)
                        print(position_cursor(50, 12) + CYAN + f"VDOP: {msg.vdop}" + RESET)
                        gps_info['pdop'] = msg.pdop
                        gps_info['hdop'] = msg.hdop
                        gps_info['vdop'] = msg.vdop

                    elif isinstance(msg, pynmea2.GLL):
                        print(position_cursor(50, 14) + BOLD + BLUE + "Geographic Position:" + RESET)
                        print(position_cursor(50, 15) + CYAN + 
                              f"Lat: {msg.latitude}° {msg.lat_dir} Lon: {msg.longitude}° {msg.lon_dir}" + RESET)
                        print(position_cursor(50, 16) + YELLOW + f"Valid: {msg.status}" + RESET)

                    elif isinstance(msg, pynmea2.ZDA):
                        print(position_cursor(50, 18) + BOLD + BLUE + "Time & Date:" + RESET)
                        print(position_cursor(50, 19) + CYAN + 
                              f"UTC: {msg.timestamp} Date: {msg.day}/{msg.month}/{msg.year}" + RESET)

                    # Display message statistics
                    print(position_cursor(2, 25) + BOLD + BLUE + "Message Statistics:" + RESET)
                    stats_y = 26
                    for msg_type, count in sorted(message_counts.items()):
                        print(position_cursor(2, stats_y) + YELLOW + f"{msg_type}: {count}" + RESET)
                        stats_y += 1

                    # Track unknown messages
                    if not any(isinstance(msg, cls) for cls in [
                        pynmea2.GGA, pynmea2.GSV, pynmea2.VTG, pynmea2.RMC, 
                        pynmea2.GSA, pynmea2.GLL, pynmea2.ZDA
                    ]):
                        unknown_messages.add(type(msg).__name__)
                        print(position_cursor(2, stats_y) + RED + "Unknown messages: " + 
                              ", ".join(unknown_messages) + RESET)

                    # Update GPS device information
                    if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                        gps_info['signal_type'] = 'GPS+GLONASS' if line.startswith('$GN') else 'GPS'
                        if msg.gps_qual == 1:
                            gps_info['mode'] = 'Autonomous'
                        elif msg.gps_qual == 2:
                            gps_info['mode'] = 'DGPS'
                        elif msg.gps_qual == 4:
                            gps_info['mode'] = 'RTK Fixed'
                        elif msg.gps_qual == 5:
                            gps_info['mode'] = 'RTK Float'
                    
                    # Display GPS device information
                    print(position_cursor(2, 15) + BOLD + BLUE + "GPS Device Information:" + RESET)
                    print(position_cursor(2, 16) + CYAN + f"Signal Type: {gps_info['signal_type']}" + RESET)
                    print(position_cursor(2, 17) + CYAN + f"Mode: {gps_info['mode']}" + RESET)
                    
                    if isinstance(msg, pynmea2.GGA):
                        print(position_cursor(2, 1) + BOLD + BLUE + "GPS Position Data:" + RESET)
                        print(position_cursor(2, 3) + CYAN + f"Latitude:  {msg.latitude}° {'N' if msg.lat_dir == 'N' else 'S'}" + RESET)
                        print(position_cursor(2, 4) + CYAN + f"Longitude: {msg.longitude}° {'E' if msg.lon_dir == 'E' else 'W'}" + RESET)
                        print(position_cursor(2, 5) + CYAN + f"Altitude:  {msg.altitude} {msg.altitude_units}" + RESET)
                        print(position_cursor(2, 6) + YELLOW + f"Time:      {msg.timestamp}" + RESET)
                        print(position_cursor(2, 7) + GREEN + f"Fix Quality: {msg.gps_qual}" + RESET)
                        print(position_cursor(2, 8) + GREEN + f"Satellites: {msg.num_sats}" + RESET)
                        
                    if isinstance(msg, pynmea2.GSV):
                        print(position_cursor(50, 1) + BOLD + MAGENTA + "Satellite Details:" + RESET)
                        sat_count = (msg.msg_num, msg.num_messages, msg.num_sv_in_view)
                        print(position_cursor(50, 3) + YELLOW + f"Satellites in view: {msg.num_sv_in_view}" + RESET)
                        
                        for i in range(4):  # GSV messages contain up to 4 satellites
                            try:
                                if msg.sv_prn_num_1:
                                    sat_data = [
                                        msg.sv_prn_num_1, msg.elevation_deg_1, 
                                        msg.azimuth_1, msg.snr_1
                                    ]
                                    print(position_cursor(50, 4+i) + 
                                          CYAN + f"SAT{i+1}: PRN:{sat_data[0]} EL:{sat_data[1]}° "+
                                          f"AZ:{sat_data[2]}° SNR:{sat_data[3]}dB" + RESET)
                            except AttributeError:
                                continue
                    
                    if isinstance(msg, pynmea2.VTG):
                        print(position_cursor(2, 10) + BOLD + GREEN + "Movement Data:" + RESET)
                        print(position_cursor(2, 11) + YELLOW + f"Speed: {msg.spd_over_grnd_kmph} km/h" + RESET)
                        print(position_cursor(2, 12) + YELLOW + f"Track: {msg.true_track}°" + RESET)
                        
            except pynmea2.ParseError as e:
                print(position_cursor(2, 24) + RED + f"Parse error: {str(e)}" + RESET)
                continue
            except UnicodeDecodeError as e:
                print(position_cursor(2, 24) + RED + f"Decode error: {str(e)}" + RESET)
                continue
                
            time.sleep(0.1)  # Small delay to prevent CPU overload
            
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if 'ser' in locals():
            ser.close()
        print("\n")  # Move to a new line after exiting

if __name__ == "__main__":
    main()
