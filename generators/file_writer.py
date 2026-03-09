"""
File Writer module.

Writes generated sales data batches to JSON text files
inside the configured DATA_DIR directory.
Each branch gets its own timestamped JSON file per cycle.
"""

# json: built-in module for reading/writing JSON format
import json

# os: provides operating system functions (path operations, directory creation)
import os

# datetime: used to generate timestamps for file names
from datetime import datetime

# Import the DATA_DIR path from our central configuration
from config.settings import DATA_DIR


class FileWriter:
    """Writes generated sales data to JSON files on disk."""

    def __init__(self, output_dir: str = DATA_DIR):
        """
        Initialize the FileWriter with an output directory.

        Args:
            output_dir: Path where JSON files will be saved (defaults to DATA_DIR)
        """
        # Store the output directory path
        self.output_dir = output_dir

        # Create the output directory if it doesn't exist yet
        # exist_ok=True means no error if directory already exists
        os.makedirs(self.output_dir, exist_ok=True)

    def write_batch(self, branch: str, records: list[dict]) -> str:
        """
        Write a list of record dicts to a single JSON file.

        File naming convention: {branch}_{YYYYMMDD_HHMMSS}.json
        Example: Branch_A_20260309_143000.json

        Args:
            branch: The branch name (used in the filename)
            records: List of sales record dictionaries to write

        Returns:
            The absolute path of the written file.
        """
        # Generate a timestamp string for the filename (e.g. "20260309_143000")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build the filename: e.g. "Branch_A_20260309_143000.json"
        filename = f"{branch}_{timestamp}.json"

        # Combine the output directory with the filename to get the full path
        filepath = os.path.join(self.output_dir, filename)

        # Open the file for writing with UTF-8 encoding
        with open(filepath, "w", encoding="utf-8") as f:
            # Serialize the records list to JSON format
            # indent=2: pretty-print with 2-space indentation
            # ensure_ascii=False: allow non-ASCII characters (e.g. Arabic names)
            json.dump(records, f, indent=2, ensure_ascii=False)

        # Return the full file path so callers know where the file was saved
        return filepath

    def write_all_branches(self, branch_data: dict[str, list[dict]]) -> list[str]:
        """
        Write data for every branch to separate JSON files.

        Args:
            branch_data: dict mapping branch name → list of record dicts
                         Example: {"Branch_A": [{...}, {...}], "Branch_B": [...]}

        Returns:
            List of file paths that were written.
        """
        # Collect all written file paths in a list
        paths = []

        # Iterate over each branch and its records
        for branch, records in branch_data.items():
            # Write this branch's records to a JSON file
            path = self.write_batch(branch, records)
            # Add the file path to our list
            paths.append(path)

        return paths
