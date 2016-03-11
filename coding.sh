#!/bin/sh
flake8 `find . -name '*.py'` | more
