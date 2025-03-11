#!/usr/bin/env python

# wifi udp input source
# levil (ilevil and B.O.M)
# 1/23/2019  Topher
# 11/6/2024  Added IMU data.

from ._input import Input
from lib import hud_utils
import struct
from lib import hud_text
import binascii
import time
import socket
from lib.common.dataship.dataship import IMU
import traceback

class levil_wifi(Input):
    def __init__(self):
        self.name = "levil"
        self.version = 1.0
        self.inputtype = "network"

    def initInput(self,num,aircraft):
        Input.initInput( self,num, aircraft )  # call parent init Input.
        self.output_logBinary = True

        if(self.PlayFile!=None and self.PlayFile!=False):
            # if in playback mode then log file.
            # get file to read from config.  else default to..
            if self.PlayFile==True:
                defaultTo = "levil_data1.bin"
                self.PlayFile = hud_utils.readConfig(self.name, "playback_file", defaultTo)
            self.ser,self.input_logFileName = Input.openLogFile(self,self.PlayFile,"rb")
            self.isPlaybackMode = True
        else:
            self.udpport = hud_utils.readConfigInt("levil", "udpport", "43211")

            # open udp connection.
            self.ser = socket.socket(socket.AF_INET, #Internet
                                    socket.SOCK_DGRAM) #UDP
                             
            #Bind to any available address on port *portNum*
            print("using UDP port:"+str(self.udpport))
            self.ser.bind(("",self.udpport))
            
            #Prevent the socket from blocking until it receives all the data it wants
            #Note: Instead of blocking, it will throw a socket.error exception if it
            #doesn't get any data
            #self.ser.settimeout(.1)
            self.ser.setblocking(0)

        # create a empty imu object.
        self.imuData = IMU()
        self.imuData.id = "levil_imu"
        self.imuData.name = self.name
        self.imu_index = len(aircraft.imus)  # Start at 0
        aircraft.imus[self.imu_index] = self.imuData
        self.last_read_time = time.time()

    def closeInput(self,aircraft):
        if self.isPlaybackMode:
            self.ser.close()
        else:
            self.ser.close()

    def getNextChunck(self,aircraft):
        if self.isPlaybackMode:
            data = self.ser.read(300)
            if(len(data)==0): self.ser.seek(0)
            #TODO: read to the next ~ in the file??
            # x = 0
            # while x != 128: #read to 2nd ~
            #     t = self.ser.read(1)
            #     if len(t) != 0:
            #         x = ord(t)
            #         data.append(x)
            #     else:
            #         self.ser.seek(0) #if at end of file reset
            #         return bytes(0)
            return data
        else:
            try:
                #Attempt to receive up to 1024 bytes of data
                data = self.ser.recvfrom(1024)
                return data[0]
            except socket.timeout:
                pass
            except socket.error:
                #If no data is received, you get here, but it's not an error
                #Ignore and continue
                pass
        return bytes(0)

    #############################################
    ## Function: readMessage
    def readMessage(self, aircraft):
        if self.shouldExit == True: aircraft.errorFoundNeedToExit = True
        if aircraft.errorFoundNeedToExit: return aircraft
        if self.skipReadInput == True: return aircraft
        msg = self.getNextChunck(aircraft)
        #count = msg.count(b'~~')
        #print("-----------------------------------------------\nNEW Chunk len:"+str(len(msg))+" seperator count:"+str(count))
        #print("chunk:"+str(msg))

        for line in msg.split(b'~~'):
            if(len(line)>3):
                if(line[0]!=126): # if no ~ then add one...
                    newline = b''.join([b'~',line])
                else:
                    newline = line
                aircraft = self.processSingleMessage(newline,aircraft)
            #key = wait_key()
            #if(key=='q'): aircraft.errorFoundNeedToExit = True

        if self.output_logFile != None:
            #Input.addToLog(self,self.output_logFile,bytearray([5,2]))
            Input.addToLog(self,self.output_logFile,msg)


        return aircraft

    #############################################
    def processSingleMessage(self, msg, aircraft):
        try:
            
            if(len(msg)<1):
                pass
            elif(msg[0]==126 and msg[1]==ord('L') and msg[2]==ord('E')):  # Check for Levil specific messages ~LE
                #print(msg)
                #print("Len:"+str(len(msg)))
                #print("Message ID "+format(msg[3]));
                if(msg[3]==0): # status message
                    #print(msg)
                    #print("status message len:"+str(len(msg)))
                    # B          B     H     B    B   
                    FirmwareVer, Batt, Error,WAAS,Aux = struct.unpack(">BBHBB",msg[5:11])
                    self.FirmwareVer = FirmwareVer
                    self.Battery = Batt
                    if(msg[4]==2):
                        if(WAAS==1):
                            aircraft.gps.GPSWAAS = 1
                        else:
                            aircraft.gps.GPSWAAS = 0


                elif(msg[3]==1): # ahrs and air data.
                    #print("len:"+str(len(msg))+" "+str(msg[len(msg)-1]))
                    if(len(msg)==27):
                        # h   h     h   h      h         h,    h   H        h     B   B
                        Roll,Pitch,Yaw,Inclin,TurnCoord,GLoad,ias,pressAlt,vSpeed,AOA,OAT = struct.unpack(">hhhhhhhHhBB",msg[5:25]) 
                        aircraft.roll = Roll * 0.1
                        aircraft.pitch = Pitch * 0.1
                        aircraft.mag_head = Yaw * 0.1
                        aircraft.slip_skid = TurnCoord * 0.01
                        aircraft.vert_G = GLoad * 0.1
                        aircraft.ias = ias * 0.115078 # convert to MPH
                        aircraft.PALT = pressAlt
                        aircraft.vsi = vSpeed
                        if(msg[4]==2): # if version is 2 then read AOA and OAT
                            aircraft.aoa = AOA
                            aircraft.oat = OAT
                        aircraft.msg_last = msg
                        aircraft.msg_count += 1

                        # Update IMU data
                        self.imuData.roll = aircraft.roll
                        self.imuData.pitch = aircraft.pitch
                        self.imuData.yaw = aircraft.mag_head
                        if aircraft.debug_mode > 0:
                            current_time = time.time() # calculate hz.
                            self.imuData.hz = round(1 / (current_time - self.last_read_time), 1)
                            self.last_read_time = current_time
                        # Update the IMU in the aircraft's imu list
                        aircraft.imus[self.imu_index] = self.imuData

                    else:
                        aircraft.msg_bad +=1

                elif(msg[3]==2): # more metrics.. like AOA for BOM.
                    #print("additonal metrics message len:"+str(len(msg)))
                    AOA,OAT = struct.unpack(">BB",msg[5:7]) 
                    aircraft.aoa = AOA
                    aircraft.oat = OAT

                elif(msg[3]==7):
                    #print("additonal metrics message len:"+str(len(msg)))
                    WAASstatus, Sats, Power, OutRate = struct.unpack(">BBHB",msg[5:10]) 
                    aircraft.gps.SatsTracked = Sats
                    aircraft.gps.msg_count += 1

                else:
                    #print("unkown message id:"+str(msg[3])+" len:"+str(len(msg)))
                    #print(msg)
                    aircraft.msg_unknown += 1 #else unknown message.
                    
                if self.isPlaybackMode:  #if play back mode then add a delay.  Else reading a file is way to fast.
                    time.sleep(.02)
                    pass
                else:
                    #else reading realtime data via udp connection
                    pass

                return aircraft

            else:
                #print("GDL 90 message id:"+str(msg[1])+" "+str(msg[2])+" "+str(msg[3])+" len:"+str(len(msg)))
                #print(msg.hex())
                #aircraft.msg_bad += 1 #bad message found.
                if(msg[1]==0): # GDL heart beat. 
                    #print("GDL 90 HeartBeat message id:"+str(msg[1])+" len:"+str(len(msg)))
                    #print(msg.hex())
                    Status1,Status2 = struct.unpack(">BB",msg[2:4]) 
                    Time = struct.unpack(">H",msg[4:6]) 
                    #print("Time "+str(Time))
                elif(msg[1]==10): # GDL ownership
                    #print("GDL 90 HeartBeat message id:"+str(msg[1])+" len:"+str(len(msg)))
                    #print(msg.hex())
                    pass
                elif(msg[1]==101): # Foreflight id?
                    pass


            return aircraft
        except ValueError:
            print("levil value error exception")
            aircraft.errorFoundNeedToExit = True
        except struct.error:
            #error with read in length.. ignore for now?
            #print("Error with read in length")
            pass
        except Exception as e:
            aircraft.errorFoundNeedToExit = True
            print(e)
            print(traceback.format_exc())
        return aircraft




# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
