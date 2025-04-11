
import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# ---- File Paths ----
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"
ARCHIVED_GOALS_FILE = "user_archived_goals.json"

# ---- Load/Save Helpers ----
def load_json(file, default): return json.load(open(file)) if os.path.exists(file) else default
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

# ---- Initialize All Session State ----
def initialize_session_state():
    defaults = {
        "USER_DB": load_json(USER_DB_FILE, {"teacher": {"password": "adminpass", "role": "admin", "groups": []}}),
        "user_goals": load_json(GOALS_FILE, {}),
        "templates": load_json(TEMPLATES_FILE, {}),
        "user_streaks": load_json(STREAKS_FILE, {}),
        "user_badges": load_json(BADGES_FILE, {}),
        "user_archived_goals": load_json(ARCHIVED_GOALS_FILE, {}),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_role" not in st.session_state:
        st.session_state.current_role = None

# ---- User Setup ----
# ---- User Setup ----
def get_current_user_and_role():
    user = st.session_state.get("current_user", None)
    role = st.session_state.get("current_role", None)
    return user, role

# ---- Placeholder Functions for Page Features ----
def show_student_dashboard(user):
    if user and role == "student":
        st.header("Your Goals")

        user_goals = st.session_state.user_goals.get(user, [])
        if "user_archived_goals" not in st.session_state:
            st.session_state.user_archived_goals = {}

        user_archived_goals = st.session_state.user_archived_goals.get(user, [])

        # Add new goal
        new_goal = st.text_input("Set a new goal", key="new_goal_input")
        if st.button("Add Goal"):
            if new_goal:
                user_goals.append(new_goal)
                st.session_state.user_goals[user] = user_goals
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.experimental_rerun()

        # Active goals list with delete/archive options
        if user_goals:
            st.subheader("Active Goals")
            for i, goal in enumerate(user_goals):
                col1, col2, col3 = st.columns([6, 1, 1])
                col1.write(goal)
                if col2.button("✓", key=f"archive_{i}"):
                    archived = st.session_state.user_archived_goals.get(user, [])
                    archived.append(goal)
                    st.session_state.user_archived_goals[user] = archived
                    user_goals.pop(i)
                    st.session_state.user_goals[user] = user_goals
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    save_json("user_archived_goals.json", st.session_state.user_archived_goals)
                    st.experimental_rerun()
                if col3.button("✕", key=f"delete_{i}"):
                    user_goals.pop(i)
                    st.session_state.user_goals[user] = user_goals
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.experimental_rerun()

        # Archived goals view
        with st.expander("View Archived Goals"):
            archived_goals = st.session_state.user_archived_goals.get(user, [])
            if archived_goals:
                for goal in archived_goals:
                    st.markdown(f"- {goal}")
            else:
                st.caption("No archived goals yet.")
    st.caption("No archived goals yet.")
    st.subheader("Student Dashboard - goals, videos, badges")

def show_teacher_dashboard(user):
    st.subheader("Teacher Dashboard - templates, comments, class")

# ---- Main App ----
def main():
    initialize_session_state()
    user, role = get_current_user_and_role()

    if not user:
        show_login_signup()
        return

    if role == "student":
        show_student_dashboard(user)
    elif role == "admin":
        show_teacher_dashboard(user)
    else:
        st.error("Unknown role")

if __name__ == "__main__":
    main()