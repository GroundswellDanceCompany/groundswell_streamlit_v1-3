import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_id = ""
    st.session_state.user_role = ""
    st.session_state.user_groups = []
    st.session_state.mode = "login"
    supabase.auth.sign_out()
    st.rerun()

def update_user_profile(user_id, display_name, groups, role=None):
    update_data = {
        "username": display_name,
        "groups": groups
    }
    if role:
        update_data["role"] = role
    supabase.table("profiles").update(update_data).eq("id", user_id).execute()
