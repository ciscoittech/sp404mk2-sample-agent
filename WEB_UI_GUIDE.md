# SP404MK2 Sample Agent - Web UI Guide

## 🌐 Yes! There IS a Complete Web UI!

You have **BOTH** a CLI and a Web Interface:

1. **CLI Interface** (`sp404_chat.py`) - Natural language chat
2. **Web UI** (FastAPI + HTMX + DaisyUI) - Full-featured dashboard

---

## 🚀 How to Run the Web UI

### Option 1: Docker (Recommended)

```bash
# Start everything with Docker
make docker-up

# Initialize the database
make docker-db-init

# Access the web UI
open http://localhost:8000
```

### Option 2: Local Development

```bash
# Start the FastAPI backend
cd backend
python run.py

# The web UI will be available at:
http://localhost:8000
```

---

## 🎨 Web UI Features

### Main Dashboard (`http://localhost:8000`)
- **Homepage**: Welcome screen with navigation
- **Sample Browser**: View and manage collected samples
- **Batch Processor**: Process multiple samples at once
- **Kit Builder**: Organize samples into SP-404MK2 kits
- **Vibe Analysis**: Real-time WebSocket vibe analysis

### Available Pages

1. **`/pages/samples.html`** - Sample Browser
   - View all collected samples
   - Search and filter
   - Download samples
   - View metadata (BPM, key, genre)

2. **`/pages/batch.html`** - Batch Processor
   - Upload multiple samples
   - AI batch analysis
   - Progress tracking
   - Bulk organization

3. **`/pages/batch-new.html`** - New Batch Creation
   - Create batch collection tasks
   - Configure AI analysis settings
   - Set target genres/styles

4. **`/pages/kits.html`** - Kit Builder
   - Organize samples into kits
   - SP-404MK2 bank layout
   - Export kit metadata

5. **`/pages/vibe-analysis.html`** - Vibe Analysis
   - Real-time WebSocket analysis
   - Detailed mood/era/genre breakdown
   - Compatibility suggestions

---

## 🏗️ Web Architecture

```
FastAPI Backend (Port 8000)
├── REST API (/api/v1/)
│   ├── /samples - Sample CRUD
│   ├── /batches - Batch processing
│   ├── /kits - Kit management
│   └── /vibe - Vibe analysis
├── WebSocket (/ws/vibe/{id})
│   └── Real-time vibe analysis
└── Static Files
    ├── /static - CSS, JS
    ├── /pages - HTML pages
    └── / - Frontend root

Frontend (HTMX + DaisyUI)
├── HTMX for server-driven UI updates
├── DaisyUI (Tailwind CSS) for styling
├── Alpine.js for minimal interactivity
└── WebSocket for real-time updates
```

---

## 📊 API Endpoints

### Samples API
```
GET    /api/v1/samples         - List all samples
POST   /api/v1/samples         - Create new sample
GET    /api/v1/samples/{id}    - Get sample details
PUT    /api/v1/samples/{id}    - Update sample
DELETE /api/v1/samples/{id}    - Delete sample
```

### Batch API
```
GET    /api/v1/batches         - List batches
POST   /api/v1/batches         - Create batch
GET    /api/v1/batches/{id}    - Get batch status
POST   /api/v1/batches/{id}/process - Start processing
GET    /api/v1/batches/{id}/results - Get results
```

### Vibe Analysis API
```
POST   /api/v1/vibe/analyze    - Analyze single sample
WS     /ws/vibe/{sample_id}    - WebSocket real-time analysis
```

### Kits API
```
GET    /api/v1/kits            - List kits
POST   /api/v1/kits            - Create kit
GET    /api/v1/kits/{id}       - Get kit details
PUT    /api/v1/kits/{id}       - Update kit
```

---

## 🎯 What You Can Do in the Web UI

### 1. Sample Management
- **Browse Collection**: View all samples in a table
- **Search & Filter**: By genre, BPM, key, mood
- **Download Samples**: Direct download links
- **View Metadata**: Complete sample information
- **Edit Details**: Update tags, notes, ratings

### 2. Batch Processing
- **Upload Multiple Files**: Drag & drop interface
- **AI Analysis**: Automatic BPM, key, genre detection
- **Progress Tracking**: Real-time progress bar
- **Bulk Import**: Add results to sample database
- **Review Results**: Quality scoring and recommendations

### 3. Kit Building
- **Create Kits**: Organize samples into sets
- **SP-404MK2 Layout**: Bank A-F, Pad 1-12 layout
- **Drag & Drop**: Easy sample assignment
- **Export Metadata**: JSON export for SP-404MK2
- **Compatibility Groups**: Auto-suggest compatible samples

### 4. Vibe Analysis
- **Real-time Analysis**: WebSocket live updates
- **Mood Detection**: Emotional quality analysis
- **Era Classification**: Time period identification
- **Genre Tagging**: Automatic genre assignment
- **Compatibility Matching**: Find similar samples

---

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Async database ORM
- **Pydantic**: Data validation
- **WebSockets**: Real-time communication
- **OpenRouter API**: AI model access

### Frontend
- **HTMX**: Server-driven UI updates (no React/Vue needed!)
- **DaisyUI**: Beautiful Tailwind CSS components
- **Alpine.js**: Minimal JavaScript framework
- **WebSocket API**: Real-time updates

### Database
- **SQLite**: Local development
- **Turso**: Production (optional)

---

## 📸 Web UI Screenshots

The project includes a screenshot at:
```
frontend/debug-screenshot.png (1.1 MB)
```

---

## 🔌 Integration with CLI

Both interfaces share the same backend:

**CLI (`sp404_chat.py`):**
- Natural language sample discovery
- YouTube video analysis
- Conversational interface
- Terminal-based workflow

**Web UI (`http://localhost:8000`):**
- Visual sample browser
- Batch processing interface
- Kit building tools
- Real-time vibe analysis

**Shared:**
- Same database
- Same AI models
- Same intelligent context manager
- Same thinking protocols

---

## 🚦 Quick Start Commands

### Start Web UI (Docker)
```bash
# Full stack
make docker-up
make docker-db-init
open http://localhost:8000
```

### Start Web UI (Local)
```bash
# Backend only
cd backend
python run.py

# Access at http://localhost:8000
```

### Start CLI
```bash
# Natural language interface
python3 sp404_chat.py
```

### Run Both at Once
```bash
# Terminal 1: Web UI
cd backend && python run.py

# Terminal 2: CLI
python3 sp404_chat.py
```

---

## 📁 Project Structure

```
sp404mk2-sample-agent/
├── backend/                # FastAPI web backend
│   ├── app/
│   │   ├── main.py        # FastAPI app entry
│   │   ├── api/v1/        # REST API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── run.py             # Dev server
│   └── requirements.txt
│
├── frontend/              # HTMX + DaisyUI frontend
│   ├── index.html         # Homepage
│   ├── pages/             # UI pages
│   │   ├── samples.html
│   │   ├── batch.html
│   │   ├── kits.html
│   │   └── vibe-analysis.html
│   ├── static/            # CSS, JS, images
│   └── components/        # Reusable components
│
├── sp404_chat.py          # CLI interface
├── docker-compose.yml     # Docker setup
└── Makefile              # Quick commands
```

---

## 🎨 UI Features

### HTMX + DaisyUI Benefits
- **No heavy JavaScript frameworks**: HTMX does server-driven updates
- **Beautiful components**: DaisyUI provides Tailwind CSS themes
- **Fast loading**: Minimal client-side JavaScript
- **Easy to maintain**: Server-side rendering
- **Real-time updates**: WebSocket + HTMX integration

### Example: Vibe Analysis Page
```html
<!-- Real-time WebSocket vibe analysis -->
<div hx-ws="connect:/ws/vibe/123">
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Vibe Analysis</h2>
      <div id="vibe-results" hx-ws="send">
        <!-- Results stream here in real-time -->
      </div>
    </div>
  </div>
</div>
```

---

## 🧪 Testing the Web UI

### E2E Tests (Playwright)
```bash
# Run end-to-end tests
cd frontend
npm install
npx playwright test

# Tests cover:
# - Sample browser functionality
# - Batch processing workflow
# - Kit builder operations
# - WebSocket vibe analysis
```

### Test Coverage
- **Backend**: 27% core coverage
- **Frontend E2E**: 100% UI coverage
- **66 Playwright tests**: All passing

---

## 🔐 Security

- **API Key Management**: Environment variables only
- **CORS**: Configured for localhost development
- **File Upload**: Size and type validation
- **Database**: Async SQLite with ORM
- **WebSocket**: Connection authentication

---

## 📝 Environment Variables

Create a `.env` file:

```bash
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
DATABASE_URL=sqlite+aiosqlite:///./data/sp404.db
SECRET_KEY=your-secret-key-here
BACKEND_CORS_ORIGINS=["http://localhost:8000"]
```

---

## 🎯 Next Steps

1. **Start the Web UI**: `make docker-up` or `cd backend && python run.py`
2. **Open browser**: http://localhost:8000
3. **Explore features**: Sample browser, batch processing, kit builder
4. **Or use CLI**: `python3 sp404_chat.py` for natural language interface

---

## 💡 Pro Tips

1. **Use Docker for full stack**: Includes database, backend, and frontend
2. **CLI for discovery**: Best for natural language sample searching
3. **Web UI for organization**: Best for batch processing and kit building
4. **Both can run simultaneously**: They share the same database
5. **WebSocket for real-time**: Watch vibe analysis happen live

---

*You have TWO powerful interfaces - choose the one that fits your workflow!* 🎵
