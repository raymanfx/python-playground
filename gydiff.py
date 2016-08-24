#!/usr/bin/env python

import collections
import re
import subprocess
import sys

def get_key_from_val(dictionary, val):
  return dictionary.keys()[dictionary.values().index(val)]

def find_missing_commits(base_path, base_revision, compare_path, compare_revision):
  ADVANCED_COMPARISON = True
  # create a new dictionary we will write the missing keys and vals to
  missing_commits = {}
  missing_commits = collections.OrderedDict(missing_commits)
  # read shortened git commit metadata
  base_cmd = "git -C {} log --full-history --no-merges --pretty=oneline {}".format(base_path, base_revision)
  base_text = subprocess.check_output(base_cmd, shell=True)
  base_lines = base_text.split('\n')
  compare_cmd = "git -C {} log --full-history --no-merges --pretty=oneline {}".format(compare_path, compare_revision)
  compare_text = subprocess.check_output(compare_cmd, shell=True)
  compare_lines = compare_text.split('\n')
  # store metadata in ordered dicts
  base_commits = {}
  base_commits = collections.OrderedDict(base_commits)
  compare_commits = {}
  compare_commits = collections.OrderedDict(compare_commits)

  # fill dicts
  for line in base_lines:
    for i in range (0, len(line)):
      if line[i] == ' ':
        base_commits[line[:i]] = line[i+1:]
        break
  for line in compare_lines:
    for i in range (0, len(line)):
      if line[i] == ' ':
        compare_commits[line[:i]] = line[i+1:]
        break

  # compare commit hashes
  for commit_id in compare_commits.keys():
    if not base_commits.has_key(commit_id):
      if not ADVANCED_COMPARISON:
        missing_commits[commit_id] = base_commits.get(commit_id)
      else:
        # check the msg header first
        if not compare_commits[commit_id] in base_commits.viewvalues():
          missing_commits[commit_id] = compare_commits.get(commit_id)
        else:
          # regex pattern to remove change-id from body
          pattern = re.compile(r"Change-Id: \w+")
          # now check the full commit msg
          # %an -> author name
          # %ae -> author email
          # %at -> UNIX timestamp
          # %B  -> raw message body
          # %n  -> newline
          base_body_cmd = 'git -C {} log -1 --format="%an%n%ae%n%at%n%B" {}'.format(base_path, commit_id)
          base_body_text = subprocess.check_output(base_body_cmd, shell=True)
          base_body_text = pattern.sub("", base_body_text)
          # remove trailing whitespace
          base_body_text = base_body_text.rstrip()
          compare_commit_id = get_key_from_val(compare_commits,compare_commits[commit_id])
          compare_body_cmd = 'git -C {} log -1 --format="%an%n%ae%n%at%n%B" {}'.format(compare_path, compare_commit_id)
          compare_body_text = subprocess.check_output(compare_body_cmd, shell=True)
          compare_body_text = pattern.sub("", compare_body_text)
          # remove trailing whitespace
          compare_body_text = compare_body_text.rstrip()
          #compare_body_text = pattern.sub("", "\n")
          if not base_body_text == compare_body_text:
            missing_commits[commit_id] = base_commits.get(commit_id)
  return missing_commits


def main():
  local_path = sys.argv[1]
  local_revision = sys.argv[2]
  remote_path = sys.argv[3]
  remote_revision = sys.argv[4]

  # Find differing commits
  local_only = find_missing_commits(remote_path, remote_revision, local_path, local_revision)
  remote_only = find_missing_commits(local_path, local_revision, remote_path, remote_revision)

  print("### {} ONLY ###".format(local_revision))
  for missing_id in local_only.keys():
    print("{} {}".format(missing_id, local_only.get(missing_id)));

  print('')

  print("### {} ONLY ###".format(remote_revision))
  for missing_id in remote_only.keys():
    print("{} {}".format(missing_id, remote_only.get(missing_id)));

if (len(sys.argv)) != 5:
  print("usage: python pydiff.py <local_dir> <local_branch>"
        " <remote_dir> <remote_revision>")
  sys.exit()

if __name__ == "__main__": main()
