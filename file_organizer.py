import os
import shutil
from pathlib import Path

class FileOrganizer:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/OrganizedFiles")
        
    def organize_file(self, filepath, category):
        """Move file to category folder"""
        try:
            # Create category directory if it doesn't exist
            category_dir = os.path.join(self.base_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # Get filename and create destination path
            filename = os.path.basename(filepath)
            dest_path = os.path.join(category_dir, filename)
            
            # Handle filename conflicts
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{name}_{counter}{ext}"
                    dest_path = os.path.join(category_dir, new_filename)
                    counter += 1
            
            # Move file
            shutil.move(filepath, dest_path)
            return dest_path, None
        except Exception as e:
            return None, str(e)
    
    def create_folder_structure(self):
        """Create default folder structure"""
        folders = [
            'Documents', 'Spreadsheets', 'Images', 'Audio', 'Video',
            'Code', 'Archives', 'Executables', 'PDFs', 'Other',
            'Duplicates', 'Similar_Files'
        ]
        
        for folder in folders:
            folder_path = os.path.join(self.base_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        return self.base_dir
    
    def organize_by_date(self, filepath):
        """Organize files by modification date"""
        try:
            # Get file modification time
            mtime = os.path.getmtime(filepath)
            from datetime import datetime
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m')
            
            # Create year-month folder
            date_dir = os.path.join(self.base_dir, 'By_Date', date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # Move file
            filename = os.path.basename(filepath)
            dest_path = os.path.join(date_dir, filename)
            
            # Handle conflicts
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{name}_{counter}{ext}"
                    dest_path = os.path.join(date_dir, new_filename)
                    counter += 1
            
            shutil.move(filepath, dest_path)
            return dest_path, None
        except Exception as e:
            return None, str(e)