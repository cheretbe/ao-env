#!/usr/bin/env python3

#pylint: disable=missing-module-docstring,missing-function-docstring


import os
import subprocess


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    vagrant_env_path = os.path.join(os.path.realpath(script_path), "vagrant", "docker-tests")

    print(f"Running tests in Vagrant environment '{vagrant_env_path}'")

    vm_needs_creation = False
    for line in subprocess.check_output(
            ["vagrant", "status", "--machine-readable"],
            cwd=vagrant_env_path,
            universal_newlines=True
    ).splitlines():
        status_values = line.split(",")
        if (status_values[2] == "state") and (status_values[3] == "not_created"):
            vm_needs_creation = True

    if vm_needs_creation:
        subprocess.check_call(["vagrant", "up"], cwd=vagrant_env_path)

    try:
        subprocess.check_call(
            ["vagrant", "ssh", "--", "cd /ao-env/tests && inv test"],
            cwd=vagrant_env_path
        )
    finally:
        if vm_needs_creation:
            subprocess.check_call(["vagrant", "destroy", "-f"], cwd=vagrant_env_path)

if __name__ == "__main__":
    main()
