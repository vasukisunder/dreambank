-- Supabase Schema for DreamBank
-- This file contains the database schema for migrating from JSON to Supabase

-- Enable Row Level Security (RLS) for public read access
-- You can adjust these policies based on your needs

-- Table: dreams
-- Stores the core dream text and metadata
CREATE TABLE dreams (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_dreams_id ON dreams(id);

-- Table: patterns 
-- Stores all extracted linguistic patterns from dreams
-- Uses a single table with pattern_type to avoid joins
CREATE TABLE patterns (
    id BIGSERIAL PRIMARY KEY,
    dream_id INTEGER NOT NULL REFERENCES dreams(id) ON DELETE CASCADE,
    pattern_type TEXT NOT NULL, -- 'adj_noun', 'verb_noun', 'prep', 'adverb_verb', 'temporal', 'compound', 'emotional'
    text TEXT NOT NULL,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX idx_patterns_dream_id ON patterns(dream_id);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_text ON patterns(text);
CREATE INDEX idx_patterns_text_lower ON patterns(LOWER(text)); -- For case-insensitive search
CREATE INDEX idx_patterns_type_text ON patterns(pattern_type, LOWER(text)); -- Composite index for common query

-- Table: visible_ranges
-- Stores the visible text ranges for the blackout poetry view
CREATE TABLE visible_ranges (
    id BIGSERIAL PRIMARY KEY,
    dream_id INTEGER NOT NULL REFERENCES dreams(id) ON DELETE CASCADE,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_visible_ranges_dream_id ON visible_ranges(dream_id);

-- Enable Row Level Security
ALTER TABLE dreams ENABLE ROW LEVEL SECURITY;
ALTER TABLE patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE visible_ranges ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed)
CREATE POLICY "Public read access for dreams" ON dreams
    FOR SELECT USING (true);

CREATE POLICY "Public read access for patterns" ON patterns
    FOR SELECT USING (true);

CREATE POLICY "Public read access for visible_ranges" ON visible_ranges
    FOR SELECT USING (true);

-- Optional: Create a materialized view for pattern counts (for performance)
CREATE MATERIALIZED VIEW pattern_counts AS
SELECT 
    pattern_type,
    LOWER(text) as text_lower,
    text as display_text,
    COUNT(*) as count,
    COUNT(DISTINCT dream_id) as dream_count
FROM patterns
GROUP BY pattern_type, LOWER(text), text;

CREATE INDEX idx_pattern_counts_type ON pattern_counts(pattern_type);
CREATE INDEX idx_pattern_counts_text ON pattern_counts(text_lower);
CREATE INDEX idx_pattern_counts_count ON pattern_counts(count DESC);

-- Function to refresh the materialized view
-- Run this after bulk uploads: REFRESH MATERIALIZED VIEW CONCURRENTLY pattern_counts;

-- Optional: Create a function to get dreams by pattern
CREATE OR REPLACE FUNCTION get_dreams_by_pattern(
    p_pattern_type TEXT,
    p_text TEXT,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    dream_id INTEGER,
    dream_text TEXT,
    pattern_start INTEGER,
    pattern_end INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.text,
        p.start_pos,
        p.end_pos
    FROM dreams d
    INNER JOIN patterns p ON d.id = p.dream_id
    WHERE p.pattern_type = p_pattern_type
    AND LOWER(p.text) = LOWER(p_text)
    ORDER BY d.id
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Function to search patterns
CREATE OR REPLACE FUNCTION search_patterns(
    p_pattern_type TEXT,
    p_search_query TEXT,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    text TEXT,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.text,
        COUNT(DISTINCT p.dream_id) as count
    FROM patterns p
    WHERE p.pattern_type = p_pattern_type
    AND LOWER(p.text) LIKE LOWER('%' || p_search_query || '%')
    GROUP BY p.text
    ORDER BY count DESC, p.text
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get all unique patterns for a type
CREATE OR REPLACE FUNCTION get_patterns_by_type(
    p_pattern_type TEXT,
    p_sort_by TEXT DEFAULT 'alpha', -- 'alpha' or 'freq'
    p_limit INTEGER DEFAULT 1000,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    text TEXT,
    count BIGINT
) AS $$
BEGIN
    IF p_sort_by = 'freq' THEN
        RETURN QUERY
        SELECT 
            p.text,
            COUNT(DISTINCT p.dream_id) as count
        FROM patterns p
        WHERE p.pattern_type = p_pattern_type
        GROUP BY p.text
        ORDER BY count DESC, p.text
        LIMIT p_limit
        OFFSET p_offset;
    ELSE
        RETURN QUERY
        SELECT 
            p.text,
            COUNT(DISTINCT p.dream_id) as count
        FROM patterns p
        WHERE p.pattern_type = p_pattern_type
        GROUP BY p.text
        ORDER BY p.text
        LIMIT p_limit
        OFFSET p_offset;
    END IF;
END;
$$ LANGUAGE plpgsql;

