# SkillMatch.AI 🎯

**Intelligent Career and Skill Matching System**

SkillMatch.AI is a comprehensive AI-powered platform that matches users with jobs, projects, and learning opportunities based on their skills, experience, and preferences. Built with Microsoft Agent Framework and powered by GitHub models.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![AI Framework](https://img.shields.io/badge/AI-Microsoft%20Agent%20Framework-purple.svg)

## ✨ Features

- 🤖 **AI-Powered Matching**: Uses advanced language models for intelligent skill and opportunity matching
- 🎯 **Multi-Type Opportunities**: Supports jobs, projects, internships, and learning opportunities
- 📊 **Comprehensive Scoring**: Detailed match scores with skill gaps and strengths analysis
- 🧠 **Smart Skill Analysis**: Identifies related skills and provides learning recommendations
- 💬 **Interactive Chat**: Natural language interface for career guidance
- 📈 **Career Planning**: Skill gap analysis and personalized learning paths
- 🔧 **Extensible**: Modular design for easy customization and extension

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token (for model access)
- Conda or virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rubyferdianto/SkillMatch.AI.git
   cd SkillMatch.AI
   ```

2. **Create and activate conda environment**
   ```bash
   conda create -n smai python=3.11
   conda activate smai
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note**: The `--pre` flag is required for the Microsoft Agent Framework as it's in preview.

4. **Set up configuration**
   ```bash
   python skillmatch.py setup
   ```
   
   You'll need to provide:
   - Your GitHub Personal Access Token ([Get one here](https://github.com/settings/tokens))
   - Preferred AI model (default: `openai/gpt-4.1-mini`)

### First Run

Try the sample profile:
```bash
python skillmatch.py match --profile profiles/john_developer.json
```

## 📖 Usage

### Command Line Interface

SkillMatch.AI provides several CLI commands:

#### 🔍 Find Matching Opportunities
```bash
# Use existing profile
python skillmatch.py match --profile profiles/john_developer.json

# Interactive profile creation
python skillmatch.py match --interactive
```

#### 📚 Analyze Skill Gaps
```bash
# General skill gap analysis
python skillmatch.py gaps --profile profiles/john_developer.json

# Target-specific analysis
python skillmatch.py gaps --profile profiles/john_developer.json --target-role "Senior Data Scientist"
```

#### 🎓 Find Learning Opportunities
```bash
# Search for specific skills
python skillmatch.py learn --skills "machine learning, deep learning" --difficulty intermediate --max-cost 500

# Free courses only
python skillmatch.py learn --skills "python, sql" --max-cost 0
```

#### 💬 Interactive Chat
```bash
python skillmatch.py chat
```

### Python API

You can also use SkillMatch.AI programmatically:

```python
import asyncio
from skillmatch import SkillMatchAgent, UserProfile

async def main():
    # Initialize the agent
    agent = SkillMatchAgent(
        github_token="your_github_token",
        model_id="openai/gpt-4.1-mini"
    )
    await agent.initialize()
    
    # Load user profile
    with open("profiles/john_developer.json", "r") as f:
        profile_data = json.load(f)
    user_profile = UserProfile(**profile_data)
    
    # Find matches
    matches = await agent.find_matching_opportunities(
        user_profile_json=json.dumps(profile_data, default=str)
    )
    
    print(matches)
    await agent.close()

# Run the async function
asyncio.run(main())
```

## 🏗️ Architecture

### Core Components

```
SkillMatch.AI/
├── src/skillmatch/
│   ├── models/              # Data models (Pydantic)
│   │   ├── user_profile.py  # User profiles and skills
│   │   └── opportunities.py # Jobs, projects, learning
│   ├── agents/              # AI agents
│   │   └── skill_match_agent.py  # Main AI agent
│   ├── utils/               # Utilities
│   │   ├── data_loader.py   # Data loading utilities
│   │   └── skill_matcher.py # Matching algorithms
│   └── cli.py              # Command line interface
├── data/                   # Data files
│   ├── skills_database.json
│   └── opportunities_database.json
├── config/                 # Configuration
├── profiles/              # Sample user profiles
└── tests/                 # Test files
```

### AI Agent Architecture

The system uses Microsoft Agent Framework with the following components:

- **SkillMatchAgent**: Main AI agent with specialized tools
- **Tools**: Function calling for specific operations
  - `find_matching_opportunities`
  - `calculate_match_score`
  - `identify_skill_gaps`
  - `get_skill_recommendations`
  - `analyze_user_strengths`
  - `search_learning_opportunities`

### Matching Algorithm

The matching algorithm considers multiple factors:

1. **Skill Compatibility** (50% weight)
   - Exact skill matches
   - Skill level comparison
   - Related skills consideration
   - Experience years bonus

2. **Experience Level** (30% weight)
   - Total years of experience
   - Role-specific experience
   - Career progression

3. **Preference Alignment** (20% weight)
   - Work type (remote/hybrid/onsite)
   - Location preferences
   - Salary expectations
   - Industry preferences

## 🎯 Skill Categories

The system organizes skills into categories:

- **Programming Languages**: Python, JavaScript, Java, C++, etc.
- **Web Development**: React, Vue.js, Node.js, Django, etc.
- **Data Science & ML**: Machine Learning, Deep Learning, Statistics, etc.
- **Database Technologies**: SQL, PostgreSQL, MongoDB, Redis, etc.
- **Cloud & DevOps**: AWS, Azure, Docker, Kubernetes, etc.
- **Soft Skills**: Leadership, Communication, Problem Solving, etc.

## 📊 Example Output

### Match Results
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Title                       ┃ Type        ┃ Company              ┃ Location        ┃ Match Score ┃ Skills Match  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Senior Python Developer    │ Job         │ TechCorp Inc         │ San Francisco   │    87.3%    │     92.1%     │
│ Data Scientist             │ Job         │ Analytics Pro        │ New York, NY    │    78.9%    │     85.4%     │
│ Machine Learning Fundamentals│ Learning   │ DataLearn Academy    │ Remote          │    65.2%    │     78.8%     │
└─────────────────────────────┴─────────────┴──────────────────────┴─────────────────┴─────────────┴───────────────┘

Top Match Details:
📋 Senior Python Developer
🏢 TechCorp Inc
📍 San Francisco, CA
📊 Overall Match: 87.3%
💡 This is an excellent match for your profile. Your skills align very well with the requirements. Your experience level meets requirements.

✓ Your Strengths:
  • Python (experienced)
  • SQL (experienced)
  • Strong in Programming Languages

📚 Skills to Develop:
  • Docker (None → beginner)
  • AWS (beginner → intermediate)
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export GITHUB_TOKEN="your_github_personal_access_token"

# Optional
export SKILLMATCH_MODEL="openai/gpt-4.1-mini"
export SKILLMATCH_CONFIG_PATH="config/config.json"
```

### Configuration File

Create `config/config.json`:

```json
{
  "github_token": "your_github_token",
  "model_id": "openai/gpt-4.1-mini",
  "skills_db_path": "data/skills_database.json",
  "opportunities_db_path": "data/opportunities_database.json"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/skillmatch
```

## 📈 Extending SkillMatch.AI

### Adding New Skills

Edit `data/skills_database.json`:

```json
{
  "skill_categories": {
    "your_category": {
      "category_name": "Your Category",
      "description": "Description of your category",
      "skills": {
        "your_skill": {
          "name": "Your Skill",
          "description": "Skill description",
          "related_skills": ["related1", "related2"],
          "levels": ["beginner", "intermediate", "advanced", "expert"]
        }
      }
    }
  }
}
```

### Adding New Opportunities

Add to `data/opportunities_database.json`:

```json
{
  "opportunities": [
    {
      "opportunity_id": "unique_id",
      "title": "Job Title",
      "description": "Job description",
      "opportunity_type": "job",
      "required_skills": [
        {
          "skill_id": "python",
          "skill_name": "Python",
          "category": "programming",
          "required_level": "intermediate",
          "importance": 0.8,
          "is_mandatory": true
        }
      ]
    }
  ]
}
```

### Custom Matching Logic

Extend the `SkillMatcher` class:

```python
from skillmatch.utils import SkillMatcher

class CustomSkillMatcher(SkillMatcher):
    def _calculate_custom_score(self, user_profile, opportunity):
        # Your custom matching logic
        return score
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft Agent Framework** for the powerful AI agent capabilities
- **GitHub Models** for providing access to state-of-the-art language models
- **Pydantic** for robust data validation and modeling
- **Rich** for beautiful terminal output
- **Click** for the CLI framework

## 📞 Support

- 📧 Email: [team@skillmatch.ai](mailto:team@skillmatch.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/rubyferdianto/SkillMatch.AI/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/rubyferdianto/SkillMatch.AI/discussions)

## 🗺️ Roadmap

- [ ] Web interface with React frontend
- [ ] Integration with job boards (LinkedIn, Indeed)
- [ ] Advanced learning path recommendations
- [ ] Team skill analysis and planning
- [ ] API for third-party integrations
- [ ] Mobile application
- [ ] Enterprise features and deployment

---

**Built with ❤️ by the SkillMatch.AI team**