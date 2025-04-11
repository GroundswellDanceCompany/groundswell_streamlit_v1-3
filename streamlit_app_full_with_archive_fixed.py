
# FULL STREAMLIT APP with all features and FIXED LOGIN FLOW to prevent blank screen

import streamlit as st
import uuid
import datetime
import json
import os

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# ---- Paths ----
USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"

# ---- Load/Save Helpers ----
def load_json(file, default): return json.load(open(file)) if os.path.exists(file) else default
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

# ---- Init ----
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
if "show_archived" not in st.session_state:
    st.session_state.show_archived = False

os.makedirs(VIDEO_DIR, exist_ok=True)

# ---- Classes ----
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

def check_and_award_badges(user, goals, streak_data):
    earned = st.session_state.user_badges.get(user, [])
    done = [g for g in goals if g["done"] and not g.get("archived")]
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

# ---- Auth ----
if not st.session_state.logged_in:
    if st.session_state.mode == "login":
        st.title("Groundswell Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            db = st.session_state.USER_DB
            if u in db and db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.experimental_rerun()
            else:
                st.error("Invalid credentials.")
        st.button("Sign Up", on_click=lambda: st.session_state.update(mode="signup"))
        st.button("Reset Password", on_click=lambda: st.session_state.update(mode="reset"))

    elif st.session_state.mode == "signup":
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
                st.experimental_rerun()

    elif st.session_state.mode == "reset":
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
                st.experimental_rerun()
            else:
                st.error("Invalid user.")
        st.button("Back", on_click=lambda: st.session_state.update(mode="login"))

# ---- Main App ----
elif st.session_state.logged_in:
    user = st.session_state.username
    info = st.session_state.USER_DB[user]
    is_teacher = info["role"] == "admin"
    goals = st.session_state.user_goals.get(user, [])

    st.sidebar.title(f"Hello, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if is_teacher:
        st.title("Teacher Dashboard")
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

    else:
        st.title("Student Dashboard")
        streak = st.session_state.user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        badges = st.session_state.user_badges.get(user, [])

        st.markdown(f"**Current Streak:** {streak['streak']} days")
        if badges:
            st.markdown("### Badges")
            for b in badges:
                st.markdown(f"{BADGE_EMOJIS[b]} {b}")

        st.checkbox("Show Archived Goals", key="show_archived")

        with st.form("new_goal"):
            text = st.text_input("New Goal")
            cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
            date = st.date_input("Target Date", datetime.date.today())
            if st.form_submit_button("Add") and text:
                goals.append({
                    "id": str(uuid.uuid4()), "text": text, "category": cat,
                    "target_date": str(date), "done": False, "videos": [], "archived": False
                })
                st.session_state.user_goals[user] = goals
                save_json(GOALS_FILE, st.session_state.user_goals)
                st.success("Goal added.")

        filtered = [
            g for g in goals if g.get("archived") == st.session_state.show_archived
        ]
        st.subheader("My Goals")
        for g in filtered:
            with st.expander(f"{g['text']} ({g['category']}) — {g['target_date']}"):
                if st.checkbox("Done", value=g["done"], key=g["id"]):
                    g["done"] = True
                    today = datetime.date.today().isoformat()
                    last = streak.get("last_completion_date")
                    if last == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
                        streak["streak"] += 1
                    elif last != today:
                        streak["streak"] = 1
                    streak["last_completion_date"] = today
                    st.session_state.user_streaks[user] = streak
                    save_json(STREAKS_FILE, st.session_state.user_streaks)
                    check_and_award_badges(user, goals, streak)

                if g["done"] and not g.get("archived"):
                    if st.button("Archive Goal", key=f"arch_{g['id']}"):
                        g["archived"] = True
                        save_json(GOALS_FILE, st.session_state.user_goals)
                        st.experimental_rerun()
                elif g.get("archived"):
                    if st.button("Unarchive Goal", key=f"unarch_{g['id']}"):
                        g["archived"] = False
                        save_json(GOALS_FILE, st.session_state.user_goals)
                        st.experimental_rerun()

                label = st.text_input("Video Label", key=f"label_{g['id']}")
                vid = st.file_uploader("Upload video", type=["mp4", "mov"], key=f"upload_{g['id']}")
                if vid and label and st.button("Upload", key=f"upload_btn_{g['id']}"):
                    fn = f"{g['id']}_{uuid.uuid4().hex}_{vid.name}"
                    path = os.path.join(VIDEO_DIR, fn)
                    with open(path, "wb") as f:
                        f.write(vid.getbuffer())
                    g["videos"].append({"filename": path, "label": label, "uploaded": str(datetime.datetime.now())})
                    save_json(GOALS_FILE, st.session_state.user_goals)
                    st.success("Video uploaded.")

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
