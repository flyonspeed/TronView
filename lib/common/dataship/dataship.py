#!/usr/bin/env python

import inspect
from enum import Enum
from typing import List, Any
from lib.common.dataship.dataship_imu import IMUData
from lib.common.dataship.dataship_gps import GPSData
from lib.common.dataship.dataship_air import AirData
from lib.common.dataship.dataship_targets import TargetData
from lib.common.dataship.dataship_engine_fuel import EngineData, FuelData
from lib.common.dataship.dataship_nav import NavData
from lib.common.dataship.dataship_analog import AnalogData

class Interface(Enum):
    TEXT = "text"
    EDITOR = "editor" 
    GRAPHIC_2D = "graphic_2d"
    GRAPHIC_3D = "graphic_3d"

#############################################
## Class: DataShip
## Store status and converted data from input modules into this class for use by screens.
## Data should be converted into a common format and stored here. 
##
class Dataship(object):

    def __init__(self):
        self.sys_time_string = None 
        self.interface: Interface = Interface.TEXT  # Default to text interface

        #### new format for data ship
        self.internalData: InternalData = InternalData()
        self.imuData: List[IMUData] = []  # list of IMU objects
        self.gpsData: List[GPSData] = [] # list of GPS objects
        self.airData: List[AirData] = [] # list of Air objects
        self.engineData: List[EngineData] = [] # list of Engine objects
        self.fuelData: List[FuelData] = [] # list of Fuel objects
        self.targetData: List[TargetData] = [] # list of Target objects
        self.navData: List[NavData] = [] # list of Nav objects
        self.analogData: List[AnalogData] = [] # list of Analog objects
        
        self.debug_mode = 0
        self.errorFoundNeedToExit = False


    def get_imu1(self):
        return self.imus[0]

    def get_imu2(self):
        return self.imus[1]

    def get_imu3(self):
        return self.imus[2]

    
    # get a list of all fields and functions in the aircraft object
    def _get_all_fields(self, prefix: str = '', force_rebuild: bool = False) -> List[str]:
        """
        Get a list of all fields in the aircraft object.
        
        Args:
            prefix (str): Prefix for nested object fields.
            force_rebuild (bool): If True, rebuild the field list even if cached.
        
        Returns:
            List[str]: List of all fields in the aircraft object.
        """
        if not force_rebuild and hasattr(self, '_all_fields'):
            #print(f"Using cached aircraft field list. len: {len(self._all_fields)}")
            return self._all_fields

        fields = []

        def add_field(name: str, value: Any, current_prefix: str):
            full_name = f"{current_prefix}{name}" if current_prefix else name
            #print(f"Checking field: {full_name} with type: {type(value).__name__}", end=' ')

            if isinstance(value, str):
                fields.append(full_name)
            elif isinstance(value, int):
                fields.append(full_name)
            elif isinstance(value, float):
                fields.append(full_name)
            elif isinstance(value, complex):
                fields.append(full_name)
            elif isinstance(value, bool):
                fields.append(full_name)
            elif isinstance(value, list):
                fields.append(f"{full_name}[{len(value)}]")
                # show all items in the list
                for i, item in enumerate(value):
                    fields.append(f"{full_name}[{i}]")
            elif isinstance(value, tuple):
                fields.append(full_name)
            elif isinstance(value, dict):
                fields.append(full_name)
            elif value is None:
                fields.append(full_name)
            elif inspect.ismethod(value) or inspect.isfunction(value):
                fields.append(f"{full_name}()")
                #print("(added as method)")
            elif isinstance(value, object):
                #print("(skipped class)")
                fields.append(f"{full_name}<obj>")

            # if it has a __dict__ then recurse through it.
            if hasattr(value, '__dict__'):
                #print("(recursing)")
                for attr, attr_value in inspect.getmembers(value):
                    if not attr.startswith('_'):
                        add_field(attr, attr_value, f"{full_name}.")
            # else:
            #     fields.append(full_name)
            #     #print("(added as unknown type)")

        for name, value in inspect.getmembers(self):
            if not name.startswith('_'):
                add_field(name, value, prefix)

        self._all_fields = fields
        #print(f"Built field list with {len(fields)} items")
        return fields


#############################################
## Class: InternalData
class InternalData(object):
    def __init__(self):
        self.Temp = 0 # internal temp of cpu
        self.LoadAvg = None
        self.MemFree = None
        self.OS = None
        self.OSVer = None
        self.Hardware = None
        self.PythonVer = None
        self.GraphicEngine2d = None
        self.GraphicEngine2dVer = None
        self.GraphicEngine3d = None
        self.GraphicEngine3dVer = None


# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
