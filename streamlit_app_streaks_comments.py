
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

# --- Login, Signup, Reset (omitted for brevity in this snippet, same as before) ---

# --- Main App ---
if st.session_state.logged_in:
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
