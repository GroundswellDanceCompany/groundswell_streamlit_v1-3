import streamlit as st
from supabase import create_client, Client
import requests
from utils import logout

st.set_page_config(page_title="Groundswell Login")

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "username" not in st.session_state:
    st.session_state.username = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"

if st.session_state.mode == "login":
    st.title("Login")
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

                st.rerun()
            else:
                st.error("Invalid login.")
        except Exception as e:
            st.error(f"Login failed: {e}")

    if st.button("Sign Up"):
        st.session_state.mode = "signup"
        st.rerun()

    if st.button("Reset Password"):
        st.session_state.mode = "reset"
        st.rerun()

elif st.session_state.mode == "signup":
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Create Account"):
        try:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            user = auth_response.user

            if user:
                supabase.table("profiles").insert({
                    "id": user.id,
                    "username": email,
                    "groups": [],
                    "role": "student"
                }).execute()

                st.success("Check your email to verify, then login.")
                st.session_state.mode = "login"
                st.rerun()
            else:
                st.error("Signup failed.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

    if st.button("Back"):
        st.session_state.mode = "login"
        st.rerun()

elif st.session_state.mode == "reset":
    st.title("Reset Password")
    user_email = st.text_input("Enter your email")

    if st.button("Send Reset Email"):
        RESET_ENDPOINT = f"{SUPABASE_URL}/auth/v1/recover"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(RESET_ENDPOINT, json={"email": user_email}, headers=headers)
        if response.status_code == 200:
            st.success("Reset email sent. Check your inbox.")
            st.session_state.mode = "login"
        else:
            st.error(f"Error: {response.json().get('msg', 'Could not send email.')}")

    if st.button("Back"):
        st.session_state.mode = "login"
        st.rerun()
