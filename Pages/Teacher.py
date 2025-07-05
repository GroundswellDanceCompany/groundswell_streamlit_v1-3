import streamlit as st
from utils import logout, supabase
import uuid
import ast

if not st.session_state.get("logged_in") or st.session_state.get("user_role") != "admin":
    st.error("Access denied.")
    st.stop()

st.title("📚 Teacher Dashboard")
st.sidebar.button("Logout", on_click=logout)

tabs = st.tabs(["Create Templates", "All Templates", "Student Goals", "Upload Class Videos"])

with tabs[0]:
    st.subheader("Create Goal Template")
    text = st.text_input("Goal Text")
    cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
    groups = st.multiselect("Assign to Groups", ["Jazz", "Contemporary", "Hip Hop", "Ballet", "Tap"])

    if st.button("Add Template"):
        try:
            supabase.table("templates").insert({
                "id": str(uuid.uuid4()),
                "text": text,
                "category": cat,
                "groups": groups
            }).execute()
            st.success("Template added.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

with tabs[1]:
    st.subheader("All Templates")
    templates = supabase.table("templates").select("*").execute().data
    for i, t in enumerate(templates):
        group_list = ast.literal_eval(t.get("groups", "[]")) if isinstance(t.get("groups"), str) else t.get("groups", [])
        st.markdown(f"**{t['text']}** ({t['category']}) → {', '.join(group_list)}")
        if st.button(f"Delete {t['text']}", key=f"del_{i}"):
            supabase.table("templates").delete().eq("id", t["id"]).execute()
            st.success("Deleted.")
            st.rerun()

with tabs[2]:
    st.subheader("Student Goals + Comments")
    goals = supabase.table("goals").select("*").execute().data
    for g in goals:
        with st.expander(f"{g['username']} - {g['text']}"):
            st.write(f"Category: {g['category']}")
            st.write(f"Target Date: {g['target_date']}")
            comment = st.text_area("Teacher Comment", value=g.get("comment", ""), key=f"comm_{g['id']}")
            if st.button("Save Comment", key=f"save_{g['id']}"):
                supabase.table("goals").update({"comment": comment}).eq("id", g["id"]).execute()
                st.success("Comment saved.")
                st.rerun()

with tabs[3]:
    st.subheader("Upload Class Videos")
    label = st.text_input("Video Label")
    video_class = st.selectbox("Class", ["Jazz", "Contemporary", "Hip Hop", "Ballet", "Tap"])
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov"])

    if uploaded_file and st.button("Upload Video"):
        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        filepath = f"teacher_videos/{filename}"
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        supabase.table("teacher_videos").insert({
            "label": label,
            "class": video_class,
            "filename": filepath,
            "uploaded": st.session_state.username
        }).execute()
        st.success("Video uploaded and saved metadata.")
