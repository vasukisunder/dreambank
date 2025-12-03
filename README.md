# Dream Bank

Linguistic pattern extraction and visualization from dream texts.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

Process dreams:
```bash
python process_dreams.py
```

View results:
```bash
python -m http.server 8000
```

Navigate to `http://localhost:8000`

## Files

- `index.html` - blackout poetry view
- `pairs.html` - pattern browser
- `process_dreams.py` - text processing
- `blacklist.json` - filter incorrect patterns

