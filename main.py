import streamlit as st
import requests
import os
import streamlit_authenticator as stauth

# Example list of users (in real apps, load from MongoD
# ✅ Corrected: Hash both passwords first
hasher = stauth.Hasher()
hashed_passwords = hasher.generate(['test123'])

# ✅ Then set up your user credentials
credentials = {
    "usernames": {
        "roopa": {
            "name": "Roopashree",
            "password": hashed_passwords[0]
        }
    }
}


# ✅ Create authenticator
authenticator = stauth.Authenticate(credentials,
                                    "smart_course_builder_app",
                                    "auth_token",
                                    cookie_expiry_days=1)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as {name}")

    # Your main app code goes here ↓↓↓
    st.set_page_config(page_title="📚 Smart Study Planner", layout="centered")
    st.title("📚 Smart Study Planner")

    api_key = os.environ.get("OPEN_ROUTER_API")
    if not api_key:
        st.error("❌ API key missing.")
        st.stop()

    # New Inputs for Course Planner
    topic = st.text_input("📚 Learning Topic", placeholder="e.g., Web Development")
    duration = st.selectbox("📅 Duration (in days)", [7, 15, 30, 60])
    goal = st.text_input("🎯 Final Goal", placeholder="e.g., Get internship-ready")
    difficulty = st.selectbox("⚙️ Difficulty Level",
                              ["Beginner", "Intermediate", "Advanced"])

    generate = st.button("Generate Course Plan")


    def generate_course_plan(topic, goal, difficulty, duration):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://smartstudyplanner.replit.app",  # Optional
            "X-Title": "SmartCourseBuilder"
        }

        prompt = (
            f"You are an AI-powered course builder. Create a structured course on '{topic}' for a {difficulty} level learner."
            f"\nThe goal is: {goal} and the learner has {duration} days."
            f"\nBreak the course into 5–7 modules. For each module:"
            f"\n- Give a clear title"
            f"\n- Write a short description"
            f"\n- Provide 2–3 FREE learning resources with titles, links, and short notes."
            f"\nUse markdown format for links: [Resource Title](https://example.com)"
            f"\nInclude only free resources (like YouTube, FreeCodeCamp, GitHub, MDN, W3Schools, etc.)"
            f"\nAvoid paid or login-required links. Keep it beginner-friendly and self-paced."
        )

        payload = {
            "model":
            "deepseek/deepseek-chat-v3-0324:free",  # You can use any good free-tier model here
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                st.error(
                    f"❌ Failed to generate course. Error: {response.status_code} — {response.text}"
                )
                return None
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
            return None


    if generate:
        if not topic or not goal:
            st.warning("⚠️ Please fill in all fields.")
        else:
            with st.spinner("🧠 Generating your personalized course plan..."):
                result = generate_course_plan(topic, goal, difficulty, duration)
                if result:
                    st.success("✅ Course Plan Ready!")

                    # Try to split modules based on numbering (e.g., '1.', '2.', etc.)
                    import re
                    modules = re.split(r'\n\d+\.\s+', result)

                    # Skip any leading text before the first module
                    for module in modules[1:]:
                        lines = module.strip().split('\n', 1)
                        title = lines[0].strip()
                        content = lines[1] if len(lines) > 1 else ""

                        with st.expander(f"📘 {title}"):
                            st.markdown(content, unsafe_allow_html=True)

