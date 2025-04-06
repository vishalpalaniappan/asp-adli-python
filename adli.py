import sys
import ast
import os
import json
import argparse
from injector.ProgramProcessor import ProgramProcessor

def verify_python_compatibility():
    if not hasattr(ast, 'unparse'):
        raise RuntimeError("This program requires Python 3.9+ (ast.unparse not available)")

def main(argv):
    verify_python_compatibility()

    args_parser = argparse.ArgumentParser(
        description="Injects diagnostic logs into a program."
    )

    args_parser.add_argument(
        "source",
        type=str,
        help="Path to source file"
    )

    args_parser.add_argument(
        "-sysinfo",
        "--sysinfo",
        type=str,
        help="A path to a JSON file containing the systems information.",
        required=False
    )

    args_parser.add_argument(
        "-uniqueid",
        "--uniqueid",
        type=str,
        help="A unique id representing this execution of the adli tool",
        required=False
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    source = parsed_args.source
    sys_info_path = parsed_args.sysinfo
    uniqueid = parsed_args.uniqueid

    try:
        open(source)
    except Exception as e:
        print(f"Invalid arguments: {str(e)}", file=sys.stderr)
        return -1
    
    # Load the system configuration from path if it was provided
    if (sys_info_path):
        with open(sys_info_path) as f:
            sysinfo = json.load(f) 
    else:
        sysinfo = None

    workingDirectory = os.path.dirname(os.path.abspath(__file__))
    processor = ProgramProcessor(source, workingDirectory, uniqueid, sysinfo)
    processor.run()

if "__main__" == __name__:
    sys.exit(main(sys.argv))
