# DeSmog Takeout Processor

A Python utility for processing Google Takeout zip files on macOS.

## Overview

This script helps you process large Google Takeout archives by:
1. Finding zip files with a specific prefix in an input directory
2. Extracting them to a target directory
3. Moving processed files to a separate directory
4. Monitoring disk space to prevent running out of space

## Requirements

- Python 3.6 or higher
- macOS (though it should work on other UNIX-like systems)

## Usage

```bash
python takeout_processor.py INPUT_DIRECTORY TARGET_DIRECTORY ZIP_PREFIX
```

### Arguments

- `INPUT_DIRECTORY`: Directory containing Google Takeout zip files
- `TARGET_DIRECTORY`: Directory where files will be extracted
- `ZIP_PREFIX`: Prefix of zip files to process (e.g., "Resource")

### Example

```bash
python takeout_processor.py /Volumes/RAINBOW/takeout_files /Volumes/RAINBOW/extracted_takeout Resource
```

## Configuration

You can modify the `config.py` file to change settings:
- `MIN_FREE_SPACE_GB`: Minimum free space required to continue processing (default: 50GB)

## Logs

The script creates a `logs` directory with two log files:
- `output.txt`: Contains all informational logs
- `error.txt`: Contains only error logs

## How It Works

1. The script scans the input directory for zip files matching the specified prefix
2. Files are sorted alphanumerically
3. Each file is extracted to the target directory
4. Processed files are moved to a `processed_takeout` directory next to the input directory
5. Before each extraction, disk space is checked to ensure at least 50GB is available
