import sys
import json
import argparse
import subprocess

def run(systemid, adli_system_paths):
    print(systemid, adli_system_paths)

    for path in adli_system_paths["programs"]:
        subprocess.run(["python3", "adli.py", path, "-sysid", systemid])
    

def main(argv):

    args_parser = argparse.ArgumentParser(
        description="Injects diagnostic logs into multiple programs with the same system id."
    )

    args_parser.add_argument(
        "adli_system_paths",
        type=str,
        help="Path to system configuration file which contains paths to the programs."
    )

    args_parser.add_argument(
        "systemid",
        type=str,
        help="System ID"
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    adli_system_paths = parsed_args.adli_system_paths
    systemid = parsed_args.systemid

    with open(adli_system_paths) as f:
        adli_system_paths = json.load(f)

    run(systemid, adli_system_paths)


if "__main__" == __name__:
    sys.exit(main(sys.argv))
