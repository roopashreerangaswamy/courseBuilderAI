import streamlit as st
import requests
import os

my_secret = os.environ['OPEN_ROUTER_API']
if not my_secret:
  raise ValueError("OPEN_ROUTER_API key not found in environment variables!")

st.set_page_config(page_title="Smart Study Planner", layout="centered")

st.title("📚 Smart Study Planner")
st.write("Get a personalized study schedule using AI!")

# Input Fields
study_hours = st.number_input("📅 Total Study Time (in hours)",
                              min_value=1,
                              value=5)
subjects = st.text_area("📖 Subjects (comma-separated)",
                        placeholder="e.g., Math, Physics, Chemistry")
priority = st.text_area("🔥 Priority Subjects (comma-separated)",
                        placeholder="e.g., Physics")

generate = st.button("Generate Study Plan")


def generate_plan(subjects, priority, hours):
  prompt = f"""
  I'm a student preparing for exams. Create a daily study schedule for {hours} hours covering these subjects: {subjects}.
  Prioritize these: {priority}. Keep it efficient, realistic, and spaced out.
  Format output clearly as a day-wise plan.
  """

  headers = {
      "Authorization": f"Bearer {my_secret}",
      "Content-Type": "application/json"
  }

  payload = {
      "model": "openai/gpt-3.5-turbo",
      "messages": [{
          "role": "user",
          "content": prompt
      }]
  }

  response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                           headers=headers,
                           json=payload)

  if response.status_code == 200:
    return response.json()["choices"][0]["message"]["content"]
  else:
    return f"❌ Failed to generate plan. Error: {response.status_code}"


# Use this when user clicks the button
if generate:
  if not subjects or not priority:
    st.warning("Please fill all fields.")
  else:
    with st.spinner("Generating your smart study plan..."):
      result = generate_plan(subjects, priority, study_hours)
      st.success("✅ Study Plan Ready!")
      st.markdown(result)
