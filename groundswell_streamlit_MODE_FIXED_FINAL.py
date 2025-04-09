
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- Mode Selection ---
mode = st.sidebar.selectbox("Select Mode", ["Student", "Teacher"], key="mode_selector")

# --- Init Session State ---
if "goals" not in st.session_state:
    st.session_state.goals = []
if "templates" not in st.session_state:
    st.session_state.templates = []
if "mode_flag" not in st.session_state:
    st.session_state.mode_flag = mode

# --- Reset form fields when switching modes ---
if mode != st.session_state.mode_flag:
    for key in list(st.session_state.keys()):
        if key not in ("goals", "templates", "mode_flag"):
            del st.session_state[key]
    st.session_state.mode_flag = mode
    st.rerun()

# --- Student Mode ---
if mode == "Student":
    st.title("Groundswell Goal Tracker")
    st.markdown("_Where discipline meets artistry._")
    st.write("Set, track, and celebrate your goals—one step at a time.")

    # Add new goal
    with st.form("add_goal_form"):
        st.subheader("Add a New Goal")
        text = st.text_input("Goal Description", key="goal_text")
        category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"], key="goal_category")
        target_date = st.date_input("Target Date", value=datetime.date.today(), key="goal_date")
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

    # Import template goals
    if st.session_state.templates:
        st.subheader("Import Template Goal")
        template_options = [f"{t['text']} ({t['category']})" for t in st.session_state.templates]
        selected = st.selectbox("Choose a Template", template_options, key="student_template_picker")
        if st.button("Add Template as Goal", key="add_template_btn"):
            index = template_options.index(selected)
            t = st.session_state.templates[index]
            st.session_state.goals.append({
                "text": f"[TEMPLATE] {t['text']}",
                "category": t['category'],
                "target_date": datetime.date.today(),
                "status": "Not Started",
                "note": "",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template added as goal!")

    # Show goals with delete option
    st.subheader("Your Goals")
    if st.session_state.goals:
        for i, goal in enumerate(st.session_state.goals):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"- **{goal['text']}** ({goal['category']}) - Due: {goal['target_date'].strftime('%b %d, %Y')}")
            with col2:
                if st.button("Delete", key=f"delete_goal_{i}"):
                    st.session_state.goals.pop(i)
                    st.rerun()
    else:
        st.info("No goals added yet. Use the form above to get started.")

# --- Teacher Mode ---
if mode == "Teacher":
    st.title("Teacher Template Builder")
    st.markdown("Create reusable goal templates for your students.")

    with st.form("add_template_form"):
        template_text = st.text_input("Template Goal Text", key="template_text")
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
                if st.button("Delete", key=f"delete_template_{i}"):
                    st.session_state.templates.pop(i)
                    st.rerun()
    else:
        st.info("No templates added yet.")
