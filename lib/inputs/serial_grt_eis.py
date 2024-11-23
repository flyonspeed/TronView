#!/usr/bin/env python

# Serial input source
# GRT EIS engine data
# 11/22/2024  Created GRT EIS input. Topher

from ._input import Input
from lib import hud_utils
from . import _utils
import serial
import struct
from lib import hud_text
import binascii
import time
import traceback

class serial_grt_eis(Input):
    def __init__(self):
        self.name = "grt_eis"
        self.version = 1.0
        self.inputtype = "serial"

    def initInput(self,num,aircraft):
        Input.initInput(self,num,aircraft)  # call parent init Input.
        print("initInput %d: %s playfile: %s"%(num,self.name,self.PlayFile))
        if(self.PlayFile!=None and self.PlayFile!=False):
            # Get playback file.
            if self.PlayFile==True:
                defaultTo = "GRT_EIS_1.bin"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            self.efis_data_format = hud_utils.readConfig("DataInput", "format", "none")
            self.efis_data_port = hud_utils.readConfig("DataInput", "port", "/dev/ttyS0")
            self.efis_data_baudrate = hud_utils.readConfigInt(
                "DataInput", "baudrate", 9600  # GRT EIS uses 9600 baud
            )

            # open serial connection
            self.ser = serial.Serial(
                port=self.efis_data_port,
                baudrate=self.efis_data_baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )

    def closeInput(self,aircraft):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft
        
        try:
            # Look for header sequence FE FF FE
            while True:
                b1 = self.ser.read(1)
                if not b1:  # Handle timeout/no data
                    if self.isPlaybackMode:
                        self.ser.seek(0)
                        print("GRT EIS file reset")
                    return aircraft
                
                if b1[0] != 0xFE:
                    continue
                    
                b2 = self.ser.read(1)
                if not b2 or b2[0] != 0xFF:
                    continue
                    
                b3 = self.ser.read(1)
                if not b3 or b3[0] != 0xFE:
                    continue
                    
                break  # Found header sequence

            # Read the rest of the frame (63 bytes)
            frame = self.ser.read(63)
            if len(frame) != 63:
                return aircraft

            # Validate checksum
            checksum = 0
            for b in frame[:-1]:
                checksum += b
            checksum = (~checksum) & 0xFF
            
            if checksum != frame[-1]:
                aircraft.msg_bad += 1
                return aircraft

            ## example line data:
            ## 

            # Parse the frame using struct
            (tach, cht1, cht2, cht3, cht4, cht5, cht6,
             egt1, egt2, egt3, egt4, egt5, egt6,
             aux5, aux6, aspd, alt, volt, fuel_flow,
             unit, carb, roc_sign, oat,
             oil_temp, oil_press, aux1, aux2, aux3, aux4,
             coolant, eti, fuel_qty, hrs, mins, secs,
             end_hrs, end_mins, baro, mag_head, spare) = struct.unpack(
                '>H6H6H2HhHHBbbhHB4HHHHBBBHHB', frame[:-1])
            
            

            # Update aircraft engine data
            aircraft.engine.RPM = tach
            aircraft.engine.OilTemp = oil_temp
            aircraft.engine.OilPress = oil_press
            aircraft.engine.FuelFlow = round(fuel_flow * 0.1, 1)  # Adjust units as needed
            
            # Update CHTs
            for i, cht in enumerate([cht1, cht2, cht3, cht4, cht5, cht6]):
                aircraft.engine.CHT[i] = cht
                
            # Update EGTs
            for i, egt in enumerate([egt1, egt2, egt3, egt4, egt5, egt6]):
                aircraft.engine.EGT[i] = egt

            aircraft.engine.CoolantTemp = coolant
            aircraft.oat = oat
            
            # Update message counts
            aircraft.engine.msg_count += 1
            if self.textMode_showRaw:
                aircraft.engine.msg_last = binascii.hexlify(frame)
            else:
                aircraft.engine.msg_last = None

            if self.isPlaybackMode:
                time.sleep(0.01)  # Add delay in playback mode

            if self.output_logFile is not None:
                header = bytearray([0xFE, 0xFF, 0xFE])
                Input.addToLog(self, self.output_logFile, header)
                Input.addToLog(self, self.output_logFile, frame)

            return aircraft

        except serial.serialutil.SerialException as e:
            print(e)
            print("grt_eis serial exception")
            traceback.print_exc()
            aircraft.errorFoundNeedToExit = True
            
        return aircraft

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
