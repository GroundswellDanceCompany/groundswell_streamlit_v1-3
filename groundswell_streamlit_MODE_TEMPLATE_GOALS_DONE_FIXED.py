
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- Mode Selection ---
mode = st.sidebar.radio("Select Mode", ["Student", "Teacher"], key="mode_selector")

# --- Init Session State ---
if "goals" not in st.session_state:
    st.session_state.goals = []
if "templates" not in st.session_state:
    st.session_state.templates = []
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

# --- Detect mode change and reset form states only ---
if mode != st.session_state.last_mode:
    st.session_state.last_mode = mode
    for k in list(st.session_state.keys()):
        if k.startswith("student_") or k.startswith("teacher_"):
            del st.session_state[k]
    st.rerun()

# --- Student Mode ---
if mode == "Student":
    st.title("Groundswell Goal Tracker")
    st.markdown("_Where discipline meets artistry._")

    with st.form("add_goal_form"):
        st.subheader("Add a New Goal")
        text = st.text_input("Goal Description", key="student_text")
        category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"], key="student_category")
        target_date = st.date_input("Target Date", value=datetime.date.today(), key="student_date")
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

    if st.session_state.templates:
        st.subheader("Import Template Goal")
        template_options = [f"{t['text']} ({t['category']})" for t in st.session_state.templates]
        selected = st.selectbox("Choose a Template", template_options, key="student_template_picker")
        if st.button("Add Template as Goal", key="student_add_template"):
            index = template_options.index(selected)
            t = st.session_state.templates[index]
            date = datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date() if 'target_date' in t else datetime.date.today()
            st.session_state.goals.append({
                "text": f"[TEMPLATE] {t['text']}",
                "category": t['category'],
                "target_date": date,
                "status": "Not Started",
                "note": "",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template added as goal!")

    st.subheader("Your Goals")
    if st.session_state.goals:
        for i, goal in enumerate(st.session_state.goals):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                status_icon = "✅" if goal["status"] == "Done" else "☐"
                st.markdown(f"{status_icon} **{goal['text']}** ({goal['category']}) - Due: {goal['target_date'].strftime('%b %d, %Y')}")
            with col2:
                if st.button("Done" if goal['status'] != "Done" else "Undo", key=f"toggle_done_{i}"):
                    goal['status'] = "Done" if goal['status'] != "Done" else "Not Started"
                    goal['completed_on'] = datetime.date.today() if goal['status'] == "Done" else None
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_goal_{i}"):
                    st.session_state.goals.pop(i)
                    st.rerun()
    else:
        st.info("No goals added yet.")

# --- Teacher Mode ---
if mode == "Teacher":
    st.title("Teacher Template Builder")
    st.markdown("Create reusable goal templates for your students.")

    with st.form("add_template_form"):
        template_text = st.text_input("Template Goal Text", key="teacher_text")
        template_category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"], key="teacher_category")
        template_date = st.date_input("Suggested Target Date", value=datetime.date.today(), key="teacher_date")
        add_template = st.form_submit_button("Add Template")
        if add_template and template_text:
            st.session_state.templates.append({
                "text": template_text,
                "category": template_category,
                "target_date": template_date.strftime("%Y-%m-%d")
            })
            st.success("Template added!")

    st.subheader("Current Templates")
    if st.session_state.templates:
        for i, temp in enumerate(st.session_state.templates):
            col1, col2 = st.columns([4, 1])
            with col1:
                date_text = f" - Target: {temp['target_date']}" if 'target_date' in temp else ""
                st.markdown(f"- **{temp['text']}** ({temp['category']}){date_text}")
            with col2:
                if st.button("Delete", key=f"delete_template_{i}"):
                    st.session_state.templates.pop(i)
                    st.rerun()
    else:
        st.info("No templates added yet.")
