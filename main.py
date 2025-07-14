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
  # Create a basic study plan without AI for now
  subjects_list = [s.strip() for s in subjects.split(',')]
  priority_list = [p.strip() for p in priority.split(',')]
  
  # Simple algorithm to create study plan
  total_subjects = len(subjects_list)
  hours_per_subject = hours / total_subjects
  
  plan = f"""
# 📚 Your Personalized Study Plan ({hours} hours total)

## 📋 **Study Schedule Overview**
- **Total Study Time**: {hours} hours
- **Subjects**: {', '.join(subjects_list)}
- **Priority Subjects**: {', '.join(priority_list)}

## 📅 **Daily Schedule**

"""
  
  for i, subject in enumerate(subjects_list):
    allocated_hours = hours_per_subject
    if subject in priority_list:
      allocated_hours += 0.5  # Give priority subjects extra time
    
    plan += f"""
### {subject} - {allocated_hours:.1f} hours
- **Focus Areas**: Review key concepts, practice problems
- **Break Schedule**: 15-min break every hour
- **Priority**: {'🔥 HIGH' if subject in priority_list else '📖 STANDARD'}

"""
  
  plan += """
## 💡 **Study Tips**
- Start with priority subjects when you're most alert
- Take regular breaks to maintain focus
- Review previous day's material before starting new topics
- Practice active recall and spaced repetition

## ⏰ **Recommended Time Blocks**
- Morning (9-12 PM): High-priority subjects
- Afternoon (2-5 PM): Practice and review
- Evening (7-9 PM): Light review and planning

*Note: This is a basic plan. For AI-generated personalized plans, please add credits to your OpenRouter account.*
"""
  
  return plan


# Use this when user clicks the button
if generate:
  if not subjects or not priority:
    st.warning("Please fill all fields.")
  else:
    with st.spinner("Generating your smart study plan..."):
      result = generate_plan(subjects, priority, study_hours)
      st.success("✅ Study Plan Ready!")
      st.markdown(result)
