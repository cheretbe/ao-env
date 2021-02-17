"""Unit tests for ../../bin/vagrant_box_publish.py"""
import unittest
import os
import sys
import freezegun


sys.path.append(os.path.dirname(__file__) + "/../../bin")
# pylint: disable=wrong-import-position,import-error
import vagrant_box_publish
# pylint: enable=wrong-import-position,import-error

class TestIncVersion(unittest.TestCase):
    """Unit tests for inc_version_release procedure"""
    def test_same_base_version(self):
        """It should increment release if supplied base version is the same"""
        new_version = vagrant_box_publish.inc_version_release(
            new_base_version="20200229",
            current_version="20200229.0",
            separator="."
        )
        self.assertEqual(new_version, "20200229.1")

    def test_greater_base_version(self):
        """It should set release to 0 if supplied base version is greater"""
        new_version = vagrant_box_publish.inc_version_release(
            new_base_version="20200301",
            current_version="20200229.0",
            separator="."
        )
        self.assertEqual(new_version, "20200301.0")

    def test_lower_base_version(self):
        """It should throw an exception if supplied base version is lower"""
        with self.assertRaisesRegex(
                SystemExit,
                "Version to be released \\(20200228\\) is lower than currently "
                "released \\(20200229\\)"
        ):
            vagrant_box_publish.inc_version_release(
                new_base_version="20200228",
                current_version="20200229.0",
                separator="."
            )

    def test_different_version_separators(self):
        """It should handle different version separators"""
        new_version = vagrant_box_publish.inc_version_release(
            new_base_version="3.4.5",
            current_version="3.4.5-2",
            separator="-"
        )
        self.assertEqual(new_version, "3.4.5-3")

@freezegun.freeze_time("2014-05-15")
def test_get_box_name_and_version():
    """Tests for get_box_name_and_version function"""

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="boxes/routeros_6.48.1.box", explicit_name="", explicit_version=""
    )
    assert box_name == "routeros"
    assert box_ver == "6.48.1"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="routeros_6.48.1.box", explicit_name="", explicit_version=""
    )
    assert box_name == "routeros"
    assert box_ver == "6.48.1"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="nametest.box", explicit_name="", explicit_version=""
    )
    assert box_name == "nametest"
    assert box_ver == "20140515"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="nametest_2.1-0.box", explicit_name="", explicit_version=""
    )
    assert box_name == "nametest"
    assert box_ver == "2.1-0"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="nametest_2.1-0.box", explicit_name="override", explicit_version=""
    )
    assert box_name == "override"
    assert box_ver == "2.1-0"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="nametest_2.1-0.box", explicit_name="", explicit_version="ver"
    )
    assert box_name == "nametest"
    assert box_ver == "ver"

    box_name, box_ver = vagrant_box_publish.get_box_name_and_version(
        box_file="nametest_2.1-0.box", explicit_name="override", explicit_version="ver"
    )
    assert box_name == "override"
    assert box_ver == "ver"
