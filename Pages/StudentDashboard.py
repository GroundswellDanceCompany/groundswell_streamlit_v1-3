import streamlit as st
from supabase import create_client
import uuid
from datetime import date, timedelta, datetime

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if st.session_state.get("user_role") != "student":
    st.error("You do not have access to this page.")
    st.stop()

st.title("🏆 Student Dashboard")
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

tabs = st.tabs(["My Goals", "Templates", "Profile"])

with tabs[0]:
    st.subheader("My Active Goals")
    user = st.session_state.username
    goals = supabase.table("goals").select("*").eq("username", user).execute().data

    today = date.today()

    with st.form("add_goal"):
        g_text = st.text_input("New Goal")
        g_cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        g_date = st.date_input("Target Date", today)
        if st.form_submit_button("Add") and g_text:
            new_goal = {
                "id": str(uuid.uuid4()),
                "username": user,
                "text": g_text,
                "category": g_cat,
                "target_date": str(g_date),
                "done": False,
                "created_on": str(today),
                "videos": []
            }
            supabase.table("goals").insert(new_goal).execute()
            st.success("Goal added.")
            st.experimental_rerun()

    for g in goals:
        if not g.get("done", False):
            st.markdown(f"**{g['text']}** — {g['category']} (due {g['target_date']})")
            if st.checkbox("Done", key=g["id"]):
                supabase.table("goals").update({"done": True}).eq("id", g["id"]).execute()
                st.success("Marked as done!")
                st.experimental_rerun()

with tabs[1]:
    st.subheader("Templates for You")
    templates = supabase.table("templates").select("*").execute().data
    my_groups = st.session_state.user_groups

    my_templates = [t for t in templates if any(g in my_groups for g in t.get("groups", []))]

    for t in my_templates:
        with st.expander(f"{t['text']} ({t['category']})"):
            goal_date = st.date_input("Target Date", date.today(), key=f"date_{t['id']}")
            if st.button("Add to My Goals", key=f"add_{t['id']}"):
                new_goal = {
                    "id": str(uuid.uuid4()),
                    "username": user,
                    "text": t["text"],
                    "category": t["category"],
                    "target_date": str(goal_date),
                    "done": False,
                    "created_on": str(date.today()),
                    "videos": []
                }
                supabase.table("goals").insert(new_goal).execute()
                st.success("Goal added.")
                st.experimental_rerun()

with tabs[2]:
    st.subheader("My Profile")
    profile = supabase.table("profiles").select("*").eq("id", st.session_state.user_id).execute().data
    profile_data = profile[0] if profile else {}

    st.markdown(f"**Email:** {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.user_role}")

    display_name = st.text_input("Display Name", value=profile_data.get("username", ""))
    updated_groups = st.multiselect("Select Your Classes", [
        "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
        "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
        "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
        "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
        "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
    ], default=st.session_state.user_groups)

    if st.button("Save Profile"):
        supabase.table("profiles").update({
            "username": display_name,
            "groups": updated_groups
        }).eq("id", st.session_state.user_id).execute()
        st.success("Profile updated successfully!")
        st.session_state.user_groups = updated_groups
