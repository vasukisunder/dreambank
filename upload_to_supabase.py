#!/usr/bin/env python3
"""
Upload dreams_processed.json to Supabase database
This script reads the large JSON file and uploads it in batches to avoid memory issues
"""

import json
import os
from supabase import create_client, Client
from typing import List, Dict
import sys
import time

# Configuration
BATCH_SIZE = 50  # Number of records to insert at once (reduced for stability)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("\nYou can get these from your Supabase project settings:")
        print("1. Go to https://app.supabase.com/")
        print("2. Select your project")
        print("3. Go to Settings > API")
        print("4. Copy the URL and anon/public key")
        print("\nThen run:")
        print("  export SUPABASE_URL='your-project-url'")
        print("  export SUPABASE_KEY='your-anon-key'")
        sys.exit(1)
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_dreams(supabase: Client, dreams: List[Dict], start_idx: int = 0, end_idx: int = None):
    """Upload dreams in batches"""
    if end_idx is None:
        end_idx = len(dreams)
    
    dreams_subset = dreams[start_idx:end_idx]
    total = len(dreams_subset)
    
    print(f"\n=== Uploading Dreams (records {start_idx} to {end_idx-1}) ===")
    
    for i in range(0, total, BATCH_SIZE):
        batch = dreams_subset[i:i+BATCH_SIZE]
        dream_records = []
        
        for dream in batch:
            dream_records.append({
                'id': dream['id'],
                'text': dream['text']
            })
        
        retries = 3
        for attempt in range(retries):
            try:
                supabase.table('dreams').insert(dream_records).execute()
                print(f"✓ Uploaded dreams {start_idx + i} to {start_idx + i + len(batch) - 1}")
                time.sleep(0.1)  # Small delay to avoid overwhelming the connection
                break
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠ Retry {attempt + 1}/{retries} for dreams batch {i}: {e}")
                    time.sleep(2)
                else:
                    print(f"✗ Error uploading dreams batch {i}: {e}")
                    return False
    
    return True

def upload_patterns(supabase: Client, dreams: List[Dict], start_idx: int = 0, end_idx: int = None):
    """Upload patterns in batches"""
    if end_idx is None:
        end_idx = len(dreams)
    
    dreams_subset = dreams[start_idx:end_idx]
    
    print(f"\n=== Uploading Patterns (for dreams {start_idx} to {end_idx-1}) ===")
    
    pattern_types = [
        ('adj_noun_pairs', 'adj_noun'),
        ('verb_noun_pairs', 'verb_noun'),
        ('prep_phrases', 'prep'),
        ('adverb_verb_pairs', 'adverb_verb'),
        ('temporal_phrases', 'temporal'),
        ('compound_nouns', 'compound'),
        ('emotional_verb_phrases', 'emotional')
    ]
    
    all_patterns = []
    
    for dream in dreams_subset:
        dream_id = dream['id']
        
        for json_key, pattern_type in pattern_types:
            patterns_list = dream.get(json_key, [])
            for pattern in patterns_list:
                all_patterns.append({
                    'dream_id': dream_id,
                    'pattern_type': pattern_type,
                    'text': pattern['text'],
                    'start_pos': pattern['start'],
                    'end_pos': pattern['end']
                })
    
    total_patterns = len(all_patterns)
    print(f"Total patterns to upload: {total_patterns}")
    
    for i in range(0, total_patterns, BATCH_SIZE):
        batch = all_patterns[i:i+BATCH_SIZE]
        
        retries = 3
        for attempt in range(retries):
            try:
                supabase.table('patterns').insert(batch).execute()
                print(f"✓ Uploaded patterns {i} to {i + len(batch) - 1} ({len(batch)} records)")
                time.sleep(0.1)  # Small delay to avoid overwhelming the connection
                break
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠ Retry {attempt + 1}/{retries} for patterns batch {i}: {e}")
                    time.sleep(2)
                else:
                    print(f"✗ Error uploading patterns batch {i}: {e}")
                    return False
    
    return True

def upload_visible_ranges(supabase: Client, dreams: List[Dict], start_idx: int = 0, end_idx: int = None):
    """Upload visible ranges for blackout poetry view"""
    if end_idx is None:
        end_idx = len(dreams)
    
    dreams_subset = dreams[start_idx:end_idx]
    
    print(f"\n=== Uploading Visible Ranges (for dreams {start_idx} to {end_idx-1}) ===")
    
    all_ranges = []
    
    for dream in dreams_subset:
        dream_id = dream['id']
        visible_ranges = dream.get('visible_ranges', [])
        
        for vr in visible_ranges:
            # visible_ranges in JSON are tuples [start, end]
            all_ranges.append({
                'dream_id': dream_id,
                'start_pos': vr[0],
                'end_pos': vr[1]
            })
    
    total_ranges = len(all_ranges)
    print(f"Total visible ranges to upload: {total_ranges}")
    
    for i in range(0, total_ranges, BATCH_SIZE):
        batch = all_ranges[i:i+BATCH_SIZE]
        
        try:
            supabase.table('visible_ranges').insert(batch).execute()
            print(f"✓ Uploaded ranges {i} to {i + len(batch) - 1} ({len(batch)} records)")
        except Exception as e:
            print(f"✗ Error uploading visible ranges batch {i}: {e}")
            return False
    
    return True

def load_json_incrementally(filepath: str, chunk_size: int = 1000):
    """
    Load large JSON file in chunks to avoid memory issues
    Returns a generator of dream chunks
    """
    print(f"Loading JSON file: {filepath}")
    print("Note: For very large files, this may take a while...")
    
    # For now, we'll load the entire file
    # If you run into memory issues, you can implement streaming JSON parsing
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} dreams from JSON")
    
    # Yield chunks
    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size], i, min(i+chunk_size, len(data))

def clear_tables(supabase: Client):
    """Clear all tables (useful for testing)"""
    response = input("⚠️  This will DELETE ALL DATA in the database. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return False
    
    print("\nClearing tables...")
    try:
        # Delete in reverse order due to foreign key constraints
        supabase.table('visible_ranges').delete().neq('id', 0).execute()
        supabase.table('patterns').delete().neq('id', 0).execute()
        supabase.table('dreams').delete().neq('id', 0).execute()
        print("✓ All tables cleared")
        return True
    except Exception as e:
        print(f"✗ Error clearing tables: {e}")
        return False

def main():
    print("=" * 60)
    print("DreamBank - Supabase Upload Tool")
    print("=" * 60)
    
    # Get Supabase client
    supabase = get_supabase_client()
    print("✓ Connected to Supabase")
    
    # Check if user wants to clear existing data
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        if not clear_tables(supabase):
            return
    
    # Load and upload data
    json_file = 'dreams_processed.json'
    
    if not os.path.exists(json_file):
        print(f"ERROR: {json_file} not found. Please run process_dreams.py first.")
        return
    
    # Process in chunks to avoid memory issues
    chunk_size = 1000  # Process 1000 dreams at a time
    
    for dreams_chunk, start_idx, end_idx in load_json_incrementally(json_file, chunk_size):
        print(f"\n{'='*60}")
        print(f"Processing dreams {start_idx} to {end_idx-1}")
        print(f"{'='*60}")
        
        # Upload dreams
        if not upload_dreams(supabase, dreams_chunk, 0, len(dreams_chunk)):
            print("Failed to upload dreams. Aborting.")
            return
        
        # Upload patterns
        if not upload_patterns(supabase, dreams_chunk, 0, len(dreams_chunk)):
            print("Failed to upload patterns. Aborting.")
            return
        
        # Upload visible ranges (SKIPPED - not needed)
        # if not upload_visible_ranges(supabase, dreams_chunk, 0, len(dreams_chunk)):
        #     print("Failed to upload visible ranges. Aborting.")
        #     return
        print("⊘ Skipping visible ranges (not needed for pairs view)")
        
        print(f"\n✓ Completed chunk {start_idx}-{end_idx-1}")
    
    print("\n" + "=" * 60)
    print("✓ Upload complete!")
    print("=" * 60)
    
    # Refresh materialized view
    print("\n⚠️  Don't forget to refresh the materialized view in Supabase:")
    print("Run this SQL in your Supabase SQL Editor:")
    print("  REFRESH MATERIALIZED VIEW CONCURRENTLY pattern_counts;")
    print("\nOr use the Supabase dashboard > SQL Editor")

if __name__ == '__main__':
    main()

