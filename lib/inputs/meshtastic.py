#!/usr/bin/env python

# Serial Meshtastic input source
# 2/26/2025  Topher

from ._input import Input
from lib import hud_utils
import struct
import time
import traceback
from lib.common.dataship.dataship import Dataship
from lib.common.dataship.dataship_targets import TargetData, Target
from lib.common.dataship.dataship_gps import GPSData
import meshtastic as mt
import meshtastic.serial_interface as mt_serial
from pubsub import pub
import json
from lib.common import shared # global shared objects stored here.


class meshtastic(Input):
    def __init__(self):
        self.name = "meshtastic"
        self.version = 1.0
        self.inputtype = "serial"
        self.targetData = TargetData()
        self.gpsData = GPSData()
        self.interface = None
        self.connected = False

    def initInput(self, num, dataship: Dataship):
        Input.initInput(self, num, dataship)  # call parent init Input.
        self.msg_unknown = 0
        self.msg_bad = 0
        self.onMessagePriority = None # None means onMessage is never called.
        self.dataship: Dataship = dataship

        self.serial_port = hud_utils.readConfig(  # serial input... example: "/dev/cu.PL2303G-USBtoUART110"
            self.name, "port", "/dev/ttyUSB0"
        )

        self.ignore_self = hud_utils.readConfigBool( self.name, "ignore_self", True)
        self.auto_reply = hud_utils.readConfigBool( self.name, "auto_reply", True)
        self.auto_reply_message = hud_utils.readConfig( self.name, "auto_reply_message", "ACK")

        # create targetData
        if (len(dataship.targetData) == 0):
            self.targetData = TargetData()
            self.targetData.id = "meshtastic_targets"
            self.targetData.source = "meshtastic"
            self.targetData.name = self.name
            self.targetData_index = len(dataship.targetData)  # Start at 0
            self.targetData.src_meshtastic_input = self # set the meshtastic input source.
            print("new meshtastic targets object "+str(self.targetData_index)+": "+str(self.targetData))
            dataship.targetData.append(self.targetData)
        else:
            print("meshtastic using existing targets object")
            self.targetData = dataship.targetData[0]
            self.targetData.src_meshtastic_input = self # set the meshtastic input source.

        # create gpsData
        self.gpsData = GPSData()
        self.gpsData.id = "meshtastic_gps"
        self.gpsData.inputSrcName = "meshtastic"
        self.gpsData.name = self.name
        self.gpsData_index = len(dataship.gpsData)  # Start at 0
        print("new meshtastic gps "+str(self.gpsData_index)+": "+str(self.gpsData))
        dataship.gpsData.append(self.gpsData)

        # use the first gpsData object as the source gps.
        self.targetData.src_gps = dataship.gpsData[0]

        if self.PlayFile is not None and self.PlayFile is not False:
            # load log file to playback.
            if self.PlayFile is True:
                defaultTo = "meshtastic_data1.txt"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser, self.input_logFileName = Input.openLogFile(self, self.PlayFile, "r")
        else:
            try:
                # Initialize meshtastic interface
                self.interface = mt_serial.SerialInterface(devPath=self.serial_port)
                self.connected = True
                
                # Subscribe to message events
                pub.subscribe(self.onReceive, "meshtastic.receive")
                pub.subscribe(self.onConnection, "meshtastic.connection.established")
                pub.subscribe(self.onConnectionLost, "meshtastic.connection.lost")
                
                # Store our node info
                if self.interface.myInfo:
                    print(f"meshtastic node id: {self.interface.myInfo.my_node_num}")
                    print(f"{self.interface.myInfo}")
                    print(f"{self.interface}")
                    self.targetData.meshtastic_node_num = self.interface.myInfo.my_node_num
                    self.targetData.meshtastic_node_device_name = self.interface.myInfo.pio_env
                    self.targetData.meshtastic_node_device_id = self.interface.myInfo.device_id
                
                self.targetData.meshtastic_node_name = self.interface.getLongName()

                # send startup message
                self.sendPayloadMsg("TronView Startup", None)
                
            except Exception as e:
                print(f"Failed to initialize meshtastic interface: {e}")
                traceback.print_exc()
                self.connected = False
    
    def print_debug(self, message):
        if self.dataship.debug_mode > 0:
            print(f"Meshtastic: {message}")

    def onReceive(self, packet, interface):
        """Handle incoming meshtastic messages"""
        try:
            # check gps data from meshtastic node
            my_node_info = self.interface.getMyNodeInfo()
            if my_node_info:
                if my_node_info['position']:
                    if my_node_info['position']['latitude'] is not None and my_node_info['position']['longitude'] is not None and my_node_info['position']['altitude'] is not None:
                        self.print_debug(f"meshtastic gps! lat: {my_node_info['position']['latitude']} lon: {my_node_info['position']['longitude']} alt: {my_node_info['position']['altitude']}")
                        self.gpsData.set_gps_location(my_node_info['position']['latitude'], my_node_info['position']['longitude'], my_node_info['position']['altitude'])

            self.print_debug(f"packet: {packet}")
            if self.ignore_self and packet["from"] == self.targetData.meshtastic_node_num:
                # get nodeId from packet
                self.targetData.meshtastic_node_id = packet["fromId"]
                self.print_debug(f"Ignoring self packet from {self.targetData.meshtastic_node_id} {self.targetData.meshtastic_node_num}")
                return
            if packet.get("decoded"):
                decoded = packet["decoded"]
                portnum = decoded["portnum"]  # what type of message is this?
                if portnum == 'TELEMETRY_APP':
                    self.print_debug("Telemetry message")
                elif portnum == 'POSITION_APP':
                    self.print_debug("Position message")
                elif portnum == 'TEXT_MESSAGE_APP':
                    self.print_debug("Text message")
                elif portnum == 'USER_LOCATION_APP':
                    self.print_debug("User location message")
                elif portnum == 'DEVICE_INFO_APP':
                    self.print_debug("Device info message")
                elif portnum == 'DEVICE_STATUS_APP':
                    self.print_debug("Device status message")
                elif portnum == 'DEVICE_SETTINGS_APP':
                    self.print_debug("Device settings message")
                else:
                    self.print_debug("Unknown message type")

                node = self.interface.nodesByNum[packet["from"]];
                #print(f"node: {node}")
                #print(f"node.user: {node['user']}")
                print(f"node.user.longName: {node['user']['longName']}")

                # Create a new target for the sender
                target = Target(node['user']['longName'])
                #target.inputSrcName = self.name
                #target.inputSrcNum = self.num
                target.address = packet["from"] # node number
                target.cat = 101  # meshtastic node type
                target.type = 101  # meshtastic node type
                target.meshtastic_node = node

                # text message payload so save to target payload messages.
                if portnum == 'TEXT_MESSAGE_APP':
                    # convert decoded['payload'] from bytes to string
                    payload = decoded["payload"].decode('utf-8')
                    print(f"Recv: from:{target.address} to:{self.targetData.meshtastic_node_num} msg: {payload}")
                    # add the payload message to the target payload messages. (before adding the target to the target list)
                    self.targetData.add_target_payload_message(target.address, target.callsign, packet["to"], payload)
                    if(packet["to"] == self.targetData.meshtastic_node_num):
                        # send a payload message to the sender.
                        if payload != self.auto_reply_message: # don't send an ack to the sender.
                            if self.auto_reply:
                                self.sendPayloadMsg(self.auto_reply_message, target)

                # Extract position data if available
                if "position" in decoded:
                    pos = decoded["position"]
                    target.lat = pos.get("latitude")
                    target.lon = pos.get("longitude")
                    target.alt = int(pos.get("altitude", 0) * 3.28084) # Convert meters to feet and round to the nearest integer
                    
                    if "groundSpeed" in pos:
                        target.speed = int(pos["groundSpeed"] * 2.23694) # Convert m/s to mph and round to the nearest integer
                    if "groundTrack" in pos:
                        target.track = int(pos["groundTrack"]) # round to the nearest integer
                    self.print_debug(f"Target Position: {target.lat}, {target.lon}, {target.alt}, {target.speed}, {target.track}")

                # Add the target to our target list
                self.targetData.addTarget(target)
                self.targetData.msg_count += 1
                self.targetData.msg_last = time.time()



                # print(self.interface.showNodes())

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
            if self.interface and self.interface.isConnected:
                self.interface.close()
    
    # send a payload message to a target.
    def sendPayloadMsg(self,text:str, target:Target=None):
        if self.interface and self.interface.isConnected:

            # if text is "position", send a position message with gps lat/lon/alt
            if text == "position":
                if len(self.dataship.gpsData) > 0:
                    if self.dataship.gpsData[0].Lat is not None or self.dataship.gpsData[0].Lon is not None:
                        alt = 0
                        if self.dataship.gpsData[0].Alt is not None:
                            alt = self.dataship.gpsData[0].Alt
                        gps = self.dataship.gpsData[0]
                        print("sending position {} {} {}".format(gps.Lat, gps.Lon, alt))
                        self.interface.sendPosition(gps.Lat, gps.Lon, alt)
                else:
                    print("meshtastic: no gps data. cant send position.")
            else:
                # else send a text message.
                if target is not None:
                    self.interface.sendText(text,target.address)
                else:
                    self.interface.sendText(text)
        else:
            print("no meshtastic interface connected")


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
