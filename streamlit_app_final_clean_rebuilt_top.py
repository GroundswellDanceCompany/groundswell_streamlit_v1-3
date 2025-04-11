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
os.makedirs(VIDEO_DIR, exist_ok=True)

# --- Helpers ---
def load_json(path, default):
    if os.path.exists(path):
        return json.load(open(path))
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --- Initialize session state ---
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_json(USER_DB_FILE, {"teacher": {"password": "adminpass", "role": "admin", "groups": []}})
if "user_goals" not in st.session_state:
    st.session_state.user_goals = load_json(GOALS_FILE, {})
if "templates" not in st.session_state:
    st.session_state.templates = load_json(TEMPLATES_FILE, [])
if "user_streaks" not in st.session_state:
    st.session_state.user_streaks = load_json(STREAKS_FILE, {})
if "user_badges" not in st.session_state:
    st.session_state.user_badges = load_json(BADGES_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "show_archived" not in st.session_state:
    st.session_state.show_archived = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "show_archived" not in st.session_state:
    st.session_state.show_archived = False


# --- File Paths ---




def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.mode = "login"

    earned = st.session_state.user_badges.get(username, [])
    if streak_data.get("streak", 0) >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")
    st.session_state.user_badges[username] = earned
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "show_archived" not in st.session_state:
    st.session_state.show_archived = False

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



if not st.session_state.logged_in:
    st.title("Groundswell Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = st.session_state.USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
if st.session_state.logged_in:
    user = st.session_state.username
    info = st.session_state.USER_DB[user]
    goals = st.session_state.user_goals.get(user, [])
    is_teacher = info["role"] == "admin"

    st.sidebar.title(f"Welcome, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if is_teacher:
        st.title("Teacher Dashboard")
        with st.form("add_template"):
            text = st.text_input("Template Goal")
            cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            grps = st.multiselect("Assign to Groups", CLASS_GROUPS)
            if st.form_submit_button("Add Template") and text:
                st.session_state.templates.append({
                    "id": str(uuid.uuid4()), "text": text, "category": cat, "groups": grps
                })

        st.subheader("Current Templates")
        for t in st.session_state.templates:
            st.markdown(f"- **{t['text']}** ({t['category']}) — {', '.join(t['groups'])}")

    else:
        st.title("My Dashboard")
        streak = st.session_state.user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        st.markdown(f"**Current Streak:** {streak['streak']} days")

        badges = st.session_state.user_badges.get(user, [])
        if badges:
            st.subheader("Badges")
            for b in badges:
                st.markdown(f"{BADGE_EMOJIS[b]} {b}")

        st.checkbox("Show Archived Goals", key="show_archived")

        with st.form("add_goal"):
            text = st.text_input("Goal")
            cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            date = st.date_input("Target Date", datetime.date.today())
            if st.form_submit_button("Add Goal") and text:
                goals.append({
                    "id": str(uuid.uuid4()), "text": text, "category": cat, "target_date": str(date),
                    "done": False, "videos": [], "archived": False
                })
                st.session_state.user_goals[user] = goals

        for g in [g for g in goals if g.get("archived") == st.session_state.show_archived]:
            with st.expander(f"{g['text']} ({g['category']}) — {g['target_date']}"):
                g["done"] = st.checkbox("Mark Done", value=g["done"], key=g["id"])
                if g["done"] and not g.get("archived") and st.button("Archive", key=f"arch_{g['id']}"):
                    g["archived"] = True
                elif g.get("archived") and st.button("Unarchive", key=f"unarch_{g['id']}"):
                    g["archived"] = False

                st.markdown("**Upload Progress Video**")
                label = st.text_input("Label", key=f"label_{g['id']}")
                vid = st.file_uploader("Upload", type=["mp4", "mov"], key=f"upload_{g['id']}")
                if vid and label and st.button("Submit Upload", key=f"up_{g['id']}"):
                    with open(path, "wb") as f:
                        f.write(vid.getbuffer())
                    g["videos"].append({
                        "filename": path, "label": label, "uploaded": str(datetime.datetime.now())
                    })

                for i, v in enumerate(g.get("videos", [])):
                    if os.path.exists(v["filename"]):
                        st.markdown(f"**{v['label']}** — {v['uploaded']}")
                        st.video(v["filename"])
    
    user = st.session_state.username
    st.sidebar.title(f"Welcome, {user}")
    st.sidebar.button("Logout", on_click=logout)
    goals = st.session_state.user_goals.get(user, [])
    st.title("My Goals + Labeled Video Uploads")
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
    for g in goals:
        st.markdown(f"### {g['text']}")
        st.markdown(f"*Category:* {g['category']}  |  *Due:* {g['target_date']}")
        if g.get("done"):
            st.success("Completed")
        else:
            if st.button("Mark as Done", key=f"done_{g['id']}"):
                g["done"] = True
                st.experimental_rerun()
        for i, v in enumerate(g.get("videos", [])):
            if os.path.exists(v["filename"]):
                st.markdown(f"**{v['label']}** — {v['uploaded']}")
                st.video(v["filename"])
                uploaded = st.file_uploader("Select a video", type=["mp4", "mov"], key=f"upload_{g['id']}")
    
                if uploaded and video_label:
                    if st.button("Upload Video", key=f"submit_upload_{g['id']}"):
                        vid_filename = f"{g['id']}_{uuid.uuid4().hex}_{uploaded.name}"
                        with open(video_path, "wb") as f:
                            f.write(uploaded.getbuffer())
                        g.setdefault("videos", []).append({
                            "filename": video_path,
                            "label": video_label,
                            "uploaded": str(datetime.datetime.now())
                        })
                        st.success(f"Video '{video_label}' uploaded.")
    
                if g.get("videos"):
                    st.markdown("### Uploaded Videos")
                    for i, v in enumerate(g["videos"]):
                        video_file = v["filename"]
                        label = v.get("label", f"Video {i+1}")
                        if os.path.exists(video_file):
                            st.markdown(f"**{label}** — Uploaded: {v['uploaded']}")
                            st.video(video_file)
                            if st.button(f"Delete {label}", key=f"del_{g['id']}_{i}"):
                                try:
                                    os.remove(video_file)
                                except:
                                    pass
                                del g["videos"][i]
                                st.success(f"Deleted {label}")
                                break
                        else:
                            st.warning(f"Missing file: {video_file}")
