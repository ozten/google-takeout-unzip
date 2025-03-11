#!/usr/bin/env python3
"""
DeSmog Takeout Processor

This script processes Google Takeout zip files, unzips them to a target directory,
and moves processed files to a 'processed_takeout' directory.
It also monitors disk space to ensure there's enough space to continue processing.
"""

import argparse
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path

from config import MIN_FREE_SPACE_BYTES

# Set up logging
def setup_logging():
    """Configure logging to write to both console and files."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # File handlers
    output_handler = logging.FileHandler(logs_dir / "output.txt")
    output_handler.setLevel(logging.INFO)
    output_handler.setFormatter(console_format)
    
    error_handler = logging.FileHandler(logs_dir / "error.txt")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_format)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(output_handler)
    root_logger.addHandler(error_handler)
    
    return root_logger

def get_free_space(path):
    """Get free space in bytes for the filesystem containing path."""
    stat = os.statvfs(path)
    return stat.f_frsize * stat.f_bavail

def check_disk_space(path):
    """Check if there's enough disk space available."""
    free_space = get_free_space(path)
    logging.info(f"Free space: {free_space / (1024**3):.2f} GB")
    
    if free_space < MIN_FREE_SPACE_BYTES:
        logging.error(f"Low disk space! Only {free_space / (1024**3):.2f} GB available. "
                     f"Minimum required: {MIN_FREE_SPACE_BYTES / (1024**3):.2f} GB")
        return False
    return True

def process_zip_files(input_dir, target_dir, zip_prefix):
    """Process zip files matching the prefix."""
    input_path = Path(input_dir)
    target_path = Path(target_dir)
    processed_path = input_path.parent / "processed_takeout"
    
    # Create target and processed directories if they don't exist
    target_path.mkdir(exist_ok=True, parents=True)
    processed_path.mkdir(exist_ok=True)
    
    # Get all directories that contain the prefix
    matching_dirs = [d for d in input_path.iterdir() if d.is_dir() and zip_prefix in d.name]
    
    if not matching_dirs:
        logging.warning(f"No directories matching prefix '{zip_prefix}' found in {input_dir}")
        logging.info(f"Available items in directory: {[item.name for item in input_path.iterdir()]}")
        return
    
    logging.info(f"Found {len(matching_dirs)} directories matching prefix '{zip_prefix}'")
    
    # Process each matching directory
    for dir_path in matching_dirs:
        logging.info(f"Processing directory: {dir_path.name}")
        
        # Find zip files in this directory
        zip_files = sorted(dir_path.glob("*.zip"))
        
        if not zip_files:
            logging.warning(f"No zip files found in directory {dir_path.name}")
            continue
        
        logging.info(f"Found {len(zip_files)} zip files in {dir_path.name}")
        
        for zip_file in zip_files:
            logging.info(f"Processing {zip_file.name} from {dir_path.name}")
            
            # Check disk space before processing
            if not check_disk_space(target_path):
                logging.error("Exiting due to low disk space")
                sys.exit(1)
            
            try:
                # Extract the zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    logging.info(f"Extracting {zip_file.name} to {target_path}")
                    zip_ref.extractall(target_path)
                
                # Create a processed directory within the resource directory if it doesn't exist
                resource_processed_path = dir_path / "processed"
                resource_processed_path.mkdir(exist_ok=True)
                
                # Move the processed zip file to the resource's processed directory
                dest_file = resource_processed_path / zip_file.name
                logging.info(f"Moving {zip_file.name} to {resource_processed_path}")
                shutil.move(zip_file, dest_file)
                
            except zipfile.BadZipFile:
                logging.error(f"Error: {zip_file.name} is not a valid zip file")
            except Exception as e:
                logging.error(f"Error processing {zip_file.name}: {str(e)}")

def main():
    """Main function to parse arguments and process zip files."""
    parser = argparse.ArgumentParser(description="Process Google Takeout zip files")
    parser.add_argument("input_dir", help="Directory containing zip files")
    parser.add_argument("target_dir", help="Directory to extract files to")
    parser.add_argument("zip_prefix", help="Prefix of zip files to process")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("Starting DeSmog Takeout Processor")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Target directory: {args.target_dir}")
    logger.info(f"Zip file prefix: {args.zip_prefix}")
    
    # Check if input directory exists
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory {args.input_dir} does not exist")
        sys.exit(1)
    
    # Process zip files
    process_zip_files(args.input_dir, args.target_dir, args.zip_prefix)
    
    logger.info("Processing complete")

if __name__ == "__main__":
    main()
