import streamlit as st
import json
import pandas as pd

FILE = "hours.json"

def load_data():
    with open(FILE, "r") as f:
        return json.load(f)

data = load_data()

st.title("📊 Attendance Dashboard")

rows = []

for date, d in data["days"].items():
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

st.subheader("📅 Daily Logs")
st.dataframe(df, use_container_width=True)

total_hours = data.get("total_hours", 0)

st.subheader("📈 Monthly Progress")
st.metric("Total Hours", round(total_hours, 2))

target = 216
progress = min(total_hours / target, 1.0)

st.progress(progress)
st.write(f"{round(progress * 100, 2)}% of 216 hours")

st.subheader("📊 Daily Hours Chart")
if not df.empty:
    st.bar_chart(df.set_index("Date")["Total Hours"])
