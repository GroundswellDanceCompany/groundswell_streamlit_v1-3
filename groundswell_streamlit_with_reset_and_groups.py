
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- In-memory user database ---
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = {
        "teacher": {"password": "adminpass", "role": "admin"},
        "alice": {"password": "dance123", "role": "student"},
        "ben": {"password": "moves456", "role": "student"},
        "cam": {"password": "groove789", "role": "student"},
    }

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_goals" not in st.session_state:
    st.session_state.user_goals = {}
if "templates" not in st.session_state:
    st.session_state.templates = []
if "mode" not in st.session_state:
    st.session_state.mode = "login"  # login, signup, reset

# --- Logout Function ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- Password Reset Page ---
if not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    username = st.text_input("Enter your username")
    new_password = st.text_input("Enter a new password", type="password")

    if st.button("Reset Password"):
        if username in st.session_state.USER_DB:
            if username.lower() == "teacher":
                st.error("Teacher password can only be reset by admin.")
            else:
                st.session_state.USER_DB[username]["password"] = new_password
                st.success("Password updated! You can now log in.")
                st.session_state.mode = "login"
                st.rerun()
        else:
            st.error("Username not found.")

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()

# --- Sign Up Page ---
if not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")

    if st.button("Create Account"):
        if not new_user or not new_pass:
            st.warning("Please fill in both fields.")
        elif new_user in st.session_state.USER_DB:
            st.error("Username already exists.")
        elif new_user.lower() == "teacher":
            st.error("This username is reserved.")
        else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student"
            }
            st.session_state.user_goals[new_user] = []
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()

# --- Login Page ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Goal Tracker")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = st.session_state.USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            if username not in st.session_state.user_goals:
                st.session_state.user_goals[username] = []
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("---")
    if st.button("Create Student Account"):
        st.session_state.mode = "signup"
        st.rerun()
    if st.button("Forgot Password?"):
        st.session_state.mode = "reset"
        st.rerun()

    st.info("Teachers: log in using your assigned credentials.")
    st.stop()

# --- Sidebar Info ---
username = st.session_state.username
role = st.session_state.USER_DB[username]["role"]
st.sidebar.markdown(f"**Logged in as:** `{username}` ({role})")
if st.sidebar.button("Logout"):
    logout()

# --- Student Mode ---
if role == "student":
    goals = st.session_state.user_goals[username]
    st.title(f"Welcome, {username.capitalize()}")
    st.markdown("_Track your goals, grow your skills._")

    with st.form("add_goal_form"):
        st.subheader("Add a New Goal")
        text = st.text_input("Goal Description", key="student_text")
        category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"], key="student_category")
        target_date = st.date_input("Target Date", value=datetime.date.today(), key="student_date")
        submitted = st.form_submit_button("Add Goal")
        if submitted and text:
            goals.append({
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
            goals.append({
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
    if goals:
        for i, goal in enumerate(goals):
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
                    goals.pop(i)
                    st.rerun()
    else:
        st.info("No goals yet. Use the form above to get started.")

# --- Teacher Mode ---
if role == "admin":
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
                st.markdown(f"- **{temp['text']}** ({temp['category']}) - Target: {temp['target_date']}")
            with col2:
                if st.button("Delete", key=f"delete_template_{i}"):
                    st.session_state.templates.pop(i)
                    st.rerun()
    else:
        st.info("No templates added yet.")




# --- Define available class groups ---
CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

# --- Extend USER_DB entries to include 'groups' ---
for user in st.session_state.USER_DB.values():
    if user["role"] == "student" and "groups" not in user:
        user["groups"] = []

# --- On signup (if applicable), students can select groups ---
if st.session_state.mode == "signup" and not st.session_state.logged_in:
    st.subheader("Select your group/classes")
    selected_groups = st.multiselect("Class Groups", CLASS_GROUPS)
    if st.session_state.get("new_user"):
        st.session_state.USER_DB[st.session_state.new_user]["groups"] = selected_groups
        st.success("Groups added.")
        st.session_state.mode = "login"
        st.rerun()

# --- Template filtering for students by group ---
if st.session_state.logged_in and st.session_state.USER_DB[st.session_state.username]["role"] == "student":
    student_groups = st.session_state.USER_DB[st.session_state.username].get("groups", [])
    group_templates = [t for t in st.session_state.templates if set(t.get("groups", [])) & set(student_groups)]
    if group_templates:
        st.subheader("Templates for Your Groups")
        for i, t in enumerate(group_templates):
            st.markdown(f"- **{t['text']}** ({t['category']}) — Target: {t['target_date']} — Groups: {', '.join(t['groups'])}")
            if st.button("Import", key=f"import_group_temp_{i}"):
                st.session_state.user_goals[st.session_state.username].append({
                    "text": f"[TEMPLATE] {t['text']}",
                    "category": t['category'],
                    "target_date": datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date(),
                    "status": "Not Started",
                    "note": "",
                    "created_on": datetime.date.today(),
                    "completed_on": None
                })
                st.success("Template imported!")

# --- Teacher ability to create templates for specific groups ---
if st.session_state.logged_in and st.session_state.USER_DB[st.session_state.username]["role"] == "admin":
    st.subheader("Assign Template to Groups")
    with st.form("group_template_form"):
        temp_text = st.text_input("Template Text")
        temp_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        temp_date = st.date_input("Target Date", value=datetime.date.today())
        temp_groups = st.multiselect("Assign to Groups", CLASS_GROUPS)
        submit = st.form_submit_button("Add Template")
        if submit and temp_text and temp_groups:
            st.session_state.templates.append({
                "text": temp_text,
                "category": temp_cat,
                "target_date": temp_date.strftime("%Y-%m-%d"),
                "groups": temp_groups
            })
            st.success("Group-based Template Added!")
