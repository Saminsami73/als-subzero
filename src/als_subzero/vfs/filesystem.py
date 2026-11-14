"""
ALS SubZero Virtual Filesystem (VFS) and Inode Management.
Developed by Samin Sami.

Provides a hierarchical POSIX-compatible directory tree, inode mapping,
and file metadata resolution.
"""

from __future__ import annotations

import os
import posixpath
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

CHUNK_SIZE = 1024


@dataclass
class Inode:
    inode_id: int
    name: str
    is_directory: bool
    mode: int
    parent_id: int
    size: int = 0
    # List of chunk indices for regular files
    chunk_indices: List[int] = field(default_factory=list)
    # Mapping: child name -> inode_id (for directories)
    children: Dict[str, int] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)


class VirtualFileSystem:
    """
    In-memory Inode Hierarchy.
    Maintains file structure, directory trees, and chunk index mappings.
    Storage payloads exist solely in the network delay line.
    """

    def __init__(self, default_k: int = 4, default_m: int = 2) -> None:
        self.default_k = default_k
        self.default_m = default_m
        self._next_inode_id = 1
        self._inodes: Dict[int, Inode] = {}

        # Initialize root directory "/"
        root = Inode(
            inode_id=self._alloc_inode_id(),
            name="",
            is_directory=True,
            mode=0o755,
            parent_id=1,
        )
        self._inodes[root.inode_id] = root

    def _alloc_inode_id(self) -> int:
        iid = self._next_inode_id
        self._next_inode_id += 1
        return iid

    def normalize_path(self, path: str) -> str:
        """Clean and normalize POSIX path."""
        p = posixpath.normpath(path.strip())
        if not p.startswith("/"):
            p = "/" + p
        return p

    def lookup(self, path: str) -> Optional[Inode]:
        """Traverse directory tree to find an inode by path."""
        norm = self.normalize_path(path)
        if norm == "/":
            return self._inodes[1]

        parts = [p for p in norm.split("/") if p]
        curr = self._inodes[1]

        for part in parts:
            if not curr.is_directory:
                return None
            if part not in curr.children:
                return None
            child_id = curr.children[part]
            curr = self._inodes[child_id]

        return curr

    def mkdir(self, path: str, mode: int = 0o755) -> Inode:
        """Create a new directory."""
        norm = self.normalize_path(path)
        if norm == "/":
            raise FileExistsError("Root directory already exists")

        parent_path, name = posixpath.split(norm)
        parent = self.lookup(parent_path)
        if not parent:
            raise FileNotFoundError(f"Parent directory not found: {parent_path}")
        if not parent.is_directory:
            raise NotADirectoryError(f"Parent is not a directory: {parent_path}")
        if name in parent.children:
            raise FileExistsError(f"Directory already exists: {norm}")

        new_inode = Inode(
            inode_id=self._alloc_inode_id(),
            name=name,
            is_directory=True,
            mode=mode,
            parent_id=parent.inode_id,
        )
        self._inodes[new_inode.inode_id] = new_inode
        parent.children[name] = new_inode.inode_id
        parent.modified_at = time.time()
        return new_inode

    def create_file(self, path: str, mode: int = 0o644) -> Inode:
        """Create an empty regular file inode."""
        norm = self.normalize_path(path)
        parent_path, name = posixpath.split(norm)
        parent = self.lookup(parent_path)
        if not parent:
            raise FileNotFoundError(f"Parent directory not found: {parent_path}")
        if not parent.is_directory:
            raise NotADirectoryError(f"Parent is not a directory: {parent_path}")
        if name in parent.children:
            existing = self._inodes[parent.children[name]]
            if existing.is_directory:
                raise IsADirectoryError(f"Target is an existing directory: {norm}")
            return existing

        new_inode = Inode(
            inode_id=self._alloc_inode_id(),
            name=name,
            is_directory=False,
            mode=mode,
            parent_id=parent.inode_id,
        )
        self._inodes[new_inode.inode_id] = new_inode
        parent.children[name] = new_inode.inode_id
        parent.modified_at = time.time()
        return new_inode

    def unlink(self, path: str) -> Inode:
        """Remove a file or directory inode."""
        norm = self.normalize_path(path)
        if norm == "/":
            raise PermissionError("Cannot remove root directory")

        parent_path, name = posixpath.split(norm)
        parent = self.lookup(parent_path)
        if not parent:
            raise FileNotFoundError(f"Parent directory not found: {parent_path}")

        if name not in parent.children:
            raise FileNotFoundError(f"Entry not found: {norm}")

        target_id = parent.children[name]
        target = self._inodes[target_id]

        if target.is_directory and target.children:
            raise OSError(f"Directory not empty: {norm}")

        del parent.children[name]
        del self._inodes[target_id]
        parent.modified_at = time.time()
        return target

    def rename(self, old_path: str, new_path: str) -> None:
        """Rename or move an inode."""
        old_norm = self.normalize_path(old_path)
        new_norm = self.normalize_path(new_path)
        if old_norm == "/" or new_norm == "/":
            raise PermissionError("Cannot rename root directory")

        target = self.lookup(old_norm)
        if not target:
            raise FileNotFoundError(f"Source not found: {old_norm}")

        old_parent_path, old_name = posixpath.split(old_norm)
        new_parent_path, new_name = posixpath.split(new_norm)

        old_parent = self.lookup(old_parent_path)
        new_parent = self.lookup(new_parent_path)
        if not old_parent or not new_parent:
            raise FileNotFoundError("Parent directory not found")
        if not new_parent.is_directory:
            raise NotADirectoryError("Destination parent is not a directory")

        # Detach from old parent
        del old_parent.children[old_name]
        # Attach to new parent
        target.name = new_name
        target.parent_id = new_parent.inode_id
        new_parent.children[new_name] = target.inode_id
        target.modified_at = time.time()

    def readdir(self, path: str) -> List[Inode]:
        """List directory contents."""
        node = self.lookup(path)
        if not node:
            raise FileNotFoundError(f"Path not found: {path}")
        if not node.is_directory:
            raise NotADirectoryError(f"Not a directory: {path}")

        return [self._inodes[child_id] for child_id in node.children.values()]

    def tree_str(self, path: str = "/") -> str:
        """Generate a visual directory tree."""
        root_node = self.lookup(path)
        if not root_node:
            return f"Path not found: {path}"

        lines = [f"{path if path != '/' else '/'}"]

        def _traverse(node: Inode, prefix: str) -> None:
            entries = sorted(node.children.items(), key=lambda x: x[0])
            for i, (name, child_id) in enumerate(entries):
                is_last = i == len(entries) - 1
                child = self._inodes[child_id]
                connector = "└── " if is_last else "├── "
                suffix = "/" if child.is_directory else f" ({child.size} bytes)"
                lines.append(f"{prefix}{connector}{name}{suffix}")
                if child.is_directory:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    _traverse(child, new_prefix)

        if root_node.is_directory:
            _traverse(root_node, "")
        return "\n".join(lines)

