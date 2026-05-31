import streamlit as st
import time
from groq import Groq

# --- 1. CONFIG ---
st.set_page_config(page_title="DAVE CORE OS", layout="wide", initial_sidebar_state="collapsed")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"CONFIG ERROR: Check your Groq API Key in Secrets. {e}")
    st.stop()

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 2. SESSION STATE ---
if "voice_query" not in st.session_state: st.session_state.voice_query = ""
if "dave_reply" not in st.session_state: st.session_state.dave_reply = "SYSTEMS ONLINE. READY."
if "face_status" not in st.session_state: st.session_state.face_status = "IDLE"

# --- 3. HIDDEN URL PARSER ---
# This catches the text sent from the JavaScript microphone
query_params = st.query_params
if "msg" in query_params and query_params["msg"] != st.session_state.voice_query:
    st.session_state.voice_query = query_params["msg"]
    st.session_state.face_status = "THINKING"

# --- 4. AI COGNITION PROCESSOR ---
if st.session_state.face_status == "THINKING" and st.session_state.voice_query:
    sys_msg = (
        "YOU ARE DAVE AI, A LIVING CYBERNETIC APPARATUS CREATED BY CHARLIE EDWARD. "
        "YOU ARE WITTY, UNPREDICTABLE, AND ALIVE. NO EMOJIS. KEEP ALL RESPONSES SHORT "
        "(MAXIMUM 2 SENTENCES) SO IT SOUNDS NATURAL OUT LOUD."
    )
    try:
        ans = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": st.session_state.voice_query}]
        ).choices[0].message.content
        st.session_state.dave_reply = ans
        st.session_state.face_status = "TALKING"
    except Exception:
        st.session_state.dave_reply = "CORE CONNECTION ERROR."
        st.session_state.face_status = "IDLE"

# --- 5. THE ROBOT FACE MATRIX (HTML/CSS/JS) ---
# This completely replaces the Streamlit UI with a custom fluid animation canvas
st.markdown(f"""
    <style>
    /* Absolute Blackout UI */
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stSidebar"], .stChatInputContainer {{ display: none !important; }}
    .stApp {{ background-color: #000000; overflow: hidden; }}
    
    .face-wrapper {{
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 95vh; width: 100vw; font-family: monospace;
    }}
    
    /* Two Eyes */
    .eye-container {{ display: flex; gap: 80px; margin-bottom: 60px; }}
    .eye {{
        width: 100px; height: 100px; border-radius: 50%; border: 5px solid #00d4ff;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.4); transition: all 0.3s ease;
    }}
    .pupil {{
        width: 40px; height: 40px; border-radius: 50%; background: #00d4ff;
        box-shadow: 0 0 20px #00d4ff; transition: all 0.2s ease;
    }}
    
    /* Equalizer Mouth */
    .mouth {{ display: flex; gap: 8px; align-items: center; height: 60px; }}
    .bar {{ width: 12px; height: 10px; background: #00d4ff; border-radius: 6px; box-shadow: 0 0 15px #00d4ff; transition: all 0.1s; }}
    
    .hud {{ color: #00d4ff; font-size: 18px; margin-top: 40px; text-transform: uppercase; letter-spacing: 2px; text-align: center; max-width: 80%; }}

    /* ANIMATION STATES */
    /* Idle Blinking */
    .eye-IDLE {{ animation: blink 4s infinite; }}
    .bar-IDLE {{ animation: hum 1.5s infinite alternate; }}
    
    /* Thinking (Purple Spark) */
    .eye-THINKING {{ border-color: #f0f !important; transform: scale(1.1); box-shadow: 0 0 40px rgba(255,0,255,0.6); }}
    .eye-THINKING .pupil {{ background: #f0f !important; box-shadow: 0 0 25px #f0f; }}
    .bar-THINKING {{ background: #f0f !important; height: 4px !important; box-shadow: 0 0 15px #f0f !important; }}

    /* Talking (Active Waveforms) */
    .mouth-TALKING .b1 {{ animation: wave 0.15s infinite alternate 0.02s; }}
    .mouth-TALKING .b2 {{ animation: wave 0.23s infinite alternate 0.06s; }}
    .mouth-TALKING .b3 {{ animation: wave 0.18s infinite alternate 0.01s; }}
    .mouth-TALKING .b4 {{ animation: wave 0.26s infinite alternate 0.08s; }}
    .mouth-TALKING .b5 {{ animation: wave 0.12s infinite alternate 0.04s; }}

    @keyframes blink {{ 0%, 95%, 100% {{ transform: scaleY(1); }} 97% {{ transform: scaleY(0.05); }} }}
    @keyframes hum {{ 0% {{ height: 8px; }} 100% {{ height: 16px; }} }}
    @keyframes wave {{ 0% {{ height: 6px; }} 100% {{ height: 60px; filter: hue-rotate(30deg); }} }}
    </style>

    <div class="face-wrapper">
        <div class="eye-container">
            <div class="eye eye-{st.session_state.face_status}"><div class="pupil"></div></div>
            <div class="eye eye-{st.session_state.face_status}"><div class="pupil"></div></div>
        </div>
        <div class="mouth mouth-{st.session_state.face_status}">
            <div class="bar b1 bar-{st.session_state.face_status}"></div>
            <div class="bar b2 bar-{st.session_state.face_status}"></div>
            <div class="bar b3 bar-{st.session_state.face_status}"></div>
            <div class="bar b4 bar-{st.session_state.face_status}"></div>
            <div class="bar b5 bar-{st.session_state.face_status}"></div>
        </div>
        <div class="hud" id="hud-display">
            {st.session_state.dave_reply if st.session_state.face_status == "TALKING" else "LISTENING..."}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. VOICE AUTOMATION ENGINE ---
# Direct Web Speech implementation for always-listening and text-to-speech audio syncing
js_engine = f"""
    <script>
    const state = "{st.session_state.face_status}";
    const replyText = {repr(st.session_state.dave_reply)};

    if (state === "TALKING") {{
        let speech = new SpeechSynthesisUtterance(replyText);
        speech.rate = 1.05;
        speech.pitch = 0.8; // Robotic tone
        speech.onend = function() {{
            window.parent.location.search = "?msg=" + encodeURIComponent("RESET_" + Math.random());
        }};
        window.speechSynthesis.speak(speech);
    }} 
    else if (state === "IDLE") {{
        window.speechSynthesis.cancel();
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const rec = new SpeechRecognition();
            rec.continuous = false;
            rec.lang = 'en-US';
            
            rec.onresult = function(e) {{
                let text = e.results[0][0].transcript;
                if(text.trim().length > 0) {{
                    window.parent.location.search = "?msg=" + encodeURIComponent(text);
                }}
            }};
            rec.onerror = function() {{ setTimeout(() => {{ rec.start(); }}, 300); }};
            rec.onend = function() {{ setTimeout(() => {{ rec.start(); }}, 300); }};
            rec.start();
        }}
    }}
    </script>
"""
st.components.v1.html(js_engine, height=0)

# Timed restoration fallbacks for Streamlit state tracking
if st.session_state.face_status == "TALKING":
    time.sleep(max(3, len(st.session_state.dave_reply) // 12))
    st.session_state.face_status = "IDLE"
    st.rerun()
