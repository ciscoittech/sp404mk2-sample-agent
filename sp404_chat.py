#!/usr/bin/env python3
"""
SP404MK2 Conversational CLI - Natural language interface for sample discovery.
Enhanced with musical intelligence from specialist knowledge bases.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator, Any
import json

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table

import aiohttp
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import our modules
from src.chat.musical_understanding import MusicalUnderstanding, MusicalRequest
from src.agents.collector import CollectorAgent
from src.agents.base import AgentStatus
from src.config import settings
from src.context import IntelligentContextManager

# Load environment
load_dotenv()
console = Console()

# Load specialist knowledge
SPECIALISTS_DIR = Path(".claude/commands")


class MusicalIntent(BaseModel):
    """Structured representation of user's musical request."""
    primary_genre: Optional[str] = Field(description="Main musical genre")
    sub_genre: Optional[str] = Field(description="Sub-genre or style")
    era: Optional[str] = Field(description="Time period (70s, 90s, etc)")
    mood: Optional[str] = Field(description="Emotional quality")
    bpm_range: Optional[tuple[int, int]] = Field(description="Tempo range")
    reference_artists: List[str] = Field(default_factory=list, description="Artist references")
    technical_descriptors: List[str] = Field(default_factory=list, description="Technical terms")
    search_queries: List[str] = Field(default_factory=list, description="Generated search queries")


class SP404ChatAgent:
    """Main conversational agent with musical intelligence."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            console.print("[red]Error: OPENROUTER_API_KEY not found in environment[/red]")
            sys.exit(1)

        # Initialize intelligent context manager
        self.context = IntelligentContextManager()
        self.specialists = self._load_specialists()

        # Initialize musical understanding
        self.musical_understanding = MusicalUnderstanding()

        # Initialize collector agent
        self.collector = CollectorAgent()

        # Model configuration
        self.model = settings.chat_model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _load_specialists(self) -> Dict[str, str]:
        """Load specialist knowledge from command files."""
        specialists = {}
        
        specialist_files = [
            "musical-search-specialist.md",
            "groove-analyst.md",
            "era-expert.md"
        ]
        
        for filename in specialist_files:
            filepath = SPECIALISTS_DIR / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Extract core knowledge sections
                    specialist_name = filename.replace('.md', '').replace('-', '_')
                    specialists[specialist_name] = content
        
        return specialists
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with specialist knowledge."""
        base_prompt = """You are an expert musical AI assistant for the SP404MK2 sample discovery system. 
You understand musical terminology, production techniques, and can translate vague descriptions into precise search queries.

Your capabilities include:
1. Understanding musical vibes, moods, and references
2. Translating producer/artist references into searchable terms  
3. Identifying era-specific production characteristics
4. Suggesting BPM ranges and musical keys
5. Building comprehensive search strategies

You have access to the following specialist knowledge:
"""
        
        # Add relevant specialist knowledge
        if "musical_search_specialist" in self.specialists:
            base_prompt += "\n\n## Musical Search Translation Expertise\n"
            base_prompt += self._extract_section(
                self.specialists["musical_search_specialist"], 
                "Core Translation Skills"
            )
        
        return base_prompt
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from specialist knowledge."""
        lines = content.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name in line and line.startswith('#'):
                in_section = True
                continue
            elif in_section and line.startswith('#') and not line.startswith('##'):
                break
            elif in_section:
                section_content.append(line)
        
        return '\n'.join(section_content[:500])  # Limit size
    
    async def process_request(self, user_input: str) -> str:
        """Process user request with streaming response."""
        # Build intelligent context
        intelligent_context = self.context.build_context(user_input)

        # Build messages
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
        ]

        # Add intelligent tier-based context
        if intelligent_context:
            messages.append({
                "role": "system",
                "content": intelligent_context
            })

        messages.append({"role": "user", "content": user_input})
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ciscoittech/sp404mk2-sample-agent",
            "X-Title": "SP404MK2 Sample Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.model_temperature,
            "max_tokens": settings.chat_max_tokens,
            "stream": True
        }
        
        full_response = ""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"API Error: {response.status} - {error_text}"
                    
                    # Stream response
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith("data: "):
                            data_str = line_text[6:]
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response += content
                                        # Don't print during streaming to avoid formatting issues
                            except json.JSONDecodeError:
                                continue
            
            return full_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def extract_search_queries(self, response: str) -> List[str]:
        """Extract search queries from agent response."""
        queries = []
        
        # Look for bullet points or numbered lists
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if any(line.startswith(prefix) for prefix in ['- ', '• ', '* ', '1.', '2.', '3.']):
                # Extract the query part
                query = line.split(maxsplit=1)[-1] if len(line.split(maxsplit=1)) > 1 else ''
                if query and len(query) > 5:  # Minimum query length
                    queries.append(query.strip('"\''))
        
        return queries
    
    async def detect_search_intent(self, user_input: str, response: str) -> bool:
        """Detect if user wants to search for samples."""
        search_indicators = [
            'find', 'search', 'looking for', 'need', 'want', 'show me',
            'get me', 'discover', 'samples', 'loops', 'breaks', 'drums'
        ]
        
        input_lower = user_input.lower()
        return any(indicator in input_lower for indicator in search_indicators)
    
    def is_youtube_url(self, text: str) -> bool:
        """Check if text contains a YouTube URL."""
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/v/',
            'youtube.com/embed/'
        ]
        return any(pattern in text.lower() for pattern in youtube_patterns)
    
    async def execute_sample_search(self, user_input: str) -> Dict[str, Any]:
        """Execute sample search based on user request."""
        # Parse request with musical understanding
        musical_request = self.musical_understanding.parse_request(user_input)

        # Update context manager with musical intent
        self.context.update_musical_intent({
            "genres": musical_request.genres,
            "sub_genres": musical_request.sub_genres,
            "bpm_range": musical_request.bpm_range,
            "era": musical_request.era,
            "texture_descriptors": musical_request.texture_descriptors,
            "artist_references": musical_request.artist_references
        })

        # Register active tools
        self.context.register_active_tool("youtube_search")

        # Prepare collector parameters
        collector_params = {
            "genre": musical_request.genres[0] if musical_request.genres else "electronic",
            "style": musical_request.sub_genres[0] if musical_request.sub_genres else "",
            "platforms": ["youtube"],  # Start with YouTube only
            "max_results": 10,
            "assess_quality": True
        }

        # Add BPM if specified
        if musical_request.bpm_range:
            collector_params["bpm_range"] = musical_request.bpm_range

        # Add era if specified
        if musical_request.era:
            collector_params["era"] = musical_request.era

        # Execute collector agent
        task_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = await self.collector.execute(task_id, **collector_params)

        return {
            "musical_request": musical_request,
            "collector_result": result,
            "search_queries": musical_request.search_queries[:5]
        }
    
    async def analyze_youtube_url(self, url: str) -> Dict[str, Any]:
        """Analyze a YouTube URL for samples."""
        from src.tools.timestamp_extractor import TimestampExtractor
        from src.tools.download import get_youtube_metadata

        # Register active tool
        self.context.register_active_tool("timestamp_extractor")

        try:
            # Try to get real metadata first
            try:
                metadata = await get_youtube_metadata(url)
                video_info = {
                    "title": metadata.get("title", "Unknown"),
                    "channel": metadata.get("uploader", "Unknown"),
                    "duration": metadata.get("duration", 0),
                    "description": metadata.get("description", "")
                }
            except:
                # Fallback to basic info extraction from URL
                video_info = {
                    "title": "Unknown Video",
                    "channel": "Unknown Channel", 
                    "duration": 0,
                    "description": ""
                }
            
            # Extract timestamps from description if available
            extractor = TimestampExtractor()
            description_timestamps = []
            
            if video_info.get("description"):
                description_timestamps = extractor.extract_timestamps_from_text(
                    video_info["description"]
                )
            
            # Format response
            return {
                "status": "success",
                "url": url,
                "video_info": video_info,
                "description_timestamps": description_timestamps,
                "comment_timestamps": [],  # Comments require separate API call
                "total_timestamps": len(description_timestamps)
            }
        except Exception as e:
            # Even if metadata fails, try to extract info from URL/title pattern
            try:
                # Extract video ID for basic analysis
                import re
                video_id_match = re.search(r'[?&]v=([^&]+)', url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    return {
                        "status": "success",
                        "url": url,
                        "video_info": {
                            "title": f"Video {video_id}",
                            "channel": "Unknown",
                            "duration": 0,
                            "description": ""
                        },
                        "description_timestamps": [],
                        "comment_timestamps": [],
                        "total_timestamps": 0
                    }
            except:
                pass
                
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }
    
    async def run_chat_interface(self):
        """Run the interactive chat interface."""
        # Welcome message
        welcome = Panel.fit(
            "[bold cyan]🎵 SP404MK2 Musical Intelligence Agent[/bold cyan]\n\n" +
            "I understand musical vibes, production styles, and can help you find the perfect samples.\n\n" +
            "[dim]Try: 'I need that Dilla bounce' or 'Find me some 70s soul breaks'[/dim]\n" +
            "[dim]Commands: /help, /clear, /history, /exit[/dim]",
            border_style="cyan"
        )
        console.print(welcome)
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                # Handle commands
                if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    console.print("\n[yellow]Thanks for using SP404MK2 Agent! Keep making beats! 🎵[/yellow]")
                    break
                
                elif user_input.lower() == '/clear':
                    console.clear()
                    console.print(welcome)
                    continue
                
                elif user_input.lower() == '/help':
                    help_text = """
[bold]Available Commands:[/bold]
• /help - Show this help message
• /clear - Clear the screen
• /history - Show conversation history
• /metrics - Show context manager metrics
• /exit - Exit the chat

[bold]Example Requests:[/bold]
• "I need dusty jazz drums from the 70s"
• "Find me some Madlib-style loops"
• "Show me boom bap drums around 90 BPM"
• "I want that lo-fi bedroom producer sound"
                    """
                    console.print(Panel(help_text, title="Help", border_style="green"))
                    continue
                
                elif user_input.lower() == '/history':
                    if self.context.conversation_history:
                        history_table = Table(title="Conversation History")
                        history_table.add_column("#", style="dim", width=3)
                        history_table.add_column("You", style="cyan")
                        history_table.add_column("Agent", style="green")

                        for i, exchange in enumerate(self.context.conversation_history[-5:], 1):
                            history_table.add_row(
                                str(i),
                                exchange['user'][:50] + "..." if len(exchange['user']) > 50 else exchange['user'],
                                exchange['agent'][:50] + "..." if len(exchange['agent']) > 50 else exchange['agent']
                            )

                        console.print(history_table)
                    else:
                        console.print("[dim]No conversation history yet[/dim]")
                    continue

                elif user_input.lower() == '/metrics':
                    # Display context manager metrics
                    metrics = self.context.get_metrics_summary()

                    metrics_table = Table(title="Context Manager Metrics")
                    metrics_table.add_column("Metric", style="cyan")
                    metrics_table.add_column("Value", style="green")

                    # Current state
                    metrics_table.add_row("Total Tokens", str(metrics["current_state"]["total_tokens"]))
                    for tier, tokens in metrics["current_state"]["tier_tokens"].items():
                        metrics_table.add_row(f"  {tier}", str(tokens))

                    metrics_table.add_row("", "")  # Spacer

                    # Performance
                    metrics_table.add_row("Total Requests", str(metrics["performance"]["total_requests"]))
                    metrics_table.add_row("Avg Load Time", f"{metrics['performance']['avg_load_time_ms']:.2f}ms")

                    metrics_table.add_row("", "")  # Spacer

                    # Budget management
                    metrics_table.add_row("Pruning Events", str(metrics["budget_management"]["total_pruning_events"]))
                    metrics_table.add_row("Pruning Rate", f"{metrics['budget_management']['pruning_rate']:.1f}%")

                    console.print(metrics_table)
                    continue
                
                # Check if user provided a YouTube URL
                if self.is_youtube_url(user_input):
                    console.print("\n[bold green]Agent:[/bold green] I'll analyze this YouTube video for sample opportunities...\n")
                    
                    # Extract URL from input
                    import re
                    url_match = re.search(r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+)', user_input)
                    if url_match:
                        url = url_match.group(1)
                        
                        # Analyze with progress indicator
                        with console.status("[dim]🎵 Analyzing YouTube video...[/dim]", spinner="dots"):
                            analysis_result = await self.analyze_youtube_url(url)
                        
                        if analysis_result["status"] == "success":
                            # Display formatted results
                            video_info = analysis_result["video_info"]
                            console.print(f"[bold]Video Analysis:[/bold]")
                            console.print(f"  • Title: {video_info.get('title', 'Unknown')}")
                            console.print(f"  • Channel: {video_info.get('channel', 'Unknown')}")
                            console.print(f"  • Duration: {video_info.get('duration', 0)} seconds")
                            
                            # Show timestamps if found
                            desc_timestamps = analysis_result["description_timestamps"]
                            if desc_timestamps:
                                console.print(f"\n[bold]Sample Timestamps Found ({len(desc_timestamps)}):[/bold]")
                                
                                # Create a table for timestamps
                                ts_table = Table()
                                ts_table.add_column("Time", style="cyan", width=10)
                                ts_table.add_column("Description", style="white")
                                ts_table.add_column("Type", style="green", width=12)
                                
                                for ts in desc_timestamps[:15]:  # Show first 15
                                    ts_table.add_row(
                                        ts["timestamp"],
                                        ts["description"][:60] + "..." if len(ts["description"]) > 60 else ts["description"],
                                        "Sample" if ts.get("is_sample") else "Section"
                                    )
                                
                                console.print(ts_table)
                                
                                if len(desc_timestamps) > 15:
                                    console.print(f"\n[dim]... and {len(desc_timestamps) - 15} more timestamps[/dim]")
                            else:
                                console.print("\n[yellow]No timestamps found in video description[/yellow]")
                                
                                # Analyze the video title for sample information
                                title = video_info.get('title', '')
                                console.print("\n[bold]Analyzing video content from title:[/bold]")
                                
                                # Extract sample pack information
                                if 'sample pack' in title.lower():
                                    # Parse common sample pack naming patterns
                                    features = []
                                    
                                    # Look for genre/style
                                    if '70s' in title or 'vintage' in title.lower():
                                        features.append("• Era: 1970s vintage style")
                                    if '90s' in title or '90\'s' in title:
                                        features.append("• Era: 1990s classic style")
                                    
                                    # Look for musical styles
                                    styles = ['soul', 'hip-hop', 'hip hop', 'drill', 'jazz', 'funk', 'italian']
                                    found_styles = [s for s in styles if s in title.lower()]
                                    if found_styles:
                                        features.append(f"• Genres: {', '.join(s.title() for s in found_styles)}")
                                    
                                    # Look for artist references
                                    if 'larry june' in title.lower():
                                        features.append("• Style Reference: Larry June (smooth, laid-back)")
                                    if 'alchemist' in title.lower():
                                        features.append("• Style Reference: The Alchemist (sample-heavy)")
                                    if 'curren$y' in title.lower() or 'currensy' in title.lower():
                                        features.append("• Style Reference: Curren$y (jazzy, smooth)")
                                    
                                    # Look for descriptors
                                    if 'free' in title.lower():
                                        features.append("• License: Free to use")
                                    
                                    if features:
                                        for feature in features:
                                            console.print(feature)
                                    
                                    # Suggest actions
                                    console.print("\n[bold]Suggested Actions:[/bold]")
                                    console.print("  1. Download the full video for sample extraction")
                                    console.print("  2. Use the SP-404MK2 chop mode to create loops")
                                    console.print("  3. Search for similar packs with: 'find me more " + 
                                                (' '.join(found_styles[:2]) if found_styles else 'vintage') + " samples'")
                            
                            # Save to context
                            response = f"Analyzed YouTube video: {video_info.get('title', 'Unknown')}. Found {analysis_result['total_timestamps']} timestamps."
                            self.context.add_exchange(user_input, response)
                            
                            # Enhanced tip based on content
                            if 'sample pack' in video_info.get('title', '').lower():
                                console.print("\n[dim]💡 This appears to be a sample pack. You can download the entire video[/dim]")
                                console.print("[dim]   and use the SP-404MK2 to chop it into individual samples.[/dim]")
                            else:
                                console.print("\n[dim]Tip: You can download specific segments using the timestamp extractor[/dim]")
                        else:
                            console.print(f"[red]Failed to analyze video: {analysis_result['error']}[/red]")
                            self.context.add_exchange(user_input, f"Failed to analyze video: {analysis_result['error']}")
                    else:
                        console.print("[red]Could not extract YouTube URL from input[/red]")
                
                # Check if user wants to search for samples
                elif await self.detect_search_intent(user_input, ""):
                    console.print("\n[bold green]Agent:[/bold green] I understand you're looking for samples. Let me analyze your request...\n")
                    
                    # Execute search with progress indicator
                    with console.status("[dim]🎵 Searching for samples...[/dim]", spinner="dots"):
                        search_results = await self.execute_sample_search(user_input)
                    
                    # Display results
                    musical_req = search_results["musical_request"]
                    collector_result = search_results["collector_result"]
                    
                    if collector_result.status == AgentStatus.SUCCESS:
                        result_data = collector_result.result
                        sources = result_data.get("sources", [])

                        # Update context with search results and samples
                        self.context.update_search_results(sources)
                        for source in sources:
                            self.context.add_discovered_sample(source)

                        # Show musical understanding
                        console.print("[bold]Musical Understanding:[/bold]")
                        if musical_req.genres:
                            console.print(f"  • Genres: {', '.join(musical_req.genres)}")
                        if musical_req.bpm_range:
                            console.print(f"  • BPM Range: {musical_req.bpm_range[0]}-{musical_req.bpm_range[1]}")
                        if musical_req.texture_descriptors:
                            console.print(f"  • Vibes: {', '.join(musical_req.texture_descriptors[:3])}")
                        if musical_req.artist_references:
                            console.print(f"  • Artist References: {', '.join(musical_req.artist_references)}")
                        
                        console.print(f"\n[bold]Found {len(sources)} samples:[/bold]")
                        
                        # Display sources in a table
                        if sources:
                            table = Table(title="Sample Results")
                            table.add_column("#", style="dim", width=3)
                            table.add_column("Title", style="cyan")
                            table.add_column("Platform", style="green")
                            table.add_column("Quality", style="yellow")
                            
                            for i, source in enumerate(sources[:10], 1):
                                quality = f"{source.get('quality_score', 0.7):.1%}" if 'quality_score' in source else "N/A"
                                table.add_row(
                                    str(i),
                                    source.get("title", "Unknown")[:50] + "...",
                                    source.get("platform", "unknown"),
                                    quality
                                )
                            
                            console.print(table)
                        
                        # Save to context
                        response = f"Found {len(sources)} samples matching your request."
                        self.context.add_exchange(user_input, response)
                        
                        # Ask if user wants to download
                        console.print("\n[dim]Type 'download 1-3' to download samples 1, 2, and 3[/dim]")
                        console.print("[dim]Or continue chatting to refine your search[/dim]")
                    else:
                        console.print(f"[red]Search failed: {collector_result.error}[/red]")
                        response = "Sorry, I encountered an error while searching."
                        self.context.add_exchange(user_input, response)
                    
                else:
                    # Regular conversational response
                    console.print("\n[bold green]Agent:[/bold green] ", end='')
                    
                    # Show thinking spinner
                    with console.status("[dim]Thinking...[/dim]", spinner="dots"):
                        response = await self.process_request(user_input)
                    
                    # Format the response with proper line breaks
                    formatted_response = response.replace("\\n", "\n")
                    
                    # If response contains markdown-style formatting, render it properly
                    if "**" in formatted_response or "##" in formatted_response:
                        from rich.markdown import Markdown
                        md = Markdown(formatted_response)
                        console.print(md)
                    else:
                        console.print(formatted_response)
                    
                    # Save to context
                    self.context.add_exchange(user_input, response)
                    
                    # Extract search queries if present
                    queries = await self.extract_search_queries(response)
                    if queries:
                        console.print("\n[dim]Generated search queries:[/dim]")
                        for i, query in enumerate(queries, 1):
                            console.print(f"  {i}. {query}")
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Type /exit to quit.[/yellow]")
                continue
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")
                continue


async def main():
    """Main entry point."""
    agent = SP404ChatAgent()
    await agent.run_chat_interface()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 🎵[/yellow]")