"""
Unit tests for Virtual Filesystem and Inode management.
ALS SubZero - Developed by Samin Sami.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.vfs.filesystem import VirtualFileSystem


class TestVFS(unittest.TestCase):
    def setUp(self):
        self.vfs = VirtualFileSystem()

    def test_root_lookup(self):
        root = self.vfs.lookup("/")
        self.assertIsNotNone(root)
        self.assertEqual(root.inode_id, 1)
        self.assertTrue(root.is_directory)

    def test_mkdir_and_hierarchy(self):
        dir_node = self.vfs.mkdir("/var")
        self.assertEqual(dir_node.name, "var")
        self.assertTrue(dir_node.is_directory)

        sub_node = self.vfs.mkdir("/var/log")
        self.assertEqual(sub_node.name, "log")

        found = self.vfs.lookup("/var/log")
        self.assertEqual(found.inode_id, sub_node.inode_id)

    def test_file_create_and_readdir(self):
        self.vfs.mkdir("/etc")
        file_node = self.vfs.create_file("/etc/config.json")
        self.assertFalse(file_node.is_directory)

        entries = self.vfs.readdir("/etc")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "config.json")

    def test_unlink_file(self):
        self.vfs.create_file("/temp.txt")
        self.assertIsNotNone(self.vfs.lookup("/temp.txt"))
        self.vfs.unlink("/temp.txt")
        self.assertIsNone(self.vfs.lookup("/temp.txt"))

    def test_rename(self):
        self.vfs.create_file("/original.txt")
        self.vfs.rename("/original.txt", "/renamed.txt")
        self.assertIsNone(self.vfs.lookup("/original.txt"))
        self.assertIsNotNone(self.vfs.lookup("/renamed.txt"))

    def test_tree_string(self):
        self.vfs.mkdir("/src")
        self.vfs.create_file("/src/main.py")
        tree_out = self.vfs.tree_str("/")
        self.assertIn("src/", tree_out)
        self.assertIn("main.py", tree_out)


if __name__ == "__main__":
    unittest.main()
