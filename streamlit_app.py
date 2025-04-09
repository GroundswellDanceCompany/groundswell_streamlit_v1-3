import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

st.title("Groundswell Goal Tracker")
st.markdown("_Where discipline meets artistry._")
st.write("Set, track, and celebrate your goals—one step at a time.")

if "goals" not in st.session_state:
    st.session_state.goals = []

with st.form("add_goal_form"):
    st.subheader("Add a New Goal")
    text = st.text_input("Goal Description")
    category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
    target_date = st.date_input("Target Date", value=datetime.date.today())
    submitted = st.form_submit_button("Add Goal")

    if submitted and text:
        st.session_state.goals.append({
            "text": text,
            "category": category,
            "target_date": target_date,
            "status": "Not Started",
            "note": "",
            "created_on": datetime.date.today(),
            "completed_on": None
        })
        st.success("Goal added!")

st.subheader("Your Goals")
if st.session_state.goals:
    for i, goal in enumerate(st.session_state.goals):
        st.markdown(f"- **{goal['text']}** ({goal['category']}) - Due: {goal['target_date'].strftime('%b %d, %Y')}")
else:
    st.info("No goals added yet. Use the form above to get started.")
