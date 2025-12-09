import os,json

def getSdgFile (sourceFile) :
    '''
    Returns the SDG JSON file if it exists.
    '''

    no_ext, _ = os.path.splitext(sourceFile)
    sdg_path = no_ext + "_sdg.json"

    try:
        with open(sdg_path, "r") as f:
            sdg = json.loads(f.read())
    except FileNotFoundError:
        print("Could not find SDG file for", sourceFile)
        sdg = None
    except json.JSONDecodeError:
        print("SDG file is not a valid JSON for", sourceFile)
        sdg = None

    return sdg


def getSdgMetaFile (sourceFile) :
    '''
    Returns the SDG JSON meta file if it exists.
    '''

    no_ext, _ = os.path.splitext(sourceFile)
    sdg_path = no_ext + "_meta.json"

    try:
        with open(sdg_path, "r") as f:
            sdg_meta = json.loads(f.read())
    except FileNotFoundError:
        print("Could not find SDG metadata file for", sourceFile)
        sdg_meta = None
    except json.JSONDecodeError:
        print("SDG metadata file is not a valid JSON for", sourceFile)
        sdg_meta = None

    return sdg_meta

def getAbsMapFile (sourceFile):
    '''
    Gets the abstraction map file if it exists and returns
    the abstraction map that was built.
    '''

    no_ext, _ = os.path.splitext(sourceFile)
    sdg_path = no_ext + "_abs_map.json"

    try:
        with open(sdg_path, "r") as f:
            absMap = json.loads(f.read())
            absMap = buildMap(absMap)    
    except FileNotFoundError:
        print("Could not find abstraction map file for", sourceFile)
        absMap = None
    except json.JSONDecodeError:
        print("Abstraction map file is not a valid JSON for", sourceFile)
        absMap = None

    return absMap

def buildMap(absMap):
    '''
    Build a map of abstraction ids to line numbers for each file.
    
    :param absMap: Mapping of abstractions to line that was provided by user.
    '''
    map = {}

    # Loop through each file
    for file in absMap["files"]:
        map[file["path"]] = {}
        fileMap = map[file["path"]]

        # Loop through each module in the file
        for moduleName in file["modules"]:
            module = file["modules"][moduleName]

            # Loop through each abstraction in the module
            for abs in module["abstractions"]:
                # Use the line delta to get the line number in the file
                line = abs["lineDelta"] + module["startLine"]
                fileMap[line] = abs["id"]

    return map

            
