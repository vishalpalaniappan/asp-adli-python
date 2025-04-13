import sys
import os
import shutil
import argparse
import subprocess
import json
import uuid
from pathlib import Path

TEMP_DIRECTORY = "./temp"

def injectSystemLogs(sdf):
    '''
        Inject logs into the system.
    '''
    programs = sdf["programs"] 
    sdfPath = os.path.join(TEMP_DIRECTORY, "system_definition_file.json")

    uid = str(uuid.uuid4())

    for program in programs:
        print(f"Processing program: {program}")
        path = Path(TEMP_DIRECTORY) / program
        result = subprocess.run(['python3', 'adli.py', path, '-sysInfo', sdfPath, '-adliSysUid', uid ])

    print("Finished injecting logs into the system.")
    return 0

def validateSDF(sdfJsonStr):
    '''
        Given the contents of an SDF file, this function
        parses it into an object and validates that the
        necessary keys are present.
    '''
    sdf = json.loads(sdfJsonStr)

    if not isinstance(sdf, dict):
        raise Exception("SDF file is not a valid dictionary.")

    if not sdf.get("metadata"):
        raise Exception("SDF file is missing the metadata.")

    if not sdf["metadata"].get("name"):
        raise Exception("SDF metadata is missing the name property.")
    
    if not sdf["metadata"].get("description"):
        raise Exception("SDF metadata is missing the description property.")    
    
    if not sdf["metadata"].get("systemVersion"):
        raise Exception("SDF metadata is missing the systemVersion property.")
    
    if not sdf["metadata"].get("systemId"):
        raise Exception("SDF metadata is missing the systemId property.")
    
    return sdf

def cloneRepo(url):
    '''
        Clone the given repo and load/validate the system definition file.
    '''
    if os.path.exists(TEMP_DIRECTORY):
        shutil.rmtree(TEMP_DIRECTORY)
    os.makedirs(TEMP_DIRECTORY)
    
    subprocess.run(['git', 'clone', url, TEMP_DIRECTORY])

    # If sdf file exists, validate it and return it.
    sdfPath = os.path.join(TEMP_DIRECTORY, "system_definition_file.json")
    if os.path.exists(sdfPath):
        with open(os.path.join(TEMP_DIRECTORY, "system_definition_file.json")) as f:
            return validateSDF(f.read())
    else:
        return None
        
def cleanTempDirectory():
    '''
        Clear the temporary directory.
    '''
    if os.path.exists(TEMP_DIRECTORY):
        shutil.rmtree(TEMP_DIRECTORY)
    print("Cleared temporary directory.")

def main(argv):
    args_parser = argparse.ArgumentParser(
        description="This program injects diagnostic logs into all programs in the system given a repository URL." \
        "The repo must have a system definition file."
    )

    args_parser.add_argument(
        "repo_url",
        type=str,
        help="URL of the repository containing the system to inject logs into.",
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    url = parsed_args.repo_url

    sdf = cloneRepo(url)

    if (sdf):
        print("SDF file found in repository.")
        result = injectSystemLogs(sdf)
        cleanTempDirectory()
        return result        
    else:
        print("No system definition file was found")
        cleanTempDirectory()
        return -1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
