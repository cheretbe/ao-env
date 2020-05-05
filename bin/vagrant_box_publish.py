#!/usr/bin/env python3

# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

import sys
import argparse
import datetime
import pathlib
import subprocess
import packaging
import requests
import PyInquirer


def ask_for_confirmation(prompt):
    conf_questions = [
        {
            "type": "confirm",
            "name": "continue",
            "message": prompt,
            "default": True
        }
    ]
    conf_answers = PyInquirer.prompt(conf_questions)
    return bool(conf_answers) and conf_answers["continue"]


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


def select_box_file():
    box_files = sorted(pathlib.Path().rglob("*.box"))
    if len(box_files) == 0:
        raise Exception(
            "Can't find any *.box files in current directory and subdirectories"
        )
    if len(box_files) == 1:
        return box_files[0]
    answers = PyInquirer.prompt(
        questions=[
            {
                'type': 'list',
                'name': 'boxfile',
                'message': 'Select a box file to publish',
                'choices': [str(i) for i in box_files]
            }
        ]
    )
    if not answers:
        sys.exit(1)
    return answers["boxfile"]


def main():
    box_data = [
        {
            "name": "docker-tests",
            "description": "Ubuntu 18.04 with Docker CE and testing tools installed"
        },
        {
            "name": "dummy",
            "description": "Temporary box for upload testing"
        }
    ]

    parser = argparse.ArgumentParser(description="Publish boxes to Vagrant Cloud")
    parser.add_argument(
        "box_ver",
        nargs="?",
        default="",
        help="Box base version (optional, yyyymmdd will be used by default, where yyyy "
             "is current year, mm is current month, dd is current day)"
    )
    parser.add_argument(
        "-f", "--box-file",
        default="",
        help="Path to a box file to publish"
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

    if options.box_file == "":
        options.box_file = select_box_file()
    print(f"Box file name: {options.box_file}")

    print("Checking Vagrant Cloud login...")

    if subprocess.call(
            "vagrant cloud auth login --check",
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
    ) != 0:
        print("You are not currently logged in.")
        print("Please provide your login information to authenticate.")
        subprocess.check_call("vagrant cloud auth login", shell=True)

    cloud_user_name = ""
    for line in subprocess.check_output(
            "vagrant cloud auth whoami",
            shell=True,
            universal_newlines=True
    ).splitlines():
        print(line)
        if "Currently logged in as" in line:
            cloud_user_name = line.split(" ")[-1]

    if not cloud_user_name:
        raise Exception("Could not detect current Vagrant Cloud user name")

    answers = PyInquirer.prompt(
        questions=[
            {
                'type': 'list',
                'name': 'box',
                'message': 'Select a name to publish a box under',
                'choices': [i["name"] for i in box_data]
            }
        ]
    )
    if not answers:
        sys.exit(1)
    box_name = answers["box"]
    box_description = next(i for i in box_data if i["name"] == box_name)["description"]

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

    if not ask_for_confirmation(
            f"Do you want to release '{options.box_file}' as '{cloud_user_name}/{box_name}' "
            f"version {new_version}?"
    ):
        sys.exit("Cancelled by user")

    answers = PyInquirer.prompt(
        questions=[
            {
                "type": "editor",
                "name": "description",
                "message": "Please enter a version description (Alt+Enter to finish)",
                "default": box_description
            }
        ]
    )
    if not answers:
        sys.exit(1)
    version_description = answers["description"]

    print(f"Publishing '{options.box_file}' as '{cloud_user_name}/{box_name}'version {new_version}")
    subprocess.check_call(
        f"vagrant cloud publish '{cloud_user_name}/{box_name}' "
        f"{new_version} virtualbox {options.box_file} "
        f"--short-description '{box_description}' "
        f"--version-description '{version_description}' "
        "--release --force",
        shell=True
    )


if __name__ == '__main__':
    main()
