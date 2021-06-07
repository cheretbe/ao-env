#!/usr/bin/env python3

import os
import sys
import argparse
import pathlib
import subprocess

sys.path.append(os.path.dirname(__file__))
import common

def print_verbose(msg, verbose=False):
    if verbose:
        print(msg)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ca_path", nargs="?", default=os.getcwd(),
        help="Path to offline CA directory (default is current working directory)"
    )
    parser.add_argument(
        "-b", "--batch-mode", action="store_true", default=False,
        help="Batch mode"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Increase output verbosity"
    )

    options, unknown = parser.parse_known_args() #pylint: disable=unused-variable
    return options

def main():
    options = parse_arguments()
    print_verbose(f"Offline CA path: {options.ca_path}", options.verbose)

    root_ca_cert = pathlib.Path(options.ca_path) / "root_ca/root_ca.crt"
    root_ca_key = pathlib.Path(options.ca_path) / "root_ca/root_ca.key"

    # print(common.get_openssl_executable())
    # subprocess.check_call([common.get_openssl_executable(), "version"])
    # return

    if not os.path.isfile(root_ca_key):
        print(f"Root CA key file [{root_ca_key}] is missing")
        common.ask_for_confirmation(
            "Would you like to create it now?",
            batch_mode=options.batch_mode, default=False
        )
        root_ca_key.parent.mkdir(mode=0o775, parents=True, exist_ok=True)
        subprocess.check_call([
            common.get_openssl_executable(),
            "genrsa", "-aes256", "-out", root_ca_key, "4096"
        ])

if __name__ == "__main__":
    main()
