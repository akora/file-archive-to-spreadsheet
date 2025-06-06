# Directory Cleanup and Inventory Tool

This script cleans up system-generated and hidden files while creating a detailed inventory of remaining files in CSV format.

## Features

- Automatically removes hidden files and macOS system files
- Tracks and reports space freed from cleanup
- Creates inventory of remaining files after cleanup
- Generates two CSV files compatible with Google Sheets
- Uses human-readable file sizes
- Processes directories and files in alphabetical order

## Cleanup Features

The script automatically removes:

- Hidden files (starting with a dot)
- macOS system files (.DS_Store, .localized, etc.)
- macOS resource fork files (starting with ._)
- Time Machine and Spotlight related files
- Other common system files (Thumbs.db, etc.)

This ensures your directories are clean of system-generated metadata files while maintaining an inventory of your actual content.

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Open `directory_cleanup_and_inventory.py` and configure the directories:

```python
# Configuration
ROOT_DIRECTORY = "/path/to/clean"  # Directory to clean and inventory
OUTPUT_DIRECTORY = "/path/to/save/csv"  # Directory where CSV will be saved
```

1. Run the script:

```bash
python directory_cleanup_and_inventory.py
```

The script will:

1. Scan the specified directory and its subdirectories
2. Remove hidden and system files
3. Generate two CSV inventory files:
   - A complete file inventory
   - A directory structure inventory
4. Display a summary of:
   - Total files processed
   - Number of files cleaned up
   - Amount of space freed
   - Number of remaining files inventoried
   - Number of directories inventoried
   - Location of both CSV files

The CSV filenames are automatically generated using:

- The name of the scanned directory (normalized to be filename-safe)
- A prefix indicating the type ("inventory_files" or "inventory_dirs")
- A timestamp to ensure uniqueness

## CSV Output Formats

### Files Inventory CSV

Contains detailed information about each file:

- relative_path: Path relative to the root directory
- filename: Name of the file
- size: Human-readable file size
- raw_size: File size in bytes
- modified: Last modification date and time
- directory: Directory containing the file

### Directory Structure CSV

Contains information about the directory hierarchy:

- directory_path: Full path relative to the root directory
- depth: Directory depth level (0 for root)
- parent_directory: Path of the parent directory
- directory_name: Name of the directory
