import streamlit as st
from supabase import create_client, Client

# --- Setup Supabase ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Create New Account")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Create Account"):
    try:
        # Sign up with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        user = auth_response.user

        if user:
            # Insert initial profile (optional)
            supabase.table("profiles").insert({
                "id": user.id,
                "username": email,
                "groups": [],
                "role": "student"  # default role
            }).execute()

            st.success("Account created! Please check your email to verify, then log in.")
            st.switch_page("Home.py")
        else:
            st.error("Signup failed. No user returned.")

    except Exception as e:
        st.error(f"Signup failed: {e}")

if st.button("Back to Login"):
    st.switch_page("Home.py")
