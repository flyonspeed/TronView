import os
import importlib
import json
from lib.common import shared
from lib.common.graphic.edit_TronViewScreenObject import TronViewScreenObject
from datetime import datetime
from lib import hud_utils

def save_screen_to_json(filename=None, update_settings_last_run=True):

    # shared.pygamescreen is pygame screen
    # shared.smartdisplay is smartdisplay object
    # shared.CurrentScreen is current screen object
    if filename is not None:
        shared.CurrentScreen.filename = filename

    if shared.CurrentScreen.filename is None:
        shared.CurrentScreen.filename = "screen.json"

    if not shared.CurrentScreen.filename.endswith(".json"):
        shared.CurrentScreen.filename = shared.CurrentScreen.filename + ".json"
    
    # if the screen name is empty or none, then use the filename without the extension
    if shared.CurrentScreen.name == "" or shared.CurrentScreen.name is None:
        shared.CurrentScreen.name = shared.CurrentScreen.filename.split(".")[0]

    data = {
        "ver": {"version": "1.0"},  # You can update this version as needed
        "screen": {
            "title": shared.CurrentScreen.name,
            "filename": shared.CurrentScreen.filename,
            "width": shared.smartdisplay.x_end,
            "height": shared.smartdisplay.y_end,
            "date_updated": datetime.now().strftime("%Y%m%d_%H%M%S")
        },
        "screenObjects": [obj.to_dict() for obj in shared.CurrentScreen.ScreenObjects]
    }
    
    filename = shared.CurrentScreen.filename

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = shared.DataDir + "screens/" + filename
    # if it doesn't end with .json then add it.
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Screen saved to {filename}")

    # update the last run config
    if update_settings_last_run:
        hud_utils.writeConfig("Main", "screen", shared.CurrentScreen.filename)



########################################################
# Load screen from json file
########################################################
def load_screen_from_json(filename,from_templates=False, update_settings_last_run=True):

    if not hasattr(shared.CurrentScreen, "ScreenObjects"):
        shared.CurrentScreen.ScreenObjects = []    
    shared.CurrentScreen.ScreenObjects = []

    try:

        # if filename starts with "template:" then load from templates
        if filename.startswith("template:"):
            filename = filename.split(":")[1]
            from_templates = True

        if from_templates:
            filename = "lib/screens/templates/" + filename
        else:
            filename = shared.DataDir + "screens/" + filename
        # if it doesn't end with .json then add it.
        if not filename.endswith(".json"):
            filename = filename + ".json"
        with open(filename, 'r') as f:
            data = json.load(f)
        
        just_filename = filename.split("/")[-1]


        # Clear existing screen objects
        shared.CurrentScreen.ScreenObjects.clear()
        
        # Set screen properties
        shared.CurrentScreen.name = data['screen']['title']
        if from_templates:
            shared.CurrentScreen.filename = "" # reset filename to empty string so when we save it the user will enter a new filename.
            # make sure filename exists and is not empty
            shared.CurrentScreen.loaded_from_template = just_filename
        else:
            shared.CurrentScreen.filename = just_filename
        
        # Load screen objects using the from_dict method
        for obj_data in data['screenObjects']:
            new_obj = TronViewScreenObject(shared.pygamescreen, obj_data['type'], obj_data['title'])
            new_obj.from_dict(obj_data)
            shared.CurrentScreen.ScreenObjects.append(new_obj)
        
        print(f"Screen loaded from {filename}")


        # update the last run config
        if update_settings_last_run:
            # if template then add template: to the filename
            if from_templates:
                just_filename = "template:" + just_filename
            hud_utils.writeConfig("Main", "screen", just_filename)

    except Exception as e:
        # get full error
        import traceback
        traceback.print_exc()
        print(f"Error loading screen from {filename}: {str(e)}")
