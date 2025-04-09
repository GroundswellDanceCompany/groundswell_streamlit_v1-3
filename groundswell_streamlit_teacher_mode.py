
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- Mode Selection ---
mode = st.sidebar.selectbox("Select Mode", ["Student", "Teacher"])

# --- Init Session State ---
if "goals" not in st.session_state:
    st.session_state.goals = []
if "templates" not in st.session_state:
    st.session_state.templates = []

# --- Student Mode ---
if mode == "Student":
    st.title("Groundswell Goal Tracker")
    st.markdown("_Where discipline meets artistry._")
    st.write("Set, track, and celebrate your goals—one step at a time.")

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

# --- Teacher Mode ---
if mode == "Teacher":
    st.title("Teacher Template Builder")
    st.markdown("Create reusable goal templates for your students.")

    with st.form("add_template_form"):
        template_text = st.text_input("Template Goal Text")
        template_category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"], key="template_category")
        add_template = st.form_submit_button("Add Template")
        if add_template and template_text:
            st.session_state.templates.append({
                "text": template_text,
                "category": template_category
            })
            st.success("Template added!")

    st.subheader("Current Templates")
    if st.session_state.templates:
        for i, temp in enumerate(st.session_state.templates):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"- **{temp['text']}** ({temp['category']})")
            with col2:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.templates.pop(i)
                    st.experimental_rerun()
    else:
        st.info("No templates added yet.")
