import sys
import ast
import os
import json
import argparse
from injector.ProgramProcessor import ProgramProcessor

'''
    {
        "type": "adli_metadata",
        "value": {
            "name": "ADLI",
            "description": "A tool to inject diagnostic logs into a python program.",
            "version": "0.0",
            "language": "python"
        
        }
    }
'''

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
        type=str,
        help="A path to a JSON file containing the systems information.",
        required=False
    )

    args_parser.add_argument(
        "-adlisysuid",
        type=str,
        help="A unique id representing the system this program belongs to.",
        required=False
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    source = parsed_args.source
    sys_info_path = parsed_args.sysinfo
    sysuid = parsed_args.adlisysuid

    try:
        open(source)
    except Exception as e:
        print(f"Invalid arguments: {str(e)}", file=sys.stderr)
        return -1
    
    # Load the system configuration from path if it was provided
    if (sys_info_path):
        try:
            with open(sys_info_path) as f:
                sysinfo = json.load(f)
                sysinfo["adliSystemExecutionId"] = sysuid
        except FileNotFoundError:
            print(f"System info file not found: {sys_info_path}", file=sys.stderr)
            return -1
        except json.JSONDecodeError:
            print(f"Invalid JSON in system info file: {sys_info_path}", file=sys.stderr)
            return -1
        except Exception as e:
            print(f"Error reading system info file: {str(e)}", file=sys.stderr)
            return -1
    else:
        sysinfo = None

    workingDirectory = os.path.dirname(os.path.abspath(__file__))
    processor = ProgramProcessor(source, workingDirectory, sysinfo)
    processor.run()

if "__main__" == __name__:
    sys.exit(main(sys.argv))
