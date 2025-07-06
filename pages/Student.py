import streamlit as st
from utils import logout, supabase, update_user_profile
import uuid
from datetime import date, timedelta, datetime

if not st.session_state.get("logged_in") or st.session_state.get("user_role") != "student":
    st.error("Access denied.")
    st.stop()

st.title("🏆 Student Dashboard")
st.sidebar.button("Logout", on_click=logout)

tabs = st.tabs(["My Profile", "My Goals", "Templates", "Progress"])

with tabs[0]:
    st.subheader("Profile")
    profile_data = supabase.table("profiles").select("*").eq("id", st.session_state.user_id).execute().data[0]
    display_name = st.text_input("Display Name", value=profile_data.get("username", ""))
    groups = st.multiselect("Groups", ["Jazz", "Contemporary", "Hip Hop", "Ballet", "Tap"], default=profile_data.get("groups", []))

    if st.button("Save Profile"):
        update_user_profile(st.session_state.user_id, display_name, groups)
        st.success("Profile updated.")

with tabs[1]:
    st.subheader("My Goals")
    goals = supabase.table("goals").select("*").eq("username", st.session_state.username).execute().data

    with st.form("Add Goal"):
        g_text = st.text_input("Goal Text")
        g_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        g_date = st.date_input("Target Date", date.today())
        if st.form_submit_button("Add"):
            new_goal = {
                "id": str(uuid.uuid4()),
                "username": st.session_state.username,
                "text": g_text,
                "category": g_cat,
                "target_date": str(g_date),
                "done": False,
                "created_on": str(date.today())
            }
            supabase.table("goals").insert(new_goal).execute()
            st.success("Goal added.")
            st.rerun()

    for g in goals:
        st.markdown(f"**{g['text']}** ({g['category']}) — Target: {g['target_date']}")
        if st.checkbox("Done", value=g["done"], key=g["id"]):
            supabase.table("goals").update({"done": True}).eq("id", g["id"]).execute()
            st.rerun()

with tabs[2]:
    st.subheader("Templates for You")
    profile_data = supabase.table("profiles").select("*").eq("id", st.session_state.user_id).execute().data[0]
    groups = profile_data.get("groups", [])

    templates = supabase.table("templates").select("*").execute().data
    my_templates = [t for t in templates if any(group in t["groups"] for group in groups)]

    for t in my_templates:
        with st.expander(f"{t['text']} ({t['category']})"):
            if st.button("Add to My Goals", key=f"add_{t['id']}"):
                new_goal = {
                    "id": str(uuid.uuid4()),
                    "username": st.session_state.username,
                    "text": t["text"],
                    "category": t["category"],
                    "target_date": str(date.today() + timedelta(days=7)),
                    "done": False,
                    "created_on": str(date.today())
                }
                supabase.table("goals").insert(new_goal).execute()
                st.success("Goal added.")

with tabs[3]:
    st.subheader("My Progress")
    goals = supabase.table("goals").select("*").eq("username", st.session_state.username).execute().data
    completed = [g for g in goals if g["done"]]
    st.markdown(f"**Total Completed:** {len(completed)}")

    for g in completed:
        st.markdown(f"- {g['text']} ({g['category']}) ✅")
