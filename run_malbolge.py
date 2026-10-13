"""Run a Malbolge source file, preserving its raw UTF-8 output bytes."""
import argparse
from pathlib import Path
import sys
from mal import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'source', nargs='?', type=Path,
        default=Path(__file__).with_name('cursed_hello.mb'),
        help='Malbolge source file (default: bundled cursed_hello.mb)',
    )
    args = parser.parse_args()
    sys.stdout.buffer.write(run(args.source.read_text(encoding='ascii')))


if __name__ == '__main__':
    main()
