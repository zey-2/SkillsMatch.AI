"""
Professional PDF Application Generator for SkillsMatch.AI
Creates AI-powered job application PDFs with SkillsMatch.AI branding
"""

import io
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white, gray
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class SkillsMatchPDFGenerator:
    """Professional PDF generator for job applications"""
    
    def __init__(self):
        self.colors = {
            'primary': HexColor('#1e40af'),      # Professional Blue
            'secondary': HexColor('#0f766e'),    # Teal Green  
            'accent': HexColor('#ea580c'),       # Orange accent
            'text': HexColor('#111827'),         # Rich black
            'light_gray': HexColor('#f8fafc'),   # Light background
            'medium_gray': HexColor('#6b7280'),  # Medium gray
            'border': HexColor('#d1d5db'),       # Border gray
            'success': HexColor('#16a34a'),      # Success green
            'warning': HexColor('#d97706')       # Warning orange
        }
        
        # Initialize OpenAI if available
        self.openai_client = None
        openai_key = os.environ.get('OPENAI_API_KEY')
        if OPENAI_AVAILABLE and openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
    
    def create_styles(self):
        """Create custom styles for the PDF"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Header style
        styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subheader style
        styles.add(ParagraphStyle(
            name='CustomSubHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['text'],
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Small text style
        styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=styles['Normal'],
            fontSize=9,
            textColor=gray,
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        return styles
    
    def generate_ai_cover_letter(self, profile_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate AI-powered cover letter"""
        if not self.openai_client:
            return self._generate_template_cover_letter(profile_data, job_data)
        
        try:
            # Build context for AI
            user_name = profile_data.get('name', 'Professional')
            job_title = job_data.get('title', 'Position')
            company = job_data.get('company', 'Your Company')
            
            # Extract skills
            skills = []
            if profile_data.get('skills'):
                for skill in profile_data['skills']:
                    if isinstance(skill, dict):
                        skill_name = skill.get('skill_name', '')
                    else:
                        skill_name = str(skill)
                    if skill_name:
                        skills.append(skill_name)
            
            # Extract experience
            experience = profile_data.get('work_experience', [])
            education = profile_data.get('education', [])
            
            prompt = f"""Write a professional, compelling cover letter for this job application:

APPLICANT: {user_name}
JOB TITLE: {job_title}
COMPANY: {company}
LOCATION: {profile_data.get('location', 'Singapore')}

APPLICANT PROFILE:
- Current Title: {profile_data.get('title', 'Professional')}
- Experience Level: {profile_data.get('experience_level', 'Experienced')}
- Key Skills: {', '.join(skills[:8])}
- Work Experience: {len(experience)} positions
- Education: {len(education)} qualifications
- Professional Summary: {profile_data.get('summary', 'Dedicated professional')}

JOB REQUIREMENTS:
- Position Level: {job_data.get('position_level', 'N/A')}
- Experience Required: {job_data.get('min_years_experience', 'N/A')}
- Education Level: {job_data.get('min_education_level', 'N/A')}
- Work Arrangement: {job_data.get('work_arrangement', 'N/A')}
- Required Skills: {', '.join(job_data.get('required_skills', [])[:6])}
- Job Description: {(job_data.get('description') or job_data.get('keywords', ''))[:300]}...

INSTRUCTIONS:
1. Write a professional, engaging cover letter (300-400 words)
2. Highlight relevant skills and experience matches
3. Show enthusiasm for the specific role and company
4. Include specific achievements or capabilities
5. End with a strong call to action
6. Use professional but personable tone
7. Avoid generic phrases - make it specific to this application

Format as plain text paragraphs."""

            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are an expert career writer who creates compelling, personalized cover letters that get results. Write engaging, specific cover letters that showcase the applicant's unique value."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content.strip()
            print(f"✅ Generated AI cover letter ({len(cover_letter)} characters)")
            return cover_letter
            
        except Exception as e:
            print(f"⚠️ AI cover letter generation failed: {e}")
            return self._generate_template_cover_letter(profile_data, job_data)
    
    def _generate_template_cover_letter(self, profile_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate template cover letter when AI is not available"""
        user_name = profile_data.get('name', 'Professional')
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company_name') or job_data.get('company', 'Your Company')
        
        return f"""Dear Hiring Manager at {company},

I am writing to express my strong interest in the {job_title} position. With my background in {profile_data.get('title', 'technology')} and proven experience in {profile_data.get('experience_level', 'professional development')}, I am confident I would be a valuable addition to your team.

Throughout my career, I have developed expertise in key areas that align with your requirements. My technical skills include {', '.join([skill.get('skill_name', skill) if isinstance(skill, dict) else str(skill) for skill in (profile_data.get('skills', [])[:4])])}, which directly match the requirements for this role.

I am particularly drawn to this opportunity because it combines my passion for {profile_data.get('title', 'technology')} with my desire to contribute to a forward-thinking organization like {company}. My experience has taught me the importance of {profile_data.get('summary', 'continuous learning and professional excellence')}.

I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's success. Thank you for considering my application.

Sincerely,
{user_name}"""
    
    def generate_application_pdf(self, profile_data: Dict[str, Any], job_data: Dict[str, Any]) -> bytes:
        """Generate complete job application PDF"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Create styles
        styles = self.create_styles()
        story = []
        
        # Header with SkillsMatch.AI branding
        story.append(Paragraph("SkillsMatch.AI", styles['CustomTitle']))
        story.append(Paragraph("Professional Job Application", styles['CustomSmall']))
        story.append(Spacer(1, 12))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=2, color=self.colors['primary']))
        story.append(Spacer(1, 20))
        
        # Applicant Information
        story.append(Paragraph("APPLICANT INFORMATION", styles['CustomHeader']))
        
        applicant_info = [
            ['Name:', profile_data.get('name', 'N/A')],
            ['Title:', profile_data.get('title', 'N/A')],
            ['Location:', profile_data.get('location', 'N/A')],
            ['Experience Level:', profile_data.get('experience_level', 'N/A').title()],
            ['Application Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        applicant_table = Table(applicant_info, colWidths=[2*inch, 4*inch])
        applicant_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['secondary']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(applicant_table)
        story.append(Spacer(1, 20))
        
        # Job Information
        story.append(Paragraph("TARGET POSITION", styles['CustomHeader']))
        
        # Handle job categories (JSON array)
        job_categories = job_data.get('job_category', [])
        if isinstance(job_categories, list) and job_categories:
            category_text = ', '.join([str(cat) for cat in job_categories[:3]])  # Show first 3 categories
        else:
            category_text = job_data.get('category', 'General')
        
        # Handle employment type (JSON array)
        employment_types = job_data.get('employment_type', [])
        if isinstance(employment_types, list) and employment_types:
            employment_text = ', '.join([str(emp) for emp in employment_types])
        else:
            employment_text = 'Full-time'
        
        job_info = [
            ['Position:', job_data.get('title', 'N/A')],
            ['Company:', job_data.get('company_name', job_data.get('company', 'Various Companies'))],
            ['Category:', category_text],
            ['Employment Type:', employment_text],
            ['Position Level:', job_data.get('position_level', 'N/A')],
            ['Work Arrangement:', job_data.get('work_arrangement', 'N/A')],
            # Match score removed per user request
            # ['Match Score:', f"{job_data.get('match_percentage', 0):.1f}%"]
        ]
        
        # Add salary information if available
        salary_info = []
        if job_data.get('min_salary') or job_data.get('max_salary'):
            min_sal = job_data.get('min_salary', 0)
            max_sal = job_data.get('max_salary', 0)
            currency = job_data.get('currency', 'SGD')
            salary_interval = job_data.get('salary_interval', 'Monthly')
            
            if min_sal and max_sal:
                salary_text = f"{currency} {min_sal:,} - {max_sal:,} ({salary_interval})"
            elif min_sal:
                salary_text = f"{currency} {min_sal:,}+ ({salary_interval})"
            elif max_sal:
                salary_text = f"Up to {currency} {max_sal:,} ({salary_interval})"
            else:
                salary_text = 'Competitive'
            
            salary_info.append(['Salary Range:', salary_text])
        
        # Add location information
        if job_data.get('address'):
            salary_info.append(['Location:', job_data.get('address', 'Singapore')])
        elif job_data.get('postal_code'):
            salary_info.append(['Location:', f"Singapore {job_data.get('postal_code')}"])
        
        # Add MRT information if available
        nearest_mrt = job_data.get('nearest_mrt_station', [])
        if isinstance(nearest_mrt, list) and nearest_mrt:
            mrt_text = ', '.join([str(mrt) for mrt in nearest_mrt[:2]])  # Show first 2 MRT stations
            salary_info.append(['Nearest MRT:', mrt_text])
        
        # Combine job info with salary/location info
        all_job_info = job_info + salary_info
        
        job_table = Table(all_job_info, colWidths=[2*inch, 4*inch])
        job_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['secondary']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(job_table)
        story.append(Spacer(1, 20))
        
        # Job Requirements Section
        story.append(Paragraph("JOB REQUIREMENTS", styles['CustomHeader']))
        
        requirements_info = []
        if job_data.get('min_years_experience'):
            requirements_info.append(['Experience Required:', job_data.get('min_years_experience', 'N/A')])
        if job_data.get('min_education_level'):
            requirements_info.append(['Education Level:', job_data.get('min_education_level', 'N/A')])
        if job_data.get('no_of_vacancies'):
            requirements_info.append(['Number of Openings:', str(job_data.get('no_of_vacancies', 1))])
        
        # Add timing/shift information
        timing_shift = job_data.get('timing_shift', [])
        if isinstance(timing_shift, list) and timing_shift:
            shift_text = ', '.join([str(shift) for shift in timing_shift])
            requirements_info.append(['Working Hours:', shift_text])
        
        if requirements_info:
            req_table = Table(requirements_info, colWidths=[2*inch, 4*inch])
            req_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), self.colors['secondary']),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(req_table)
            story.append(Spacer(1, 15))
        
        # Company Information (if available)
        if job_data.get('company_description') or job_data.get('website'):
            story.append(Paragraph("COMPANY INFORMATION", styles['CustomHeader']))
            
            if job_data.get('website'):
                story.append(Paragraph(f"Website: {job_data.get('website')}", styles['CustomBody']))
                story.append(Spacer(1, 5))
            
            if job_data.get('company_description'):
                # Truncate long company descriptions
                desc = job_data.get('company_description', '')
                if len(desc) > 500:
                    desc = desc[:500] + '...'
                story.append(Paragraph(desc, styles['CustomBody']))
                story.append(Spacer(1, 15))
        
        # Cover Letter
        story.append(Paragraph("COVER LETTER", styles['CustomHeader']))
        cover_letter = self.generate_ai_cover_letter(profile_data, job_data)
        
        # Split cover letter into paragraphs
        paragraphs = cover_letter.strip().split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['CustomBody']))
                story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 20))
        
        # Skills Summary
        story.append(Paragraph("SKILLS SUMMARY", styles['CustomHeader']))
        
        skills = []
        if profile_data.get('skills'):
            for skill in profile_data['skills']:
                if isinstance(skill, dict):
                    skill_name = skill.get('skill_name', '')
                else:
                    skill_name = str(skill)
                if skill_name:
                    skills.append(skill_name)
        
        if skills:
            # Create skills table (2 columns)
            skills_data = []
            for i in range(0, len(skills), 2):
                row = [skills[i] if i < len(skills) else '', 
                       skills[i+1] if i+1 < len(skills) else '']
                skills_data.append(row)
            
            skills_table = Table(skills_data, colWidths=[3*inch, 3*inch])
            skills_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text']),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ]))
            story.append(skills_table)
        else:
            story.append(Paragraph("Skills information not available", styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Match Analysis (if available)
        if job_data.get('matched_skills') or job_data.get('missing_skills'):
            story.append(Paragraph("MATCH ANALYSIS", styles['CustomHeader']))
            
            if job_data.get('matched_skills'):
                story.append(Paragraph("Matching Skills:", styles['CustomSubHeader']))
                matched_text = ', '.join(job_data['matched_skills'][:10])
                story.append(Paragraph(matched_text, styles['CustomBody']))
                story.append(Spacer(1, 8))
            
            if job_data.get('missing_skills'):
                story.append(Paragraph("Skills to Develop:", styles['CustomSubHeader']))
                missing_text = ', '.join(job_data['missing_skills'][:8])
                story.append(Paragraph(missing_text, styles['CustomBody']))
                story.append(Spacer(1, 8))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=self.colors['border']))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Generated by SkillsMatch.AI - Your AI-Powered Career Partner", styles['CustomSmall']))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['CustomSmall']))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _get_rating(self, score):
        """Get rating based on score"""
        if score >= 80: return "⭐⭐⭐⭐⭐ Excellent"
        elif score >= 70: return "⭐⭐⭐⭐ Very Good"
        elif score >= 60: return "⭐⭐⭐ Good"
        elif score >= 50: return "⭐⭐ Fair"
        else: return "⭐ Needs Improvement"
    
    def _get_score_analysis(self, score):
        """Get analysis text based on score"""
        if score >= 80: return "Outstanding match - Highly recommended"
        elif score >= 70: return "Strong alignment - Great opportunity"
        elif score >= 60: return "Good fit with growth potential"
        elif score >= 50: return "Moderate match - Consider skills gap"
        else: return "Limited alignment - Significant upskilling needed"

# Global instance
pdf_generator = SkillsMatchPDFGenerator()

def get_pdf_generator() -> SkillsMatchPDFGenerator:
    """Get the global PDF generator instance"""
    return pdf_generator