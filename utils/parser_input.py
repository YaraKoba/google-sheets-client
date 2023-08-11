import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Website link checker script', exit_on_error=False)
    parser.add_argument('-iff', '--is_from_file', help='is_from_file', default=None, type=int)
    parser.add_argument('-t', '--tilda', help='time-tilda', default=None, type=int)
    return None if not parser.parse_args() else parser.parse_args()


args = parse_arguments()
IS_FROM_FILE = None if not args else args.is_from_file
TILDA = None if not args else args.tilda
