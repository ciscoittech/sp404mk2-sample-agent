# SP404MK2 Sample Agent - Project Memory

**Last Updated:** 2025-01-29  
**Status:** ✅ Production Ready - Web UI Complete  
**Coverage:** 27% backend / 100% E2E tests

---

## 🎯 **PROJECT OVERVIEW**

AI-powered sample collection and organization system for Roland SP-404MK2 workflow. Analyzes YouTube videos, extracts samples, and organizes content for hip-hop/electronic music production.

### Core Capabilities
- **YouTube Analysis**: Extract samples from music videos with timestamp detection
- **AI-Powered Classification**: Genre, BPM, key, and style analysis
- **Download Management**: Complete metadata tracking and review system
- **SP-404MK2 Integration**: Organized workflow for hardware sampler
- **Web Dashboard**: FastAPI + DaisyUI interface with real-time updates
- **Rich CLI Interface**: Beautiful terminal output with tables and panels

---

## 🤖 **CURRENT AI MODELS**

### Production Models (Upgraded 2025-01-27)
- **Chat Agent**: `google/gemma-3-27b-it` (27B parameters)
- **Collector Agent**: `qwen/qwen3-235b-a22b-2507` (235B parameters)
- **Token Limits**: 4000 chat, 2000 collector
- **Temperature**: 0.5 (configurable)

### Benefits
- **10x More Powerful**: Upgraded from 7B to 27B/235B parameter models
- **Better Analysis**: Enhanced musical understanding and classification
- **Improved Accuracy**: More reliable timestamp and content detection

---

## 📁 **PROJECT STRUCTURE**

```
sp404mk2-sample-agent/
├── src/                    # Core source code
│   ├── agents/            # AI agent implementations
│   ├── tools/             # Tool implementations
│   ├── config.py         # Configuration management
│   └── cli_download_manager.py  # Download management CLI
├── backend/               # FastAPI web backend
│   ├── app/              # Application code
│   ├── tests/            # Backend tests
│   └── uploads/          # Sample uploads
├── frontend/              # Web UI (HTMX + DaisyUI)
│   ├── pages/            # UI pages
│   ├── tests/e2e/        # Playwright E2E tests
│   └── static/           # Assets
├── downloads/             # Download storage
│   ├── test/             # YouTube downloads
│   └── metadata/         # Download metadata
├── expansion-plans/       # Future development plans
├── .claude/commands/      # AI assistant commands
├── docs/                 # Documentation
├── sp404_chat.py         # Main chat interface
└── docker-compose.yml    # Docker configuration
```

---

## 🛠 **AVAILABLE COMMANDS**

### Sample Collection & Analysis
- `/agent-overview` - Overview of all agent capabilities
- `/vibe-analyst` - Analyze emotional/textural qualities
- `/groove-analyst` - Rhythm and timing analysis
- `/era-expert` - Musical history and production techniques
- `/sample-compatibility` - Check sample compatibility
- `/musical-search-specialist` - Build effective search queries

### Workflow Management
- `/create-sample-workspace` - Initialize collection workspace with git
- `/process-sample-task` - Complete sample collection workflow
- `/list-sample-tasks` - View active collection tasks
- `/batch-processor` - Handle large sample collections
- `/download-manager` - Manage sample downloads
- `/kit-builder` - Organize samples for SP-404MK2

---

## 🎵 **DOWNLOAD MANAGEMENT SYSTEM**

### Metadata Tracking
- **Complete Records**: URL, platform, file info, timestamps
- **Review System**: Rating, notes, status tracking
- **Usage Analytics**: Access counts, project usage
- **Tagging**: Genre, style, custom labels

### CLI Commands
```bash
# List downloads
python -m src.cli_download_manager list --limit 10 --platform youtube

# Show details  
python -m src.cli_download_manager show <download_id>

# Review content
python -m src.cli_download_manager review <download_id> --rating 8 --notes "Great sample"

# Add tags
python -m src.cli_download_manager tag <download_id> --tags "jazz,vintage,70s"

# View statistics
python -m src.cli_download_manager stats

# Export data
python -m src.cli_download_manager export --output my_downloads.json
```

---

## 🔧 **DEVELOPMENT STATUS**

### ✅ Completed Features
- YouTube video analysis and download
- Rich CLI formatting with tables/panels
- Download metadata tracking system
- AI model upgrades (27B/235B parameters)
- Complete cleanup of demo code and old samples
- Working test suite with fixtures
- Review and rating system
- **Web UI**: FastAPI backend with DaisyUI frontend
- **Real-time Updates**: WebSocket vibe analysis
- **Docker Support**: Complete containerization setup

### 🎯 Current Sample Data
- **YouTube Downloads**: 1 video (82.63 MB) with complete metadata
- **Test Fixtures**: 3 audio samples for unit testing
- **Clean State**: All old demos and samples removed

---

## 🚀 **QUICK START COMMANDS**

### Docker Quick Start
```bash
# Start everything
make docker-up
make docker-db-init

# Access Web UI
open http://localhost:8000
```

### Main Chat Interface
```bash
python sp404_chat.py
```

### Download Management
```bash
# List all downloads
python -m src.cli_download_manager list

# View statistics
python -m src.cli_download_manager stats
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run in Docker
make docker-test
```

---

## 📋 **WORKFLOW INTEGRATION**

### For Sample Collection
1. **Discover**: Find YouTube videos with samples
2. **Analyze**: Get AI analysis of content and timestamps
3. **Download**: Save with complete metadata tracking
4. **Review**: Rate quality and add tags/notes
5. **Organize**: Export and integrate with SP-404MK2

### For SP-404MK2 Production
- Download high-quality samples
- Use AI analysis for BPM/key matching
- Organize by genre/style tags
- Track usage in projects

---

## 🎨 **MUSIC PRODUCTION FOCUS**

### Genres Supported
- Hip-Hop and Trap
- Jazz and Soul samples
- Electronic and House
- Vintage and retro sounds
- Drum breaks and loops

### Analysis Features
- BPM detection and estimation
- Musical key identification
- Genre classification
- Timestamp extraction for chops
- Quality assessment

---

## ⚡ **RECENT UPDATES (2025-01-29)**

### Complete Web UI Implementation ✅
- **Backend**: FastAPI with async SQLAlchemy, JWT auth, WebSocket support
- **Frontend**: DaisyUI + HTMX + Alpine.js for beautiful, responsive UI
- **Features**: Sample browser, kit builder, real-time vibe analysis
- **Testing**: 66 E2E tests with Playwright, 100% UI coverage
- **Docker**: Full containerization with docker-compose

### GitHub Integration ✅
- **Issues Closed**: Completed issues #24, #36-43 (Web UI implementation)
- **Git Workflow**: Updated commands for proper branch management
- **CI/CD**: GitHub Actions for automated testing and builds

### Command Cleanup ✅
- **Removed**: Generic development commands (backend, frontend, etc.)
- **Kept**: SP404MK2-specific commands for sampling workflow
- **Updated**: Git integration in sample workspace creation

### Expansion Plans ✅
- **AI Discovery Engine**: Detailed plan for smart sample recommendations
- **File Management Suite**: Comprehensive SP404MK2 file organization solution
- **Market Research**: Identified key pain points from community forums

### Project Stats
- **Total Commits**: 5 major milestones completed
- **Code Coverage**: 27% backend core, 100% E2E tests
- **Dependencies**: All updated and production-ready
- **Documentation**: Comprehensive guides for all features

---

## 🔄 **NEXT DEVELOPMENT PRIORITIES**

### Phase 1: Fresh Collection
1. Test enhanced AI models with new YouTube analysis
2. Start fresh sample collection with improved accuracy
3. Build curated library using review system

### Phase 2: Advanced Features
1. **Audio Analysis**: BPM/key detection integration
2. **Batch Processing**: Multiple video analysis
3. **Project Integration**: Link samples to SP-404MK2 projects
4. **Auto-tagging**: AI-powered genre classification

### Phase 3: Production Tools
1. **Export Workflows**: Direct SP-404MK2 format support
2. **Quality Filtering**: Automatic high-quality detection
3. **Collaboration**: Share sample collections
4. **Performance**: Real-time analysis optimization

---

## 🛠 **TECHNICAL NOTES**

### Dependencies
- **OpenRouter API**: For AI model access
- **yt-dlp**: YouTube download functionality  
- **Rich**: CLI formatting and display
- **Pydantic**: Data validation and models
- **Typer**: CLI interface framework
- **FastAPI**: Web API framework
- **SQLAlchemy**: Async database ORM
- **HTMX**: Server-driven UI updates
- **Alpine.js**: Minimal client interactivity
- **DaisyUI**: Tailwind CSS components

### Configuration
- Models configurable via `src/config.py`
- API keys via `.env` file
- Download paths configurable
- Test fixtures included
- Docker environment variables

### Testing
- **Unit Tests**: 27% coverage (backend core)
- **E2E Tests**: 100% coverage (web UI)
- **Fixtures**: Audio samples for realistic testing
- **CI Ready**: Pytest + Playwright configuration
- **Docker Tests**: Automated test containers

---

*The project is now in a clean, production-ready state with powerful AI models and comprehensive download management. Ready for fresh sample collection and SP-404MK2 integration workflows.*