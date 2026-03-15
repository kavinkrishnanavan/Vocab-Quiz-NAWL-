import streamlit as st
import pandas as pd
import os
import random
import time

# --- Page Config ---
st.set_page_config(page_title="Vocab Quiz", page_icon="📝", layout="centered")

st.markdown("<h1>📝<u><i>Vocabulary Quiz</i></u></h1>" , unsafe_allow_html=True)

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

SESSION_SIZE = 25
CSV_FILE = "words.csv"

def load_data():
    if not os.path.exists(CSV_FILE):
        st.error(f"File '{CSV_FILE}' not found. Please place it in the same folder.")
        st.stop()
    
    try:
        df = pd.read_csv(CSV_FILE)
        # Clean column names
        df.columns = df.columns.str.strip()
        # Clean string data
        if 'Word' in df.columns:
            df['Word'] = df['Word'].astype(str).str.strip()
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame() # Return empty if file is empty

def init_session():
    df = load_data()
    
    if df.empty:
        st.session_state.game_over = True
        return

    st.session_state.game_over = False
    
    # Get all potential meanings for distractors
    all_meanings = df['Meaning'].unique().tolist()
    
    # --- UPDATED LOGIC HERE ---
    # Instead of head(), we use sample() to get random words.
    # We use min() to handle cases where the CSV has fewer words than SESSION_SIZE
    sample_n = min(len(df), SESSION_SIZE)
    current_batch = df.sample(n=sample_n)
    
    questions = []
    
    for _, row in current_batch.iterrows():
        # Generate distractors
        distractors = [m for m in all_meanings if m != row['Meaning']]
        # Handle case where there aren't enough distractors
        if len(distractors) < 3:
            opts = distractors + [row['Meaning']]
        else:
            opts = random.sample(distractors, 3)
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
    st.session_state.start_time = time.time() # Start Timer

if 'questions' not in st.session_state or 'game_over' not in st.session_state:
    init_session()

# --- Quiz UI ---

# Check if global list is finished (empty csv check)
if st.session_state.get('game_over', False):
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1>⚠️ CSV is empty!</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Check if Session is finished
if st.session_state.index >= len(st.session_state.questions):
    end_time = time.time()
    total_time = end_time - st.session_state.start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    total_q = len(st.session_state.questions)
    percentage = int((st.session_state.score / total_q) * 100) if total_q > 0 else 0

    st.markdown("<div style='text-align:center; padding: 10px;'>", unsafe_allow_html=True)
    st.markdown("<h2>Session Complete!</h2>", unsafe_allow_html=True)
    
    # Score Display
    st.markdown(f"<h3 style='color: #4285f4 !important;'>Score: {percentage}%</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 18px;'>You got {st.session_state.score} out of {total_q} correct.</p>", unsafe_allow_html=True)
    
    # Time Display
    st.markdown(f"<p style='font-size: 18px; color: #666 !important;'>⏱ Time Taken: {minutes}m {seconds}s</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Removed text saying "words have been removed"
    
    if st.button("Start New Session ➔"):
        # We clear the state to force init_session to run again and pick new random words
        del st.session_state.questions
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Display Current Question ---

q = st.session_state.questions[st.session_state.index]

st.progress((st.session_state.index) / len(st.session_state.questions))
st.caption(f"Question {st.session_state.index + 1} of {len(st.session_state.questions)}")

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
        pos = "Word"

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
    
    # Logic to proceed WITHOUT deleting word
    if st.button("Next Question ➔"):
        # 1. Advance the game state
        st.session_state.index += 1
        st.session_state.submitted = False
        st.rerun()