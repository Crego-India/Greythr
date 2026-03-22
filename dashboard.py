import streamlit as st
import json
import pandas as pd

FILE = "hours.json"

# ===== LOAD DATA =====
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"months": {}}

data = load_data()

st.set_page_config(page_title="Attendance Dashboard", layout="wide")

st.title("📊 Attendance Dashboard")

months = list(data.get("months", {}).keys())

if not months:
    st.warning("⚠️ No data available yet")
    st.stop()

# ===== MONTH SELECT =====
selected_month = st.selectbox(
    "📅 Select Month",
    sorted(months, reverse=True)
)

month_data = data["months"][selected_month]

# ===== PREPARE TABLE =====
rows = []

for date, d in month_data["days"].items():
    rows.append({
        "Date": date,
        "Morning In": d.get("morning", {}).get("in", ""),
        "Morning Out": d.get("morning", {}).get("out", ""),
        "Morning Hours": d.get("morning", {}).get("hours", 0),
        "Afternoon In": d.get("afternoon", {}).get("in", ""),
        "Afternoon Out": d.get("afternoon", {}).get("out", ""),
        "Afternoon Hours": d.get("afternoon", {}).get("hours", 0),
        "Total Hours": d.get("total", 0)
    })

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values(by="Date")

# ===== SUMMARY =====
total_hours = month_data.get("total_hours", 0)
target = 216
remaining = max(target - total_hours, 0)
progress = min(total_hours / target, 1.0)

col1, col2, col3 = st.columns(3)

col1.metric("📊 Total Hours", round(total_hours, 2))
col2.metric("🎯 Target", target)
col3.metric("⏳ Remaining", round(remaining, 2))

st.progress(progress)
st.write(f"📈 Progress: {round(progress * 100, 2)}% of 216 hours")

# ===== TABLE =====
st.subheader(f"📅 Logs for {selected_month}")
st.dataframe(df, use_container_width=True)

# ===== CHART =====
st.subheader("📊 Daily Hours")

if not df.empty:
    st.bar_chart(df.set_index("Date")["Total Hours"])

# ===== INSIGHTS (SMART ADDITION) =====
st.subheader("🧠 Insights")

if total_hours > 0:
    working_days = len(df)
    avg_hours = total_hours / working_days if working_days > 0 else 0

    st.write(f"📌 Avg hours/day: **{round(avg_hours, 2)} hrs**")

    remaining_days_estimate = max(1, 26 - working_days)
    needed_per_day = remaining / remaining_days_estimate

    st.write(f"🎯 Needed per day to hit 216: **{round(needed_per_day, 2)} hrs/day**")
else:
    st.write("No sufficient data yet")
