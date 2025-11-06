"""
SkillsMatch.AI Flask Web Application

A modern web interface for the SkillsMatch.AI career matching system
with real-time features, beautiful UI, and comprehensive functionality.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Check conda environment on startup
def check_conda_environment():
    """Check if we're running in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'smai':
        print("⚠️  WARNING: Not running in 'smai' conda environment!")
        print(f"📍 Current environment: {conda_env or 'base'}")
        print("🔧 To fix this, activate the environment first:")
        print("   conda activate smai")
        print("   python app.py")
        print("")
    else:
        print(f"✅ Running in correct conda environment: {conda_env}")

# Check environment on import
check_conda_environment()

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
# import eventlet  # Commented out due to SSL issue

# AI imports
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import storage layer
try:
    from web.storage import profile_manager
except ImportError:
    # Fallback for when running from web directory
    from storage import profile_manager

# Debug: Check if API keys are loaded
openai_key = os.environ.get('OPENAI_API_KEY')
github_token = os.environ.get('GITHUB_TOKEN')

if openai_key:
    print(f"✅ OpenAI API key loaded from .env (length: {len(openai_key)} characters)")
    print("🚀 Using latest OpenAI models: GPT-4o, GPT-4 Turbo (including ChatGPT Pro models)")
    if github_token:
        print("🔄 GitHub token also available as fallback")
elif github_token:
    print(f"✅ GitHub token loaded from .env (length: {len(github_token)} characters)")
    print("🚀 Using GitHub Copilot Pro models: GPT-5, O1, DeepSeek-R1")
else:
    print("❌ No AI API keys found - will use enhanced basic matching")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def parse_datetime(date_str):
    """Parse datetime string from database into datetime object"""
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        # Handle ISO format: 2025-11-02T15:52:15.200314
        return datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
    except (ValueError, AttributeError):
        return None

# Try to import SkillMatch modules with graceful error handling
try:
    # First try importing the models and utilities (less likely to have OpenAI issues)
    from skillmatch.models import UserProfile, SkillItem, ExperienceLevel, UserPreferences, PreferenceType
    from skillmatch.utils import DataLoader, SkillMatcher
    
    # Then try importing the agent (more likely to have OpenAI compatibility issues)
    try:
        from skillmatch import SkillMatchAgent
        print("✅ SkillMatch core modules loaded successfully")
    except Exception as agent_error:
        print(f"⚠️  SkillMatch agent not available (OpenAI compatibility issue): {agent_error}")
        SkillMatchAgent = None
    
    SKILLMATCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SkillMatch core modules not available: {e}")
    SkillMatchAgent = None
    UserProfile = None
    SkillItem = None
    ExperienceLevel = None
    UserPreferences = None
    PreferenceType = None
    DataLoader = None
    SkillMatcher = None
    SKILLMATCH_AVAILABLE = False

# Scraping functionality removed - using direct API access instead
SCRAPER_AVAILABLE = False

# AI Summary Generation Function
def generate_ai_summary(profile_data):
    """Generate AI summary for profile using OpenAI"""
    if not openai or not openai_key or not OpenAI:
        return None
    
    try:
        # Set up OpenAI client (new API format)
        client = OpenAI(api_key=openai_key)
        
        # Extract key information from profile
        name = profile_data.get('name', 'Professional')
        location = profile_data.get('location', 'Singapore')
        experience_level = profile_data.get('experience_level', 'entry')
        
        # Extract skills (handle malformed data)
        skills = []
        for skill in profile_data.get('skills', []):
            if isinstance(skill, dict) and 'skill_name' in skill:
                skill_name = skill['skill_name']
                if skill_name.startswith('["') and skill_name.endswith('"]'):
                    # Parse malformed JSON string
                    skill_list = skill_name[2:-2].split('","')
                    skills.extend(skill_list)
                else:
                    skills.append(skill_name)
            else:
                skills.append(str(skill))
        
        # Extract work experience
        work_exp = profile_data.get('work_experience', [])
        current_role = work_exp[0] if work_exp else None
        
        # Extract education
        education = profile_data.get('education', [])
        highest_education = education[0] if education else None
        
        # Try to read resume content for additional context
        resume_content = ""
        resume_file = profile_data.get('resume_file')
        if resume_file:
            try:
                # For now, we'll use the filename as context since PDF parsing is complex
                # In a production system, you'd use a PDF parser like PyPDF2 or pdfplumber
                resume_content = f"Has resume: {resume_file}"
            except Exception as e:
                print(f"Could not read resume file: {e}")
        
        # Create prompt for AI summary
        # Build detailed context
        context_details = []
        if current_role:
            years_exp = current_role.get('years', 0)
            context_details.append(f"{years_exp} years experience as {current_role.get('position')} at {current_role.get('company')}")
        if highest_education:
            context_details.append(f"{highest_education.get('degree')} in {highest_education.get('field_of_study')} from {highest_education.get('institution')}")
        if resume_content:
            context_details.append(resume_content)

        # Build comprehensive work description
        work_description = ""
        if current_role:
            work_description = f"Currently works as {current_role.get('position')} at {current_role.get('company')} with {current_role.get('years', 0)} years of experience"
            if current_role.get('description'):
                work_description += f", specializing in {current_role.get('description')}"
        
        # Build education description
        education_description = ""
        if highest_education:
            education_description = f"Holds a {highest_education.get('degree')} in {highest_education.get('field_of_study')} from {highest_education.get('institution')}"
        
        prompt = f"""Write a compelling professional summary for {name}.

Profile Details:
- Location: {location}
- Experience Level: {experience_level}
- Primary Skills: {', '.join(skills[:5]) if skills else 'Various technical skills'}
- Work Experience: {work_description if work_description else 'Building professional experience'}
- Education: {education_description if education_description else 'Continuing professional development'}
- Career Focus: Looking for opportunities in {location} with skills in {', '.join(skills[:3]) if skills else 'technology'}

Create a professional, engaging summary that highlights their unique value proposition, technical expertise, and career potential. Make it sound accomplished and forward-looking. Keep it under 280 characters but make every word count."""

        # Call OpenAI API with ChatGPT Pro models (new format)
        print(f"Generating AI summary for {name}...")  # Debug log
        
        # Try ChatGPT Pro models first, then fallback
        models_to_try = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert career writer who creates compelling professional summaries. Write engaging, accomplished-sounding summaries that showcase the person's expertise and potential. Use dynamic language and focus on achievements and capabilities."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=120,
                    temperature=0.8
                )
                
                summary = response.choices[0].message.content.strip()
                print(f"✅ Generated AI summary using {model}: {summary[:50]}...")
                return summary
                
            except Exception as model_error:
                print(f"⚠️ Model {model} failed: {model_error}")
                continue
        
        # If all models fail
        print("❌ All AI models failed for summary generation")
        return None
        
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        print(f"OpenAI available: {openai is not None}")
        print(f"OpenAI key available: {openai_key is not None}")
        return None

# Initialize Flask app with production configuration
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'skillmatch-production-key-change-me')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['TEMPLATES_AUTO_RELOAD'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Domain configuration - using localhost for development
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', None)  # Set in production
app.config['PREFERRED_URL_SCHEME'] = 'http' if os.environ.get('FLASK_ENV') != 'production' else 'https'

# CORS configuration - allow localhost for development
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000,http://localhost:5001,http://127.0.0.1:5001').split(',')
CORS(app, origins=cors_origins if os.environ.get('FLASK_ENV') == 'production' else "*")

# Initialize SocketIO with production settings
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins if os.environ.get('FLASK_ENV') == 'production' else "*",
    async_mode='threading',  # Using threading instead of eventlet
    logger=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
    engineio_logger=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
)

# Global variables
data_loader = None
skill_matcher = None
current_agent = None


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config = {}
    
    # Try to load from config file
    config_path = Path("../config/config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Override with environment variables
    if "GITHUB_TOKEN" in os.environ:
        config["github_token"] = os.environ["GITHUB_TOKEN"]
    
    return config


def initialize_data():
    """Initialize data loader and skill matcher"""
    global data_loader, skill_matcher
    
    if not SKILLMATCH_AVAILABLE:
        print("SkillMatch modules not available - using mock data")
        data_loader = None
        skill_matcher = None
        return False
    
    try:
        data_loader = DataLoader(
            skills_db_path="../data/skills_database.json",
            opportunities_db_path="../data/opportunities_database.json"
        )
        skill_matcher = SkillMatcher(data_loader.skills_data)
        return True
    except Exception as e:
        print(f"Error initializing data: {e}")
        data_loader = None
        skill_matcher = None
        return False


@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    
    # Get database statistics
    stats = {
        'skills_categories': 0,
        'total_opportunities': 0,
        'last_scrape': 'Never',
        'github_configured': bool(config.get('github_token'))
    }
    
    if data_loader:
        if hasattr(data_loader, 'skills_data') and data_loader.skills_data:
            stats['skills_categories'] = len(data_loader.skills_data.get('skills', {}))
        
        if hasattr(data_loader, 'opportunities_data') and data_loader.opportunities_data:
            stats['total_opportunities'] = len(data_loader.opportunities_data.get('opportunities', []))
    
    # Check for last scrape date
    scraped_data_dir = Path("../scraped_data")
    if scraped_data_dir.exists():
        scrape_files = list(scraped_data_dir.glob("*_raw_*.json"))
        if scrape_files:
            latest_scrape = max(scrape_files, key=lambda p: p.stat().st_mtime)
            stats['last_scrape'] = datetime.fromtimestamp(latest_scrape.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    
    # Get profiles data for analytics
    profiles_dir = Path(__file__).parent.parent / "profiles"
    profile_files = []
    
    if profiles_dir.exists():
        for profile_file in profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    profile_files.append(profile_data)
            except Exception as e:
                print(f"Error loading profile {profile_file}: {e}")
    
    return render_template('index.html', stats=stats, profiles=profile_files)


@app.route('/profiles')
def profiles():
    """Profile management page"""
    try:
        # Use the profile manager for storage abstraction
        profiles_data = profile_manager.list_profiles()
        profile_files = []
        
        for profile_data in profiles_data:
            # Create profile object with enhanced data structure
            profile_obj = {
                'id': profile_data.get('user_id', profile_data.get('name', 'unknown')),
                'filename': f"{profile_data.get('user_id', profile_data.get('name', 'unknown'))}.json",
                'name': profile_data.get('name', 'Unknown'),
                'email': profile_data.get('email', ''),
                'title': profile_data.get('title', 'No title'),
                'experience_level': profile_data.get('experience_level', 'not_specified'),
                'skills': profile_data.get('skills', []),
                'industries': profile_data.get('industries', []),
                'location': profile_data.get('location', ''),
                'resume_file': profile_data.get('resume_file'),
                'skills_count': len(profile_data.get('skills', [])),
                'experience_years': sum(exp.get('years', 0) or 0 for exp in profile_data.get('work_experience', [])),
                'created_at': parse_datetime(profile_data.get('created_at')) or datetime.now(),
                'modified': parse_datetime(profile_data.get('updated_at')) or datetime.now()
            }
            profile_files.append(profile_obj)
            
        # Sort profiles by name
        profile_files.sort(key=lambda x: x['name'].lower())
            
        # Show storage info
        storage_info = profile_manager.get_storage_info()
        print(f"✅ Using {storage_info['type']} storage for profiles")
            
    except Exception as e:
        print(f"Error loading profiles: {e}")
        profile_files = []
    
    return render_template('profiles.html', profiles=profile_files)


@app.route('/profile/create')
def create_profile():
    """Profile creation form"""
    # Get available skills for the form
    skills_data = []
    if data_loader and data_loader.skills_data:
        for category, category_data in data_loader.skills_data.get('skills', {}).items():
            for skill_id, skill_info in category_data.get('skills', {}).items():
                skills_data.append({
                    'id': skill_id,
                    'name': skill_info.get('name', skill_id),
                    'category': category_data.get('category_name', category)
                })
    
    return render_template('create_profile.html', available_skills=skills_data)


@app.route('/profile/save', methods=['POST'])
def save_profile():
    """Save user profile (create new or update existing)"""
    try:
        # Check if this is an edit operation
        edit_profile_id = request.form.get('edit_profile_id')
        is_editing = bool(edit_profile_id)
        
        # Get form data
        profile_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'title': request.form.get('title'),
            'location': request.form.get('location'),
            'bio': request.form.get('bio'),
            'goals': request.form.get('goals', ''),
            'summary': request.form.get('summary', ''),
            'skills': [],
            'work_experience': [],
            'education': [],
            'preferences': {
                'work_types': [request.form.get('work_type')] if request.form.get('work_type') else [],
                'locations': [request.form.get('location')] if request.form.get('location') else [],
                'industries': json.loads(request.form.get('industries', '[]')) if request.form.get('industries') else [],
                'salary_min': int(float(request.form.get('salary_min'))) if request.form.get('salary_min') and request.form.get('salary_min').strip() else None,
                'salary_max': int(float(request.form.get('salary_max'))) if request.form.get('salary_max') and request.form.get('salary_max').strip() else None,
                'remote_preference': request.form.get('remote_preference', 'hybrid')
            }
        }
        
        # If editing, preserve existing resume_file unless new one is uploaded
        existing_resume_file = None
        if is_editing:
            existing_data = profile_manager.load_profile(edit_profile_id)
            if existing_data:
                existing_resume_file = existing_data.get('resume_file')
        
        profile_data['resume_file'] = existing_resume_file
        
        # Set experience level - prefer direct selection over calculated from years
        profile_data['experience_level'] = request.form.get('experience_level', 'entry')
        
        # Process skills
        skills_raw = request.form.get('skills', '[]')
        try:
            # Try to parse as JSON first (from the new form)
            selected_skills = json.loads(skills_raw) if skills_raw else []
        except json.JSONDecodeError:
            # Fallback to old way if JSON parsing fails
            selected_skills = request.form.getlist('skills')
        
        for skill_id in selected_skills:
            skill_level = request.form.get(f'skill_level_{skill_id}', 'intermediate')
            skill_years = int(float(request.form.get(f'skill_years_{skill_id}', 1)))
            
            # Find skill info
            skill_name = skill_id
            skill_category = 'other'
            
            if data_loader and data_loader.skills_data:
                for category, category_data in data_loader.skills_data.get('skills', {}).items():
                    if skill_id in category_data.get('skills', {}):
                        skill_name = category_data['skills'][skill_id].get('name', skill_id)
                        skill_category = category
                        break
            
            profile_data['skills'].append({
                'skill_id': skill_id,
                'skill_name': skill_name,
                'category': skill_category,
                'level': skill_level,
                'years_experience': skill_years
            })
        
        # Add work experience if provided
        if request.form.get('job_title'):
            profile_data['work_experience'].append({
                'position': request.form.get('job_title'),
                'company': request.form.get('company'),
                'years': int(float(request.form.get('experience_years'))) if request.form.get('experience_years') and request.form.get('experience_years').strip() else 0,
                'description': request.form.get('job_description', ''),
                'employment_status': request.form.get('employment_status', ''),
                'key_skills': selected_skills
            })
        
        # Add education if provided
        if request.form.get('degree'):
            profile_data['education'].append({
                'degree': request.form.get('degree'),
                'institution': request.form.get('institution'),
                'graduation_year': int(float(request.form.get('graduation_year'))) if request.form.get('graduation_year') and request.form.get('graduation_year').strip() else datetime.now().year,
                'field_of_study': request.form.get('field_of_study', '')
            })
        
        # Handle resume upload (replace existing if new file uploaded)
        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file and resume_file.filename and resume_file.filename.endswith('.pdf'):
                # Create uploads directory
                uploads_dir = Path(__file__).parent.parent / "uploads" / "resumes"
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                # If editing and old resume exists, delete it first
                if is_editing and existing_resume_file:
                    old_resume_path = uploads_dir / existing_resume_file
                    if old_resume_path.exists():
                        old_resume_path.unlink()
                        print(f"Deleted old resume: {existing_resume_file}")
                
                # Generate filename (one resume per profile)
                resume_filename = f"{profile_data['name'].lower().replace(' ', '_')}_resume.pdf"
                resume_path = uploads_dir / resume_filename
                
                # Save the new file
                resume_file.save(str(resume_path))
                profile_data['resume_file'] = resume_filename
                print(f"Saved new resume: {resume_filename}")
                
                # Generate AI summary from PDF if no existing summary
                if not profile_data.get('summary'):
                    try:
                        from .utils.pdf_extractor import extract_resume_text
                        from .utils.ai_summarizer import generate_profile_summary
                        
                        print("🔍 Analyzing PDF for professional summary...")
                        
                        # Extract text from PDF
                        pdf_result = extract_resume_text(str(resume_path))
                        
                        if pdf_result['success']:
                            print(f"✅ PDF text extracted ({pdf_result['word_count']} words)")
                            
                            # Generate AI summary
                            summary_result = generate_profile_summary(
                                pdf_result['text'], 
                                profile_data
                            )
                            
                            if summary_result['success']:
                                profile_data['summary'] = summary_result['summary']
                                print(f"✅ AI summary generated using {summary_result['model_used']}")
                                print(f"📝 Summary: {summary_result['summary'][:100]}...")
                            else:
                                print(f"⚠️ AI summary generation failed: {summary_result['error']}")
                        else:
                            print(f"⚠️ PDF text extraction failed: {pdf_result['error']}")
                            
                    except Exception as e:
                        print(f"⚠️ PDF analysis error (continuing without summary): {e}")
        
        # Save profile
        profiles_dir = Path(__file__).parent.parent / "profiles"
        profiles_dir.mkdir(exist_ok=True)
        
        # Set profile ID for storage
        if is_editing and edit_profile_id:
            profile_data['user_id'] = edit_profile_id
        else:
            profile_data['user_id'] = profile_data['name'].lower().replace(' ', '_')
        
        # Use profile manager to save profile  
        success = profile_manager.save_profile(profile_data)
        
        if success:
            if is_editing:
                flash(f"✅ Profile '{profile_data['name']}' updated successfully!", "success")
            else:
                flash(f"🎉 Profile '{profile_data['name']}' created successfully!", "success")
        else:
            flash("❌ Error saving profile to database", "error")
        return redirect(url_for('profiles'))
        
    except Exception as e:
        flash(f"Error saving profile: {e}", "error")
        # If editing, redirect back to edit page; otherwise to create page
        if is_editing and edit_profile_id:
            return redirect(url_for('edit_profile', profile_id=edit_profile_id))
        else:
            return redirect(url_for('create_profile'))


@app.route('/profiles/<profile_id>')
def view_profile(profile_id):
    """View individual profile details"""
    try:
        # Use PostgreSQL storage instead of JSON files
        profile_data = profile_manager.load_profile(profile_id)
        
        if not profile_data:
            flash("Profile not found.", "error")
            return redirect(url_for('profiles'))
        
        # Generate AI summary from PDF if it doesn't exist
        if not profile_data.get('summary'):
            # Check if there's a PDF resume file
            resume_filename = profile_data.get('resume_file')
            if resume_filename:
                try:
                    uploads_dir = Path(__file__).parent.parent / "uploads" / "resumes"
                    resume_path = uploads_dir / resume_filename
                    
                    if resume_path.exists():
                        print(f"🔍 Generating summary from PDF: {resume_filename}")
                        
                        # Extract text from PDF
                        from .utils.pdf_extractor import extract_resume_text
                        from .utils.ai_summarizer import generate_profile_summary
                        
                        pdf_result = extract_resume_text(str(resume_path))
                        
                        if pdf_result['success']:
                            print(f"✅ PDF text extracted ({pdf_result['word_count']} words)")
                            
                            # Generate AI summary from extracted text
                            summary_result = generate_profile_summary(
                                pdf_result['text'], 
                                profile_data
                            )
                            
                            if summary_result['success']:
                                profile_data['summary'] = summary_result['summary']
                                print(f"✅ AI summary generated using {summary_result['model_used']}")
                                
                                # Save the updated profile with AI summary
                                try:
                                    profile_manager.save_profile(profile_data)
                                    print("✅ Profile updated with AI summary")
                                except Exception as e:
                                    print(f"Warning: Could not save AI summary to profile: {e}")
                            else:
                                print(f"⚠️ AI summary generation failed: {summary_result['error']}")
                        else:
                            print(f"⚠️ PDF text extraction failed: {pdf_result['error']}")
                            
                    else:
                        print(f"⚠️ Resume file not found: {resume_path}")
                        
                except Exception as e:
                    print(f"⚠️ Error processing PDF resume: {e}")
            
            # Fallback to profile-based summary if no PDF or PDF processing failed
            if not profile_data.get('summary'):
                ai_summary = generate_ai_summary(profile_data)
                if ai_summary:
                    profile_data['summary'] = ai_summary
                    # Save the updated profile with AI summary
                    try:
                        profile_manager.save_profile(profile_data)
                    except Exception as e:
                        print(f"Warning: Could not save AI summary to profile: {e}")
        
        return render_template('view_profile.html', profile=profile_data, profile_id=profile_id)
        
    except Exception as e:
        flash(f"Error loading profile: {e}", "error")
        return redirect(url_for('profiles'))


@app.route('/profiles/<profile_id>/delete', methods=['POST'])
def delete_profile(profile_id):
    """Delete a profile and its associated resume file"""
    try:
        uploads_dir = Path(__file__).parent.parent / "uploads" / "resumes"
        
        # Load profile to get resume filename before deleting
        profile_data = profile_manager.load_profile(profile_id)
        
        if profile_data:
            # Delete resume file if it exists
            resume_filename = profile_data.get('resume_file')
            if resume_filename:
                resume_path = uploads_dir / resume_filename
                if resume_path.exists():
                    try:
                        resume_path.unlink()
                        print(f"Deleted resume file: {resume_filename}")
                    except Exception as e:
                        print(f"Warning: Could not delete resume file: {e}")
            
            # Delete profile from database
            success = profile_manager.delete_profile(profile_id)
            if success:
                flash("Profile and associated files deleted successfully.", "success")
            else:
                flash("Error deleting profile from database.", "error")
        else:
            flash("Profile not found.", "error")
            
    except Exception as e:
        flash(f"Error deleting profile: {e}", "error")
    
    return redirect(url_for('profiles'))


@app.route('/profiles/<profile_id>/edit')
def edit_profile(profile_id):
    """Edit profile form"""
    try:
        # Use profile manager to load profile
        profile_data = profile_manager.load_profile(profile_id)
        
        if not profile_data:
            flash("Profile not found.", "error")
            return redirect(url_for('profiles'))
            
        # Get available skills for the form
        skills_data = []
        try:
            skills_file = Path(__file__).parent.parent / "data" / "skills_database.json"
            if skills_file.exists():
                with open(skills_file, 'r') as f:
                    skills_db = json.load(f)
                    skills_data = skills_db.get('skills', [])
        except Exception as e:
            print(f"Warning: Could not load skills database: {e}")
            
        return render_template('create_profile.html', profile=profile_data, skills=skills_data, edit_mode=True)
        
    except Exception as e:
        flash(f"Error loading profile for editing: {e}", "error")
        return redirect(url_for('profiles'))


@app.route('/profiles/<profile_id>/resume/download')
def download_resume(profile_id):
    """Download resume file from PostgreSQL storage"""
    try:
        # Get profile data from PostgreSQL
        profile_data = profile_manager.load_profile(profile_id)
        
        if not profile_data:
            flash("Profile not found.", "error")
            return redirect(url_for('profiles'))
            
        resume_filename = profile_data.get('resume_file')
        if not resume_filename:
            flash("No resume file found for this profile.", "error")
            return redirect(url_for('view_profile', profile_id=profile_id))
            
        # Check uploads directory
        uploads_dir = Path(__file__).parent.parent / "uploads" / "resumes" 
        resume_path = uploads_dir / resume_filename
        
        if not resume_path.exists():
            flash("Resume file not found on server.", "error")
            return redirect(url_for('view_profile', profile_id=profile_id))
            
        print(f"📥 Downloading resume: {resume_filename} for {profile_data.get('name', 'Unknown')}")
        
        from flask import send_file
        return send_file(
            resume_path,
            as_attachment=True,
            download_name=f"{profile_data.get('name', 'profile').replace(' ', '_')}_resume.pdf"
        )
        
    except Exception as e:
        print(f"Resume download error: {e}")
        flash(f"Error downloading resume: {e}", "error")
        return redirect(url_for('profiles'))


@app.route('/match')
def match_page():
    """Job matching page"""
    try:
        # Use PostgreSQL storage to get profiles
        available_profiles = []
        profiles = profile_manager.list_profiles()
        
        for profile_data in profiles:
            # Format skills for display
            skill_names = []
            if profile_data.get('skills'):
                skill_names = [skill.get('skill_name', '') for skill in profile_data['skills'] if skill.get('skill_name')]
            
            available_profiles.append({
                'id': profile_data['user_id'],
                'name': profile_data.get('name', 'Unknown'),
                'title': profile_data.get('title', 'No title'),
                'location': profile_data.get('location', ''),
                'experience_level': profile_data.get('experience_level', 'entry'),
                'skills': skill_names
            })
        
        return render_template('match.html', profiles=available_profiles)
        
    except Exception as e:
        print(f"Error loading profiles for matching: {e}")
        return render_template('match.html', profiles=[])


@app.route('/api/match', methods=['POST'])
def api_match():
    """Enhanced API endpoint for AI-powered job matching"""
    try:
        data = request.get_json()
        profile_id = data.get('profile_id')
        use_ai = data.get('use_ai', True)  # Default to AI matching
        
        if not profile_id:
            return jsonify({'error': 'Profile ID is required'}), 400
        
        # Load profile from PostgreSQL
        profile_data = profile_manager.load_profile(profile_id)
        if not profile_data:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Load opportunities from JSON file
        opportunities_path = Path(__file__).parent.parent / "data" / "opportunities_database.json"
        if not opportunities_path.exists():
            return jsonify({'error': 'Opportunities database not found'}), 500
        
        with open(opportunities_path, 'r') as f:
            opportunities_data = json.load(f)
        
        opportunities = opportunities_data.get('opportunities', [])
        
        if use_ai:
            # Try advanced AI matching first
            try:
                from .utils.ai_matcher import get_ai_job_matches
                import asyncio
                
                print(f"🤖 Using AI-powered matching for {profile_data.get('name', 'user')}")
                
                # Run AI matching
                ai_matches = asyncio.run(get_ai_job_matches(profile_data, opportunities))
                
                if ai_matches:
                    return jsonify({
                        'status': 'success',
                        'matching_type': 'ai_powered',
                        'model_used': ai_matches[0].get('model_used', 'advanced') if ai_matches else 'fallback',
                        'profile_name': profile_data.get('name', 'Unknown'),
                        'profile_title': profile_data.get('title', ''),
                        'profile_location': profile_data.get('location', ''),
                        'total_matches': len(ai_matches),
                        'matches': ai_matches[:20]  # Top 20 AI matches
                    }), 200
                else:
                    print("⚠️ AI matching returned no results, falling back to enhanced basic")
                    use_ai = False
                    
            except ImportError as ie:
                print(f"⚠️ AI matcher not available: {ie}")
                use_ai = False
            except Exception as ai_error:
                print(f"⚠️ AI matching failed, falling back to enhanced basic: {ai_error}")
                use_ai = False
        
        if not use_ai:
            # Enhanced basic matching algorithm
            print(f"📊 Using enhanced basic matching for {profile_data.get('name', 'user')}")
            
            matches = []
            user_skills = profile_data.get('skills', [])
            user_skill_names = [skill.get('skill_name', '').lower() for skill in user_skills if skill.get('skill_name')]
            user_location = profile_data.get('location', '').lower()
            user_experience_level = profile_data.get('experience_level', 'entry').lower()
            
            for opportunity in opportunities:
                # Calculate skill match score
                required_skills = opportunity.get('required_skills', [])
                preferred_skills = opportunity.get('preferred_skills', [])
                all_opp_skills = required_skills + preferred_skills
                
                skill_matches = 0
                total_skill_weight = 0
                skill_gaps = []
                strengths = []
                
                for req_skill in all_opp_skills:
                    skill_name = req_skill.get('skill_name', '').lower()
                    importance = req_skill.get('importance', 0.5)
                    required_level = req_skill.get('required_level', 'beginner')
                    is_mandatory = req_skill.get('is_mandatory', False)
                    
                    total_skill_weight += importance
                    
                    # Check if user has this skill
                    user_has_skill = any(skill_name in user_skill.lower() for user_skill in user_skill_names)
                    
                    if user_has_skill:
                        skill_matches += importance
                        strengths.append(f"Has {req_skill.get('skill_name', skill_name)}")
                    else:
                        skill_gaps.append({
                            'skill_name': req_skill.get('skill_name', skill_name),
                            'required_level': required_level,
                            'importance': round(importance * 100, 1),
                            'is_mandatory': is_mandatory
                        })
                
                # Calculate scores
                skill_score = (skill_matches / total_skill_weight * 100) if total_skill_weight > 0 else 0
                
                # Location match bonus
                location_score = 50  # Base score
                opp_location = opportunity.get('location', '').lower()
                if user_location and opp_location:
                    if user_location in opp_location or opp_location in user_location:
                        location_score = 100
                    elif 'singapore' in user_location and 'singapore' in opp_location:
                        location_score = 90
                
                # Experience level match
                experience_score = 50  # Base score
                opp_exp = opportunity.get('experience_level', 'entry').lower()
                if user_experience_level == opp_exp:
                    experience_score = 100
                elif (user_experience_level == 'senior' and opp_exp in ['intermediate', 'mid']) or \
                     (user_experience_level == 'intermediate' and opp_exp == 'entry'):
                    experience_score = 80
                
                # Overall score (weighted average)
                overall_score = (skill_score * 0.6 + location_score * 0.2 + experience_score * 0.2)
                
                # Only include opportunities with reasonable matches
                if overall_score >= 30:  # Minimum threshold
                    company_name = opportunity.get('company', {}).get('name', 'Unknown Company') if isinstance(opportunity.get('company'), dict) else opportunity.get('company', 'Unknown Company')
                    
                    matches.append({
                        'opportunity_id': opportunity.get('opportunity_id', ''),
                        'title': opportunity.get('title', 'Unknown Position'),
                        'company': company_name,
                        'location': opportunity.get('location', 'Not specified'),
                        'type': opportunity.get('opportunity_type', 'job'),
                        'overall_score': round(overall_score, 1),
                        'skill_score': round(skill_score, 1),
                        'location_score': round(location_score, 1),
                        'experience_score': round(experience_score, 1),
                        'strengths': strengths[:5],  # Top 5 strengths
                        'skill_gaps': skill_gaps[:5],  # Top 5 gaps
                        'description': opportunity.get('description', ''),
                        'url': opportunity.get('url', ''),
                        'salary_range': opportunity.get('salary_range', {}),
                        'requirements': [skill.get('skill_name', '') for skill in required_skills[:5]],
                        'match_explanation': f"Matched {len(strengths)} key requirements with {round(skill_score, 1)}% skill alignment",
                        'next_steps': ['Review job description thoroughly', 'Tailor resume to highlight matching skills', 'Research company culture and values']
                    })
            
            # Sort by overall score
            matches.sort(key=lambda x: x['overall_score'], reverse=True)
            
            return jsonify({
                'status': 'success',
                'matching_type': 'enhanced_basic',
                'profile_name': profile_data.get('name'),
                'profile_title': profile_data.get('title', ''),
                'profile_location': profile_data.get('location', ''),
                'total_matches': len(matches),
                'matches': matches[:20]  # Top 20 matches
            })
        
    except Exception as e:
        print(f"Match API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Matching failed: {str(e)}'}), 500


# Scraping functionality removed - using direct API access instead


@app.route('/chat')
def chat_page():
    """AI chat interface page"""
    config = load_config()
    openai_api_key = config.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
    github_token = config.get('github_token') or os.environ.get('GITHUB_TOKEN')
    
    # Consider configured if either API key is available
    ai_configured = bool(openai_api_key or github_token)
    preferred_api = "OpenAI" if openai_api_key else "GitHub" if github_token else None
    
    return render_template('chat.html', 
                         github_configured=ai_configured,  # Keep same variable name for template compatibility
                         ai_configured=ai_configured,
                         preferred_api=preferred_api)


@socketio.on('send_chat_message')
def handle_chat_message(data):
    """Handle chat messages with AI career advisor"""
    try:
        message = data.get('message', '').strip()
        chat_history = data.get('chat_history', [])
        
        if not message:
            return
        
        print(f"🤖 DEBUG: Received chat message: {message}")
        
        # Send typing indicator
        emit('chat_response', {'type': 'thinking', 'message': 'AI is thinking...'})
        
        def chat_task():
            try:
                config = load_config()
                
                # Try OpenAI API key first (preferred), then GitHub token as fallback
                openai_api_key = config.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
                github_token = config.get('github_token') or os.environ.get('GITHUB_TOKEN')
                
                if not openai_api_key and not github_token:
                    # Demo mode - provide helpful responses without AI
                    demo_responses = {
                        "hello": "👋 Hello! I'm your AI Career Advisor (Demo Mode). I can help with career guidance, skills development, and job market insights in Singapore!",
                        "career": "🚀 For career development in Singapore, I recommend exploring SkillsFuture courses and identifying in-demand skills like data analytics, digital marketing, and software development.",
                        "skills": "💡 Popular skills in Singapore's job market include: Python programming, data analysis, digital marketing, project management, and cloud computing. What area interests you?",
                        "tech": "💻 Tech careers in Singapore are booming! Consider roles in software development, data science, cybersecurity, or cloud architecture. The government supports tech skill development through various initiatives.",
                        "time": f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Singapore Time. How can I help with your career today?",
                        "default": "🤖 I'm running in demo mode. To unlock full AI capabilities, please set your GITHUB_TOKEN environment variable. Meanwhile, I can provide basic career guidance! Try asking about 'skills', 'tech careers', or 'singapore jobs'."
                    }
                    
                    # Simple keyword matching for demo
                    message_lower = message.lower()
                    response = demo_responses["default"]
                    
                    for keyword, demo_response in demo_responses.items():
                        if keyword in message_lower:
                            response = demo_response
                            break
                    
                    response += "\n\n💡 **To enable full AI chat:** Set GITHUB_TOKEN environment variable with your GitHub Personal Access Token."
                    
                    socketio.emit('chat_response', {'type': 'ai', 'message': response})
                    return
                
                # Import OpenAI client
                from openai import OpenAI
                
                # Load skills data for context
                skills_context = ""
                try:
                    skills_db_path = Path("../data/skills_database.json")
                    if skills_db_path.exists():
                        with open(skills_db_path, 'r') as f:
                            skills_data = json.load(f)
                            # Get a sample of skills for context
                            sample_skills = list(skills_data.keys())[:20]
                            skills_context = f"Available skills in database: {', '.join(sample_skills)}"
                except Exception as e:
                    print(f"Could not load skills context: {e}")
                
                # Build conversation messages
                messages = [
                    {
                        "role": "system",
                        "content": f"""You are an AI Career Advisor for SkillsMatch.AI, specializing in Singapore's job market and skills development. 

Your expertise includes:
- Career guidance and planning in Singapore
- Skills development recommendations based on MySkillsFuture.gov.sg data
- Job market insights and trends
- Interview preparation and career transitions
- Professional development advice

{skills_context}

Guidelines:
- Provide practical, actionable advice
- Reference Singapore's job market and SkillsFuture initiatives when relevant
- Be encouraging and supportive
- Ask clarifying questions when needed
- Keep responses concise but comprehensive
- Use emojis occasionally to make conversations friendly

Current context: Singapore job market, SkillsFuture ecosystem, and career development."""
                    }
                ]
                
                # Add chat history (last 10 messages to manage context)
                for hist_msg in chat_history[-10:]:
                    if hist_msg.get('sender') == 'user':
                        messages.append({"role": "user", "content": hist_msg.get('message', '')})
                    elif hist_msg.get('sender') == 'ai':
                        messages.append({"role": "assistant", "content": hist_msg.get('message', '')})
                
                # Add current user message
                messages.append({"role": "user", "content": message})
                
                # Try multiple APIs in order of preference
                api_success = False
                last_error = None
                
                # First try OpenAI API if available
                if openai_api_key and not api_success:
                    try:
                        print("🤖 DEBUG: Trying OpenAI API")
                        client = OpenAI(api_key=openai_api_key)
                        model_name = "gpt-3.5-turbo"  # Use accessible model
                        
                        # Test the API with the actual request
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            temperature=0,
                            max_tokens=1000,
                            top_p=0.95
                        )
                        
                        ai_message = response.choices[0].message.content
                        print(f"🤖 DEBUG: OpenAI API succeeded with {len(ai_message)} characters")
                        socketio.emit('chat_response', {'type': 'ai', 'message': ai_message})
                        api_success = True
                        
                    except Exception as openai_error:
                        print(f"🤖 DEBUG: OpenAI API failed: {openai_error}")
                        last_error = openai_error
                
                # If OpenAI failed, try GitHub models
                if github_token and not api_success:
                    try:
                        print("🤖 DEBUG: Trying GitHub models API")
                        client = OpenAI(
                            base_url="https://models.github.ai/inference",
                            api_key=github_token,
                        )
                        model_name = "gpt-5"  # Use GitHub models format
                        
                        # Test the API with the actual request
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            temperature=0,
                            max_tokens=1000,
                            top_p=0.95
                        )
                        
                        ai_message = response.choices[0].message.content
                        print(f"🤖 DEBUG: GitHub API succeeded with {len(ai_message)} characters")
                        socketio.emit('chat_response', {'type': 'ai', 'message': ai_message})
                        api_success = True
                        
                    except Exception as github_error:
                        print(f"🤖 DEBUG: GitHub API failed: {github_error}")
                        last_error = github_error
                
                # If both APIs failed, fall back to demo mode
                if not api_success:
                    if last_error:
                        raise last_error
                    else:
                        raise Exception("No working API available")
                
            except Exception as e:
                print(f"🤖 DEBUG: Chat error: {str(e)}")
                import traceback
                traceback.print_exc()
                
                error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                if ("403" in str(e) and "no_access" in str(e)) or ("429" in str(e) and "insufficient_quota" in str(e)) or "quota" in str(e).lower():
                    # Model access issue or quota exceeded - fallback to enhanced demo mode
                    print("🤖 DEBUG: Model access/quota issue, falling back to enhanced demo mode")
                    
                    # Enhanced demo responses based on the user's question
                    demo_responses = {
                        "time": f"🕐 The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Singapore Time.",
                        "career": "🚀 **Career Development in Singapore:**\n\n• **Tech Sector**: High demand for software developers, data scientists, and cybersecurity experts\n• **Healthcare**: Growing opportunities in digital health and eldercare\n• **Finance**: FinTech and digital banking are expanding rapidly\n• **Logistics**: Smart port technologies and supply chain optimization\n\n💡 Consider exploring SkillsFuture courses to upskill in these areas!",
                        "skills": "💼 **In-Demand Skills in Singapore 2025:**\n\n**Technical Skills:**\n• Python, JavaScript, SQL programming\n• Data analysis and visualization\n• Cloud computing (AWS, Azure)\n• Cybersecurity fundamentals\n\n**Soft Skills:**\n• Digital marketing and e-commerce\n• Project management (Agile/Scrum)\n• Cross-cultural communication\n• Problem-solving and critical thinking",
                        "default": f"🤖 **Smart Career Guidance** (Enhanced Mode)\n\nI can help you with career questions about Singapore's job market! While I don't have full AI access right now, I can provide valuable insights about:\n\n• Tech career pathways\n• In-demand skills\n• SkillsFuture opportunities\n• Industry trends\n\n**Your question:** \"{message}\"\n\nFor this query, I'd recommend researching current market trends and considering upskilling through official Singapore resources like SkillsFuture.gov.sg and MyCareersFuture.gov.sg."
                    }
                    
                    # Smart keyword matching
                    message_lower = message.lower()
                    response = demo_responses["default"]
                    
                    if any(word in message_lower for word in ["time", "what time", "current time"]):
                        response = demo_responses["time"]
                    elif any(word in message_lower for word in ["career", "job", "work", "profession"]):
                        response = demo_responses["career"] 
                    elif any(word in message_lower for word in ["skill", "learn", "study", "course"]):
                        response = demo_responses["skills"]
                    
                    response += "\n\n⚠️ **Note:** Running in enhanced demo mode due to AI model access limitations."
                    
                    socketio.emit('chat_response', {'type': 'ai', 'message': response})
                    return
                    
                elif "401" in str(e):
                    error_msg = "🔑 Authentication failed. Please check your GitHub token."
                elif "429" in str(e) or "rate limit" in str(e).lower() or "quota" in str(e).lower():
                    error_msg = "💳 OpenAI quota exceeded. Using fallback demo mode above."
                elif "network" in str(e).lower() or "connection" in str(e).lower():
                    error_msg = "🌐 Network issue. Please check your connection and try again."
                
                socketio.emit('chat_response', {'type': 'error', 'message': error_msg})
        
        # Run in background thread
        socketio.start_background_task(chat_task)
        
    except Exception as e:
        print(f"🤖 DEBUG: Chat handler error: {str(e)}")
        emit('chat_response', {'type': 'error', 'message': f'Error processing message: {str(e)}'})


# Health check endpoint for production monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'skillmatch_available': SKILLMATCH_AVAILABLE,
        'scraper_available': SCRAPER_AVAILABLE
    })

# Error handlers for production
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors gracefully"""
    # Create default stats for error pages
    config = load_config()
    stats = {
        'skills_categories': 0,
        'total_opportunities': 0,
        'last_scrape': 'Never',
        'github_configured': bool(config.get('github_token'))
    }
    return render_template('index.html', stats=stats), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create default stats for error pages
    config = load_config()
    stats = {
        'skills_categories': 0,
        'total_opportunities': 0,
        'last_scrape': 'Never',
        'github_configured': bool(config.get('github_token'))
    }
    return render_template('index.html', stats=stats), 500


if __name__ == '__main__':
    # Initialize data on startup
    initialize_data()
    
    # Production vs Development configuration
    if os.environ.get('FLASK_ENV') == 'production':
        print("🚀 Starting SkillsMatch.AI in PRODUCTION mode...")
        print("🌐 Available at: https://skillsmatch.ai")
        # In production, use a proper WSGI server like Gunicorn
        port = int(os.environ.get('PORT', 8000))
        socketio.run(app, debug=False, host='0.0.0.0', port=port)
    else:
        port = int(os.environ.get('PORT', 5003))  # Default to 5003 for local development
        print("🚀 Starting SkillsMatch.AI Web Interface in DEVELOPMENT mode...")
        print(f"🌐 Open your browser to: http://localhost:{port}")
        print("💡 Using localhost for development - no domain setup needed!")
        print("� Direct API access configured for data integration")
        socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)