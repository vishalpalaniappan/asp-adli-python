import sys
import argparse

def cloneRepo(url):
    '''
        Clone the given repo and load the system definition file.
    '''

def main(argv):

    args_parser = argparse.ArgumentParser(
        description="This program injects diagnostic logs into all programs in the system given a repository URL." \
        "The repo must have a system definition file."
    )

    args_parser.add_argument(
        "repo_url",
        type=str,
        help="URL of the repository containing the system to inject logs into."
    )
    
    parsed_args = args_parser.parse_args(argv[1:])
    url = parsed_args.repo_url

    cloneRepo(url)

    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
