import os
import importlib

def find_module(byName = None, debugOutput = False):
    # find all modules in the lib/modules folder recursively. look for all .py files.
    # for each file, look for a class that inherits from Module.
    # return a list of all modules found.
    # example: lib/modules/efis/trafficscope/trafficscope.py
    modules = []
    moduleNames = []
    for root, dirs, files in os.walk("lib/modules"):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                # get full path to the file
                path = os.path.join(root, file)
                # get the name after lib/modules but before the file name and remove slashes
                modulePath = path.split("lib/modules/")[1].split("/"+file)[0].replace("/",".")
                # import the file
                module = ".%s" % (file[:-3])
                mod = importlib.import_module(module, "lib.modules."+modulePath)  # dynamically load class
                ClassToload = file[:-3]  # get classname to load
                class_ = getattr(mod, ClassToload)
                newModuleClass = class_()
                # if the module has a hide attribute, and it is true, skip it.
                if hasattr(newModuleClass, "hide_from_add_menu"):
                    if newModuleClass.hide_from_add_menu:
                        continue
                if byName is not None:
                    #print("Looking for "+byName+" .. Checking module: %s (%s)" % (newModuleClass.name, path))
                    if newModuleClass.name == byName:
                        #print("Found module: %s (%s)" % (newModuleClass.name, path))
                        modules.append(newModuleClass)
                        moduleNames.append(newModuleClass.name)
                        return modules, moduleNames
                else: 
                    if debugOutput:
                        print("module: %s (%s)" % (newModuleClass.name, path))
                    modules.append(newModuleClass)
                    moduleNames.append(newModuleClass.name)

    # sort the modules by name
    modules.sort(key=lambda x: x.name)
    moduleNames.sort()

    #print("Found %d modules" % len(modules))
    #print(modules)
    return modules, moduleNames
