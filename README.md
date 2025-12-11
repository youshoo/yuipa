# yuipa

Thai Romanization to Thai Script Converter with Streamlit Web Demo

## 🚀 Quick Start

### Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Try Online
Visit the [live demo](https://yuipa-demo.streamlit.app) hosted on Streamlit Cloud

## Features

- Convert romanized Thai spelling to Thai script
- Smart dictionary-based and phonetic conversion
- Alternative spelling suggestions
- Web-based UI with Streamlit

## Usage

### Phrase Conversion
Enter romanized Thai text (space-separated words):
- Input: `aroi khon baan`
- Output: `อร่อย คน บ้าน`

### Word Converter
Enter individual words with optional tone markers (1-5):
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

## Examples

- **aroi** - อร่อย (delicious)
- **khon** - คน (person)
- **baan** - บ้าน (house)
- **khao** - เขา (he/she)
- **phuean** - เพื่อน (friend)
- **sawatdii** - สวัสดี (hello)