import streamlit as st
import sys

try:
    from main import convert_phrase, suggest, convert_token
except ImportError as e:
    st.error(f"Error importing main module: {e}")
    sys.exit(1)

st.set_page_config(
    page_title="Thai IME - Romanization Converter",
    page_icon="🇹🇭",
    layout="wide"
)

st.title("🇹🇭 Thai IME - Romanization to Thai Script")
st.markdown("Convert Roman/English phonetic spelling to Thai script")

# Sidebar for info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool converts English romanization to Thai script.
    
    **Examples:**
    - `aroi` → อร่อย (delicious)
    - `khon` → คน (person)
    - `baan` → บ้าน (house)
    - `khao` → เขา (he/she)
    - `phuean` → เพื่อน (friend)
    - `sawatdii` → สวัสดี (hello)
    """)

# Main conversion section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Romanized Input")
    roman_input = st.text_area(
        "Enter romanized Thai (e.g., 'aroi', 'khon', 'phuean')",
        height=150,
        label_visibility="collapsed",
        placeholder="Type romanized Thai here..."
    )

with col2:
    st.subheader("Thai Script Output")
    if roman_input:
        thai_output = convert_phrase(roman_input)
        st.text_area(
            "Converted Thai script",
            value=thai_output,
            height=150,
            disabled=True,
            label_visibility="collapsed"
        )
    else:
        st.text_area(
            "Converted Thai script",
            value="",
            height=150,
            disabled=True,
            label_visibility="collapsed"
        )

# Single word conversion with suggestions
st.markdown("---")
st.subheader("Word Converter with Suggestions")

col1, col2 = st.columns([1, 1])

with col1:
    word_input = st.text_input(
        "Enter a single word (with optional tone marker 1-5)",
        placeholder="e.g., aroi, khon3, baan"
    )

if word_input:
    with col2:
        converted = convert_token(word_input)
        st.metric("Converted to Thai", converted)
    
    # Show suggestions
    suggestions = suggest(word_input, max_suggestions=10)
    
    if suggestions:
        st.markdown("**Alternative spellings/pronunciations:**")
        cols = st.columns(2)
        for idx, entry in enumerate(suggestions):
            col = cols[idx % 2]
            with col:
                st.button(
                    f"{entry.roman} → {entry.thai}",
                    key=f"suggestion_{idx}",
                    use_container_width=True
                )
    else:
        st.info("No alternative spellings found")

# Examples section
st.markdown("---")
st.subheader("Common Words")

example_words = {
    "Hello": "sawatdii",
    "Thank you": "khrap",
    "Person": "khon",
    "House": "baan",
    "Friend": "phuean",
    "Delicious": "aroi",
    "Happy": "sabay",
    "Fun": "sanuk",
    "Water": "naam",
    "Rice": "khao",
}

cols = st.columns(5)
for idx, (english, roman) in enumerate(example_words.items()):
    col = cols[idx % 5]
    with col:
        thai = convert_token(roman)
        st.write(f"**{english}**")
        st.write(f"`{roman}`")
        st.write(f"**{thai}**")
        st.divider()

st.markdown("---")
st.caption("Thai IME Lab - Roman to Thai Script Converter")
