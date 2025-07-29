# SP404MK2 Sample Agent 🎵🤖

An AI-powered agent system for automated sample collection, organization, and curation for the SP404MK2 drum machine.

## 🎯 Overview

This project uses Pydantic AI to create specialized agents that:
- Discover and download samples from YouTube and direct sources
- Analyze audio files for BPM and musical characteristics
- Organize samples into a structured library
- Create human-reviewable queues for sample approval
- Track all operations through GitHub issues

## 🚀 Features

### Core Features
- **Web UI Dashboard**: Full-featured web interface with HTMX + DaisyUI
- **Batch Processing**: Process multiple samples at once with AI analysis
- **Conversational CLI Interface**: Natural language interaction for sample discovery
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Intelligent YouTube Discovery**: Enhanced search with quality scoring
- **Timestamp-Based Extraction**: Extract specific segments from longer videos
- **Automated BPM Detection**: Analyzes and organizes samples by tempo
- **Database Tracking**: Turso database for sample metadata
- **Real-time Updates**: WebSocket support for live progress tracking

### Specialized Agents
- **Groove Analyst**: Deep rhythm analysis with swing detection and artist similarity
- **Era Expert**: Musical production history and era-specific knowledge
- **Sample Relationship**: Compatibility analysis between samples
- **Intelligent Organizer**: Smart sample library management with multiple strategies

### Organization Features
- **SP-404 Bank Templates**: Pre-configured layouts for different performance styles
- **Compatibility Grouping**: Automatically groups samples that work well together
- **Genre/Era Organization**: Historical and stylistic categorization
- **Project-Specific Layouts**: Tailored organization for different workflows

## 🛠️ Tech Stack

- **Framework**: [Pydantic AI](https://github.com/pydantic/pydantic-ai)
- **Database**: [Turso](https://turso.tech/) (SQLite at the edge)
- **AI Models**: Via [OpenRouter](https://openrouter.ai/)
  - Gemma-2-27B (Conversational interface)
  - Google Flash 2.0 (Quick analysis tasks)
- **Audio Processing**: 
  - [yt-dlp](https://github.com/yt-dlp/yt-dlp) (YouTube downloads)
  - [librosa](https://librosa.org/) (Audio analysis)
- **CLI**: Natural language interface with Rich formatting
- **Language**: Python 3.11+

## 📁 Project Structure

```
sp404mk2-sample-agent/
├── src/
│   ├── agents/         # Individual agent implementations
│   ├── models/         # Pydantic models
│   ├── workflows/      # Task orchestration
│   └── tools/          # Utility functions
├── data/               # Local database and files
├── review_queue/       # Pending samples for review
├── config/            # Configuration files
└── tests/             # Test suite
```

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- GitHub CLI (`gh`)
- FFmpeg (for audio processing)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Build and start with Docker
make docker-build
make docker-up
make docker-db-init

# Access at http://localhost:8000
```

#### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

1. Set up your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-api-key"
```

2. Configure Turso database:
```bash
export TURSO_URL="your-turso-url"
export TURSO_TOKEN="your-turso-token"
```

3. Set up GitHub authentication:
```bash
gh auth login
```

## 📋 Usage

### Web Interface

```bash
# Access the web UI (Docker must be running)
open http://localhost:8000

# Available pages:
- /pages/samples.html    # Browse and analyze samples
- /pages/batch.html      # Batch process audio files
- /pages/kits.html       # Build SP-404 kits
```

### Conversational Sample Discovery

```bash
# Start the conversational CLI
python sp404_chat.py

# Example conversations:
> Find me some 90s boom bap drums like DJ Premier
> Show me jazzy piano loops around 85 BPM
> I need that Dilla swing drums
> Looking for 70s soul bass lines with that Motown vibe
```

### Intelligent Organization

```bash
# Organize by musical properties (BPM, key, type)
python -m sp404agent organize --strategy musical --dir "my_samples"

# Create SP-404 banks
python -m sp404agent organize --strategy sp404 --template hip_hop_kit

# Group compatible samples
python -m sp404agent organize --strategy compatibility --threshold 7.0

# Organize by genre and era
python -m sp404agent organize --strategy genre
```

### Agent Analysis

```bash
# Analyze groove characteristics
python test_groove_analyst.py

# Check era information
python test_era_expert.py

# Test sample compatibility
python test_sample_relationship.py

# Test organization system
python test_intelligent_organizer.py
```

## 🤖 Agent Types

### Discovery & Collection
1. **Collector Agent**
   - Enhanced YouTube search with quality scoring
   - Era-specific and producer-style searches
   - Filters out non-sample content

2. **Downloader Agent**
   - Downloads from YouTube/direct links
   - Timestamp-based extraction
   - Handles retries and errors

### Analysis Agents
3. **Groove Analyst Agent**
   - Deep rhythm analysis with swing percentage
   - Artist similarity matching (Dilla, Questlove, etc.)
   - Groove type classification

4. **Era Expert Agent**
   - Detects production era from audio
   - Provides equipment and technique knowledge
   - Generates era-specific search queries

5. **Sample Relationship Agent**
   - Analyzes harmonic compatibility
   - Checks rhythmic alignment
   - Evaluates frequency overlap
   - Suggests optimal arrangements

### Organization
6. **Intelligent Organizer**
   - Multiple organization strategies
   - SP-404 bank templates
   - Compatibility grouping
   - Project-specific layouts

## 📊 Database Schema

The project uses Turso (SQLite) with the following main tables:
- `samples`: Sample metadata and file paths
- `tasks`: Agent task tracking
- `review_queue`: Human review status
- `agent_logs`: Detailed operation logs

## 🤝 Contributing

This project uses GitHub issues for all task tracking:

1. Check existing issues for current work
2. Create an issue using appropriate template
3. Fork and create a feature branch
4. Submit PR referencing the issue

## 🧪 Testing

The project includes a comprehensive test suite using pytest:

```bash
# Run all tests
make test

# Run with coverage report
make coverage

# Run specific test suites
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-e2e        # End-to-end tests

# Run tests with the test runner
python run_tests.py

# Run tests in Docker
make docker-test
make docker-e2e
```

For detailed testing information, see [TESTING.md](docs/TESTING.md)

## 🐳 Docker Support

The project includes full Docker support for easy deployment:

```bash
# Quick start
make docker-up

# Development with hot reload
make docker-dev

# Production deployment
make docker-prod

# View logs
make docker-logs

# Clean up
make docker-clean
```

For detailed Docker information, see [DOCKER.md](docs/DOCKER.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built for the SP404MK2 community
- Inspired by lo-fi hip hop producers worldwide
- Special thanks to J Dilla and MF DOOM for the inspiration

---

For detailed architecture information, see [ARCHITECTURE.md](docs/ARCHITECTURE.md)