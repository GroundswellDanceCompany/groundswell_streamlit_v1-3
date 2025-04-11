
import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

GOALS_FILE = "user_goals.json"
USER_DB_FILE = "user_db.json"
VIDEO_DIR = "videos"

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

if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

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

# Student Goal Tracker with Multi-Video Support
elif st.session_state.logged_in:
    user = st.session_state.username
    st.sidebar.title(f"Welcome, {user}")
    st.sidebar.button("Logout", on_click=logout)

    goals = st.session_state.user_goals.get(user, [])

    st.title("My Goals + Video Progress Tracker")

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
                "videos": []
            })
            st.session_state.user_goals[user] = goals
            save_json(GOALS_FILE, st.session_state.user_goals)

    st.subheader("Active Goals")
    for g in goals:
        with st.expander(f"{g['text']} ({g['category']}) — {g['target_date']}"):
            col1, col2 = st.columns([0.7, 0.3])
            with col2:
                if st.checkbox("Done", value=g["done"], key=g["id"]):
                    g["done"] = True

            uploaded = st.file_uploader("Upload a new video", type=["mp4", "mov"], key=f"upload_{g['id']}")
            if uploaded:
                vid_filename = f"{g['id']}_{uuid.uuid4().hex}_{uploaded.name}"
                video_path = os.path.join(VIDEO_DIR, vid_filename)
                with open(video_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                g.setdefault("videos", []).append({
                    "filename": video_path,
                    "uploaded": str(datetime.datetime.now())
                })
                st.success("Video added.")

            st.markdown("### Uploaded Videos")
            to_delete = []
            for i, v in enumerate(g.get("videos", [])):
                vid_file = v["filename"]
                label = v["uploaded"]
                st.markdown(f"**Video {i+1}** (Uploaded: {label})")
                if os.path.exists(vid_file):
                    st.video(vid_file)
                    if st.button("Delete", key=f"del_{g['id']}_{i}"):
                        to_delete.append(i)
                else:
                    st.warning("Missing file: " + vid_file)

            for index in sorted(to_delete, reverse=True):
                # Remove video file from disk and from list
                try:
                    os.remove(g["videos"][index]["filename"])
                except Exception:
                    pass
                del g["videos"][index]
                st.success("Video deleted.")

    st.session_state.user_goals[user] = goals
    save_json(GOALS_FILE, st.session_state.user_goals)
