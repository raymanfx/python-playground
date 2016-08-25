#!/usr/bin/env python

import re
import subprocess
import sys

glog_cmd = 'git log --full-history --no-merges --format="%h %ce %f -- %cd" --date=format:"%Y-%m-%d" | grep google.com'
glog_text = subprocess.check_output(glog_cmd, shell=True)
glog_lines = glog_text.split('\n')

for line in glog_lines:
  print(line)