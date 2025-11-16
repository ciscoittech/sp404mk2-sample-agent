# Typer CLI Hardware Assistant - Implementation Plan

**Status**: 📋 Planned (Not Yet Implemented)
**Priority**: Medium
**Estimated Effort**: 2-3 days
**Dependencies**: Hardware Manual Integration ✅ (Complete)

---

## 🎯 Executive Summary

Create a Typer-based CLI that provides **three modes** of hardware assistance:
1. **Fast Mode**: Instant manual lookups (no LLM, <1s response)
2. **Smart Mode**: AI-powered context-aware answers (LLM, ~5s response)
3. **Interactive Mode**: Natural language conversations

This complements the existing `sp404_chat.py` conversational interface by providing quick, scriptable access to hardware guidance.

---

## 🏗️ Architecture Overview

### Current State
```
SP-404MK2 Sample Agent
│
├─ 💬 sp404_chat.py (Conversational, LLM-powered)
│   └─ Use case: Deep learning, exploration, complex questions
│
├─ 🎵 src/cli.py (Typer - sample collection)
│   └─ Use case: Automated sample gathering
│
└─ 📥 src/cli_download_manager.py (Typer - download management)
    └─ Use case: Review and organize downloads
```

### Proposed State
```
SP-404MK2 Sample Agent
│
├─ 💬 sp404_chat.py (Conversational, LLM-powered)
│   └─ Use case: Deep learning, exploration, complex questions
│
├─ ⚡ src/cli_hardware.py (NEW - Typer + LLM hybrid)
│   ├─ Fast Mode: Instant manual lookups
│   ├─ Smart Mode: AI-powered answers
│   └─ Use case: Quick reference, automation, scriptable workflows
│
├─ 🎵 src/cli.py (Typer - sample collection)
│   └─ Use case: Automated sample gathering
│
└─ 📥 src/cli_download_manager.py (Typer - download management)
    └─ Use case: Review and organize downloads
```

---

## 📁 File Structure

### New Files to Create

```
project/
├─ src/
│  ├─ cli_hardware.py                    # Main Typer CLI app (NEW)
│  ├─ hardware/                          # Hardware CLI modules (NEW)
│  │  ├─ __init__.py
│  │  ├─ manual_display.py               # Fast manual section display
│  │  ├─ llm_interface.py                # LLM integration wrapper
│  │  ├─ workflows.py                    # Predefined workflow guides
│  │  └─ tips.py                         # Daily tips and tricks
│  │
│  └─ sp404_chat.py                      # Existing - may need minor refactoring
│
├─ scripts/
│  └─ test_cli_hardware.py               # CLI testing script (NEW)
│
└─ docs/
   └─ plans/
      ├─ TYPER_CLI_HARDWARE_ASSISTANT.md # This file
      └─ TYPER_CLI_USAGE_EXAMPLES.md     # Usage examples (NEW)
```

### Files to Modify

```
backend/requirements.txt                  # Already has typer, no changes needed
pyproject.toml (if exists)               # Add CLI entry point
setup.py (if exists)                     # Add CLI entry point
```

---

## 🔧 Implementation Phases

### Phase 1: Core CLI Structure (Day 1, 4-6 hours)

**Goal**: Basic Typer app with fast mode commands

**Tasks**:
1. Create `src/cli_hardware.py` with Typer app
2. Create `src/hardware/manual_display.py` for fast lookups
3. Implement 5 basic commands:
   - `resample` - Resampling guide
   - `effects` - Effects reference
   - `pattern` - Pattern sequencer guide
   - `looper` - Looper operations
   - `manual` - Search full manual
4. Add `--fast` flag for instant lookups
5. Test basic functionality

**Deliverables**:
- Working CLI: `sp404 hardware resample --fast`
- Fast mode operational (no LLM calls)
- Clean markdown display with Rich

**Success Criteria**:
- ✅ All 5 commands work in fast mode
- ✅ Response time < 1 second
- ✅ Proper error handling
- ✅ Help text displays correctly

---

### Phase 2: LLM Integration (Day 1-2, 6-8 hours)

**Goal**: Add smart mode with AI-powered responses

**Tasks**:
1. Create `src/hardware/llm_interface.py`
2. Refactor `sp404_chat.py` for code reuse:
   - Extract LLM calling logic into shared module
   - Extract context building into reusable function
   - Maintain backward compatibility
3. Implement smart mode for all commands
4. Add `--ask` flag for natural language questions
5. Implement genre-specific recommendations (effects)
6. Add cost tracking for CLI LLM calls

**Deliverables**:
- Working LLM integration: `sp404 hardware effects lofi`
- Natural language questions: `sp404 hardware ask "..."`
- Context-aware responses using hardware manual
- Cost tracking in database

**Success Criteria**:
- ✅ LLM responses include manual context
- ✅ Smart mode provides creative suggestions
- ✅ API costs tracked to database
- ✅ No breaking changes to `sp404_chat.py`

---

### Phase 3: Workflows & Advanced Features (Day 2, 4-6 hours)

**Goal**: Complete workflow guides and convenience commands

**Tasks**:
1. Create `src/hardware/workflows.py`
2. Implement workflow commands:
   - `workflow beatmaking` - Complete beat creation guide
   - `workflow lofi` - Lo-fi production workflow
   - `workflow sampling` - Sampling workflow
   - `workflow export` - Sample export workflow
3. Add convenience commands:
   - `tip` - Daily random tip
   - `quickref` - Common button combinations
   - `shortcuts` - Keyboard shortcuts
4. Add `--interactive` flag for step-by-step walkthroughs

**Deliverables**:
- 4 workflow commands operational
- Tip of the day feature
- Interactive mode prototype

**Success Criteria**:
- ✅ Workflows load multiple manual sections
- ✅ Tips pull from manual + AI creativity
- ✅ Interactive mode guides user step-by-step

---

### Phase 4: Shell Integration & Scripting (Day 3, 3-4 hours)

**Goal**: Make CLI production-ready with shell features

**Tasks**:
1. Add shell completion support (bash, zsh, fish)
2. Create example scripts:
   - Daily practice routine
   - Export study notes
   - Quick reference card generator
3. Add output format options:
   - `--format markdown` - For piping to files
   - `--format json` - For scripting
   - `--format plain` - Plain text
4. Add `--quiet` and `--verbose` flags
5. Create man page / comprehensive help

**Deliverables**:
- Shell completion scripts
- 3 example usage scripts
- Multiple output formats
- Complete documentation

**Success Criteria**:
- ✅ Tab completion works in bash/zsh
- ✅ CLI is fully scriptable
- ✅ Output formats tested and documented

---

### Phase 5: Testing & Documentation (Day 3, 2-3 hours)

**Goal**: Comprehensive testing and user documentation

**Tasks**:
1. Create `scripts/test_cli_hardware.py`
2. Test all commands in all modes
3. Test error handling and edge cases
4. Create usage examples document
5. Update main CLAUDE.md with CLI info
6. Create video tutorial script

**Deliverables**:
- Complete test suite
- Usage examples document
- Updated project documentation
- Tutorial outline

**Success Criteria**:
- ✅ 100% command coverage in tests
- ✅ All error cases handled gracefully
- ✅ Documentation complete and clear

---

## 💻 Detailed Code Specifications

### 1. Main CLI App (`src/cli_hardware.py`)

```python
#!/usr/bin/env python3
"""
SP-404MK2 Hardware Assistant CLI

Provides quick reference and AI-powered guidance for SP-404MK2 operations.

Usage:
    # Fast mode (instant manual lookup)
    sp404 hardware resample --fast
    sp404 hardware effects --list

    # Smart mode (AI-powered)
    sp404 hardware resample
    sp404 hardware effects lofi
    sp404 hardware ask "how do I layer effects?"

    # Workflows
    sp404 hardware workflow beatmaking
    sp404 hardware workflow lofi --interactive

    # Utilities
    sp404 hardware tip
    sp404 hardware quickref
"""

import typer
from typing import Optional
from rich.console import Console
from enum import Enum

# Create main app
app = typer.Typer(
    name="sp404-hardware",
    help="SP-404MK2 Hardware Assistant - Quick reference and AI guidance",
    add_completion=True,
    rich_markup_mode="rich"
)

console = Console()

# Output format options
class OutputFormat(str, Enum):
    rich = "rich"
    markdown = "markdown"
    json = "json"
    plain = "plain"


# ============================================================================
# CORE COMMANDS
# ============================================================================

@app.command()
def resample(
    fast: bool = typer.Option(False, "--fast", "-f", help="Skip AI, show manual only"),
    question: Optional[str] = typer.Option(None, "--ask", "-q", help="Ask specific question"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format", help="Output format")
):
    """
    Resampling guide and tips.

    Examples:
        sp404 hardware resample --fast              # Quick manual lookup
        sp404 hardware resample                     # AI-enhanced guide
        sp404 hardware resample --ask "with effects?"
    """
    from .hardware.manual_display import display_section
    from .hardware.llm_interface import ask_hardware_question

    if fast:
        # Fast mode - just display manual
        display_section("sp404-sampling.md", "Resampling", output_format)
    elif question:
        # Natural language question
        full_question = f"Resampling: {question}"
        response = ask_hardware_question(
            question=full_question,
            sections=["hardware/sp404-sampling.md"],
            output_format=output_format
        )
        console.print(response)
    else:
        # Smart mode - AI enhanced
        response = ask_hardware_question(
            question="Explain resampling on the SP-404MK2 with practical tips and creative techniques",
            sections=["hardware/sp404-sampling.md"],
            output_format=output_format
        )
        console.print(response)


@app.command()
def effects(
    genre: Optional[str] = typer.Argument(None, help="Genre for AI recommendations"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all effects (fast)"),
    creative: bool = typer.Option(False, "--creative", "-c", help="Get creative AI suggestions"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Effects guide and AI recommendations.

    Examples:
        sp404 hardware effects --list               # Fast list
        sp404 hardware effects lofi                 # AI recommendations
        sp404 hardware effects hiphop --creative    # Creative chains
    """
    from .hardware.manual_display import display_section
    from .hardware.llm_interface import ask_hardware_question

    if list_all:
        display_section("sp404-effects.md", output_format=output_format)
    elif genre:
        if creative:
            question = f"Give me creative SP-404MK2 effect chains and techniques for {genre} production, including unconventional combinations"
        else:
            question = f"Recommend SP-404MK2 effects for {genre} with settings and workflow tips"

        response = ask_hardware_question(
            question=question,
            sections=["hardware/sp404-effects.md"],
            output_format=output_format
        )
        console.print(response)
    else:
        # Default: AI overview
        response = ask_hardware_question(
            question="Give me an overview of SP-404MK2 effects with usage tips",
            sections=["hardware/sp404-effects.md"],
            output_format=output_format
        )
        console.print(response)


@app.command()
def pattern(
    mode: Optional[str] = typer.Option(None, "--mode", help="TR-REC or realtime"),
    fast: bool = typer.Option(False, "--fast", "-f", help="Quick manual lookup"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Pattern sequencer guide.

    Examples:
        sp404 hardware pattern --fast               # Quick reference
        sp404 hardware pattern --mode trrec         # TR-REC specific
        sp404 hardware pattern                      # AI guide
    """
    from .hardware.manual_display import display_section
    from .hardware.llm_interface import ask_hardware_question

    if fast:
        display_section("sp404-sequencer.md", output_format=output_format)
    elif mode:
        question = f"Explain {mode} mode for pattern creation on SP-404MK2 with tips and workflow"
        response = ask_hardware_question(
            question=question,
            sections=["hardware/sp404-sequencer.md"],
            output_format=output_format
        )
        console.print(response)
    else:
        response = ask_hardware_question(
            question="Guide me through pattern creation on SP-404MK2, comparing TR-REC and realtime recording",
            sections=["hardware/sp404-sequencer.md"],
            output_format=output_format
        )
        console.print(response)


@app.command()
def looper(
    fast: bool = typer.Option(False, "--fast", "-f"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Looper operation guide.

    Examples:
        sp404 hardware looper --fast                # Quick reference
        sp404 hardware looper                       # AI guide with tips
    """
    from .hardware.manual_display import display_section
    from .hardware.llm_interface import ask_hardware_question

    if fast:
        display_section("sp404-sampling.md", "Looper", output_format)
    else:
        response = ask_hardware_question(
            question="Explain the SP-404MK2 looper with creative techniques and workflow tips",
            sections=["hardware/sp404-sampling.md"],
            output_format=output_format
        )
        console.print(response)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Your hardware question"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show which manual sections were loaded"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Ask any hardware question (uses AI with manual context).

    Examples:
        sp404 hardware ask "how do I layer effects with resampling?"
        sp404 hardware ask "what's the best lo-fi workflow?"
        sp404 hardware ask "how to save my project?"
    """
    from .hardware.llm_interface import ask_hardware_question, route_question_to_sections

    # Auto-route to relevant sections
    sections = route_question_to_sections(question)

    if verbose:
        console.print(f"\n[dim]📖 Loading sections: {', '.join([s.split('/')[-1] for s in sections])}[/dim]\n")

    response = ask_hardware_question(
        question=question,
        sections=sections,
        output_format=output_format
    )
    console.print(response)


@app.command()
def manual(
    query: str = typer.Argument(..., help="Search term"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Limit to section"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Search the full manual.

    Examples:
        sp404 hardware manual "bpm sync"
        sp404 hardware manual "button combination" --section sequencer
    """
    from .hardware.manual_display import search_manual

    results = search_manual(query, section)

    if output_format == OutputFormat.rich:
        from rich.table import Table
        table = Table(title=f"Manual Search: '{query}'")
        table.add_column("Section", style="cyan")
        table.add_column("Match", style="white")
        table.add_column("Context", style="dim")

        for result in results[:20]:
            table.add_row(
                result["section"],
                result["match"],
                result["context"][:60] + "..."
            )

        console.print(table)
    else:
        # Other formats...
        pass


# ============================================================================
# WORKFLOW COMMANDS
# ============================================================================

@app.command()
def workflow(
    name: str = typer.Argument(..., help="Workflow name (beatmaking, lofi, sampling, export)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Step-by-step mode"),
    fast: bool = typer.Option(False, "--fast", "-f", help="Quick overview only"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Complete workflow tutorials.

    Examples:
        sp404 hardware workflow beatmaking
        sp404 hardware workflow lofi --interactive
        sp404 hardware workflow sampling --fast
    """
    from .hardware.workflows import get_workflow, run_interactive_workflow

    if interactive:
        run_interactive_workflow(name)
    else:
        workflow_guide = get_workflow(name, use_ai=not fast, output_format=output_format)
        console.print(workflow_guide)


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@app.command()
def tip(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Tip category"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Get a random SP-404 tip.

    Examples:
        sp404 hardware tip
        sp404 hardware tip --category effects
    """
    from .hardware.tips import get_random_tip

    tip = get_random_tip(category, use_ai=True)

    if output_format == OutputFormat.rich:
        from rich.panel import Panel
        console.print(Panel(
            tip,
            title="💡 SP-404 Tip of the Day",
            border_style="cyan"
        ))
    else:
        console.print(tip)


@app.command()
def quickref(
    topic: Optional[str] = typer.Argument(None, help="Specific topic"),
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    Quick reference for common operations.

    Examples:
        sp404 hardware quickref
        sp404 hardware quickref buttons
        sp404 hardware quickref shortcuts
    """
    from .hardware.manual_display import display_quickref

    display_quickref(topic, output_format)


@app.command()
def shortcuts(
    output_format: OutputFormat = typer.Option(OutputFormat.rich, "--format")
):
    """
    List all keyboard shortcuts and button combinations.
    """
    from .hardware.manual_display import display_section

    display_section("sp404-quick-ref.md", "Shortcuts", output_format)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
```

---

### 2. Manual Display Module (`src/hardware/manual_display.py`)

```python
"""
Fast manual section display (no LLM).

Handles instant display of hardware manual sections for quick reference.
"""

from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
import re

console = Console()

MANUAL_DIR = Path(".claude/commands/hardware")


def display_section(
    filename: str,
    section: Optional[str] = None,
    output_format: str = "rich"
) -> None:
    """
    Display a manual section.

    Args:
        filename: Manual file (e.g., "sp404-sampling.md")
        section: Optional section name to extract
        output_format: Output format (rich, markdown, plain, json)
    """
    filepath = MANUAL_DIR / filename

    if not filepath.exists():
        console.print(f"[red]Manual file not found: {filename}[/red]")
        return

    content = filepath.read_text()

    # Extract specific section if requested
    if section:
        content = extract_section(content, section)

    # Limit content for quick display
    if len(content) > 3000 and not section:
        content = content[:3000] + "\n\n[dim]... (use --section for specific topic)[/dim]"

    # Display based on format
    if output_format == "rich":
        console.print(Markdown(content))
    elif output_format == "markdown":
        print(content)
    elif output_format == "plain":
        # Strip markdown formatting
        plain = strip_markdown(content)
        print(plain)
    elif output_format == "json":
        import json
        print(json.dumps({
            "file": filename,
            "section": section,
            "content": content
        }))


def extract_section(content: str, section_name: str) -> str:
    """
    Extract a specific section from manual content.

    Args:
        content: Full manual content
        section_name: Section heading to extract

    Returns:
        Section content
    """
    lines = content.split('\n')
    in_section = False
    section_content = []
    section_level = None

    for line in lines:
        # Check if this is the target section
        if section_name.lower() in line.lower() and line.strip().startswith('#'):
            in_section = True
            section_level = len(line) - len(line.lstrip('#'))
            section_content.append(line)
            continue

        # If in section, collect content
        if in_section:
            # Stop if we hit another section at same or higher level
            if line.strip().startswith('#'):
                current_level = len(line) - len(line.lstrip('#'))
                if current_level <= section_level:
                    break
            section_content.append(line)

    if not section_content:
        return f"Section '{section_name}' not found in manual."

    return '\n'.join(section_content)


def search_manual(query: str, section_filter: Optional[str] = None) -> List[Dict]:
    """
    Search across all manual files.

    Args:
        query: Search term
        section_filter: Optional section to limit search

    Returns:
        List of search results with context
    """
    results = []

    # Determine which files to search
    if section_filter:
        files = [MANUAL_DIR / f"sp404-{section_filter}.md"]
    else:
        files = MANUAL_DIR.glob("sp404-*.md")

    query_lower = query.lower()

    for filepath in files:
        if not filepath.exists():
            continue

        content = filepath.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Get context (2 lines before and after)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = '\n'.join(lines[context_start:context_end])

                results.append({
                    "section": filepath.stem.replace("sp404-", ""),
                    "match": line.strip(),
                    "context": context,
                    "line_number": i + 1
                })

    return results


def display_quickref(topic: Optional[str] = None, output_format: str = "rich") -> None:
    """
    Display quick reference information.

    Args:
        topic: Optional topic filter
        output_format: Output format
    """
    quickrefs = {
        "buttons": {
            "Resample": "Hold [RESAMPLE] + press pads",
            "Looper": "Hold [LOOPER] + press pad",
            "Pattern": "Press [PATTERN] for sequencer",
            "Effects": "Press effect pad to toggle",
            "Save": "[SHIFT] + [PROJECT]"
        },
        "shortcuts": {
            "Undo": "[SHIFT] + [MARK]",
            "BPM Tap": Tap [VALUE] knob",
            "Copy Pad": "[SHIFT] + [COPY] + source + dest",
            "Delete Pad": "[SHIFT] + [DEL] + pad"
        },
        "modes": {
            "Sample Mode": "Default mode, press pads to play",
            "DJ Mode": "[SHIFT] + [SAMPLE]",
            "Pattern Mode": "Press [PATTERN]",
            "TR-REC": "[SHIFT] + [REC] in pattern mode"
        }
    }

    if topic and topic in quickrefs:
        data = {topic: quickrefs[topic]}
    else:
        data = quickrefs

    if output_format == "rich":
        for category, items in data.items():
            table = Table(title=f"{category.title()} Quick Reference")
            table.add_column("Operation", style="cyan")
            table.add_column("Button Combination", style="yellow")

            for op, combo in items.items():
                table.add_row(op, combo)

            console.print(table)
            console.print()
    else:
        # Other formats...
        pass


def strip_markdown(text: str) -> str:
    """
    Strip markdown formatting for plain text output.

    Args:
        text: Markdown text

    Returns:
        Plain text
    """
    # Remove headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove code blocks
    text = re.sub(r'```[^\n]*\n', '', text)
    text = re.sub(r'```', '', text)

    return text
```

---

### 3. LLM Interface Module (`src/hardware/llm_interface.py`)

```python
"""
LLM integration for smart mode hardware assistance.

Wraps the existing sp404_chat.py LLM functionality for CLI use.
"""

import asyncio
from typing import List, Optional
from pathlib import Path

# Import existing chat agent
from sp404_chat import SP404ChatAgent

# Will need to refactor sp404_chat.py to make this reusable
# For now, this is the interface design


def ask_hardware_question(
    question: str,
    sections: Optional[List[str]] = None,
    output_format: str = "rich",
    model: Optional[str] = None
) -> str:
    """
    Ask a hardware question with LLM assistance.

    Args:
        question: Natural language question
        sections: Manual sections to load as context
        output_format: Output format (rich, markdown, plain, json)
        model: Optional model override

    Returns:
        LLM response with manual context
    """
    # Run async function
    return asyncio.run(_ask_hardware_question_async(
        question, sections, output_format, model
    ))


async def _ask_hardware_question_async(
    question: str,
    sections: Optional[List[str]],
    output_format: str,
    model: Optional[str]
) -> str:
    """Async implementation of hardware question."""
    # Initialize agent
    agent = SP404ChatAgent()

    # Override model if specified
    if model:
        agent.model = model

    # Load hardware sections into context
    if sections:
        agent.context.specialist_sections = sections

    # Mark as hardware intent (skip detection)
    agent.context.register_active_tool("hardware_manual")

    # Get response
    response = await agent.process_request(question)

    # Clear sections for next use
    agent.context.specialist_sections = []

    # Format response based on output format
    if output_format == "json":
        import json
        return json.dumps({
            "question": question,
            "answer": response,
            "sections_used": sections or []
        })
    elif output_format == "plain":
        # Strip markdown
        from .manual_display import strip_markdown
        return strip_markdown(response)
    elif output_format == "markdown":
        return response
    else:  # rich
        from rich.markdown import Markdown
        return Markdown(response)


def route_question_to_sections(question: str) -> List[str]:
    """
    Auto-route question to relevant manual sections.

    Uses the existing routing logic from sp404_chat.py

    Args:
        question: User's question

    Returns:
        List of relevant section paths
    """
    agent = SP404ChatAgent()
    sections = agent._route_to_manual_sections(question)
    return sections


def estimate_cost(question: str, sections: List[str]) -> dict:
    """
    Estimate LLM call cost.

    Args:
        question: The question
        sections: Sections to load

    Returns:
        Cost estimate dict
    """
    # Rough token estimation
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")

    # Question tokens
    question_tokens = len(enc.encode(question))

    # Section tokens (approximate)
    section_tokens = 0
    for section_path in sections:
        filepath = Path(".claude/commands") / section_path
        if filepath.exists():
            content = filepath.read_text()
            section_tokens += len(enc.encode(content[:3000]))  # Limit per section

    # System prompt estimate
    system_tokens = 500

    # Total input
    input_tokens = question_tokens + section_tokens + system_tokens

    # Estimate output (assume 500 tokens)
    output_tokens = 500

    # Cost calculation (Qwen 235B pricing)
    input_cost = (input_tokens / 1_000_000) * 0.50  # $0.50 per 1M input tokens
    output_cost = (output_tokens / 1_000_000) * 1.50  # $1.50 per 1M output tokens
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens_estimated": output_tokens,
        "total_tokens_estimated": input_tokens + output_tokens,
        "estimated_cost_usd": total_cost,
        "sections_loaded": len(sections)
    }
```

---

### 4. Workflows Module (`src/hardware/workflows.py`)

```python
"""
Predefined workflow guides for common SP-404 tasks.
"""

from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt

from .llm_interface import ask_hardware_question
from .manual_display import display_section

console = Console()

WORKFLOWS = {
    "beatmaking": {
        "title": "Complete Beat Making Workflow",
        "steps": [
            ("Sampling", "Record or import your drum sounds"),
            ("Pattern Creation", "Create drum pattern with sequencer"),
            ("Effects", "Add effects to individual pads"),
            ("Mixing", "Balance levels in DJ mode"),
            ("Export", "Export final beat for use")
        ],
        "sections": [
            "hardware/sp404-sampling.md",
            "hardware/sp404-sequencer.md",
            "hardware/sp404-effects.md",
            "hardware/sp404-performance.md",
            "hardware/sp404-file-mgmt.md"
        ]
    },

    "lofi": {
        "title": "Lo-Fi Hip-Hop Production Workflow",
        "steps": [
            ("Sample Selection", "Choose jazzy, soulful samples"),
            ("Lo-Fi Effects", "Apply Cassette Sim, Vinyl Sim, Lo-fi effect"),
            ("Resampling", "Layer and freeze effects"),
            ("Pattern", "Create laid-back drum pattern"),
            ("Final Mix", "Balance everything in DJ mode")
        ],
        "sections": [
            "hardware/sp404-sampling.md",
            "hardware/sp404-effects.md",
            "hardware/sp404-sequencer.md"
        ]
    },

    "sampling": {
        "title": "Sample Collection and Organization Workflow",
        "steps": [
            ("Recording", "Record samples from external sources"),
            ("Editing", "Trim, mark, and process samples"),
            ("Organizing", "Arrange in banks by type/genre"),
            ("Backup", "Export to SD card for safety"),
            ("Documentation", "Tag and note sample details")
        ],
        "sections": [
            "hardware/sp404-sampling.md",
            "hardware/sp404-file-mgmt.md"
        ]
    },

    "export": {
        "title": "Sample Export and Organization Workflow",
        "steps": [
            ("Prepare", "Ensure samples are 48kHz/16-bit"),
            ("Organize", "Group by type/genre/BPM"),
            ("Export", "Use export service or manual SD card"),
            ("Import to SP-404", "Load into correct project/bank"),
            ("Test", "Verify all samples load correctly")
        ],
        "sections": [
            "hardware/sp404-file-mgmt.md"
        ]
    }
}


def get_workflow(
    name: str,
    use_ai: bool = True,
    output_format: str = "rich"
) -> str:
    """
    Get a workflow guide.

    Args:
        name: Workflow name
        use_ai: Use AI for enhanced guide (vs. basic steps)
        output_format: Output format

    Returns:
        Workflow guide content
    """
    if name not in WORKFLOWS:
        return f"Unknown workflow: {name}. Available: {', '.join(WORKFLOWS.keys())}"

    workflow = WORKFLOWS[name]

    if use_ai:
        # Use LLM for comprehensive guide
        question = f"Guide me through the {workflow['title']} on SP-404MK2, with detailed steps, tips, and creative techniques"

        response = ask_hardware_question(
            question=question,
            sections=workflow["sections"],
            output_format=output_format
        )
        return response
    else:
        # Fast mode - just list steps
        steps_md = f"# {workflow['title']}\n\n"
        for i, (step, desc) in enumerate(workflow['steps'], 1):
            steps_md += f"{i}. **{step}**: {desc}\n"

        if output_format == "rich":
            return Markdown(steps_md)
        else:
            return steps_md


def run_interactive_workflow(name: str) -> None:
    """
    Run a workflow in interactive step-by-step mode.

    Args:
        name: Workflow name
    """
    if name not in WORKFLOWS:
        console.print(f"[red]Unknown workflow: {name}[/red]")
        return

    workflow = WORKFLOWS[name]

    console.print(f"\n[bold cyan]{workflow['title']}[/bold cyan]\n")
    console.print("This interactive guide will walk you through each step.\n")

    for i, (step, desc) in enumerate(workflow['steps'], 1):
        console.print(f"\n[bold]Step {i}/{len(workflow['steps'])}: {step}[/bold]")
        console.print(f"[dim]{desc}[/dim]\n")

        # Get AI guidance for this step
        question = f"Explain the '{step}' step for {workflow['title']}, with specific SP-404MK2 instructions"

        # Use relevant sections
        response = ask_hardware_question(
            question=question,
            sections=workflow["sections"]
        )

        console.print(response)
        console.print()

        # Wait for user to complete step
        if i < len(workflow['steps']):
            if not Confirm.ask(f"Ready for step {i+1}?"):
                console.print("\n[yellow]Workflow paused. Run again to continue.[/yellow]")
                return

    console.print("\n[bold green]✓ Workflow complete![/bold green]")
    console.print("[dim]Great work! Your beat/project is ready.[/dim]\n")
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# scripts/test_cli_hardware.py

import pytest
from typer.testing import CliRunner
from src.cli_hardware import app

runner = CliRunner()

def test_fast_mode_commands():
    """Test all commands in fast mode (no LLM)."""
    commands = [
        ["resample", "--fast"],
        ["effects", "--list"],
        ["pattern", "--fast"],
        ["looper", "--fast"],
        ["quickref"]
    ]

    for cmd in commands:
        result = runner.invoke(app, cmd)
        assert result.exit_code == 0
        assert "error" not in result.stdout.lower()

def test_smart_mode_mock():
    """Test smart mode with mocked LLM (avoid API costs)."""
    # Mock the LLM interface
    # ... mock implementation ...

    result = runner.invoke(app, ["resample"])
    assert result.exit_code == 0

def test_workflow_commands():
    """Test workflow commands."""
    workflows = ["beatmaking", "lofi", "sampling", "export"]

    for workflow in workflows:
        result = runner.invoke(app, ["workflow", workflow, "--fast"])
        assert result.exit_code == 0

def test_search():
    """Test manual search."""
    result = runner.invoke(app, ["manual", "resample"])
    assert result.exit_code == 0
    assert "resample" in result.stdout.lower()

def test_output_formats():
    """Test different output formats."""
    formats = ["rich", "markdown", "plain", "json"]

    for fmt in formats:
        result = runner.invoke(app, ["resample", "--fast", "--format", fmt])
        assert result.exit_code == 0
```

### Integration Tests

```python
def test_llm_integration():
    """Test actual LLM calls (use with caution - costs money)."""
    # Only run when explicitly enabled
    import os
    if not os.getenv("RUN_LLM_TESTS"):
        pytest.skip("LLM tests disabled")

    result = runner.invoke(app, ["ask", "how do I resample?"])
    assert result.exit_code == 0
    assert "resample" in result.stdout.lower()
```

---

## 📖 Usage Examples Document

Create `docs/plans/TYPER_CLI_USAGE_EXAMPLES.md` with:

- 50+ usage examples
- Real-world scenarios
- Scripting examples
- Shell integration examples

---

## 🚀 Entry Point Configuration

### Add to `pyproject.toml` (if exists)

```toml
[tool.poetry.scripts]
sp404 = "src.cli_hardware:main"
sp404-hardware = "src.cli_hardware:main"
```

### Or add to `setup.py` (if exists)

```python
entry_points={
    'console_scripts': [
        'sp404=src.cli_hardware:main',
        'sp404-hardware=src.cli_hardware:main',
    ],
}
```

---

## 📊 Success Metrics

### Phase 1 Complete When:
- ✅ 5 basic commands working
- ✅ Fast mode response < 1s
- ✅ Help text displays properly
- ✅ Manual sections display correctly

### Phase 2 Complete When:
- ✅ LLM integration functional
- ✅ Smart mode provides good answers
- ✅ Cost tracking working
- ✅ No breaking changes to sp404_chat.py

### Phase 3 Complete When:
- ✅ 4 workflow commands work
- ✅ Tip of the day functional
- ✅ Interactive mode prototype complete

### Phase 4 Complete When:
- ✅ Shell completion works
- ✅ 3 example scripts created
- ✅ Multiple output formats work
- ✅ CLI is fully scriptable

### Phase 5 Complete When:
- ✅ Test suite passes
- ✅ Documentation complete
- ✅ Usage examples published

---

## 💰 Cost Considerations

### Fast Mode
- **Cost**: $0 (no LLM calls)
- **Use for**: Quick lookups during production

### Smart Mode
- **Cost**: ~$0.0001-0.0003 per query
- **Depends on**: Manual sections loaded, question complexity
- **Use for**: Learning, creative suggestions

### Cost Tracking
- All LLM calls logged to database
- Same tracking as sp404_chat.py
- View with: `sp404 downloads stats`

---

## 🔮 Future Enhancements (Phase 6+)

### Voice Integration
- `sp404 hardware ask --voice "how do I resample?"`
- Speak questions, hear answers

### Video Tutorials
- Link to timestamped YouTube tutorials
- Auto-generate tutorial links

### Community Tips
- Share tips with other users
- Vote on best tips
- Integrate with forums

### Hardware Simulator
- Visual button diagram
- Interactive practice mode
- Record and playback sessions

---

## ✅ Pre-Implementation Checklist

Before starting implementation:

- [ ] Review this plan with team/user
- [ ] Confirm priority and timeline
- [ ] Ensure hardware manual integration is complete
- [ ] Verify sp404_chat.py refactoring scope
- [ ] Prepare test environment
- [ ] Set up cost tracking alerts
- [ ] Create implementation branch
- [ ] Schedule development time blocks

---

## 📝 Notes

**Current Status**: 📋 Planning Complete, Ready for Implementation

**Dependencies Met**:
- ✅ Hardware manual extracted (6 sections)
- ✅ sp404_chat.py LLM integration working
- ✅ Typer already in requirements
- ✅ Rich formatting available

**Blocking Issues**: None

**Estimated Total Time**: 2-3 days
**Estimated Total Cost** (LLM testing): ~$0.50

**Priority**: Medium (nice-to-have, not critical)

**Value Proposition**:
- Fast CLI for quick hardware lookups
- Complements conversational interface
- Scriptable for automation
- Shell completion for discoverability

---

**Plan Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Author**: Claude Code (SP-404MK2 Sample Agent Project)
