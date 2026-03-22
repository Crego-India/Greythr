import streamlit as st
import json
import pandas as pd
from datetime import datetime
import calendar
import requests
import base64

FILE = "hours.json"

# ===== GITHUB CONFIG =====
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

# ===== LOAD DATA =====
def load_data():
    with open(FILE, "r") as f:
        return json.load(f)

def save_to_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"token {TOKEN}"
    }

    # Get SHA
    res = requests.get(url, headers=headers)
    sha = res.json()["sha"]

    content = base64.b64encode(
        json.dumps(data, indent=2).encode()
    ).decode()

    payload = {
        "message": "update holidays/leaves",
        "content": content,
        "sha": sha
    }

    requests.put(url, headers=headers, json=payload)

# ===== MAIN =====
data = load_data()

st.title("📊 Attendance Dashboard")

months = list(data["months"].keys())
selected_month = st.selectbox("Select Month", months[::-1])

month_data = data["months"][selected_month]

holidays = month_data.get("holidays", [])
leaves = month_data.get("leaves", [])

# ===== ADD CONTROLS =====
st.subheader("⚙️ Manage Holidays & Leaves")

col1, col2 = st.columns(2)

with col1:
    new_holiday = st.date_input("Add Holiday")
    if st.button("Add Holiday"):
        date_str = new_holiday.strftime("%Y-%m-%d")
        if date_str not in holidays:
            holidays.append(date_str)
            month_data["holidays"] = holidays
            save_to_github(data)
            st.success("Holiday added")

with col2:
    new_leave = st.date_input("Add Leave")
    if st.button("Add Leave"):
        date_str = new_leave.strftime("%Y-%m-%d")
        if date_str not in leaves:
            leaves.append(date_str)
            month_data["leaves"] = leaves
            save_to_github(data)
            st.success("Leave added")

# ===== DISPLAY =====
st.write("### Holidays:", holidays)
st.write("### Leaves:", leaves)

# ===== TARGET =====
def get_target():
    year, month = map(int, selected_month.split("-"))
    cal = calendar.monthcalendar(year, month)

    working_days = 0

    for week in cal:
        for i, day in enumerate(week):
            date_str = f"{selected_month}-{str(day).zfill(2)}"
            if day != 0 and i != 6 and date_str not in holidays:
                working_days += 1

    return working_days * 9

target = get_target()
total = month_data.get("total_hours", 0)

st.metric("Total Hours", total)
st.metric("Target", target)
st.metric("Remaining", target - total)

# ===== TABLE =====
rows = []
for d, val in month_data["days"].items():
    rows.append({
        "Date": d,
        "Total": val.get("total", 0)
    })

df = pd.DataFrame(rows)
st.dataframe(df)

# ===== CHART =====
if not df.empty:
    st.line_chart(df.set_index("Date")["Total"])
