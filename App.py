import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Groundswell Login", layout="centered")

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_groups" not in st.session_state:
    st.session_state.user_groups = []
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if not st.session_state.logged_in:
    st.title("Groundswell Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user = auth_response.user
            session = auth_response.session

            if user and session:
                st.session_state.logged_in = True
                st.session_state.username = user.email
                st.session_state.user_id = user.id

                profile = supabase.table("profiles").select("*").eq("id", user.id).execute().data
                if profile:
                    st.session_state.user_role = profile[0].get("role", "student")
                    st.session_state.user_groups = profile[0].get("groups", [])
                else:
                    st.session_state.user_role = "student"
                    st.session_state.user_groups = []

                st.success("Logged in successfully! Choose your dashboard in the sidebar.")
                st.rerun()
            else:
                st.error("Invalid login credentials.")
        except Exception as e:
            st.error(f"Login failed: {e}")

    if st.button("Sign Up"):
        st.write("Please use the signup page on our website or contact your teacher for an account.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    st.sidebar.info("Select a page from the sidebar!")
