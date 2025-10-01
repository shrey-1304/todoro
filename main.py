import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import os

st.set_page_config(page_title="Productivity App", page_icon="⏱️", layout="centered")
st.title("📝 Productivity App")
st.markdown("*Focus, Organize, Achieve, Repeat, Grow*")

# ------------------------------
# File paths for persistence
# ------------------------------
TASKS_FILE = "tasks.csv"
HISTORY_FILE = "history.csv"

# ------------------------------
# Load existing data
# ------------------------------
if os.path.exists(TASKS_FILE):
    tasks_df = pd.read_csv(TASKS_FILE)
else:
    tasks_df = pd.DataFrame(columns=["Task", "Completed"])

if os.path.exists(HISTORY_FILE):
    history_df = pd.read_csv(HISTORY_FILE)
else:
    history_df = pd.DataFrame(columns=["Timestamp", "Completed Tasks", "Pending Tasks"])

# ------------------------------
# 1️⃣ Welcome Screen
# ------------------------------
st.subheader("Enter your email to start")
email = st.text_input("Email")
if not email:
    st.stop()  # Stop app until email is entered
st.success(f"Welcome, {email}!")

# ------------------------------
# 2️⃣ Task Dashboard
# ------------------------------
st.subheader("📋 Your Tasks")

# Quick-add task
new_task = st.text_input("Quick-add task")
if st.button("Add Task") and new_task:
    tasks_df = pd.concat([tasks_df, pd.DataFrame([{"Task": new_task, "Completed": False}])], ignore_index=True)
    tasks_df.to_csv(TASKS_FILE, index=False)

# AI-simulated task generator
ai_tasks = [
    "Finish report on project X",
    "Organize workspace",
    "Plan tomorrow's schedule",
    "Review code for errors",
    "Respond to pending emails"
]
if st.button("Generate AI Task"):
    ai_task = random.choice(ai_tasks)
    tasks_df = pd.concat([tasks_df, pd.DataFrame([{"Task": ai_task, "Completed": False}])], ignore_index=True)
    tasks_df.to_csv(TASKS_FILE, index=False)

# Display tasks
for i, row in tasks_df.iterrows():
    col1, col2, col3 = st.columns([4, 1, 1])
    col1.write(f"{i+1}. {row['Task']} {'✅' if row['Completed'] else ''}")
    if col2.button("Complete", key=f"c{i}"):
        tasks_df.at[i, "Completed"] = True
        tasks_df.to_csv(TASKS_FILE, index=False)
    if col3.button("Delete", key=f"d{i}"):
        tasks_df = tasks_df.drop(i).reset_index(drop=True)
        tasks_df.to_csv(TASKS_FILE, index=False)

# ------------------------------
# 3️⃣ Focus Mode with Pomodoro
# ------------------------------
incomplete_tasks = tasks_df[tasks_df["Completed"] == False]["Task"].tolist()
if incomplete_tasks:
    focus_task = st.selectbox("Select a task to focus on", incomplete_tasks)
    if focus_task:
        st.subheader("🍅 Focus Mode - Pomodoro Timer")

        # Pomodoro settings
        WORK_MIN = 25
        BREAK_MIN = 5
        mode = st.selectbox("Mode", ["Work", "Break"])
        duration_sec = WORK_MIN*60 if mode == "Work" else BREAK_MIN*60

        if st.button("Start Timer"):
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=duration_sec)
            progress_placeholder = st.empty()
            timer_placeholder = st.empty()

            while datetime.now() < end_time:
                remaining = end_time - datetime.now()
                minutes, seconds = divmod(remaining.seconds, 60)
                percent = int(((duration_sec - remaining.seconds)/duration_sec)*100)
                progress_placeholder.progress(percent)
                timer_placeholder.markdown(f"⏳ {minutes:02d}:{seconds:02d} remaining")
                time.sleep(1)

            progress_placeholder.progress(100)
            timer_placeholder.markdown("✅ Time's up! Take a break or start next session")

            # Automatically mark task as complete
            tasks_df.loc[tasks_df["Task"] == focus_task, "Completed"] = True
            tasks_df.to_csv(TASKS_FILE, index=False)

# ------------------------------
# 4️⃣ Save Session Progress
# ------------------------------
if st.button("Save Session Progress"):
    completed_count = tasks_df["Completed"].sum()
    pending_count = len(tasks_df) - completed_count
    new_history = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Completed Tasks": completed_count,
        "Pending Tasks": pending_count
    }])
    history_df = pd.concat([history_df, new_history], ignore_index=True)
    history_df.to_csv(HISTORY_FILE, index=False)
    st.success("Session saved!")

# ------------------------------
# 5️⃣ Productivity History
# ------------------------------
st.subheader("📊 Productivity History")
if not history_df.empty:
    st.dataframe(history_df)
    st.write(f"Total Sessions: {len(history_df)}")
    st.write(f"Total Completed Tasks: {history_df['Completed Tasks'].sum()}")
else:
    st.write("No session history yet. Start focusing to track your productivity!")
