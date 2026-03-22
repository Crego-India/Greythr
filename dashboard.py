import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
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
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Get latest SHA
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        st.error("❌ Failed to fetch file from GitHub")
        return

    sha = res.json()["sha"]

    content = base64.b64encode(
        json.dumps(data, indent=2).encode()
    ).decode()

    payload = {
        "message": "update holidays/leaves",
        "content": content,
        "sha": sha
    }

    update = requests.put(url, headers=headers, json=payload)

    if update.status_code == 200:
        st.success("✅ Saved to GitHub")
    else:
        st.error(f"❌ GitHub update failed: {update.text}")

# ===== HEADER =====
col1, col2 = st.columns([4, 1])

with col1:
    st.title("📊 Attendance Dashboard")

months = list(data["months"].keys())

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

# ===== MANAGE HOLIDAYS / LEAVES =====
with st.expander("⚙️ Manage Holidays & Leaves"):
    c1, c2 = st.columns(2)

    with c1:
        h = st.date_input("Add Holiday")
        if st.button("➕ Add Holiday"):
            d = h.strftime("%Y-%m-%d")
            if d not in holidays:
                holidays.append(d)
                month_data["holidays"] = holidays
                save_to_github(data)
                st.success("Holiday added")

    with c2:
        l = st.date_input("Add Leave")
        if st.button("➕ Add Leave"):
            d = l.strftime("%Y-%m-%d")
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

# ===== REMAINING DAYS (FIXED LOGIC) =====
def get_remaining_days(selected_month, holidays):
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    today = now.date()

    year, month = map(int, selected_month.split("-"))
    cal = calendar.monthcalendar(year, month)

    remaining_days = 0

    for week in cal:
        for i, day in enumerate(week):

            if day == 0:
                continue

            d = datetime(year, month, day).date()
            date_str = d.strftime("%Y-%m-%d")

            if (
                d > today and          # exclude today
                i != 6 and             # exclude Sunday
                date_str not in holidays
            ):
                remaining_days += 1

    return max(1, remaining_days)

remaining_days = get_remaining_days(selected_month, holidays)

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
        "M-In": d.get("morning", {}).get("in", ""),
        "M-Out": d.get("morning", {}).get("out", ""),
        "M-Hours": d.get("morning", {}).get("hours", 0),
        "A-In": d.get("afternoon", {}).get("in", ""),
        "A-Out": d.get("afternoon", {}).get("out", ""),
        "A-Hours": d.get("afternoon", {}).get("hours", 0),
        "Total": d.get("total", 0)
    })

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values(by="Date")

# ===== METRICS =====
c1, c2, c3, c4 = st.columns(4)

c1.metric("📊 Total", round(total_hours, 2))
c2.metric("🎯 Target", target)
c3.metric("⏳ Remaining", round(remaining, 2))
c4.metric("📅 Working Days", working_days)

# ===== PROGRESS =====
st.progress(progress)
st.write(f"📈 {round(progress*100,2)}% completed")

# ===== DAILY TABLE =====
st.subheader("📊 Daily Logs")
st.dataframe(df, use_container_width=True)

# ===== CHART =====
st.subheader("📈 Daily Hours")
if "Total" in df.columns:
    st.line_chart(df.set_index("Date")["Total"])

# ===== WEEKLY =====
st.subheader("📅 Weekly Breakdown")
if not df.empty:
    df["Week"] = pd.to_datetime(df["Date"], format="%d/%m").dt.isocalendar().week
    weekly = df.groupby("Week")["Total"].sum()
    st.bar_chart(weekly)

# ===== SMART INSIGHTS =====
st.subheader("🧠 Smart Insights")

if total_hours > 0:

    # AVG (correct)
    actual_days = len(df)
    avg = total_hours / actual_days if actual_days else 0
    st.write(f"📌 Avg/day: **{round(avg,2)} hrs**")

    # 9 hour mode
    needed_9 = remaining / remaining_days

    st.write("### 🎯 Based on 9 hrs/day target")
    if needed_9 > 9:
        st.error(f"⚠️ Need **{round(needed_9,2)} hrs/day** (high pressure)")
    elif needed_9 < 6:
        st.success(f"✅ You are ahead ({round(needed_9,2)} hrs/day enough)")
    else:
        st.info(f"👉 Maintain **{round(needed_9,2)} hrs/day**")

    # 8 hour mode
    relaxed_target = working_days * 8
    relaxed_remaining = max(relaxed_target - total_hours, 0)
    needed_8 = relaxed_remaining / remaining_days

    st.write("### 😌 Based on 8 hrs/day (comfortable pace)")
    if needed_8 > 8:
        st.warning(f"⚠️ Need **{round(needed_8,2)} hrs/day**")
    elif needed_8 < 6:
        st.success(f"✅ Relaxed ({round(needed_8,2)} hrs/day enough)")
    else:
        st.info(f"👉 Maintain **{round(needed_8,2)} hrs/day**")
