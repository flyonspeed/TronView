#!/usr/bin/env python

import serial
import time
import struct

class SerialParser:
    def __init__(self, port='/dev/ttyS0', baudrate=115200):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )
        self.serial_buffer = ''
        self.serial_millis = time.time()
        self.Pitch = 0.0
        self.Roll = 0.0
        self.IAS = 0.0
        self.Palt = 0.0
        self.TurnRate = 0.0
        self.LateralG = 0.0
        self.VerticalG = 0.0
        self.PercentLift = 0
        self.AOA = 0.0
        self.iVSI = 0.0
        self.OAT = 0
        self.FlightPath = 0.0
        self.FlapPos = 0
        self.OnSpeedStallWarnAOA = 0.0
        self.OnSpeedSlowAOA = 0.0
        self.OnSpeedFastAOA = 0.0
        self.OnSpeedTonesOnAOA = 0.0
        self.gOnsetRate = 0.0
        self.SpinRecoveryCue = 0
        self.DataMark = 0

    def read_serial(self):
        while True:
            if self.ser.in_waiting > 0:
                inChar = self.ser.read(1).decode('utf-8')
                if inChar == '#':
                    self.serial_buffer = inChar
                    continue

                if len(self.serial_buffer) > 80:
                    self.serial_buffer = ''
                    print("Serial data buffer overflow")
                    continue

                if self.serial_buffer:
                    self.serial_buffer += inChar

                    if len(self.serial_buffer) == 80 and self.serial_buffer[0] == '#' and self.serial_buffer[1] == '1' and inChar == '\n':
                        # Calculate CRC
                        calcCRC = sum([ord(c) for c in self.serial_buffer[:76]]) & 0xFF
                        receivedCRC = int(self.serial_buffer[76:78], 16)

                        if calcCRC == receivedCRC:
                            self.parse_data()
                            self.serial_millis = time.time()
                        else:
                            print("ONSPEED CRC Failed")

    def parse_data(self):
        self.Pitch = float(self.serial_buffer[2:6]) / 10
        self.Roll = float(self.serial_buffer[6:11]) / 10
        self.IAS = float(self.serial_buffer[11:15]) / 10
        self.Palt = float(self.serial_buffer[15:21])
        self.TurnRate = float(self.serial_buffer[21:26]) / 10
        self.LateralG = float(self.serial_buffer[26:29]) / 100
        self.VerticalG = float(self.serial_buffer[29:32]) / 10
        self.PercentLift = int(self.serial_buffer[32:34])
        self.AOA = float(self.serial_buffer[34:38]) / 10
        self.iVSI = float(self.serial_buffer[38:42]) * 10
        self.OAT = int(self.serial_buffer[42:45])
        self.FlightPath = float(self.serial_buffer[45:49]) / 10
        self.FlapPos = int(self.serial_buffer[49:52])
        self.OnSpeedStallWarnAOA = float(self.serial_buffer[52:56]) / 10
        self.OnSpeedSlowAOA = float(self.serial_buffer[56:60]) / 10
        self.OnSpeedFastAOA = float(self.serial_buffer[60:64]) / 10
        self.OnSpeedTonesOnAOA = float(self.serial_buffer[64:68]) / 10
        self.gOnsetRate = float(self.serial_buffer[68:72]) / 100
        self.SpinRecoveryCue = int(self.serial_buffer[72:74])
        self.DataMark = int(self.serial_buffer[74:76])

        self.serial_buffer = ""
        self.serial_process()

    def serial_process(self):
        if self.AOA == -100:
            self.AOA = 0.0

        # Add smoothing and processing logic as needed
        # Example:
        # self.SmoothedAOA = self.SmoothedAOA * aoaSmoothingAlpha + (1 - aoaSmoothingAlpha) * self.AOA

        # Print or process the parsed values
        print(f"ONSPEED data: IAS {self.IAS:.2f}, Pitch {self.Pitch:.1f}, Roll {self.Roll:.1f}, LateralG {self.LateralG:.2f}, VerticalG {self.VerticalG:.2f}, Palt {self.Palt:.1f}, iVSI {self.iVSI:.1f}, AOA: {self.AOA:.1f}")

if __name__ == "__main__":
    parser = SerialParser()
    parser.read_serial()
