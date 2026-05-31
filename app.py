import streamlit as st
import time
from groq import Groq

# --- 1. CONFIG ---
st.set_page_config(page_title="DAVE CORE V2", layout="wide", initial_sidebar_state="collapsed")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"CONFIG ERROR: Check your Groq API Key in Secrets. {e}")
    st.stop()

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 2. SESSION STATE ---
if "voice_query" not in st.session_state: st.session_state.voice_query = ""
if "dave_reply" not in st.session_state: st.session_state.dave_reply = "SYSTEMS ENGAGED. RECEPTORS WIDE OPEN."
if "face_status" not in st.session_state: st.session_state.face_status = "IDLE"

# --- 3. MODERN QUERY PARAM PARSER ---
try:
    current_params = st.query_params
    if "msg" in current_params and current_params["msg"] != st.session_state.voice_query:
        # Check if it's a reset token; if not, it's user input
        if not current_params["msg"].startswith("RESET_"):
            st.session_state.voice_query = current_params["msg"]
            st.session_state.face_status = "THINKING"
except Exception:
    pass

# --- 4. COGNITIVE PROCESSING (GROQ) ---
if st.session_state.face_status == "THINKING" and st.session_state.voice_query:
    sys_msg = (
        "YOU ARE DAVE AI, A LIVING CYBERNETIC ENGINE CREATED BY CHARLIE EDWARD. "
        "YOU ARE WITTY, BRUTALLY HONEST, AND ACTIVE. NO EMOJIS. KEEP ALL RESPONSES "
        "UNDER 2 SHORT SENTENCES SO IT SOUNDS IMPACTFUL AND NATURAL WHEN SPOKEN OUT LOUD."
    )
    try:
        ans = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": st.session_state.voice_query}]
        ).choices[0].message.content
        st.session_state.dave_reply = ans
        st.session_state.face_status = "TALKING"
    except Exception:
        st.session_state.dave_reply = "CORE COMM FREQUENCY FAULT."
        st.session_state.face_status = "IDLE"

# --- 5. THE SUPERSIZED MECHANICAL FACE MATRIX ---
state = st.session_state.face_status
st.markdown(f"""
    <style>
    /* Total app UI purge */
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stSidebar"], .stChatInputContainer {{ display: none !important; }}
    .stApp {{ background-color: #000000; overflow: hidden; }}
    
    .face-wrapper {{
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 95vh; width: 100vw; font-family: 'Courier New', monospace;
        user-select: none;
    }}
    
    /* MASSIVE TWO-EYE DESIGN */
    .eye-container {{ display: flex; gap: 120px; margin-bottom: 80px; }}
    .eye {{
        width: 160px; height: 160px; border-radius: 50%; border: 8px solid #00d4ff;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 50px rgba(0, 212, 255, 0.5); transition: all 0.2s ease;
    }}
    .pupil {{
        width: 65px; height: 65px; border-radius: 50%; background: #00d4ff;
        box-shadow: 0 0 35px #00d4ff; transition: all 0.2s ease;
    }}
    
    /* FULL WIDTH EQUALIZER JAW */
    .mouth {{ display: flex; gap: 14px; align-items: center; height: 120px; min-width: 320px; justify-content: center; }}
    .bar {{ width: 22px; height: 14px; background: #00d4ff; border-radius: 8px; box-shadow: 0 0 25px #00d4ff; transition: all 0.05s; }}
    
    .hud {{ color: #00d4ff; font-size: 22px; margin-top: 60px; text-transform: uppercase; letter-spacing: 3px; text-align: center; max-width: 75%; font-weight: bold; }}

    /* MECHANICAL STATES SETUP */
    /* Idle Pulsing and Automatic Blinking */
    .eye-IDLE {{ animation: blink 4.5s infinite, look-around 8s infinite alternate ease-in-out; }}
    .bar-IDLE {{ animation: hum 1.2s infinite alternate ease-in-out; }}
    
    /* Thinking Diagnostics (Purple Aggressive Shifts) */
    .eye-THINKING {{ border-color: #f0f !important; transform: scale(1.15); box-shadow: 0 0 60px rgba(255,0,255,0.7); }}
    .eye-THINKING .pupil {{ background: #f0f !important; box-shadow: 0 0 40px #f0f; transform: scale(0.6); }}
    .bar-THINKING {{ background: #f0f !important; height: 4px !important; box-shadow: 0 0 20px #f0f !important; }}

    /* Talking (Violent Synchronized Waveforms) */
    .mouth-TALKING .b1 {{ animation: wave 0.14s infinite alternate 0.01s; }}
    .mouth-TALKING .b2 {{ animation: wave 0.21s infinite alternate 0.04s; }}
    .mouth-TALKING .b3 {{ animation: wave 0.17s infinite alternate 0.02s; }}
    .mouth-TALKING .b4 {{ animation: wave 0.25s infinite alternate 0.06s; }}
    .mouth-TALKING .b5 {{ animation: wave 0.11s infinite alternate 0.03s; }}

    @keyframes blink {{ 0%, 95%, 100% {{ transform: scaleY(1); }} 97% {{ transform: scaleY(0.03); }} }}
    @keyframes look-around {{ 0%, 100% {{ transform: translate(0, 0); }} 25% {{ transform: translate(-8px, 4px); }} 70% {{ transform: translate(8px, -4px); }} }}
    @keyframes hum {{ 0% {{ height: 10px; }} 100% {{ height: 24px; }} }}
    @keyframes wave {{ 0% {{ height: 10px; }} 100% {{ height: 110px; filter: hue-rotate(40deg); }} }}
    </style>

    <div class="face-wrapper" id="clickTarget">
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
        <div class="hud">
            {st.session_state.dave_reply if state == "TALKING" else "• MICROPHONE ACTIVE - STATE: LISTENING •"}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. VOICE AUTOMATION ENGINE (JAVASCRIPT RUNTIMES) ---
# Employs a zero-latency loop linking audio output directly into microphone triggers
js_engine = f"""
    <script>
    const state = "{state}";
    const replyText = {repr(st.session_state.dave_reply)};

    // ROUTINE A: SPEECH SYNTHESIS ENGINE
    if (state === "TALKING") {{
        let speech = new SpeechSynthesisUtterance(replyText);
        speech.rate = 1.05;
        speech.pitch = 0.75; // Heavy robotic frequency tone
        speech.onend = function() {{
            // Clean state parameters and force a fast reload to jump straight back into listening mode
            window.parent.location.search = "?msg=" + encodeURIComponent("RESET_" + Math.random());
        }};
        window.speechSynthesis.speak(speech);
    }} 
    
    // ROUTINE B: AUTOMATED WEB MICROPHONE HOOK
    else if (state === "IDLE") {{
        window.speechSynthesis.cancel(); 
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const rec = new SpeechRecognition();
            rec.continuous = false;
            rec.interimResults = false;
            rec.lang = 'en-US';
            
            rec.onresult = function(e) {{
                let text = e.results[0][0].transcript;
                if(text.trim().length > 0) {{
                    window.parent.location.search = "?msg=" + encodeURIComponent(text);
                }}
            }};
            
            // Self-healing continuous connection loops
            rec.onerror = function() {{ setTimeout(() => {{ try {{ rec.start(); }} catch(e) {{}} }}, 300); }};
            rec.onend = function() {{ setTimeout(() => {{ try {{ rec.start(); }} catch(e) {{}} }}, 300); }};
            
            try {{ rec.start(); }} catch(e) {{}}
        }}
    }}

    // ROUTINE C: THE BROWSER SECURITY BYPASS CLICK CAPTURE
    document.getElementById('clickTarget').addEventListener('click', function() {{
        console.log("Audio pipeline manually re-verified via hardware click.");
    }});
    </script>
"""
st.components.v1.html(js_engine, height=0)

# Timed execution protection layers
if st.session_state.face_status == "TALKING":
    time.sleep(max(3, len(st.session_state.dave_reply) // 12))
    st.session_state.face_status = "IDLE"
    st.rerun()
