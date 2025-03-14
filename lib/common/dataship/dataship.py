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
from lib.common.graphic.edit_dropdown import menu_item

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

    
    # get a list of all fields and functions in the aircraft object
    def _get_all_fields(self, prefix: str = '', force_rebuild: bool = False) -> List[Any]:
        """
        Get a list of all fields in the aircraft object.
        
        Args:
            prefix (str): Prefix for nested object fields.
            force_rebuild (bool): If True, rebuild the field list even if cached.
        
        Returns:
            List[menu_item]: List of all fields in the aircraft object represented as menu_item objects.

        EXAMPLE:
        options = [
            menu_item("imuData", [
                menu_item("imuData[0]", [
                    menu_item("imuData[0].id"),
                    menu_item("imuData[0].name"),
                    menu_item("imuData[0].purpose"),
                    menu_item("imuData[0].address"),
                    menu_item("imuData[0].hz"),
                ]),
                menu_item("imuData[1]", [
                    menu_item("imuData[1].id"),
                    menu_item("imuData[1].name"),
                    menu_item("imuData[1].purpose"),
                    menu_item("imuData[1].address"),
                    menu_item("imuData[1].hz"),
                ]),
            ]),
            menu_item("gpsData", [
                menu_item("gpsData[0]", [
                    menu_item("gpsData[0].id"),
                    menu_item("gpsData[0].name"),
                    menu_item("gpsData[0].address"),
                    menu_item("gpsData[0].hz"),
                    menu_item("gpsData[0].latitude"),
                    menu_item("gpsData[0].longitude"),
                    menu_item("gpsData[0].altitude"),
                ]),
            ])
        ]

        """
        # if not force_rebuild and hasattr(self, '_all_fields'):
        #     #print(f"Using cached aircraft field list. len: {len(self._all_fields)}")
        #     return self._all_fields

        fields = []
        structured_fields = []

        def add_field(name: str, value: Any, current_prefix: str):
            full_name = f"{current_prefix}{name}" if current_prefix else name
            
            # Add the basic field to the flat list
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, float) or \
               isinstance(value, complex) or isinstance(value, bool) or value is None:
                fields.append(full_name)
            elif isinstance(value, list):
                fields.append(f"{full_name}[{len(value)}]")
                
                # Process list items
                if value and hasattr(value[0], '__dict__'):
                    # This is a list of objects
                    list_menu_item = menu_item(full_name)
                    
                    # For each item in the list, create a submenu
                    for i, item in enumerate(value):
                        item_name = f"{full_name}[{i}]"
                        item_menu = menu_item(item_name)
                        
                        # Add each attribute of the item to both the flat list and the submenu
                        for attr, attr_value in inspect.getmembers(item):
                            if not attr.startswith('_') and not inspect.ismethod(attr_value) and not inspect.isfunction(attr_value):
                                attr_full_name = f"{item_name}.{attr}"
                                fields.append(attr_full_name)
                                item_menu.add_submenu(menu_item(attr_full_name))
                        
                        # Add the item submenu to the list submenu
                        if item_menu.submenus:
                            list_menu_item.add_submenu(item_menu)
                    
                    # Add the list menu item to the structured fields
                    if list_menu_item.submenus:
                        structured_fields.append(list_menu_item)
                else:
                    # Simple list of values
                    for i, item in enumerate(value):
                        fields.append(f"{full_name}[{i}]")
            elif isinstance(value, tuple):
                fields.append(full_name)
            elif isinstance(value, dict):
                fields.append(full_name)
                for key, dict_value in value.items():
                    fields.append(f"{full_name}['{key}']")
            elif inspect.ismethod(value) or inspect.isfunction(value):
                fields.append(f"{full_name}()")
            elif isinstance(value, object):
                fields.append(f"{full_name}<obj>")

            # Recursively process objects with __dict__
            if hasattr(value, '__dict__') and not isinstance(value, Enum):
                obj_fields = []
                for attr, attr_value in inspect.getmembers(value):
                    if not attr.startswith('_') and not attr == 'get_all_fields':
                        add_field(attr, attr_value, f"{full_name}.")
                        if not inspect.ismethod(attr_value) and not inspect.isfunction(attr_value):
                            obj_fields.append(attr)


        # Process all members of the main object
        for name, value in inspect.getmembers(self):
            if not name.startswith('_'):
                add_field(name, value, prefix)

        self._all_fields = fields
        self._structured_fields = structured_fields
        #print(f"fields: {fields}")
        print(f"structured_fields: {structured_fields}")
        return structured_fields


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
