import streamlit as st
import requests
import pandas as pd
import json

# -------------------------------
# CONFIG
# -------------------------------
API_BASE_URL = "https://rag-fastapi-container.bravedune-842387a0.centralindia.azurecontainerapps.io"

st.set_page_config(
    page_title="BeltronGPT",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# STYLES
# -------------------------------
st.markdown("""
<style>
body, .stApp { background-color: #212121; color: white; }

/* Login Card */
.login-card {
    background-color: #2c2c2c;
    padding: 30px 25px;
    border-radius: 12px;
    max-width: 350px;
    margin: auto;
    margin-top: 100px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    text-align: center;
}
.login-card img {
    width: 60px;
    margin-bottom: 15px;
}
.login-card h1 {
    margin: 0;
    font-size: 24px;
    margin-bottom: 5px;
}
.login-card p {
    margin: 0;
    font-size: 14px;
    color: #bdbdbd;
    margin-bottom: 20px;
}

/* Inputs */
input, .stTextInput>div>input, .stSelectbox>div>div>div>select {
    background-color: #3a3a3a !important;
    color: white !important;
    border-radius: 6px;
    padding: 6px;
}

/* Login Button */
.stButton>button {
    background-color: #4a90e2 !important;
    color: white;
    padding: 8px 0;
    border-radius: 6px;
    width: 100%;
    margin-top: 10px;
}

/* Chat bubbles */
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
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "department" not in st.session_state:
    st.session_state.department = None
if "messages" not in st.session_state:
    st.session_state.messages = []

if "temp_username" not in st.session_state:
    st.session_state.temp_username = ""
if "temp_dept" not in st.session_state:
    st.session_state.temp_dept = "Education"

# -------------------------------
# LOGIN FUNCTION
# -------------------------------
def do_login():
    st.session_state.logged_in = True
    st.session_state.user_name = st.session_state.temp_username
    st.session_state.department = st.session_state.temp_dept

# -------------------------------
# LOGIN UI
# -------------------------------
if not st.session_state.logged_in:

    st.markdown("""
        <div class="login-card">
            <img src="https://stratilligent.com/deck/Beltron.svg" />
            <h1>BeltronGPT</h1>
            <p>Private departmental AI workspace</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        st.session_state.temp_username = st.text_input("Username", value=st.session_state.temp_username)
        password = st.text_input("Password", type="password")
        departments = ["Education", "Health", "Transport", "Administration"]
        st.session_state.temp_dept = st.selectbox("Department", departments, index=departments.index(st.session_state.temp_dept))
        login_submit = st.form_submit_button("Login")

    if login_submit:
        if st.session_state.temp_username == "admin" and password == "admin":
            do_login()
        else:
            st.error("Invalid credentials. Use admin/admin")

    st.stop()

# -------------------------------
# HEADER
# -------------------------------
st.markdown(f"<h2 style='color:white'>Welcome to BeltronGPT, {st.session_state.user_name}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#bdbdbd'>Department: {st.session_state.department}</p>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# CHAT FUNCTIONS
# -------------------------------
def render_chat(role, content):
    bubble = "user-bubble" if role == "user" else "bot-bubble"
    st.markdown(f'<div class="chat-message"><div class="{bubble}">{content}</div></div>', unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    render_chat(msg["role"], msg["content"])

# -------------------------------
# CHAT INPUT
# -------------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_chat("user", user_input)

    with st.spinner("Fetching response..."):
        try:
            payload = {
                "user_query": user_input,
                "user_id": st.session_state.user_name,
                "department": st.session_state.department,
                "session_id": f"{st.session_state.user_name}-{st.session_state.department}",
            }

            resp = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)

            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("response", "No response.")
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
