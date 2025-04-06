import sys
import ast
import os
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
        "-sysid",
        "--sysid",
        type=str,
        help="A unique id to identify the system this program belongs to",
        required=False
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    source = parsed_args.source
    sysid = parsed_args.sysid

    try:
        open(source)
    except Exception as e:
        print(f"Invalid arguments: {str(e)}", file=sys.stderr)
        return -1

    workingDirectory = os.path.dirname(os.path.abspath(__file__))
    processor = ProgramProcessor(source, workingDirectory, sysid)
    processor.run()

if "__main__" == __name__:
    sys.exit(main(sys.argv))
