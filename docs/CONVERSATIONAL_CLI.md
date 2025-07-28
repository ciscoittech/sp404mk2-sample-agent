# SP404MK2 Conversational CLI

The conversational CLI provides a natural language interface for discovering and organizing samples. It uses Google's Gemma-2-27B model via OpenRouter and integrates deep musical understanding from our specialist knowledge bases.

## Features

### 🎵 Natural Language Understanding
- Talk to the agent like you would a fellow producer
- Uses specialized musical knowledge to understand vibes, references, and technical terms
- Automatically translates casual descriptions into precise search queries

### 🔍 Intelligent Sample Discovery
- Parses musical requests to identify genres, BPM, era, and mood
- Generates multiple search queries optimized for different platforms
- Integrates with the collector agent for actual sample discovery

### 💬 Conversational Context
- Maintains conversation history for natural dialogue
- Refine searches based on previous exchanges
- Remember preferences within a session

## Usage

### Starting the Chat
```bash
# Activate virtual environment
source venv/bin/activate

# Set OpenRouter API key
export OPENROUTER_API_KEY="your-api-key-here"

# Run the chat interface
python sp404_chat.py
```

### Example Conversations

**Finding Specific Vibes:**
```
You: I need that dusty Dilla bounce around 90 BPM

Agent: I understand you're looking for samples. Let me analyze your request...

Musical Understanding:
  • Genres: hip-hop
  • BPM Range: 85-95
  • Vibes: off-grid, wonky, humanized
  • Artist References: dilla

Found 5 samples:
┌─────┬──────────────────────────────────────┬──────────┬─────────┐
│ #   │ Title                                │ Platform │ Quality │
├─────┼──────────────────────────────────────┼──────────┼─────────┤
│ 1   │ Dilla Style Drums - 92 BPM           │ youtube  │ 90%     │
│ 2   │ Detroit Swing Breaks                 │ youtube  │ 85%     │
│ 3   │ MPC3000 Groove Pack                  │ youtube  │ 87%     │
└─────┴──────────────────────────────────────┴──────────┴─────────┘
```

**Era-Specific Searches:**
```
You: Find me some 70s soul breaks with that vintage warmth

Agent: Analyzing your request for 70s soul samples...

Musical Understanding:
  • Genres: soul, funk
  • Era: 70s
  • Vibes: vintage, warm, analog
  • Sample Types: drums

Searching for vintage soul breaks...
```

**Producer Style References:**
```
You: Show me some Madlib-style psychedelic loops

Agent: Looking for Madlib-inspired psychedelic samples...

Musical Understanding:
  • Artists: madlib
  • Vibes: dusty, psychedelic, jazzy
  • Search focus: obscure samples, loop digga style
```

### Commands

- `/help` - Show available commands and examples
- `/clear` - Clear the screen
- `/history` - Show conversation history
- `/exit` - Exit the chat

### Search Detection

The agent automatically detects when you want to search for samples based on keywords like:
- "find", "search", "looking for"
- "need", "want", "show me"
- "samples", "loops", "breaks", "drums"

## Musical Understanding

The CLI uses specialized knowledge from our command files:

### Vibe Translations
- "dusty" → vinyl, lo-fi, tape, analog
- "smooth" → silk, liquid, mellow, warm
- "crunchy" → distorted, saturated, bit-crushed
- "spacey" → ambient, ethereal, cosmic

### Producer References
- **J Dilla**: off-grid drums, drunk swing, MPC3000
- **Madlib**: obscure samples, psychedelic soul, loop digga
- **Kaytranada**: bouncy grooves, filtered disco, future funk

### Era Mappings
- **60s**: mono, live recording, tape
- **70s**: analog, funk, disco, soul
- **80s**: digital, synth, drum machine
- **90s**: sampling, boom bap, golden era

## Architecture

### Components

1. **SP404ChatAgent** (`sp404_chat.py`)
   - Main chat interface
   - Manages conversation context
   - Handles streaming responses
   - Detects search intent

2. **MusicalUnderstanding** (`src/chat/musical_understanding.py`)
   - Parses natural language
   - Extracts musical attributes
   - Generates search queries
   - Applies specialist knowledge

3. **CollectorAgent Integration**
   - Executes actual searches
   - Assesses sample quality
   - Returns structured results

### Data Flow

```
User Input → Musical Understanding → Search Intent Detection
                                           ↓
                                    Execute Search?
                                     Yes ↓   No ↓
                              Collector Agent  Chat Response
                                      ↓
                               Display Results
```

## Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: Your OpenRouter API key for Gemma-2-27B access

### Model Settings
- Model: `google/gemma-2-27b-it`
- Temperature: 0.7
- Max tokens: 2000
- Streaming: Enabled

## Future Enhancements

1. **Download Integration**: Direct download of selected samples
2. **Playlist Creation**: Save searches as playlists
3. **Sample Preview**: Audio preview before download
4. **Multi-Platform Search**: Expand beyond YouTube
5. **Preference Learning**: Remember user preferences across sessions

## Troubleshooting

### No OpenRouter API Key
```
Error: OPENROUTER_API_KEY not found in environment
```
Solution: Set your API key with `export OPENROUTER_API_KEY="your-key"`

### Connection Issues
- Check internet connection
- Verify API key is valid
- Ensure OpenRouter service is accessible

### Search Not Triggered
- Use explicit search keywords
- Be specific about what you're looking for
- Try rephrasing with "find me" or "I need"