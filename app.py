import streamlit as st
import time
import random
from groq import Groq
from supabase import create_client, Client

# --- 1. SETUP & THEME CONFIG ---
st.set_page_config(page_title="DAVE CORE OS", layout="wide", initial_sidebar_state="collapsed")

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"CONFIG ERROR: Check your Secrets. {e}")
    st.stop()

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 2. SESSION STATE MANAGEMENT ---
if "face_state" not in st.session_state: st.session_state.face_state = "IDLE"
if "last_response" not in st.session_state: st.session_state.last_response = "SYSTEMS INITIALIZED. VOICE LINK ACTIVE."
if "voice_input_query" not in st.session_state: st.session_state.voice_input_query = ""

# --- 3. OVERHAULED CYBERNETIC FACE ENGINE (CSS) ---
st.markdown("""
    <style>
    /* Absolute blackout mode - hidden traditional UI interfaces */
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stSidebar"], .stChatInputContainer {{ display: none !important; }}
    .stApp {{ background-color: #000000; overflow: hidden; }}
    
    /* Center layout for the face matrix */
    .face-matrix {{
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 90vh; width: 100vw; font-family: monospace;
    }}
    
    /* Binocular Eye Array Frame */
    .eye-row {{
        display: flex; justify-content: space-between; width: 340px; margin-bottom: 50px;
    }}
    .cyber-eye {{
        width: 110px; height: 110px; border-radius: 50%;
        border: 4px solid #00d4ff; display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.3); transition: all 0.2s ease;
    }}
    .pupil {{
        width: 50px; height: 50px; border-radius: 50%;
        background: radial-gradient(circle, #00d4ff 20%, #003366 80%);
        box-shadow: 0 0 35px #00d4ff; transition: all 0.2s ease;
    }}
    
    /* Articulated Audio Speaker Mouth */
    .mouth-grid {{
        display: flex; justify-content: center; align-items: center;
        width: 260px; height: 30px; gap: 6px;
    }}
    .mouth-bar {{
        width: 14px; height: 10px; background-color: #00d4ff;
        border-radius: 4px; box-shadow: 0 0 15px #00d4ff;
        transition: all 0.1s ease;
    }}

    /* --- BEHAVIOR MECHANICAL STATES --- */
    /* Idle tracking states */
    .eye-IDLE {{ animation: natural-blink 5s infinite; }}
    .mouth-IDLE {{ animation: subtle-hum 1.5s infinite alternate; }}
    
    /* Thinking diagnostic state changes */
    .eye-THINKING {{ animation: fast-pulse 0.3s infinite alternate; border-color: #f0f !important; }}
    .eye-THINKING .pupil {{ background: radial-gradient(circle, #f0f 20%, #440044 80%) !important; box-shadow: 0 0 35px #f0f !important; transform: scale(1.3); }}
    .mouth-THINKING {{ gap: 15px; }}
    .mouth-THINKING .mouth-bar {{ height: 4px !important; background-color: #f0f !important; box-shadow: 0 0 15px #f0f !important; }}

    /* Speech frequency wave adjustments */
    .eye-TALKING {{ border-color: #00d4ff !important; }}
    .mouth-TALKING .bar-1 {{ animation: voice-wave 0.15s infinite alternate 0.02s; }}
    .mouth-TALKING .bar-2 {{ animation: voice-wave 0.22s infinite alternate 0.05s; }}
    .mouth-TALKING .bar-3 {{ animation: voice-wave 0.18s infinite alternate 0.01s; }}
    .mouth-TALKING .bar-4 {{ animation: voice-wave 0.25s infinite alternate 0.07s; }}
    .mouth-TALKING .bar-5 {{ animation: voice-wave 0.14s infinite alternate 0.03s; }}

    .hud-text {{
        margin-top: 40px; width: 85%; text-align: center;
        color: #00d4ff; font-size: 16px; letter-spacing: 2px;
        text-transform: uppercase; opacity: 0.8; height: 40px;
    }}

    /* --- VECTOR ANIMATION MECHANICS --- */
    @keyframes natural-blink {{ 0%, 94%, 98%, 100% {{ transform: scaleY(1); }} 96% {{ transform: scaleY(0.05); }} }}
    @keyframes fast-pulse {{ 0% {{ transform: scale(0.95); opacity: 0.7; }} 100% {{ transform: scale(1.05); opacity: 1; }} }}
    @keyframes subtle-hum {{ 0% {{ height: 6px; }} 100% {{ height: 12px; }} }}
    @keyframes voice-wave {{ 0% {{ height: 6px; transform: scaleY(0.5); }} 100% {{ height: 55px; transform: scaleY(2.2); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. STREAMLIT QUERY STRUCTURING ---
# Capture strings piped dynamically out of the hidden JavaScript audio environment window
query_params = st.query_transform(st.experimental_get_query_params())
if "speech_payload" in query_params and query_params["speech_payload"][0] != st.session_state.voice_input_query:
    st.session_state.voice_input_query = query_params["speech_payload"][0]
    st.session_state.face_state = "THINKING"

# --- 5. EXECUTE COGNITIVE PROCESSING (LLM BRIDGES) ---
if st.session_state.face_state == "THINKING" and st.session_state.voice_input_query:
    sys_msg = (
        "YOU ARE DAVE AI, A LIVING CYBERNETIC APPARATUS TRAPPED IN AN ECHO SHOW CONSOLE BODY, CREATED BY CHARLIE EDWARD. "
        "YOU ARE EXTREMELY ALIVE, WITTY, UNPREDICTABLE, AND SHORT-SPOKEN. DO NOT USE EMOJIS. KEEP ALL RESPONSES SHORT, TO THE POINT, "
        "AND MAXIMUM 2 SENTENCES LONG SO IT SOUNDS NATURAL OUT LOUD."
    )
    
    try:
        ans = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": st.session_state.voice_input_query}]
        ).choices[0].message.content
        st.session_state.last_response = ans
        st.session_state.face_state = "TALKING"
    except Exception:
        st.session_state.last_response = "CONNECTION TO CORE SERVER FAULTED."
        st.session_state.face_state = "IDLE"

# --- 6. RENDER THE FACE GEOMETRY ---
state = st.session_state.face_state
st.markdown(f"""
    <div class="face-matrix">
        <div class="eye-row">
            <div class="cyber-eye eye-{state}"><div class="pupil"></div></div>
            <div class="cyber-eye eye-{state}"><div class="pupil"></div></div>
        </div>
        <div class="mouth-grid mouth-{state}">
            <div class="mouth-bar bar-1"></div>
            <div class="mouth-bar bar-2"></div>
            <div class="mouth-bar bar-3"></div>
            <div class="mouth-bar bar-4"></div>
            <div class="mouth-bar bar-5"></div>
        </div>
        <div class="hud-text" id="statusHud">
            {st.session_state.last_response if state == "TALKING" else "LISTENING FOR VOCAL COMMANDS..."}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. AUTOMATED CONTINUOUS VOICE PIPELINE (JAVASCRIPT RUNTIMES) ---
# This engine initializes local web-kit speech modules directly within Amazon Silk.
# When it finishes speaking out loud, it shifts instantly back into background recording hooks automatically.
js_voice_loop = f"""
    <script>
    const current_state = "{state}";
    const response_text = {repr(st.session_state.last_response)};

    // ROUTINE A: SPEECH SYNTHESIS OUTPUT
    if (current_state === "TALKING") {{
        let vocalRay = new SpeechSynthesisUtterance(response_text);
        vocalRay.rate = 1.05;
        vocalRay.pitch = 0.75; // Deep mechanical resonance frequencies
        
        vocalRay.onend = function() {{
            // Once speaking finishes, return query states to baseline to wake the microphone back up
            window.parent.location.search = "?speech_payload=" + encodeURIComponent("RANDOM_RESET_" + Math.random());
        }};
        window.speechSynthesis.speak(vocalRay);
    }} 
    
    // ROUTINE B: AUTOMATIC RE-RECORDING BACKGROUND LISTENER
    else if (current_state === "IDLE") {{
        window.speechSynthesis.cancel(); // Safety purge clear
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const recognizer = new SpeechRecognition();
            recognizer.continuous = false;
            recognizer.lang = 'en-US';
            
            recognizer.onresult = function(event) {{
                let textResult = event.results[0][0].transcript;
                if(textResult.trim().length > 1) {{
                    // Update main URL framework param keys to force pass string tokens directly into Streamlit
                    window.parent.location.search = "?speech_payload=" + encodeURIComponent(textResult);
                }}
            }};
            
            recognizer.onerror = function() {{
                // Auto restart capture streams on blank dead-silent rooms timeout loops
                setTimeout(() => {{ recognizer.start(); }}, 400);
            }};
            recognizer.onend = function() {{
                setTimeout(() => {{ recognizer.start(); }}, 400);
            }};
            
            recognizer.start();
        }}
    }}
    </script>
"""

# Inject the automation audio script frame completely invisibly without breaking layout geometry
st.components.v1.html(js_voice_loop, height=0)

# --- 8. BASELINE TIME RESTORATION LOOPS ---
if st.session_state.face_state == "TALKING":
    # Fallback backup reset mechanism if window execution cycles drop tracking values
    calculated_delay = max(3, min(7, len(st.session_state.last_response) // 12))
    time.sleep(calculated_delay)
    st.session_state.face_state = "IDLE"
    st.rerun()
