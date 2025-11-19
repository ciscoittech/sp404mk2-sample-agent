# Contributing to SP404MK2 Sample Agent

Thank you for your interest in contributing to the SP404MK2 Sample Agent! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project is dedicated to providing a welcoming and harassment-free experience for everyone. We expect all contributors to:

- Be respectful and considerate
- Focus on constructive feedback
- Accept differing viewpoints gracefully
- Prioritize the community and project health

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Sample files or logs** (if applicable)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear use case** - Why is this enhancement needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - What other approaches did you consider?

### Contributing Code

We welcome code contributions! Areas where you can help:

1. **Audio Analysis**: Improve BPM/key detection accuracy
2. **AI Integration**: Enhance vibe analysis prompts and models
3. **SP-404 Features**: Add new hardware export formats or templates
4. **UI/UX**: Improve React frontend components
5. **Documentation**: Improve guides, add examples, fix typos
6. **Testing**: Add test coverage for edge cases

## Development Setup

### Prerequisites

- **Python 3.13+**
- **Node.js 20+**
- **FFmpeg** (for audio processing)
- **PostgreSQL** (or use Docker)

### Local Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .

# Install frontend dependencies
cd react-app
npm install
cd ..

# Copy environment file and configure
cp .env.example .env
# Edit .env with your API keys and settings

# Initialize database
cd backend
../venv/bin/python -m app.db.init_db
cd ..

# Run tests to verify setup
make test
```

### Docker Setup (Alternative)

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Build and start services
make docker-build
make docker-up
make docker-db-init

# Run tests in Docker
make docker-test
```

## Project Structure

```
sp404mk2-sample-agent/
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── core/         # Config and utilities
│   ├── tests/            # Backend tests
│   └── alembic/          # Database migrations
├── react-app/            # React 19 frontend
│   ├── src/              # React source code
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── api/          # API client
│   │   └── hooks/        # Custom hooks
│   └── tests/            # Frontend tests
├── src/                  # Legacy Python CLI
│   ├── agents/           # AI agent implementations
│   ├── tools/            # Tool implementations
│   └── config.py         # Configuration
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── samples/              # Sample files (gitignored)
```

## Coding Standards

### Python

- **Style**: Follow PEP 8
- **Formatter**: Use `black` with 100-character line length
- **Imports**: Use `isort` with black profile
- **Type Hints**: Required for all public functions
- **Docstrings**: Use Google-style docstrings

```python
def analyze_sample(file_path: str, model: str = "qwen/qwen3-7b-it") -> dict:
    """
    Analyze an audio sample using AI.

    Args:
        file_path: Path to the audio file
        model: OpenRouter model ID to use

    Returns:
        Dictionary with analysis results (BPM, key, vibe)

    Raises:
        ValueError: If file_path doesn't exist
    """
    pass
```

### TypeScript/React

- **Style**: Follow Airbnb style guide
- **Formatter**: Prettier with project config
- **Type Safety**: Enable strict mode
- **Components**: Use functional components with hooks

```typescript
interface SampleCardProps {
  sample: Sample;
  onAnalyze?: (id: string) => void;
}

export function SampleCard({ sample, onAnalyze }: SampleCardProps) {
  // Component implementation
}
```

### Running Code Quality Tools

```bash
# Python
make format          # Auto-format code
make lint           # Check code quality

# TypeScript
cd react-app
npm run lint        # Check code quality
npm run format      # Auto-format code
```

## Testing Guidelines

We use pytest for backend testing and Playwright for E2E tests.

### Writing Tests

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions
- **E2E Tests**: Test complete user workflows

### Test Organization

```python
# backend/tests/services/test_audio_features.py
import pytest
from app.services.audio_features_service import AudioFeaturesService

class TestAudioFeaturesService:
    """Tests for AudioFeaturesService."""

    def test_detect_bpm_basic(self, sample_audio_file):
        """Test BPM detection on a simple audio file."""
        service = AudioFeaturesService()
        result = service.detect_bpm(sample_audio_file)
        assert 80 <= result["bpm"] <= 180

    def test_detect_bpm_invalid_file(self):
        """Test BPM detection handles invalid files gracefully."""
        service = AudioFeaturesService()
        with pytest.raises(ValueError):
            service.detect_bpm("nonexistent.wav")
```

### Running Tests

```bash
# All tests
make test

# Specific test suites
make test-unit           # Unit tests only
make test-integration    # Integration tests
make test-e2e           # End-to-end tests

# With coverage
make coverage

# In Docker
make docker-test
```

### Test Coverage Goals

- **New features**: 80%+ coverage required
- **Bug fixes**: Add regression test
- **Critical paths**: 100% coverage (authentication, data loss scenarios)

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(audio): Add Essentia BPM detection with fallback to librosa

Implements multi-algorithm BPM detection using Essentia's multifeature
and degara methods. Falls back to librosa if Essentia is unavailable.

Closes #123
```

```
fix(api): Prevent duplicate sample analysis requests

Add request deduplication to avoid concurrent analysis of the same
sample, which was causing database conflicts.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make your changes**
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

4. **Run quality checks**
   ```bash
   make lint
   make test
   ```

5. **Update CHANGELOG.md** (if applicable)

### Submitting PR

1. **Push to your fork**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Open Pull Request** on GitHub with:
   - **Clear title** following conventional commits format
   - **Description** explaining what and why
   - **Issue references** (e.g., "Closes #123")
   - **Screenshots** (for UI changes)
   - **Testing notes** (how to verify)

3. **PR Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Motivation
   Why is this change needed?

   ## Changes
   - Added X feature
   - Fixed Y bug
   - Updated Z documentation

   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ## Screenshots (if applicable)

   ## Related Issues
   Closes #123
   ```

### Review Process

- Maintainers will review within 3-5 business days
- Address feedback promptly
- Keep PR focused on a single concern
- Be patient and respectful during review

### After Approval

- Maintainer will merge using squash merge
- Your PR becomes part of the next release
- Celebrate your contribution!

## Development Workflow

### Feature Development

1. **Check existing issues** or create new one
2. **Discuss approach** in issue comments
3. **Fork and branch** from `main`
4. **Develop with tests** - TDD encouraged
5. **Submit PR** following guidelines above

### Bug Fixes

1. **Create issue** with reproduction steps
2. **Write failing test** demonstrating bug
3. **Fix bug** and verify test passes
4. **Submit PR** with test + fix

### Documentation

Documentation improvements are always welcome:

- Fix typos or unclear sections
- Add examples and tutorials
- Improve API documentation
- Create guides for new features

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Discord**: (Coming soon) Real-time chat with community

### Recognition

Contributors are recognized in:

- `CHANGELOG.md` for releases
- GitHub contributors page
- Special thanks in release notes

## Questions?

Don't hesitate to ask! Open an issue with the "question" label or reach out in GitHub Discussions.

---

Thank you for contributing to SP404MK2 Sample Agent! Your efforts help the SP-404 community create better music.
