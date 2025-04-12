
# STREAMLIT APP: Full Version
# Includes: Login, Signup, Teacher Templates, Badges, Streaks, Goal Tracker, Labeled Video Upload

import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")


CLASS_GROUPS = [
    "Advanced Waacking", "Advanced Locking", "Advanced House", "Advanced Hip Hop",
    "Intermediate Ballet", "Intermediate Contemporary", "Junior Waacking", "Junior Locking",
    "Junior House", "Junior Locking", "Junior Ballet", "Junior Contemporary", "Advanced Jazz",
    "Junior Jazz", "Commercial", "Open House Class", "Tap Class", "GSD Youth", "GFoundation",
    "Jenga", "Youth Jazz Company", "Junior Jazz Company", "Youth Contemporary Company", "Junior Contemporary Company"
]


# ---- File Paths ----
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"

# ---- Load/Save Helpers ----
def load_json(file, default): return json.load(open(file)) if os.path.exists(file) else default
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

# ---- Setup State ----
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
if "user_badges" not in st.session_state:
    st.session_state.user_badges = load_json(BADGES_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"

os.makedirs(VIDEO_DIR, exist_ok=True)

# ---- Classes ----
CLASS_GROUPS = ["GSD Youth", "Jenga", "Junior Contemporary", "Junior Jazz", "Advanced Jazz"]

BADGE_EMOJIS = {
    "First Goal Completed": "🏁",
    "Goal Getter: 5 Goals Done": "⭐",
    "Well-Rounded: All Categories": "🌈",
    "Streak Star: 3-Day Streak": "🔥"
}

def check_and_award_badges(user, goals, streak_data):
    earned = st.session_state.user_badges.get(user, [])
    done = [g for g in goals if g["done"]]
    cats = set(g["category"] for g in done)

    if len(done) >= 1 and "First Goal Completed" not in earned:
        earned.append("First Goal Completed")
        st.success("🏁 Badge Unlocked!")

    if len(done) >= 5 and "Goal Getter: 5 Goals Done" not in earned:
        earned.append("Goal Getter: 5 Goals Done")
        st.success("⭐ Badge Unlocked!")

    if all(c in cats for c in ["Technique", "Strength", "Flexibility", "Performance"]) and        "Well-Rounded: All Categories" not in earned:
        earned.append("Well-Rounded: All Categories")
        st.success("🌈 Badge Unlocked!")

    if streak_data.get("streak", 0) >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")
        st.success("🔥 Badge Unlocked!")

    st.session_state.user_badges[user] = earned
    save_json(BADGES_FILE, st.session_state.user_badges)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.mode = "login"

# ---- Auth Views ----
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        db = st.session_state.USER_DB
        if u in db and db[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.username = u
        else:
            st.error("Invalid credentials.")
    if st.button("Sign Up"): st.session_state.mode = "signup"
    if st.button("Reset Password"): st.session_state.mode = "reset"

elif not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Sign Up")
    u = st.text_input("New Username")
    p = st.text_input("Password", type="password")
    g = st.multiselect("Your Classes", CLASS_GROUPS)
    if st.button("Create Account"):
        if u in st.session_state.USER_DB:
            st.error("Username taken.")
        else:
            st.session_state.USER_DB[u] = {"password": p, "role": "student", "groups": g}
            save_json(USER_DB_FILE, st.session_state.USER_DB)
            st.success("Account created!")
            st.session_state.mode = "login"

elif not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    u = st.text_input("Username")
    np = st.text_input("New Password", type="password")
    if st.button("Reset"):
        db = st.session_state.USER_DB
        if u in db and u != "teacher":
            db[u]["password"] = np
            save_json(USER_DB_FILE, db)
            st.success("Password reset.")
            st.session_state.mode = "login"
        else:
            st.error("Invalid user.")
    if st.button("Back"): st.session_state.mode = "login"

# ---- Main App ----
elif st.session_state.logged_in:
    user = st.session_state.username
    info = st.session_state.USER_DB[user]
    is_teacher = info["role"] == "admin"

    st.sidebar.title(f"Welcome, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if is_teacher:
        st.title("Teacher Mode")

        st.subheader("Create Template")
        with st.form("add_template"):
            t_text = st.text_input("Template Text")
            t_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            t_groups = st.multiselect("Assign to Classes", CLASS_GROUPS)
            if st.form_submit_button("Add") and t_text:
                st.session_state.templates.append({
                    "id": str(uuid.uuid4()), "text": t_text, "category": t_cat, "groups": t_groups
                })
                save_json(TEMPLATES_FILE, st.session_state.templates)
                st.success("Template added!")

        st.subheader("Templates")
        for t in st.session_state.templates:
            st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(t['groups'])}")

        st.subheader("Comment on Student Goals")
        for s, goals in st.session_state.user_goals.items():
            st.markdown(f"### {s}")
            for g in goals:
                st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
                ckey = f"comment_{s}_{g['id']}"
                comment = st.text_input("Comment:", value=g.get("comment", ""), key=ckey)
                if comment != g.get("comment", ""):
                    g["comment"] = comment
                    save_json(GOALS_FILE, st.session_state.user_goals)
    else:
        st.title("Student Dashboard")
        goals = st.session_state.user_goals.get(user, [])
        streak = st.session_state.user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        badges = st.session_state.user_badges.get(user, [])

        st.markdown(f"**Current Streak:** {streak['streak']} days")
        if badges:
            st.markdown("### Badges Earned")
            for b in badges:
                st.markdown(f"{BADGE_EMOJIS[b]} {b}")

        with st.form("new_goal"):
            text = st.text_input("New Goal")
            cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            date = st.date_input("Target Date", datetime.date.today())
            if st.form_submit_button("Add") and text:
                goals.append({
                    "id": str(uuid.uuid4()), "text": text, "category": cat,
                    "target_date": str(date), "done": False, "videos": []
                })
                st.session_state.user_goals[user] = goals
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.success("Goal added.")

        st.subheader("Templates for You")
        available = [t for t in st.session_state.templates if any(g in info["groups"] for g in t["groups"])]
        for t in available:
            with st.expander(f"{t['text']} ({t['category']})"):
                g_date = st.date_input(f"Date for {t['text']}", datetime.date.today(), key=t["id"])
                if st.button(f"Add Goal from Template", key=f"add_{t['id']}"):
                    goals.append({
                        "id": str(uuid.uuid4()), "text": t['text'], "category": t['category'],
                        "target_date": str(g_date), "done": False, "videos": []
                    })
                    st.session_state.user_goals[user] = goals
                    save_json(GOALS_FILE, st.session_state.user_goals)

        st.subheader("My Goals + Videos")
        for g in goals:
            with st.expander(f"{g['text']} ({g['category']}) — {g['target_date']}"):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if "comment" in g:
                        st.markdown(f"_Teacher Comment:_ {g['comment']}")
                with col2:
                    if st.checkbox("Done", value=g["done"], key=g["id"]):
                        if not g["done"]:
                            g["done"] = True
                            today = datetime.date.today().isoformat()
                            last = streak.get("last_completion_date")
                            if last == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
                                streak["streak"] += 1
                            elif last != today:
                                streak["streak"] = 1
                            streak["last_completion_date"] = today
                            st.session_state.user_streaks[user] = streak
                            save_json(GOALS_FILE, st.session_state.user_goals)
                            save_json(STREAKS_FILE, st.session_state.user_streaks)
                            check_and_award_badges(user, goals, streak)

                st.markdown("**Upload Progress Video**")
                label = st.text_input("Label for video", key=f"label_{g['id']}")
                vid = st.file_uploader("Upload video", type=["mp4", "mov"], key=f"upload_{g['id']}")
                if vid and label and st.button("Upload", key=f"submit_{g['id']}"):
                    fn = f"{g['id']}_{uuid.uuid4().hex}_{vid.name}"
                    path = os.path.join(VIDEO_DIR, fn)
                    with open(path, "wb") as f:
                        f.write(vid.getbuffer())
                    g["videos"].append({"filename": path, "label": label, "uploaded": str(datetime.datetime.now())})
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.success(f"Uploaded '{label}'")

                for i, v in enumerate(g.get("videos", [])):
                    if os.path.exists(v["filename"]):
                        st.markdown(f"**{v['label']}** — {v['uploaded']}")
                        st.video(v["filename"])
                        if st.button(f"Delete {v['label']}", key=f"del_{g['id']}_{i}"):
                            try: os.remove(v["filename"])
                            except: pass
                            del g["videos"][i]
                            save_json(GOALS_FILE, st.session_state.user_goals)
                            break

# --- Ensure user and role are always defined ---
user = st.session_state.get("current_user", None)
role = st.session_state.get("current_role", None)


# --- Goal Tracker Section ---
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