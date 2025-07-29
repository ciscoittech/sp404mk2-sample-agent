# Database Engineer Specialist

**Command**: `/database-engineer`

Database specialist for designing scalable schemas, optimizing queries, and managing data integrity for the SP404MK2 sample system.

## Expertise Areas

### Database Design
- **Schema Design**: Normalization, denormalization strategies
- **Data Modeling**: Entity relationships, constraints
- **Migration Strategy**: Version control, rollback plans
- **Multi-tenancy**: User data isolation, security

### Performance Optimization
- **Query Optimization**: Explain plans, index strategies
- **Caching**: Redis integration, cache invalidation
- **Connection Pooling**: Optimal configuration
- **Partitioning**: Time-based, user-based strategies

### Data Integrity
- **Constraints**: Foreign keys, check constraints
- **Transactions**: ACID compliance, isolation levels
- **Backup/Recovery**: Automated backups, point-in-time recovery
- **Auditing**: Change tracking, compliance

### Turso/SQLite Specific
- **Edge Deployment**: Replica configuration
- **Sync Strategy**: Primary/replica consistency
- **Embedded Features**: JSON support, full-text search
- **Performance Tuning**: PRAGMA settings, WAL mode

## Schema Design

### Core Tables
```sql
-- Users table with auth and profile
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    storage_quota_mb INTEGER DEFAULT 1000,
    storage_used_mb INTEGER DEFAULT 0,
    
    -- Indexes for common queries
    CREATE INDEX idx_users_email ON users(email);
    CREATE INDEX idx_users_username ON users(username);
);

-- Samples table with metadata
CREATE TABLE samples (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    duration_ms INTEGER,
    sample_rate INTEGER,
    bit_depth INTEGER,
    channels INTEGER DEFAULT 2,
    
    -- Metadata
    bpm REAL,
    musical_key TEXT,
    genre TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    CREATE INDEX idx_samples_user_created ON samples(user_id, created_at DESC);
    CREATE INDEX idx_samples_genre_bpm ON samples(genre, bpm);
    CREATE INDEX idx_samples_analyzed ON samples(analyzed_at) WHERE analyzed_at IS NOT NULL;
);

-- Vibe analysis results
CREATE TABLE vibe_analyses (
    id INTEGER PRIMARY KEY,
    sample_id INTEGER NOT NULL UNIQUE,
    
    -- Core vibe data
    energy_level REAL CHECK (energy_level BETWEEN 0 AND 1),
    mood_primary TEXT NOT NULL,
    mood_secondary TEXT,
    texture_tags JSON DEFAULT '[]',
    
    -- Musical characteristics
    danceability REAL CHECK (danceability BETWEEN 0 AND 1),
    acousticness REAL CHECK (acousticness BETWEEN 0 AND 1),
    instrumentalness REAL CHECK (instrumentalness BETWEEN 0 AND 1),
    
    -- Analysis metadata
    model_version TEXT NOT NULL,
    confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 1),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

-- Sample collections/kits
CREATE TABLE kits (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    pad_layout JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CREATE INDEX idx_kits_user ON kits(user_id);
    CREATE INDEX idx_kits_public ON kits(is_public) WHERE is_public = TRUE;
);

-- Many-to-many relationship for kit samples
CREATE TABLE kit_samples (
    kit_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    pad_number INTEGER CHECK (pad_number BETWEEN 1 AND 16),
    pad_bank TEXT CHECK (pad_bank IN ('A', 'B', 'C', 'D')),
    volume REAL DEFAULT 1.0 CHECK (volume BETWEEN 0 AND 1),
    pitch_shift INTEGER DEFAULT 0,
    
    PRIMARY KEY (kit_id, sample_id),
    FOREIGN KEY (kit_id) REFERENCES kits(id) ON DELETE CASCADE,
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    
    -- Ensure unique pad assignment per kit
    UNIQUE(kit_id, pad_bank, pad_number)
);

-- Tags for categorization
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT, -- 'genre', 'mood', 'instrument', etc.
    usage_count INTEGER DEFAULT 0,
    
    CREATE INDEX idx_tags_category ON tags(category);
);

-- Sample tags (many-to-many)
CREATE TABLE sample_tags (
    sample_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    
    PRIMARY KEY (sample_id, tag_id),
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Processing queue
CREATE TABLE processing_queue (
    id INTEGER PRIMARY KEY,
    sample_id INTEGER NOT NULL,
    task_type TEXT NOT NULL, -- 'analyze_vibe', 'extract_bpm', etc.
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    CREATE INDEX idx_queue_status_priority ON processing_queue(status, priority DESC) WHERE status = 'pending';
);
```

### Optimized Views
```sql
-- Sample library view with all metadata
CREATE VIEW sample_library AS
SELECT 
    s.*,
    u.username,
    va.mood_primary,
    va.energy_level,
    GROUP_CONCAT(t.name) as tags,
    COUNT(DISTINCT ks.kit_id) as kit_count
FROM samples s
JOIN users u ON s.user_id = u.id
LEFT JOIN vibe_analyses va ON s.id = va.sample_id
LEFT JOIN sample_tags st ON s.id = st.sample_id
LEFT JOIN tags t ON st.tag_id = t.id
LEFT JOIN kit_samples ks ON s.id = ks.sample_id
GROUP BY s.id;

-- User storage usage
CREATE VIEW user_storage AS
SELECT 
    u.id,
    u.username,
    u.storage_quota_mb,
    COALESCE(SUM(s.file_size_bytes) / 1048576.0, 0) as used_mb,
    u.storage_quota_mb - COALESCE(SUM(s.file_size_bytes) / 1048576.0, 0) as available_mb,
    COUNT(s.id) as sample_count
FROM users u
LEFT JOIN samples s ON u.id = s.user_id
GROUP BY u.id;
```

## Query Optimization

### Common Query Patterns
```sql
-- Get user's recent samples with vibe data
EXPLAIN QUERY PLAN
SELECT s.*, va.mood_primary, va.energy_level
FROM samples s
LEFT JOIN vibe_analyses va ON s.id = va.sample_id
WHERE s.user_id = ?
ORDER BY s.created_at DESC
LIMIT 20;
-- Uses: idx_samples_user_created

-- Find compatible samples by BPM range
EXPLAIN QUERY PLAN
SELECT * FROM samples
WHERE bpm BETWEEN ? AND ?
AND genre = ?
AND analyzed_at IS NOT NULL
ORDER BY bpm;
-- Uses: idx_samples_genre_bpm, idx_samples_analyzed

-- Full-text search on sample titles
CREATE VIRTUAL TABLE samples_fts USING fts5(
    title, 
    content=samples, 
    content_rowid=id
);

SELECT s.* FROM samples s
JOIN samples_fts ON s.id = samples_fts.rowid
WHERE samples_fts MATCH ?
ORDER BY rank;
```

### Performance Tuning
```sql
-- SQLite pragmas for performance
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000; -- 64MB
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 134217728; -- 128MB

-- Analyze statistics regularly
ANALYZE;

-- Vacuum periodically
VACUUM;
```

## Data Migration Strategy

### Migration Framework
```python
# migrations/001_initial_schema.py
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, nullable=False, unique=True),
        # ... more columns
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

### Safe Migration Practices
```python
# Zero-downtime migrations
class SafeMigration:
    """Patterns for safe production migrations."""
    
    async def add_column_with_default(self, table: str, column: str, default: Any):
        """Add column without locking table."""
        # 1. Add nullable column
        await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type}")
        
        # 2. Backfill in batches
        batch_size = 1000
        offset = 0
        while True:
            result = await db.execute(
                f"UPDATE {table} SET {column} = ? "
                f"WHERE {column} IS NULL LIMIT {batch_size}",
                [default]
            )
            if result.rowcount < batch_size:
                break
            offset += batch_size
            await asyncio.sleep(0.1)  # Prevent blocking
        
        # 3. Add NOT NULL constraint
        await db.execute(f"ALTER TABLE {table} ALTER COLUMN {column} SET NOT NULL")
```

## Backup & Recovery

### Automated Backup Strategy
```python
# backup_manager.py
class BackupManager:
    """Automated backup with retention policies."""
    
    async def create_backup(self):
        """Create timestamped backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backups/sp404_db_{timestamp}.db"
        
        # Use SQLite backup API
        async with aiosqlite.connect(self.db_path) as source:
            async with aiosqlite.connect(backup_file) as backup:
                await source.backup(backup)
        
        # Compress
        with gzip.open(f"{backup_file}.gz", 'wb') as f:
            with open(backup_file, 'rb') as src:
                f.write(src.read())
        
        # Upload to S3
        await self.upload_to_s3(f"{backup_file}.gz")
        
        # Clean up old backups
        await self.cleanup_old_backups()
    
    async def restore_from_backup(self, backup_date: str):
        """Restore database from specific backup."""
        # Download from S3
        backup_file = await self.download_from_s3(backup_date)
        
        # Decompress
        with gzip.open(backup_file, 'rb') as f:
            with open('restore.db', 'wb') as dst:
                dst.write(f.read())
        
        # Verify integrity
        async with aiosqlite.connect('restore.db') as db:
            integrity = await db.execute("PRAGMA integrity_check")
            if await integrity.fetchone() != ('ok',):
                raise ValueError("Backup integrity check failed")
        
        # Atomic swap
        os.rename(self.db_path, f"{self.db_path}.old")
        os.rename('restore.db', self.db_path)
```

## Monitoring & Maintenance

### Query Performance Monitoring
```python
# monitor.py
class DatabaseMonitor:
    """Track slow queries and performance metrics."""
    
    async def log_slow_queries(self):
        """Log queries taking > 100ms."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS slow_query_log (
                id INTEGER PRIMARY KEY,
                query TEXT,
                execution_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Monitor active queries
        while True:
            queries = await db.fetch_all("""
                SELECT sql, elapsed_ms 
                FROM pragma_query_log() 
                WHERE elapsed_ms > 100
            """)
            
            for query in queries:
                await self.analyze_slow_query(query)
            
            await asyncio.sleep(60)
```

### Data Integrity Checks
```sql
-- Regular integrity checks
PRAGMA integrity_check;
PRAGMA foreign_key_check;

-- Orphaned records check
SELECT s.* FROM samples s
LEFT JOIN users u ON s.user_id = u.id
WHERE u.id IS NULL;

-- Storage consistency
SELECT 
    u.username,
    u.storage_used_mb as reported,
    SUM(s.file_size_bytes) / 1048576.0 as actual,
    ABS(u.storage_used_mb - SUM(s.file_size_bytes) / 1048576.0) as diff
FROM users u
LEFT JOIN samples s ON u.id = s.user_id
GROUP BY u.id
HAVING diff > 0.1;
```

## Integration Points

### With Backend Developer
- Query builders
- Transaction patterns
- Connection pooling
- Migration scripts

### With DevOps Engineer
- Backup automation
- Monitoring setup
- Replication config
- Performance alerts

### With Full-Stack Developer
- API query optimization
- Caching strategies
- Data validation
- Schema updates

## Success Metrics

- Query response < 50ms (95th percentile)
- Zero data loss incidents
- 99.9% uptime
- Automated daily backups
- < 5% storage fragmentation
- Successful migration rollbacks