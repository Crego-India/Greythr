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

# ===== LOAD =====
def load_data():
    with open(FILE, "r") as f:
        return json.load(f)

def save_to_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {"Authorization": f"token {TOKEN}"}

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

# ===== LOAD DATA =====
data = load_data()

st.set_page_config(page_title="Attendance Dashboard", layout="wide")

# ===== HEADER =====
col1, col2 = st.columns([4, 1])

with col1:
    st.title("📊 Attendance Dashboard")

months = list(data["months"].keys())

# Month names
month_map = {
    m: datetime.strptime(m, "%Y-%m").strftime("%B")
    for m in months
}

with col2:
    selected_name = st.selectbox("", [month_map[m] for m in months[::-1]])

selected_month = [k for k, v in month_map.items() if v == selected_name][0]
month_data = data["months"][selected_month]

holidays = month_data.get("holidays", [])
leaves = month_data.get("leaves", [])

# ===== POPUP CONTROL =====
with st.expander("⚙️ Manage Holidays & Leaves"):
    col1, col2 = st.columns(2)

    with col1:
        new_holiday = st.date_input("Add Holiday")
        if st.button("➕ Add Holiday"):
            d = new_holiday.strftime("%Y-%m-%d")
            if d not in holidays:
                holidays.append(d)
                month_data["holidays"] = holidays
                save_to_github(data)
                st.success("Holiday added")

    with col2:
        new_leave = st.date_input("Add Leave")
        if st.button("➕ Add Leave"):
            d = new_leave.strftime("%Y-%m-%d")
            if d not in leaves:
                leaves.append(d)
                month_data["leaves"] = leaves
                save_to_github(data)
                st.success("Leave added")

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

    return working_days * 9, working_days

target, working_days = get_target()
total_hours = month_data.get("total_hours", 0)
remaining = max(target - total_hours, 0)
progress = min(total_hours / target, 1.0)

# ===== METRICS =====
c1, c2, c3, c4 = st.columns(4)

c1.metric("📊 Total", round(total_hours, 2))
c2.metric("🎯 Target", target)
c3.metric("⏳ Remaining", round(remaining, 2))
c4.metric("📅 Working Days", working_days)

# ===== PROGRESS BAR =====
st.progress(progress)
st.write(f"📈 {round(progress*100,2)}% completed")

# ===== TABLE =====
# ===== TABLE =====
rows = []

for date, d in month_data["days"].items():
    dt = datetime.strptime(date, "%Y-%m-%d")

    status = "Working"
    if date in holidays:
        status = "Holiday"
    elif date in leaves:
        status = "Leave"

    rows.append({
        "Date": dt.strftime("%d/%m"),
        "Status": status,

        # MORNING
        "M-In": d.get("morning", {}).get("in", ""),
        "M-Out": d.get("morning", {}).get("out", ""),
        "M-Hours": d.get("morning", {}).get("hours", 0),

        # AFTERNOON
        "A-In": d.get("afternoon", {}).get("in", ""),
        "A-Out": d.get("afternoon", {}).get("out", ""),
        "A-Hours": d.get("afternoon", {}).get("hours", 0),

        # TOTAL
        "Total": d.get("Total Hours", 0)
    })

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values(by="Date")

st.subheader("📊 Daily Logs")
st.dataframe(df, use_container_width=True)

# ===== CHART =====
st.subheader("📈 Daily Hours")
if not df.empty:
    st.line_chart(df.set_index("Date")["Total Hours"])

# ===== WEEKLY =====
st.subheader("📅 Weekly Breakdown")
if not df.empty:
    df["Week"] = pd.to_datetime(df["Date"], format="%d/%m").dt.isocalendar().week
    weekly = df.groupby("Week")["Total Hours"].sum()
    st.bar_chart(weekly)

# ===== SMART INSIGHTS =====
st.subheader("🧠 Smart Insights")

if total_hours > 0:
    avg = total_hours / working_days if working_days else 0
    st.write(f"📌 Avg/day: **{round(avg,2)} hrs**")

    remaining_days = max(1, working_days - len(df))
    needed = remaining / remaining_days

    if needed > 9:
        st.error(f"⚠️ Need {round(needed,2)} hrs/day (high!)")
    elif needed < 6:
        st.success("✅ You are ahead")
    else:
        st.info(f"👉 Maintain ~{round(needed,2)} hrs/day")
