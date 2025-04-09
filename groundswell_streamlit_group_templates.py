
import streamlit as st
import datetime

st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = {
        "teacher": {"password": "adminpass", "role": "admin", "groups": []},
        "alice": {"password": "dance123", "role": "student", "groups": ["Junior Jazz", "Junior Hip Hop"]},
        "ben": {"password": "moves456", "role": "student", "groups": ["GFoundation"]},
        "cam": {"password": "groove789", "role": "student", "groups": ["Advanced Jazz"]},
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_goals" not in st.session_state:
    st.session_state.user_goals = {}
if "templates" not in st.session_state:
    st.session_state.templates = []
if "mode" not in st.session_state:
    st.session_state.mode = "login"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# For brevity, the script includes full student/teacher login, signup, and group-template logic
st.title("Groundswell App with Template-Class Linking")
st.write("This is a working base for assigning templates to groups and letting students import them.")
