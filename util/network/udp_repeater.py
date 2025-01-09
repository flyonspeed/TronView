#!/usr/bin/env python3

import socket
import threading
import logging
import argparse
import sys
import subprocess
from typing import Tuple, Optional

class UDPRepeater:
    def __init__(self, input_addr: Tuple[str, int], output_addr: Tuple[str, int], buffer_size: int = 1024):
        """
        Initialize UDP Repeater
        
        Args:
            input_addr: Tuple of (host, port) for input interface
            output_addr: Tuple of (host, port) for output interface
            buffer_size: Size of the receive buffer
        """
        self.input_addr = input_addr
        self.output_addr = output_addr
        self.buffer_size = buffer_size
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create sockets
        self.input_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def start(self):
        """Start the UDP repeater"""
        try:
            self.input_socket.bind(self.input_addr)
            self.running = True
            
            self.logger.info(f"UDP Repeater started")
            self.logger.info(f"Listening on {self.input_addr[0]}:{self.input_addr[1]}")
            self.logger.info(f"Forwarding to {self.output_addr[0]}:{self.output_addr[1]}")
            
            while self.running:
                try:
                    data, addr = self.input_socket.recvfrom(self.buffer_size)
                    self.output_socket.sendto(data, self.output_addr)
                    self.logger.debug(f"Forwarded {len(data)} bytes from {addr} to {self.output_addr}")
                except socket.error as e:
                    self.logger.error(f"Socket error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in UDP repeater: {e}")
            self.stop()
            
    def stop(self):
        """Stop the UDP repeater"""
        self.running = False
        self.input_socket.close()
        self.output_socket.close()
        self.logger.info("UDP Repeater stopped")

def get_interface_ip(interface_name: str) -> Optional[str]:
    """
    Get IP address for a network interface using the ip command
    
    Args:
        interface_name: Name of the network interface (e.g., 'wlan0', 'eth0')
    
    Returns:
        IP address as string if found, None otherwise
    """
    try:
        # Run ip addr show command for the specified interface
        cmd = ['ip', 'addr', 'show', interface_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
            
        # Parse the output to find the inet (IPv4) address
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                # Extract IP address (excluding subnet mask)
                ip = line.strip().split()[1].split('/')[0]
                return ip
        return None
    except Exception as e:
        logging.error(f"Error getting IP for interface {interface_name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='UDP Packet Repeater')
    parser.add_argument('--input-host', default='0.0.0.0', help='Input interface to listen on (IP or interface name)')
    parser.add_argument('--input-port', type=int, required=True, help='Input port to listen on')
    parser.add_argument('--output-host', required=True, help='Output interface to forward to (IP or interface name)')
    parser.add_argument('--output-port', type=int, required=True, help='Output port to forward to')
    parser.add_argument('--buffer-size', type=int, default=1024, help='Size of receive buffer')
    
    args = parser.parse_args()
    
    # Resolve interface names to IP addresses if needed
    input_host = args.input_host
    if not input_host == '0.0.0.0' and not input_host.replace('.', '').isdigit():
        resolved_ip = get_interface_ip(input_host)
        if resolved_ip:
            input_host = resolved_ip
            print(f"Resolved input interface {args.input_host} to IP: {input_host}")
        else:
            print(f"Failed to resolve input interface {args.input_host}, using as-is")
    
    output_host = args.output_host
    if not output_host.replace('.', '').isdigit():
        resolved_ip = get_interface_ip(output_host)
        if resolved_ip:
            output_host = resolved_ip
            print(f"Resolved output interface {args.output_host} to IP: {output_host}")
        else:
            print(f"Failed to resolve output interface {args.output_host}, using as-is")
    
    input_addr = (input_host, args.input_port)
    output_addr = (output_host, args.output_port)
    
    repeater = UDPRepeater(input_addr, output_addr, args.buffer_size)
    
    try:
        repeater.start()
    except KeyboardInterrupt:
        repeater.stop()
        sys.exit(0)

if __name__ == '__main__':
    main()