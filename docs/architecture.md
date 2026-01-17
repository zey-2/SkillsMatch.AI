# Architecture

## Overview
SkillsMatch.AI has two primary entry points:
- CLI: `skillmatch.py`
- Web app: `web/app.py`

The core AI matching logic lives in `src/skillmatch/` and the Flask UI lives in
`web/`.

## Key Modules
- `src/skillmatch/agents/skill_match_agent.py`: AI agent (Microsoft Agent Framework)
- `src/skillmatch/models/`: Pydantic domain models
- `src/skillmatch/utils/`: data loading + matching utilities
- `web/services/`: web-specific services (matching, vector search, PDF)
- `web/database/`: SQLAlchemy models + DB config

## AI Stack
- Microsoft Agent Framework (`agent_framework`) for orchestration
- OpenAI/GitHub Models for chat + embeddings
- TF‑IDF vector search for local similarity
