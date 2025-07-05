
import streamlit as st
from supabase import create_client, Client

# --- Setup Supabase ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialize session state keys ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_groups" not in st.session_state:
    st.session_state.user_groups = []
if "mode" not in st.session_state:
    st.session_state.mode = "login"

# --- Logout function ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_id = ""
    st.session_state.user_role = ""
    st.session_state.user_groups = []
    st.session_state.mode = "login"
    supabase.auth.sign_out()
    st.rerun()

# --- Login Page ---
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

                # Fetch profile
                profile_data = supabase.table("profiles").select("*").eq("id", user.id).execute().data
                if profile_data:
                    st.session_state.user_role = profile_data[0].get("role", "student")
                    st.session_state.user_groups = profile_data[0].get("groups", [])
                else:
                    st.session_state.user_role = "student"
                    st.session_state.user_groups = []

                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid email or password.")

        except Exception as e:
            st.error(f"Login failed: {e}")

    if st.button("Sign Up"):
        st.switch_page("pages/Signup.py")

    if st.button("Reset Password"):
        st.switch_page("pages/ResetPassword.py")

else:
    st.success(f"Logged in as {st.session_state.username}")
    st.markdown(f"**Role:** `{st.session_state.user_role}`")
    st.markdown(f"**Groups:** `{', '.join(st.session_state.user_groups)}`")

    if st.session_state.user_role == "admin":
        st.markdown("### ✅ You are in Teacher mode.")
    else:
        st.markdown("### 🏆 You are in Student mode.")

    if st.button("Logout"):
        logout()
        
 
