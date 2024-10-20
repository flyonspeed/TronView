import os
import importlib
import json
from lib.common import shared
from lib.common.graphic.edit_TronViewScreenObject import TronViewScreenObject

def save_screen_to_json():

    data = {
        "ver": {"version": "1.0"},  # You can update this version as needed
        "screen": {
            "title": "No Name",
            "width": shared.smartdisplay.x_end,
            "height": shared.smartdisplay.y_end
        },
        "screenObjects": [obj.to_dict() for obj in shared.CurrentScreen.ScreenObjects]
    }
    
    filename = "screen.json"

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = shared.DataDir + "screens/" + filename
    # if it doesn't end with .json then add it.
    if not filename.endswith(".json"):
        filename = filename + ".json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Screen saved to {filename}")

def load_screen_from_json(filename,from_templates=False):
    shared.CurrentScreen.ScreenObjects = []

    try:
        if from_templates:
            filename = "lib/screens/templates/" + filename
        else:
            filename = shared.DataDir + "screens/" + filename
        # if it doesn't end with .json then add it.
        if not filename.endswith(".json"):
            filename = filename + ".json"
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing screen objects
        shared.CurrentScreen.ScreenObjects.clear()
        
        # Set screen properties
        shared.CurrentScreen.title = data['screen']['title']
        #shared.smartdisplay.x_end = data['screen']['width']
        #shared.smartdisplay.y_end = data['screen']['height']
        
        # Load screen objects using the from_dict method
        for obj_data in data['screenObjects']:
            new_obj = TronViewScreenObject(shared.CurrentScreen.pygamescreen, obj_data['type'], obj_data['title'])
            new_obj.from_dict(obj_data)
            shared.CurrentScreen.ScreenObjects.append(new_obj)
        
        print(f"Screen loaded from {filename}")
    except Exception as e:
        # get full error
        import traceback
        traceback.print_exc()
        print(f"Error loading screen from {filename}: {str(e)}")
