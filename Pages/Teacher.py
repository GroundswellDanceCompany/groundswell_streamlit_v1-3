import streamlit as st
from supabase import create_client
import uuid
import ast
from utils import logout

# --- Load connection
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Constants
CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

# --- Check login
if not st.session_state.get("logged_in"):
    st.error("Please log in first.")
    st.stop()

# --- Check teacher/admin role
if st.session_state.get("user_role") not in ["admin", "teacher"]:
    st.error("You do not have access to this page.")
    st.stop()

st.sidebar.title(f"Hello, {st.session_state.username}")
st.sidebar.button("Logout", on_click=logout)

st.title("📚 Teacher Dashboard")

tabs = st.tabs([
    "Create Templates",
    "All Templates",
    "Student Goals + Comments",
    "Class Resources",
    "My Profile"
])

# --- Create Templates tab
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
                    "groups": assign
                }).execute()
                st.success("Template added.")
                st.rerun()
            except Exception as e:
                st.error(f"Template save failed: {e}")

# --- All Templates tab
with tabs[1]:
    st.subheader("All Templates")
    templates = supabase.table("templates").select("*").execute().data
    for i, t in enumerate(templates):
        try:
            group_list = ast.literal_eval(t.get("groups", "[]"))
        except:
            group_list = t.get("groups", [])
        st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(group_list)}")
        if st.button(f"Delete Template {i+1}", key=f"del_template_{i}"):
            try:
                supabase.table("templates").delete().eq("id", t["id"]).execute()
                st.success("Template deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")

# --- Student Goals + Comments tab
with tabs[2]:
    st.subheader("Student Goals + Comments")
    students = supabase.table("goals").select("*").order("created_on", desc=True).limit(50).execute().data

    if not students:
        st.info("No goals found yet.")
    else:
        for g in students:
            with st.expander(f"{g['username']} — {g['text']} ({g['category']})"):
                st.write(f"**Target Date:** {g['target_date']}")
                st.write(f"**Completed:** {'✅' if g.get('done') else '❌'}")
                st.write(f"**Expired:** {'⚠️' if g.get('expired') else '—'}")
                st.write(f"**Student Comment:** {g.get('comment', 'None')}")

                new_comment = st.text_area("Add or update teacher comment", key=f"tc_{g['id']}")
                if st.button("Save Comment", key=f"sc_{g['id']}"):
                    supabase.table("goals").update({"comment": new_comment}).eq("id", g["id"]).execute()
                    st.success("Comment saved.")
                    st.rerun()

# --- Class Resources tab
with tabs[3]:
    st.subheader("Upload Class Resource Videos")
    video_label = st.text_input("Video Label")
    video_class = st.selectbox("Assign to Class", CLASS_GROUPS)
    uploaded = st.file_uploader("Select a video", type=["mp4", "mov"])

    if uploaded and video_label and video_class:
        if st.button("Upload Video"):
            filename = f"{uuid.uuid4().hex}_{uploaded.name}"
            filepath = os.path.join("teacher_videos", filename)
            with open(filepath, "wb") as f:
                f.write(uploaded.getbuffer())

            supabase.table("teacher_videos").insert({
                "label": video_label,
                "class": video_class,
                "filename": filepath,
                "uploaded": str(datetime.now()),
                "username": st.session_state.username
            }).execute()
            st.success("Video uploaded successfully.")
            st.rerun()

    st.markdown("### Class Video Library")
    selected_class = st.selectbox("Filter by Class", CLASS_GROUPS, key="view_class_teacher")
    videos = supabase.table("teacher_videos").select("*").eq("class", selected_class).execute().data

    if not videos:
        st.info("No videos uploaded for this class.")
    else:
        for v in videos:
            st.markdown(f"**{v['label']}** — uploaded {v['uploaded']}")
            if os.path.exists(v["filename"]):
                st.video(v["filename"])
            else:
                st.warning("Video file missing.")

# --- My Profile tab
with tabs[4]:
    st.subheader("My Profile")
    st.markdown(f"**Email:** `{st.session_state.username}`")
    st.markdown(f"**Role:** `{st.session_state.user_role}`")
    st.markdown(f"**Groups:** `{st.session_state.user_groups}`")
    st.success("✅ You are in Teacher mode.")
