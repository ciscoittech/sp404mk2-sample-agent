-- SP-404MK2 Sample Reorganization Database Schema
-- This schema tracks the reorganization of samples from cryptic folder names
-- to human-readable structures while maintaining SP-404MK2 compatibility

-- Main table for tracking sample reorganization
CREATE TABLE IF NOT EXISTS sample_reorganization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Original file information
    original_path TEXT NOT NULL,
    original_bank TEXT NOT NULL,
    original_pad INTEGER NOT NULL,
    source_description TEXT,  -- From LOOPS_INFO.txt
    
    -- New organization paths
    sp404_path TEXT,
    human_path TEXT,
    
    -- Musical metadata
    instrument TEXT,
    instrument_subcategory TEXT,  -- e.g., 'kick', 'snare' for drums
    bpm INTEGER,
    musical_key TEXT,
    genre TEXT,
    
    -- File metadata
    filename_original TEXT NOT NULL,
    filename_human TEXT,
    file_size_bytes INTEGER,
    duration_seconds REAL,
    sample_rate INTEGER,
    bit_depth INTEGER,
    
    -- Processing metadata
    detection_method TEXT CHECK(detection_method IN ('filename_parse', 'ai_analysis', 'manual', 'flagged')),
    ai_confidence REAL,  -- 0.0 to 1.0 for AI detection confidence
    flagged_for_review BOOLEAN DEFAULT 0,
    flag_reason TEXT,
    
    -- Organization metadata
    new_bank_assignment TEXT,
    new_pad_position INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_instrument ON sample_reorganization(instrument);
CREATE INDEX IF NOT EXISTS idx_bpm ON sample_reorganization(bpm);
CREATE INDEX IF NOT EXISTS idx_flagged ON sample_reorganization(flagged_for_review);
CREATE INDEX IF NOT EXISTS idx_original_bank_pad ON sample_reorganization(original_bank, original_pad);

-- Table for tracking instrument detection rules
CREATE TABLE IF NOT EXISTS instrument_detection_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,  -- Regex pattern to match
    instrument TEXT NOT NULL,
    subcategory TEXT,
    priority INTEGER DEFAULT 10,  -- Lower number = higher priority
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default detection rules
INSERT OR IGNORE INTO instrument_detection_rules (pattern, instrument, subcategory, priority) VALUES
    ('(kick|bd|bassdrum)', 'drums', 'kick', 1),
    ('(snare|sd|snr)', 'drums', 'snare', 1),
    ('(hat|hh|hihat)', 'drums', 'hat', 1),
    ('(crash|cym|cymbal)', 'drums', 'cymbal', 1),
    ('(ride)', 'drums', 'ride', 1),
    ('(perc|percussion|conga|bongo|tamb)', 'drums', 'percussion', 2),
    ('(drum|break)', 'drums', 'full_loop', 3),
    
    ('(bass|bs)', 'bass', NULL, 1),
    ('(sub)', 'bass', 'sub', 2),
    
    ('(piano|pno)', 'keys', 'piano', 1),
    ('(rhodes|rhds)', 'keys', 'rhodes', 1),
    ('(organ|org)', 'keys', 'organ', 1),
    ('(wurli|wurlitzer)', 'keys', 'wurlitzer', 1),
    ('(synth|keys)', 'keys', 'synth', 2),
    
    ('(vocal|vox|voice)', 'vocals', NULL, 1),
    ('(choir)', 'vocals', 'choir', 2),
    
    ('(sax|saxophone)', 'brass', 'saxophone', 1),
    ('(trumpet|trp)', 'brass', 'trumpet', 1),
    ('(trombone|trb)', 'brass', 'trombone', 1),
    
    ('(guitar|gtr)', 'strings', 'guitar', 1),
    ('(violin|vln)', 'strings', 'violin', 1),
    ('(cello)', 'strings', 'cello', 1),
    
    ('(atmosphere|atmos|ambient)', 'atmosphere', NULL, 1),
    ('(pad)', 'atmosphere', 'pad', 2);

-- Table for tracking reorganization sessions
CREATE TABLE IF NOT EXISTS reorganization_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    source_directory TEXT NOT NULL,
    sp404_output_directory TEXT,
    human_output_directory TEXT,
    
    total_samples INTEGER DEFAULT 0,
    processed_samples INTEGER DEFAULT 0,
    flagged_samples INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'cancelled')),
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    configuration_json TEXT  -- Store session config as JSON
);

-- Table for error logging
CREATE TABLE IF NOT EXISTS reorganization_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    sample_id INTEGER,
    error_type TEXT,
    error_message TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES reorganization_sessions(session_id),
    FOREIGN KEY (sample_id) REFERENCES sample_reorganization(id)
);

-- View for easy querying of samples by instrument
CREATE VIEW IF NOT EXISTS samples_by_instrument AS
SELECT 
    instrument,
    instrument_subcategory,
    COUNT(*) as sample_count,
    AVG(bpm) as avg_bpm,
    MIN(bpm) as min_bpm,
    MAX(bpm) as max_bpm,
    SUM(CASE WHEN flagged_for_review = 1 THEN 1 ELSE 0 END) as flagged_count
FROM sample_reorganization
WHERE processed_at IS NOT NULL
GROUP BY instrument, instrument_subcategory
ORDER BY instrument, instrument_subcategory;

-- View for reorganization progress
CREATE VIEW IF NOT EXISTS reorganization_progress AS
SELECT 
    s.session_id,
    s.source_directory,
    s.total_samples,
    s.processed_samples,
    s.flagged_samples,
    s.error_count,
    s.status,
    s.started_at,
    ROUND(CAST(s.processed_samples AS REAL) / s.total_samples * 100, 2) as progress_percent,
    COUNT(DISTINCT r.instrument) as unique_instruments,
    COUNT(DISTINCT r.new_bank_assignment) as banks_used
FROM reorganization_sessions s
LEFT JOIN sample_reorganization r ON s.started_at = r.created_at
GROUP BY s.id;