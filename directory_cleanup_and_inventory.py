import os
import csv
from datetime import datetime
import humanize
import re
from pathlib import Path
from tqdm import tqdm

# Configuration
ROOT_DIRECTORY = "/path/to/scan"  # Directory to scan
OUTPUT_DIRECTORY = "/path/to/output"  # Directory where CSV will be saved

# Files to clean up (macOS specific and general hidden files)
CLEANUP_FILES = {
    '.DS_Store',
    '.localized',
    '.AppleDouble',
    '.LSOverride',
    'Thumbs.db',
    '.com.apple.timemachine.supported',
    '.DocumentRevisions-V100',
    '.Spotlight-V100',
    '.TemporaryItems',
    '.Trashes',
    '.VolumeIcon.icns',
    '.fseventsd',
    '.apdisk'
}

class FileStats:
    def __init__(self):
        self.total_files = 0
        self.cleaned_files = 0
        self.cleaned_size = 0
        self.errors = []

def should_clean_file(filename, filepath):
    """
    Check if the file should be cleaned up.
    Returns True for hidden files and macOS system files.
    """
    # Match files that start with a dot (hidden files)
    if filename.startswith('.'):
        return True
        
    # Match files in the cleanup list
    if filename in CLEANUP_FILES:
        return True
        
    # Match macOS resource fork files
    if filename.startswith('._'):
        return True
        
    # Match .AppleDouble directories and their contents
    if '.AppleDouble' in filepath:
        return True
    
    return False

def clean_directory(root_path, stats):
    """
    Clean up hidden and system files while walking through the directory.
    Returns a list of remaining files for inventory.
    """
    file_data = []
    
    print("\nScanning and cleaning directory...")
    
    # Walk through directory with sorted order
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        # Remove hidden directories from the walk
        dirnames[:] = [d for d in sorted(dirnames) if not d.startswith('.')]
        
        # Sort files for consistent processing
        filenames.sort()
        
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            stats.total_files += 1
            
            try:
                if should_clean_file(filename, full_path):
                    # Get file size before deletion for statistics
                    try:
                        file_size = os.path.getsize(full_path)
                        stats.cleaned_size += file_size
                    except:
                        pass
                    
                    # Delete the file
                    os.remove(full_path)
                    stats.cleaned_files += 1
                    continue
                
                # Process remaining files for inventory
                file_stats = os.stat(full_path)
                rel_path = os.path.relpath(full_path, root_path)
                
                file_info = {
                    'filename': filename,
                    'relative_path': rel_path,
                    'size': humanize.naturalsize(file_stats.st_size),
                    'raw_size': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'directory': os.path.dirname(rel_path)
                }
                file_data.append(file_info)
                
            except Exception as e:
                error_msg = f"Error processing {full_path}: {e}"
                print(f"\n{error_msg}")
                stats.errors.append(error_msg)
    
    # Sort the final list by relative path
    file_data.sort(key=lambda x: x['relative_path'])
    return file_data

def save_to_csv(file_data, output_file):
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("\nSaving inventory to CSV...")
    # Define CSV headers in desired order
    headers = ['relative_path', 'filename', 'size', 'raw_size', 'modified', 'directory']
    
    # Write to CSV file with progress bar
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        # Write rows with progress bar
        for row in tqdm(file_data, desc="Writing to CSV", unit="row"):
            writer.writerow(row)

def get_directory_structure(file_data):
    """
    Extract unique directories from file data and create directory structure list
    """
    directories = set()
    dir_data = []
    
    # Get unique directories
    for file_info in file_data:
        rel_path = file_info['relative_path']
        current_path = ''
        # Add each level of the path
        for part in rel_path.split(os.sep):
            if current_path:
                current_path = os.path.join(current_path, part)
            else:
                current_path = part
            directories.add(os.path.dirname(current_path))
    
    # Remove empty string if present
    directories.discard('')
    
    # Convert to list and sort
    dir_list = sorted(list(directories))
    
    # Create directory information list
    for dir_path in dir_list:
        dir_info = {
            'directory_path': dir_path,
            'depth': len(dir_path.split(os.sep)) if dir_path else 0,
            'parent_directory': os.path.dirname(dir_path) if dir_path else '',
            'directory_name': os.path.basename(dir_path) if dir_path else ''
        }
        dir_data.append(dir_info)
    
    return dir_data

def save_directory_structure(dir_data, output_file):
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("\nSaving directory structure to CSV...")
    # Define CSV headers for directory structure
    headers = ['directory_path', 'depth', 'parent_directory', 'directory_name']
    
    # Write to CSV file with progress bar
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        # Write rows with progress bar
        for row in tqdm(dir_data, desc="Writing directory structure", unit="dir"):
            writer.writerow(row)

def normalize_path_to_filename(path, prefix):
    # Get the last directory name from the path
    base_name = os.path.basename(path.rstrip('/'))
    # Replace non-alphanumeric characters with underscores and convert to lowercase
    normalized = re.sub(r'[^a-zA-Z0-9]', '_', base_name).lower()
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{normalized}_{timestamp}.csv"

def main():
    print(f"Starting cleanup and inventory of: {ROOT_DIRECTORY}")
    
    # Initialize statistics
    stats = FileStats()
    
    # Clean directory and get remaining files
    file_data = clean_directory(ROOT_DIRECTORY, stats)
    
    # Get directory structure
    dir_data = get_directory_structure(file_data)
    
    # Generate output filenames and save both inventories
    files_filename = normalize_path_to_filename(ROOT_DIRECTORY, "inventory_files")
    dirs_filename = normalize_path_to_filename(ROOT_DIRECTORY, "inventory_dirs")
    
    files_csv = os.path.join(OUTPUT_DIRECTORY, files_filename)
    dirs_csv = os.path.join(OUTPUT_DIRECTORY, dirs_filename)
    
    save_to_csv(file_data, files_csv)
    save_directory_structure(dir_data, dirs_csv)
    
    # Print summary
    print(f"\nCleanup and Inventory Summary:")
    print(f"Total files processed: {stats.total_files}")
    print(f"Files cleaned up: {stats.cleaned_files}")
    print(f"Space freed: {humanize.naturalsize(stats.cleaned_size)}")
    print(f"Remaining files inventoried: {len(file_data)}")
    print(f"Directories inventoried: {len(dir_data)}")
    print(f"\nOutput files:")
    print(f"- Files inventory: {files_csv}")
    print(f"- Directory structure: {dirs_csv}")
    
    if stats.errors:
        print(f"\nErrors encountered ({len(stats.errors)}):")
        for error in stats.errors:
            print(f"- {error}")

if __name__ == "__main__":
    main()
