#!/usr/bin/env python3

# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

import sys
import types
import subprocess
import shlex
import humanfriendly.prompts


def run_command(command):
    result = []
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        universal_newlines=True
    )
    while True:
        output = process.stdout.readline().strip()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output)
            result += [output]
    rc = process.poll()
    if rc != 0:
        raise Exception(f"Command '{command}' returned non-zero exit status {rc}")
    return result

boxes_to_update = []


for line in run_command("vagrant box outdated --global"):
    if "is outdated!" in line:
        # pylint: disable=line-too-long
        # We are looking for lines like this:
        # * 'ubuntu/xenial64' for 'virtualbox' is outdated! Current: 20200320.0.0. Latest: 20200415.0.0
        # pylint: enable=line-too-long
        tokens = line.split()
        boxes_to_update += [
            types.SimpleNamespace(
                name=tokens[1].replace("'", ""),
                old_version=tokens[7],
                new_version=tokens[9]
            )
        ]

if len(boxes_to_update) == 0:
    sys.exit(0)

print(f"Boxes to update: {len(boxes_to_update)}")
for box in boxes_to_update:
    print(f"  {box.name}: {box.old_version} => {box.new_version}")
if not humanfriendly.prompts.prompt_for_confirmation("Continue with update?", default=True):
    sys.exit(0)

for box in boxes_to_update:
    subprocess.check_call(shlex.split(f"vagrant box update --box {box.name}"))

print("\nRemoving old version of installed boxes")
subprocess.check_call(shlex.split("vagrant box prune --force --keep-active-boxes"))
