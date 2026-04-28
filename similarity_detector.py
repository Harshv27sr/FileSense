import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class SimilarityDetector:
    def __init__(self):
        self.text_files_cache = {}
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
    
    def extract_text(self, filepath):
        """Extract text content from file"""
        try:
            # Check cache first
            if filepath in self.text_files_cache:
                return self.text_files_cache[filepath]
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        text = f.read(2000)  # Read first 2000 chars for efficiency
                        self.text_files_cache[filepath] = text
                        return text
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            return ""
    
    def calculate_cosine_similarity(self, text1, text2):
        """Calculate cosine similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def calculate_filename_similarity(self, name1, name2):
        """Calculate Levenshtein distance ratio for filenames"""
        if not name1 or not name2:
            return 0.0
        
        # Remove extensions for comparison
        name1 = os.path.splitext(name1)[0]
        name2 = os.path.splitext(name2)[0]
        
        # Calculate Levenshtein ratio
        distance = Levenshtein.distance(name1.lower(), name2.lower())
        max_len = max(len(name1), len(name2))
        
        if max_len == 0:
            return 0.0
        
        similarity = 1 - (distance / max_len)
        return similarity
    
    def find_similar_files(self, files_with_content, threshold=0.8):
        """Find similar files based on content and filename"""
        similar_pairs = []
        n = len(files_with_content)
        
        if n < 2:
            return similar_pairs
        
        # Prepare data
        file_ids = [f['id'] for f in files_with_content]
        texts = [f['content'] for f in files_with_content]
        filenames = [f['filename'] for f in files_with_content]
        
        try:
            # Calculate TF-IDF for all texts
            if any(texts):
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                
                # Calculate cosine similarities
                cosine_sim_matrix = cosine_similarity(tfidf_matrix)
                
                # Find similar pairs
                for i in range(n):
                    for j in range(i+1, n):
                        # Content similarity
                        content_sim = cosine_sim_matrix[i, j]
                        
                        # Filename similarity
                        name_sim = self.calculate_filename_similarity(filenames[i], filenames[j])
                        
                        # Combined similarity (weighted average)
                        combined_sim = (content_sim * 0.7) + (name_sim * 0.3)
                        
                        if combined_sim >= threshold:
                            similar_pairs.append({
                                'file_id1': file_ids[i],
                                'file_id2': file_ids[j],
                                'content_similarity': float(content_sim),
                                'filename_similarity': float(name_sim),
                                'combined_similarity': float(combined_sim)
                            })
        except Exception as e:
            print(f"Error in similarity calculation: {e}")
        
        return similar_pairs
    
    def process_files_parallel(self, files, max_workers=4):
        """Process multiple files in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.extract_text, f['filepath']): f 
                for f in files
            }
            
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    content = future.result()
                    results.append({
                        'id': file_info['id'],
                        'filename': file_info['filename'],
                        'content': content
                    })
                except Exception as e:
                    print(f"Error processing {file_info['filename']}: {e}")
                    results.append({
                        'id': file_info['id'],
                        'filename': file_info['filename'],
                        'content': ""
                    })
        
        return results