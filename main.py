import streamlit as st
import pandas as pd
import os
import random

# --- Page Config ---
st.set_page_config(page_title="Vocab Quiz", page_icon="📝", layout="centered")

st.header("📝 Vocabulary Quiz [NAWL]")

# --- CSS Fix for Buttons and UI ---
st.markdown("""
<style>
    /* 1. Hide Streamlit Branding/Header */
    header {visibility: hidden;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0); height: 0px;}
    footer {visibility: hidden;}

    /* 2. Force White Background */
    .stApp {
        background-color: white !important;
    }
    
    /* 3. Global Text Color Fix */
    h1, h2, h3, p, span, div, label {
        color: #222222 !important;
    }

    /* 4. FIX FOR THE "BLACK BUTTON" ISSUE */
    div.stButton > button {
        background-color: #4285f4 !important; /* Nice Google Blue */
        color: white !important;              /* Force text to white */
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        height: 3em !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background-color: #357ae8 !important; /* Slightly darker on hover */
        color: white !important;
        border: none !important;
    }

    /* Remove the black focus ring around buttons */
    button:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* 5. Custom Card Styling */
    .word-card {
        text-align: center;
        padding: 40px;
        background-color: #fcfcfc;
        border: 2px solid #eeeeee;
        border-radius: 20px;
        margin-bottom: 25px;
    }

    /* 6. Feedback Box Styling */
    .feedback-box {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-top: 10px;
    }
    html, body {
        overflow: hidden;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---

def load_data():
    if not os.path.exists("words.csv"):
        st.error("File 'words.csv' not found. Please place it in the same folder.")
        st.stop()
    df = pd.read_csv("words.csv")
    df.columns = df.columns.str.strip()
    return df

def init_game():
    df = load_data()
    all_meanings = df['Meaning'].unique().tolist()
    
    questions = []
    # Follows CSV order
    for _, row in df.iterrows():
        distractors = [m for m in all_meanings if m != row['Meaning']]
        opts = random.sample(distractors, min(3, len(distractors)))
        opts.append(row['Meaning'])
        random.shuffle(opts)
        
        questions.append({
            "word": row['Word'],
            "correct": row['Meaning'],
            "pos": row['Pos'],
            "options": opts
        })
    
    st.session_state.questions = questions
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.submitted = False

if 'questions' not in st.session_state:
    init_game()

# --- Quiz UI ---

if st.session_state.index >= len(st.session_state.questions):
    st.markdown("<div style='text-align:center; padding: 50px;'>", unsafe_allow_html=True)
    st.markdown("<h1>Quiz Finished!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2>Final Score: {st.session_state.score} / {len(st.session_state.questions)}</h2>", unsafe_allow_html=True)
    if st.button("Restart Quiz"):
        init_game()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

q = st.session_state.questions[st.session_state.index]

st.write(f"Word {st.session_state.index + 1} of {len(st.session_state.questions)} | Score: {st.session_state.score} / {st.session_state.index + 1}")
# The Main Word Card


# Question Area
if not st.session_state.submitted:

    if q['pos'] == "n":
        pos = "Noun"
    elif q['pos'] == "verb":
        pos = "Verb"
    elif q['pos'] == "adj":
        pos = "Adjective"  
    elif q['pos'] == "adv":
        pos = "Adverb" 
    elif q['pos'] == "prep":
        pos = "Preposition"
    else:
        pos = "Undefined"

    st.markdown(f"""
<div class="word-card">
    <div style="color: #888; font-weight: bold; font-size: 14px;">{pos}</div>
    <h1 style="font-size: 48px; margin: 10px 0;">{q['word']}</h1>
</div>
    """, unsafe_allow_html=True)
    # Use Radio buttons
    choice = st.radio(
        "Select the meaning:",
        q['options'],
        index=None,
        key=f"radio_{st.session_state.index}"
    )
    
    if choice:
        st.session_state.user_choice = choice
        st.session_state.submitted = True
        if choice == q['correct']:
            st.session_state.score += 1
        st.rerun()

else:
    # Show feedback
    is_correct = st.session_state.user_choice == q['correct']
    bg_color = "#e6fffa" if is_correct else "#fff5f5"
    border_color = "#38b2ac" if is_correct else "#e53e3e"
    status = "Correct! ✅" if is_correct else "Incorrect! ❌"

    st.markdown(f"""
    <div class="feedback-box" style="background-color: {bg_color}; border: 2px solid {border_color};">
        <h2 style="margin: 0;">{status}</h2>
        <p style="margin: 15px 0; font-size: 18px;"><b>{q['word'].capitalize()}</b> means: <br><i>{q['correct']}</i></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("") # Spacer
    if st.button("Next Question ➔"):
        st.session_state.index += 1
        st.session_state.submitted = False
        st.rerun()

# Bottom Score Tracker
