
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

# Student Goal Tracker with multi-video support and working delete
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
            st.checkbox("Done", value=g["done"], key=g["id"], on_change=lambda: g.update({"done": not g["done"]}))

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
                st.success("New video added.")
                st.experimental_rerun()  # Refresh to show new video immediately

            delete_key = f"del_{g['id']}"
            delete_index = st.selectbox(f"Delete a video for '{g['text']}'", 
                                        options=[(i, v['filename']) for i, v in enumerate(g.get("videos", []))],
                                        format_func=lambda x: f"{x[1].split('/')[-1]}",
                                        key=delete_key)

            if st.button("Delete Selected Video", key=f"del_btn_{g['id']}"):
                idx = delete_index[0]
                filepath = g["videos"][idx]["filename"]
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    del g["videos"][idx]
                    st.success("Video deleted.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error deleting video: {e}")

            if g.get("videos"):
                st.markdown("### Uploaded Videos")
                for v in g["videos"]:
                    if os.path.exists(v["filename"]):
                        st.markdown(f"_Uploaded: {v['uploaded']}_")
                        st.video(v["filename"])

    st.session_state.user_goals[user] = goals
    save_json(GOALS_FILE, st.session_state.user_goals)
