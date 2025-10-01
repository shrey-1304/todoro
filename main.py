import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# ------------------------------
# File paths
# ------------------------------
TASKS_FILE = "tasks.csv"
HISTORY_FILE = "history.csv"
USERS_FILE = "users.csv"

# ------------------------------
# Load users
# ------------------------------
if os.path.exists(USERS_FILE):
    users_df = pd.read_csv(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=["Username", "Email", "Password"])

# ------------------------------
# Authentication
# ------------------------------
if "username" not in st.session_state:
    st.title("📝 Productivity App Login")
    st.markdown("<i>*Enter your credentials to continue*</i>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab2:
        st.subheader("Create a new account")
        new_username = st.text_input("Username", key="signup_username")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            if new_username and new_email and new_password:
                if new_username in users_df["Username"].values:
                    st.error("Username already exists! Pick another one.")
                else:
                    users_df = pd.concat([users_df, pd.DataFrame([{
                        "Username": new_username,
                        "Email": new_email,
                        "Password": new_password
                    }])], ignore_index=True)
                    users_df.to_csv(USERS_FILE, index=False)
                    st.success("Account created! You can now log in.")
            else:
                st.warning("Fill in all fields!")

    with tab1:
        st.subheader("Login to your account")
        username_input = st.text_input("Username", key="login_username")
        password_input = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username_input and password_input:
                user_row = users_df[(users_df["Username"]==username_input) & (users_df["Password"]==password_input)]
                if not user_row.empty:
                    st.session_state.username = username_input
                    st.session_state.update_flag = not st.session_state.get("update_flag", False)
                else:
                    st.error("Invalid username or password!")
            else:
                st.warning("Enter both username and password!")
    st.stop()

# ------------------------------
# Main app (user is logged in)
# ------------------------------
st.set_page_config(page_title="Productivity App", page_icon="⏱️", layout="centered")
st.title("📝 Productivity App")
st.markdown(f"<i>Welcome, {st.session_state.username}! Focus, Organize, Achieve, Repeat, Grow</i>", unsafe_allow_html=True)

# ------------------------------
# Load tasks and history
# ------------------------------
tasks_df = pd.read_csv(TASKS_FILE) if os.path.exists(TASKS_FILE) else pd.DataFrame(columns=["Task", "Completed"])
history_df = pd.read_csv(HISTORY_FILE) if os.path.exists(HISTORY_FILE) else pd.DataFrame(columns=["Timestamp", "Completed Tasks", "Pending Tasks"])

# ------------------------------
# Tasks Section
# ------------------------------
st.markdown("### 📋 Tasks")
new_task = st.text_input("Quick-add task", key="task_input")
if st.button("Add Task"):
    if new_task:
        tasks_df = pd.concat([tasks_df, pd.DataFrame([{"Task": new_task, "Completed": False}])], ignore_index=True)
        tasks_df.to_csv(TASKS_FILE, index=False)
        st.session_state.update_flag = not st.session_state.get("update_flag", False)

for i, row in tasks_df.iterrows():
    col1, col2, col3 = st.columns([4,1,1])
    col1.write(f"{i+1}. {row['Task']} {'✅' if row['Completed'] else ''}")
    if col2.button("Complete", key=f"c{i}"):
        tasks_df.at[i,"Completed"] = True
        tasks_df.to_csv(TASKS_FILE, index=False)
        st.session_state.update_flag = not st.session_state.get("update_flag", False)
    if col3.button("Delete", key=f"d{i}"):
        tasks_df = tasks_df.drop(i).reset_index(drop=True)
        tasks_df.to_csv(TASKS_FILE, index=False)
        st.session_state.update_flag = not st.session_state.get("update_flag", False)

# ------------------------------
# Pomodoro Timer Section
# ------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("### 🍅 Focus Mode - Pomodoro Timer")

incomplete_tasks = tasks_df[tasks_df["Completed"]==False]["Task"].tolist()
if incomplete_tasks:
    focus_task = st.selectbox("Select a task to focus on", incomplete_tasks, key="focus_task")
    if focus_task:
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "remaining_time" not in st.session_state:
            st.session_state.remaining_time = 25*60
        if "current_task" not in st.session_state:
            st.session_state.current_task = None
        if "total_time" not in st.session_state:
            st.session_state.total_time = 25*60

        minutes, seconds = divmod(st.session_state.remaining_time, 60)
        timer_placeholder = st.empty()
        timer_placeholder.markdown(f"⏳ {minutes:02d}:{seconds:02d} remaining")
        progress = st.progress(int(((st.session_state.total_time - st.session_state.remaining_time)/st.session_state.total_time)*100))

        col1b, col2b, col3b = st.columns(3)
        with col1b:
            if st.button("▶️ Start"):
                st.session_state.timer_running = True
                st.session_state.current_task = focus_task
                st.session_state.total_time = st.session_state.remaining_time
        with col2b:
            if st.button("⏸️ Pause"):
                st.session_state.timer_running = False
        with col3b:
            if st.button("⏹️ Reset"):
                st.session_state.timer_running = False
                st.session_state.remaining_time = 25*60
                st.session_state.total_time = 25*60
                st.session_state.current_task = None

        if st.session_state.timer_running and st.session_state.remaining_time>0:
            time.sleep(1)
            st.session_state.remaining_time -=1
            st.session_state.update_flag = not st.session_state.get("update_flag", False)

        if st.session_state.remaining_time==0 and st.session_state.timer_running:
            st.success("✅ Time's up!")
            st.session_state.timer_running = False
            tasks_df.loc[tasks_df["Task"]==st.session_state.current_task,"Completed"]=True
            tasks_df.to_csv(TASKS_FILE,index=False)
            st.balloons()
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Productivity History
# ------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("### 📊 Productivity History")

if st.button("Save Session Progress"):
    completed_count = tasks_df["Completed"].sum()
    pending_count = len(tasks_df)-completed_count
    new_history = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Completed Tasks": completed_count,
        "Pending Tasks": pending_count
    }])
    history_df = pd.concat([history_df,new_history],ignore_index=True)
    history_df.to_csv(HISTORY_FILE,index=False)
    st.session_state.update_flag = not st.session_state.get("update_flag", False)
    st.success("Session saved!")

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True)
    st.write(f"Total Sessions: {len(history_df)}")
    st.write(f"Total Completed Tasks: {history_df['Completed Tasks'].sum()}")
else:
    st.write("No session history yet. Start focusing to track your productivity!")

st.markdown('</div>', unsafe_allow_html=True)
