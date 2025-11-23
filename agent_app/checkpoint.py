"""
Checkpoint and rollback system for Hades.

Provides file-level snapshot and restoration capabilities to enable
safe rollback of multi-file agent operations. Checkpoints are stored
in .apex/checkpoints/<checkpoint_id>/ and can be restored atomically.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .types import ChangeManifest


class CheckpointManager:
    """Manages checkpoint creation and restoration for safe rollback."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.checkpoint_dir = root / ".apex" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(self, files: Sequence[Path], description: str = "") -> str:
        """
        Create a snapshot of the specified files.

        Args:
            files: Paths to back up (relative or absolute)
            description: Human-readable checkpoint description

        Returns:
            Checkpoint ID (timestamp-based)
        """
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_path.mkdir(parents=True, exist_ok=True)

        # Write metadata
        metadata_path = checkpoint_path / "metadata.txt"
        file_list = []

        with metadata_path.open("w", encoding="utf-8") as f:
            f.write(f"Checkpoint ID: {checkpoint_id}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Root: {self.root}\n")
            f.write("\nFiles:\n")

            for file_path in files:
                # Resolve to absolute path
                if not file_path.is_absolute():
                    file_path = self.root / file_path

                # Skip if file doesn't exist (e.g., it's about to be created)
                if not file_path.exists():
                    continue

                # Calculate relative path for storage
                try:
                    rel_path = file_path.relative_to(self.root)
                except ValueError:
                    # File is outside project root, skip
                    continue

                # Create backup with preserved directory structure
                backup_file = checkpoint_path / rel_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)

                file_list.append(str(rel_path))
                f.write(f"  - {rel_path}\n")

        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> list[Path]:
        """
        Restore files from a checkpoint.

        Args:
            checkpoint_id: ID returned from create_checkpoint

        Returns:
            List of restored file paths

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")

        restored_files = []

        # Restore all files in the checkpoint
        for backup_file in checkpoint_path.rglob("*"):
            if backup_file.name == "metadata.txt":
                continue
            if not backup_file.is_file():
                continue

            # Calculate relative path and target location
            rel_path = backup_file.relative_to(checkpoint_path)
            target_file = self.root / rel_path

            # Restore the file
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target_file)
            restored_files.append(target_file)

        return restored_files

    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Remove a checkpoint from disk."""
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        if checkpoint_path.exists():
            shutil.rmtree(checkpoint_path)

    def list_checkpoints(self) -> list[tuple[str, str]]:
        """
        List all available checkpoints.

        Returns:
            List of (checkpoint_id, description) tuples
        """
        checkpoints = []
        for checkpoint_path in sorted(self.checkpoint_dir.iterdir()):
            if not checkpoint_path.is_dir():
                continue

            metadata_path = checkpoint_path / "metadata.txt"
            description = ""
            if metadata_path.exists():
                with metadata_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("Description:"):
                            description = line.split(":", 1)[1].strip()
                            break

            checkpoints.append((checkpoint_path.name, description))

        return checkpoints

    def create_from_manifest(self, manifest: ChangeManifest) -> str:
        """
        Create a checkpoint for all files in a ChangeManifest.

        Args:
            manifest: Change manifest to checkpoint

        Returns:
            Checkpoint ID
        """
        files_to_backup = []
        for change in manifest.files:
            files_to_backup.append(change.path)
            if change.old_path:  # Handle renames
                files_to_backup.append(change.old_path)

        checkpoint_id = self.create_checkpoint(
            files_to_backup, description=manifest.summary or "ChangeManifest checkpoint"
        )

        # Update manifest with checkpoint reference
        manifest.checkpoint_id = checkpoint_id

        return checkpoint_id

    def cleanup_old_checkpoints(self, keep_count: int = 10) -> int:
        """
        Remove old checkpoints, keeping only the most recent ones.

        Args:
            keep_count: Number of checkpoints to retain

        Returns:
            Number of checkpoints deleted
        """
        checkpoints = sorted(self.checkpoint_dir.iterdir(), reverse=True)
        deleted = 0

        for checkpoint_path in checkpoints[keep_count:]:
            if checkpoint_path.is_dir():
                shutil.rmtree(checkpoint_path)
                deleted += 1

        return deleted
