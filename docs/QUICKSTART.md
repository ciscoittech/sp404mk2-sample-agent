# SP404MK2 Sample Agent - Quick Start Guide

## 🚀 Prerequisites

1. **Python 3.11+**
2. **Turso CLI** (already installed)
3. **GitHub CLI** (`gh`)
4. **FFmpeg** (for audio processing)

## 📦 Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Install additional requirements
pip install -r requirements.txt
```

## 🔧 Configuration

Your `.env` file is already configured with:
- ✅ Turso database credentials
- ✅ OpenRouter API key

## 🏃 Running the Agent

### Method 1: Command Line Interface

```bash
# Run the main CLI
python -m sp404agent --help

# Or use the shorthand
sp404agent --help
```

### Method 2: Direct Agent Execution

```bash
# Run specific agents
python -m src.agents.collector --genre jazz --style bebop --max-results 10
python -m src.agents.downloader --task-id 1
python -m src.agents.analyzer --input-dir ./downloads
python -m src.agents.reporter --action daily-summary
```

### Method 3: Python Script

Create a script `run_collection.py`:

```python
import asyncio
from src.agents.collector import CollectorAgent
from src.agents.downloader import DownloaderAgent
from src.agents.analyzer import AnalyzerAgent
from src.agents.reporter import ReporterAgent

async def collect_samples():
    # 1. Discover samples
    collector = CollectorAgent()
    result = await collector.execute(
        task_id="demo_001",
        genre="jazz",
        style="bebop", 
        bpm_range=(120, 140),
        max_results=5
    )
    print(f"Found {len(result.result['sources'])} sources")
    
    # 2. Download samples
    downloader = DownloaderAgent()
    result = await downloader.execute(
        task_id="demo_002",
        sources=result.result['sources'],
        output_dir="./downloads",
        audio_format="wav"
    )
    print(f"Downloaded {result.result['downloaded_count']} files")
    
    # 3. Analyze samples
    analyzer = AnalyzerAgent()
    result = await analyzer.execute(
        task_id="demo_003",
        input_dir="./downloads",
        organize_by_bpm=True,
        detect_key=True
    )
    print(f"Analyzed {result.result['analyzed_count']} files")
    
    # 4. Create review queue
    reporter = ReporterAgent()
    result = await reporter.execute(
        task_id="demo_004",
        action="create_review_queue",
        batch_data={
            "batch_name": "Jazz Bebop Collection",
            "samples": result.result['files']
        }
    )
    print(f"Review queue created: {result.result['review_file']}")

# Run the collection
asyncio.run(collect_samples())
```

## 🎯 Example Workflows

### 1. Quick Sample Collection
```bash
# Collect 10 hip-hop drum breaks
python -m sp404agent collect \
  --genre "hip-hop" \
  --style "boom-bap" \
  --bpm-range 85 95 \
  --count 10
```

### 2. Analyze Existing Samples
```bash
# Analyze all WAV files in a directory
python -m sp404agent analyze \
  --input-dir ./my-samples \
  --organize-by-bpm \
  --detect-duplicates
```

### 3. Create GitHub Issue for Collection
```bash
# Using GitHub CLI
gh issue create \
  --title "[SAMPLES] Jazz fusion 120-130 BPM" \
  --label "agent-task,samples" \
  --body "Source: YouTube\nGenre: Jazz Fusion\nBPM: 120-130\nCount: 20"
```

## 🧪 Test Run

Try this simple test to verify everything works:

```bash
# 1. Test database connection
turso db shell fafo "SELECT COUNT(*) FROM samples;"

# 2. Test a simple collection
python -c "
import asyncio
from src.agents.collector import CollectorAgent

async def test():
    agent = CollectorAgent()
    result = await agent.execute('test', genre='test', max_results=1)
    print('Success!' if result.status.value == 'success' else 'Failed')

asyncio.run(test())
"
```

## 📁 Output Structure

After running, you'll find:
```
downloads/          # Downloaded samples
samples/           
  ├── drum_breaks/
  │   ├── 85_90_bpm/
  │   ├── 90_95_bpm/
  │   └── 95_100_bpm/
  └── bass/
      ├── c_minor/
      ├── f_minor/
      └── g_minor/
review_queue/      # Markdown files for review
```

## 🐛 Troubleshooting

### Common Issues:

1. **Import errors**: Make sure you're in the virtual environment
2. **Database errors**: Check Turso connection with `turso auth whoami`
3. **Download failures**: Ensure yt-dlp is installed: `pip install yt-dlp`
4. **Audio errors**: Install librosa: `pip install librosa`

### Check Logs:
```bash
# View agent logs
tail -f logs/agent.log

# Check database logs
turso db shell fafo "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT 10;"
```

## 🎉 Next Steps

1. Review samples in `review_queue/`
2. Approve/reject samples
3. Load approved samples into your SP404MK2
4. Make beats! 🎵

---

For detailed documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)