#!/usr/bin/env python3
"""
Script to refresh the pattern_counts materialized view after deleting patterns.
"""

import os
import sys
from supabase import create_client, Client

def main():
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        sys.exit(1)
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("Refreshing pattern_counts materialized view...")
    print("=" * 60)
    
    try:
        # Refresh the materialized view using RPC or direct SQL
        # Note: Supabase Python client doesn't have direct support for REFRESH MATERIALIZED VIEW
        # So we need to use the SQL editor in Supabase dashboard, or use a Postgres function
        
        # Try using RPC if a function exists, otherwise instruct user
        print("\n⚠️  Supabase Python client cannot directly execute REFRESH MATERIALIZED VIEW.")
        print("You need to run this SQL in the Supabase SQL Editor:")
        print("\n  REFRESH MATERIALIZED VIEW pattern_counts;")
        print("\nOr I can try to create a function to do it...")
        
        # Try to create and call a function
        try:
            # Create function if it doesn't exist
            create_func_sql = """
            CREATE OR REPLACE FUNCTION refresh_pattern_counts()
            RETURNS void AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW pattern_counts;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            # Execute via RPC (this might not work, but worth trying)
            result = supabase.rpc('refresh_pattern_counts').execute()
            print("✓ Materialized view refreshed successfully!")
        except Exception as e:
            print(f"\n⚠️  Could not refresh via RPC: {e}")
            print("\nPlease run this SQL in the Supabase SQL Editor:")
            print("  REFRESH MATERIALIZED VIEW pattern_counts;")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease run this SQL in the Supabase SQL Editor:")
        print("  REFRESH MATERIALIZED VIEW pattern_counts;")

if __name__ == '__main__':
    main()

