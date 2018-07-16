#!/usr/bin/env python3

import os
import sys
import subprocess
import apt
import shutil

required_os_packages = ("mc", "htop", "colordiff", "ncdu", "zsh",
    "python3-colorama")

def append_line_to_file(file_name, line_to_append):
    with open(file_name, "r+") as file:
        for line in file:
            if line_to_append in line:
               break
        else:
            # Not found, we at the EOF
            print("Adding '{}' to '{}'".format(line_to_append, file_name))
            file.write("\n" + line_to_append + "\n")

def create_link(target, link):
    needs_creation = True
    if os.path.isdir(link):
        if os.readlink(link) == target:
            needs_creation = False
        else:
            os.remove(link)
    if needs_creation:
        print("Creating symlink '{}' ==> '{}'".format(link, target))
        os.symlink(target, link)

apt_cache = apt.cache.Cache()
packages_to_install = []
for package in required_os_packages:
    if not apt_cache[package].is_installed:
        packages_to_install += [package]

if len(packages_to_install) != 0:
    package_install_cmd = "sudo apt install {} -y".format(" ".join(packages_to_install))
    print("Not all required OS packages are installed")
    print("Do you want to install them with the following command?\n")
    print(package_install_cmd)

    if input("\nRun the command? [y/N] ").lower() == 'y':
        subprocess.check_call(package_install_cmd, shell=True)
    else:
        print("Cancelled")
        sys.exit(1)

ao_env_root = os.path.dirname(os.path.realpath(__file__))

append_line_to_file(os.path.expanduser("~/.bashrc"), "#source " + os.path.join(ao_env_root, "ao-env_zshrc"))

if not os.path.isfile(os.path.expanduser("~/.zshrc")):
    print("Copying '/etc/zsh/newuser.zshrc.recommended' ==> '{}'".format(os.path.expanduser("~/.zshrc")))
    shutil.copyfile("/etc/zsh/newuser.zshrc.recommended", os.path.expanduser("~/.zshrc"))
append_line_to_file(os.path.expanduser("~/.zshrc"), "source " + os.path.join(ao_env_root, "ao-env_zshrc"))

os.makedirs(os.path.expanduser("~/.local/share/fonts"), exist_ok=True)
create_link(os.path.join(ao_env_root, "fonts"), os.path.expanduser("~/.local/share/fonts/ao-env"))

os.makedirs(os.path.expanduser("~/.config/sublime-text-3/Packages"), exist_ok=True)
create_link(os.path.join(ao_env_root, "settings", "sublime-text-3"), os.path.expanduser("~/.config/sublime-text-3/Packages/User"))