"""Batch mode tests"""

import pathlib
import subprocess

publish_script_path = pathlib.Path(__file__).resolve().parents[2] / "bin" / "vagrant_box_publish.py"

def assert_script_error(cwd, script_params, error_msg):
    completed_proc = subprocess.run( # pylint: disable=subprocess-run-check
        [publish_script_path] + script_params,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    assert completed_proc.returncode == 1
    assert completed_proc.stderr.decode("utf-8").splitlines()[0] == error_msg


def test_no_files(tmpdir):
    """Should fail if there are no *.box files and --box-file option is not present"""
    assert_script_error(
        cwd=tmpdir,
        script_params=["--batch", "--dry-run"],
        error_msg="Can't find any *.box files in current directory and subdirectories"
    )

def test_no_files_plus_box_option(tmpdir):
    """Should try to publish the box if --box-file option is present"""
    assert_script_error(
        cwd=tmpdir,
        script_params=["--batch", "--box-file", "missing-file.box", "--dry-run"],
        error_msg=(
            "'box_description.md' is missing. Will not create a new box without "
            "a description in batch mode"
        )
    )
