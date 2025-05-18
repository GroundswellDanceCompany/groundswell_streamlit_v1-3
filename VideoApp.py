
import streamlit as st
import uuid
import datetime
import json
import os
import streamlit as st

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

from supabase import create_client, Client

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- File Paths ---
#USER_DB_FILE = "user_db.json"
GOALS_FILE = "user_goals.json"
TEMPLATES_FILE = "templates.json"
STREAKS_FILE = "user_streaks.json"
BADGES_FILE = "user_badges.json"
VIDEO_DIR = "videos"
CLASS_VIDEO_DIR = "teacher_videos"

# --- Setup ---
for folder in [VIDEO_DIR, CLASS_VIDEO_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

#def load_json(filename, default):
    #if os.path.exists(filename):
        #with open(filename, "r") as f:
            #return json.load(f)
    #return default

#def save_json(filename, data):
    #with open(filename, "w") as f:
        #json.dump(data, f, indent=2)

#if "USER_DB" not in st.session_state:
    #st.session_state.USER_DB = load_json(USER_DB_FILE, {
        #"teacher": {"password": "adminpass", "role": "admin", "groups": []}
    #})

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

# --- Login System ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        result = supabase.table("users").select("*").eq("username", username).execute()
        users = result.data
        if users and users[0]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = users[0]["role"]
            st.session_state.user_groups = users[0].get("groups", [])
        else:
            st.error("Invalid login.")

    if st.button("Sign Up"):
        st.session_state.mode = "signup"
        st.rerun()

    if st.button("Reset Password"):
        st.session_state.mode = "reset"
        st.rerun()

elif not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    groups = st.multiselect("Select Your Classes", CLASS_GROUPS)

    if st.button("Create"):
        existing = supabase.table("users").select("username").eq("username", new_user).execute().data
        if existing:
            st.error("Username already exists.")
        else:
            supabase.table("users").insert({
                "username": new_user,
                "password": new_pass,
                "role": "student",
                "groups": groups
            }).execute()
            st.success("Account created! Please log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back"):
        st.session_state.mode = "login"
        st.rerun()

elif not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    user = st.text_input("Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Reset"):
        result = supabase.table("users").select("*").eq("username", user).execute().data
        if result:
            supabase.table("users").update({"password": new_pass}).eq("username", user).execute()
            st.success("Password reset.")
            st.session_state.mode = "login"
            st.rerun()
        else:
            st.error("User not found.")

    if st.button("Back"):
        st.session_state.mode = "login"
        st.rerun()

# --- Main App ---
elif st.session_state.logged_in:
    user = st.session_state.username
    user_info = st.session_state.USER_DB[user]
    is_teacher = user_info["role"] == "admin"
    st.sidebar.title(f"Hello, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if is_teacher:
        # TEACHER DASHBOARD
        st.title("Teacher Dashboard")

        tabs = st.tabs([
            "Create Templates",
            "All Templates",
            "Student Goals + Comments",
            "Class Resources"
        ])

        with tabs[0]:
            st.subheader("Create Goal Template")
            with st.form("template_form"):
                text = st.text_input("Goal Text")
                cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
                assign = st.multiselect("Assign to Groups", CLASS_GROUPS)
                if st.form_submit_button("Add") and text:
                    templates.append({
                        "id": str(uuid.uuid4()),
                        "text": text,
                        "category": cat,
                        "groups": assign
                    })
                    save_json(TEMPLATES_FILE, templates)
                    st.success("Template added.")

        with tabs[1]:
            st.subheader("All Templates")
            for i, t in enumerate(templates):
                st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(t['groups'])}")
                if st.button(f"Delete Template {i+1}", key=f"del_template_{i}"):
                    del templates[i]
                    save_json(TEMPLATES_FILE, templates)
                    st.success("Template deleted.")
                    st.experimental_rerun()

        with tabs[2]:
            st.subheader("Student Goals + Comments")
            if user_goals:
                selected_student = st.selectbox("Select a student", list(user_goals.keys()))
                student_goals = user_goals.get(selected_student, [])

                st.markdown(f"### {selected_student}")
                for g in student_goals:
                    st.markdown(f"**{g['text']}** ({g['category']}) — due {g['target_date']}")
                    created = datetime.date.fromisoformat(g.get("created_on", g["target_date"]))
                    target = datetime.date.fromisoformat(g["target_date"])
                    total_days = (target - created).days or 1
                    elapsed_days = (datetime.date.today() - created).days
                    progress = min(max(elapsed_days / total_days, 0), 1.0)
                    st.progress(progress)
                    st.caption(f"{int(progress * 100)}% complete — due {g['target_date']}")
                    comment_key = f"comment_{selected_student}_{g['id']}"
                    new_comment = st.text_input("Comment", value=g.get("comment", ""), key=comment_key)
                    if new_comment != g.get("comment", ""):
                        g["comment"] = new_comment
                        save_json(GOALS_FILE, user_goals)
            else:
                st.info("No student goals available.")

        with tabs[3]:
            st.subheader("Upload Class Resource Videos")

            teacher_videos_file = "teacher_videos.json"
            teacher_videos = load_json(teacher_videos_file, [])

            # Upload section
            video_label = st.text_input("Video Label")
            video_class = st.selectbox("Assign to Class", CLASS_GROUPS)
            uploaded = st.file_uploader("Select a video to upload", type=["mp4", "mov"])

            if uploaded and video_label and video_class:
                if st.button("Upload Video"):
                    filename = f"{uuid.uuid4().hex}_{uploaded.name}"
                    filepath = os.path.join(CLASS_VIDEO_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(uploaded.getbuffer())

                    video_entry = {
                        "label": video_label,
                        "class": video_class,
                        "filename": filepath,
                        "uploaded": str(datetime.datetime.now())
                    }
                    teacher_videos.append(video_entry)
                    save_json(teacher_videos_file, teacher_videos)
                    st.success("Video uploaded successfully.")

            # Viewing section
            st.markdown("### Class Video Library")
            selected_class = st.selectbox("Filter by Class", CLASS_GROUPS)
            filtered_videos = [v for v in teacher_videos if v["class"] == selected_class]

            if not filtered_videos:
                st.info("No videos uploaded for this class.")
            else:
                for i, v in enumerate(filtered_videos):
                    st.markdown(f"**{v['label']}** — uploaded {v['uploaded']}")
                    if os.path.exists(v["filename"]):
                        st.video(v["filename"])
                        if st.button(f"Delete {v['label']}", key=f"del_teacher_video_{i}"):
                            try:
                                os.remove(v["filename"])
                            except:
                                pass
                            teacher_videos.remove(v)
                            save_json(teacher_videos_file, teacher_videos)
                            st.success(f"Deleted {v['label']}")
                            st.experimental_rerun()
                    else:
                        st.warning("File not found.")

# Student dashboard goes here...

    else:
        # STUDENT DASHBOARD
        st.title("My Dashboard")
        tabs = st.tabs([
            "My Goals",
            "Templates for Me",
            "Upload Videos",
            "Today's Goals",
            "My Progress",
            "Class Resources"
        ])

        goals = user_goals.get(user, [])
        streak = user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        badges = user_badges.get(user, [])

        with tabs[0]:
            st.subheader("My Active Goals")
            with st.form("add_goal"):
                g_text = st.text_input("New Goal")
                g_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
                g_date = st.date_input("Target Date", datetime.date.today())
                if st.form_submit_button("Add") and g_text:
                    goals.append({
                        "id": str(uuid.uuid4()),
                        "text": g_text,
                        "category": g_cat,
                        "target_date": str(g_date),
                        "done": False,
                        "videos": [],
                        "created_on": str(datetime.date.today())
                    })
                    user_goals[user] = goals
                    save_json(GOALS_FILE, user_goals)

            for g in goals:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
                    if "comment" in g:
                        st.markdown(f"_Teacher Comment:_ {g['comment']}")
                    created = datetime.date.fromisoformat(g.get("created_on", g["target_date"]))
                    target = datetime.date.fromisoformat(g["target_date"])
                    total_days = (target - created).days or 1
                    elapsed_days = (datetime.date.today() - created).days
                    progress = min(max(elapsed_days / total_days, 0), 1.0)
                    st.progress(progress)
                    st.caption(f"{int(progress * 100)}% complete — due {g['target_date']}")
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

        with tabs[1]:
            st.subheader("Templates for You")
            my_groups = user_info.get("groups", [])
            my_templates = [t for t in templates if any(g in my_groups for g in t.get("groups", []))]
            for t in my_templates:
                with st.expander(f"{t['text']} ({t['category']})"):
                    with st.form(f"form_{t['id']}"):
                        goal_date = st.date_input("Target Date", datetime.date.today())
                        submitted = st.form_submit_button("Add to My Goals")
                        if submitted:
                            goals.append({
                                "id": str(uuid.uuid4()),
                                "text": t['text'],
                                "category": t['category'],
                                "target_date": str(goal_date),
                                "done": False,
                                "videos": [],
                                "created_on": str(datetime.date.today())
                            })
                            user_goals[user] = goals
                            save_json(GOALS_FILE, user_goals)

        with tabs[2]:
            st.subheader("Upload Progress Videos")
            for g in goals:
                st.markdown(f"### {g['text']}")
                video_label = st.text_input("Label for new video", key=f"label_{g['id']}")
                uploaded = st.file_uploader("Select a video", type=["mp4", "mov"], key=f"upload_{g['id']}")
                if uploaded and video_label:
                    if st.button("Upload Video", key=f"submit_upload_{g['id']}"):
                        vid_filename = f"{g['id']}_{uuid.uuid4().hex}_{uploaded.name}"
                        video_path = os.path.join("videos", vid_filename)
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
                    for i, v in enumerate(g["videos"]):
                        video_file = v["filename"]
                        label = v.get("label", f"Video {i+1}")
                        if os.path.exists(video_file):
                            st.markdown(f"**{label}** — Uploaded: {v['uploaded']}")
                            st.video(video_file)

        with tabs[3]:
            st.subheader("Today's Goals")
            today = datetime.date.today().isoformat()
            todays_goals = [g for g in goals if g["target_date"] == today and not g["done"]]
            if not todays_goals:
                st.info("No goals due today — you're all caught up!")
            else:
                for g in todays_goals:
                    st.markdown(f"- **{g['text']}** — {g['category']}")

        with tabs[4]:
            st.subheader("My Progress Overview")
            last_week = datetime.date.today() - datetime.timedelta(days=7)
            completed_goals = [
                g for g in goals
                if g.get("done") and g.get("completed_on") and
                datetime.date.fromisoformat(g["completed_on"]) >= last_week
            ]
            if completed_goals:
                st.markdown("### Goals Completed This Week")
                for g in completed_goals:
                    st.markdown(f"- **{g['text']}** ({g['category']}) — completed on {g['completed_on']}")
            else:
                st.info("No goals completed this week.")
            st.markdown("### Streak Status")
            st.markdown(f"**Current Streak:** {streak['streak']} day(s)")
            st.markdown("### Badges Earned")
            if badges:
                for b in badges:
                    st.markdown(f"{BADGE_EMOJIS.get(b, '')} {b}")
            else:
                st.caption("No badges yet — keep going!")

            with tabs[5]:
                st.subheader("Class Resources from Teacher")

                teacher_videos_file = "teacher_videos.json"
                teacher_videos = load_json(teacher_videos_file, [])
                my_groups = user_info.get("groups", [])

                available_videos = [v for v in teacher_videos if v["class"] in my_groups]

                if not available_videos:
                    st.info("No videos uploaded yet for your classes.")
                else:
                    for i, v in enumerate(available_videos):
                        st.markdown(f"**{v['label']}** — {v['class']} — uploaded {v['uploaded']}")
                        if os.path.exists(v["filename"]):
                            st.video(v["filename"])
                        else:
                            st.warning("Video file missing.")
