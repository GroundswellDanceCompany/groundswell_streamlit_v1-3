
import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_json(USER_DB_FILE, {
        "teacher": {"password": "adminpass", "role": "admin", "groups": []}
    })
if "user_goals" not in st.session_state:
    st.session_state.user_goals = load_json(GOALS_FILE, {})
if "templates" not in st.session_state:
    st.session_state.templates = load_json(TEMPLATES_FILE, [])
if "user_streaks" not in st.session_state:
    st.session_state.user_streaks = load_json(STREAKS_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"

CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

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

# --- Signup Page ---
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

# --- Main App ---
elif st.session_state.logged_in:
    username = st.session_state.username
    user_info = st.session_state.USER_DB[username]
    is_teacher = user_info["role"] == "admin"

    st.sidebar.title(f"Hello, {username}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("Groundswell Goal Tracker")

    if is_teacher:
        st.header("Comment on Student Goals")
        for student, goals in st.session_state.user_goals.items():
            st.subheader(f"{student}'s Goals")
            for g in goals:
                st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
                comment_key = f"comment_{student}_{g['id']}"
                new_comment = st.text_input("Comment:", value=g.get("comment", ""), key=comment_key)
                if new_comment != g.get("comment", ""):
                    g["comment"] = new_comment
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.success("Comment saved.")

    else:
        st.header("Your Goals")
        goals = st.session_state.user_goals.get(username, [])
        streak_data = st.session_state.user_streaks.get(username, {"streak": 0, "last_completion_date": ""})
        st.markdown(f"**Current Streak:** {streak_data['streak']} day(s)")
        for g in goals:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
                if "comment" in g:
                    st.markdown(f"_Teacher Comment:_ {g['comment']}")
            with col2:
                if st.checkbox("Done", value=g["done"], key=g["id"]):
                    today = datetime.date.today().isoformat()
                    if not g["done"]:
                        g["done"] = True
                        g["completed_on"] = today
                        last_date = streak_data.get("last_completion_date")
                        if last_date == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
                            streak_data["streak"] += 1
                        elif last_date != today:
                            streak_data["streak"] = 1
                        streak_data["last_completion_date"] = today
                        st.session_state.user_streaks[username] = streak_data
                        save_json(GOALS_FILE, st.session_state.user_goals)
                        save_json(STREAKS_FILE, st.session_state.user_streaks)
