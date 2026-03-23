import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import calendar
import requests
import base64

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Attendance Dashboard",
    page_icon="📊",
    layout="wide"
)

# ===== FORCE WHITE MODE + BENTO STYLES =====
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  /* ── Force light mode ── */
  html, body, [data-testid="stAppViewContainer"],
  [data-testid="stApp"], .stApp {
    background-color: #f4f4f0 !important;
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  [data-testid="stSidebar"] { background-color: #ebebeb !important; }
  [data-testid="stHeader"]  { background-color: #f4f4f0 !important; }

  /* hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px; }

  /* ── Bento card base ── */
  .bento-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.05);
    border: 1px solid #ececec;
    height: 100%;
    transition: box-shadow .2s ease;
  }
  .bento-card:hover { box-shadow: 0 4px 24px rgba(0,0,0,.10); }

  /* ── Metric cards ── */
  .metric-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #ececec;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }
  .metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: .3rem;
  }
  .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1;
    font-family: 'DM Mono', monospace;
  }
  .metric-sub {
    font-size: 0.75rem;
    color: #aaa;
    margin-top: .3rem;
  }

  /* accent colours per card */
  .acc-blue   { border-top: 3px solid #3b82f6; }
  .acc-green  { border-top: 3px solid #22c55e; }
  .acc-amber  { border-top: 3px solid #f59e0b; }
  .acc-rose   { border-top: 3px solid #f43f5e; }
  .acc-purple { border-top: 3px solid #8b5cf6; }

  /* ── Page title area ── */
  .dash-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #111;
    letter-spacing: -.02em;
  }
  .dash-sub {
    font-size: .9rem;
    color: #888;
    margin-top: .1rem;
  }

  /* ── Progress bar ── */
  .prog-wrap {
    background: #f0f0ee;
    border-radius: 99px;
    height: 12px;
    overflow: hidden;
    margin: .5rem 0 .4rem;
  }
  .prog-fill {
    height: 100%;
    border-radius: 99px;
    transition: width .6s ease;
  }
  .prog-label {
    font-size: .8rem;
    font-weight: 600;
    color: #555;
  }

  /* ── Insight pills ── */
  .insight-box {
    border-radius: 14px;
    padding: .9rem 1.1rem;
    font-size: .88rem;
    font-weight: 500;
    margin-bottom: .5rem;
  }
  .insight-info    { background: #eff6ff; color: #1d4ed8; border-left: 4px solid #3b82f6; }
  .insight-success { background: #f0fdf4; color: #15803d; border-left: 4px solid #22c55e; }
  .insight-warn    { background: #fffbeb; color: #92400e; border-left: 4px solid #f59e0b; }
  .insight-danger  { background: #fff1f2; color: #be123c; border-left: 4px solid #f43f5e; }

  /* ── Section headers ── */
  .section-head {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #aaa;
    margin: 1.6rem 0 .7rem;
  }

  /* ── Expander override ── */
  [data-testid="stExpander"] {
    background: #fff !important;
    border-radius: 16px !important;
    border: 1px solid #ececec !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.05) !important;
  }
  [data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #333 !important;
  }

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #ececec !important;
  }
  .stDataFrame thead th {
    background: #f8f8f6 !important;
    font-weight: 600;
    font-size: .8rem;
    text-transform: uppercase;
    letter-spacing: .05em;
  }

  /* ── Selectbox / inputs override ── */
  .stSelectbox > div > div,
  .stDateInput > div > div > input {
    background: #fff !important;
    border-radius: 10px !important;
    border: 1px solid #e0e0e0 !important;
    color: #1a1a1a !important;
  }
  .stButton > button {
    background: #1a1a1a !important;
    color: #fff !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: .45rem 1.1rem !important;
    font-size: .85rem !important;
  }
  .stButton > button:hover {
    background: #3b3b3b !important;
    box-shadow: 0 4px 12px rgba(0,0,0,.15) !important;
  }

  /* chart backgrounds */
  [data-testid="stVegaLiteChart"],
  [data-testid="stArrowVegaLiteChart"] {
    background: transparent !important;
  }

  /* divider */
  hr { border: none; border-top: 1px solid #ebebeb; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ===== UI HELPERS =====
def metric_card(label, value, sub="", accent="acc-blue"):
    return f"""
    <div class="metric-card {accent}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""

def insight(text, kind="info"):
    cls = {"info": "insight-info", "success": "insight-success",
           "warn": "insight-warn", "danger": "insight-danger"}.get(kind, "insight-info")
    return f'<div class="insight-box {cls}">{text}</div>'

def section(title):
    st.markdown(f'<div class="section-head">{title}</div>', unsafe_allow_html=True)


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
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error("❌ Failed to fetch file from GitHub")
        return
    sha = res.json()["sha"]
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    payload = {"message": "update holidays/leaves", "content": content, "sha": sha}
    update = requests.put(url, headers=headers, json=payload)
    if update.status_code == 200:
        st.success("✅ Saved to GitHub")
    else:
        st.error(f"❌ GitHub update failed: {update.text}")

data = load_data()

# ===== HEADER ROW =====
h_left, h_right = st.columns([5, 1])
with h_left:
    st.markdown('<div class="dash-title">📊 Attendance Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-sub">Track your working hours, targets & insights</div>', unsafe_allow_html=True)

months = list(data.get("months", {}).keys())
month_map = {m: datetime.strptime(m, "%Y-%m").strftime("%B") for m in months}

with h_right:
    selected_name = st.selectbox("", [month_map[m] for m in months[::-1]], label_visibility="collapsed")

selected_month = [k for k, v in month_map.items() if v == selected_name][0]
month_data = data["months"][selected_month]
holidays = month_data.get("holidays", [])
leaves   = month_data.get("leaves", [])

st.markdown("<hr>", unsafe_allow_html=True)

# ===== MANAGE HOLIDAYS / LEAVES =====
with st.expander("⚙️  Manage Holidays & Leaves"):
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
total_hours  = month_data.get("total_hours", 0)
remaining    = max(target - total_hours, 0)
progress     = min(total_hours / target, 1.0) if target else 0

# ===== REMAINING DAYS =====
def get_remaining_days(selected_month, holidays):
    now   = datetime.utcnow() + timedelta(hours=5, minutes=30)
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
            if d > today and i != 6 and date_str not in holidays:
                remaining_days += 1
    return max(1, remaining_days)

remaining_days = get_remaining_days(selected_month, holidays)

# ===== BUILD TABLE =====
rows = []
for date, d in month_data["days"].items():
    dt = datetime.strptime(date, "%Y-%m-%d")
    status = "Working"
    if date in holidays:  status = "Holiday"
    elif date in leaves:  status = "Leave"
    rows.append({
        "Date":    dt.strftime("%d/%m"),
        "Status":  status,
        "M-In":    d.get("morning",   {}).get("in",    ""),
        "M-Out":   d.get("morning",   {}).get("out",   ""),
        "M-Hours": d.get("morning",   {}).get("hours", 0),
        "A-In":    d.get("afternoon", {}).get("in",    ""),
        "A-Out":   d.get("afternoon", {}).get("out",   ""),
        "A-Hours": d.get("afternoon", {}).get("hours", 0),
        "Total":   d.get("total", 0)
    })

df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values(by="Date")

actual_days = len(df) if not df.empty else 1
avg         = round(total_hours / actual_days, 2) if actual_days else 0

# =====================================================================
#  BENTO ROW 1 — 5 stat cards
# =====================================================================
section("Overview")
mc1, mc2, mc3, mc4, mc5 = st.columns(5)
cards = [
    (mc1, "Total Hours",  f"{round(total_hours, 2)}h", f"logged this month",       "acc-blue"),
    (mc2, "Target Hours", f"{target}h",                f"{working_days} days × 9h","acc-purple"),
    (mc3, "Remaining",    f"{round(remaining, 2)}h",   "still to clock in",        "acc-amber"),
    (mc4, "Working Days", f"{working_days}",            "excl. holidays & leaves",  "acc-green"),
    (mc5, "Days Left",    f"{remaining_days}",          "remaining workdays",       "acc-rose"),
]
for col, label, val, sub, acc in cards:
    with col:
        st.markdown(metric_card(label, val, sub, acc), unsafe_allow_html=True)

# =====================================================================
#  BENTO ROW 2 — progress bar (wide) + avg/day card
# =====================================================================
section("Progress")
prog_col, avg_col = st.columns([3, 1])

with prog_col:
    pct = round(progress * 100, 2)
    bar_color = "#22c55e" if pct >= 90 else "#3b82f6" if pct >= 50 else "#f59e0b"
    st.markdown(f"""
    <div class="bento-card" style="padding:1.6rem 2rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.6rem;">
        <span style="font-weight:700;font-size:1rem;color:#222;">Monthly Progress</span>
        <span style="font-family:'DM Mono',monospace;font-size:1.4rem;font-weight:700;color:{bar_color};">{pct}%</span>
      </div>
      <div class="prog-wrap">
        <div class="prog-fill" style="width:{pct}%;background:{bar_color};"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:.5rem;">
        <span class="prog-label" style="color:#aaa;">0h</span>
        <span class="prog-label" style="color:#555;">{round(total_hours,1)}h done of {target}h</span>
        <span class="prog-label" style="color:#aaa;">{target}h</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with avg_col:
    st.markdown(metric_card("Avg / Day", f"{avg}h", "based on days logged", "acc-blue"), unsafe_allow_html=True)

# =====================================================================
#  BENTO ROW 3 — daily log table + smart insights
# =====================================================================
section("Daily Logs & Insights")
tbl_col, ins_col = st.columns([3, 1])

with tbl_col:
    st.markdown('<div class="bento-card" style="padding:1rem 1.2rem;">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with ins_col:
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    st.markdown("<strong style='font-size:.95rem;'>🧠 Smart Insights</strong>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if total_hours > 0:
        needed_9 = remaining / remaining_days
        st.markdown("**🎯 9 hrs/day target**")
        if needed_9 > 9:
            st.markdown(insight(f"⚠️ Need <b>{round(needed_9,2)} hrs/day</b> — high pressure!", "danger"), unsafe_allow_html=True)
        elif needed_9 < 6:
            st.markdown(insight(f"✅ Ahead — {round(needed_9,2)} hrs/day enough", "success"), unsafe_allow_html=True)
        else:
            st.markdown(insight(f"👉 Maintain <b>{round(needed_9,2)} hrs/day</b>", "info"), unsafe_allow_html=True)

        relaxed_target    = working_days * 8
        relaxed_remaining = max(relaxed_target - total_hours, 0)
        needed_8          = relaxed_remaining / remaining_days

        st.markdown("<br>**😌 8 hrs/day pace**")
        if needed_8 > 8:
            st.markdown(insight(f"⚠️ Need <b>{round(needed_8,2)} hrs/day</b>", "warn"), unsafe_allow_html=True)
        elif needed_8 < 6:
            st.markdown(insight(f"✅ Relaxed — {round(needed_8,2)} hrs/day enough", "success"), unsafe_allow_html=True)
        else:
            st.markdown(insight(f"👉 Maintain <b>{round(needed_8,2)} hrs/day</b>", "info"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(insight(f"📌 Daily avg: <b>{avg} hrs</b>", "info"), unsafe_allow_html=True)
    else:
        st.markdown(insight("No hours logged yet this month.", "info"), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
#  BENTO ROW 4 — line chart + weekly bar chart
# =====================================================================
section("Charts")
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    st.markdown("<strong>📈 Daily Hours</strong>", unsafe_allow_html=True)
    if "Total" in df.columns and not df.empty:
        st.line_chart(df.set_index("Date")["Total"], height=220, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    st.markdown("<strong>📅 Weekly Breakdown</strong>", unsafe_allow_html=True)
    if not df.empty:
        df["Week"] = pd.to_datetime(df["Date"], format="%d/%m").dt.isocalendar().week
        weekly = df.groupby("Week")["Total"].sum()
        st.bar_chart(weekly, height=220, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
