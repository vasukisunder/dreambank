#!/usr/bin/env python3

import csv
import json
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    exit(1)

EMOTIONAL_WORDS = {
    'afraid', 'angry', 'anxious', 'ashamed', 'bewildered', 'bitter', 'brave', 
    'calm', 'confused', 'content', 'depressed', 'desperate', 'disgusted', 
    'eager', 'embarrassed', 'excited', 'fearful', 'frightened', 'frustrated',
    'guilty', 'happy', 'helpless', 'hopeful', 'horrified', 'hurt', 'jealous',
    'lonely', 'loved', 'mad', 'nervous', 'overwhelmed', 'panicked', 'peaceful',
    'proud', 'sad', 'scared', 'shocked', 'sick', 'suspicious', 'sympathetic',
    'terrified', 'tired', 'uncomfortable', 'worried', 'angry', 'sad', 'happy',
    'fear', 'love', 'hate', 'joy', 'sorrow', 'pain', 'pleasure', 'anxiety',
    'dread', 'hope', 'despair', 'rage', 'calm', 'panic', 'peace', 'tension',
    'relief', 'comfort', 'discomfort', 'loneliness', 'belonging', 'isolation'
}

SENSORY_WORDS = {
    'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 
    'white', 'gray', 'grey', 'brown', 'gold', 'silver', 'crimson', 'azure',
    'emerald', 'amber', 'violet', 'scarlet', 'turquoise', 'ivory', 'ebony',
    'smooth', 'rough', 'soft', 'hard', 'slick', 'sticky', 'gritty', 'silky',
    'fuzzy', 'sharp', 'dull', 'glossy', 'matte', 'bumpy', 'velvety', 'coarse',
    'loud', 'quiet', 'silent', 'noisy', 'shrill', 'muffled', 'echoing',
    'ringing', 'buzzing', 'humming', 'whispering', 'shouting', 'screaming',
    'crashing', 'thumping', 'ticking', 'clicking', 'whooshing', 'rumbling'
}

PHYSICAL_STATE_WORDS = {
    'running', 'walking', 'falling', 'sitting', 'standing', 'lying', 'crouching',
    'jumping', 'climbing', 'crawling', 'dancing', 'swimming', 'flying', 'driving',
    'riding', 'moving', 'stopping', 'turning', 'pushing', 'pulling', 'grabbing',
    'holding', 'reaching', 'stretching', 'bending', 'twisting', 'leaning',
    'collapsing', 'rising', 'descending', 'ascending', 'floating', 'sinking'
}

NEGATIONS = {
    "not", "never", "no", "none", "nothing", "nobody", "nowhere",
    "neither", "nor", "cannot"
}

def extract_patterns(doc, dream_text):
    visible_ranges = []
    
    for token in doc:
        if token.pos_ == 'ADJ' and token.i + 1 < len(doc):
            next_token = doc[token.i + 1]
            if next_token.pos_ == 'NOUN':
                start = token.idx
                end = next_token.idx + len(next_token.text)
                visible_ranges.append((start, end, 'adj-noun'))
    
    for token in doc:
        if token.lemma_.lower() in EMOTIONAL_WORDS:
            start = token.idx
            end = token.idx + len(token.text)
            visible_ranges.append((start, end, 'emotional'))
    
    for token in doc:
        if token.lemma_.lower() in SENSORY_WORDS:
            start = token.idx
            end = token.idx + len(token.text)
            visible_ranges.append((start, end, 'sensory'))
    
    for ent in doc.ents:
        visible_ranges.append((ent.start_char, ent.end_char, 'entity'))
    
    for token in doc:
        if token.pos_ == 'PROPN':
            start = token.idx
            end = token.idx + len(token.text)
            visible_ranges.append((start, end, 'proper'))
    
    sentences = list(doc.sents)
    for sent in sentences:
        if sent.text.strip().endswith('.'):
            words = [t for t in sent if not t.is_punct and not t.is_space]
            if 3 <= len(words) <= 5:
                visible_ranges.append((sent.start_char, sent.end_char, 'phrase'))
    
    for token in doc:
        if token.text.lower() in NEGATIONS or token.lemma_.lower() in NEGATIONS:
            start = token.idx
            end = token.idx + len(token.text)
            visible_ranges.append((start, end, 'negation'))
    
    for token in doc:
        if token.lemma_.lower() in PHYSICAL_STATE_WORDS and token.pos_ in ['VERB', 'ADJ']:
            start = token.idx
            end = token.idx + len(token.text)
            visible_ranges.append((start, end, 'physical'))
    
    visible_ranges = merge_ranges(visible_ranges)
    
    return visible_ranges

def extract_additional_patterns(doc, dream_text):
    patterns = {
        'verb_noun': [],
        'prep_phrases': [],
        'adverb_verb': [],
        'temporal': [],
        'compound_nouns': [],
        'emotional_verb': []
    }
    
    for token in doc:
        if token.pos_ == 'VERB':
            for child in token.children:
                if child.dep_ in ['dobj', 'pobj'] and child.pos_ == 'NOUN':
                    start = min(token.idx, child.idx)
                    end = max(token.idx + len(token.text), child.idx + len(child.text))
                    phrase = dream_text[start:end].strip()
                    if phrase:
                        patterns['verb_noun'].append({
                            'text': phrase,
                            'start': start,
                            'end': end
                        })
    
    for token in doc:
        if token.pos_ == 'ADP':
            phrase_tokens = [token]
            for child in token.children:
                if child.dep_ == 'pobj':
                    phrase_tokens.append(child)
                    for grandchild in child.children:
                        if grandchild.dep_ in ['det', 'amod', 'compound']:
                            phrase_tokens.append(grandchild)
            
            if len(phrase_tokens) > 1:
                phrase_tokens.sort(key=lambda t: t.i)
                start = phrase_tokens[0].idx
                end = phrase_tokens[-1].idx + len(phrase_tokens[-1].text)
                phrase = dream_text[start:end].strip()
                if phrase and len(phrase.split()) <= 5:
                    patterns['prep_phrases'].append({
                        'text': phrase,
                        'start': start,
                        'end': end
                    })
    
    for token in doc:
        if token.pos_ == 'ADV':
            if token.head.pos_ == 'VERB':
                start = min(token.idx, token.head.idx)
                end = max(token.idx + len(token.text), token.head.idx + len(token.head.text))
                phrase = dream_text[start:end].strip()
                if phrase and len(phrase.split()) <= 3:
                    patterns['adverb_verb'].append({
                        'text': phrase,
                        'start': start,
                        'end': end
                    })
    
    temporal_markers = {'when', 'while', 'before', 'after', 'during', 'until', 'since', 
                       'now', 'then', 'suddenly', 'always', 'never', 'sometimes',
                       'today', 'yesterday', 'tonight', 'morning', 'night', 'evening',
                       'ago', 'later', 'earlier', 'soon', 'recently', 'finally'}
    
    for token in doc:
        if token.lemma_.lower() in temporal_markers or token.ent_type_ in ['TIME', 'DATE']:
            phrase_tokens = [token]
            for child in token.children:
                if child.dep_ in ['prep', 'det', 'amod', 'nummod']:
                    phrase_tokens.append(child)
            
            phrase_tokens.sort(key=lambda t: t.i)
            start = phrase_tokens[0].idx
            end = phrase_tokens[-1].idx + len(phrase_tokens[-1].text)
            phrase = dream_text[start:end].strip()
            if phrase and len(phrase.split()) <= 4:
                patterns['temporal'].append({
                    'text': phrase,
                    'start': start,
                    'end': end
                })
    
    for token in doc:
        if token.pos_ == 'NOUN' and token.i + 1 < len(doc):
            next_token = doc[token.i + 1]
            if next_token.pos_ == 'NOUN':
                start = token.idx
                end = next_token.idx + len(next_token.text)
                phrase = dream_text[start:end].strip()
                if phrase:
                    patterns['compound_nouns'].append({
                        'text': phrase,
                        'start': start,
                        'end': end
                    })
    
    emotional_verbs = {'feel', 'felt', 'seem', 'seemed', 'become', 'became', 'look', 'looked',
                      'appear', 'appeared', 'sense', 'sensed', 'realize', 'realized'}
    
    for token in doc:
        if token.lemma_.lower() in emotional_verbs:
            phrase_tokens = [token]
            for child in token.children:
                if child.dep_ in ['acomp', 'attr', 'oprd'] or (child.dep_ == 'xcomp' and child.pos_ == 'ADJ'):
                    phrase_tokens.append(child)
                    for grandchild in child.children:
                        if grandchild.dep_ in ['advmod', 'neg']:
                            phrase_tokens.append(grandchild)
            
            if len(phrase_tokens) > 1:
                phrase_tokens.sort(key=lambda t: t.i)
                start = phrase_tokens[0].idx
                end = phrase_tokens[-1].idx + len(phrase_tokens[-1].text)
                phrase = dream_text[start:end].strip()
                if phrase and len(phrase.split()) <= 4:
                    patterns['emotional_verb'].append({
                        'text': phrase,
                        'start': start,
                        'end': end
                    })
    
    return patterns

def merge_ranges(ranges):
    if not ranges:
        return []
    
    range_tuples = [(r[0], r[1]) for r in ranges]
    sorted_ranges = sorted(range_tuples, key=lambda x: x[0])
    merged = [sorted_ranges[0]]
    
    for current in sorted_ranges[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged

def process_dreams(input_csv, output_json):
    dreams = []
    
    print("Loading dreams from CSV...")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dream_text = row['dream'].strip()
            if dream_text:
                dreams.append(dream_text)
    
    print(f"Processing {len(dreams)} dreams with spaCy...")
    processed_dreams = []
    
    for i, dream_text in enumerate(dreams):
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(dreams)} dreams...")
        
        doc = nlp(dream_text)
        visible_ranges = extract_patterns(doc, dream_text)
        
        adj_noun_pairs = []
        for token in doc:
            if token.pos_ == 'ADJ' and token.i + 1 < len(doc):
                next_token = doc[token.i + 1]
                if next_token.pos_ == 'NOUN':
                    start = token.idx
                    end = next_token.idx + len(next_token.text)
                    pair_text = dream_text[start:end].strip()
                    adj_noun_pairs.append({
                        'text': pair_text,
                        'start': start,
                        'end': end
                    })
        
        additional_patterns = extract_additional_patterns(doc, dream_text)
        
        processed_dreams.append({
            'id': i,
            'text': dream_text,
            'visible_ranges': visible_ranges,
            'adj_noun_pairs': adj_noun_pairs,
            'verb_noun_pairs': additional_patterns['verb_noun'],
            'prep_phrases': additional_patterns['prep_phrases'],
            'adverb_verb_pairs': additional_patterns['adverb_verb'],
            'temporal_phrases': additional_patterns['temporal'],
            'compound_nouns': additional_patterns['compound_nouns'],
            'emotional_verb_phrases': additional_patterns['emotional_verb']
        })
    
    print(f"Saving results to {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(processed_dreams, f, indent=2, ensure_ascii=False)
    
    print("Done!")
    return processed_dreams

if __name__ == '__main__':
    import sys
    
    input_csv = 'all_dreams_combined.csv'
    output_json = 'dreams_processed.json'
    
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    if len(sys.argv) > 2:
        output_json = sys.argv[2]
    
    process_dreams(input_csv, output_json)
