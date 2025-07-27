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

- **Multi-Agent Architecture**: Specialized agents for different tasks
- **AI-Powered Decisions**: Uses DeepSeek R1, DeepSeek V3, Qwen3, and Google Flash models
- **Automated BPM Detection**: Analyzes and organizes samples by tempo
- **GitHub Integration**: All tasks tracked as GitHub issues
- **Review Queue System**: Human-in-the-loop approval process
- **Database Tracking**: Turso database for sample metadata
- **Cost Optimization**: Uses cheapest appropriate AI model for each task

## 🛠️ Tech Stack

- **Framework**: [Pydantic AI](https://github.com/pydantic/pydantic-ai)
- **Database**: [Turso](https://turso.tech/) (SQLite at the edge)
- **AI Models**: Via [OpenRouter](https://openrouter.ai/)
  - DeepSeek R1 (Architecture)
  - DeepSeek V3 / Qwen3 Coder (Implementation)
  - Google Flash 2.0 (Quick tasks)
- **Audio Processing**: 
  - [yt-dlp](https://github.com/yt-dlp/yt-dlp) (YouTube downloads)
  - [librosa](https://librosa.org/) (Audio analysis)
- **CLI**: [Typer](https://typer.tiangolo.com/)
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

### Creating a Sample Collection Task

```bash
# Using GitHub CLI
gh issue create \
  --title "[SAMPLES] Jazz drum breaks from 1970s" \
  --label "agent-task,samples" \
  --body "Source: YouTube\nStyle: Jazz\nBPM: 80-100\nCount: 20"

# Using the agent CLI
python -m sp404agent collect \
  --source "https://youtube.com/playlist?..." \
  --style "jazz" \
  --bpm "80-100" \
  --count 20
```

### Reviewing Samples

```bash
# Check review queue
python -m sp404agent review --list

# Approve samples
python -m sp404agent review --approve 1,3,5,7

# Reject samples
python -m sp404agent review --reject 2,4,6
```

### Agent Management

```bash
# Check agent status
python -m sp404agent status

# Run specific agent
python -m sp404agent run --agent downloader --issue 123

# View agent logs
python -m sp404agent logs --agent analyzer --tail 50
```

## 🤖 Agent Types

1. **Architect Agent** (DeepSeek R1)
   - Designs system improvements
   - Plans complex workflows
   - Optimizes agent interactions

2. **Coder Agent** (DeepSeek V3/Qwen3)
   - Implements new features
   - Fixes bugs
   - Writes tests

3. **Collector Agent** (Flash 2.0)
   - Discovers sample sources
   - Validates URLs
   - Categorizes content

4. **Downloader Agent**
   - Downloads from YouTube/direct links
   - Handles retries and errors
   - Converts to proper format

5. **Analyzer Agent**
   - Detects BPM
   - Analyzes audio characteristics
   - Organizes by tempo

6. **Reporter Agent**
   - Creates GitHub issues
   - Updates task status
   - Generates review queues

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

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built for the SP404MK2 community
- Inspired by lo-fi hip hop producers worldwide
- Special thanks to J Dilla and MF DOOM for the inspiration

---

For detailed architecture information, see [ARCHITECTURE.md](docs/ARCHITECTURE.md)