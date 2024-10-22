import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)

args = parser.parse_args()

n = 0
for line in args.infile:
    if not (line.startswith("(") or line.startswith("O") or line.startswith("%") or not line.strip()):
        n += 1
        print(f"N{n:03}", line.strip())
    else:
        print(line.strip())
