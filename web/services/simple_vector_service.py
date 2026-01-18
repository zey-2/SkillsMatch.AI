"""
Simple Vector Search Service for SkillsMatch.AI
Using scikit-learn for PDF document similarity matching
"""

import os
import json
import pickle
import pdfplumber
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimpleVectorService:
    """Simple vector search service using TF-IDF and cosine similarity"""
    
    def __init__(self, data_dir: str = "data/vector_db"):
        """Initialize vector service"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.resumes_file = self.data_dir / "resumes.json"
        self.jobs_file = self.data_dir / "jobs.json"
        self.vectorizer_file = self.data_dir / "vectorizer.pkl"
        self.resume_vectors_file = self.data_dir / "resume_vectors.pkl"
        self.job_vectors_file = self.data_dir / "job_vectors.pkl"
        
        # Initialize components
        self.vectorizer = None
        self.resume_data = []
        self.job_data = []
        self.resume_vectors = None
        self.job_vectors = None
        
        # Load existing data
        self._load_data()
        
        print(f"✅ Simple Vector Service initialized at: {data_dir}")
    
    def _load_data(self):
        """Load existing vector data"""
        try:
            # Load resume data
            if self.resumes_file.exists():
                with open(self.resumes_file, 'r') as f:
                    self.resume_data = json.load(f)
                print(f"📂 Loaded {len(self.resume_data)} resumes")
            
            # Load job data
            if self.jobs_file.exists():
                with open(self.jobs_file, 'r') as f:
                    self.job_data = json.load(f)
                print(f"💼 Loaded {len(self.job_data)} jobs")
            
            # Load vectorizer
            if self.vectorizer_file.exists():
                with open(self.vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("🔧 Loaded existing vectorizer")
            
            # Load vectors
            if self.resume_vectors_file.exists():
                with open(self.resume_vectors_file, 'rb') as f:
                    self.resume_vectors = pickle.load(f)
                print("📊 Loaded resume vectors")
            
            if self.job_vectors_file.exists():
                with open(self.job_vectors_file, 'rb') as f:
                    self.job_vectors = pickle.load(f)
                print("📊 Loaded job vectors")
                
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
    
    def _save_data(self):
        """Save vector data"""
        try:
            # Save resume data
            with open(self.resumes_file, 'w') as f:
                json.dump(self.resume_data, f, indent=2)
            
            # Save job data
            with open(self.jobs_file, 'w') as f:
                json.dump(self.job_data, f, indent=2)
            
            # Save vectorizer
            if self.vectorizer:
                with open(self.vectorizer_file, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
            
            # Save vectors
            if self.resume_vectors is not None:
                with open(self.resume_vectors_file, 'wb') as f:
                    pickle.dump(self.resume_vectors, f)
            
            if self.job_vectors is not None:
                with open(self.job_vectors_file, 'wb') as f:
                    pickle.dump(self.job_vectors, f)
                    
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                return full_text.strip()
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return ""
    
    def add_resume_to_vector_db(self, profile_id: str, pdf_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Add resume PDF to vector database"""
        try:
            print(f"📄 Processing resume for profile: {profile_id}")
            
            # Extract text from PDF
            text_content = self.extract_pdf_text(pdf_path)
            if not text_content:
                print(f"⚠️ No text extracted from PDF: {pdf_path}")
                return False
            
            # Create resume entry
            resume_entry = {
                'profile_id': profile_id,
                'text_content': text_content,
                'file_path': pdf_path,
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Check if resume already exists
            existing_index = None
            for i, resume in enumerate(self.resume_data):
                if resume['profile_id'] == profile_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing resume
                self.resume_data[existing_index] = resume_entry
                print(f"📝 Updated existing resume for {profile_id}")
            else:
                # Add new resume
                self.resume_data.append(resume_entry)
                print(f"➕ Added new resume for {profile_id}")
            
            # Rebuild vectors
            self._rebuild_vectors()
            self._save_data()
            
            print(f"✅ Resume successfully processed for {profile_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding resume to vector DB: {e}")
            return False
    
    def add_job_to_vector_db(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """Add job description to vector database"""
        try:
            print(f"💼 Processing job for vector DB: {job_id}")
            
            # Combine job text fields
            text_parts = []
            if job_data.get('title'):
                text_parts.append(f"Job Title: {job_data['title']}")
            if job_data.get('description'):
                text_parts.append(f"Description: {job_data['description']}")
            if job_data.get('requirements'):
                if isinstance(job_data['requirements'], list):
                    text_parts.append(f"Requirements: {', '.join(job_data['requirements'])}")
                else:
                    text_parts.append(f"Requirements: {job_data['requirements']}")
            if job_data.get('skills'):
                if isinstance(job_data['skills'], list):
                    text_parts.append(f"Skills: {', '.join(job_data['skills'])}")
                else:
                    text_parts.append(f"Skills: {job_data['skills']}")
            
            text_content = "\n".join(text_parts)
            if not text_content:
                print(f"⚠️ No text content for job: {job_id}")
                return False
            
            # Create job entry
            job_entry = {
                'job_id': job_id,
                'text_content': text_content,
                'title': job_data.get('title', ''),
                'company': job_data.get('company', ''),
                'location': job_data.get('location', ''),
                'category': job_data.get('category', ''),
                'created_at': datetime.now().isoformat(),
                'original_data': job_data
            }
            
            # Check if job already exists
            existing_index = None
            for i, job in enumerate(self.job_data):
                if job['job_id'] == job_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing job
                self.job_data[existing_index] = job_entry
                print(f"📝 Updated existing job {job_id}")
            else:
                # Add new job
                self.job_data.append(job_entry)
                print(f"➕ Added new job {job_id}")
            
            # Rebuild vectors
            self._rebuild_vectors()
            self._save_data()
            
            print(f"✅ Job successfully processed: {job_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding job to vector DB: {e}")
            return False
    
    def _rebuild_vectors(self):
        """Rebuild TF-IDF vectors for all documents"""
        try:
            print("🔄 Rebuilding vectors...")
            
            # Collect all text documents
            all_texts = []
            
            # Add resume texts
            for resume in self.resume_data:
                all_texts.append(resume['text_content'])
            
            # Add job texts
            for job in self.job_data:
                all_texts.append(job['text_content'])
            
            if not all_texts:
                print("⚠️ No texts to vectorize")
                return
            
            # Create or update vectorizer
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.9
                )
            
            # Fit and transform all texts
            all_vectors = self.vectorizer.fit_transform(all_texts)
            
            # Split vectors back into resumes and jobs
            num_resumes = len(self.resume_data)
            
            if num_resumes > 0:
                self.resume_vectors = all_vectors[:num_resumes]
            
            if len(self.job_data) > 0:
                self.job_vectors = all_vectors[num_resumes:]
            
            print(f"✅ Rebuilt vectors: {len(self.resume_data)} resumes, {len(self.job_data)} jobs")
            
        except Exception as e:
            print(f"❌ Error rebuilding vectors: {e}")
    
    def search_similar_jobs(self, resume_text: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Find jobs similar to resume content using vector search"""
        try:
            print(f"🔍 Searching for jobs similar to resume content...")
            
            if self.vectorizer is None or self.job_vectors is None or len(self.job_data) == 0:
                print("⚠️ No job vectors available for search")
                return []
            
            # Vectorize query text
            query_vector = self.vectorizer.transform([resume_text])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.job_vectors)[0]
            
            # Get top N results
            top_indices = np.argsort(similarities)[::-1][:n_results]
            
            # Build results
            similar_jobs = []
            for idx in top_indices:
                if idx < len(self.job_data):
                    job = self.job_data[idx]
                    similarity_score = float(similarities[idx])
                    
                    similar_jobs.append({
                        'job_id': job['job_id'],
                        'title': job['title'],
                        'company': job['company'],
                        'location': job['location'],
                        'category': job['category'],
                        'similarity_score': similarity_score,
                        'matched_text': job['text_content'][:200] + "...",
                        'original_data': job.get('original_data', {})
                    })
            
            # Debug: show all similarity scores
            similarity_preview = [f"{job['similarity_score']:.3f}" for job in similar_jobs[:5]]
            print(f"🔍 Similarity scores: {similarity_preview}")
            
            # Filter out low similarity scores (lowered threshold for testing)
            similar_jobs = [job for job in similar_jobs if job['similarity_score'] > 0.01]
            
            print(f"✅ Found {len(similar_jobs)} similar jobs")
            return similar_jobs
            
        except Exception as e:
            print(f"❌ Error searching similar jobs: {e}")
            return []
    
    def get_resume_insights(self, profile_id: str) -> Dict[str, Any]:
        """Get insights from resume"""
        try:
            # Find resume
            resume_data = None
            for resume in self.resume_data:
                if resume['profile_id'] == profile_id:
                    resume_data = resume
                    break
            
            if not resume_data:
                return {"status": "no_resume", "message": "No resume found in vector database"}
            
            return {
                "status": "success", 
                "profile_id": profile_id,
                "text_length": len(resume_data['text_content']),
                "resume_available": True,
                "created_at": resume_data.get('created_at', ''),
                "metadata": resume_data.get('metadata', {})
            }
            
        except Exception as e:
            print(f"❌ Error getting resume insights: {e}")
            return {"status": "error", "message": str(e)}
    
    def initialize_existing_resumes(self, uploads_dir: str = "uploads/resumes"):
        """Initialize vector database with existing resume files"""
        try:
            print(f"🔄 Initializing existing resumes from: {uploads_dir}")
            
            if not os.path.exists(uploads_dir):
                print(f"⚠️ Uploads directory not found: {uploads_dir}")
                return
            
            resume_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
            
            for resume_file in resume_files:
                # Extract profile ID from filename
                profile_id = resume_file.replace('_resume.pdf', '').replace('.pdf', '')
                pdf_path = os.path.join(uploads_dir, resume_file)
                
                print(f"📄 Processing existing resume: {resume_file} -> {profile_id}")
                
                success = self.add_resume_to_vector_db(
                    profile_id=profile_id,
                    pdf_path=pdf_path,
                    metadata={"source": "initialization", "filename": resume_file}
                )
                
                if success:
                    print(f"✅ Successfully processed: {resume_file}")
                else:
                    print(f"❌ Failed to process: {resume_file}")
            
            print(f"🎉 Initialization complete. Processed {len(resume_files)} resume files.")
            
        except Exception as e:
            print(f"❌ Error initializing existing resumes: {e}")

# Global instance
vector_service = None

def get_vector_service() -> SimpleVectorService:
    """Get or create Simple Vector service instance"""
    global vector_service
    if vector_service is None:
        vector_service = SimpleVectorService()
        # Initialize with existing resumes
        vector_service.initialize_existing_resumes()
    return vector_service