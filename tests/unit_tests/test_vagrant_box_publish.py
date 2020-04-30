"""Unit tests for ../../bin/vagrant_box_publish.py"""
import unittest
import os
import sys


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
                Exception,
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

        new_version = vagrant_box_publish.inc_version_release(
            new_base_version="3.4.6",
            current_version="3.4.5_3",
            separator="_"
        )
        self.assertEqual(new_version, "3.4.6_0")