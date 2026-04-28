import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="file_registry.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main file registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT UNIQUE NOT NULL,
                filetype TEXT,
                filesize INTEGER,
                hash_value TEXT,
                upload_date TIMESTAMP,
                category TEXT,
                is_duplicate BOOLEAN DEFAULT 0,
                duplicate_group_id INTEGER
            )
        ''')
        
        # Similar files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similar_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id1 INTEGER,
                file_id2 INTEGER,
                similarity_score REAL,
                FOREIGN KEY (file_id1) REFERENCES file_registry(id),
                FOREIGN KEY (file_id2) REFERENCES file_registry(id)
            )
        ''')
        
        # Trash table for safe deletion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT,
                trash_path TEXT,
                deletion_date TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_file(self, filepath, filename, filetype, filesize, hash_value, category):
        """Insert file record into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO file_registry 
                (filename, filepath, filetype, filesize, hash_value, upload_date, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (filename, filepath, filetype, filesize, hash_value, datetime.now(), category))
            
            conn.commit()
            file_id = cursor.lastrowid
            conn.close()
            return file_id, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "File already exists in database"
        except Exception as e:
            conn.close()
            return None, str(e)
    
    def get_all_files(self):
        """Retrieve all files from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM file_registry ORDER BY upload_date DESC')
        files = cursor.fetchall()
        conn.close()
        return files
    
    def check_duplicate(self, hash_value):
        """Check if hash already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, filepath FROM file_registry WHERE hash_value = ?', (hash_value,))
        duplicate = cursor.fetchone()
        conn.close()
        return duplicate
    
    def mark_as_duplicate(self, file_id, group_id):
        """Mark file as duplicate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE file_registry 
            SET is_duplicate = 1, duplicate_group_id = ? 
            WHERE id = ?
        ''', (group_id, file_id))
        conn.commit()
        conn.close()
    
    def add_similar_pair(self, file_id1, file_id2, score):
        """Add similar file pair to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO similar_files (file_id1, file_id2, similarity_score)
            VALUES (?, ?, ?)
        ''', (file_id1, file_id2, score))
        conn.commit()
        conn.close()
    
    def get_similar_files(self, file_id):
        """Get similar files for a given file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, s.similarity_score 
            FROM file_registry f
            JOIN similar_files s ON f.id = s.file_id2
            WHERE s.file_id1 = ? AND s.similarity_score >= 0.8
            ORDER BY s.similarity_score DESC
        ''', (file_id,))
        similar = cursor.fetchall()
        conn.close()
        return similar
    
    def delete_file_record(self, file_id):
        """Delete file record from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM file_registry WHERE id = ?', (file_id,))
        cursor.execute('DELETE FROM similar_files WHERE file_id1 = ? OR file_id2 = ?', (file_id, file_id))
        conn.commit()
        conn.close()
    
    def add_to_trash(self, original_path, trash_path):
        """Add deleted file to trash record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trash (original_path, trash_path, deletion_date)
            VALUES (?, ?, ?)
        ''', (original_path, trash_path, datetime.now()))
        conn.commit()
        conn.close()
    
    # FIXED: These methods are now properly indented inside the class
    def clear_all_files(self):
        """Clear all file records but keep trash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete all file records
        cursor.execute('DELETE FROM file_registry')
        cursor.execute('DELETE FROM similar_files')
        
        conn.commit()
        conn.close()
        print("✅ All file records cleared")
        return True

    def reset_database(self):
        """Reset the database completely (clear all tables)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop and recreate tables
        cursor.execute('DROP TABLE IF EXISTS file_registry')
        cursor.execute('DROP TABLE IF EXISTS similar_files')
        # Don't drop trash table
        
        # Recreate tables
        self.init_database()
        
        conn.commit()
        conn.close()
        print("✅ Database reset completed")
        return True

    def get_trash_count(self):
        """Get number of files in trash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM trash')
        count = cursor.fetchone()[0]
        conn.close()
        return count