import streamlit as st
import os
import requests
from datetime import datetime
from db import users_collection, plans_collection
from pymongo.errors import DuplicateKeyError
import bcrypt

st.set_page_config(page_title="📚 Smart Course Builder", layout="centered")
st.title("📚 Smart Course Builder")

# --- LOGIN LOGIC ---
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None

if st.session_state.authentication_status != True:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode(), user["password"]):
            st.session_state.authentication_status = True
            st.session_state.username = username
            st.session_state.name = user["name"]
            st.success(f"Welcome {user['name']} 👋")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.subheader("📝 Sign Up")
    new_user = st.text_input("New Username")
    new_name = st.text_input("Your Name")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        if users_collection.find_one({"username": new_user}):
            st.error("Username already exists")
        else:
            hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
            users_collection.insert_one({
                "username": new_user,
                "name": new_name,
                "password": hashed
            })
            st.success("Account created! Please log in.")
else:
    # --- LOGGED IN ---
    st.sidebar.write(f"👤 Logged in as: {st.session_state['name']}")
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.subheader("🛠️ Build Your Custom Course Plan")
    topic = st.text_input("Topic (e.g. Data Structures, ReactJS)")
    goal = st.text_input("Goal (e.g. Crack coding interviews)")
    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    duration = st.slider("Duration (in weeks)", 1, 12)

    if st.button("🚀 Generate Plan"):
        if not all([topic, goal, difficulty, duration]):
            st.warning("Please fill out all fields.")
        else:
            with st.spinner("Talking to DeepSeek 🤖..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {os.getenv('OPEN_ROUTER_API')}",
                        "HTTP-Referer": "https://your-app-name.streamlit.app",  # Replace if deployed
                        "X-Title": "Smart Course Builder"
                    }

                    prompt = (
                        f"Create a {difficulty} level, {duration}-week course plan on '{topic}' "
                        f"to help the user achieve this goal: {goal}. \n\n"
                        "Format the plan as:\n"
                        "- Week-wise breakdown (Week 1, Week 2, ...)\n"
                        "- Topics per week\n"
                        "- At least one free resource (like YouTube or Docs) per week.\n"
                        "Only output the course. Do NOT ask follow-up questions or request input."
                    )

                    payload = {
                        "model": "deepseek/deepseek-chat-v3-0324:free",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }


                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()

                    # Debugging info (optional):
                    # st.write(data)

                    if "choices" in data and data["choices"]:
                        plan = data["choices"][0]["message"]["content"]
                        st.markdown(plan)

                        plans_collection.insert_one({
                            "username": st.session_state["username"],
                            "plan": plan,
                            "topic": topic,
                            "goal": goal,
                            "difficulty": difficulty,
                            "duration": duration,
                            "timestamp": datetime.now()
                        })
                    else:
                        st.error("❌ The AI did not return any plan. Try again.")

                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # --- SAVED PLANS ---
    st.subheader("📜 Your Saved Plans")
    saved = plans_collection.find({"username": st.session_state["username"]}).sort("timestamp", -1)
    for doc in saved:
        with st.expander(f"{doc['topic']} – {doc['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            st.markdown(doc["plan"], unsafe_allow_html=True)
