"""Verify the actual Malbolge program and its command-line output."""
from pathlib import Path
import subprocess
import sys
import unittest

from mal import run

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    'h\u035b\u030c\u0328\u0349e\u0350\u031d\u0319'
    'l\u030c\u0325\u0317l\u0308\u0329o\u0304\u0305\u0308\u032d\u0328 '
    'w\u0350\u0302\u0357\u0323\u0318o\u0314\u034d'
    'r\u0301\u0321l\u030b\u0326d\u030f\u0306\u0318\u0331\n'
).encode('utf-8')


class OutputTests(unittest.TestCase):
    def test_program_emits_exact_utf8(self):
        self.assertEqual(run((ROOT / 'cursed_hello.mb').read_text('ascii')), EXPECTED)

    def test_cli_default_works_outside_repository(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'run_malbolge.py')],
            cwd=ROOT.parent, capture_output=True, check=True, timeout=30,
        )
        self.assertEqual(result.stdout, EXPECTED)
        self.assertEqual(result.stderr, b'')

    def test_cli_explicit_source(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'run_malbolge.py'), str(ROOT / 'cursed_hello.mb')],
            capture_output=True, check=True, timeout=30,
        )
        self.assertEqual(result.stdout, EXPECTED)


if __name__ == '__main__':
    unittest.main()
