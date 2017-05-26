import collections
import getopt
import re
import subprocess
import sys


"""
Get the key for a given value from a dictionary.

args:
    dictionary: the dict with the keys and values
    val:        the value for which the key shall be retrieved

returns:
    The key as string
"""


def get_key_from_val(dictionary, val):

    return dictionary.keys()[dictionary.values().index(val)]


"""
Compare two git revisions against each other and list the differences in
commits.

args:
    local_path:      the path to the baseline repository
    local_revision:  the baseline revision
    remote_path:     the path to the remote repository
    remote_revision: the remote revision
    num_commits:     the number of commits that shall be compared
    compare_path:    the path that will be compared, "." means everything

returns:
    A dictionary containing the missing commits.
    Key   -> SHA checksum
    Value -> Commit description header (one line)
"""


def find_missing_commits(local_path, local_revision, remote_path,
                         remote_revision, num_commits, compare_path):

    # create a new dictionary we will write the missing keys and vals to
    missing_commits = {}
    missing_commits = collections.OrderedDict(missing_commits)

    # read shortened git commit metadata
    base_cmd = "git -C {} log -n {} --no-merges --oneline {} {}".format(
        local_path, num_commits, local_revision, compare_path)
    base_text = subprocess.check_output(base_cmd, shell=True)
    base_lines = base_text.split('\n')
    compare_cmd = "git -C {} log -n {} --no-merges --oneline {} {}".format(
        remote_path, num_commits, remote_revision, compare_path)
    compare_text = subprocess.check_output(compare_cmd, shell=True)
    compare_lines = compare_text.split('\n')

    # store metadata in ordered dicts
    base_commits = {}
    base_commits = collections.OrderedDict(base_commits)
    compare_commits = {}
    compare_commits = collections.OrderedDict(compare_commits)

    # fill dicts
    for line in base_lines:
        for i in range(0, len(line)):
            if line[i] == ' ':
                base_commits[line[:i]] = line[i+1:]
                break
    for line in compare_lines:
        for i in range(0, len(line)):
            if line[i] == ' ':
                compare_commits[line[:i]] = line[i+1:]
                break

    # compare commit hashes
    for commit_id in compare_commits.keys():
        if commit_id not in base_commits:
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
                # %B    -> raw message body
                # %n    -> newline
                base_body_cmd = ("git -C {} log -1"
                                 " --format='%an%n%ae%n%at%n%B' {}"
                                 .format(local_path, commit_id))
                base_body_text = subprocess.check_output(base_body_cmd,
                                                         shell=True)
                base_body_text = pattern.sub("", base_body_text)
                # remove trailing whitespace
                base_body_text = base_body_text.rstrip()
                compare_commit_id = get_key_from_val(
                    compare_commits, compare_commits[commit_id])
                compare_body_cmd = ("git -C {} log -1"
                                    " --format='%an%n%ae%n%at%n%B' {}"
                                    .format(remote_path, compare_commit_id))
                compare_body_text = subprocess.check_output(
                    compare_body_cmd, shell=True)
                compare_body_text = pattern.sub("", compare_body_text)
                # remove trailing whitespace
                compare_body_text = compare_body_text.rstrip()
                if base_body_text is not compare_body_text:
                    missing_commits[commit_id] = base_commits.get(commit_id)

    return missing_commits


"""
The entrypoint to the git history diff engine.
"""


def main():

    try:
        opts, args = getopt.getopt(sys.argv[2:], "np", ["num", "path"])
    except getopt.GetoptError as err:
        # print help information and exit
        print(str(err))
        # print_usage()
        sys.exit()

    if (len(sys.argv)) < 5:
        print("usage: python pydiff.py <local_dir> <local_branch>"
              " <remote_dir> <remote_revision>")
        sys.exit()

    local_path = sys.argv[-4]
    local_revision = sys.argv[-3]
    remote_path = sys.argv[-2]
    remote_revision = sys.argv[-1]

    compare_path = '.'
    num_commits = 1000

    for o, a in opts:
        if o in ("-n", "--num"):
            num_commits = int(a)
        elif o in ("-p", "--path"):
            compare_path = a
        else:
            print("[E] unhandled option: " + o)
            sys.exit()

    # Find differing commits
    local_only = find_missing_commits(
        remote_path, remote_revision, local_path, local_revision, num_commits,
        compare_path)
    remote_only = find_missing_commits(
        local_path, local_revision, remote_path, remote_revision, num_commits,
        compare_path)

    print("### {} ONLY ###".format(local_revision))
    for missing_id in local_only.keys():
        print("{} {}".format(missing_id, local_only.get(missing_id)))

    print('')

    print("### {} ONLY ###".format(remote_revision))
    for missing_id in remote_only.keys():
        print("{} {}".format(missing_id, remote_only.get(missing_id)))


if __name__ == "__main__":
    main()
