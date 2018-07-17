#!/usr/bin/env python3

# Script to generate a CircleCI 2.0 .circleci/config.yml file
# Please see the README for more details

import os
from subprocess import run

import requests  # python3 -m pip install --upgrade requests

DEST_DIR = ".circleci"
DEST_FILE = "config.yml"
SRCE_FILE = "circle.yml"
TEST_BRANCH = "circleci-20-test"
URL_FMT = "https://circleci.com/api/v1.1/project/{}/{}/config-translation"
VCS_DICT = {"bitbucket": "bb", "github": "gh"}

assert os.path.isfile(SRCE_FILE), "Local file {} not found".format(SRCE_FILE)
dest = os.path.join(DEST_DIR, DEST_FILE)
assert not os.path.isfile(dest), "Local file {} already exists".format(dest)


def run_command(cmd):
    return run(str(cmd).split(), capture_output=True, text=True).stdout


print("Gathering info, please wait...")
git_branches = run_command("git branch -a")
assert git_branches, "fatal: not a git repository (or any parent directories)"
# assert TEST_BRANCH in git_branches, '{} git branch not found'.format(TEST_BRANCH)
git_origin = run_command("git remote -v").partition("origin")[-1]
assert git_origin, 'Unable to find a remote named "origin"'
vcs_provider, _, project = git_origin.partition("://")[-1].partition(".com/")
assert vcs_provider, 'Unable to determine vcs_provider for "git remote -v".'
msg = "CircleCI currently supports bitbucket and github only"
assert vcs_provider in VCS_DICT, msg
project = project.split(" ")[0]
fmt = "Attempting to create a CircleCI v2.0 file for {} on {}..."
print(fmt.format(vcs_provider, project))
cmd = "git ls-remote git@{}.com:{}.git {}".format(vcs_provider, project, TEST_BRANCH)
fmt = "{} branch already exists on remote - please delete it before continuing."
assert not run_command(cmd), fmt.format(TEST_BRANCH)
url = URL_FMT.format(vcs_provider, project)
print("url: {}".format(url))

circle_token = input("Paste your CircleCI API token here: ").strip()
assert len(circle_token) == 40, "Invalid CircleCI API token"

# https://circleci.com/api/v1.1/project/:vcs-type/:username/:project/tree/:branch
# ?circle-token="$circle_token"\&branch=circleci-20-test

print(requests.get(url, data={"circle-token": circle_token, "branch": TEST_BRANCH}))
