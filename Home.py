import streamlit as st
from supabase import create_client, Client
import requests

st.set_page_config(page_title="Groundswell Login", layout="centered")

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "mode" not in st.session_state:
    st.session_state.mode = "login"

st.title("Groundswell Login")

if st.session_state.mode == "login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
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

                st.success("Login successful! Choose your dashboard in the sidebar.")
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
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        try:
            auth_response = supabase.auth.sign_up({"email": email, "password": password})
            user = auth_response.user
            if user:
                supabase.table("profiles").insert({
                    "id": user.id,
                    "username": email,
                    "groups": [],
                    "role": "student"
                }).execute()
                st.success("Check your email to verify, then log in.")
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
    email = st.text_input("Enter your email to reset password")

    if st.button("Send Reset Email"):
        RESET_ENDPOINT = f"{SUPABASE_URL}/auth/v1/recover"
        headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
        response = requests.post(RESET_ENDPOINT, json={"email": email}, headers=headers)
        if response.status_code == 200:
            st.success("Password reset email sent.")
            st.session_state.mode = "login"
        else:
            st.error("Could not send reset email.")

    if st.button("Back"):
        st.session_state.mode = "login"
        st.rerun()
