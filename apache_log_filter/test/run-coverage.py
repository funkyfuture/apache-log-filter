#!/usr/bin/env python3

from glob import glob
import os
from subprocess import call, STDOUT
from webbrowser import open_new_tab

wd = os.path.dirname(__file__)

call(['coverage', 'erase'], cwd=wd, stderr=STDOUT)
tests = glob(os.path.join(wd, 'test_*.py'))
for test in tests:
	call(['coverage', 'run', '-a', test], cwd=wd)
call(['coverage', 'html'], cwd=wd)
open_new_tab(os.path.join('htmlcov', 'index.html'))
