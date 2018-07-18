#!/usr/bin/env python3

# Script to generate a CircleCI 2.0 .circleci/config.yml file
# Please see the README for more details

import os
from subprocess import run
from urllib.parse import urlencode

DEST_DIR = ".circleci"
DEST_FILE = "config.yml"
SRCE_FILE = "circle.yml"
TEST_BRANCH = "circleci-20-test"
URL_FMT = "https://circleci.com/api/v1.1/project/{}/{}/config-translation?{}"
VCS_DICT = {"bitbucket": "bb", "github": "gh"}

assert os.path.isfile(SRCE_FILE), "Local file {} not found".format(SRCE_FILE)
dest = os.path.join(DEST_DIR, DEST_FILE)
assert not os.path.isfile(dest), "Local file {} already exists".format(dest)


def run_command(cmd):
    return run(str(cmd).split(), capture_output=True, text=True).stdout


print("Gathering info, please wait...")
git_branches = run_command("git branch -a")
assert git_branches, "fatal: not a git repository (or any parent directories)"
assert TEST_BRANCH in git_branches, '{} git branch not found'.format(TEST_BRANCH)
git_origin = run_command("git remote -v").partition("origin")[-1]
assert git_origin, 'Unable to find a remote named "origin"'
vcs_provider, _, project = git_origin.partition("://")[-1].partition(".com/")
assert vcs_provider, 'Unable to determine vcs_provider for "git remote -v".'
msg = "CircleCI currently supports bitbucket and github only"
assert vcs_provider in VCS_DICT, msg
project = project.split(" ")[0]
fmt = "Attempting to create a CircleCI v2.0 file for {} on {}..."
print(fmt.format(project, vcs_provider))
cmd = "git ls-remote git@{}.com:{}.git {}".format(vcs_provider, project, TEST_BRANCH)
fmt = "{} branch already exists on remote - please delete it before continuing."
assert not run_command(cmd), fmt.format(TEST_BRANCH)
# https://circleci.com/api/v1.1/project/:vcs-type/:username/:project/config-translation
# ?circle-token="$circle_token"\&branch=circleci-20-test
query_data = {"branch": TEST_BRANCH, "circle-token": "<circle_token>"}
print(URL_FMT.format(vcs_provider, project, urlencode(query_data)))

circle_token = input("Paste your CircleCI API token here: ").strip()
assert len(circle_token) == 40, "Invalid CircleCI API token"
query_data["circle-token"] = circle_token
url = URL_FMT.format(vcs_provider, project, urlencode(query_data))
new_config = run_command('curl -X GET ' + url)
print(new_config)
try:
    os.mkdir(DEST_DIR)
except OSError:
    pass
with open(dest, "w"):
    write(new_config)
print(run_command("git add " + dest))
msg = "Adding auto-generated CircleCI 2.0 config file"
print(run("git", "commit", "-m", msg, capture_output=True, text=True).stdout)
print(run_command("git push origin " + TEST_BRANCH))

