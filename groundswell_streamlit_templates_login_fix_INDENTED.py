
import streamlit as st
import datetime

# MUST be first Streamlit command
st.set_page_config(page_title="Groundswell Goal Tracker", layout="centered")

# --- Class Groups ---
CLASS_GROUPS = [
    "GSD Youth", "Jenga", "GFoundation", "Junior Contemporary", "Intermediate Contemporary",
    "Junior Jazz", "Advanced Jazz", "Junior House", "Junior Hip Hop", "Advanced House",
    "Advanced Hip Hop", "Junior Waacking", "Junior Locking", "Advanced Waacking",
    "Advanced Locking", "Junior Ballet", "Intermediate Ballet", "Youth Contemporary Company",
    "Junior Contemporary Company", "Youth Jazz Company", "Junior Jazz Company", "Tap Class"
]

# --- Session Defaults ---
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = {
        "teacher": {"password": "adminpass", "role": "admin", "groups": []},
        "alice": {"password": "dance123", "role": "student", "groups": ["Junior Jazz"]},
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

# --- Logout ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- Password Reset Page ---
if not st.session_state.logged_in and st.session_state.mode == "reset":
    st.title("Reset Password")
    username = st.text_input("Enter your username")
    new_password = st.text_input("Enter a new password", type="password")

    if st.button("Reset Password"):
        if username in st.session_state.USER_DB:
            if username.lower() == "teacher":
                st.error("Teacher password can only be reset by admin.")
            else:
                st.session_state.USER_DB[username]["password"] = new_password
                st.success("Password updated! You can now log in.")
                st.session_state.mode = "login"
                st.rerun()
        else:
            st.error("Username not found.")

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()



# --- Sign Up Page ---
if not st.session_state.logged_in and st.session_state.mode == "signup":
    st.title("Create Student Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    groups = st.multiselect("Select your class/groups", CLASS_GROUPS)

    if st.button("Create Account"):
       if not new_user or not new_pass or not groups:
       st.warning("Please fill in all fields.")
    elif new_user in st.session_state.USER_DB:
       st.error("Username already exists.")
    elif new_user.lower() == "teacher":
       st.error("This username is reserved.")
       else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student",
                "groups": groups
            }
            if "user_goals" not in st.session_state:
                st.session_state.user_goals = {}
            st.session_state.user_goals[new_user] = []
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()

        elif new_user in st.session_state.USER_DB:
            st.error("Username already exists.")
        elif new_user.lower() == "teacher":
            st.error("This username is reserved.")
        else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student",
                "groups": groups
            }
            if "user_goals" not in st.session_state:
                st.session_state.user_goals = {}
            st.session_state.user_goals[new_user] = []
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()
        elif new_user in st.session_state.USER_DB:
            st.error("Username already exists.")
        elif new_user.lower() == "teacher":
            st.error("This username is reserved.")
        else:
            st.session_state.USER_DB[new_user] = {
                "password": new_pass,
                "role": "student",
                "groups": groups
            }
            st.session_state.user_goals[new_user] = []
            st.success("Account created! You can now log in.")
            st.session_state.mode = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.mode = "login"
        st.rerun()
    st.stop()

# --- Login Page ---
if not st.session_state.logged_in and st.session_state.mode == "login":
    st.title("Groundswell Goal Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = st.session_state.USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            if username not in st.session_state.user_goals:
                st.session_state.user_goals[username] = []
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("---")
    if st.button("Create Student Account"):
        st.session_state.mode = "signup"
        st.rerun()
    if st.button("Forgot Password?"):
        st.session_state.mode = "reset"
        st.rerun()

    st.info("Teachers: log in using your assigned credentials.")
    st.stop()

# --- Sidebar Info ---
username = st.session_state.username
role = st.session_state.USER_DB[username]["role"]
st.sidebar.markdown(f"**Logged in as:** `{username}` ({role})")
if st.sidebar.button("Logout"):
    logout()

# --- Student View ---
if role == "student":
    groups = st.session_state.USER_DB[username].get("groups", [])
    st.title(f"Welcome, {username.capitalize()}")
    st.caption(f"Your classes: {', '.join(groups)}")
    goals = st.session_state.user_goals[username]

    st.subheader("Your Goals")
    with st.form("add_goal"):
        text = st.text_input("Goal Description")
        category = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        date = st.date_input("Target Date", datetime.date.today())
        if st.form_submit_button("Add Goal") and text:
            goals.append({
                "text": text,
                "category": category,
                "target_date": date,
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Goal added.")
            st.rerun()

    for i, g in enumerate(goals):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"**{g['text']}** ({g['category']}) - {g['target_date']:%b %d}")
        if col2.button("✅" if g["status"] == "Done" else "Done", key=f"done_{i}"):
            g["status"] = "Done" if g["status"] != "Done" else "Not Started"
            g["completed_on"] = datetime.date.today() if g["status"] == "Done" else None
            st.rerun()
        if col3.button("Delete", key=f"del_{i}"):
            goals.pop(i)
            st.rerun()

    
    
    st.subheader("Templates for Your Classes")
    relevant = sorted(
        [t for t in st.session_state.templates if set(t.get("groups", [])) & set(groups)],
        key=lambda x: datetime.datetime.strptime(x['target_date'], '%Y-%m-%d')
    )
    for i, t in enumerate(relevant):
        group_tags = []
        for gname in t['groups']:
            if gname in groups:
                group_tags.append(f"<span style='color:red'><b>{gname}</b></span>")
            else:
                group_tags.append(gname)
        group_display = ', '.join(group_tags)

        st.markdown(f"- 📌 **{t['text']}** ({t['category']}) — Due: {t['target_date']}<br/>Groups: {group_display}", unsafe_allow_html=True)
        if st.button("Import to My Goals", key=f"import_{i}_{t['text'][:8].replace(' ', '')}_{t['target_date']}"):
            st.session_state.user_goals[username].append({
                "text": f"📌 {t['text']}",
                "category": t['category'],
                "target_date": datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date(),
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template imported!")
            st.rerun()
            if gname in groups:
                group_tags.append(f"<span style='color:red'><b>{gname}</b></span>")
            else:
                group_tags.append(gname)
        group_display = ', '.join(group_tags)

        st.markdown(f"- **{t['text']}** ({t['category']}) — Due: {t['target_date']}<br/>Groups: {group_display}", unsafe_allow_html=True)
        if st.button("Import to My Goals", key=f"import_{i}_{t['text'][:8].replace(' ', '')}_{t['target_date']}"):
            st.session_state.user_goals[username].append({
                "text": f"[TEMPLATE] {t['text']}",
                "category": t['category'],
                "target_date": datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date(),
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template imported!")
            st.rerun()
            st.session_state.user_goals[username].append({
                "text": f"[TEMPLATE] {t['text']}",
                "category": t['category'],
                "target_date": datetime.datetime.strptime(t['target_date'], "%Y-%m-%d").date(),
                "status": "Not Started",
                "created_on": datetime.date.today(),
                "completed_on": None
            })
            st.success("Template imported!")
            st.rerun()

# --- Teacher View ---
if role == "admin":
    st.title("Teacher Dashboard")
    st.subheader("Create Templates by Group")
    with st.form("template_form"):
        text = st.text_input("Template Text")
        cat = st.selectbox("Category", ["Technique", "Strength", "Flexibility", "Performance"])
        date = st.date_input("Target Date", datetime.date.today())
        groups = st.multiselect("Assign to Groups", CLASS_GROUPS)
        if st.form_submit_button("Add Template") and text and groups:
            st.session_state.templates.append({
                "text": text,
                "category": cat,
                "target_date": date.strftime("%Y-%m-%d"),
                "groups": groups
            })
            st.success("Template added.")
            st.rerun()

    st.subheader("Templates")
    for i, t in enumerate(st.session_state.templates):
        st.markdown(f"- **{t['text']}** ({t['category']}) — {t['target_date']} — Groups: {', '.join(t['groups'])}")
        if st.button("Delete", key=f"del_temp_{i}"):
            st.session_state.templates.pop(i)
            st.rerun()

    st.subheader("Students by Group")
    selected = st.selectbox("Select Group", CLASS_GROUPS)
    students = [u for u, d in st.session_state.USER_DB.items() if d["role"] == "student" and selected in d.get("groups", [])]
    for s in students:
        st.markdown(f"### {s.capitalize()}")
        for g in st.session_state.user_goals.get(s, []):
            st.markdown(f"- {'✅' if g['status'] == 'Done' else '⬜️'} {g['text']} ({g['category']}) – Due: {g['target_date']:%b %d}")
