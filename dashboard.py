import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import calendar
import requests
import base64
import plotly.graph_objects as go

# ===== PAGE CONFIG — must be first =====
st.set_page_config(
    page_title="Attendance Dashboard",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== GLOBAL CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── Reset & base ─── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp,
[data-testid="stMain"],
section[data-testid="stMain"] > div,
.main .block-container {
  background-color: #F7F8FA !important;
  color: #1C1C1E !important;
  font-family: 'Inter', sans-serif !important;
}

/* kill all dark-mode overrides */
[data-testid="stHeader"]  { background: #F7F8FA !important; box-shadow: none !important; }
[data-testid="stSidebar"] { background: #F0F1F5 !important; }
#MainMenu, footer         { visibility: hidden !important; }

.block-container {
  padding: 2rem 2.8rem 5rem !important;
  max-width: 1440px !important;
}

/* ─── Typography helpers ─── */
.page-title {
  font-size: 1.65rem; font-weight: 700; color: #111;
  letter-spacing: -.025em; margin: 0;
}
.page-sub { font-size: .875rem; color: #8E8E93; margin-top: 2px; }
.section-label {
  font-size: .65rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: #AEAEB2; margin: 1.8rem 0 .75rem;
}

/* ─── Cards ─── */
.card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E5E5EA;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 2px 8px rgba(0,0,0,.04);
  padding: 1.25rem 1.5rem;
  transition: box-shadow .18s ease;
}
.card:hover { box-shadow: 0 4px 20px rgba(0,0,0,.09); }

/* ─── Stat cards ─── */
.stat-card {
  background: #FFFFFF;
  border-radius: 14px;
  border: 1px solid #E5E5EA;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
  padding: 1.1rem 1.3rem 1rem;
  position: relative;
  overflow: hidden;
}
.stat-accent {
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: 14px 14px 0 0;
}
.stat-label {
  font-size: .68rem; font-weight: 600; letter-spacing: .09em;
  text-transform: uppercase; color: #AEAEB2; margin-bottom: .35rem;
}
.stat-value {
  font-size: 1.85rem; font-weight: 700; color: #1C1C1E;
  letter-spacing: -.03em; line-height: 1; font-variant-numeric: tabular-nums;
}
.stat-sub { font-size: .72rem; color: #C7C7CC; margin-top: .35rem; }

/* ─── Progress bar ─── */
.prog-card {
  background: #fff; border-radius: 14px;
  border: 1px solid #E5E5EA; padding: 1.4rem 1.8rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.prog-header {
  display: flex; justify-content: space-between;
  align-items: baseline; margin-bottom: .9rem;
}
.prog-title { font-size: .95rem; font-weight: 600; color: #1C1C1E; }
.prog-pct   { font-size: 1.5rem; font-weight: 700; letter-spacing: -.03em; }
.prog-track {
  background: #F2F2F7; border-radius: 99px;
  height: 10px; overflow: hidden; margin-bottom: .6rem;
}
.prog-fill  { height: 100%; border-radius: 99px; transition: width .5s ease; }
.prog-feet  {
  display: flex; justify-content: space-between;
  font-size: .72rem; font-weight: 500;
}
.prog-feet span:nth-child(2) { color: #3A3A3C; font-weight: 600; }
.prog-feet span:first-child,
.prog-feet span:last-child    { color: #AEAEB2; }

/* ─── Insight pills ─── */
.insight-pill {
  border-radius: 10px; padding: .7rem 1rem;
  font-size: .82rem; font-weight: 500;
  margin-bottom: .5rem; line-height: 1.4;
}
.pill-blue   { background:#EFF6FF; color:#1D4ED8; border-left:3px solid #3B82F6; }
.pill-green  { background:#F0FDF4; color:#15803D; border-left:3px solid #22C55E; }
.pill-amber  { background:#FFFBEB; color:#92400E; border-left:3px solid #F59E0B; }
.pill-red    { background:#FFF1F2; color:#BE123C; border-left:3px solid #F43F5E; }

/* ─── Status badges ─── */
.badge {
  display:inline-block; padding:.18rem .6rem;
  border-radius:99px; font-size:.7rem; font-weight:600;
  letter-spacing:.03em;
}
.badge-work    { background:#E8F5E9; color:#2E7D32; }
.badge-holiday { background:#E3F2FD; color:#1565C0; }
.badge-leave   { background:#FFF3E0; color:#E65100; }

/* ─── Expander ─── */
[data-testid="stExpander"] {
  background: #FFFFFF !important;
  border: 1px solid #E5E5EA !important;
  border-radius: 14px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.04) !important;
  overflow: hidden;
}
[data-testid="stExpander"] > details > summary {
  font-weight: 600 !important; font-size: .9rem !important;
  color: #1C1C1E !important; padding: 1rem 1.25rem !important;
}
[data-testid="stExpander"] > details > summary:hover {
  background: #F7F8FA !important;
}
[data-testid="stExpander"] > details[open] > summary {
  border-bottom: 1px solid #E5E5EA !important;
}

/* ─── Inputs ─── */
.stDateInput > div > div,
.stDateInput > div > div > input {
  background: #F7F8FA !important;
  border: 1px solid #E5E5EA !important;
  border-radius: 10px !important;
  color: #1C1C1E !important;
  font-family: 'Inter', sans-serif !important;
}
.stSelectbox > div > div {
  background: #F7F8FA !important;
  border: 1px solid #E5E5EA !important;
  border-radius: 10px !important;
  color: #1C1C1E !important;
}

/* ─── Buttons ─── */
.stButton > button {
  background: #1C1C1E !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: .83rem !important;
  padding: .5rem 1.2rem !important;
  letter-spacing: .01em;
  transition: background .15s ease, box-shadow .15s ease !important;
}
.stButton > button:hover {
  background: #3A3A3C !important;
  box-shadow: 0 4px 12px rgba(0,0,0,.18) !important;
}

/* ─── Dataframe — force white ─── */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe {
  background: #FFFFFF !important;
  border-radius: 12px !important;
  border: none !important;
}
.stDataFrame table       { background: #FFFFFF !important; color: #1C1C1E !important; }
.stDataFrame thead th    {
  background: #F7F8FA !important; color: #6E6E73 !important;
  font-size: .72rem !important; font-weight: 700 !important;
  letter-spacing: .08em !important; text-transform: uppercase !important;
  border-bottom: 1px solid #E5E5EA !important;
}
.stDataFrame tbody tr    { border-bottom: 1px solid #F2F2F7 !important; }
.stDataFrame tbody tr:hover { background: #F7F8FA !important; }
.stDataFrame tbody td    { color: #1C1C1E !important; font-size: .84rem !important; }

/* ─── Plotly chart containers ─── */
[data-testid="stPlotlyChart"] > div,
.js-plotly-plot, .plotly, .plot-container {
  background: transparent !important;
}

/* ─── Divider ─── */
.divider { border: none; border-top: 1px solid #E5E5EA; margin: 1.2rem 0; }

/* ─── Chart card inner header ─── */
.chart-head {
  font-size: .88rem; font-weight: 600; color: #1C1C1E;
  margin-bottom: .25rem;
}
.chart-sub { font-size: .75rem; color: #AEAEB2; margin-bottom: .5rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────
def stat_card(label, value, sub="", accent="#3B82F6"):
    return f"""
    <div class="stat-card">
      <div class="stat-accent" style="background:{accent};"></div>
      <div class="stat-label">{label}</div>
      <div class="stat-value">{value}</div>
      {"<div class='stat-sub'>" + sub + "</div>" if sub else ""}
    </div>"""

def pill(text, kind="blue"):
    cls = {"blue":"pill-blue","green":"pill-green","amber":"pill-amber","red":"pill-red"}.get(kind,"pill-blue")
    return f'<div class="insight-pill {cls}">{text}</div>'

def section(title):
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)

def divider():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

def plotly_line(df_plot):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["Date"], y=df_plot["Total"],
        mode="lines+markers",
        line=dict(color="#3B82F6", width=2.5, shape="spline"),
        marker=dict(size=5, color="#3B82F6", line=dict(width=1.5, color="#fff")),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.07)",
        hovertemplate="<b>%{x}</b><br>%{y:.2f} hrs<extra></extra>"
    ))
    fig.add_hline(y=9, line=dict(color="#E5E5EA", dash="dot", width=1.5),
                  annotation_text="9h target", annotation_font_size=10,
                  annotation_font_color="#AEAEB2")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=10, b=0), height=230,
        font=dict(family="Inter", color="#6E6E73", size=11),
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-35,
                   tickfont=dict(size=10, color="#AEAEB2"),
                   linecolor="#E5E5EA", showline=False),
        yaxis=dict(showgrid=True, gridcolor="#F2F2F7", zeroline=False,
                   tickfont=dict(size=10, color="#AEAEB2")),
        hoverlabel=dict(bgcolor="#1C1C1E", font_color="#fff",
                        bordercolor="#1C1C1E", font_size=12),
        showlegend=False
    )
    return fig

def plotly_bar(weekly_series):
    colors = ["#3B82F6" if v < 45 else "#22C55E" for v in weekly_series.values]
    fig = go.Figure(go.Bar(
        x=[f"Wk {w}" for w in weekly_series.index],
        y=weekly_series.values,
        marker=dict(color=colors, cornerradius=6),
        hovertemplate="<b>%{x}</b><br>%{y:.1f} hrs<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=10, b=0), height=230,
        font=dict(family="Inter", color="#6E6E73", size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=11, color="#AEAEB2"), linecolor="#E5E5EA"),
        yaxis=dict(showgrid=True, gridcolor="#F2F2F7", zeroline=False,
                   tickfont=dict(size=10, color="#AEAEB2")),
        hoverlabel=dict(bgcolor="#1C1C1E", font_color="#fff",
                        bordercolor="#1C1C1E", font_size=12),
        bargap=0.35, showlegend=False
    )
    return fig


# ─────────────────────────────────────────
#  CONFIG & DATA
# ─────────────────────────────────────────
FILE = "hours.json"
TOKEN    = st.secrets["GITHUB_TOKEN"]
REPO     = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

def load_data():
    with open(FILE, "r") as f:
        return json.load(f)

def save_to_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
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


# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
months    = list(data.get("months", {}).keys())
month_map = {m: datetime.strptime(m, "%Y-%m").strftime("%B %Y") for m in months}

head_l, head_r = st.columns([6, 1])
with head_l:
    st.markdown('<p class="page-title">🗓️ Attendance Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Personal timesheet — hours logged, targets & smart insights</p>', unsafe_allow_html=True)
with head_r:
    selected_name = st.selectbox("", [month_map[m] for m in months[::-1]], label_visibility="collapsed")

selected_month = [k for k, v in month_map.items() if v == selected_name][0]
month_data     = data["months"][selected_month]
holidays       = month_data.get("holidays", [])
leaves         = month_data.get("leaves",   [])

divider()

# ─────────────────────────────────────────
#  MANAGE HOLIDAYS / LEAVES
# ─────────────────────────────────────────
with st.expander("⚙️  Manage Holidays & Leaves"):
    c1, _, c2 = st.columns([2, .15, 2])
    with c1:
        st.markdown("**📅 Add a Holiday**")
        h_date = st.date_input("Holiday date", key="holiday_date", label_visibility="collapsed")
        if st.button("➕ Add Holiday", key="btn_holiday"):
            d = h_date.strftime("%Y-%m-%d")
            if d not in holidays:
                holidays.append(d)
                month_data["holidays"] = holidays
                save_to_github(data)
                st.success(f"Holiday added: {d}")
    with c2:
        st.markdown("**🏖️ Add a Leave**")
        l_date = st.date_input("Leave date", key="leave_date", label_visibility="collapsed")
        if st.button("➕ Add Leave", key="btn_leave"):
            d = l_date.strftime("%Y-%m-%d")
            if d not in leaves:
                leaves.append(d)
                month_data["leaves"] = leaves
                save_to_github(data)
                st.success(f"Leave added: {d}")


# ─────────────────────────────────────────
#  CALCULATIONS  (untouched logic)
# ─────────────────────────────────────────
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

def get_remaining_days(selected_month, holidays):
    now   = datetime.utcnow() + timedelta(hours=5, minutes=30)
    today = now.date()
    year, month = map(int, selected_month.split("-"))
    cal = calendar.monthcalendar(year, month)
    remaining_days = 0
    for week in cal:
        for i, day in enumerate(week):
            if day == 0: continue
            d = datetime(year, month, day).date()
            date_str = d.strftime("%Y-%m-%d")
            if d > today and i != 6 and date_str not in holidays:
                remaining_days += 1
    return max(1, remaining_days)

remaining_days = get_remaining_days(selected_month, holidays)


# ─────────────────────────────────────────
#  BUILD DATAFRAME
# ─────────────────────────────────────────
rows = []
for date, d in month_data["days"].items():
    dt     = datetime.strptime(date, "%Y-%m-%d")
    status = "Working"
    if date in holidays: status = "Holiday"
    elif date in leaves: status = "Leave"
    rows.append({
        "Date":    dt.strftime("%d/%m"),
        "Day":     dt.strftime("%a"),
        "Status":  status,
        "M-In":    d.get("morning",   {}).get("in",    "—"),
        "M-Out":   d.get("morning",   {}).get("out",   "—"),
        "M-Hrs":   d.get("morning",   {}).get("hours", 0),
        "A-In":    d.get("afternoon", {}).get("in",    "—"),
        "A-Out":   d.get("afternoon", {}).get("out",   "—"),
        "A-Hrs":   d.get("afternoon", {}).get("hours", 0),
        "Total":   d.get("total", 0)
    })

df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values("Date").reset_index(drop=True)

actual_days = len(df) if not df.empty else 1
avg         = round(total_hours / actual_days, 2) if actual_days else 0


# ─────────────────────────────────────────
#  ROW 1 — 5 STAT CARDS
# ─────────────────────────────────────────
section("Overview")

s1, s2, s3, s4, s5 = st.columns(5)
stat_data = [
    (s1, "Total Hours",   f"{round(total_hours,2)}",  "hrs logged this month",          "#3B82F6"),
    (s2, "Target Hours",  f"{target}",                 f"{working_days} days × 9 hrs",   "#8B5CF6"),
    (s3, "Remaining",     f"{round(remaining,2)}",     "hrs still to clock in",          "#F59E0B"),
    (s4, "Working Days",  f"{working_days}",            "excl. holidays & leaves",        "#22C55E"),
    (s5, "Days Left",     f"{remaining_days}",          "remaining work days",            "#F43F5E"),
]
for col, lbl, val, sub, color in stat_data:
    with col:
        st.markdown(stat_card(lbl, val, sub, color), unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ROW 2 — PROGRESS + AVG PER DAY
# ─────────────────────────────────────────
section("Progress")

p_col, a_col = st.columns([4, 1])

with p_col:
    pct = round(progress * 100, 2)
    if pct >= 90:   bar_color = "#22C55E"
    elif pct >= 60: bar_color = "#3B82F6"
    elif pct >= 30: bar_color = "#F59E0B"
    else:           bar_color = "#F43F5E"

    st.markdown(f"""
    <div class="prog-card">
      <div class="prog-header">
        <span class="prog-title">Monthly Progress</span>
        <span class="prog-pct" style="color:{bar_color};">{pct}%</span>
      </div>
      <div class="prog-track">
        <div class="prog-fill" style="width:{pct}%;background:{bar_color};"></div>
      </div>
      <div class="prog-feet">
        <span>0h</span>
        <span>{round(total_hours,1)}h done of {target}h</span>
        <span>{target}h</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with a_col:
    st.markdown(stat_card("Avg / Day", f"{avg}", "hrs based on days logged", "#3B82F6"),
                unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ROW 3 — DAILY TABLE + INSIGHTS
# ─────────────────────────────────────────
section("Daily Timesheet")

tbl_col, ins_col = st.columns([3, 1])

with tbl_col:
    st.markdown('<div class="card" style="padding:.8rem 1rem;">', unsafe_allow_html=True)
    display_df = df.copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Date":  st.column_config.TextColumn("Date",   width="small"),
                     "Day":   st.column_config.TextColumn("Day",    width="small"),
                     "Status":st.column_config.TextColumn("Status", width="small"),
                     "M-In":  st.column_config.TextColumn("M In",   width="small"),
                     "M-Out": st.column_config.TextColumn("M Out",  width="small"),
                     "M-Hrs": st.column_config.NumberColumn("M Hrs",format="%.2f", width="small"),
                     "A-In":  st.column_config.TextColumn("A In",   width="small"),
                     "A-Out": st.column_config.TextColumn("A Out",  width="small"),
                     "A-Hrs": st.column_config.NumberColumn("A Hrs",format="%.2f", width="small"),
                     "Total": st.column_config.NumberColumn("Total",format="%.2f hrs", width="small"),
                 })
    st.markdown('</div>', unsafe_allow_html=True)

with ins_col:
    st.markdown('<div class="card" style="min-height:300px;">', unsafe_allow_html=True)
    st.markdown("**🧠 Smart Insights**")
    st.markdown("<br>", unsafe_allow_html=True)

    if total_hours > 0:
        needed_9 = remaining / remaining_days

        st.markdown("**🎯 9 hrs / day target**")
        if needed_9 > 9:
            st.markdown(pill(f"⚠️ Need <b>{round(needed_9,2)} hrs/day</b> — high pressure!", "red"),
                        unsafe_allow_html=True)
        elif needed_9 < 6:
            st.markdown(pill(f"✅ You're ahead — {round(needed_9,2)} hrs/day is enough", "green"),
                        unsafe_allow_html=True)
        else:
            st.markdown(pill(f"👉 Maintain <b>{round(needed_9,2)} hrs/day</b>", "blue"),
                        unsafe_allow_html=True)

        relaxed_target    = working_days * 8
        relaxed_remaining = max(relaxed_target - total_hours, 0)
        needed_8          = relaxed_remaining / remaining_days

        st.markdown("<br>**😌 8 hrs / day pace**", unsafe_allow_html=True)
        if needed_8 > 8:
            st.markdown(pill(f"⚠️ Need <b>{round(needed_8,2)} hrs/day</b>", "amber"),
                        unsafe_allow_html=True)
        elif needed_8 < 6:
            st.markdown(pill(f"✅ Relaxed — {round(needed_8,2)} hrs/day enough", "green"),
                        unsafe_allow_html=True)
        else:
            st.markdown(pill(f"👉 Maintain <b>{round(needed_8,2)} hrs/day</b>", "blue"),
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(pill(f"📌 Daily average: <b>{avg} hrs</b>", "blue"), unsafe_allow_html=True)
    else:
        st.markdown(pill("No hours logged yet this month.", "blue"), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ROW 4 — PLOTLY CHARTS (always white)
# ─────────────────────────────────────────
section("Charts")

ch1, ch2 = st.columns(2)

with ch1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-head">📈 Daily Hours</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Hours logged per working day</div>', unsafe_allow_html=True)
    if not df.empty and "Total" in df.columns:
        st.plotly_chart(plotly_line(df), use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-head">📅 Weekly Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Total hours aggregated by ISO week</div>', unsafe_allow_html=True)
    if not df.empty:
        df["Week"] = pd.to_datetime(df["Date"], format="%d/%m").dt.isocalendar().week
        weekly = df.groupby("Week")["Total"].sum()
        st.plotly_chart(plotly_bar(weekly), use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)
