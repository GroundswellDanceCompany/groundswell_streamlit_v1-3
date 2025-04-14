
import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- File Paths ---
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"

if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

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

user_goals = load_json(GOALS_FILE, {})
templates = load_json(TEMPLATES_FILE, [])
user_streaks = load_json(STREAKS_FILE, {})
user_badges = load_json(BADGES_FILE, {})

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

BADGE_EMOJIS = {
    "First Goal Completed": "🏁",
    "Goal Getter: 5 Goals Done": "⭐",
    "Well-Rounded: All Categories": "🌈",
    "Streak Star: 3-Day Streak": "🔥"
}

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.mode = "login"

def check_and_award_badges(username, goals, streak_data):
    earned = user_badges.get(username, [])
    done_goals = [g for g in goals if g["done"]]
    categories = set(g["category"] for g in done_goals)

    if len(done_goals) >= 1 and "First Goal Completed" not in earned:
        earned.append("First Goal Completed")
        st.success("🏁 Badge Unlocked: First Goal Completed!")
    if len(done_goals) >= 5 and "Goal Getter: 5 Goals Done" not in earned:
        earned.append("Goal Getter: 5 Goals Done")
        st.success("⭐ Badge Unlocked: Goal Getter!")
    if all(cat in categories for cat in ["Technique", "Strength", "Flexibility", "Performance"]) and "Well-Rounded: All Categories" not in earned:
        earned.append("Well-Rounded: All Categories")
        st.success("🌈 Badge Unlocked: Well-Rounded!")
    if streak_data.get("streak", 0) >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")
        st.success("🔥 Badge Unlocked: Streak Star!")

    user_badges[username] = earned
    save_json(BADGES_FILE, user_badges)

# Login system continues...
# ... (script truncated here for demonstration brevity)
