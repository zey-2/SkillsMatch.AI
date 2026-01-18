# SkillsMatch.AI

AI-powered career matching platform that helps you find the perfect job based on your skills, experience, and career goals.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and navigate
git clone https://github.com/rubyferdianto/SkillsMatch.AI.git
cd SkillsMatch.AI

# Create environment
conda create -n smai python=3.11
conda activate smai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your OpenAI API key:

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your key
OPENAI_API_KEY=sk-your-key-here
```

Get your API key: [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Run the Application

```bash
# Always activate the environment first
conda activate smai

# Start the web interface
python web/app.py
```

Visit `http://localhost:5004` in your browser.

## ✨ What Can You Do?

### 📝 Create Your Profile
- Add your work experience and education
- List your skills with proficiency levels
- Upload your resume (PDF)
- Set salary and work preferences

### 🎯 Get Matched
- Find jobs that match your skills
- See detailed compatibility scores
- Understand what skills you need
- Get personalized recommendations

### 💬 AI Career Advisor
- Chat with an AI career coach
- Get advice on career growth
- Learn about industry trends
- Ask any career-related questions

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[API Reference](docs/API_REFERENCE.md)** - API documentation

## 🛠️ Tech Stack

- **AI**: OpenAI GPT-5-mini for consistent, high-quality matching
- **Backend**: Python, Flask
- **Frontend**: Bootstrap 5, JavaScript
- **Storage**: SQLite database, JSON profiles
- **Matching**: TF-IDF vectorization + cosine similarity

## ⚠️ Important Notes

### Current Limitations

This is a **proof-of-concept** application best suited for:
- Personal career planning
- Small team use (<50 employees)
- Educational/demo purposes
- Research projects

**Not recommended for:**
- Large-scale production (designed for local/small deployments)
- Processing highly sensitive data (basic security only)
- Mission-critical applications (no high-availability features)

### Key Constraints

- **Storage**: JSON file-based (not optimized for thousands of profiles)
- **Performance**: AI processing takes 3-8 seconds per match
- **Security**: No user authentication or data encryption
- **Data**: Static job database (not live job feeds)

See full limitations in [TECHNICAL_DEBT_STATUS.md](TECHNICAL_DEBT_STATUS.md)

## 💡 Common Tasks

### Create a Profile via CLI
```bash
conda activate smai
python skillmatch.py match --interactive
```

### Analyze Skill Gaps
```bash
python skillmatch.py gaps --profile profiles/your_profile.json
```

### Find Learning Resources
```bash
python skillmatch.py learn --skills "python, machine learning"
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with OpenAI, Flask, and Bootstrap.

---

**Need Help?**
- 🐛 [Report Issues](https://github.com/rubyferdianto/SkillsMatch.AI/issues)
- 💬 [Discussions](https://github.com/rubyferdianto/SkillsMatch.AI/discussions)
