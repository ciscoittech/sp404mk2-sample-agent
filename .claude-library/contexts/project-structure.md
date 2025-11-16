# SP404MK2 Sample Agent - Project Structure

## Overview
AI-powered sample collection and organization system for Roland SP-404MK2 workflow. Analyzes YouTube videos, extracts samples, organizes content for hip-hop/electronic music production.

## Technology Stack

### Backend
- **Framework**: FastAPI (async web framework)
- **Database**: SQLite with async support (aiosqlite)
- **ORM**: SQLAlchemy 2.0 (async patterns)
- **Migrations**: Alembic
- **Validation**: Pydantic v2 (request/response schemas)
- **AI**: OpenRouter API (Qwen models)
- **Audio**: librosa, soundfile, numpy

### Frontend
- **Server-Driven UI**: HTMX (hypermedia-driven)
- **Interactivity**: Alpine.js (minimal JavaScript)
- **Styling**: DaisyUI (Tailwind CSS components)
- **Templating**: Jinja2 (server-side rendering)

### Testing
- **Backend**: Pytest, async tests, real database
- **E2E**: Playwright (browser automation)
- **Philosophy**: MVP-level (2-5 tests per feature)

## Directory Structure

```
sp404mk2-sample-agent/
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── api/                   # API layer
│   │   │   └── v1/
│   │   │       ├── api.py        # Router registration
│   │   │       └── endpoints/    # Endpoint handlers
│   │   │           ├── public.py         # Samples, upload
│   │   │           ├── batch.py          # Batch processing
│   │   │           ├── usage.py          # Cost tracking
│   │   │           ├── preferences.py    # User settings
│   │   │           └── sp404_export.py   # Hardware export
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── sample.py
│   │   │   ├── batch.py
│   │   │   ├── user_preferences.py
│   │   │   ├── audio_features.py
│   │   │   ├── sp404_export.py
│   │   │   └── youtube.py
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── sample.py
│   │   │   ├── batch.py
│   │   │   ├── preferences.py
│   │   │   ├── sp404_export.py
│   │   │   └── hybrid_analysis.py
│   │   ├── services/              # Business logic
│   │   │   ├── audio_features_service.py      # librosa analysis
│   │   │   ├── openrouter_service.py          # AI API client
│   │   │   ├── hybrid_analysis_service.py     # Orchestration
│   │   │   ├── preferences_service.py         # User settings
│   │   │   └── sp404_export_service.py        # Hardware export
│   │   ├── db/                    # Database config
│   │   │   ├── init_db.py
│   │   │   └── session.py
│   │   ├── core/                  # Configuration
│   │   │   └── config.py
│   │   ├── main.py                # FastAPI app
│   │   └── templates_config.py    # Shared Jinja2 config
│   ├── templates/                 # HTMX templates
│   │   ├── samples/
│   │   ├── batches/
│   │   ├── preferences/
│   │   └── sp404/
│   ├── tests/                     # Test suite
│   │   ├── conftest.py           # Shared fixtures
│   │   ├── fixtures/             # Test audio files
│   │   ├── api/                  # API tests
│   │   ├── services/             # Service tests
│   │   ├── models/               # Model tests
│   │   └── schemas/              # Schema tests
│   ├── alembic/                   # Database migrations
│   │   └── versions/
│   ├── requirements.txt
│   ├── run.py                     # Server entry point
│   └── sp404_samples.db          # SQLite database
│
├── frontend/                       # Web UI
│   ├── index.html                # Landing page
│   ├── pages/
│   │   ├── samples.html          # Sample browser
│   │   ├── kits.html             # Kit builder
│   │   ├── batch.html            # Batch processing
│   │   ├── usage.html            # API cost tracking
│   │   └── settings.html         # User preferences
│   ├── components/
│   │   └── nav.html              # Navigation
│   ├── tests/e2e/                # Playwright tests
│   │   └── *.spec.js
│   ├── package.json
│   └── playwright.config.js
│
├── src/                           # Python CLI tools
│   ├── agents/                   # AI agent implementations
│   │   └── collector_real.py
│   ├── tools/                    # CLI tools
│   │   └── kit_assembler.py
│   ├── context/
│   │   └── intelligent_manager.py
│   ├── config.py
│   └── cli_download_manager.py   # Download CLI
│
├── .claude/                       # Agent system (NEW)
│   ├── agent-launcher.md         # Agent router
│   ├── settings.json             # Project metadata
│   └── commands/                 # Workflow commands
│       ├── build.md
│       ├── debug.md
│       ├── test.md
│       └── deploy.md
│
├── .claude-library/               # Agent library (NEW)
│   ├── REGISTRY.json             # Agent registry
│   ├── agents/
│   │   ├── core/                 # Core agents
│   │   └── specialized/          # Domain specialists
│   └── contexts/                 # Project knowledge
│
├── downloads/                     # YouTube downloads
├── expansion-plans/               # Future features
├── docs/                          # Documentation
├── sp404_chat.py                  # Main CLI
├── docker-compose.yml
└── README.md
```

## Key Architectural Patterns

### Service Layer Pattern
Business logic separated from API layer:
- **Services**: `backend/app/services/`
- **API Endpoints**: Call services, return responses
- **Separation**: API handles HTTP, Services handle business logic

### Dual Response Pattern
API endpoints support both JSON (API clients) and HTMX (web UI):
- Check `hx-request` header
- Return HTML template for HTMX
- Return JSON for API clients

### Hybrid Analysis Architecture
Two-phase audio analysis:
1. **Phase 1**: librosa audio feature extraction (local, $0)
2. **Phase 2**: OpenRouter AI vibe interpretation (~$0.00001-$0.00005)
3. **Orchestration**: `HybridAnalysisService` coordinates both

### Repository Pattern
Database access through models:
- **Models**: SQLAlchemy ORM (`backend/app/models/`)
- **Async**: All database operations use `await`
- **Session Management**: Dependency injection via `get_db()`

## File Naming Conventions

### Python Files
- **Models**: `backend/app/models/sample.py` (singular)
- **Schemas**: `backend/app/schemas/sample.py` (singular)
- **Services**: `backend/app/services/sample_service.py` (underscore)
- **Tests**: `backend/tests/test_*.py` or `*/test_*.py`

### HTML Templates
- **Pages**: `frontend/pages/*.html` (full pages)
- **Components**: `frontend/components/*.html` (reusable)
- **HTMX Templates**: `backend/templates/*/*.html` (partial responses)

## Configuration Files

### Backend Configuration
- **Settings**: `backend/app/core/config.py` (Pydantic Settings)
- **Database**: `backend/app/db/session.py` (async engine)
- **Logging**: Configured in `backend/app/main.py`

### Frontend Configuration
- **Playwright**: `frontend/playwright.config.js`
- **Package**: `frontend/package.json`

### Environment Variables
- **Database**: `DATABASE_URL`
- **OpenRouter**: `OPENROUTER_API_KEY`
- **Upload**: `UPLOAD_DIR`, `MAX_UPLOAD_SIZE`
- **Export**: `SP404_EXPORT_DIR`

## Development Workflow

### Start Server
```bash
./venv/bin/python backend/run.py
# Access: http://localhost:8100
```

### Run Tests
```bash
# Backend tests
pytest backend/tests/ -v

# E2E tests
cd frontend && npm run test:e2e
```

### Database Migrations
```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Docker
```bash
# Start services
docker-compose up -d

# Initialize database
docker-compose exec backend python -m app.db.init_db

# View logs
docker-compose logs -f
```

## Project Stats
- **Complexity**: COMPLEX (47,739 lines of code)
- **Python Files**: 98 backend files
- **Test Coverage**: 97.6% pass rate (83/85 tests)
- **Database Tables**: 8 tables
- **API Endpoints**: 20+ endpoints
- **Features**: Complete (Workstreams A-G)
