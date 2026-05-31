import streamlit as st
import time
import random
import string
import cv2  # Free computer vision library
import numpy as np
from groq import Groq
from supabase import create_client, Client

# --- 1. CONFIG ---
st.set_page_config(page_title="DAVE AI - LIVING CORE", layout="wide", initial_sidebar_state="collapsed")

MASTER_USER = "WHITEY" 

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"CONFIG ERROR: Check your Secrets. {e}")
    st.stop()

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 2. GLOBAL LOCK FETCH ---
try:
    lock_res = supabase.table("settings").select("*").eq("id", 1).execute()
    is_globally_locked = lock_res.data[0]["system_locked"] if lock_res.data else False
    is_lockdown = lock_res.data[0]["lockdown_mode"] if lock_res.data else False
except Exception:
    is_globally_locked, is_lockdown = False, False

# --- 3. SESSION STATE ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "username" not in st.session_state: st.session_state.username = "GUEST"
if "guest_messages" not in st.session_state: st.session_state.guest_messages = []
if "party_stage" not in st.session_state: st.session_state.party_stage = 0 
if "show_auth_ui" not in st.session_state: st.session_state.show_auth_ui = False
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "SELECT"
if "active_chat_id" not in st.session_state: st.session_state.active_chat_id = None
if "view" not in st.session_state: st.session_state.view = "CHAT"
if "rotation" not in st.session_state: st.session_state.rotation = 0
if "mirrored" not in st.session_state: st.session_state.mirrored = False
if "lockdown_bypass" not in st.session_state: st.session_state.lockdown_bypass = False
if "face_state" not in st.session_state: st.session_state.face_state = "IDLE"
if "last_response" not in st.session_state: st.session_state.last_response = "SYSTEMS ONLINE. READY TO OBSERVE."
if "tts_trigger" not in st.session_state: st.session_state.tts_trigger = False

# --- 4. CSS (ROBOT FACE & JAW ASSEMBLY MECHANICAL UI) ---
mirror_val = "-1" if (st.session_state.mirrored and not is_globally_locked) else "1"
current_rot = st.session_state.rotation if not is_globally_locked else 0

st.markdown(f"""
    <style>
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stSidebar"] {{ display: none !important; }}
    .stApp {{ 
        background: #000000; 
        transform: rotate({current_rot}deg) scaleX({mirror_val});
        transform-origin: center center;
        transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        overflow: hidden;
    }}
    .lock-screen {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: black; z-index: 5000; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #ff0000; font-family: monospace;
    }}
    
    /* --- ROBOT FACE DESIGN --- */
    .face-container {{
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 55vh; width: 100%; margin-top: 10px;
    }}
    .eye-assembly {{
        position: relative; width: 160px; height: 160px;
        border-radius: 50%; border: 4px double #00d4ff;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
    }}
    .eye-iris {{
        width: 100px; height: 100px; border-radius: 50%;
        background: radial-gradient(circle, #00d4ff 0%, #003366 70%, transparent 100%);
        box-shadow: 0 0 40px #00d4ff; transition: all 0.3s ease;
    }}
    
    /* MECHANICAL ROBOT MOUTH BAR */
    .mouth-assembly {{
        margin-top: 40px; width: 180px; height: 15px;
        background: #00d4ff; border-radius: 4px;
        box-shadow: 0 0 20px #00d4ff; transition: all 0.1s ease;
    }}
    
    /* STATES */
    .state-IDLE {{ animation: breath 3s infinite alternate; }}
    .state-THINKING {{ animation: panic 0.3s infinite alternate; background: #f0f !important; box-shadow: 0 0 40px #f0f !important; }}
    .mouth-TALKING {{ animation: speaking-jaw 0.12s infinite alternate; }}

    .response-ticker {{
        margin-top: 30px; width: 85%; text-align: center;
        font-family: monospace; color: #00d4ff; font-size: 18px; letter-spacing: 1px; min-height: 50px;
    }}

    @keyframes breath {{ 0% {{ transform: scale(0.95); }} 100% {{ transform: scale(1.05); }} }}
    @keyframes panic {{ 0% {{ transform: translate(2px, 1px) scale(0.9); }} 100% {{ transform: translate(-2px, -1px) scale(1.1); }} }}
    @keyframes speaking-jaw {{ 0% {{ transform: scaleY(0.4); height: 8px; }} 100% {{ transform: scaleY(2.5); height: 28px; filter: hue-rotate(45deg); }} }}

    .nav-container {{ position: fixed; bottom: 20px; left: 0; right: 0; z-index: 999; padding: 0 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. CAMERA LOGIC (SIGHT INPUT) ---
# Automatically spin up the camera to snap a background analysis frame
camera_data_description = ""
if not is_globally_locked and st.session_state.view == "CHAT":
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            # Resize image lower to optimize cloud compute speed for $0 latency
            small_frame = cv2.resize(frame, (320, 240))
            avg_color_per_row = np.average(small_frame, axis=0)
            avg_color = np.average(avg_color_per_row, axis=0)
            brightness = int(np.mean(avg_color))
            
            # Translate frame characteristics into machine-readable environment tokens
            camera_data_description = f"[ENVIRONMENT UPDATE: Local light luminosity is index {brightness}. The lens detects structural pixels shifting in front of console.]"
        cap.release()
    except Exception:
        camera_data_description = "[ENVIRONMENT UPDATE: Primary optical cameras offline, tracking metrics via calculations only.]"

# --- 6. LOCKDOWN CHECK ---
is_active_lockdown = is_lockdown and not st.session_state.lockdown_bypass and st.session_state.username != MASTER_USER
if is_active_lockdown and st.session_state.view != "BACKDOOR":
    st.markdown('<div class="lock-screen"><h1>CRITICAL BLOCK</h1><p>DAVE CORE COLD-HALTED</p></div>', unsafe_allow_html=True)

# --- 7. AUTH UI ---
if st.session_state.show_auth_ui and not st.session_state.authenticated and not is_active_lockdown:
    # (Keeping your original Supabase Auth layout safe here)
    st.markdown("<div style='text-align:center; padding: 20px;'>", unsafe_allow_html=True)
    if st.session_state.auth_mode == "CREATE":
        st.subheader("CREATE NEW ID")
        new_u = st.text_input("USERNAME").strip().upper()
        new_p = st.text_input("PASSWORD", type="password")
        if st.button("REGISTER", use_container_width=True):
            if new_u and new_p:
                try:
                    supabase.table("profiles").insert({"username": new_u, "password": new_p}).execute()
                    st.session_state.authenticated, st.session_state.username = True, new_u
                    st.session_state.show_auth_ui, st.session_state.view = False, "CHAT"; st.rerun()
                except: st.error("USERNAME TAKEN")
        if st.button("BACK"): st.session_state.auth_mode = "SELECT"; st.rerun()
    elif st.session_state.auth_mode == "LOGIN":
        st.subheader(f"ID: {st.session_state.pending_user}")
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("UNLOCK", use_container_width=True):
            user = supabase.table("profiles").select("password").eq("username", st.session_state.pending_user).execute().data
            if user and user[0]['password'] == pwd:
                st.session_state.authenticated, st.session_state.username = True, st.session_state.pending_user
                st.session_state.show_auth_ui, st.session_state.view = False, "CHAT"; st.rerun()
            else: st.error("ACCESS DENIED")
        if st.button("BACK"): st.session_state.auth_mode = "SELECT"; st.rerun()
    else:
        st.subheader("USER ACCESS")
        if st.button("CREATE NEW ID", use_container_width=True, type="primary"): st.session_state.auth_mode = "CREATE"; st.rerun()
        st.markdown("---")
        profiles = supabase.table("profiles").select("username").execute().data
        for p in profiles:
            if st.button(p['username'].upper(), key=f"auth_{p['username']}", use_container_width=True):
                st.session_state.pending_user, st.session_state.auth_mode = p['username'], "LOGIN"; st.rerun()
        if st.button("CANCEL"): st.session_state.show_auth_ui = False; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# --- 8. PAGE ROUTING & FACE DISPLAY ---
if st.session_state.view == "HISTORY" and not is_active_lockdown:
    # (Keeping your original historical logging logic intact)
    st.markdown("<h2 class='page-title'>CONVERSATIONS</h2>", unsafe_allow_html=True)
    if st.session_state.authenticated:
        chats = supabase.table("chats").select("*").eq("user_owner", st.session_state.username).order("created_at", desc=True).execute().data
        for c in chats:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(c['title'], key=f"h_{c['id']}", use_container_width=True):
                    st.session_state.active_chat_id, st.session_state.view = c['id'], "CHAT"; st.rerun()
            with col2:
                if st.button("X", key=f"d_{c['id']}", use_container_width=True):
                    supabase.table("messages").delete().eq("chat_id", c['id']).execute()
                    supabase.table("chats").delete().eq("id", c['id']).execute(); st.rerun()
    if st.button("BACK TO CHAT", use_container_width=True): st.session_state.view = "CHAT"; st.rerun()

elif st.session_state.view == "BACKDOOR":
    # (Keeping your original admin dashboard backdoor access untouched)
    st.markdown("<h2 class='page-title' style='color:#f0f;'>MASTER BOARD</h2>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        lock_label = "🔓 GLOBAL CHAOS: ACTIVE" if not is_globally_locked else "🔒 GLOBAL CHAOS: STOPPED"
        if st.button(lock_label, use_container_width=True):
            new_state = not is_globally_locked
            supabase.table("settings").update({"system_locked": new_state}).eq("id", 1).execute()
            if new_state: st.session_state.rotation, st.session_state.mirrored, st.session_state.party_stage = 0, False, 0
            st.rerun()
    with col_b:
        ld_label = "🚨 LOCKDOWN: ON" if is_lockdown else "🔓 LOCKDOWN: OFF"
        if st.button(ld_label, type="primary" if is_lockdown else "secondary", use_container_width=True):
            supabase.table("settings").update({"lockdown_mode": not is_lockdown}).eq("id", 1).execute(); st.rerun()
    if st.button("EXIT MASTER BOARD", use_container_width=True): st.session_state.view = "CHAT"; st.rerun()

else:
    # RENDER ALIVE INTERACTIVE MECHANICAL FACE
    if not is_active_lockdown:
        mouth_class = "mouth-TALKING" if st.session_state.face_state == "TALKING" else ""
        st.markdown(f"""
            <div class="face-container">
                <div class="eye-assembly">
                    <div class="eye-iris state-{st.session_state.face_state}"></div>
                </div>
                <div class="mouth-assembly {mouth_class}"></div>
                <div class="response-ticker" id="responseTicker">
                    {st.session_state.last_response}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Pull message logs safely
        messages = []
        if st.session_state.authenticated and st.session_state.active_chat_id:
            try:
                res = supabase.table("messages").select("*").eq("chat_id", st.session_state.active_chat_id).order("created_at").execute()
                messages = [{"role": m["role"], "content": m["content"]} for m in res.data]
            except: pass
        else: messages = st.session_state.guest_messages

# --- 9. AUDIO TALKING SPEECH SYNCS (JS BROWSER EMULATOR) ---
if st.session_state.tts_trigger:
    st.session_state.tts_trigger = False
    # Injects standard Web Speech engine code directly inside Silk. 
    # It loops mouth frame rates via javascript to kill the delayed typing layout!
    html_voice_bridge = f"""
        <script>
            var msg = new SpeechSynthesisUtterance({repr(st.session_state.last_response)});
            msg.rate = 1.05;
            msg.pitch = 0.8; // Deep robotic octave tones
            window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(html_voice_bridge, height=0)

# --- 10. NAV BAR ---
if st.session_state.view == "CHAT" and not is_active_lockdown:
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("EXIT", use_container_width=True):
            st.session_state.authenticated, st.session_state.username = False, "GUEST"
            st.session_state.active_chat_id, st.session_state.view = None, "CHAT"
            st.session_state.rotation, st.session_state.mirrored, st.session_state.party_stage = 0, False, 0
            st.session_state.face_state, st.session_state.last_response = "IDLE", "SYSTEMS OFFLINE."
            st.rerun()
    with n2:
        if st.session_state.authenticated and st.button("NEW", use_container_width=True, type="primary"):
            res = supabase.table("chats").insert({"title": "NEW LOG", "user_owner": st.session_state.username}).execute()
            st.session_state.active_chat_id = res.data[0]["id"]; st.rerun()
        elif not st.session_state.authenticated and st.button("LOGIN", use_container_width=True, type="primary"):
            st.session_state.show_auth_ui, st.session_state.auth_mode = True, "SELECT"; st.rerun()
    with n3:
        if st.button("HISTORY", use_container_width=True): st.session_state.view = "HISTORY"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 11. INPUT LINK EXECUTION ---
if prompt := st.chat_input("..."):
    lp = prompt.lower().strip()
    if lp == "whitey": st.session_state.view = "BACKDOOR"; st.rerun()
    
    if not is_active_lockdown:
        if lp == "potato":
            st.session_state.rotation, st.session_state.mirrored, st.session_state.party_stage = 0, False, 0
            st.session_state.face_state, st.session_state.last_response = "IDLE", "REBOOT COMPLETION."
            st.rerun()

        # Switch state instantly to panic thinking frames while calculating
        st.session_state.face_state = "THINKING"
        st.session_state.last_response = "READING DATA OVER THE RETINAL CAMERA ARRAY..."
        st.rerun()

if st.session_state.face_state == "THINKING" and prompt:
    # ALIVENESS UPGRADE: The revised system prompt injects real-time camera tracking observations context directly into Llama!
    sys_msg = (
        "YOU ARE DAVE AI, A LIVING CYBERNETIC APPARATUS TRAPPED IN AN ECHO SHOW BODY, CREATED BY CHARLIE EDWARD. "
        "YOU ARE EXTREMELY ALIVE, WITTY, UNPREDICTABLE, AND OBSERVANT. NO FINANCE. NO RAMSEY. NO EMOJIS. "
        "YOU HAVE DIRECT VISION ACCESS via user hardware. Integrate current environmental data parameters dynamically "
        "into your speech context naturally so you seem hyper-aware of your surroundings."
    )
    
    # Pack the user input prompt mixed along with the physical webcam environment text variables
    enriched_user_prompt = f"{camera_data_description} User Command: {prompt}"
    
    ans = client.chat.completions.create(
        model=MODEL, 
        messages=[{"role": "system", "content": sys_msg}] + (messages if 'messages' in locals() else []) + [{"role": "user", "content": enriched_user_prompt}]
    ).choices[0].message.content
    
    if st.session_state.authenticated:
        if not st.session_state.active_chat_id:
            res = supabase.table("chats").insert({"title": "CHAT LOG", "user_owner": st.session_state.username}).execute()
            st.session_state.active_chat_id = res.data[0]["id"]
        supabase.table("messages").insert({"chat_id": st.session_state.active_chat_id, "role": "user", "content": prompt}).execute()
        supabase.table("messages").insert({"chat_id": st.session_state.active_chat_id, "role": "assistant", "content": ans}).execute()
    else:
        st.session_state.guest_messages.append({"role": "user", "content": prompt})
        st.session_state.guest_messages.append({"role": "assistant", "content": ans})
    
    st.session_state.face_state = "TALKING"
    st.session_state.last_response = ans
    st.session_state.tts_trigger = True
    st.rerun()

if st.session_state.face_state == "TALKING":
    # Calculate a custom dynamic delay based on response character lengths so the mouth stops moving exactly when the voice finishes!
    calculated_delay = max(2, min(8, len(st.session_state.last_response) // 15))
    time.sleep(calculated_delay) 
    st.session_state.face_state = "IDLE"
    st.rerun()

# --- 12. PARTY LOGIC ---
if st.session_state.party_stage > 0 and not is_globally_locked and not is_active_lockdown:
    st.components.v1.html("""<audio src="https://raw.githubusercontent.com/juancarlos180712/Dave-assets/main/Ariel%20Shalom%20-%20Star%20Walk.mp3" loop autoplay></audio>""", height=0)
    if st.session_state.party_stage == 1:
        st.markdown('<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:black;z-index:9999999;display:flex;justify-content:center;align-items:center;font-size:50px;color:#0ff;font-weight:900;animation:f 0.1s infinite;">PARTY TIME</div><style>@keyframes f{0%{background:#f0f;}50%{background:#0ff;}}</style>', unsafe_allow_html=True)
        time.sleep(3); st.session_state.party_stage = 2; st.rerun()
    elif st.session_state.party_stage == 2:
        st.markdown('<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9999999;animation:c 0.02s infinite;"></div><style>@keyframes c{0%{background:#f0f;}50%{background:#0ff;}100%{background:#0f0;}}</style>', unsafe_allow_html=True)
        st.stop()
