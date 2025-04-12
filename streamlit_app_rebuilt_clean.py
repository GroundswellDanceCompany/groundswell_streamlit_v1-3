
import streamlit as st
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
ARCHIVED_GOALS_FILE = "user_archived_goals.json"
VIDEO_DIR = "videos"

CLASS_GROUPS = [
    "Advanced - Advanced Waacking", "Advanced - Advanced Locking", "Advanced - Advanced House",
    "Advanced - Advanced Hip Hop", "Advanced - Advanced Jazz",
    "Intermediate - Intermediate Ballet", "Intermediate - Intermediate Contemporary",
    "Junior - Junior Waacking", "Junior - Junior Locking", "Junior - Junior House",
    "Junior - Junior Ballet", "Junior - Junior Contemporary", "Junior - Junior Jazz",
    "Company - Youth Jazz Company", "Company - Junior Jazz Company",
    "Company - Youth Contemporary Company", "Company - Junior Contemporary Company",
    "Open/Other - Commercial", "Open/Other - Open House Class", "Open/Other - Tap Class",
    "Open/Other - GSD Youth", "Open/Other - GFoundation", "Open/Other - Jenga"
]

def save_json(file, data): 
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_json(file, default): 
    return json.load(open(file)) if os.path.exists(file) else default

def initialize_session_state():
    if "USER_DB" not in st.session_state:
        st.session_state.USER_DB = load_json(USER_DB_FILE, {})
    if "user_goals" not in st.session_state:
        st.session_state.user_goals = load_json(GOALS_FILE, {})
    if "user_archived_goals" not in st.session_state:
        st.session_state.user_archived_goals = load_json(ARCHIVED_GOALS_FILE, {})
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_role" not in st.session_state:
        st.session_state.current_role = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "mode" not in st.session_state:
        st.session_state.mode = "login"

def get_current_user_and_role():
    return st.session_state.get("current_user"), st.session_state.get("current_role")

def show_login_signup():
    if st.session_state.mode == "login":
        st.title("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            db = st.session_state.USER_DB
            if u in db and db[u]["password"] == p:
                st.session_state.current_user = u
                st.session_state.current_role = db[u]["role"]
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        if st.button("Create Account Instead"):
            st.session_state.mode = "signup"
            st.experimental_rerun()
    elif not st.session_state.logged_in and st.session_state.mode == "signup":
        st.title("Sign Up")
        u = st.text_input("New Username")
        p = st.text_input("Password", type="password")
        g = st.multiselect("Your Classes", CLASS_GROUPS, key="signup_classes")
        st.write("CLASS_GROUPS available:", CLASS_GROUPS)
        if st.button("Create Account"):
            if u in st.session_state.USER_DB:
                st.error("Username taken.")
            else:
                st.session_state.USER_DB[u] = {
                    "password": p,
                    "role": "student",
                    "groups": g
                }
                save_json(USER_DB_FILE, st.session_state.USER_DB)
                st.success("Account created.")
                st.session_state.mode = "login"
                st.experimental_rerun()

def show_student_dashboard(user):
    st.title(f"Welcome, {user}!")
    goals = st.session_state.user_goals.get(user, [])
    archived = st.session_state.user_archived_goals.get(user, [])

    new_goal = st.text_input("Set a new goal")
    if st.button("Add Goal"):
        if new_goal:
            goals.append(new_goal)
            st.session_state.user_goals[user] = goals
            save_json(GOALS_FILE, st.session_state.user_goals)
            st.experimental_rerun()

    if goals:
        st.subheader("Active Goals")
        for i, goal in enumerate(goals):
            col1, col2, col3 = st.columns([6, 1, 1])
            col1.write(goal)
            if col2.button("✓", key=f"archive_{i}"):
                archived.append(goal)
                goals.pop(i)
                st.session_state.user_goals[user] = goals
                st.session_state.user_archived_goals[user] = archived
                save_json(GOALS_FILE, st.session_state.user_goals)
                save_json(ARCHIVED_GOALS_FILE, st.session_state.user_archived_goals)
                st.experimental_rerun()
            if col3.button("✕", key=f"delete_{i}"):
                goals.pop(i)
                st.session_state.user_goals[user] = goals
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.experimental_rerun()

    with st.expander("Archived Goals"):
        if archived:
            for goal in archived:
                st.markdown(f"- {goal}")
        else:
            st.caption("No archived goals yet.")

def main():
    initialize_session_state()
    user, role = get_current_user_and_role()
    if not st.session_state.logged_in:
        show_login_signup()
        return

    if role == "student":
        show_student_dashboard(user)
    else:
        st.error("You do not have access to this view.")

if __name__ == "__main__":
    main()
