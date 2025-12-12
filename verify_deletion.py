#!/usr/bin/env python3
"""
Script to verify that blacklisted patterns have been deleted from the database.
"""

import os
import sys
from supabase import create_client, Client

# Blacklist data
EMBEDDED_BLACKLIST = {
    "adj_noun": ["2nd bag", "2nd choice", "2nd elevator", "2nd row", "3rd person", "8th floor", "_ dollars", "_ tank", "--then baby", "-action", "-circle", "-country", "-de", "-disc", "-dressing", "-five men", "-golf", "-haul", "-like look", "-office", "-school", "-smoking", "-state", "-truck", "-year", "! tat", "'social modeling", "*calypso", "° movement", "+ feeling", "~2 inch", "100th floor", "100th percentile", "10th century", "10th day", "10th floor", "10th grade", "10th tickets", "11th floor", "11th grade", "11th level", "11th story", "11th street", "12th grade", "12th level", "12th man", "12th night", "12th year", "13th floor", "14th floor", "14th level", "14th street", "15th birthday", "15th century", "15th floor", "16th century", "16th floor", "16th note", "16th notes", "16th room", "17th birthday", "17th century", "18th birthday", "18th century", "190ng bamboo", "19th birthday", "19th century", "1st base", "1st class", "1st dream", "1st floor", "1st grade", "1st level", "1st man", "1st nurse", "1st one", "1st parking", "1st part", "1st person", "1st question", "1st race", "1st room", "1st slip", "1st story", "1st strip", "1st violin", "1st wife", "1st year", "20th century", "20th floor", "21st story", "25th anniversary", "25th floor", "25th wedding", "27th century", "2nd baby", "2nd balcony", "2nd class", "2nd dream", "2nd flight", "2nd floor", "2nd gear", "2nd girl", "2nd glass", "2nd grade", "2nd healing", "2nd horse", "2nd house", "2nd kind", "2nd lady", "2nd man", "2nd meeting", "2nd part", "2nd quarter", "2nd race", "2nd room", "2nd shift", "2nd story", "2nd street", "2nd thing", "2nd time", "2nd trimester", "2nd wife", "2nd woman", "2nd year", "30ish woman", "32nd floor", "38th street", "39th street", "3d bar", "3d effects", "a+ +"],
    "verb_noun": ["---a large platter", "--see a black cat", "--to my horror", "= a good friend", "= an acquaintence", "= an aquaintance", "= an older cousin", "= good friend", "= my best friend", "= my hometown", "­ the same one"],
    "prep": ["---for shore", "'cause the", "'s she's learned from", "@ $5", "@ $5.98", "@ 90 m.p.h", "@ a scene", "++ feeling", "= throne", "a guy i am with", "about _"],
    "adverb_verb": ["'s also", "'s dirt here", "'s maybe", "'s rather", "a********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************ht add", "--also see", "--can't recall", "--literally manicuring", "'d better", "'d rather", "'quite", "'s actually", "'s already", "'s always", "'s another, though", "'s apparently", "'s barely", "'s hardly", "'s just", "'s light now", "'s literally", "'s mainly", "'s mostly", "'s nobody around", "'s nobody here", "'s normally", "'s not actually", "'s not even", "'s not really", "'s not still", "'s now", "'s nowhere", "'s nowhere here", "'s others here", "'s out", "'s so", "'s still", "'s stuff everywhere", "'s tv around", "++ feeling", "aand lovingly", "about based", "about finished", "about got", "about made", "about see", "about as harried", "abandon her too", "abandoning them there", "abducted too", "aboard, someone tells", "above-mentioned", "above, there were"],
    "temporal": ["-", "'", "05", "09", "10", "11", "12", "17", "18", "20", "24", "27", "3", "2nd", "30", "4", "5", "8", "a", "a 7-11", "80 in", "_", "-8:00", "-full of", ",", ".", "...", "'s", "'s in", "\"", "(", ")", "/", "&", "#", "+", "+ 28", "0", "003", "004", "01", "01-01", "01-02", "01-03", "01-04", "01-05", "01-06", "01-07", "01-08", "01-09", "01-10", "01-11", "01-12", "01-13", "01-14", "01-15", "01-16", "01-17", "01-18", "01-19", "01-20", "01-21", "01-22", "01-23", "01-24", "01-25", "01-26", "01-27", "01-28", "01-29", "01-30", "01-31", "01/06/48", "01/13/48", "01/15/48", "01/20/2004", "01/20/97", "01/26/48", "010", "014", "015", "018", "02", "02 (12", "02-01", "02-02", "02-03", "02-04", "02-05", "02-06", "02-07", "02-08", "02-09", "02-10", "02-11", "02-12", "02-13", "02-14", "02-15", "02-16", "02-17", "02-18", "02-19", "02-20", "02-21", "02-22", "02-23", "02-24", "02-25", "02-26", "02-27", "02-28", "02-29", "02/01/48", "02/10/47", "02/10/48", "02/14/48", "02/17/47", "02/18/48", "02/19/47", "02/21/48", "02/22/47", "02/28/48", "020", "03", "03-01", "03-02", "03-03", "03-04", "03-05", "03-06", "03-07", "03-08", "03-09", "03-10", "03-11", "03-12", "03-13", "03-14", "03-15", "03-16", "03-17", "03-18", "03-19", "03-20", "03-21", "03-22", "03-23", "03-24", "03-25", "03-26", "a '", "age", "age 10", "age 11", "age 12", "age 13", "age 14", "age 15", "age 16", "age 17", "age 18", "age 19", "age 19, 04/??/48", "age 19, 06/??/47", "age 2", "age 20", "age 20, 01/??/48", "age 20, 04/??/47", "age 20, 10/??/46", "age 20, 10/??/47", "age 20, 12/??/47", "age 20, 12/29/47", "age 21", "age 21, 01/??/47", "age 21, 01/??/48", "age 21, 03/06/4", "age 21, 03/08/4", "age 21, 03/26/4", "age 21, 06/??/46", "age 21, 06/26/4", "age 21, 10/??/47", "age 21, 10/??/49", "age 21, 11/??/47", "age 21, 12/??/47", "age 21, 12/29/47", "age 22", "age 22, 05/14/4", "age 22, 05/22/4", "age 22, 05/24/4", "age 22, 07/06/4", "age 23", "age 24", "age 24, 10/??/47", "age 24, 11/??/47", "age 25", "age 26", "age 30", "age 32", "age 39 from", "age 4", "age 40", "age 44", "age 45", "age 47", "age 5", "age 50", "age 55", "age 6", "age 69", "age 7", "age 80", "age 9", "age thirty", "ages", "ages 11", "ages 12", "ages 16", "ages 19", "ages 45", "a 1 year old", "a 1 yr old", "a 1:00 am lab", "a 1/2 hour", "a 10-year-old", "a 12 year old", "a 12 years", "a 12-year-old", "a 13 year old", "a 14 year old", "a 14-year-old", "a 15 hour day", "a 15 year old", "a 16-year-old", "a 1930", "a 1950", "a 1950s", "a 1975", "a 2 year", "a 2-year", "a 20 year", "a 2nd quarter", "a 3 day weekend", "a 3 year", "a 3-year old", "a 30-30", "a 4-year old", "a 4-year-old", "a 5-year-old", "a 54", "a 7", "a 7 year old", "a 8-5", "a 9-year old girl", "a b'day", "inch", "ish", "jack", "jan", "jan.", "jan. 18", "jan. 23", "jan. 31", "january", "january 1", "january 1, 1966", "january 11", "january 15, 1998", "in their late 20's", "january 28, 1998", "january 27", "january 25 1979", "january 25", "january 21, 1998", "january 21, 1982", "january 2, 1979", "january 19, 1982", "january 8", "january 5, 1998", "her", "high", "high school", "his", "holiday", "holidays", "horrible", "i", "illuminated", "im", "important", "in", "jizz", "judgement", "judgement day", "july", "july 10, 2000", "july 12, 1977", "july 15", "july 15, 1941", "july 17, 1981", "july 17, 1982", "july 19, 1981", "july 2", "july 20", "july 2003", "july 23, 1980", "july 27, 1981", "july 28, 1981", "july 3, 1977", "july 3, 1981", "july 31, 1998", "july 4, 1981", "june 3, 1999", "june 27, 1971", "june 24, 1981", "june 21", "june 16, 1970", "june 15, 1981", "june 1", "june", "july of", "july 8", "july 5"],
    "compound": ["-clockwise", "-height", "-lovers", "-muck", "-streets", "-thing", "-turn", "-type", "-workers", "1st row", "_ building", "_ car", "_ gift", "_ parking", "_ pill", "_ schedule", "_ thing", "_ years", ": style", "?buggies", ". fence", ". height", ". man", ". night", ". table", ". woman", "..brother", ".the girls", "'50s", "'60s", "'80s", "'ants", "'omg", "* body", "*love", "*shrug", "*size", "/desk", "# a", "# cross", "% auto", "% commission", "% discount", "% human", "% interest", "% match", "% nonfat", "% pc", "% princess", "% tip", "° angle", "°c", "+ r", "++", "= acquaintence", "= ex", "= f", "= friend", "= friends", "= guy", "= sister", "=_", "a batteries", "a-- building", "a. building", "a. feeling", "a. m.", "a dream", "a team", "a. man", "a. sleeps", "a.m. class", "a.m. weather", "ab roller"],
    "emotional": []
}

def main():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        sys.exit(1)
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("Checking for remaining blacklisted patterns...")
    print("=" * 60)
    
    total_found = 0
    
    for pattern_type, phrases in EMBEDDED_BLACKLIST.items():
        if not phrases:
            continue
        
        print(f"\nChecking {pattern_type}...")
        found_count = 0
        
        # Check first 10 phrases as a sample
        sample_phrases = phrases[:10]
        for phrase in sample_phrases:
            try:
                # Check in patterns table
                result = supabase.table('patterns').select('id, text').eq('pattern_type', pattern_type).limit(1000).execute()
                if result.data:
                    matching = [r for r in result.data if r['text'].lower() == phrase.lower()]
                    if matching:
                        found_count += len(matching)
                        print(f"  ❌ Found {len(matching)} instances of: {phrase[:50]}")
                
                # Also check in pattern_counts view
                result2 = supabase.table('pattern_counts').select('text_lower, display_text, count').eq('pattern_type', pattern_type).ilike('text_lower', phrase.lower()).execute()
                if result2.data:
                    exact_matches = [r for r in result2.data if r['text_lower'] == phrase.lower()]
                    if exact_matches:
                        print(f"  ❌ Found in view: {phrase[:50]} (count: {exact_matches[0]['count']})")
            except Exception as e:
                print(f"  Error checking '{phrase}': {e}")
        
        if found_count == 0:
            print(f"  ✓ No matches found in sample (good!)")
        total_found += found_count
    
    print("\n" + "=" * 60)
    if total_found > 0:
        print(f"⚠️  Found {total_found} blacklisted patterns still in database!")
        print("The deletion may not have worked correctly.")
    else:
        print("✓ No blacklisted patterns found in sample check.")
        print("If you still see them on the website, try:")
        print("  1. Hard refresh the browser (Cmd+Shift+R or Ctrl+Shift+R)")
        print("  2. Clear browser cache")
        print("  3. Check if the materialized view was refreshed")

if __name__ == '__main__':
    main()

