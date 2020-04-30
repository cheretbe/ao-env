#!/usr/bin/env python3

# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

import sys
import argparse
import datetime
import subprocess
import packaging
import requests
import PyInquirer

def inc_version_release(new_base_version, current_version, separator):
    current_base_version, current_subversion = current_version.split(separator)
    if current_base_version == new_base_version:
        new_version = current_base_version + separator + str(int(current_subversion) + 1)
    elif packaging.version.parse(new_base_version) > packaging.version.parse(current_version):
        new_version = new_base_version + separator + "0"
    else:
        raise Exception(
            f"Version to be released ({new_base_version}) is lower than currently "
            f"released ({current_base_version})"
        )
    return new_version

def main():
    box_names = ["docker-ce", "dummy"]

    parser = argparse.ArgumentParser(description="Publish boxes to Vagrant Cloud")
    parser.add_argument(
        "box_ver",
        nargs="?",
        default="",
        help="Box base version (optional, yyyymmdd will be used by default, where yyyy "
             "is current year, mm is current month, dd is current day)"
    )
    parser.add_argument(
        "-s", "--version-separator",
        default=".",
        help="Separator. A character, that separates box base version from a box "
             "release (default: '.')"
    )

    options = parser.parse_args()
    if options.box_ver == "":
        options.box_ver = datetime.datetime.now().strftime("%Y%m%d")
        print(f"Box version is not specified. Using {options.box_ver}")

    print("Checking Vagrant Cloud login...")

    # if subprocess.call(
    #         "vagrant cloud auth login --check",
    #         shell=True,
    #         stdin=subprocess.DEVNULL,
    #         stdout=subprocess.DEVNULL
    # ) != 0:
    #     print("You are not currently logged in.")
    #     print("Please provide your login information to authenticate.")
    #     subprocess.check_call("vagrant cloud auth login", shell=True)

    # cloud_user_name = ""
    # for line in subprocess.check_output(
    #         "vagrant cloud auth whoami",
    #         shell=True,
    #         universal_newlines=True
    # ).splitlines():
    #     print(line)
    #     if "Currently logged in as" in line:
    #         cloud_user_name = line.split(" ")[-1]

    # if not cloud_user_name:
    #     raise Exception("Could not detect current Vagrant Cloud user name")
    cloud_user_name = "dummy"

    answers = PyInquirer.prompt(
        questions=[
            {
                'type': 'list',
                'name': 'box',
                'message': 'Select a box to publish',
                'choices': box_names
            }
        ]
    )
    if not answers:
        sys.exit(1)
    box_name = answers["box"]

    print(f"'{cloud_user_name}/{box_name}' is selected")

    response = requests.get(
        f"https://app.vagrantup.com/api/v1/box/{cloud_user_name}/{box_name}"
    ).json()
    if response.get("current_version", ""):
        current_version = response["current_version"]["version"]
        print(f"Currently released version of '{cloud_user_name}/{box_name}': {current_version}")
        new_version = inc_version_release(
            new_base_version=options.box_ver,
            current_version=current_version,
            separator=options.version_separator
        )
    else:
        print(f"There is no currently released version of '{cloud_user_name}/{box_name}'")
        new_version = options.box_ver + options.version_separator + "0"

    print(new_version)

    # if not ask_for_confirmation("Do you want to release version '{}' of the box?".format(new_version)):
    #     sys.exit(1)


if __name__ == '__main__':
    main()