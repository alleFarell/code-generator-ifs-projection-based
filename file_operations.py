import os
import logging

def ensure_directory_exists(directory_path):
    """Ensure the directory exists. If not, create it."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")
