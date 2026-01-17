#!/usr/bin/env python3
"""
Job Vector Database Generator for SkillsMatch.AI
Pre-processes all jobs and creates embeddings for efficient matching.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import pickle

# Load environment
load_dotenv()

class JobVectorGenerator:
    def __init__(self):
        self.openai_client = None
        self.initialize_openai()
        self.jobs_data = []
        self.job_embeddings = {}
        self.project_root = Path(__file__).resolve().parents[1]
        
    def initialize_openai(self):
        """Initialize OpenAI client for embeddings"""
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            print("✅ OpenAI client initialized for embeddings")
        else:
            print("❌ No OpenAI API key found - using fallback method")
    
    def load_jobs_from_sqlite(self):
        """Load all jobs from SQLite database"""
        try:
            db_path = self.project_root / "web" / "data" / "skillsmatch.db"
            
            if not db_path.exists():
                print(f"❌ Database not found at {db_path}")
                return []
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all active jobs
            cursor.execute("""
                SELECT job_id, title, company_name, job_description, 
                       position_level, min_years_experience, employment_type,
                       work_arrangement, min_salary, max_salary, address
                FROM jobs 
                WHERE is_active = 1
            """)
            
            jobs = cursor.fetchall()
            conn.close()
            
            # Convert to dictionaries
            job_list = []
            for job in jobs:
                job_dict = {
                    'job_id': job[0],
                    'title': job[1],
                    'company_name': job[2],
                    'description': job[3],
                    'position_level': job[4],
                    'min_years_experience': job[5],
                    'employment_type': job[6],
                    'work_arrangement': job[7],
                    'min_salary': job[8],
                    'max_salary': job[9],
                    'location': job[10]
                }
                job_list.append(job_dict)
            
            print(f"📊 Loaded {len(job_list)} jobs from SQLite database")
            return job_list
            
        except Exception as e:
            print(f"❌ Error loading jobs from SQLite: {e}")
            return []
    
    def create_job_summary(self, job: Dict) -> str:
        """Create a comprehensive summary for embedding"""
        summary_parts = []
        
        # Job title and company
        if job.get('title'):
            summary_parts.append(f"Job Title: {job['title']}")
        if job.get('company_name'):
            summary_parts.append(f"Company: {job['company_name']}")
        
        # Job description (truncated for embedding efficiency)
        if job.get('description'):
            desc = job['description'][:500]  # Limit length
            summary_parts.append(f"Description: {desc}")
        
        # Level and experience
        if job.get('position_level'):
            summary_parts.append(f"Level: {job['position_level']}")
        if job.get('min_years_experience'):
            summary_parts.append(f"Experience: {job['min_years_experience']} years")
        
        # Employment details
        if job.get('employment_type'):
            summary_parts.append(f"Type: {job['employment_type']}")
        if job.get('work_arrangement'):
            summary_parts.append(f"Arrangement: {job['work_arrangement']}")
        
        # Location
        if job.get('location'):
            summary_parts.append(f"Location: {job['location']}")
        
        return " | ".join(summary_parts)
    
    def generate_embeddings(self, jobs: List[Dict]) -> Dict[int, List[float]]:
        """Generate embeddings for all jobs"""
        if not self.openai_client:
            print("⚠️ No OpenAI client - using simple text matching fallback")
            return self.generate_fallback_vectors(jobs)
        
        embeddings = {}
        batch_size = 10  # Process in batches to avoid rate limits
        
        print(f"🔄 Generating embeddings for {len(jobs)} jobs...")
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            batch_texts = [self.create_job_summary(job) for job in batch]
            
            try:
                # Use OpenAI's text-embedding-3-small (most cost-effective)
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch_texts
                )
                
                # Store embeddings
                for j, job in enumerate(batch):
                    job_id = job['job_id']
                    embedding = response.data[j].embedding
                    embeddings[job_id] = embedding
                
                print(f"✅ Processed batch {i//batch_size + 1}/{(len(jobs) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"❌ Error generating embeddings for batch {i//batch_size + 1}: {e}")
                # Fallback for this batch
                for job in batch:
                    embeddings[job['job_id']] = self.simple_text_vector(self.create_job_summary(job))
        
        return embeddings
    
    def generate_fallback_vectors(self, jobs: List[Dict]) -> Dict[int, List[float]]:
        """Generate simple text-based vectors as fallback"""
        print("🔄 Generating fallback text vectors...")
        
        # Create vocabulary from all job texts
        all_words = set()
        job_texts = {}
        
        for job in jobs:
            text = self.create_job_summary(job).lower()
            words = set(text.split())
            all_words.update(words)
            job_texts[job['job_id']] = words
        
        vocab = sorted(list(all_words))
        print(f"📝 Created vocabulary with {len(vocab)} words")
        
        # Create simple vectors
        embeddings = {}
        for job_id, words in job_texts.items():
            vector = [1.0 if word in words else 0.0 for word in vocab]
            embeddings[job_id] = vector
        
        return embeddings
    
    def simple_text_vector(self, text: str, dim: int = 384) -> List[float]:
        """Create a simple hash-based vector"""
        import hashlib
        
        # Create hash-based vector
        vector = []
        words = text.lower().split()
        
        for i in range(dim):
            hash_input = f"{text}_{i}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
            vector.append(float(hash_val % 1000) / 1000.0)
        
        return vector
    
    def save_job_vectors(self, jobs: List[Dict], embeddings: Dict[int, List[float]]):
        """Save jobs and embeddings to files"""
        data_dir = self.project_root / "web" / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Save job data
        jobs_file = data_dir / "jobs_vector_data.json"
        with open(jobs_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Save embeddings
        embeddings_file = data_dir / "job_embeddings.pkl"
        with open(embeddings_file, 'wb') as f:
            pickle.dump(embeddings, f)
        
        print(f"✅ Saved {len(jobs)} jobs to {jobs_file}")
        print(f"✅ Saved {len(embeddings)} embeddings to {embeddings_file}")
    
    def generate_all(self):
        """Main method to generate and save all job vectors"""
        print("🚀 Starting Job Vector Generation")
        print("=" * 50)
        
        # Load jobs from SQLite
        jobs = self.load_jobs_from_sqlite()
        if not jobs:
            print("❌ No jobs found - exiting")
            return
        
        # Generate embeddings
        embeddings = self.generate_embeddings(jobs)
        
        # Save everything
        self.save_job_vectors(jobs, embeddings)
        
        print("=" * 50)
        print("✅ Job vector generation complete!")
        print(f"📊 Processed {len(jobs)} jobs")
        print(f"🎯 Ready for efficient AI matching")

if __name__ == "__main__":
    generator = JobVectorGenerator()
    generator.generate_all()