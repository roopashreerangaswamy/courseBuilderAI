import streamlit as st
import requests
import os
import re

# ✅ Streamlit setup
st.set_page_config(page_title="📚 Smart Study Planner", layout="centered")
st.title("📚 Smart Study Planner")

# ✅ API key from environment
api_key = os.environ.get("OPEN_ROUTER_API")
if not api_key:
    st.error("❌ API key missing. Set the OPEN_ROUTER_API environment variable.")
    st.stop()

# ✅ User inputs
topic = st.text_input("📚 Learning Topic", placeholder="e.g., Web Development")
duration = st.selectbox("📅 Duration (in days)", [7, 15, 30, 60])
goal = st.text_input("🎯 Final Goal", placeholder="e.g., Get internship-ready")
difficulty = st.selectbox("⚙️ Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

generate = st.button("Generate Course Plan")

# ✅ AI call to generate course
def generate_course_plan(topic, goal, difficulty, duration):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smartstudyplanner.replit.app",
        "X-Title": "SmartCourseBuilder"
    }

    prompt = (
        f"You are an AI-powered course builder. Create a structured course on '{topic}' for a {difficulty} level learner.\n"
        f"The goal is: {goal} and the learner has {duration} days.\n"
        f"Break the course into 5–7 modules. For each module:\n"
        f"- Give a clear title\n"
        f"- Write a short description\n"
        f"- Provide 2–3 FREE learning resources with titles, links, and short notes.\n"
        f"Use markdown format for links: [Resource Title](https://example.com)\n"
        f"Include only free resources (YouTube, FreeCodeCamp, GitHub, MDN, etc.). Avoid paid/login-required ones.\n"
        f"Keep it self-paced and beginner-friendly."
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
            st.error(f"❌ Error: {response.status_code} — {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Exception: {e}")
        return None

# ✅ Display result
if generate:
    if not topic or not goal:
        st.warning("⚠️ Please fill in all fields.")
    else:
        with st.spinner("🧠 Generating your personalized course plan..."):
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
