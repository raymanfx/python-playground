#!/usr/bin/env python

import re
import subprocess
import sys

if len(sys.argv) != 2:
  print("usage: python gylog.py <revision>")
  sys.exit()

glog_cmd = 'git log {} --full-history --no-merges --format="%h  %cd  %ce  %f" --date=format:"%Y-%m-%d" | grep google.com'.format(sys.argv[1])
glog_text = subprocess.check_output(glog_cmd, shell=True)
glog_lines = glog_text.split('\n')

for line in glog_lines:
  print(line)
