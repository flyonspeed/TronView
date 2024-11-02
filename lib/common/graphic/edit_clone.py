from lib.common.graphic.edit_TronViewScreenObject import TronViewScreenObject

def clone_screen_objects(selected_objects, mouse_x, mouse_y):
    if not selected_objects:
        return []

    cloned_objects = []
    reference_obj = selected_objects[0]
    offset_x = mouse_x - reference_obj.x
    offset_y = mouse_y - reference_obj.y

    for obj in selected_objects:
        new_obj = TronViewScreenObject(
            obj.pygamescreen,
            obj.type,
            obj.title + "_clone",
            module=None,
            x=obj.x + offset_x,
            y=obj.y + offset_y,
            width=obj.width,
            height=obj.height,
            id=None
        )
        
        new_obj.showBounds = obj.showBounds
        new_obj.showOptions = obj.showOptions
        
        if obj.type == 'group':
            new_obj.childScreenObjects = [clone_screen_object(child, offset_x, offset_y) for child in obj.childScreenObjects]
        else:
            if obj.module:
                new_module = type(obj.module)()
                for attr, value in vars(obj.module).items():
                    if not callable(value) and not attr.startswith("__"):
                        setattr(new_module, attr, value)
                new_obj.setModule(new_module)
                new_obj.showOptions = False
                new_obj.showEvents = False

        # reset the width and height to the original values.
        new_obj.resize(obj.width, obj.height)
        cloned_objects.append(new_obj)
    
    return cloned_objects

def clone_screen_object(obj, offset_x, offset_y):
    new_obj = TronViewScreenObject(
        obj.pygamescreen,
        obj.type,
        obj.title + "_clone",
        module=None,
        x=obj.x + offset_x,
        y=obj.y + offset_y,
        width=obj.width,
        height=obj.height,
        id=None
    )
    
    new_obj.showBounds = obj.showBounds
    new_obj.showOptions = obj.showOptions
    
    if obj.type == 'group':
        new_obj.childScreenObjects = [clone_screen_object(child, offset_x, offset_y) for child in obj.childScreenObjects]
    else:
        if obj.module:
            # new_module = type(obj.module)()
            # for attr, value in vars(obj.module).items():
            #     if not callable(value) and not attr.startswith("__"):
            #         setattr(new_module, attr, value)
            # new_obj.setModule(new_module, showOptions = obj.showOptions, width = obj.width, height = obj.height)
            new_obj.from_dict(obj.to_dict(), load_grid_position = False)
            new_obj.showOptions = False
            new_obj.showEvents = False
            new_obj.move(obj.x, obj.y)
    
    # reset the width and height to the original values.
    new_obj.resize(obj.width, obj.height)
    return new_obj

