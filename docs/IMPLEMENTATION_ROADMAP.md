# SP404MK2 Sample Agent - Implementation Roadmap

**Created:** 2025-01-27  
**Status:** Planning Phase

## 📋 Overview

We've created GitHub issues for all major agent implementations. Here's how we should approach building them:

## 🏗️ Implementation Order

### Phase 1: Foundation (Week 1)
1. **Tools Module** (#10) - Create shared utilities
   - Start with `database.py` for Turso operations
   - Add `filesystem.py` for file operations
   - Implement basic error handling

### Phase 2: Core Agents (Week 2-3)
2. **Downloader Agent** (#6)
   - Integrate yt-dlp for YouTube
   - Add requests for direct downloads
   - Test with sample URLs

3. **Analyzer Agent** (#7)
   - Integrate librosa for BPM detection
   - Implement file organization
   - Test with downloaded samples

### Phase 3: AI Integration (Week 4)
4. **Collector Agent** (#8)
   - Set up Pydantic AI with Google Flash 2.0
   - Implement search functionality
   - Test with various search criteria

5. **AI Agents** (#11)
   - Configure Architect with DeepSeek R1
   - Configure Coder with DeepSeek V3
   - Create prompt templates

### Phase 4: Workflow (Week 5)
6. **Reporter Agent** (#9)
   - GitHub CLI integration
   - Markdown generation
   - Review queue creation

## 🔧 Technical Approach

### 1. Tools Module Structure
```python
# src/tools/database.py
async def create_sample(data: dict) -> int:
    """Create sample in Turso database."""
    pass

# src/tools/download.py
async def download_youtube(url: str, output_path: str) -> str:
    """Download from YouTube using yt-dlp."""
    pass

# src/tools/audio.py
def detect_bpm(file_path: str) -> float:
    """Detect BPM using librosa."""
    pass
```

### 2. Agent Implementation Pattern
```python
# Each agent follows this pattern
class SpecificAgent(Agent):
    def __init__(self):
        super().__init__("agent_name")
        # Import tools
        self.tools = {
            'download': tools.download,
            'database': tools.database
        }
    
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        # Use tools to accomplish task
        pass
```

### 3. Pydantic AI Integration
```python
# For AI-powered agents
from pydantic_ai import Agent

collector = Agent(
    model='google/gemini-flash-2.0',
    tools=[search_youtube, categorize_content]
)
```

## 🧪 Testing Strategy

1. **Unit Tests**: Each tool function
2. **Integration Tests**: Agent + Tools
3. **End-to-End Tests**: Full workflow

## 📊 Success Metrics

- [ ] Can download samples from YouTube
- [ ] Accurately detects BPM (±2 BPM)
- [ ] AI agents make sensible decisions
- [ ] Review queues are human-readable
- [ ] GitHub issues update automatically

## 🚀 Quick Start for Development

```bash
# 1. Install dependencies
pip install yt-dlp librosa pydantic-ai openrouter

# 2. Set environment variables
export OPENROUTER_API_KEY="your-key"

# 3. Start with tools module
mkdir src/tools
touch src/tools/__init__.py

# 4. Implement first tool
# Start with database.py using Turso CLI
```

## 💡 Key Decisions to Make

1. **Async vs Sync**: Most operations should be async
2. **Error Handling**: Use custom exceptions
3. **Logging**: Structured logging to database
4. **Cost Control**: Token limits for AI agents
5. **Rate Limiting**: Respect YouTube/API limits

## 📚 Resources

- [Pydantic AI Docs](https://ai.pydantic.dev/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [librosa Documentation](https://librosa.org/)
- [OpenRouter API](https://openrouter.ai/docs)

---

Next Steps: Start with Issue #10 (Tools Module) as it's the foundation for all agents.