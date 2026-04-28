import os
import hashlib
from pathlib import Path

class FileScanner:
    def __init__(self):
        self.supported_text_extensions = {'.txt', '.py', '.java', '.cpp', '.html', '.css', 
                                          '.js', '.json', '.xml', '.md', '.csv', '.ini',
                                          '.conf', '.log', '.rtf', '.doc', '.docx'}
    
    def get_file_hash(self, filepath, chunk_size=8192):
        """Generate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error hashing file {filepath}: {e}")
            return None
    
    def get_file_info(self, filepath):
        """Extract file metadata"""
        try:
            path = Path(filepath)
            stats = os.stat(filepath)
            
            return {
                'filename': path.name,
                'filepath': str(path.absolute()),
                'filetype': path.suffix.lower(),
                'filesize': stats.st_size,
                'modified_time': stats.st_mtime,
                'category': self.get_category(path.suffix.lower())
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def get_category(self, extension):
        """Categorize file based on extension"""
        categories = {
            '.txt': 'Documents', '.pdf': 'Documents', '.doc': 'Documents', 
            '.docx': 'Documents', '.odt': 'Documents', '.rtf': 'Documents',
            '.xls': 'Spreadsheets', '.xlsx': 'Spreadsheets', '.csv': 'Spreadsheets',
            '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images',
            '.bmp': 'Images', '.svg': 'Images', '.webp': 'Images',
            '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio', '.aac': 'Audio',
            '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video', '.mov': 'Video',
            '.py': 'Code', '.java': 'Code', '.cpp': 'Code', '.html': 'Code',
            '.css': 'Code', '.js': 'Code', '.json': 'Code',
            '.zip': 'Archives', '.rar': 'Archives', '.7z': 'Archives', '.tar': 'Archives',
            '.exe': 'Executables', '.msi': 'Executables', '.app': 'Executables',
            '.pdf': 'PDFs'
        }
        return categories.get(extension, 'Other')
    
    def scan_directory(self, directory_path, progress_callback=None):
        """Scan directory and return list of files"""
        files = []
        total_files = 0
        
        # Count total files first
        for root, dirs, files_in_dir in os.walk(directory_path):
            total_files += len(files_in_dir)
        
        processed = 0
        # Collect all files
        for root, dirs, files_in_dir in os.walk(directory_path):
            for file in files_in_dir:
                filepath = os.path.join(root, file)
                files.append(filepath)
                
                processed += 1
                if progress_callback:
                    progress_callback(processed, total_files, file)
        
        return files