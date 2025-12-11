import streamlit as st
from dataclasses import dataclass
from typing import List, Optional

# ===============================
# 1. MAPPINGS
# ===============================

CONSONANT_ONSET = {
    # single consonants
    "kh": "ข", "k":  "ก", "ph": "ผ", "p":  "ป",
    "th": "ถ", "t":  "ต", "ch": "ช", "c":  "จ",
    "j":  "จ", "b":  "บ", "d":  "ด", "f":  "ฟ",
    "s":  "ส", "h":  "ห", "m":  "ม", "n":  "น",
    "ng": "ง", "r":  "ร", "l":  "ล", "w":  "ว",
    "y":  "ย", "?":  "อ",
    # clusters
    "pr": "ปร", "phr":"พร", "kr": "กร", "khr":"คร", "tr": "ตร",
    "pl": "ปล", "phl":"พล", "kl": "กล", "khl":"คล", "kw": "กว", "khw":"ขว",
    # h-leading
    "hng":"หง", "hn": "หน", "hm": "หม", "hy": "หย", "hr": "หร", "hl": "หล", "hw": "หว",
}
ONSET_KEYS = sorted(CONSONANT_ONSET.keys(), key=len, reverse=True)

ALT_ONSET_FORMS = {
    "th": ["ถ", "ท", "ธ", "ฒ", "ฐ"],
    "ph": ["ผ", "พ", "ภ"],
    "ch": ["ช", "ฉ", "ฌ"],
    "s":  ["ส", "ซ", "ศ", "ษ"],
    "h":  ["ห", "ฮ"],
    "y":  ["ย", "ญ"],
    "f":  ["ฟ", "ฝ"],
    "k":  ["ก", "ไก"], 
    "kh": ["ข", "ค", "ฆ"],
    "d":  ["ด", "ฎ"],
    "t":  ["ต", "ฏ"],
    "n":  ["น", "ณ"],
    "l":  ["ล", "ฬ"],
}

ALT_CODA_FORMS = {
    "n":  ["น", "ร", "ล", "ญ", "ณ", "ฬ", "รย์"], 
    "t":  ["ด", "ต", "ท", "ธ", "ศ", "ษ", "ส", "จ", "ช", "ซ", "ฎ", "ฏ", "ฐ", "ฑ", "ฒ", "ติ", "ตุ", "ตว์"],
    "p":  ["บ", "ป", "พ", "ฟ", "ภ", "พธ์"],
    "k":  ["ก", "ข", "ค", "ฆ", "คร์"],
}

VOWEL_MAP = {
    "a":  ("",  "",   "ะ"), "aa": ("",  "",   "า"),
    "i":  ("",  "ิ",  ""),  "ii": ("",  "ี",  ""),
    "u":  ("",  "ุ",  ""),  "uu": ("",  "ู",  ""),
    "e":  ("เ", "็",  ""),  "ee": ("เ", "",   ""), 
    "o":  ("โ", "",   "ะ"), "oo": ("โ", "",   ""), 
    "ae": ("แ", "",   "ะ"), "aee":("แ", "",   ""),
    "ea": ("แ", "",   "ะ"), "eaa":("แ", "",   ""),
    "oe": ("เ", "",   "อะ"),"oee":("เ", "",   "อ"),
    "err":("เ", "",   "อะ"),"er": ("เ", "",   "อ"),
    "or": ("เ", "",   "าะ"),"orr":("",  "",   "อ"),
    "ia": ("เ", "ี",  "ย"), "ua": ("", "ั",  "ว"),
    "ai": ("ไ", "",   ""),  "ay": ("ไ", "",   ""), 
    "aw": ("เ", "",   "า"), "uea":("เ", "ื", "อ"),
    "am": ("", "",   "ำ"),    
}
VOWEL_KEYS = sorted(VOWEL_MAP.keys(), key=len, reverse=True)

TONE_MAP = {"1": "", "2": "่", "3": "้", "4": "๊", "5": "๋"}
CODA_MAP = {"ng": "ง", "k": "ก", "t": "ด", "p": "บ", "m": "ม", "n": "น", "w": "ว", "y": "ย"}
CODA_KEYS = sorted(CODA_MAP.keys(), key=len, reverse=True)

# ===============================
# 2. CORE CONVERSION
# ===============================

def split_tone(s: str):
    if s and s[-1] in TONE_MAP: return s[:-1], TONE_MAP[s[-1]]
    return s, ""

def match_prefix(keys, s):
    for k in keys:
        if s.startswith(k): return k, s[len(k):]
    return "", s

def match_vowel(s):
    for v in VOWEL_KEYS:
        idx = s.find(v)
        if idx != -1: return v, s[:idx], s[idx+len(v):]
    return "", s, ""

def match_coda(s):
    for k in CODA_KEYS:
        if s.endswith(k): return k, s[:-len(k)]
    return "", s

def assemble(onset_thai: str, vowel_key: str, tone: str) -> str:
    onset_thai = onset_thai or "ก"
    pre, main, post = VOWEL_MAP[vowel_key]
    if len(onset_thai) > 1:
        return pre + onset_thai[0] + onset_thai[1] + main + tone + post
    return pre + onset_thai + main + tone + post

def convert_syllable(roman: str) -> Optional[str]:
    roman = roman.lower()
    if not roman: return ""

    core, tone = split_tone(roman)
    vowel_key, before, after = match_vowel(core)
    
    if not vowel_key:
        onset_key, remainder = match_prefix(ONSET_KEYS, core)
        if remainder: return None
        onset_thai = CONSONANT_ONSET.get(onset_key, "")
        if len(onset_thai) > 1: return onset_thai[0] + onset_thai[1] + tone
        return onset_thai + tone

    onset_key, _ = match_prefix(ONSET_KEYS, before)
    onset_thai = CONSONANT_ONSET.get(onset_key, "")
    coda_key, _ = match_coda(after)
    coda_thai = CODA_MAP.get(coda_key, "")

    if vowel_key == "o" and coda_thai:
        onset_thai = onset_thai or "ก"
        if len(onset_thai) > 1: return onset_thai[0] + onset_thai[1] + tone + coda_thai
        return onset_thai + tone + coda_thai

    if vowel_key == "a" and coda_thai:
        onset_thai = onset_thai or "ก"
        if len(onset_thai) > 1: return onset_thai[0] + onset_thai[1] + "ั" + tone + coda_thai
        return onset_thai + "ั" + tone + coda_thai

    if vowel_key in ("er", "oee") and coda_thai in {"ม", "น", "ง"}:
        onset_thai = onset_thai or "ก"
        if len(onset_thai) > 1: return "เ" + onset_thai[0] + onset_thai[1] + "ิ" + tone + coda_thai
        return "เ" + onset_thai + "ิ" + tone + coda_thai

    return assemble(onset_thai, vowel_key, tone) + coda_thai

def recursive_split(roman: str) -> Optional[str]:
    if not roman: return ""
    for i in range(len(roman), 1, -1):
        prefix = roman[:i]
        res = convert_syllable(prefix)
        if res:
            remainder = roman[i:]
            if not remainder: return res
            rem_res = recursive_split(remainder)
            if rem_res: return res + rem_res
    return None

# ===============================
# 3. DICTIONARY
# ===============================

@dataclass
class DictEntry:
    roman: str
    thai: str
    freq: int = 1

BASE_DICTIONARY = [
    DictEntry("khon3", "คน", 100), DictEntry("khoon3", "คุณ", 90),
    DictEntry("khao3", "เขา", 80), DictEntry("baan3", "บ้าน", 95),
    DictEntry("di1", "ดี", 85), DictEntry("phuean3", "เพื่อน", 90),
    DictEntry("er", "เออ", 120), DictEntry("err", "เออะ", 110),
    DictEntry("dern", "เดิน", 200),
]

COMPOUND_WORDS = [
    DictEntry("khanom",   "ขนม",     500),
    DictEntry("?aacaan",  "อาจารย์", 500),
    DictEntry("aacaan",   "อาจารย์", 500),
    DictEntry("ajarn",    "อาจารย์", 500),
    DictEntry("?aahaan",  "อาหาร",   500),
    DictEntry("aahaan",   "อาหาร",   500),
    DictEntry("?arory",   "อร่อย",   500),
    DictEntry("arory",    "อร่อย",   500),
    DictEntry("aroy",     "อร่อย",   450), 
    DictEntry("aroi",     "อร่อย",   450),
    DictEntry("phuying",  "ผู้หญิง",  500),
    DictEntry("sawatdii", "สวัสดี",  1000),
    DictEntry("sabay",    "สบาย",    400),
    DictEntry("sanuk",    "สนุก",    400),
    DictEntry("sanam",    "สนาม",    300),
    DictEntry("arak",     "อรักษ์",  300),
    DictEntry("talaat",   "ตลาด",    300),
    DictEntry("thalay",   "ทะเล",    300),
    DictEntry("welaa",    "เวลา",    300),
    DictEntry("naka",     "นะคะ",    300),
    DictEntry("khrap",    "ครับ",    300),
    # Pseudo-clusters
    DictEntry("sabaay",   "สบาย",    400),
    DictEntry("sadaeng",  "แสดง",    350),
    DictEntry("sathaanii","สถานี",   350),
    DictEntry("satrii",   "สตรี",    300),
    DictEntry("thanon",   "ถนน",     450),
    DictEntry("samut",    "สมุด",    350),
    DictEntry("samoe",    "เสมอ",    350),
    DictEntry("sanaam",   "สนาม",    350),
    DictEntry("chalaat",  "ฉลาด",    350),
    DictEntry("phanaek",  "แผนก",    300),
    DictEntry("chalaam",  "ฉลาม",    300),
    DictEntry("khaya",    "ขยะ",     300),
    DictEntry("sara",     "สระ",     300),
    DictEntry("sataem",   "สแตมป์",  250),
    DictEntry("khamooy",   "ขโมย",    350),
    DictEntry("samaakhom", "สมาคม",   300),
    DictEntry("samaachik", "สมาชิก",   300),
    DictEntry("samaathi",  "สมาธิ",    300),
]

AI_IRREGULARS = [
    DictEntry("cay", "ใจ", 200), DictEntry("khray", "ใคร", 200),
    DictEntry("may", "ใหม่", 200), DictEntry("hay", "ให้", 200),
    DictEntry("chay", "ใช่", 200),
]

VOWEL_SUGGESTIONS = [
    DictEntry("a", "อะ", 150), DictEntry("a", "อา", 140),
    DictEntry("ai", "ไอ", 130), DictEntry("ay", "ไอ", 130),
]

DICTIONARY = BASE_DICTIONARY + COMPOUND_WORDS + AI_IRREGULARS + VOWEL_SUGGESTIONS
DICT_LOOKUP = {e.roman.lower(): e.thai for e in DICTIONARY}

def convert_token(token: str) -> str:
    token = token.lower()
    if token in DICT_LOOKUP: return DICT_LOOKUP[token]
    syl = convert_syllable(token)
    if syl: return syl
    compound = recursive_split(token)
    if compound: return compound
    return "?"

def convert_phrase(text: str) -> str:
    """Converts a full phrase/sentence by splitting on spaces."""
    return " ".join(convert_token(t) for t in text.split())

def alt_onset_suggestions(buffer):
    roman = buffer.lower()
    core, _ = split_tone(roman)
    vowel_key, before, after = match_vowel(core)
    if not vowel_key and not before: roman_onset, _ = match_prefix(ONSET_KEYS, core)
    else: roman_onset, _ = match_prefix(ONSET_KEYS, before)
    if roman_onset not in ALT_ONSET_FORMS: return []
    default_thai = CONSONANT_ONSET.get(roman_onset, "")
    base_thai = convert_token(buffer)
    if not base_thai or base_thai == "?": return []
    alts = []
    for alt in ALT_ONSET_FORMS[roman_onset]:
        if alt == default_thai: continue
        thai_form = base_thai.replace(default_thai, alt, 1)
        alts.append(DictEntry(roman=buffer, thai=thai_form, freq=40))
    return alts

def alt_coda_suggestions(buffer):
    roman = buffer.lower()
    core, _ = split_tone(roman)
    vowel_key, _, after = match_vowel(core)
    if not vowel_key: return [] 
    coda_key, _ = match_coda(after)
    if coda_key not in ALT_CODA_FORMS: return []
    default_coda = CODA_MAP.get(coda_key, "")
    base_thai = convert_token(buffer)
    if not base_thai or base_thai == "?" or not base_thai.endswith(default_coda): return []
    base_stem = base_thai[: -len(default_coda)]
    alts = []
    for alt in ALT_CODA_FORMS[coda_key]:
        if alt == default_coda: continue
        alts.append(DictEntry(roman=buffer, thai=base_stem + alt, freq=35))
    return alts

def suggest(buffer: str, max_suggestions: int = 8) -> List[DictEntry]:
    q = buffer.lower()
    if not q: return []
    q_core = q[:-1] if q[-1] in "12345" else q
    exact_prefix = [e for e in DICTIONARY if e.roman.startswith(q_core)]
    def simple_distance(a, b):
        n = min(len(a), len(b))
        diff = sum(a[i] != b[i] for i in range(n)) + abs(len(a) - len(b))
        return diff
    fuzzy = [e for e in DICTIONARY if 0 < simple_distance(q_core, e.roman) <= 1]
    seen = set()
    results = []
    def add(entries):
        for e in entries:
            key = (e.roman, e.thai)
            if key not in seen:
                seen.add(key); results.append(e)
    # Add base conversion first if valid
    base_val = convert_token(q)
    if base_val and base_val != "?":
        add([DictEntry(q, base_val, 999)])
    add(exact_prefix)
    add(fuzzy)
    add(alt_onset_suggestions(buffer))
    add(alt_coda_suggestions(buffer))
    results.sort(key=lambda e: e.freq, reverse=True)
    return results[:max_suggestions]

# ===============================
# 4. STREAMLIT UI
# ===============================

st.set_page_config(page_title="Thai IME", page_icon="🇹🇭", layout="centered")

# --- SESSION STATE INITIALIZATION ---
if 'draft_text' not in st.session_state:
    st.session_state['draft_text'] = ""
if 'last_roman' not in st.session_state:
    st.session_state['last_roman'] = ""

def append_word(word):
    """Appends word to draft text"""
    if st.session_state.draft_text:
        st.session_state.draft_text += " " + word
    else:
        st.session_state.draft_text = word

def submit_input():
    """Callback: commits input to draft, stores for suggestions, and clears input"""
    roman = st.session_state.input_text
    if roman:
        # 1. Convert
        thai_word = convert_phrase(roman)
        # 2. Append to Draft
        append_word(thai_word)
        # 3. Save for suggestions display
        st.session_state.last_roman = roman
        # 4. Clear Input
        st.session_state.input_text = ""

# --- SIDEBAR: CHEAT SHEET (3 SECTIONS) ---
with st.sidebar:
    st.title("Cheat Sheet 📖")
    
    with st.expander("1. Vowels", expanded=True):
        st.markdown("""
        | Roman | Pre | Stack | Post | Ex. (k) |
        | :--- | :---: | :---: | :---: | :--- |
        | **a** | - | - | ะ | กะ |
        | **aa** | - | - | า | กา |
        | **i** | - | ิ | - | กิ |
        | **ii** | - | ี | - | กี |
        | **u** | - | ุ | - | กุ |
        | **uu** | - | ู | - | กู |
        | **e** | เ | ็ | - | เก็น |
        | **ee** | เ | - | - | เก |
        | **o** | โ | - | ะ | โกะ |
        | **oo** | โ | - | - | โก |
        | **ae** | แ | - | ะ | แกะ |
        | **aee** | แ | - | - | แก |
        | **oe** | เ | - | อะ | เกอะ |
        | **or** | เ | - | าะ | เกาะ |
        | **ia** | เ | ี | ย | เกีย |
        | **ua** | - | ั | ว | กัว |
        | **ai** | ไ | - | - | ไก |
        | **aw** | เ | - | า | เกา |
        | **uea** | เ | ื | อ | เกือ |
        | **am** | - | - | ำ | กำ |
        """)

    with st.expander("2. Consonants & Tones"):
        st.markdown("""
        **Consonants**
        * `k` = ก, `kh` = ข
        * `p` = ป, `ph` = ผ
        * `t` = ต, `th` = ถ
        * `ng` = ง, `ch` = ช
        
        **Tones**
        * `1` = Mid, `2` = Low (่)
        * `3` = Falling (้), `4` = High (๊)
        * `5` = Rising (๋)
        """)

    with st.expander("3. Tips & Compounds"):
        st.markdown("""
        **Typing Tips**
        * **Enter Key**: Commits the word and clears the input box.
        * **Suggestions**: Appear *after* you hit Enter (based on what you just added).
        """)

# --- MAIN PAGE ---
st.title("🇹🇭 Thai Word Converter")

# 1. Result Text
st.markdown("##### Result Text")
st.text_area(
    label="Result",
    key="draft_text",
    height=100,
    label_visibility="collapsed"
)

# 2. Roman Input
st.markdown("##### Enter Romanized Thai")
st.text_input(
    label="Input", 
    key="input_text", # Linked to session state
    placeholder="Type (e.g., sabaay) and hit ENTER to add...",
    label_visibility="collapsed",
    on_change=submit_input # Triggers commit & clear on Enter
)

# 3. Suggestions (Based on LAST submitted word)
if st.session_state.last_roman:
    suggestions = suggest(st.session_state.last_roman)
    if suggestions:
        st.markdown(f"**Alternatives for:** `{st.session_state.last_roman}`")
        cols = st.columns(4)
        for i, s in enumerate(suggestions):
            with cols[i % 4]:
                st.button(
                    f"{s.thai}\n({s.roman})", 
                    key=f"btn_{i}", 
                    on_click=append_word, 
                    args=(s.thai,)
                )