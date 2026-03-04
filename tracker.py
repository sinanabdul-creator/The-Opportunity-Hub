import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="The Opportunity Hub", layout="wide", page_icon="🎯")
st.title("🎯 The Opportunity Hub")
st.markdown("Track your Scholarships and Job Applications. Keep an eye on those deadlines and follow-up intervals!")

# --- 2. FILE PATHS ---
SCHOLAR_FILE = "scholarships.csv"
JOB_FILE = "jobs.csv"

# --- 3. HELPER FUNCTIONS ---
def calculate_days_left(deadline):
    """Calculates days remaining until a deadline."""
    if pd.isna(deadline):
        return None
    if isinstance(deadline, str):
        try:
            deadline = pd.to_datetime(deadline).date()
        except Exception:
            return None
    elif isinstance(deadline, pd.Timestamp):
        deadline = deadline.date()
        
    delta = deadline - date.today()
    return delta.days

def calculate_follow_up_status(last_contact, interval_days):
    """Determines if a follow-up is due based on the interval."""
    if pd.isna(last_contact) or pd.isna(interval_days):
        return "Missing Info"
    
    if isinstance(last_contact, str):
        try:
            last_contact = pd.to_datetime(last_contact).date()
        except Exception:
            return "Invalid Date"
    elif isinstance(last_contact, pd.Timestamp):
        last_contact = last_contact.date()
        
    next_follow_up = last_contact + timedelta(days=int(interval_days))
    days_until_followup = (next_follow_up - date.today()).days
    
    if days_until_followup < 0:
        return f"🚨 OVERDUE by {abs(days_until_followup)} days"
    elif days_until_followup == 0:
        return "⚠️ Due Today!"
    else:
        return f"Wait {days_until_followup} days"

def load_data(filepath, default_data, date_cols):
    """Loads data from CSV or returns default data if no CSV exists."""
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        return df
    return pd.DataFrame(default_data)

# --- 4. DEFAULT DATA (Used only on the very first run) ---
default_scholarships = {
    "Scholarship Name": ["Example Scholarship"],
    "Provider": ["XYZ Foundation"],
    "Value": ["$5,000"],
    "Deadline": [date.today() + timedelta(days=14)],
    "Requirements": ["Essay, 2 References"],
    "Status": ["In Progress"],
    "Last Contact Date": [date.today() - timedelta(days=3)],
    "Follow-up Interval (Days)": [7]
}

default_jobs = {
    "Role & Company": ["Data Analyst - TechCorp"],
    "Job Link": ["https://example.com"],
    "Resume Version": ["Standard Tech v2"],
    "Referral/Contact": ["Jane Doe (LinkedIn)"],
    "Interview Stage": ["Phone Screen"],
    "Last Contact Date": [date.today() - timedelta(days=5)],
    "Follow-up Interval (Days)": [7]
}

# --- 5. INITIALIZE DATA ---
if "scholarships" not in st.session_state:
    st.session_state.scholarships = load_data(SCHOLAR_FILE, default_scholarships, ["Deadline", "Last Contact Date"])

if "jobs" not in st.session_state:
    st.session_state.jobs = load_data(JOB_FILE, default_jobs, ["Last Contact Date"])

# --- 6. UI LAYOUT & LOGIC ---
tab1, tab2 = st.tabs(["🎓 Scholarships", "💼 Job Applications"])

# === TAB 1: SCHOLARSHIPS ===
with tab1:
    st.header("Scholarship Tracker")
    st.markdown("Focus: **Deadlines, Requirements, & Admin Follow-ups**")
    
    edited_scholars = st.data_editor(
        st.session_state.scholarships,
        num_rows="dynamic",
        column_config={
            "Deadline": st.column_config.DateColumn("Deadline", format="YYYY-MM-DD"),
            "Last Contact Date": st.column_config.DateColumn("Last Contact Date", format="YYYY-MM-DD"),
            "Follow-up Interval (Days)": st.column_config.NumberColumn("Follow-up Interval (Days)", min_value=1, max_value=60, step=1),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Not Started", "In Progress", "References Requested", "Submitted", "Awarded", "Rejected"]
            )
        },
        key="scholar_editor"
    )
    
    st.session_state.scholarships = edited_scholars
    edited_scholars.to_csv(SCHOLAR_FILE, index=False)
    
    st.subheader("⏳ Scholarship Radar")
    df_scholars = st.session_state.scholarships.copy()
    df_scholars["Days to Deadline"] = df_scholars["Deadline"].apply(calculate_days_left)
    df_scholars["Follow-up Action"] = df_scholars.apply(
        lambda row: calculate_follow_up_status(row["Last Contact Date"], row["Follow-up Interval (Days)"]), axis=1
    )
    st.dataframe(df_scholars[["Scholarship Name", "Deadline", "Days to Deadline", "Follow-up Action", "Status"]], use_container_width=True)

# === TAB 2: JOB APPLICATIONS ===
with tab2:
    st.header("Job Application Tracker")
    st.markdown("Focus: **Networking & Follow-up Intervals**")
    
    edited_jobs = st.data_editor(
        st.session_state.jobs,
        num_rows="dynamic",
        column_config={
            "Last Contact Date": st.column_config.DateColumn("Last Contact Date", format="YYYY-MM-DD"),
            "Follow-up Interval (Days)": st.column_config.NumberColumn("Follow-up Interval (Days)", min_value=1, max_value=60, step=1),
            "Interview Stage": st.column_config.SelectboxColumn(
                "Interview Stage",
                options=["Applied", "Phone Screen", "Tech Round", "Final", "Offer", "Rejected"]
            )
        },
        key="job_editor"
    )
    
    st.session_state.jobs = edited_jobs
    edited_jobs.to_csv(JOB_FILE, index=False)
    
    st.subheader("🔔 Follow-Up Radar")
    df_jobs = st.session_state.jobs.copy()
    df_jobs["Follow-up Action"] = df_jobs.apply(
        lambda row: calculate_follow_up_status(row["Last Contact Date"], row["Follow-up Interval (Days)"]), axis=1
    )
    st.dataframe(df_jobs[["Role & Company", "Referral/Contact", "Interview Stage", "Follow-up Action"]], use_container_width=True)