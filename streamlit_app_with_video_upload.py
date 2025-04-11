
import streamlit as st
import uuid
import datetime
import json
import os

# Setup
st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

GOALS_FILE = "user_goals.json"
USER_DB_FILE = "user_db.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Session init
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_json(USER_DB_FILE, {
        "student": {"password": "pass", "role": "student", "groups": []}
    })
if "user_goals" not in st.session_state:
    st.session_state.user_goals = load_json(GOALS_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.mode = "login"

# Login
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        db = st.session_state.USER_DB
        if username in db and db[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid login.")

# Student Goal Tracker with Video Upload
elif st.session_state.logged_in:
    user = st.session_state.username
    st.sidebar.title(f"Welcome, {user}")
    st.sidebar.button("Logout", on_click=logout)

    goals = st.session_state.user_goals.get(user, [])

    st.title("My Goals + Progress Videos")

    with st.form("add_goal"):
        text = st.text_input("Goal")
        cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        date = st.date_input("Target Date", datetime.date.today())
        add = st.form_submit_button("Add Goal")
        if add and text:
            goals.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "category": cat,
                "target_date": str(date),
                "done": False,
                "video": None
            })
            st.session_state.user_goals[user] = goals
            save_json(GOALS_FILE, st.session_state.user_goals)

    st.subheader("Active Goals")
    for g in goals:
        with st.expander(f"{g['text']} ({g['category']}) — {g['target_date']}"):
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                if g.get("video"):
                    st.video(g["video"])
            with col2:
                if st.checkbox("Done", value=g["done"], key=g["id"]):
                    g["done"] = True

            uploaded = st.file_uploader("Upload Progress Video", type=["mp4", "mov"], key=f"upload_{g['id']}")
            if uploaded:
                g["video"] = uploaded.name
                with open(os.path.join("videos", uploaded.name), "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success("Video uploaded and linked to goal.")

    st.session_state.user_goals[user] = goals
    save_json(GOALS_FILE, st.session_state.user_goals)
