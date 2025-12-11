import streamlit as st
from dataclasses import dataclass
from typing import List, Optional

# ===============================
# 1. MAPPINGS & DATA
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
    "th": ["ถ", "ท", "ธ", "ฒ", "ฐ"], "ph": ["ผ", "พ", "ภ"],
    "ch": ["ช", "ฉ", "ฌ"], "s":  ["ส", "ซ", "ศ", "ษ"],
    "h":  ["ห", "ฮ"], "y":  ["ย", "ญ"], "f":  ["ฟ", "ฝ"],
    "k":  ["ก", "ไก"], "kh": ["ข", "ค", "ฆ"], "d":  ["ด", "ฎ"],
    "t":  ["ต", "ฏ"], "n":  ["น", "ณ"], "l":  ["ล", "ฬ"],
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

TONE_MAP = {"1": "Mid", "2": "่ (Low)", "3": "้ (Falling)", "4": "๊ (High)", "5": "๋ (Rising)"}
CODA_MAP = {"ng": "ง", "k": "ก", "t": "ด", "p": "บ", "m": "ม", "n": "น", "w": "ว", "y": "ย"}
CODA_KEYS = sorted(CODA_MAP.keys(), key=len, reverse=True)

# ===============================
# 2. CORE CONVERSION LOGIC
# ===============================

def split_tone(s: str):
    # Map back to simple char for processing
    t_map = {"1": "", "2": "่", "3": "้", "4": "๊", "5": "๋"}
    if s and s[-1] in t_map: return s[:-1], t_map[s[-1]]
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
        c1, c2 = onset_thai[0], onset_thai[1]
        return pre + c1 + c2 + main + tone + post
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

    # Rules
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
    DictEntry("khanom", "ขนม", 500), DictEntry("ajarn", "อาจารย์", 500),
    DictEntry("?aacaan", "อาจารย์", 500), DictEntry("aacaan", "อาจารย์", 500),
    DictEntry("arory", "อร่อย", 500), DictEntry("aroy", "อร่อย", 450), 
    DictEntry("aroi", "อร่อย", 450), DictEntry("phuying", "ผู้หญิง", 500),
    DictEntry("sawatdii", "สวัสดี", 1000), DictEntry("sabay", "สบาย", 400),
    DictEntry("sanuk", "สนุก", 400), DictEntry("sanam", "สนาม", 300),
    # Pseudo-clusters
    DictEntry("sabaay", "สบาย", 400), DictEntry("sadaeng", "แสดง", 350),
    DictEntry("sathaanii","สถานี", 350), DictEntry("satrii", "สตรี", 300),
    DictEntry("thanon", "ถนน", 450), DictEntry("samut", "สมุด", 350),
    DictEntry("samoe", "เสมอ", 350), DictEntry("sanaam", "สนาม", 350),
    DictEntry("chalaat", "ฉลาด", 350), DictEntry("phanaek", "แผนก", 300),
    DictEntry("chalaam", "ฉลาม", 300), DictEntry("khaya", "ขยะ", 300),
    DictEntry("sara", "สระ", 300), DictEntry("sataem", "สแตมป์", 250),
    DictEntry("khamooy", "ขโมย", 350), DictEntry("samaakhom", "สมาคม", 300),
    DictEntry("samaachik", "สมาชิก", 300), DictEntry("samaathi", "สมาธิ", 300),
]

AI_IRREGULARS = [
    DictEntry("cay", "ใจ", 200), DictEntry("khray", "ใคร", 200),
    DictEntry("may", "ใหม่", 200), DictEntry("hay", "ให้", 200),
    DictEntry("chay", "ใช่", 200),
]

DICTIONARY = BASE_DICTIONARY + COMPOUND_WORDS + AI_IRREGULARS
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
    return " ".join(convert_token(t) for t in text.split())

def simple_distance(a, b):
    a, b = a.lower(), b.lower()
    if abs(len(a) - len(b)) > 2: return 999
    n = min(len(a), len(b))
    diff = sum(a[i] != b[i] for i in range(n))
    diff += abs(len(a) - len(b))
    return diff

def suggest(buffer: str, max_suggestions: int = 8) -> List[DictEntry]:
    q = buffer.lower()
    if not q: return []
    q_core = q[:-1] if q[-1] in "12345" else q
    exact_prefix = [e for e in DICTIONARY if e.roman.startswith(q_core)]
    fuzzy = [e for e in DICTIONARY if 0 < simple_distance(q_core, e.roman) <= 1]
    
    seen = set()
    results = []
    def add(entries):
        for e in entries:
            key = (e.roman, e.thai)
            if key not in seen:
                seen.add(key); results.append(e)
    add(exact_prefix)
    add(fuzzy)
    results.sort(key=lambda e: e.freq, reverse=True)
    return results[:max_suggestions]

# ===============================
# 4. STREAMLIT UI
# ===============================

st.set_page_config(page_title="Thai IME Tester", page_icon="🇹🇭")

st.title("🇹🇭 Thai Phonetic IME")
st.markdown("Type Romanized Thai (e.g., *sawatdii*, *khanom*, *thaaw2*) to see the conversion.")

# --- CHEAT SHEET SECTION ---
with st.expander("📖 Cheat Sheet & Instructions (How to Type)"):
    tab1, tab2, tab3 = st.tabs(["Tone Mappings", "Consonant Onsets", "Vowels"])
    
    with tab1:
        st.markdown("### Tone Numbers")
        st.markdown("Type these numbers at the end of a syllable.")
        tone_data = [{"Key": k, "Tone": v} for k, v in TONE_MAP.items()]
        st.table(tone_data)

    with tab2:
        st.markdown("### Initial Consonants")
        st.markdown("Sorted by length. Type the **Key** to get the **Thai Char**.")
        # Convert dictionary to list of dicts for display
        cons_data = [{"Key": k, "Thai Char": v} for k, v in CONSONANT_ONSET.items()]
        st.dataframe(cons_data, use_container_width=True)
    
    with tab3:
        st.markdown("### Vowels")
        st.markdown("Type the **Key** to get the vowel combination.")
        # Simplify Vowel Map for display (just showing key and components)
        vowel_disp = []
        for k, v in VOWEL_MAP.items():
            pre, main, post = v
            display_str = f"{pre} - {main} - {post}"
            vowel_disp.append({"Key": k, "Structure": display_str})
        st.dataframe(vowel_disp, use_container_width=True)

# --- MAIN APP ---
with st.container():
    roman_input = st.text_input("Roman Input:", placeholder="Type here... (e.g., sabaay, aroy, thaaw2)", key="input")

    if roman_input:
        # 1. Base Conversion
        base_thai = convert_phrase(roman_input)
        
        st.markdown("### Base Conversion")
        st.success(f"**{base_thai}**")

        # 2. Suggestions
        suggestions = suggest(roman_input)
        
        st.markdown("### Suggestions")
        if suggestions:
            cols = st.columns(3)
            for i, s in enumerate(suggestions):
                with cols[i % 3]:
                    st.button(f"{s.thai} ({s.roman})", key=f"sug_{i}")
        else:
            st.caption("No additional suggestions found.")

st.markdown("---")
st.caption("Tip: Check the Cheat Sheet above for Tones (1-5) and specific spellings.")