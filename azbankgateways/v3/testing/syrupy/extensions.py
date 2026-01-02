from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from syrupy.data import Snapshot, SnapshotCollection
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.extensions.single_file import SingleFileSnapshotExtension


if TYPE_CHECKING:
    from syrupy.location import PyTestLocation
    from syrupy.types import SnapshotIndex


class NestedDirectoryJSONSnapshotExtension(JSONSnapshotExtension):
    """
    A JSON snapshot extension that organizes snapshots in nested directories.

    Structure: __snapshots__/<TestClass>/<test_method>/<param_id>/<index>.json
    When you have more than one snapshot assertion in the same test,
    Syrupy uses an auto‑incrementing index as the snapshot’s name unless you provide a custom name.

    Example:
        test_send[200_success] with index 0 -> __snapshots__/test_send/200_success/0.json
    """

    SNAPSHOT_NAME_SEPARATOR = "::"

    @classmethod
    def get_snapshot_name(cls, *, test_location: PyTestLocation, index: SnapshotIndex = 0) -> str:
        parts = [
            *cls._get_test_directory(test_location=test_location).parts,
            cls._get_file_basename(index=index),
        ]
        return cls.SNAPSHOT_NAME_SEPARATOR.join(parts)

    @classmethod
    def get_location(cls, *, test_location: PyTestLocation, index: SnapshotIndex) -> str:
        path = (
            Path(cls.dirname(test_location=test_location))
            / cls._get_test_directory(test_location=test_location)
            / cls._get_file_basename(index=index)
        )
        return f"{path}.{cls.file_extension}"

    def read_snapshot_collection(self, *, snapshot_location: str) -> SnapshotCollection:
        snapshot_name = self._extract_snapshot_name(snapshot_location)
        snapshot_collection = SnapshotCollection(location=snapshot_location)
        snapshot_collection.add(Snapshot(snapshot_name))
        return snapshot_collection

    def _extract_snapshot_name(self, snapshot_location: str) -> str:
        """Extract snapshot name from file path."""
        path = Path(snapshot_location)
        # Get parts after __snapshots__ directory
        try:
            snapshot_dir_index = path.parts.index(self.snapshot_dirname)
        except ValueError:
            return path.stem
        relevant_parts = path.parts[snapshot_dir_index + 2 :]
        if not relevant_parts:
            return path.stem
        *dirs, last = relevant_parts
        last_stem = Path(last).stem
        snapshot_name_parts = [*dirs, last_stem]
        return self.SNAPSHOT_NAME_SEPARATOR.join(snapshot_name_parts)

    @classmethod
    def _get_test_directory(cls, *, test_location: PyTestLocation) -> Path:
        """Build the directory path for a test's snapshots."""
        parts: list[str] = []

        # Add class names if test is inside a class
        if test_location.classname:
            parts.extend(test_location.classname.split(cls.SNAPSHOT_NAME_SEPARATOR))

        # Add test method name
        parts.append(test_location.methodname)

        # Add parametrized id if present
        if callspec := getattr(test_location.item, "callspec", None):
            parts.append(callspec.id)

        return Path(*(cls._clean_filename(p) for p in parts))

    @classmethod
    def _get_file_basename(cls, *, index: SnapshotIndex) -> str:
        """Get the base filename for a snapshot."""
        return cls._clean_filename(str(index))

    @classmethod
    def _clean_filename(cls, filename: str) -> str:
        """Clean a string to be used as a filename."""
        return SingleFileSnapshotExtension._SingleFileSnapshotExtension__clean_filename(filename)
