"""
ChromaDB Service for SkillsMatch.AI
Handles vector embeddings for PDF documents and semantic search
"""

import os
import hashlib
import pdfplumber
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
import json

class ChromaDBService:
    """Service for managing PDF document vectors using ChromaDB"""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """Initialize ChromaDB service"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collections with default embedding function
        self.resume_collection = self._get_or_create_collection("resumes")
        self.job_collection = self._get_or_create_collection("jobs")
        
        print(f"✅ ChromaDB initialized at: {persist_directory}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            collection = self.client.get_collection(name=name)
            print(f"📂 Using existing collection: {name}")
        except:
            # Use default embedding function (all-MiniLM-L6-v2)
            collection = self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"🆕 Created new collection: {name}")
        return collection
    
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
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better embeddings"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def add_resume_to_vector_db(self, profile_id: str, pdf_path: str, metadata: Dict[str, Any] = None) -> bool:
        """Add resume PDF to vector database"""
        try:
            print(f"📄 Processing resume for profile: {profile_id}")
            
            # Extract text from PDF
            text_content = self.extract_pdf_text(pdf_path)
            if not text_content:
                print(f"⚠️ No text extracted from PDF: {pdf_path}")
                return False
            
            # Chunk text for better embeddings
            chunks = self.chunk_text(text_content)
            if not chunks:
                print(f"⚠️ No text chunks created from PDF: {pdf_path}")
                return False
            
            # Prepare metadata
            base_metadata = {
                "profile_id": profile_id,
                "document_type": "resume",
                "file_path": pdf_path,
                "total_chunks": len(chunks),
                "text_length": len(text_content)
            }
            if metadata:
                base_metadata.update(metadata)
            
            # Create unique IDs for each chunk
            chunk_ids = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{profile_id}_resume_chunk_{i}"
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
                chunk_ids.append(chunk_id)
                chunk_metadatas.append(chunk_metadata)
            
            # Add to ChromaDB (uses default embedding function)
            self.resume_collection.add(
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            print(f"✅ Added {len(chunks)} chunks to resume collection for {profile_id}")
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
            
            # Chunk text
            chunks = self.chunk_text(text_content, chunk_size=300)
            if not chunks:
                print(f"⚠️ No text chunks created for job: {job_id}")
                return False
            
            # Prepare metadata
            base_metadata = {
                "job_id": job_id,
                "document_type": "job",
                "title": job_data.get('title', ''),
                "company": job_data.get('company', ''),
                "location": job_data.get('location', ''),
                "category": job_data.get('category', ''),
                "total_chunks": len(chunks)
            }
            
            # Create unique IDs for each chunk
            chunk_ids = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{job_id}_job_chunk_{i}"
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
                chunk_ids.append(chunk_id)
                chunk_metadatas.append(chunk_metadata)
            
            # Add to ChromaDB (uses default embedding function)
            self.job_collection.add(
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            print(f"✅ Added {len(chunks)} chunks to job collection for {job_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding job to vector DB: {e}")
            return False
    
    def search_similar_jobs(self, resume_text: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Find jobs similar to resume content using vector search"""
        try:
            print(f"🔍 Searching for jobs similar to resume content...")
            
            # Search in job collection (ChromaDB will handle embedding)
            results = self.job_collection.query(
                query_texts=[resume_text],
                n_results=n_results,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Process results
            similar_jobs = []
            seen_jobs = set()
            
            for i, metadata in enumerate(results['metadatas'][0]):
                job_id = metadata.get('job_id')
                if job_id not in seen_jobs:
                    similarity_score = 1 - results['distances'][0][i]  # Convert distance to similarity
                    similar_jobs.append({
                        'job_id': job_id,
                        'title': metadata.get('title', ''),
                        'company': metadata.get('company', ''),
                        'location': metadata.get('location', ''),
                        'category': metadata.get('category', ''),
                        'similarity_score': float(similarity_score),
                        'matched_text': results['documents'][0][i][:200] + "..."
                    })
                    seen_jobs.add(job_id)
            
            print(f"✅ Found {len(similar_jobs)} similar jobs")
            return similar_jobs
            
        except Exception as e:
            print(f"❌ Error searching similar jobs: {e}")
            return []
    
    def get_resume_insights(self, profile_id: str) -> Dict[str, Any]:
        """Get insights from resume vectors"""
        try:
            # Query resume chunks for this profile
            results = self.resume_collection.get(
                where={"profile_id": profile_id},
                include=['metadatas', 'documents']
            )
            
            if not results['ids']:
                return {"status": "no_resume", "message": "No resume found in vector database"}
            
            total_chunks = len(results['ids'])
            total_text_length = sum(meta.get('text_length', 0) for meta in results['metadatas'])
            
            return {
                "status": "success",
                "profile_id": profile_id,
                "total_chunks": total_chunks,
                "estimated_text_length": total_text_length,
                "resume_available": True
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
                # Extract profile ID from filename (assuming format: profilename_resume.pdf)
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
chroma_service = None

def get_chroma_service() -> ChromaDBService:
    """Get or create ChromaDB service instance"""
    global chroma_service
    if chroma_service is None:
        chroma_service = ChromaDBService()
        # Initialize with existing resumes
        chroma_service.initialize_existing_resumes()
    return chroma_service