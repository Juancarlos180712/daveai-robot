import streamlit as st
import time
from groq import Groq
from streamlit_mic_recorder import speech_to_text

# --- 1. SET UP PLATFORM ENVIRONMENT ---
st.set_page_config(page_title="DAVE MAINFRAME V3", layout="wide", initial_sidebar_state="collapsed")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"SECRETS FAULT: Check Groq configuration settings. {e}")
    st.stop()

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 2. INITIALIZE LOGICAL SYSTEMS ---
if "dave_reply" not in st.session_state: st.session_state.dave_reply = "CORE SYSTEMS ONLINE. CAPTURE CHANNELS WAITING."
if "face_status" not in st.session_state: st.session_state.face_status = "IDLE"

# --- 3. GIANT NEON CYBERNETIC FACE MATRICES (CSS) ---
state = st.session_state.face_status
st.markdown(f"""
    <style>
    /* Wipeout traditional web app layout parameters */
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stSidebar"] {{ display: none !important; }}
    .stApp {{ background-color: #000000; overflow: hidden; }}
    
    .face-wrapper {{
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 70vh; width: 100vw; font-family: 'Courier New', monospace;
        user-select: none; margin-top: 20px;
    }}
    
    /* OVERSIZED DETECTOR BINOCULARS */
    .eye-container {{ display: flex; gap: 140px; margin-bottom: 60px; }}
    .eye {{
        width: 190px; height: 190px; border-radius: 50%; border: 10px solid #00d4ff;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 60px rgba(0, 212, 255, 0.6); transition: all 0.2s ease;
    }}
    .pupil {{
        width: 80px; height: 80px; border-radius: 50%; background: #00d4ff;
        box-shadow: 0 0 45px #00d4ff; transition: all 0.2s ease;
    }}
    
    /* MEGA FREQUENCY EQUALIZER JAW MODULE */
    .mouth {{ display: flex; gap: 16px; align-items: center; height: 130px; min-width: 400px; justify-content: center; }}
    .bar {{ width: 28px; height: 16px; background: #00d4ff; border-radius: 10px; box-shadow: 0 0 35px #00d4ff; transition: all 0.05s; }}
    
    .console-hud {{ 
        color: #00d4ff; font-size: 24px; margin-top: 40px; text-transform: uppercase; 
        letter-spacing: 3px; text-align: center; max-width: 80%; font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }}

    /* BEHAVIOR MOTOR STATES */
    /* Idle Tracking & Variable Blinks */
    .eye-IDLE {{ animation: blink 4s infinite, scanning 6s infinite alternate ease-in-out; }}
    .bar-IDLE {{ animation: hum 1s infinite alternate ease-in-out; }}
    
    /* Processing States (Hyper Neural Acceleration) */
    .eye-THINKING {{ border-color: #f0f !important; transform: scale(1.15); box-shadow: 0 0 80px rgba(255,0,255,0.8); }}
    .eye-THINKING .pupil {{ background: #f0f !important; box-shadow: 0 0 50px #f0f; transform: scale(0.5); }}
    .bar-THINKING {{ background: #f0f !important; height: 4px !important; box-shadow: 0 0 25px #f0f !important; }}

    /* Speech Outputs */
    .mouth-TALKING .b1 {{ animation: wave 0.13s infinite alternate 0.01s; }}
    .mouth-TALKING .b2 {{ animation: wave 0.20s infinite alternate 0.04s; }}
    .mouth-TALKING .b3 {{ animation: wave 0.16s infinite alternate 0.02s; }}
    .mouth-TALKING .b4 {{ animation: wave 0.24s infinite alternate 0.05s; }}
    .mouth-TALKING .b5 {{ animation: wave 0.11s infinite alternate 0.03s; }}

    @keyframes blink {{ 0%, 94%, 100% {{ transform: scaleY(1); }} 97% {{ transform: scaleY(0.02); }} }}
    @keyframes scanning {{ 0%, 100% {{ transform: translate(0, 0); }} 50% {{ transform: translate(-12px, 6px); }} }}
    @keyframes hum {{ 0% {{ height: 12px; }} 100% {{ height: 32px; }} }}
    @keyframes wave {{ 0% {{ height: 12px; }} 100% {{ height: 120px; filter: hue-rotate(50deg); }} }}
    
    /* Center the physical transmission interface block */
    .input-deck {{ display: flex; justify-content: center; align-items: center; width: 100vw; margin-top: 10px; }}
    div[data-testid="stVerticalBlock"] > div:has(button) {{ text-align: center !important; }}
    </style>

    <div class="face-wrapper">
        <div class="eye-container">
            <div class="eye eye-{state}"><div class="pupil"></div></div>
            <div class="eye eye-{state}"><div class="pupil"></div></div>
        </div>
        <div class="mouth mouth-{state}">
            <div class="bar b1 bar-{state}"></div>
            <div class="bar b2 bar-{state}"></div>
            <div class="bar b3 bar-{state}"></div>
            <div class="bar b4 bar-{state}"></div>
            <div class="bar b5 bar-{state}"></div>
        </div>
        <div class="console-hud">
            {st.session_state.dave_reply}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. SECURE AUDIO CAPTURE CONTROLLER ---
st.markdown('<div class="input-deck">', unsafe_allow_html=True)

# Direct secure bridge running on python context rather than basic raw iframes
vocal_input = speech_to_text(
    start_prompt="🔴 ENGAGE VOCAL LINK (CLICK TO TALK)",
    stop_prompt="🎚️ DECODING FREQUENCIES... (CLICK TO SUBMIT)",
    language='en',
    use_container_width=False,
    just_once=True,
    key='DAVE_MIC'
)

st.markdown('</div>', unsafe_allow_html=True)

# --- 5. COGNITION EVALUATOR ---
if vocal_input:
    st.session_state.face_status = "THINKING"
    st.rerun()

if st.session_state.face_status == "THINKING":
    sys_msg = (
        "YOU ARE DAVE AI, A LIVING CYBERNETIC CORE CREATED BY CHARLIE EDWARD. "
        "YOU ARE EXTREMELY ALIVE, WITTY, AND BRUTALLY COLD. NO EMOJIS. KEEP ALL RESPONSES "
        "UNDER TWO SENTENCES LONG."
    )
    try:
        ans = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": vocal_input}]
        ).choices[0].message.content
        st.session_state.dave_reply = ans
        st.session_state.face_status = "TALKING"
    except Exception:
        st.session_state.dave_reply = "CORE FREQUENCY CONNECTION REFUSED."
        st.session_state.face_status = "IDLE"
    st.rerun()

# --- 6. VOICE GENERATION AND FALLBACK EXECUTION RESET ---
if st.session_state.face_status == "TALKING":
    # Employs simple text-to-speech engine frame directly matching the updated reply
    js_speech = f"""
        <script>
        window.speechSynthesis.cancel();
        let voiceTrack = new SpeechSynthesisUtterance({repr(st.session_state.dave_reply)});
        voiceTrack.rate = 1.05;
        voiceTrack.pitch = 0.75;
        window.speechSynthesis.speak(voiceTrack);
        </script>
    """
    st.components.v1.html(js_speech, height=0)
    
    # Calculate screen lock animation time based on syllable lengths
    calculated_delay = max(3, len(st.session_state.dave_reply) // 12)
    time.sleep(calculated_delay)
    st.session_state.face_status = "IDLE"
    st.rerun()
