import streamlit as st
from supabase import create_client
import uuid
from datetime import datetime
import ast

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if st.session_state.get("user_role") not in ["teacher", "admin"]:
    st.error("You do not have access to this page.")
    st.stop()

st.title("📚 Teacher Dashboard")
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

tabs = st.tabs([
    "Create Templates",
    "All Templates",
    "Student Goals + Comments",
    "Class Resources"
])

CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

with tabs[0]:
    st.subheader("Create Goal Template")
    with st.form("template_form"):
        text = st.text_input("Goal Text")
        cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        assign = st.multiselect("Assign to Groups", CLASS_GROUPS)
        if st.form_submit_button("Add") and text:
            supabase.table("templates").insert({
                "id": str(uuid.uuid4()),
                "text": text,
                "category": cat,
                "groups": assign
            }).execute()
            st.success("Template added!")
            st.experimental_rerun()

with tabs[1]:
    st.subheader("All Templates")
    templates = supabase.table("templates").select("*").execute().data
    for i, t in enumerate(templates):
        group_list = ast.literal_eval(t.get("groups", "[]")) if isinstance(t.get("groups"), str) else t.get("groups", [])
        st.markdown(f"- **{t['text']}** ({t['category']}) → {', '.join(group_list)}")
        if st.button(f"Delete Template {i+1}", key=f"del_{i}"):
            supabase.table("templates").delete().eq("id", t["id"]).execute()
            st.success("Template deleted.")
            st.experimental_rerun()

with tabs[2]:
    st.subheader("Student Goals + Comments")
    students = supabase.table("goals").select("*").order("created_on", desc=True).limit(50).execute().data

    if not students:
        st.info("No student goals yet.")
    else:
        for g in students:
            with st.expander(f"{g['username']} — {g['text']} ({g['category']})"):
                st.write(f"**Target Date:** {g['target_date']}")
                st.write(f"**Completed:** {'✅' if g.get('done') else '❌'}")
                comment = st.text_area("Add / update comment", value=g.get("comment", ""), key=f"comment_{g['id']}")
                if st.button("Save Comment", key=f"save_{g['id']}"):
                    supabase.table("goals").update({"comment": comment}).eq("id", g["id"]).execute()
                    st.success("Comment updated.")
                    st.experimental_rerun()

with tabs[3]:
    st.subheader("Class Resources Upload")
    label = st.text_input("Video Label")
    group = st.selectbox("Assign to Class", CLASS_GROUPS)
    uploaded = st.file_uploader("Upload Video", type=["mp4", "mov"])

    if uploaded and label and group:
        if st.button("Upload"):
            filename = f"{uuid.uuid4().hex}_{uploaded.name}"
            filepath = f"teacher_videos/{filename}"
            with open(filepath, "wb") as f:
                f.write(uploaded.getbuffer())

            supabase.table("teacher_videos").insert({
                "label": label,
                "class": group,
                "filename": filepath,
                "uploaded": datetime.now().isoformat(),
                "username": st.session_state.username
            }).execute()
            st.success("Video uploaded and saved!")
