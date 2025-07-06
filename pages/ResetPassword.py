import streamlit as st
from supabase import create_client, Client
import requests

# --- Setup Supabase ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Reset Password")

user_email = st.text_input("Enter your email to reset password")

if st.button("Send Reset Email"):
    RESET_ENDPOINT = f"{SUPABASE_URL}/auth/v1/recover"
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        RESET_ENDPOINT,
        json={"email": user_email},
        headers=headers
    )

    if response.status_code == 200:
        st.success("Password reset email sent. Please check your inbox.")
        st.switch_page("Home.py")
    else:
        error_msg = response.json().get("msg", "Could not send reset email.")
        st.error(f"Error: {error_msg}")

if st.button("Back to Login"):
    st.switch_page("Home.py")
