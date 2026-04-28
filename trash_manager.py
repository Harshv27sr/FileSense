import os
import shutil
from datetime import datetime

class TrashManager:
    def __init__(self):
        self.trash_dir = os.path.join(os.path.expanduser("~"), ".file_manager_trash")
        os.makedirs(self.trash_dir, exist_ok=True)
    
    def move_to_trash(self, filepath):
        """Move file to trash folder instead of permanent deletion"""
        try:
            if not os.path.exists(filepath):
                return False, "File does not exist"
            
            # Create unique filename in trash
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_filename = f"{timestamp}_{filename}"
            trash_path = os.path.join(self.trash_dir, trash_filename)
            
            # Move to trash
            shutil.move(filepath, trash_path)
            
            return True, trash_path
        except Exception as e:
            return False, str(e)
    
    def restore_from_trash(self, trash_path, original_path=None):
        """Restore file from trash"""
        try:
            if not os.path.exists(trash_path):
                return False, "File not found in trash"
            
            if original_path and os.path.exists(original_path):
                # Handle conflict
                base, ext = os.path.splitext(original_path)
                counter = 1
                while os.path.exists(original_path):
                    original_path = f"{base}_restored_{counter}{ext}"
                    counter += 1
            
            dest_path = original_path or os.path.join(
                os.path.dirname(trash_path), 
                os.path.basename(trash_path)[16:]  # Remove timestamp
            )
            
            shutil.move(trash_path, dest_path)
            return True, dest_path
        except Exception as e:
            return False, str(e)
    
    def empty_trash(self):
        """Permanently delete all files in trash"""
        try:
            for filename in os.listdir(self.trash_dir):
                filepath = os.path.join(self.trash_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            return True, "Trash emptied"
        except Exception as e:
            return False, str(e)
    
    def get_trash_contents(self):
        """Get list of files in trash"""
        files = []
        for filename in os.listdir(self.trash_dir):
            filepath = os.path.join(self.trash_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    'trash_path': filepath,
                    'filename': filename[16:],  # Remove timestamp
                    'deleted_date': filename[:15],
                    'size': os.path.getsize(filepath)
                })
        return files