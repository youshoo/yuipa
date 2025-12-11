# yuipa

Thai Romanization to Thai Script Converter with Streamlit Web Demo

## Features

- Convert romanized Thai spelling to Thai script
- Smart dictionary-based and phonetic conversion
- Alternative spelling suggestions
- Web-based UI with Streamlit

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

### Phrase Conversion
Enter romanized Thai text (space-separated words) and get instant conversion:
- Input: `aroi khon baan`
- Output: `อร่อย คน บ้าน`

### Word Converter
Enter individual words (with optional tone markers 1-5):
- `aroi` → อร่อย
- `khon3` → คน
- `baan` → บ้าน

### Tone Markers
Append 1-5 to specify tone:
- `1` = level tone
- `2` = falling tone  
- `3` = high tone
- `4` = rising tone
- `5` = extra high tone

Example: `khao3` → เขา (high tone "he/she")

## Examples

- **aroi** - อร่อย (delicious)
- **khon** - คน (person)
- **baan** - บ้าน (house)
- **khao** - เขา (he/she)
- **phuean** - เพื่อน (friend)
- **sawatdii** - สวัสดี (hello)