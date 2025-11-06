"""
PDF Text Extraction Service for SkillsMatch.AI
Extracts text from PDF resume files using multiple libraries for best compatibility
"""
import os
import io
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import re

# PDF processing libraries
import PyPDF2
import pdfplumber
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """
    Service class for extracting text from PDF and document files
    Uses multiple extraction methods for best compatibility
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a file (PDF, DOCX, etc.)
        
        Args:
            file_path: Path to the file to extract text from
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'text': '',
                'method': None,
                'word_count': 0
            }
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            return {
                'success': False,
                'error': f'Unsupported file format: {file_extension}',
                'text': '',
                'method': None,
                'word_count': 0
            }
    
    def _extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF using multiple methods"""
        
        # Method 1: Try pdfplumber (best for complex layouts)
        try:
            text = self._extract_with_pdfplumber(file_path)
            if text and len(text.strip()) > 50:  # Minimum viable text length
                return {
                    'success': True,
                    'text': text,
                    'method': 'pdfplumber',
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'error': None
                }
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
        
        # Method 2: Try PyPDF2 (fallback)
        try:
            text = self._extract_with_pypdf2(file_path)
            if text and len(text.strip()) > 50:
                return {
                    'success': True,
                    'text': text,
                    'method': 'PyPDF2',
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'error': None
                }
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {file_path}: {e}")
        
        return {
            'success': False,
            'error': 'All PDF extraction methods failed',
            'text': '',
            'method': None,
            'word_count': 0
        }
    
    def _extract_with_pdfplumber(self, file_path: Path) -> str:
        """Extract text using pdfplumber"""
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return self._clean_text('\n'.join(text_parts))
    
    def _extract_with_pypdf2(self, file_path: Path) -> str:
        """Extract text using PyPDF2"""
        text_parts = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return self._clean_text('\n'.join(text_parts))
    
    def _extract_from_docx(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
            text = '\n'.join(paragraphs)
            
            return {
                'success': True,
                'text': self._clean_text(text),
                'method': 'python-docx',
                'word_count': len(text.split()),
                'char_count': len(text),
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'DOCX extraction failed: {e}',
                'text': '',
                'method': None,
                'word_count': 0
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s@.,;:()\-+/]', '', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_key_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from resume text
        
        Args:
            text: Raw extracted text from resume
            
        Returns:
            Dictionary with identified sections
        """
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'other': ''
        }
        
        # Convert to lowercase for pattern matching
        text_lower = text.lower()
        lines = text.split('\n')
        
        current_section = 'other'
        section_text = []
        
        # Common section headers
        section_patterns = {
            'summary': r'(summary|profile|objective|about)',
            'experience': r'(experience|employment|work|career)',
            'education': r'(education|academic|qualification|degree)',
            'skills': r'(skills|competenc|technical|expertise)',
            'contact': r'(contact|phone|email|address)'
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line_lower) and len(line.strip()) < 50:
                    # Save previous section
                    if section_text:
                        sections[current_section] += ' '.join(section_text)
                    
                    # Start new section
                    current_section = section_name
                    section_text = []
                    section_found = True
                    break
            
            if not section_found and line.strip():
                section_text.append(line.strip())
        
        # Save the last section
        if section_text:
            sections[current_section] += ' '.join(section_text)
        
        return sections

# Global instance
pdf_extractor = PDFTextExtractor()

def extract_resume_text(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to extract text from resume file
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dictionary with extraction results and parsed sections
    """
    result = pdf_extractor.extract_text_from_file(file_path)
    
    if result['success']:
        # Extract key sections
        sections = pdf_extractor.extract_key_sections(result['text'])
        result['sections'] = sections
    
    return result

if __name__ == "__main__":
    # Test the PDF extractor
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"Testing PDF extraction on: {test_file}")
        
        result = extract_resume_text(test_file)
        
        print(f"Success: {result['success']}")
        print(f"Method: {result.get('method', 'N/A')}")
        print(f"Word count: {result.get('word_count', 0)}")
        
        if result['success']:
            print(f"Text preview: {result['text'][:200]}...")
            
            if 'sections' in result:
                print("\nDetected sections:")
                for section, content in result['sections'].items():
                    if content:
                        print(f"  {section}: {len(content)} chars")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python pdf_extractor.py <path_to_pdf>")