"""
File Writer module.

Writes generated sales data batches to JSON text files
inside the configured DATA_DIR directory.
"""

import json
import os
from datetime import datetime

from config.settings import DATA_DIR


class FileWriter:
    """Writes generated sales data to JSON files on disk."""

    def __init__(self, output_dir: str = DATA_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def write_batch(self, branch: str, records: list[dict]) -> str:
        """
        Write a list of record dicts to a JSON file.

        File naming convention: {branch}_{YYYYMMDD_HHMMSS}.json

        Returns:
            The absolute path of the written file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{branch}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        return filepath

    def write_all_branches(self, branch_data: dict[str, list[dict]]) -> list[str]:
        """
        Write data for every branch to separate JSON files.

        Args:
            branch_data: dict mapping branch name → list of records

        Returns:
            List of file paths that were written.
        """
        paths = []
        for branch, records in branch_data.items():
            path = self.write_batch(branch, records)
            paths.append(path)
        return paths
