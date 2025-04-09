
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- Classes ---
CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

# --- In-memory DB ---
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = {
        "teacher": {"password": "adminpass", "role": "admin", "groups": []},
        "alice": {"password": "dance123", "role": "student", "groups": ["Junior Jazz", "Junior Hip Hop"]},
        "ben": {"password": "moves456", "role": "student", "groups": ["GFoundation"]},
        "cam": {"password": "groove789", "role": "student", "groups": ["Advanced Jazz"]},
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_goals" not in st.session_state:
    st.session_state.user_goals = {}
if "templates" not in st.session_state:
    st.session_state.templates = []
if "mode" not in st.session_state:
    st.session_state.mode = "login"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- Sign Up ---
if not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    groups = st.multiselect("Select your class/groups", CLASS_GROUPS)
    if st.button("Create Account"):
        if not new_user or not new_pass:
            st.warning("Please fill in all fields.")
        elif new_user in st.session_state.USER_DB:
            st.error("Username already exists.")
        elif new_user.lower() == "teacher":
            st.error("This username is reserved.")
        else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student",
                "groups": groups
            }
            st.session_state.user_goals[new_user] = []
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()
    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()

# --- Login ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Goal Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = st.session_state.USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            if username not in st.session_state.user_goals:
                st.session_state.user_goals[username] = []
            st.rerun()
        else:
            st.error("Invalid username or password")
    if st.button("Create Student Account"):
        st.session_state.mode = "signup"
        st.rerun()
    st.info("Teachers: log in using your assigned credentials.")
    st.stop()

# --- Sidebar Info ---
username = st.session_state.username
user_info = st.session_state.USER_DB[username]
role = user_info["role"]
st.sidebar.markdown(f"**Logged in as:** `{username}` ({role})")
if st.sidebar.button("Logout"):
    logout()

# --- Student Mode ---
if role == "student":
    goals = st.session_state.user_goals[username]
    st.title(f"Welcome, {username.capitalize()}")
    st.markdown("_Track your goals, grow your skills._")
    st.caption(f"Your groups: {', '.join(user_info.get('groups', []))}")
    with st.form("add_goal_form"):
        text = st.text_input("Goal Description")
        category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        date = st.date_input("Target Date", value=datetime.date.today())
        submitted = st.form_submit_button("Add Goal")
        if submitted and text:
            goals.append({
                "text": text,
                "category": category,
                "target_date": date,
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Goal added!")

    if st.session_state.templates:
        st.subheader("Import Template")
        selected = st.selectbox("Template", [f"{t['text']} ({t['category']})" for t in st.session_state.templates])
        if st.button("Add Template"):
            index = [f"{t['text']} ({t['category']})" for t in st.session_state.templates].index(selected)
            t = st.session_state.templates[index]
            goals.append({
                "text": f"[TEMPLATE] {t['text']}",
                "category": t['category'],
                "target_date": datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date(),
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template goal added!")

    st.subheader("Your Goals")
    for i, g in enumerate(goals):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"**{g['text']}** ({g['category']}) - Due: {g['target_date']:%b %d}")
        if col2.button("✅" if g["status"] == "Done" else "Mark Done", key=f"done_{i}"):
            g["status"] = "Done" if g["status"] != "Done" else "Not Started"
            g["completed_on"] = datetime.date.today() if g["status"] == "Done" else None
            st.rerun()
        if col3.button("Delete", key=f"delete_{i}"):
            goals.pop(i)
            st.rerun()

# --- Teacher Mode ---
if role == "admin":
    st.title("Teacher Dashboard")
    st.subheader("View Students by Class")
    group = st.selectbox("Select a Group", CLASS_GROUPS)
    students = [k for k, v in st.session_state.USER_DB.items()
                if v["role"] == "student" and group in v.get("groups", [])]
    for s in students:
        st.markdown(f"### {s.capitalize()}")
        for g in st.session_state.user_goals.get(s, []):
            st.markdown(f"- {'✅' if g['status'] == 'Done' else '⬜️'} **{g['text']}** ({g['category']}) - Due {g['target_date']:%b %d}")
    st.divider()
    st.subheader("Manage Templates")
    with st.form("add_template_form"):
        text = st.text_input("Template Text")
        cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        date = st.date_input("Target Date", value=datetime.date.today())
        submitted = st.form_submit_button("Add Template")
        if submitted and text:
            st.session_state.templates.append({
                "text": text,
                "category": cat,
                "target_date": date.strftime("%Y-%m-%d")
            })
            st.success("Template added!")

    for i, t in enumerate(st.session_state.templates):
        st.markdown(f"- **{t['text']}** ({t['category']}) - Target: {t['target_date']}")
        if st.button("Delete", key=f"t_delete_{i}"):
            st.session_state.templates.pop(i)
            st.rerun()
