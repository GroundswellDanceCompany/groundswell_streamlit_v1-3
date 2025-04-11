
import streamlit as st
import json
import os
import uuid

st.set_page_config("Groundswell App", layout="centered")

# ---------- File Paths ----------
USER_DB_FILE = "user_db.json"
TEMPLATES_FILE = "templates.json"
os.makedirs("videos", exist_ok=True)

# ---------- Load/Save Helpers ----------
def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- Initialize Session ----------
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_json(USER_DB_FILE, {
        "teacher": {"password": "adminpass", "role": "teacher", "groups": ["All"]}
    })
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "templates" not in st.session_state:
    st.session_state.templates = load_json(TEMPLATES_FILE, [])
if "register" not in st.session_state:
    st.session_state.register = False

CLASS_GROUPS = [
    "Junior Jazz", "Junior Ballet", "Contemporary", "Hip Hop", "Tap", "Advanced Jazz"
]

# ---------- Registration ----------
st.sidebar.title("Welcome to Groundswell App")
mode = st.sidebar.radio("Select Mode", ["Login", "Create Account"])
st.session_state.register = (mode == "Create Account")

if st.session_state.register:
    st.title("Student Registration")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    new_class = st.selectbox("Select your class", CLASS_GROUPS)
    if st.button("Create Account"):
        if new_user in st.session_state.USER_DB:
            st.error("Username already exists.")
        else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student",
                "groups": [new_class]
            }
            save_json(USER_DB_FILE, st.session_state.USER_DB)
            st.success("Account created! Please log in.")
            st.session_state.register = False
            st.experimental_rerun()

# ---------- Login ----------
if not st.session_state.logged_in and not st.session_state.register:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = st.session_state.USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# ---------- Main App ----------
if st.session_state.logged_in:
    username = st.session_state.username
    user = st.session_state.USER_DB[username]
    is_teacher = user["role"] == "teacher"
    is_teacher = user["role"] == "teacher"
    st.sidebar.success(f"Logged in as {username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    st.title("Groundswell Goal App")

    # ---------- Template Section ----------
    st.subheader("Goal Templates")
    if is_teacher:
        st.markdown("### Create Template")
        temp_title = st.text_input("Template Title")
        temp_cat = st.selectbox("Category", ["Technique", "Strength", "Performance"])
        temp_class = st.selectbox("Class Group", CLASS_GROUPS)
        if st.button("Add Template"):
            new_template = {
                "id": str(uuid.uuid4()),
                "title": temp_title,
                "category": temp_cat,
                "class": temp_class
            }
            st.session_state.templates.append(new_template)
            save_json(TEMPLATES_FILE, st.session_state.templates)
            st.success("Template added.")

    else:
        student_classes = user.get("groups", [])
        available_templates = [t for t in st.session_state.templates if t["class"] in student_classes]

    st.markdown("## Available Templates")
    for t in available_templates:
        st.markdown(f"**{t['title']}** — {t['category']} ({t['class']})")
        if st.button(f"Add to My Goals: {t['id']}", key=f"add_{t['id']}"):
            new_goal = {
                "id": str(uuid.uuid4()),
                "title": t["title"],
                "category": t["category"],
                "target_date": str(datetime.date.today()),
                "done": False
            }
            user_goals.append(new_goal)
            st.session_state.user_goals[username] = user_goals
            save_json(GOALS_FILE, st.session_state.user_goals)
            st.success(f"Added goal from template: {t['title']}")

    # ---------- Placeholders ----------
    st.markdown("---")

import datetime

GOALS_FILE = "user_goals.json"
if "user_goals" not in st.session_state:
    st.session_state.user_goals = load_json(GOALS_FILE, {})

# ---------- Student Goal Tracking ----------
if not is_teacher:

    st.markdown("## My Goals + Video Uploads")
    for goal in user_goals:
        st.markdown(f"**{goal['title']}** — {goal['category']} | Due: {goal['target_date']}")
        if goal.get("done"):
            st.success("Completed")
        else:
            if st.button("Mark as Done", key=f"done_{goal['id']}"):
                goal["done"] = True
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.experimental_rerun()

        # --- Video Upload Section for This Goal ---
        with st.expander("Upload Video"):
            uploaded = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"], key=f"video_{goal['id']}")
            label = st.text_input("Label for this video", key=f"label_{goal['id']}")
            if st.button("Save Video", key=f"savevid_{goal['id']}"):
                if uploaded and label:
                    vid_id = str(uuid.uuid4()) + "_" + uploaded.name.replace(" ", "_")
                    vid_path = os.path.join("videos", vid_id)
                    with open(vid_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    if "videos" not in goal:
                        goal["videos"] = []
                    goal["videos"].append({
                        "label": label,
                        "filename": vid_path,
                        "uploaded": str(datetime.date.today())
                    })
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.success("Video saved.")
                else:
                    st.warning("Please select a video and enter a label.")

        if goal.get("videos"):
            st.markdown("**Uploaded Videos:**")
            for vid in goal["videos"]:
                st.markdown(f"- {vid['label']} ({vid['uploaded']})")
                if os.path.exists(vid["filename"]):
                    st.video(vid["filename"])
        st.markdown("---")
    st.markdown("## My Goals")

    user_goals = st.session_state.user_goals.get(username, [])

    # Add new goal from scratch
    with st.form("add_goal"):
        goal_title = st.text_input("Goal Title")
        goal_cat = st.selectbox("Category", ["Technique", "Strength", "Performance"])
        goal_date = st.date_input("Target Date", datetime.date.today())
        submitted = st.form_submit_button("Add Goal")
        if submitted and goal_title:
            new_goal = {
                "id": str(uuid.uuid4()),
                "title": goal_title,
                "category": goal_cat,
                "target_date": str(goal_date),
                "done": False
            }
            user_goals.append(new_goal)
            st.session_state.user_goals[username] = user_goals
            save_json(GOALS_FILE, st.session_state.user_goals)
            st.success("Goal added!")

    # List and mark completed goals
    for goal in user_goals:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{goal['title']}** — {goal['category']} | Due: {goal['target_date']}")
        with col2:
            if not goal["done"] and st.button("Done", key=goal["id"]):
                goal["done"] = True
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.experimental_rerun()
        if goal["done"]:
            st.success("Completed")
    st.subheader("Badges & Streaks [coming next]")
    st.subheader("Video Upload [coming next]")

# ---------- Badge + Streak System ----------
BADGES_FILE = "user_badges.json"
STREAKS_FILE = "user_streaks.json"

if "user_badges" not in st.session_state:
    st.session_state.user_badges = load_json(BADGES_FILE, {})
if "user_streaks" not in st.session_state:
    st.session_state.user_streaks = load_json(STREAKS_FILE, {})

BADGE_EMOJIS = {
    "First Goal Completed": "🏁",
    "Goal Getter: 5 Goals Done": "⭐",
    "Well-Rounded: All Categories": "🌈",
    "Streak Star: 3-Day Streak": "🔥"
}

def check_and_award_badges(username, goals):
    earned = st.session_state.user_badges.get(username, [])
    done = [g for g in goals if g["done"]]
    cats = set(g["category"] for g in done)

    if len(done) >= 1 and "First Goal Completed" not in earned:
        earned.append("First Goal Completed")
    if len(done) >= 5 and "Goal Getter: 5 Goals Done" not in earned:
        earned.append("Goal Getter: 5 Goals Done")
    if all(c in cats for c in ["Technique", "Strength", "Performance"]) and "Well-Rounded: All Categories" not in earned:
        earned.append("Well-Rounded: All Categories")

    # --- Streaks ---
    streak_data = st.session_state.user_streaks.get(username, {"dates": [], "streak": 0})
    today = str(datetime.date.today())
    if today not in streak_data["dates"]:
        streak_data["dates"].append(today)
    streak_data["dates"] = sorted(set(streak_data["dates"]))[-5:]  # keep last 5 unique days
    streak_data["streak"] = 1
    for i in range(len(streak_data["dates"]) - 1, 0, -1):
        d1 = datetime.datetime.strptime(streak_data["dates"][i], "%Y-%m-%d")
        d0 = datetime.datetime.strptime(streak_data["dates"][i - 1], "%Y-%m-%d")
        if (d1 - d0).days == 1:
            streak_data["streak"] += 1
        else:
            break
    if streak_data["streak"] >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")

    st.session_state.user_badges[username] = earned
    st.session_state.user_streaks[username] = streak_data
    save_json(BADGES_FILE, st.session_state.user_badges)
    save_json(STREAKS_FILE, st.session_state.user_streaks)

# ---------- Show Badges ----------
check_and_award_badges(username, user_goals)
user_badges = st.session_state.user_badges.get(username, [])
if user_badges:
    st.markdown("### Badges Earned:")
    st.markdown(" ".join(BADGE_EMOJIS[b] for b in user_badges if b in BADGE_EMOJIS))
