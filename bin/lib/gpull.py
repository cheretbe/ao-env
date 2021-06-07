#!/usr/bin/env python3

import sys
import subprocess

def main():
    if subprocess.check_output(["git", "status", "--porcelain"]) == b"":
        if subprocess.check_output(["git", "diff", "@{u}"]) == b"":
            subprocess.check_call(["git", "pull"])
            subprocess.check_call(["git", "status"])
        else:
            sys.exit("Will not pull as local Git repo has unpushed commits")
    else:
        sys.exit("Will not pull as local Git repo has uncommitted changes")

if __name__ == "__main__":
    main()
