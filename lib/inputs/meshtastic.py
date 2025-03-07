#!/usr/bin/env python

# Serial Meshtastic input source
# 2/26/2025  Topher

from ._input import Input
from lib import hud_utils
import struct
import time
import traceback
from lib.common.dataship.dataship import IMUData
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_air import AirData
from ..common.dataship.dataship_targets import TargetData, Target
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import json

class meshtastic(Input):
    def __init__(self):
        self.name = "meshtastic"
        self.version = 1.0
        self.inputtype = "serial"
        self.imuData = IMUData()
        self.airData = AirData()
        self.targetData = TargetData()
        self.interface = None
        self.connected = False

    def initInput(self, num, dataship: Dataship):
        Input.initInput(self, num, dataship)  # call parent init Input.
        self.msg_unknown = 0
        self.msg_bad = 0
        
        if self.PlayFile is not None and self.PlayFile is not False:
            # load log file to playback.
            if self.PlayFile is True:
                defaultTo = "meshtastic_data1.txt"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self, self.PlayFile, "r")
        else:
            try:
                # Initialize meshtastic interface
                self.interface = meshtastic.serial_interface.SerialInterface()
                self.connected = True
                
                # Subscribe to message events
                pub.subscribe(self.onReceive, "meshtastic.receive")
                pub.subscribe(self.onConnection, "meshtastic.connection.established")
                pub.subscribe(self.onConnectionLost, "meshtastic.connection.lost")
                
                # Store our node info
                if self.interface.myInfo:
                    self.targetData.meshtastic_node_id = self.interface.myInfo.get('id')
                
            except Exception as e:
                print(f"Failed to initialize meshtastic interface: {e}")
                traceback.print_exc()
                self.connected = False

    def onReceive(self, packet, interface):
        """Handle incoming meshtastic messages"""
        try:
            if packet.get("decoded"):
                decoded = packet["decoded"]
                
                # Create a new target for the sender
                target = Target(str(packet["fromId"]))
                target.inputSrcName = self.name
                target.inputSrcNum = self.num
                target.address = packet["fromId"]
                target.cat = 101  # meshtastic node type
                
                # Extract position data if available
                if "position" in decoded:
                    pos = decoded["position"]
                    target.lat = pos.get("latitude")
                    target.lon = pos.get("longitude")
                    target.alt = pos.get("altitude", 0) * 3.28084  # Convert meters to feet
                    
                    if "ground_speed" in pos:
                        target.speed = pos["ground_speed"] * 2.23694  # Convert m/s to mph
                    if "ground_track" in pos:
                        target.track = pos["ground_track"]
                
                # Add the target to our target list
                self.targetData.addTarget(target)
                self.targetData.msg_count += 1
                self.targetData.msg_last = time.time()
                
        except Exception as e:
            print(f"Error processing meshtastic message: {e}")
            traceback.print_exc()
            self.targetData.msg_bad += 1

    def onConnection(self, interface, topic=pub.AUTO_TOPIC):
        """Handle connection established event"""
        print("Meshtastic connection established")
        self.connected = True

    def onConnectionLost(self, interface, topic=pub.AUTO_TOPIC):
        """Handle connection lost event"""
        print("Meshtastic connection lost")
        self.connected = False

    def closeInput(self, dataship: Dataship):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            if self.interface:
                self.interface.close()

    def readMessage(self, dataship: Dataship):
        if dataship.errorFoundNeedToExit:
            return dataship
        
        try:
            # In playback mode, read from file
            if self.isPlaybackMode:
                # ... existing playback code ...
                pass
            else:
                # For live mode, messages are handled by callbacks
                # Just update target ages and cleanup
                self.targetData.cleanUp(dataship)
                
            return dataship
            
        except ValueError as ex:
            print("conversion error")
            print(ex)
            traceback.print_exc()
            dataship.errorFoundNeedToExit = True
        except Exception as e:
            dataship.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
        return dataship

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
