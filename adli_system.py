import sys
import json
import argparse
import subprocess
import uuid

def run(sys_def_file_path):
    '''
        This program parses the system definition file and 
        injects logs into every program in the system.
    '''

    # Load the system definition file using the given path
    with open(sys_def_file_path) as f:
        sys_def_file = json.load(f)

    '''
    Create a unique instance id that is passed to every program in the system.
    The system definition file contains systemId and systemVersion which allow us
    to identify the system. This unique id will be used to identify every deployment
    of the system.
    '''
    instance_uid = str(uuid.uuid4())
    for path in sys_def_file["programs"]:
        subprocess.run(
            [
                "python3",
                "adli.py",
                path,
                "-sysinfo",
                sys_def_file_path,
                "-uid",
                instance_uid
            ]
        )
    

def main(argv):

    args_parser = argparse.ArgumentParser(
        description="Injects diagnostic logs into multiple programs with the same system id."
    )

    args_parser.add_argument(
        "adli_system_paths",
        type=str,
        help="Path to the system definition file."
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    sys_def_file_path = parsed_args.adli_system_paths

    run(sys_def_file_path)


if "__main__" == __name__:
    sys.exit(main(sys.argv))
