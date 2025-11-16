# Database Schemas - SP404MK2 Sample Agent

## Database Overview

**Type**: SQLite with async support (aiosqlite)
**ORM**: SQLAlchemy 2.0 (async)
**Migrations**: Alembic
**Location**: `sp404_samples.db`

## Core Tables

### samples
Audio sample metadata and storage.

```sql
CREATE TABLE samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(512) NOT NULL UNIQUE,
    genre VARCHAR(50),
    bpm FLOAT,
    key VARCHAR(10),
    duration FLOAT,
    file_size INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_genre ON samples(genre);
CREATE INDEX idx_samples_name ON samples(name);
CREATE INDEX idx_samples_created_at ON samples(created_at);
```

**SQLAlchemy Model** (`backend/app/models/sample.py`):
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    file_path = Column(String(512), nullable=False, unique=True)
    genre = Column(String(50), index=True)
    bpm = Column(Float)
    key = Column(String(10))
    duration = Column(Float)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audio_features = relationship("AudioFeatures", back_populates="sample", uselist=False, cascade="all, delete-orphan")
    batch_samples = relationship("BatchSample", back_populates="sample")
    kits = relationship("Kit", secondary="kit_samples", back_populates="samples")
```

### audio_features
Extracted audio features from librosa analysis.

```sql
CREATE TABLE audio_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id INTEGER NOT NULL UNIQUE,
    bpm FLOAT,
    tempo_confidence FLOAT,
    onset_rate FLOAT,
    key VARCHAR(10),
    scale VARCHAR(10),
    spectral_centroid FLOAT,
    spectral_rolloff FLOAT,
    spectral_bandwidth FLOAT,
    spectral_flatness FLOAT,
    zero_crossing_rate FLOAT,
    rms_energy FLOAT,
    harmonic_percussive_ratio FLOAT,
    mfcc_coefficients TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

CREATE INDEX idx_audio_features_sample_id ON audio_features(sample_id);
CREATE INDEX idx_audio_features_bpm ON audio_features(bpm);
```

**SQLAlchemy Model** (`backend/app/models/audio_features.py`):
```python
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

class AudioFeatures(Base):
    __tablename__ = "audio_features"

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Rhythm features
    bpm = Column(Float)
    tempo_confidence = Column(Float)
    onset_rate = Column(Float)

    # Musical features
    key = Column(String(10))
    scale = Column(String(10))

    # Spectral features
    spectral_centroid = Column(Float)
    spectral_rolloff = Column(Float)
    spectral_bandwidth = Column(Float)
    spectral_flatness = Column(Float)

    # Temporal features
    zero_crossing_rate = Column(Float)
    rms_energy = Column(Float)

    # Advanced features
    harmonic_percussive_ratio = Column(Float)
    mfcc_coefficients = Column(Text)  # JSON serialized

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="audio_features")
```

### batches
Batch processing jobs for multiple samples.

```sql
CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    source_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    progress INTEGER DEFAULT 0,
    total_samples INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE INDEX idx_batches_status ON batches(status);
```

**SQLAlchemy Model** (`backend/app/models/batch.py`):
```python
class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_url = Column(Text)
    status = Column(String(20), default="pending", index=True)
    progress = Column(Integer, default=0)
    total_samples = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    batch_samples = relationship("BatchSample", back_populates="batch", cascade="all, delete-orphan")
```

### batch_samples
Association between batches and samples (one-to-many).

```sql
CREATE TABLE batch_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

CREATE INDEX idx_batch_samples_batch_id ON batch_samples(batch_id);
CREATE INDEX idx_batch_samples_sample_id ON batch_samples(sample_id);
```

### user_preferences
User settings for AI models and auto-analysis (single row, id=1).

```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row
    vibe_model VARCHAR(100) DEFAULT 'qwen/qwen3-7b-it',
    batch_model VARCHAR(100) DEFAULT 'qwen/qwen3-7b-it',
    auto_analyze_single BOOLEAN DEFAULT FALSE,
    auto_analyze_batch BOOLEAN DEFAULT FALSE,
    auto_extract_features BOOLEAN DEFAULT TRUE,
    max_cost_per_request FLOAT DEFAULT 0.01,
    default_export_format VARCHAR(10) DEFAULT 'WAV',
    default_organization VARCHAR(20) DEFAULT 'flat',
    auto_sanitize_filenames BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default row
INSERT INTO user_preferences (id) VALUES (1);
```

**SQLAlchemy Model** (`backend/app/models/user_preferences.py`):
```python
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=False)

    # AI model settings
    vibe_model = Column(String(100), default="qwen/qwen3-7b-it")
    batch_model = Column(String(100), default="qwen/qwen3-7b-it")

    # Auto-analysis settings
    auto_analyze_single = Column(Boolean, default=False)
    auto_analyze_batch = Column(Boolean, default=False)
    auto_extract_features = Column(Boolean, default=True)
    max_cost_per_request = Column(Float, default=0.01)

    # SP-404MK2 export settings
    default_export_format = Column(String(10), default="WAV")
    default_organization = Column(String(20), default="flat")
    auto_sanitize_filenames = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### api_usage
API cost tracking for OpenRouter calls.

```sql
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    total_cost FLOAT NOT NULL,
    operation VARCHAR(50),  -- vibe_analysis, batch_processing, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_api_usage_model ON api_usage(model);
```

### sp404_exports
SP-404MK2 export operations tracking.

```sql
CREATE TABLE sp404_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_format VARCHAR(10) NOT NULL,  -- WAV or AIFF
    organization_strategy VARCHAR(20) NOT NULL,  -- flat, genre, bpm, kit
    output_path VARCHAR(512) NOT NULL,
    file_count INTEGER DEFAULT 0,
    total_size INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE INDEX idx_sp404_exports_status ON sp404_exports(status);
```

### sp404_export_samples
Individual samples in an export operation.

```sql
CREATE TABLE sp404_export_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    output_filename VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (export_id) REFERENCES sp404_exports(id) ON DELETE CASCADE,
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

CREATE INDEX idx_sp404_export_samples_export_id ON sp404_export_samples(export_id);
CREATE INDEX idx_sp404_export_samples_sample_id ON sp404_export_samples(sample_id);
```

## Relationships

### One-to-One
- `samples` ↔ `audio_features` (one sample has one audio_features record)

### One-to-Many
- `batches` → `batch_samples` (one batch has many samples)
- `sp404_exports` → `sp404_export_samples` (one export has many samples)

### Many-to-Many
- `kits` ↔ `samples` through `kit_samples` association table

## Query Patterns

### Eager Loading (Prevent N+1)
```python
from sqlalchemy.orm import selectinload

# Load sample with audio features
query = select(Sample).options(selectinload(Sample.audio_features))
result = await db.execute(query)
sample = result.scalar_one()

# Access features without additional query
print(sample.audio_features.bpm)
```

### Filtering
```python
# Filter by genre and BPM range
query = select(Sample).where(
    and_(
        Sample.genre == "hip-hop",
        Sample.bpm.between(80, 100)
    )
)
```

### Aggregation
```python
from sqlalchemy import func

# Count samples by genre
query = select(
    Sample.genre,
    func.count(Sample.id).label("count")
).group_by(Sample.genre)

result = await db.execute(query)
counts = result.all()  # [("hip-hop", 50), ("jazz", 30), ...]
```

## Migration Commands

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Indexes Strategy

### High Priority Indexes
- Foreign keys (automatic in SQLite)
- Frequently filtered columns (`genre`, `status`, `bpm`)
- Frequently sorted columns (`created_at`)

### Query Optimization
- Use indexes for WHERE, JOIN, ORDER BY
- Use eager loading for relationships
- Avoid N+1 queries
- Use pagination for large result sets
