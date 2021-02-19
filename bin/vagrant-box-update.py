#!/usr/bin/env python3

# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

import sys
import types
import argparse
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

def parse_arguments():
    parser = argparse.ArgumentParser(description="Update and prune Vagrant boxes")
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        default=False,
        help="Batch mode (disables all interactive prompts)"
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Dry run mode (doesn't actually update anything, just echoes "
            "commands to be called)"
        )
    )
    return parser.parse_args()

def ask_for_confirmation(prompt, batch_mode, default):
    if batch_mode:
        print(prompt)
        print("Batch mode is on. Autoselecting default option ({})".format(
            {True: "yes", False: "no"}[default]
        ))
        confirmed = default
    else:
        confirmed = humanfriendly.prompts.prompt_for_confirmation(prompt, default=True)
    if not confirmed:
        sys.exit("Cancelled by user")


def main():
    boxes_to_update = []

    options = parse_arguments()

    for line in run_command("vagrant box outdated --global"):
        if "is outdated!" in line:
            # pylint: disable=line-too-long
            # We are looking for lines like this:
            # * 'ubuntu/xenial64' for 'virtualbox' is outdated! Current: 20200320.0.0. Latest: 20200415.0.0
            # pylint: enable=line-too-long
            tokens = line.split()
            box_name = tokens[1].replace("'", "")

            existing_box = next((i for i in boxes_to_update if i.name == box_name), None)
            if existing_box:
                existing_box.old_versions += [tokens[7].rstrip(".")]
            else:
                boxes_to_update += [
                    types.SimpleNamespace(
                        name=box_name,
                        old_versions=[tokens[7].rstrip(".")],
                        new_version=tokens[9]
                    )
                ]

    if len(boxes_to_update) == 0:
        print("All boxes are up to date. Exiting.")
        sys.exit(0)

    print(f"\nBoxes to update: {len(boxes_to_update)}")
    for box in boxes_to_update:
        print(f"  {box.name}: {';'.join(box.old_versions)} => {box.new_version}")
    ask_for_confirmation(
        prompt="Continue with update?", batch_mode=options.batch, default=True
    )

    for box in boxes_to_update:
        update_command = shlex.split(f"vagrant box update --box {box.name}")
        if options.dry_run:
            print("Dry-run mode is on. Skipping vagrant box update call")
            print(update_command)
        else:
            subprocess.check_call(update_command)

    print("\nThis will prune(remove) old versions of installed boxes, keeping ones still actively in use")
    ask_for_confirmation(
        prompt="Do you want to continue with pruning?", batch_mode=options.batch, default=True
    )

    print("Pruning old boxes")
    prune_command = shlex.split("vagrant box prune --force --keep-active-boxes")
    if options.dry_run:
        print("Dry-run mode is on. Skipping vagrant box update call")
        print(prune_command)
    else:
        subprocess.check_call(shlex.split("vagrant box prune --force --keep-active-boxes"))

if __name__ == '__main__':
    main()
