# API Documentation - SkillsMatch.AI v2.0

## Overview

This document provides comprehensive API documentation for SkillsMatch.AI v2.0, including all endpoints, request/response formats, and integration examples.

**Base URL**: `http://localhost:5004`  
**Version**: 2.0 (AI-Enhanced)  
**Last Updated**: November 21, 2025

## Authentication

Currently, SkillsMatch.AI operates without authentication for development purposes. Production deployments should implement proper authentication mechanisms.

## Core Endpoints

### User Profiles

#### GET /profiles
List all active user profiles.

**Response:**
```json
{
  "profiles": [
    {
      "user_id": "tim_cooking",
      "name": "TIM COOKING",
      "title": "Healthcare Professional",
      "experience_level": "senior",
      "skills": [
        {"skill_name": "nurse", "level": "expert", "years_experience": 10}
      ],
      "location": "Singapore",
      "is_active": true
    }
  ],
  "count": 1
}
```

#### GET /profiles/{user_id}
Get detailed profile information.

**Parameters:**
- `user_id` (string): Unique user identifier

**Response:**
```json
{
  "user_id": "tim_cooking",
  "name": "TIM COOKING",
  "email": "tim@example.com",
  "title": "Healthcare Professional",
  "bio": "Experienced nursing professional...",
  "skills": [...],
  "work_experience": [...],
  "education": [...],
  "career_goals": [...]
}
```

#### POST /profiles
Create a new user profile.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "title": "Software Developer",
  "experience_level": "mid",
  "skills": [
    {"skill_name": "python", "level": "intermediate", "years_experience": 3}
  ],
  "location": "Singapore"
}
```

#### PUT /profiles/{user_id}
Update existing profile.

**Request Body:** Same as POST /profiles

### Job Matching

#### POST /match_jobs
Find job matches for a user profile using AI-enhanced matching.

**Request Body:**
```json
{
  "user_id": "tim_cooking",
  "limit": 10,
  "use_ai": true
}
```

**Response:**
```json
{
  "matches": [
    {
      "job": {
        "id": 42,
        "title": "TCM Physician",
        "company_name": "Ma Kuang Chinese Medicine & Research Centre Pte Ltd",
        "job_description": "Traditional Chinese Medicine practice...",
        "location": "Singapore",
        "employment_type": "Full-time"
      },
      "score": 0.85,
      "ai_analysis": {
        "skill_matches": [
          {
            "user_skill": "nurse",
            "job_skill": "patient care",
            "confidence": 0.90,
            "reasoning": "Nursing skills directly applicable to patient care"
          }
        ],
        "match_breakdown": {
          "skills": 0.85,
          "location": 1.0,
          "experience": 0.80,
          "industry": 0.90
        },
        "recommended_skills": ["traditional medicine", "holistic care"]
      },
      "reasons": ["Strong skill alignment with healthcare requirements"]
    }
  ],
  "total_analyzed": 100,
  "ai_enabled": true
}
```

### Jobs

#### GET /jobs
List all available job opportunities.

**Query Parameters:**
- `limit` (integer): Maximum number of jobs to return (default: 50)
- `category` (string): Filter by job category
- `location` (string): Filter by location
- `experience_level` (string): Filter by experience level

**Response:**
```json
{
  "jobs": [
    {
      "id": 1,
      "title": "Customer Service Executive",
      "company_name": "Ministry of Clean Pte Ltd",
      "location": "Singapore",
      "employment_type": "Full-time",
      "experience_level": "Entry",
      "job_description": "Manage telephone enquiries professionally...",
      "keywords": "customer service, communication, problem solving",
      "salary_range": "2500-3500",
      "posted_date": "2025-11-15T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50
}
```

#### GET /jobs/{job_id}
Get detailed job information.

**Response:**
```json
{
  "id": 42,
  "title": "TCM Physician",
  "company_name": "Ma Kuang Chinese Medicine & Research Centre Pte Ltd",
  "job_description": "Full job description...",
  "requirements": ["Medical degree", "Patient care experience"],
  "benefits": ["Health insurance", "Professional development"],
  "application_deadline": "2025-12-31T23:59:59Z",
  "contact_info": {
    "email": "careers@makuang.com",
    "phone": "+65-1234-5678"
  }
}
```

### AI Services

#### POST /ai/analyze_skills
Use AI to analyze and categorize skills.

**Request Body:**
```json
{
  "skills": ["nurse", "python", "data analysis"],
  "context": "job_matching"
}
```

**Response:**
```json
{
  "categories": [
    {
      "name": "Healthcare & Medical",
      "skills": ["nurse"],
      "confidence": 0.95,
      "related_industries": ["Healthcare", "Medical", "Nursing"],
      "synonyms": ["healthcare", "medical", "patient care"]
    },
    {
      "name": "Technology & Programming",
      "skills": ["python"],
      "confidence": 0.98,
      "related_industries": ["Technology", "Software Development"],
      "synonyms": ["programming", "software development"]
    }
  ],
  "ai_provider": "github_models",
  "processing_time": 1.2
}
```

#### POST /ai/match_analysis
Get detailed AI analysis for job matching.

**Request Body:**
```json
{
  "user_skills": ["nurse", "patient care"],
  "job_description": "TCM Physician role requiring clinical experience...",
  "job_title": "TCM Physician"
}
```

**Response:**
```json
{
  "matches": [
    {
      "user_skill": "nurse",
      "job_skill": "clinical experience",
      "confidence": 0.88,
      "reasoning": "Nursing provides extensive clinical experience applicable to TCM practice",
      "category": "Healthcare"
    }
  ],
  "overall_compatibility": 0.85,
  "ai_reasoning": "Strong healthcare background makes candidate highly suitable for TCM physician role",
  "skill_gaps": ["traditional chinese medicine knowledge"],
  "recommendations": ["Consider TCM certification courses"]
}
```

### Chat Interface

#### POST /chat
Interact with AI career counselor.

**Request Body:**
```json
{
  "message": "I'm a nurse looking to transition to traditional medicine. Any advice?",
  "user_id": "tim_cooking",
  "context": "career_transition"
}
```

**Response:**
```json
{
  "response": "As an experienced nurse, you have excellent foundational skills for traditional medicine. Your patient care experience, clinical knowledge, and healthcare background are highly transferable. I'd recommend exploring TCM certification programs and highlighting your holistic care approach.",
  "suggestions": [
    "Look into TCM Physician roles",
    "Consider traditional medicine certification",
    "Highlight patient care experience"
  ],
  "related_jobs": [42, 67, 89],
  "confidence": 0.92
}
```

### PDF Generation

#### POST /generate_pdf
Generate professional job application PDF.

**Request Body:**
```json
{
  "user_id": "tim_cooking",
  "job_id": 42,
  "include_match_analysis": true,
  "template": "professional"
}
```

**Response:**
```json
{
  "pdf_url": "/downloads/tim_cooking_tcm_physician_application.pdf",
  "generated_at": "2025-11-21T10:30:00Z",
  "file_size": "245KB",
  "pages": 2,
  "includes": ["profile_summary", "skill_analysis", "match_reasoning", "company_info"]
}
```

### Analytics

#### GET /analytics/dashboard
Get comprehensive platform analytics.

**Response:**
```json
{
  "summary": {
    "total_jobs": 100,
    "active_profiles": 2,
    "successful_matches": 15,
    "ai_requests_today": 45
  },
  "skill_trends": [
    {"skill": "healthcare", "demand": 85, "trend": "increasing"},
    {"skill": "python", "demand": 78, "trend": "stable"}
  ],
  "match_quality": {
    "average_score": 0.82,
    "ai_enhanced_improvement": "23%"
  },
  "popular_jobs": [
    {"title": "TCM Physician", "applications": 8},
    {"title": "Data Analyst", "applications": 12}
  ]
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid user_id format",
    "details": {
      "field": "user_id",
      "expected": "string",
      "received": "integer"
    }
  },
  "timestamp": "2025-11-21T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

- `400` - Bad Request: Invalid input parameters
- `404` - Not Found: Resource not found
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server-side error
- `503` - Service Unavailable: AI service temporarily unavailable

## Rate Limiting

- **Default Rate**: 100 requests per minute per IP
- **AI Endpoints**: 20 requests per minute per IP
- **PDF Generation**: 10 requests per minute per IP

## SDK Examples

### Python SDK Usage

```python
import requests
import json

class SkillsMatchAPI:
    def __init__(self, base_url="http://localhost:5004"):
        self.base_url = base_url
    
    def get_profiles(self):
        response = requests.get(f"{self.base_url}/profiles")
        return response.json()
    
    def match_jobs(self, user_id, use_ai=True):
        data = {"user_id": user_id, "use_ai": use_ai}
        response = requests.post(f"{self.base_url}/match_jobs", json=data)
        return response.json()
    
    def chat(self, message, user_id=None):
        data = {"message": message, "user_id": user_id}
        response = requests.post(f"{self.base_url}/chat", json=data)
        return response.json()

# Usage
api = SkillsMatchAPI()
profiles = api.get_profiles()
matches = api.match_jobs("tim_cooking")
chat_response = api.chat("What healthcare jobs are available?")
```

### JavaScript SDK Usage

```javascript
class SkillsMatchAPI {
    constructor(baseUrl = 'http://localhost:5004') {
        this.baseUrl = baseUrl;
    }
    
    async getProfiles() {
        const response = await fetch(`${this.baseUrl}/profiles`);
        return response.json();
    }
    
    async matchJobs(userId, useAI = true) {
        const response = await fetch(`${this.baseUrl}/match_jobs`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: userId, use_ai: useAI})
        });
        return response.json();
    }
    
    async chat(message, userId = null) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message, user_id: userId})
        });
        return response.json();
    }
}

// Usage
const api = new SkillsMatchAPI();
const profiles = await api.getProfiles();
const matches = await api.matchJobs('tim_cooking');
const chatResponse = await api.chat('Help me find healthcare jobs');
```

## WebSocket Support

For real-time updates, connect to the WebSocket endpoint:

```javascript
const socket = io('http://localhost:5004');

socket.on('match_update', (data) => {
    console.log('New match found:', data);
});

socket.on('profile_updated', (data) => {
    console.log('Profile updated:', data);
});

socket.emit('subscribe_matches', {user_id: 'tim_cooking'});
```

## Testing

### Health Check

```bash
curl http://localhost:5004/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0",
  "ai_services": "available",
  "database": "connected",
  "uptime": "2h 15m 32s"
}
```

### API Testing Examples

```bash
# Get all profiles
curl -X GET "http://localhost:5004/profiles"

# Match jobs for TIM COOKING
curl -X POST "http://localhost:5004/match_jobs" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "tim_cooking", "use_ai": true}'

# AI skill analysis
curl -X POST "http://localhost:5004/ai/analyze_skills" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["nurse", "patient care", "clinical"], "context": "job_matching"}'
```

## Production Considerations

### Security
- Implement API authentication (JWT tokens recommended)
- Add HTTPS/TLS encryption
- Set up proper CORS policies
- Implement request validation and sanitization

### Performance
- Use caching for frequently accessed data
- Implement database connection pooling
- Set up load balancing for high traffic
- Monitor API response times and optimize slow endpoints

### Monitoring
- Set up logging for all API requests
- Monitor AI service usage and costs
- Track error rates and performance metrics
- Implement health checks and alerting

---

**SkillsMatch.AI v2.0 API Documentation** - Complete reference for AI-enhanced career matching platform.