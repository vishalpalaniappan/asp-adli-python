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
        sdg = {}
    except json.JSONDecodeError:
        print("SDG file is not a valid JSON for", sourceFile)
        sdg = {}

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
        sdg_meta = {}
    except json.JSONDecodeError:
        print("SDG metadata file is not a valid JSON for", sourceFile)
        sdg_meta = {}

    return sdg_meta

def getAbsMapFile (sourceFile):
    '''
    Returns the SDG JSON meta file if it exists.
    '''

    no_ext, _ = os.path.splitext(sourceFile)
    sdg_path = no_ext + "_abs_map.json"

    try:
        with open(sdg_path, "r") as f:
            abs_map = json.loads(f.read())
    except FileNotFoundError:
        print("Could not find SDG metadata file for", sourceFile)
        abs_map = {}
    except json.JSONDecodeError:
        print("SDG metadata file is not a valid JSON for", sourceFile)
        abs_map = {}

    return abs_map    