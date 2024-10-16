#!/bin/sh

set -eu

pytest-3

black --target-version py310 --check *.py

pyflakes3 *.py

# C0111 = missing docstrings
# C0103 = snake_case naming style (forbids single-letter attibute names)
pylint --disable=C0111,C0103 *.py
