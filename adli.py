import sys
import argparse
from injector import processFile

def main(argv):
    args_parser = argparse.ArgumentParser(
        description="Injects diagnostic logs into a program."
    )

    args_parser.add_argument(
        "source",
        type=str,
        help="Path to source file"
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    source = parsed_args.source

    try:
        open(source)
    except Exception as e:
        print(f"Invalid arguments: {str(e)}", file=sys.stderr)
        return -1

    processFile(source)

if "__main__" == __name__:
    sys.exit(main(sys.argv))
