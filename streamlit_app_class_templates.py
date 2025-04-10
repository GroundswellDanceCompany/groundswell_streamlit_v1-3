
# streamlit_app.py

import streamlit as st
import uuid
import datetime
import json
import os

# --- Page Config ---
st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- File Paths for Persistent Storage ---
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"

# --- Helper Functions ---
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# --- Load or Initialize Data ---
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_json(USER_DB_FILE, {
        "teacher": {"password": "adminpass", "role": "admin", "groups": []}
    })
if "user_goals" not in st.session_state:
    st.session_state.user_goals = load_json(GOALS_FILE, {})
if "templates" not in st.session_state:
    st.session_state.templates = load_json(TEMPLATES_FILE, [])
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"

# --- Full Class Group List ---
CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

# --- Utility ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.mode = "login"
    st.rerun()

# --- Login Page ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Goal Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_db = st.session_state.USER_DB
        if username in user_db and user_db[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

    if st.button("Sign Up"):
        st.session_state.mode = "signup"
        st.rerun()

    if st.button("Reset Password"):
        st.session_state.mode = "reset"
        st.rerun()

# --- Sign Up Page ---
elif not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    groups = st.multiselect("Select your class/groups", CLASS_GROUPS)

    if st.button("Create Account"):
        user_db = st.session_state.USER_DB
        if new_user in user_db:
            st.error("Username already exists.")
        else:
            user_db[new_user] = {"password": new_pass, "role": "student", "groups": groups}
            save_json(USER_DB_FILE, user_db)
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()

# --- Reset Password Page ---
elif not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    username = st.text_input("Enter your username")
    new_password = st.text_input("Enter a new password", type="password")

    if st.button("Reset Password"):
        user_db = st.session_state.USER_DB
        if username in user_db and username != "teacher":
            user_db[username]["password"] = new_password
            save_json(USER_DB_FILE, user_db)
            st.success("Password updated. You can now log in.")
            st.session_state.mode = "login"
            st.rerun()
        elif username == "teacher":
            st.error("Teacher password can only be reset by an admin.")
        else:
            st.error("Username not found.")

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()

# --- Main App (Student or Teacher View) ---
elif st.session_state.logged_in:
    username = st.session_state.username
    user_info = st.session_state.USER_DB[username]
    is_teacher = user_info["role"] == "admin"

    st.sidebar.title(f"Hello, {username}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("Groundswell Goal Tracker")

    # --- Teacher View ---
    if is_teacher:
        st.header("Template Manager")
        with st.form("add_template"):
            temp_text = st.text_input("Template Goal")
            temp_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            assigned_groups = st.multiselect("Assign to classes/groups", CLASS_GROUPS)
            submitted = st.form_submit_button("Add Template")
            if submitted and temp_text:
                st.session_state.templates.append({
                    "id": str(uuid.uuid4()), "text": temp_text, "category": temp_cat,
                    "groups": assigned_groups
                })
                save_json(TEMPLATES_FILE, st.session_state.templates)
                st.success("Template added.")

        st.subheader("Current Templates")
        for t in st.session_state.templates:
            st.markdown(f"- **{t['text']}** ({t['category']}) → _{', '.join(t.get('groups', []))}_")

    # --- Student View ---
    else:
        st.header("Your Goals")
        user_goals = st.session_state.user_goals.get(username, [])

        # Show group membership
        st.markdown("**Your Groups:** " + ", ".join(user_info.get("groups", [])))

        with st.form("add_goal"):
            goal_text = st.text_input("New Goal")
            goal_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            goal_date = st.date_input("Target Date", datetime.date.today(), help="Pick your goal deadline.")
            add = st.form_submit_button("Add Goal")
            if add and goal_text:
                user_goals.append({
                    "id": str(uuid.uuid4()), "text": goal_text, "category": goal_cat,
                    "target_date": str(goal_date), "done": False
                })
                st.session_state.user_goals[username] = user_goals
                save_json(GOALS_FILE, st.session_state.user_goals)

        st.subheader("Class-Assigned Templates")

        student_groups = user_info.get("groups", [])
        available_templates = [
            t for t in st.session_state.templates
            if any(g in student_groups for g in t.get("groups", []))
        ]

        for t in available_templates:
            with st.expander(f"{t['text']} ({t['category']}) — from {', '.join(t.get('groups', []))}"):
                goal_date = st.date_input(f"Pick date for: {t['text']}", datetime.date.today(), key=f"date_{t['id']}")
                if st.button(f"Add to My Goals", key=f"add_{t['id']}"):
                    user_goals.append({
                        "id": str(uuid.uuid4()), "text": t['text'], "category": t['category'],
                        "target_date": str(goal_date), "done": False
                    })
                    st.session_state.user_goals[username] = user_goals
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.success(f"Added: {t['text']}")

        st.subheader("Your Active Goals")
        for g in user_goals:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
            with col2:
                if st.checkbox("Done", value=g["done"], key=g["id"]):
                    g["done"] = True
                    save_json(GOALS_FILE, st.session_state.user_goals)
