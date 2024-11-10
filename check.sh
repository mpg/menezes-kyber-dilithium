#!/bin/sh

set -eu

pytest-3

# Don't just check, fix (despite this script's name)
black --target-version py310 *.py

pyflakes3 *.py

# C0111 = missing docstrings
# C0103 = snake_case naming style (forbids single-letter attibute names)
pylint --disable=C0103 $(ls *.py | grep -vF _test.py)
pylint --disable=C0111,C0103 *_test.py

# Leftovers from debugging
! grep '\<print(' *.py
