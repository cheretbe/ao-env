"""Batch mode tests"""

import sys
import os
import types
import pathlib
import contextlib
import pytest
import freezegun

sys.path.append(os.path.dirname(__file__) + "/../../bin")
# pylint: disable=wrong-import-position,import-error
import vagrant_box_publish
# pylint: enable=wrong-import-position,import-error

@contextlib.contextmanager
def temporary_cwd(temp_cwd):
    current_dir = os.getcwd()
    try:
        os.chdir(temp_cwd)
        yield
    finally:
        os.chdir(current_dir)

def assert_script_error(error_msg):
    with pytest.raises(SystemExit) as exception_info:
        vagrant_box_publish.main()
    assert str(exception_info.value) == error_msg

def mock_script_params(mocker_obj, **kwargs):
    # Default parameter values
    script_params = {
        "batch": True,
        "box_file": "",
        "box_name": "",
        "box_ver": "",
        "version_separator": ".",
        "dry_run": False
    }
    # Update defaults with explicitly set values
    script_params.update(kwargs)
    mocker_obj.patch(
        "vagrant_box_publish.parse_arguments",
        return_value=types.SimpleNamespace(**script_params)
    )

def mock_vagrant_cloud_functions(mocker_obj, requests_mock_obj=None, existing_box_ver=None):
    mocker_obj.patch(
        "vagrant_box_publish.check_vagrant_cloud_login",
        return_value="test-user-name"
    )
    if requests_mock_obj is not None:
        if existing_box_ver is None:
            return_json = {"errors": ["Resource not found!"], "success": False}
        else:
            return_json = {"current_version": {"version": existing_box_ver}}
        requests_mock_obj.get(
            "https://app.vagrantup.com/api/v1/box/test-user-name/test-file",
            json=return_json
        )
    return mocker_obj.patch(
        "vagrant_box_publish.publish_box",
        return_value="test-user-name"
    )


def test_no_files(tmpdir, mocker):
    """Should fail if there are no *.box files and --box-file option is not present"""

    mock_script_params(mocker_obj=mocker, batch=True)
    # mock_vagrant_cloud_functions(mocker_obj=mocker)

    with temporary_cwd(tmpdir):
        assert_script_error(
            error_msg="Can't find any *.box files in current directory and subdirectories"
        )

def test_no_files_box_option_does_not_exist(tmpdir, mocker):
    """Should fail if --box-file option is present, but the file doesn't exist"""

    mock_script_params(mocker_obj=mocker, batch=True, box_file="missing-file.box")
    # mock_vagrant_cloud_functions(mocker_obj=mocker)

    with temporary_cwd(tmpdir):
        assert_script_error(
            error_msg="File doesn't exist: missing-file.box"
        )


def test_no_files_box_option(tmpdir, mocker, requests_mock):
    """Should try to publish the box if --box-file option is present"""

    mock_script_params(mocker_obj=mocker, batch=True, box_file="test-file.box")
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver=None
    )

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file.box").touch()
        assert_script_error(
            error_msg=(
                "'box_description.md' is missing. Will not create a new box without "
                "a description in batch mode"
            )
        )

    assert not publish_mock.called

@freezegun.freeze_time("2014-03-31")
def test_no_files_plus_box_option_new_box(tmpdir, mocker, requests_mock):
    """Should publish a new box if --box-file option is present and there is a description"""

    mock_script_params(mocker_obj=mocker, batch=True, box_file="subdir/test-file.box")
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver=None
    )

    with temporary_cwd(tmpdir):
        os.mkdir("subdir")
        pathlib.Path("subdir/test-file.box").touch()
        with open("box_description.md", "w") as desc_f:
            desc_f.write("Box **description** test\n")
        vagrant_box_publish.main()

    # print(publish_mock.call_args)
    publish_mock.assert_called_once_with(
        box_description='Box **description** test',
        box_file='subdir/test-file.box',
        box_name='test-file', box_version='20140331.0',
        cloud_user_name='test-user-name',
        version_description="**31.03.2014 update**",
        dry_run_mode=False
    )

@freezegun.freeze_time("2012-01-14")
def test_single_file(tmpdir, mocker, requests_mock):
    """Should auto-select a single box file"""

    mock_script_params(mocker_obj=mocker, batch=True)
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver="20110101.0"
    )

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file.box").touch()
        vagrant_box_publish.main()

    # print(publish_mock.call_args)
    publish_mock.assert_called_once_with(
        box_description='',
        box_file='test-file.box',
        box_name='test-file', box_version='20120114.0',
        cloud_user_name='test-user-name',
        version_description="**14.01.2012 update**",
        dry_run_mode=False
    )

def test_multiple_files(tmpdir, mocker):
    """Should fail if there is more than one box file"""

    mock_script_params(mocker_obj=mocker, batch=True)

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file-1.box").touch()
        pathlib.Path("test-file-2.box").touch()
        assert_script_error(
            error_msg=(
                "More than one box file has been found. Will not display "
                "selection dialog in batch mode"
            )
        )

@freezegun.freeze_time("2014-05-15")
def test_auto_generated_lower_version(tmpdir, mocker, requests_mock):
    """Should fail if auto-generated version is lower than currently released"""

    mock_script_params(mocker_obj=mocker, batch=True)
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver="20150101.0"
    )

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file.box").touch()
        assert_script_error(
            error_msg=(
                "Version to be released (20140515) is lower than currently "
                "released (20150101)"
            )
        )

    assert not publish_mock.called

def test_explicit_lower_version(tmpdir, mocker, requests_mock):
    """Should fail if explicitly specified version is lower than currently released"""

    mock_script_params(
        mocker_obj=mocker, batch=True, box_ver="2.3.1", version_separator="-"
    )
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver="2.3.2-0"
    )

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file.box").touch()
        assert_script_error(
            error_msg=(
                "Version to be released (2.3.1) is lower than currently "
                "released (2.3.2)"
            )
        )

    assert not publish_mock.called

def test_version_description(tmpdir, mocker, requests_mock):
    """Should use a version description file"""

    mock_script_params(mocker_obj=mocker, batch=True, box_ver="20110101")
    publish_mock = mock_vagrant_cloud_functions(
        mocker_obj=mocker,
        requests_mock_obj=requests_mock,
        existing_box_ver="20110101.0"
    )

    with temporary_cwd(tmpdir):
        pathlib.Path("test-file.box").touch()
        with open("test-file.md", "w") as desc_f:
            desc_f.write("Version description **test**\n")
        vagrant_box_publish.main()

    # print(publish_mock.call_args)
    publish_mock.assert_called_once_with(
        box_description='',
        box_file='test-file.box',
        box_name='test-file', box_version='20110101.1',
        cloud_user_name='test-user-name',
        version_description="Version description **test**",
        dry_run_mode=False
    )
