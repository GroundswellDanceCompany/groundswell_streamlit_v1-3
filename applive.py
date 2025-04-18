
import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Dance Portal", layout="centered")

# --- File Paths ---
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"

# --- Ensure video directory exists ---
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# --- Load/Save Helpers ---
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# --- Initialize State ---
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
    st.rerun()

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

    if all(cat in categories for cat in ["Technique", "Strength", "Flexibility", "Performance"]) and         "Well-Rounded: All Categories" not in earned:
        earned.append("Well-Rounded: All Categories")
        st.success("🌈 Badge Unlocked: Well-Rounded!")

    if streak_data.get("streak", 0) >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")
        st.success("🔥 Badge Unlocked: Streak Star!")

    user_badges[username] = earned
    save_json(BADGES_FILE, user_badges)

# --- Login System ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Dance Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        db = st.session_state.USER_DB
        if username in db and db[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid login.")
    if st.button("Sign Up"): st.session_state.mode = "signup"; st.rerun()
    if st.button("Reset Password"): st.session_state.mode = "reset"; st.rerun()

elif not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    groups = st.multiselect("Your Classes", CLASS_GROUPS)
    if st.button("Create"):
        db = st.session_state.USER_DB
        if new_user in db:
            st.error("Username taken.")
        else:
            db[new_user] = {"password": new_pass, "role": "student", "groups": groups}
            save_json(USER_DB_FILE, db)
            st.success("Account created!")
            st.session_state.mode = "login"
            st.rerun()
    if st.button("Back"): st.session_state.mode = "login"; st.rerun()

elif not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    user = st.text_input("Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset"):
        db = st.session_state.USER_DB
        if user in db and user != "teacher":
            db[user]["password"] = new_pass
            save_json(USER_DB_FILE, db)
            st.success("Password reset.")
            st.session_state.mode = "login"
            st.rerun()
        else:
            st.error("User not found.")
    if st.button("Back"): st.session_state.mode = "login"; st.rerun()

# --- Main App (Logged In) ---
elif st.session_state.logged_in:
    user = st.session_state.username
    user_info = st.session_state.USER_DB[user]
    is_teacher = user_info["role"] == "admin"
    st.sidebar.title(f"Hello, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if is_teacher:
        st.title("Teacher Dashboard")
        st.subheader("Create Goal Template")
        with st.form("template_form"):
            text = st.text_input("Goal Text")
            cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            assign = st.multiselect("Assign to Groups", CLASS_GROUPS)
            if st.form_submit_button("Add") and text:
                templates.append({
                    "id": str(uuid.uuid4()), "text": text, "category": cat, "groups": assign
                })
                save_json(TEMPLATES_FILE, templates)
                st.success("Template added.")
        st.subheader("Templates")
        for t in templates:
            st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(t['groups'])}")

        st.subheader("Student Goals + Comments")
        for student, goals in user_goals.items():
            st.markdown(f"### {student}")
            for g in goals:
                st.markdown(f"**{g['text']}** ({g['category']}) — due {g['target_date']}")
                comment_key = f"comment_{student}_{g['id']}"
                new_comment = st.text_input("Comment", value=g.get("comment", ""), key=comment_key)
                if new_comment != g.get("comment", ""):
                    g["comment"] = new_comment
                    save_json(GOALS_FILE, user_goals)

    else:
        st.title("My Goals")
        goals = user_goals.get(user, [])
        streak = user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        badges = user_badges.get(user, [])

        st.markdown(f"**Current Streak:** {streak['streak']} day(s)")
        if badges:
            st.markdown("### Badges:")
            for b in badges:
                st.markdown(f"{BADGE_EMOJIS.get(b, '')} {b}")

        with st.form("add_goal"):
            g_text = st.text_input("New Goal")
            g_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            g_date = st.date_input("Target Date", datetime.date.today())
            if st.form_submit_button("Add") and g_text:
                goals.append({
                    "id": str(uuid.uuid4()), "text": g_text, "category": g_cat,
                    "target_date": str(g_date), "done": False, "videos": []
                })
                user_goals[user] = goals
                save_json(GOALS_FILE, user_goals)

        st.subheader("Templates for You")
        my_groups = user_info.get("groups", [])
        my_templates = [t for t in templates if any(g in my_groups for g in t.get("groups", []))]
        for t in my_templates:
            with st.expander(f"{t['text']} ({t['category']})"):
                goal_date = st.date_input(f"Date for: {t['text']}", datetime.date.today(), key=t["id"])
                if st.button(f"Add to My Goals", key=f"add_{t['id']}"):
                    goals.append({
                        "id": str(uuid.uuid4()), "text": t['text'], "category": t['category'],
                        "target_date": str(goal_date), "done": False, "videos": []
                    })
                    user_goals[user] = goals
                    save_json(GOALS_FILE, user_goals)

        st.subheader("My Active Goals")
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
                        last = streak.get("last_completion_date")
                        if last == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
                            streak["streak"] += 1
                        elif last != today:
                            streak["streak"] = 1
                        streak["last_completion_date"] = today
                        user_streaks[user] = streak
                        save_json(GOALS_FILE, user_goals)
                        save_json(STREAKS_FILE, user_streaks)
                        check_and_award_badges(user, goals, streak)

            st.markdown("#### Upload a New Video")
            video_label = st.text_input("Label for new video", key=f"label_{g['id']}")
            uploaded = st.file_uploader("Select a video", type=["mp4", "mov"], key=f"upload_{g['id']}")
            if uploaded and video_label:
                if st.button("Upload Video", key=f"submit_upload_{g['id']}"):
                    vid_filename = f"{g['id']}_{uuid.uuid4().hex}_{uploaded.name}"
                    video_path = os.path.join(VIDEO_DIR, vid_filename)
                    with open(video_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    g.setdefault("videos", []).append({
                        "filename": video_path,
                        "label": video_label,
                        "uploaded": str(datetime.datetime.now())
                    })
                    st.success(f"Video '{video_label}' uploaded.")
                    save_json(GOALS_FILE, user_goals)

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
                            save_json(GOALS_FILE, user_goals)
                            st.success(f"Deleted {label}")
                            break
                    else:
                        st.warning(f"Missing file: {video_file}")
