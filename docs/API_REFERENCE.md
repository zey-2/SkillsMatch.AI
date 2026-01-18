# SkillsMatch.AI - API Reference

## Overview

SkillsMatch.AI provides a comprehensive RESTful API for profile management, job matching, and AI-powered skill analysis. All endpoints return JSON responses and use standard HTTP status codes.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Endpoints](#endpoints)

## Authentication

Currently, the API does not require authentication for development. In production, implement API keys:

```bash
# Add to request headers
X-API-Key: your-api-key-here
Authorization: Bearer <token>
```

## Base URL

```
Development:  http://127.0.0.1:5000
Production:   https://api.skillsmatch.ai
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Example"
  },
  "timestamp": "2024-01-18T10:30:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  },
  "timestamp": "2024-01-18T10:30:00Z"
}
```

## Error Handling

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | AI service down |

### Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `VALIDATION_ERROR` | Input validation failed | Check request format |
| `NOT_FOUND` | Resource doesn't exist | Verify ID/parameters |
| `UNAUTHORIZED` | Authentication failed | Check API key |
| `RATE_LIMIT` | Too many requests | Wait before retrying |
| `AI_SERVICE_ERROR` | AI service unavailable | Retry later |
| `DATABASE_ERROR` | Database operation failed | Contact support |
| `INTERNAL_ERROR` | Unexpected server error | Contact support |

## Rate Limiting

### Limits

- **Standard**: 100 requests per minute per IP
- **Batch**: 10 batch requests per minute
- **AI Operations**: 20 AI calls per minute

### Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705580400
```

## Endpoints

### Profile Management

#### List Profiles

```http
GET /api/profiles?page=1&per_page=20&search=john
```

**Parameters**:
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)
- `search` (string, optional): Search by name or email

**Response** (200):
```json
{
  "success": true,
  "profiles": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Developer",
      "email": "john@example.com",
      "experience_level": "senior",
      "total_years_experience": 8,
      "location": "Singapore",
      "skills": [
        {
          "id": "python-001",
          "name": "Python",
          "level": "expert",
          "years": 8,
          "category": "Programming Language"
        }
      ],
      "created_at": "2024-01-18T10:00:00Z",
      "updated_at": "2024-01-18T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

#### Create Profile

```http
POST /api/profiles
Content-Type: application/json

{
  "name": "John Developer",
  "email": "john@example.com",
  "experience_level": "senior",
  "total_years_experience": 8,
  "location": "Singapore",
  "skills": [
    {
      "skill_id": "python-001",
      "level": "expert",
      "years": 8
    },
    {
      "skill_id": "javascript-001",
      "level": "advanced",
      "years": 6
    }
  ]
}
```

**Response** (201):
```json
{
  "success": true,
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Developer",
    "email": "john@example.com",
    "experience_level": "senior",
    "total_years_experience": 8,
    "location": "Singapore",
    "skills": [...],
    "created_at": "2024-01-18T10:30:00Z"
  },
  "message": "Profile created successfully"
}
```

#### Get Profile

```http
GET /api/profiles/{profile_id}
```

**Response** (200):
```json
{
  "success": true,
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Developer",
    ...
  }
}
```

#### Update Profile

```http
PUT /api/profiles/{profile_id}
Content-Type: application/json

{
  "total_years_experience": 9,
  "location": "Singapore, Singapore"
}
```

**Response** (200):
```json
{
  "success": true,
  "profile": { ... },
  "message": "Profile updated successfully"
}
```

#### Delete Profile

```http
DELETE /api/profiles/{profile_id}
```

**Response** (204): No content

#### Add Skills to Profile

```http
POST /api/profiles/{profile_id}/skills
Content-Type: application/json

{
  "skills": [
    {
      "skill_id": "golang-001",
      "level": "intermediate",
      "years": 2
    }
  ]
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Skills added successfully",
  "skills": [...]
}
```

### Job Management

#### List Jobs

```http
GET /api/jobs?page=1&per_page=20&search=python&position_level=senior
```

**Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page
- `search` (string): Search by title or company
- `position_level` (string): Filter by position level (entry/junior/mid/senior/lead)

**Response** (200):
```json
{
  "success": true,
  "jobs": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "position_level": "senior",
      "description": "We are looking for...",
      "required_skills": ["Python", "Django", "PostgreSQL"],
      "location": "Singapore",
      "salary_range": {
        "min": 8000,
        "max": 12000
      },
      "created_at": "2024-01-18T08:00:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "per_page": 20
}
```

#### Create Job

```http
POST /api/jobs
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "position_level": "senior",
  "description": "We are looking for experienced Python developers...",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "location": "Singapore",
  "salary_range": {
    "min": 8000,
    "max": 12000
  }
}
```

**Response** (201):
```json
{
  "success": true,
  "job": { ... },
  "message": "Job created successfully"
}
```

#### Get Job Details

```http
GET /api/jobs/{job_id}
```

**Response** (200):
```json
{
  "success": true,
  "job": { ... }
}
```

### Job Matching

#### Match Profile to Jobs

```http
POST /api/match
Content-Type: application/json

{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Parameters**:
- `profile_id` (string, required): ID of profile to match
- `job_ids` (array, optional): Specific job IDs to match against. If not provided, matches against all jobs.

**Response** (200):
```json
{
  "success": true,
  "matches": [
    {
      "job_id": "660e8400-e29b-41d4-a716-446655440001",
      "job_title": "Senior Python Developer",
      "overall_score": 0.92,
      "skill_match_score": 0.95,
      "experience_match_score": 0.90,
      "location_match": true,
      "reasoning": "Strong Python background with 8 years of experience. Minor gap in Django expertise.",
      "skill_gaps": ["Advanced Django", "Docker orchestration"],
      "recommendations": [
        "Consider taking Docker certification",
        "Practice with Django REST framework"
      ]
    }
  ],
  "match_timestamp": "2024-01-18T10:35:00Z"
}
```

#### Analyze Skill Gap

```http
POST /api/match/skill-gap-analysis
Content-Type: application/json

{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response** (200):
```json
{
  "success": true,
  "analysis": {
    "profile_skills": ["Python", "JavaScript", "PostgreSQL"],
    "required_skills": ["Python", "Django", "PostgreSQL", "Docker"],
    "gaps": ["Django", "Docker"],
    "surplus_skills": ["JavaScript"],
    "gap_analysis": [
      {
        "skill": "Django",
        "importance": "high",
        "current_level": "none",
        "required_level": "advanced",
        "learning_resources": ["Django official docs", "Real Python", "Udemy courses"]
      }
    ]
  }
}
```

### AI Services

#### Analyze Resume

```http
POST /api/ai/analyze-resume
Content-Type: multipart/form-data

file: <resume.pdf>
```

**Response** (200):
```json
{
  "success": true,
  "analysis": {
    "experience_level": "senior",
    "years_of_experience": 8,
    "key_skills": ["Python", "Django", "PostgreSQL", "AWS"],
    "summary": "Experienced backend developer with strong Python and cloud architecture background",
    "recommendations": [
      "Consider learning modern frontend frameworks",
      "Expand knowledge in containerization"
    ]
  }
}
```

#### Get Skill Recommendations

```http
POST /api/ai/skill-recommendations
Content-Type: application/json

{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_position": "senior",
  "industry": "fintech"
}
```

**Response** (200):
```json
{
  "success": true,
  "recommendations": [
    {
      "skill": "Machine Learning",
      "importance": "high",
      "why": "Growing demand in fintech for fraud detection and risk assessment",
      "resources": ["Coursera", "Andrew Ng's ML course", "Kaggle competitions"],
      "estimated_learning_time": "3-6 months"
    },
    {
      "skill": "Kubernetes",
      "importance": "medium",
      "why": "Industry standard for container orchestration in enterprise fintech",
      "resources": ["Linux Academy", "Kubernetes official docs"],
      "estimated_learning_time": "2-3 months"
    }
  ]
}
```

### System Health

#### Health Check

```http
GET /api/health
```

**Response** (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T10:40:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_service": "healthy",
    "vector_search": "healthy"
  },
  "version": "1.0.0"
}
```

## Best Practices

### 1. Error Handling

Always check the `success` field:

```python
import requests

response = requests.post('http://localhost:5000/api/profiles', json={...})
data = response.json()

if not data['success']:
    print(f"Error: {data['error']}")
    print(f"Code: {data['code']}")
    print(f"Details: {data.get('details', {})}")
else:
    profile = data['profile']
```

### 2. Pagination

Use pagination for large datasets:

```python
# Get all profiles with pagination
page = 1
profiles = []

while True:
    response = requests.get(
        'http://localhost:5000/api/profiles',
        params={'page': page, 'per_page': 50}
    )
    data = response.json()
    profiles.extend(data['profiles'])
    
    if page * 50 >= data['total']:
        break
    page += 1
```

### 3. Correlation IDs

Include correlation IDs for tracing:

```python
import uuid

correlation_id = str(uuid.uuid4())
headers = {'X-Correlation-ID': correlation_id}

response = requests.post(
    'http://localhost:5000/api/profiles',
    json={...},
    headers=headers
)
```

### 4. Batch Operations

Use batch endpoints for multiple operations:

```python
# Batch match multiple profiles
response = requests.post(
    'http://localhost:5000/api/match/batch',
    json={
        'profile_ids': [id1, id2, id3],
        'job_ids': [job1, job2, job3]
    }
)
```

## Versioning

Current API version: **1.0.0**

Future versions will maintain backward compatibility with deprecation notices.

---

**Last Updated**: January 18, 2026
**API Version**: 1.0.0
**Documentation Version**: 1.0.0
