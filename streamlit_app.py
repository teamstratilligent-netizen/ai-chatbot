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
# PROFESSIONAL UI CSS (Dark Mode)
# -------------------------------
st.markdown("""
<style>

/* FULL PAGE DARK BACKGROUND (Desktop + Mobile) */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background-color: #212121 !important;
    color: white !important;
}

/* Ensure header text is white */
.header-title, .sub-title {
    color: white !important;
}

/* Chat wrapper */
.chat-message {
    display: flex;
    margin: 12px 0;
}

/* USER bubble */
.user-bubble {
    margin-left: auto;
    background: #303030 !important;
    color: white !important;
    padding: 12px 16px;
    border-radius: 16px 16px 4px 16px;
    max-width: 75%;
    font-size: 16px;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.8);
}

/* ASSISTANT bubble */
.bot-bubble {
    margin-right: auto;
    background: #303030 !important;
    color: white !important;
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
    max-width: 75%;
    font-size: 16px;
    line-height: 1.55;
    border: 1px solid #3a3a3a;
    box-shadow: 0 1px 4px rgba(0,0,0,0.8);
}

/* Chat input text color fix */
input, textarea {
    color: white !important;
}

/* Streamlit chat input background fix */
[data-testid="stChatInput"] {
    background-color: #212121 !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<div class='header-title'>🌄 Welcome to Jharkhand Tourism</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Your personal guide to the land of forests, waterfalls, heritage & adventure.</div>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# RENDER CHAT BUBBLES
# -------------------------------
def render_chat(role, content):
    bubble_class = "user-bubble" if role == "user" else "bot-bubble"

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
# DISPLAY CHAT HISTORY
# -------------------------------
for msg in st.session_state.messages:
    render_chat(msg["role"], msg["content"])

# -------------------------------
# USER INPUT
# -------------------------------
prompt = st.chat_input("Ask about places, culture, food, or travel in Jharkhand...")

if prompt:
    # Save + display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_chat("user", prompt)

    # -------------------------------
    # CALL API
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
                reply = data.get("response", "No response received.")

                # Add execution time
                if data.get("execution_time_ms"):
                    reply += f"\n\n⏱️ {data['execution_time_ms']:.2f} ms"

                st.session_state.messages.append({"role": "assistant", "content": reply})
                render_chat("assistant", reply)

                # Render table if available
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
