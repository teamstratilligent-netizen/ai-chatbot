import streamlit as st 
import requests
import pandas as pd
import json

# -------------------------------
# CONFIG
# -------------------------------
API_BASE_URL = "https://rag-fastapi-container.bravedune-842387a0.centralindia.azurecontainerapps.io"

st.set_page_config(
    page_title="Jharkhand Tourism Assistant",
    page_icon="🌄",
    layout="wide"
)

# -------------------------------
# FIXED CSS
# -------------------------------
st.markdown("""
<style>
html, body, .stApp, .block-container, .appview-container, .main {
    background-color: #212121 !important;
}
header { background-color: #212121 !important; }

.chat-message { display: flex; margin: 14px 0; }
.user-bubble {
    margin-left: auto;
    background: #303030;
    color: white;
    padding: 14px 18px;
    border-radius: 16px 16px 4px 16px;
    max-width: 75%;
}
.bot-bubble {
    margin-right: auto;
    background: #303030;
    color: white;
    padding: 14px 18px;
    border-radius: 16px 16px 16px 4px;
    max-width: 75%;
}

/* Header styles */
.header-title {
    font-size: 36px;
    font-weight: 700;
    color: white;
    margin-bottom: -8px;
}

.sub-title {
    color: #bdbdbd;
    font-size: 18px;
    margin-bottom: 25px;
}

            /* --- FIX: Make header visible on mobile --- */
@media (max-width: 768px) {

    /* Remove Streamlit's default top padding */
    .block-container {
        padding-top: 40px !important;
    }

    /* Force header to be visible */
    .header-title, .sub-title {
        position: relative !important;
        z-index: 9999 !important;
        padding-top: 20px !important;
        display: block !important;
        visibility: visible !important;
    }

    /* Remove clipping caused by Streamlit mobile bar */
    header[data-testid="stHeader"] {
        position: relative !important;
        top: 0 !important;
        z-index: 10000 !important;
        height: auto !important;
        padding-top: 10px !important;
    }
}
            
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER  ✅ (Added exactly as requested)
# -------------------------------
st.markdown("<div class='header-title'>🌄 Welcome to Jharkhand Tourism</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Your personal guide to the land of forests, waterfalls, heritage & adventure.</div>", unsafe_allow_html=True)
st.divider()


# -------------------------------
# SESSION STATE
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "ask_name"  # ask_name → ask_phone → chat

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_phone" not in st.session_state:
    st.session_state.user_phone = None


# -------------------------------
# RENDER CHAT
# -------------------------------
def render_chat(role, content):
    bubble = "user-bubble" if role == "user" else "bot-bubble"
    st.markdown(
        f"""
        <div class="chat-message">
            <div class="{bubble}">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------
for msg in st.session_state.messages:
    render_chat(msg["role"], msg["content"])


# -------------------------------
# ONBOARDING BOT MESSAGES
# -------------------------------
if st.session_state.step == "ask_name" and len(st.session_state.messages) == 0:
    bot_msg = "Hi! 👋 Welcome to the Tourism Guide Assist. May I know your name?"
    st.session_state.messages.append({"role": "assistant", "content": bot_msg})
    render_chat("assistant", bot_msg)


# -------------------------------
# USER INPUT
# -------------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_chat("user", user_input)

    # -------------------------------
    # STEP 1 — USER PROVIDES NAME
    # -------------------------------
    if st.session_state.step == "ask_name":
        st.session_state.user_name = user_input.strip()

        bot_msg = (
            f"Nice to meet you, {st.session_state.user_name}! 😊 "
            f"Please share your phone number so I can assist you further."
        )
        st.session_state.messages.append({"role": "assistant", "content": bot_msg})
        render_chat("assistant", bot_msg)

        st.session_state.step = "ask_phone"
        st.stop()

    # -------------------------------
    # STEP 2 — USER PROVIDES PHONE
    # -------------------------------
    if st.session_state.step == "ask_phone":
        st.session_state.user_phone = user_input.strip()

        bot_msg = (
            "Thank you! You're all set. 🙌\n\n"
            "You can now ask me anything!"
        )
        st.session_state.messages.append({"role": "assistant", "content": bot_msg})
        render_chat("assistant", bot_msg)

        st.session_state.step = "chat"
        st.stop()

    # -------------------------------
    # STEP 3 — NORMAL CHAT MODE
    # -------------------------------
    if st.session_state.step == "chat":
        with st.spinner("Exploring Jharkhand for you..."):
            try:
                payload = {
                    "user_query": user_input,
                    "user_id": st.session_state.user_name,
                    "phone": st.session_state.user_phone,
                    "session_id": "tourism-session-01",
                }

                resp = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)

                if resp.status_code == 200:
                    data = resp.json()
                    reply = data.get("response", "No response.")

                    if data.get("execution_time_ms"):
                        reply += f"\n\n⏱️ {data['execution_time_ms']:.2f} ms"

                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )
                    render_chat("assistant", reply)

                    if data.get("dataframe"):
                        df = pd.DataFrame(json.loads(data["dataframe"]))
                        st.write("### 📊 Additional Info")
                        st.dataframe(df, use_container_width=True)

                else:
                    error = f"❌ Server Error {resp.status_code}"
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error}
                    )
                    render_chat("assistant", error)

            except Exception as e:
                error = f"⚠️ Unable to reach server: {str(e)}"
                st.session_state.messages.append(
                    {"role": "assistant", "content": error}
                )
                render_chat("assistant", error)
