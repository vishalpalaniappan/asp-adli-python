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
        help="A JSON object that has been dumped into a string containing system relevant information.",
        required=False
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    source = parsed_args.source
    sysinfo = parsed_args.sysinfo

    try:
        open(source)
    except Exception as e:
        print(f"Invalid arguments: {str(e)}", file=sys.stderr)
        return -1

    if (sysinfo):
        try:
            sysinfo = json.loads(sysinfo)
        except Exception as e:
            print(f"Invalid JSON string in sysinfo: {str(e)}", file=sys.stderr)
            return -1

    workingDirectory = os.path.dirname(os.path.abspath(__file__))
    processor = ProgramProcessor(source, workingDirectory, sysinfo)
    processor.run()

if "__main__" == __name__:
    sys.exit(main(sys.argv))
