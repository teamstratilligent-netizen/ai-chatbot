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
# PROFESSIONAL UI CSS (UPDATED COLORS)
# -------------------------------
st.markdown("""
<style>

/* Background color */
body {
    background-color: #212121 !important;    /* DARK background */
    font-family: "Inter", sans-serif;
}

.block-container {
    padding-top: 3rem !important;
}

/* Chat wrapper */
.chat-message {
    display: flex;
    margin: 14px 0;
}

/* USER bubble */
.user-bubble {
    margin-left: auto;
    background: #303030;         /* BUBBLE COLOR */
    color: white;                /* TEXT COLOR */
    padding: 14px 18px;
    border-radius: 16px 16px 4px 16px;
    max-width: 75%;
    font-size: 16px;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.35);
}

/* ASSISTANT bubble */
.bot-bubble {
    margin-right: auto;
    background: #303030;          /* BUBBLE COLOR */
    color: white;                 /* TEXT COLOR */
    padding: 14px 18px;
    border-radius: 16px 16px 16px 4px;
    max-width: 75%;
    font-size: 16px;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.35);
}

/* Header */
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

/* ------------------------------
   MOBILE FIX: CHAT INPUT TEXT VISIBLE
------------------------------ */
@media (max-width: 768px) {
    .stChatInput textarea {
        color: black !important;                   /* Visible text */
        background-color: white !important;        /* White input box */
    }

    .stChatInput textarea::placeholder {
        color: #555 !important;                    /* Visible placeholder */
    }
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# HEADER TEXT
# -------------------------------
st.markdown("<div class='header-title'>🌄 Welcome to Jharkhand Tourism</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Your personal guide to the land of forests, waterfalls, heritage & adventure.</div>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# RENDER CHAT
# -------------------------------
def render_chat(role, content):
    if role == "user":
        bubble_class = "user-bubble"
    else:
        bubble_class = "bot-bubble"

    st.markdown(
        f"""
        <div class="chat-message">
            <div class="{bubble_class}">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# DISPLAY HISTORY
# -------------------------------
for msg in st.session_state.messages:
    render_chat(msg["role"], msg["content"])

# -------------------------------
# USER INPUT
# -------------------------------
prompt = st.chat_input("Ask about places, culture, or travel in Jharkhand...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_chat("user", prompt)

    # -------------------------------
    # CALL BACKEND API
    # -------------------------------
    with st.spinner("Exploring Jharkhand for you..."):
        try:
            payload = {
                "user_query": prompt,
                "user_id": "visitor",
                "session_id": "tourism-session-01"
            }

            resp = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)

            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("response", "No response.")

                if data.get("execution_time_ms"):
                    reply += f"\n\n⏱️ {data['execution_time_ms']:.2f} ms"

                st.session_state.messages.append({"role": "assistant", "content": reply})
                render_chat("assistant", reply)

                if data.get("dataframe"):
                    df = pd.DataFrame(json.loads(data["dataframe"]))
                    st.write("### 📊 Additional Info")
                    st.dataframe(df, use_container_width=True)

            else:
                error = f"❌ Server Error {resp.status_code}"
                st.session_state.messages.append({"role": "assistant", "content": error})
                render_chat("assistant", error)

        except Exception as e:
            error = f"⚠️ Unable to reach server: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error})
            render_chat("assistant", error)
