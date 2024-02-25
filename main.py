import os
import shutil
import json
import hashlib
import schedule
import time


def load_config(config_file):
    """Load configuration from a JSON file."""
    with open(config_file) as f:
        return json.load(f)


def organize_files(source_folder, config):
    """Organize files based on the provided configuration."""
    # Get file types and their corresponding folders from the config
    file_types = config.get("file_types", {})

    # Create folders for each file type if they don't already exist
    for folder in file_types.values():
        folder_path = os.path.join(source_folder, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Dictionary to keep track of file hashes
    file_hashes = {}

    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        if os.path.isfile(os.path.join(source_folder, filename)):
            file_path = os.path.join(source_folder, filename)
            file_hash = hash_file(file_path)

            # Check for duplicate files
            if file_hash in file_hashes.values():
                # Move duplicate file to separate folder
                duplicate_folder = os.path.join(source_folder, "Duplicates")
                if not os.path.exists(duplicate_folder):
                    os.makedirs(duplicate_folder)
                destination_file_path = os.path.join(duplicate_folder, filename)
                shutil.move(file_path, destination_file_path)
            else:
                file_hashes[filename] = file_hash

                # Determine destination folder based on file type
                file_extension = filename.split('.')[-1]
                destination_folder = file_types.get(file_extension, 'Others')
                destination_folder_path = os.path.join(source_folder, destination_folder)
                if not os.path.exists(destination_folder_path):
                    os.makedirs(destination_folder_path)

                # Move file to the corresponding destination folder
                destination_file_path = os.path.join(destination_folder_path, filename)
                shutil.move(file_path, destination_file_path)


def hash_file(file_path):
    """Calculate hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in 64k chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def main():
    # Ask user for the path
    source_folder = input("Enter the path to the folder you want to organize: ")

    # Check if the path exists
    if not os.path.exists(source_folder):
        print("The specified folder does not exist.")
        return

    # Load configuration
    config = load_config("config.json")

    # Organize files immediately
    organize_files(source_folder, config)
    print("Files organized successfully!")

    # Schedule automatic sorting
    interval = config.get("interval")
    schedule.every(interval).minutes.do(organize_files, source_folder=source_folder, config=config)

    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
