
import streamlit as st
st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")
import uuid
import datetime
import json
import os
import ast
import io
import tempfile  


if "username" not in st.session_state:
    st.session_state.username = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"

from supabase import create_client, Client

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- File Paths ---
#USER_DB_FILE = "user_db# JSON filename removed (Supabase used)"
GOALS_FILE = "user_goals# JSON filename removed (Supabase used)"
TEMPLATES_FILE = "templates# JSON filename removed (Supabase used)"
STREAKS_FILE = "user_streaks# JSON filename removed (Supabase used)"
BADGES_FILE = "user_badges# JSON filename removed (Supabase used)"
VIDEO_DIR = "videos"
CLASS_VIDEO_DIR = "teacher_videos"

# --- Setup ---
for folder in [VIDEO_DIR, CLASS_VIDEO_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def parse_groups(template):
    try:
        return ast.literal_eval(template.get("groups", "[]"))  # safely convert string to list
    except:
        return []


if "username" in st.session_state:
    # Load goals
    all_goals = supabase.table("goals").select("*").execute().data

else:
    user_goals = []
    
templates = supabase.table("templates") \
    .select("*") \
    .execute().data
if st.session_state.logged_in:
    # Safe to use st.session_state.username here
    streak_rows = supabase.table("streaks") \
        .select("*") \
        .eq("username", st.session_state.username) \
        .execute().data
    user_streaks = {st.session_state.username: streak_rows[0] if streak_rows else {"streak": 0, "last_completion_date": ""}}
if st.session_state.logged_in:
    # Safe to use st.session_state.username here
    badge_rows = supabase.table("badges") \
        .select("*") \
        .eq("username", st.session_state.username) \
        .execute().data
    user_badges = {st.session_state.username: badge_rows[0]["earned"] if badge_rows else []}

def check_and_award_badges(username, goals, streak_data):
    earned = user_badges.get(username, [])
    done_goals = [g for g in goals if g.get("done")]
    categories = set(g["category"] for g in done_goals)

    if len(done_goals) >= 1 and "First Goal Completed" not in earned:
        earned.append("First Goal Completed")
        st.success("🏁 Badge Unlocked: First Goal Completed!")

    if len(done_goals) >= 5 and "Goal Getter: 5 Goals Done" not in earned:
        earned.append("Goal Getter: 5 Goals Done")
        st.success("⭐ Badge Unlocked: Goal Getter!")

    if all(cat in categories for cat in ["Technique", "Strength", "Flexibility", "Performance"]) \
            and "Well-Rounded: All Categories" not in earned:
        earned.append("Well-Rounded: All Categories")
        st.success("🌈 Badge Unlocked: Well-Rounded!")

    if streak_data.get("streak", 0) >= 3 and "Streak Star: 3-Day Streak" not in earned:
        earned.append("Streak Star: 3-Day Streak")
        st.success("🔥 Badge Unlocked: Streak Star!")

    # Update in memory
    user_badges[username] = earned

    # Save to Supabase
    supabase.table("badges").upsert({
        "username": username,
        "earned": earned
    }).execute()

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
    "First Goal Completed": "ð",
    "Goal Getter: 5 Goals Done": "â­",
    "Well-Rounded: All Categories": "ð",
    "Streak Star: 3-Day Streak": "ð¥"
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
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": username,
                "password": password
            })

            user = auth_response.user
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.email
                st.session_state.user_id = user.id  # <- This is the UUID you use in tables
            else:
                st.error("Invalid login credentials.")
        except Exception as e:
            st.error(f"Login failed: {e}")
            
    #if st.button("Login"):
        #result = supabase.table("users").select("*").eq("username", username).execute()
        #users = result.data
        #if users and users[0]["password"] == password:
            #st.session_state.logged_in = True
            #st.session_state.username = username
            #st.session_state.user_role = users[0]["role"]
            #st.session_state.user_groups = users[0].get("groups", [])
        #else:
            #st.error("Invalid login.")

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
if st.session_state.get("logged_in"):
    user = st.session_state.get("username")
    role = st.session_state.get("user_role")

    st.sidebar.title(f"Hello, {user}")
    st.sidebar.button("Logout", on_click=logout)

    if role in ["teacher", "admin"]:
        # Show teacher view
        st.title("Teacher Dashboard")

        tabs = st.tabs([
            "Create Templates",
            "All Templates",
            "Student Goals + Comments",
            "Class Resources" ])

        with tabs[0]:
            st.subheader("Create Goal Template")
            with st.form("template_form"):
                text = st.text_input("Goal Text")
                cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
                assign = st.multiselect("Assign to Groups", CLASS_GROUPS)
                if st.form_submit_button("Add") and text:
                    try:
                        supabase.table("templates").insert({
                            "id": str(uuid.uuid4()),
                            "text": text,
                            "category": cat,
                            "groups": assign  # now works because the column exists and is text[]
                        }).execute()
                        st.success("Template added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Template save failed: {e}")

        with tabs[1]:
            st.subheader("All Templates")
            for i, t in enumerate(templates):
                try:
                    group_list = ast.literal_eval(t.get("groups", "[]"))
                except:
                    group_list = t.get("groups", [])
                st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(group_list)}")
                if st.button(f"Delete Template {i+1}", key=f"del_template_{i}"):
                    try:
                        response = supabase.table("templates").delete().eq("id", t["id"]).execute()
                        st.success("Template deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")    

        
        with tabs[2]:
            st.subheader("Student Goals + Comments")

            # Collect unique usernames
            student_usernames = sorted(list(set([g["username"] for g in all_goals])))

            selected_student = st.selectbox("Select a student", student_usernames)
            student_goals = [g for g in all_goals if g["username"] == selected_student]

            for g in student_goals:
                st.markdown(f"**{g['text']}** ({g['category']}) — due {g['target_date']}")
                created = datetime.date.fromisoformat(g.get("created_on", g["target_date"]).split("T")[0])
                target = datetime.date.fromisoformat(g["target_date"].split("T")[0])
                total_days = (target - created).days or 1
                elapsed_days = (datetime.date.today() - created).days
                progress = min(max(elapsed_days / total_days, 0), 1.0)
                st.progress(progress)
                st.caption(f"{int(progress * 100)}% complete — due {g['target_date']}")

                comment_key = f"comment_{selected_student}_{g['id']}"
                new_comment = st.text_input("Comment", value=g.get("comment", ""), key=comment_key)

                if new_comment != g.get("comment", ""):
                    try:
                        supabase.table("goals").update({"comment": new_comment}).eq("id", g["id"]).execute()
                        st.success("Comment saved.")
                    except Exception as e:
                        st.error(f"Failed to save comment: {e}")

        
        
        with tabs[3]:
            st.subheader("Upload Class Resource Videos")

            # Upload Section
            video_label = st.text_input("Video Label")
            video_class = st.selectbox("Assign to Class", CLASS_GROUPS)
            uploaded = st.file_uploader("Select a video", type=["mp4", "mov"])

            if uploaded and video_label and video_class:
                if st.button("Upload Video"):
                    filename = f"{uuid.uuid4().hex}_{uploaded.name}"
                    filepath = os.path.join("teacher_videos", filename)
                    with open(filepath, "wb") as f:
                        f.write(uploaded.getbuffer())

                    # Store metadata in Supabase table
                    supabase.table("teacher_videos").insert({
                        "label": video_label,
                        "class": video_class,
                        "filename": filepath,
                        "uploaded": str(datetime.datetime.now()),
                        "username": st.session_state.username
                    }).execute()
                    st.success("Video uploaded successfully.")

            # View Section
            st.markdown("### Class Video Library")
            selected_class = st.selectbox("Filter by Class", CLASS_GROUPS, key="view_class")
            response = supabase.table("teacher_videos").select("*").eq("class", selected_class).execute()
            teacher_videos = response.data

            if not teacher_videos:
                st.info("No videos uploaded for this class.")
            else:
                for v in teacher_videos:
                    st.markdown(f"**{v['label']}** — uploaded {v['uploaded']}")
                    if os.path.exists(v["filename"]):
                        st.video(v["filename"])
                    else:
                        st.warning("Video file missing.")

# Student dashboard goes here...

    else:
        # STUDENT DASHBOARD
        st.title("My Dashboard")
        tabs = st.tabs([
            "About",
            "My Goals",
            "Templates for Me",
            "Upload Videos",
            "Today's Goals",
            "My Progress",
            "Class Resources",
            "Youtube"
        ])

        user_goals = [g for g in all_goals if g["username"] == st.session_state.username]
        goals = user_goals  # already a list of goals for this user
        streak = user_streaks.get(user, {"streak": 0, "last_completion_date": ""})
        badges = user_badges.get(user, [])

        with tabs[0]:
            st.subheader("About the Groundswell Goal Tracker")

            st.markdown("""
            Welcome to the **Groundswell Goal Tracker** â your personal space to set, track, and celebrate your dance training progress.

            **What you can do here:**
            - Set goals in areas like Technique, Strength, Flexibility, and Performance
            - Upload progress videos to track your journey
            - Complete goals and earn badges
            - View class resources uploaded by your teachers

            **Badges are awarded for:**
            - Completing your first goal
            - Finishing 5 goals
            - Completing at least one goal in all 4 categories
            - Building a 3-day streak of goal completion

            **Tips:**
            - Use the âToday's Goalsâ tab to stay focused on deadlines
            - Check âClass Resourcesâ for helpful videos from your teachers
            - Be consistent â small steps lead to big progress!

            _This platform is built for the Groundswell Dance community â letâs grow together._
            """)

        with tabs[1]:
            st.subheader("My Active Goals")
            with st.form("add_goal"):
                g_text = st.text_input("New Goal")
                g_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
                g_date = st.date_input("Target Date", datetime.date.today())
                # Filter for current student's goals
                

                if st.form_submit_button("Add") and g_text:
                    try:
                        new_goal = {
                            "id": str(uuid.uuid4()),
                            "username": st.session_state.username,  # <- important!
                            "text": g_text,
                            "category": g_cat,
                            "target_date": str(g_date),
                            "done": False,
                            "created_on": str(datetime.date.today()),
                            "videos": []
                        }
                        supabase.table("goals").insert(new_goal).execute()
                    
                    except Exception as e:
                        st.error(f"Insert failed: {e}")
                        st.stop()

                    # Insert into Supabase
                    

                    # Refresh goals
                    goals = supabase.table("goals").select("*") \
                        .eq("username", st.session_state.username).execute().data

            for g in goals:
                if not g.get("done", False):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
                        if "comment" in g:
                            st.markdown(f"_Teacher Comment:_ {g['comment']}")
                        created = datetime.datetime.fromisoformat(
                            g.get("created_on", g["target_date"])
                        ).date()
                        target = datetime.datetime.fromisoformat(g["target_date"]).date()
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
                                # save_json removed (Supabase used)(GOALS_FILE, user_goals)
                                # save_json removed (Supabase used)(STREAKS_FILE, user_streaks)
                                check_and_award_badges(user, goals, streak)

            done_goals = [g for g in goals if g["done"]]
            if done_goals:
                with st.expander("View Completed Goals"):
                    for g in done_goals:
                        st.markdown(f"- **{g['text']}** ({g['category']}) â Completed on {g.get('completed_on', 'N/A')}")

        
        with tabs[2]:
            st.subheader("Templates for You")
            my_groups = st.session_state.user_groups

            my_templates = [
                t for t in templates
                if any(group in my_groups for group in parse_groups(t))
            ]

            if not my_templates:
                st.info("No templates assigned to your classes yet.")
            else:
                for t in my_templates:
                    with st.expander(f"{t['text']} ({t['category']})"):
                        with st.form(f"form_{t['id']}"):
                            goal_date = st.date_input("Target Date", datetime.date.today())
                            submitted = st.form_submit_button("Add to My Goals")
                            if submitted:
                                new_goal = {
                                    "id": str(uuid.uuid4()),
                                    "username": st.session_state.username,
                                    "text": t["text"],
                                    "category": t["category"],
                                    "target_date": str(goal_date),
                                    "done": False,
                                    "created_on": str(datetime.date.today()),
                                    "videos": []
                                }
                                supabase.table("goals").insert(new_goal).execute()
                                st.success("Goal added.")
                            # save_json removed (Supabase used)(GOALS_FILE, user_goals)

        with tabs[3]:
            st.subheader("Upload Progress Videos")
            for g in goals:
                with st.expander(f"{g['text']} ({g['category']})"):
                    video_label = st.text_input("Label for new video", key=f"label_{g['id']}")
                    uploaded = st.file_uploader("Select a video", type=["mp4", "mov"], key=f"upload_{g['id']}")
                    if uploaded and video_label:
                        if st.button("Upload Video", key=f"submit_upload_{g['id']}"):
                            video_filename = f"{g['id']}_{uuid.uuid4().hex}_{uploaded.name}"
                            video_path = f"{st.session_state.username}/{video_filename}"

                            try:
                                supabase.storage.from_("studentvideos").upload(
                                    path=video_path,
                                    file=uploaded.getvalue(),
                                    file_options={"content-type": uploaded.type}
                                )

                                g.setdefault("videos", []).append({
                                    "filename": video_path,
                                    "label": video_label,
                                    "uploaded": str(datetime.datetime.now())
                                })

                                supabase.table("goals").update({"videos": g["videos"]}).eq("id", g["id"]).execute()
                                st.success(f"Video '{video_label}' uploaded.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Upload failed: {e}")

        with tabs[4]:
            st.subheader("Today's Goals")
            today = datetime.date.today().isoformat()
            todays_goals = [g for g in goals if g["target_date"] == today and not g["done"]]
            if not todays_goals:
                st.info("No goals due today â you're all caught up!")
            else:
                for g in todays_goals:
                    st.markdown(f"- **{g['text']}** â {g['category']}")

        with tabs[5]:
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
                    st.markdown(f"- **{g['text']}** ({g['category']}) â completed on {g['completed_on']}")
            else:
                st.info("No goals completed this week.")
            st.markdown("### Streak Status")
            st.markdown(f"**Current Streak:** {streak['streak']} day(s)")
            st.markdown("### Badges Earned")
            if badges:
                for b in badges:
                    st.markdown(f"{BADGE_EMOJIS.get(b, '')} {b}")
            else:
                st.caption("No badges yet â keep going!")
                
        
        with tabs[6]:
            st.subheader("Class Resources from Teacher")

            teacher_videos = supabase.table("teacher_videos").select("*").execute().data
            my_groups = st.session_state.user_groups

            if not teacher_videos:
                st.info("No teacher videos available yet.")
            else:
                keyword = st.text_input("Search by keyword (optional)", "")
                results = [
                    v for v in teacher_videos
                    if v["class"] in my_groups and keyword.lower() in v["label"].lower()
                ]

                if not results:
                    st.warning("No videos match your filters.")
                else:
                    for v in results:
                        with st.expander(f"{v['class']} – {v['label']}"):
                            st.caption(f"Uploaded: {v['uploaded']}")
                    
                            # Generate signed URL
                            try:
                                signed_url_resp = supabase.storage \
                                    .from_("teacher_videos") \
                                    .create_signed_url(v["filename"], expires_in=3600)
                                video_url = signed_url_resp.get("signedURL")

                                if video_url:
                                    st.video(video_url)
                                else:
                                    st.warning("Video not accessible.")
                            except Exception as e:
                                st.error(f"Error loading video: {e}")
                    

        with tabs[7]:
            st.subheader("Groundswell on YouTube")

            st.markdown("""
            Looking for more inspiration or full-length tutorials?

            - [Visit our YouTube Channel](https://www.youtube.com/@yourchannelname)
            - Watch new choreography, strength routines, and flexibility drills
            """)

            st.markdown("### Featured Video")
            st.video("https://youtu.be/6-R4oJkjY0s?feature=shared") # Replace with your video URL

            st.markdown("### Core Playlist")
            st.markdown("[Hip Hop Foundations](https://www.youtube.com/playlist?list=PLxyz123...)")
            

            

            

            

            
