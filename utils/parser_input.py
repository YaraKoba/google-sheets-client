import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Website link checker script', exit_on_error=False)
    parser.add_argument('-iff', '--is_from_file', help='is_from_file', default=None, type=int)
    parser.add_argument('-t', '--tilda', help='time-tilda', default=None, type=int)
    parser.add_argument('-m', '--mode', help='mode may be "start" or "end"', default="start", type=str)
    parser.add_argument('-day', '--day_report', help='create total report', default=None, type=str)
    parser.add_argument('-a', '--aigul', help='0.5 or 1 Aigul', default=1, type=float)
    return None if not parser.parse_args() else parser.parse_args()


args = parse_arguments()
IS_FROM_FILE = None if not args else args.is_from_file
TILDA = None if not args else args.tilda
MODE = args.mode
DATE = args.day_report
AIGUL = args.aigul
