import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import requests
import re

# ---- PAGE CONFIG ----
st.set_page_config(page_title="📚 Smart Course Builder", layout="centered")

# ---- LOAD CONFIG ----
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# ---- AUTH SETUP ----
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
)

# ---- LOGIN PAGE ----
authenticator.login()

# ---- MAIN LOGIC ----
if st.session_state["authentication_status"] is True:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {st.session_state['name']} 👋")

    # Sidebar navigation
    page = st.sidebar.radio("Go to", ["🏠 Home", "📚 Course Builder"])

    if page == "🏠 Home":
        st.title("Welcome to Smart Study Planner 🎓")
        st.write("Use the sidebar to generate your personalized course plan.")

    elif page == "📚 Course Builder":
        st.title("📚 Course Builder")

        api_key = os.environ.get("OPEN_ROUTER_API")
        if not api_key:
            st.error("❌ API key missing. Set the OPEN_ROUTER_API environment variable.")
            st.stop()

        # Inputs
        topic = st.text_input("Learning Topic", placeholder="e.g., Web Development")
        duration = st.selectbox("Duration (in days)", [7, 15, 30, 60])
        goal = st.text_input("Final Goal", placeholder="e.g., Get internship-ready")
        difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

        generate = st.button("Generate Course Plan")

        # Function
        def generate_course_plan(topic, goal, difficulty, duration):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://smartstudyplanner.replit.app",
                "X-Title": "SmartCourseBuilder"
            }

            prompt = (
                f"You are an AI-powered course builder. Create a structured course on '{topic}' "
                f"for a {difficulty} level learner. Goal: {goal}. Duration: {duration} days.\n"
                f"Break it into 5–7 modules. Each module should have:\n"
                f"- A clear title\n- A short description\n"
                f"- 2–3 FREE learning resources with titles, links (markdown), and short notes.\n"
                f"Only free content from YouTube, FreeCodeCamp, GitHub, MDN, etc."
            )

            payload = {
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [{"role": "user", "content": prompt}]
            }

            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    return None
            except Exception as e:
                st.error(f"Exception: {e}")
                return None

        if generate:
            if not topic or not goal:
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Generating course plan..."):
                    result = generate_course_plan(topic, goal, difficulty, duration)
                    if result:
                        st.success("✅ Course Plan Ready!")
                        modules = re.split(r'\n\d+\.\s+', result)
                        for module in modules[1:]:
                            lines = module.strip().split('\n', 1)
                            title = lines[0].strip()
                            content = lines[1] if len(lines) > 1 else ""
                            with st.expander(f"📘 {title}"):
                                st.markdown(content, unsafe_allow_html=True)

elif st.session_state["authentication_status"] is False:
    st.error("Incorrect username or password.")

elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password.")
