"""
OLA Ride Analytics - Booking, Cancellation, Revenue and Customer Satisfaction
SQL querying | Data preprocessing | Power BI | Streamlit | Business intelligence

Run:  streamlit run 04_streamlit_app.py
Put ola_cleaned.csv in the same folder (or upload it in the sidebar).
Created by Challapalli Mamatha
"""

import base64
import html
import io
import os
import re
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

st.set_page_config(page_title="OLA Ride Analytics", layout="wide", initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------
# COLOURS AND SECTION LIST
# ----------------------------------------------------------------------------
NAVY = "#0B2545"
BLUE = "#1F6FB2"
ORANGE = "#E8871E"
TEAL = "#13806F"
RED = "#C0392B"
GOLD = "#EDAE49"
PURPLE = "#6C5B9E"
INK = "#1B1B1B"
PALETTE = [BLUE, ORANGE, TEAL, RED, GOLD, PURPLE, "#4A4E69"]
STATUS_COLORS = {
    "Success": TEAL,
    "Canceled by Customer": ORANGE,
    "Canceled by Driver": RED,
    "Driver Not Found": GOLD,
}

SECTIONS = [
    "1. Project Title",
    "2. Project Summary",
    "3. Business Objective",
    "4. Key Findings",
    "5. Problem Statement",
    "6. What We Should Increase",
    "7. Charts and Graphs",
    "8. Why Cancellation Is Happening",
    "9. Top Rated Areas",
    "10. Customer Satisfaction",
    "11. Power BI Dashboards",
    "12. Business Insights and Recommendations",
    "13. Conclusion",
]

CSS = """
<style>
.stApp { background: #EEF3F9; }
header[data-testid="stHeader"] { background: #EEF3F9; }
.block-container { padding-top: 1.6rem; max-width: 1350px; }

/* main area text */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: #0B2545 !important; }
.stApp .stMarkdown p, .stApp .stMarkdown li { color: #1B1B1B; font-size: 1.02rem; line-height: 1.65; }
.stApp [data-testid="stWidgetLabel"] p { color: #0B2545; font-weight: 600; }

/* sidebar */
section[data-testid="stSidebar"] { background: #0B2545; border-right: 4px solid #F2B705; }
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label { color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stMarkdown h3 { color: #F2B705 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width: 100%; padding: 10px 12px; border-radius: 8px;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(255,255,255,0.20); }
section[data-testid="stSidebar"] div[role="radiogroup"] > label p { color: #FFFFFF !important; font-size: 0.98rem; margin: 0; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background: #F2B705; border-color: #F2B705; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #0B2545 !important; font-weight: 700; }

/* tabs */
button[data-baseweb="tab"] p { color: #0B2545 !important; font-weight: 600; font-size: 1rem; }
button[data-baseweb="tab"][aria-selected="true"] p { color: #C0392B !important; }

/* section header */
.stApp .stMarkdown .sec-head { background: #0B2545; border-radius: 12px; padding: 18px 24px; margin-bottom: 18px; border-left: 8px solid #F2B705; }
.stApp .stMarkdown .sec-num { color: #F2B705 !important; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px; }
.stApp .stMarkdown .sec-title { color: #FFFFFF !important; font-size: 1.9rem; font-weight: 800; line-height: 1.25; }
.stApp .stMarkdown .sec-sub { color: #D6E4F5 !important; font-size: 1rem; margin-top: 4px; }

/* hero (title page) */
.stApp .stMarkdown .hero { background: linear-gradient(120deg, #0B2545 0%, #1F6FB2 100%); border-radius: 16px; padding: 44px 40px; margin-bottom: 20px; }
.stApp .stMarkdown .hero-tag { color: #F2B705 !important; font-weight: 700; letter-spacing: 2px; font-size: 0.95rem; }
.stApp .stMarkdown .hero-title { color: #FFFFFF !important; font-size: 3.2rem; font-weight: 800; line-height: 1.15; margin: 8px 0; }
.stApp .stMarkdown .hero-sub { color: #FFFFFF !important; font-size: 1.35rem; margin-bottom: 14px; }
.stApp .stMarkdown .hero-tools { color: #D6E4F5 !important; font-size: 1rem; }

/* cards and KPIs */
.stApp .stMarkdown .card { background: #FFFFFF; border: 1px solid #D5DEEA; border-left: 6px solid #1F6FB2; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; }
.stApp .stMarkdown .card.warn { border-left-color: #C0392B; }
.stApp .stMarkdown .card.good { border-left-color: #13806F; }
.stApp .stMarkdown .card.gold { border-left-color: #E8871E; }
.stApp .stMarkdown .card-title { color: #0B2545 !important; font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; }
.stApp .stMarkdown .card-body, .stApp .stMarkdown .card-body * { color: #1B1B1B !important; font-size: 1.02rem; line-height: 1.65; }
.stApp .stMarkdown .card-body b { color: #0B2545 !important; }
.stApp .stMarkdown .card-body ul { margin: 6px 0 0 0; padding-left: 20px; }
.stApp .stMarkdown .kpi { background: #FFFFFF; border: 1px solid #D5DEEA; border-top: 5px solid #1F6FB2; border-radius: 12px; padding: 14px 10px; text-align: center; margin-bottom: 14px; }
.stApp .stMarkdown .kpi-val { color: #0B2545 !important; font-size: 1.75rem; font-weight: 800; white-space: nowrap; }
.stApp .stMarkdown .kpi-lab { color: #1B1B1B !important; font-size: 1rem; font-weight: 600; }
.stApp .stMarkdown .kpi-note { color: #4A5568 !important; font-size: 0.88rem; }
.stApp .stMarkdown .note { background: #FFF4D6; border: 1px solid #F2B705; border-radius: 10px; padding: 10px 14px; color: #1B1B1B !important; font-size: 0.95rem; margin: 8px 0 14px 0; }
.stApp .stMarkdown .answer { background: #E4F4F0; border: 1px solid #13806F; border-radius: 10px; padding: 12px 16px; color: #0B2545 !important; font-size: 1.05rem; font-weight: 600; margin: 10px 0; }

/* tables */
.stApp .stMarkdown .tbl-wrap { overflow-x: auto; margin-bottom: 14px; }
.stApp .stMarkdown table.tbl { width: 100%; border-collapse: collapse; background: #FFFFFF; border: 1px solid #D5DEEA; }
.stApp .stMarkdown table.tbl th { background: #0B2545; color: #FFFFFF !important; padding: 10px 12px; text-align: left; font-size: 0.95rem; }
.stApp .stMarkdown table.tbl td { color: #1B1B1B !important; background: #FFFFFF; padding: 9px 12px; border-top: 1px solid #E3E8EF; font-size: 0.95rem; vertical-align: top; }
.stApp .stMarkdown table.tbl tr:nth-child(even) td { background: #F3F7FC; }

div[data-testid="stPlotlyChart"] { background: #FFFFFF; border: 1px solid #D5DEEA; border-radius: 12px; padding: 6px; margin-bottom: 12px; }

.stApp .stMarkdown .credit { text-align: center; margin-top: 26px; padding: 26px; background: #0B2545; border-radius: 16px; border-bottom: 6px solid #F2B705; }
.stApp .stMarkdown .credit-small { color: #D6E4F5 !important; font-size: 1.05rem; }
.stApp .stMarkdown .credit-name { color: #FFFFFF !important; font-size: 2rem; font-weight: 800; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# SMALL HELPERS
# ----------------------------------------------------------------------------
_counter = {"n": 0}


def show(fig):
    _counter["n"] += 1
    key = f"chart_{_counter['n']}"
    try:
        st.plotly_chart(fig, key=key, width="stretch")
    except Exception:
        st.plotly_chart(fig, key=key, use_container_width=True)


def show_table(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(df, use_container_width=True)


def inr(x):
    if x is None or pd.isna(x):
        return "Rs 0"
    if x >= 1e7:
        return f"Rs {x / 1e7:,.2f} Cr"
    if x >= 1e5:
        return f"Rs {x / 1e5:,.2f} L"
    return f"Rs {x:,.0f}"


def pct(a, b):
    return (a / b * 100) if b else 0.0


def top_label(series, default="N/A"):
    series = series.dropna()
    return series.idxmax() if len(series) else default


def head(n, title, sub=""):
    st.markdown(
        f'<div class="sec-head"><div class="sec-num">SECTION {n} OF 13</div>'
        f'<div class="sec-title">{title}</div><div class="sec-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def card(title, body, kind=""):
    st.markdown(
        f'<div class="card {kind}"><div class="card-title">{title}</div><div class="card-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def kpi(value, label, note="", color=BLUE):
    st.markdown(
        f'<div class="kpi" style="border-top-color:{color}"><div class="kpi-val">{value}</div>'
        f'<div class="kpi-lab">{label}</div><div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def note(text):
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def answer(text):
    st.markdown(f'<div class="answer">{text}</div>', unsafe_allow_html=True)


def bullets(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def html_table(df):
    th = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows = ""
    for _, r in df.iterrows():
        rows += "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in r.values) + "</tr>"
    st.markdown(
        f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# CHART STYLE (dark readable text on white)
# ----------------------------------------------------------------------------
def finish(fig, title, height=400, xrange=None, yrange=None, legend_bottom=False):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"<b>{title}</b>", font=dict(size=18, color=NAVY), x=0.01, xanchor="left"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color=INK),
        height=height,
        margin=dict(l=50, r=40, t=70, b=60),
        legend=dict(font=dict(size=13, color=INK), title=dict(font=dict(color=INK))),
        hoverlabel=dict(bgcolor="white", font=dict(size=13, color=INK)),
    )
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", y=-0.28, x=0, font=dict(size=13, color=INK),
                                      title=dict(text="")))
    fig.update_xaxes(showgrid=False, linecolor="#7A8699", tickfont=dict(size=13, color=INK),
                     title_font=dict(size=14, color=INK))
    fig.update_yaxes(gridcolor="#E3E8EF", linecolor="#7A8699", tickfont=dict(size=13, color=INK),
                     title_font=dict(size=14, color=INK))
    if xrange:
        fig.update_xaxes(range=xrange)
    if yrange:
        fig.update_yaxes(range=yrange)
    return fig


def hbar(df, x, y, title, color=BLUE, fmt=",.0f", suffix="", xtitle="", height=None, xrange=None):
    df = df.sort_values(x, ascending=True)
    fig = px.bar(df, x=x, y=y, orientation="h", color_discrete_sequence=[color])
    fig.update_traces(
        text=df[x].values,
        texttemplate="%{text:" + fmt + "}" + suffix,
        textposition="outside",
        textfont=dict(size=13, color=INK),
        cliponaxis=False,
        marker=dict(line=dict(color="white", width=1)),
    )
    h = height or max(340, 38 * len(df) + 110)
    rng = xrange or [0, float(df[x].max()) * 1.18 if len(df) else 1]
    fig = finish(fig, title, height=h, xrange=rng)
    fig.update_xaxes(title_text=xtitle)
    fig.update_yaxes(title_text="", gridcolor="white")
    fig.update_xaxes(showgrid=True, gridcolor="#E3E8EF")
    return fig


def vbar(df, x, y, title, color=None, fmt=",.0f", suffix="", ytitle="", height=400, yrange=None):
    fig = px.bar(df, x=x, y=y)
    if color is None:
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(df))]
    else:
        colors = [color] * len(df)
    fig.update_traces(
        marker_color=colors,
        text=df[y].values,
        texttemplate="%{text:" + fmt + "}" + suffix,
        textposition="outside",
        textfont=dict(size=13, color=INK),
        cliponaxis=False,
        marker_line_color="white",
        marker_line_width=1,
    )
    top = float(df[y].max()) if len(df) else 1
    fig = finish(fig, title, height=height, yrange=yrange or [0, top * 1.18])
    fig.update_layout(showlegend=False)
    fig.update_yaxes(title_text=ytitle)
    fig.update_xaxes(title_text="")
    return fig


def donut(df, names, values, title, colors=None, height=400):
    fig = px.pie(df, names=names, values=values, hole=0.55, color=names,
                 color_discrete_map=colors or {}, color_discrete_sequence=PALETTE)
    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=14, color=INK),
        marker=dict(line=dict(color="white", width=2)),
        sort=False,
    )
    fig = finish(fig, title, height=height)
    fig.update_layout(showlegend=False, margin=dict(l=90, r=90, t=70, b=40))
    return fig


# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
def make_demo(n=8000, seed=42):
    rng = np.random.default_rng(seed)
    vehicles = ["Auto", "Bike", "E-Bike", "Mini", "Prime Plus", "Prime SUV", "Prime Sedan"]
    places = ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar", "MG Road", "Electronic City",
              "Hebbal", "BTM Layout", "Marathahalli", "Banashankari", "Yelahanka"]
    status = rng.choice(["Success", "Canceled by Customer", "Canceled by Driver", "Driver Not Found"],
                        n, p=[0.62, 0.10, 0.18, 0.10])
    dates = pd.Timestamp("2024-07-01") + pd.to_timedelta(rng.integers(0, 31, n), unit="D")
    hours = rng.integers(0, 24, n)
    times = [f"{h:02d}:{m:02d}:{s:02d}" for h, m, s in zip(hours, rng.integers(0, 60, n), rng.integers(0, 60, n))]
    dist = np.round(rng.uniform(1, 49, n))
    succ = status == "Success"
    incomplete = succ & (rng.random(n) < 0.06)
    cust = ["Driver is not moving towards pickup location", "Driver asked to cancel", "Change of plans",
            "AC is Not working", "Wrong Address"]
    drv = ["Personal & Car related issue", "Customer related issue", "Customer was coughing/sick",
           "More than permitted people in there"]
    return pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"), "Time": times,
        "Booking_ID": [f"CNR{100000 + i}" for i in range(n)], "Booking_Status": status,
        "Customer_ID": [f"CID{rng.integers(1000, 9000)}" for _ in range(n)],
        "Vehicle_Type": rng.choice(vehicles, n), "Pickup_Location": rng.choice(places, n),
        "Drop_Location": rng.choice(places, n),
        "Canceled_Rides_by_Customer": np.where(status == "Canceled by Customer", rng.choice(cust, n), None),
        "Canceled_Rides_by_Driver": np.where(status == "Canceled by Driver", rng.choice(drv, n), None),
        "Incomplete_Rides": np.where(succ, np.where(incomplete, "Yes", "No"), "Unknown"),
        "Incomplete_Rides_Reason": np.where(incomplete, rng.choice(["Customer Demand", "Vehicle Breakdown",
                                                                    "Other Issue"], n), None),
        "Booking_Value": np.round(60 + dist * rng.uniform(6, 16, n)),
        "Payment_Method": np.where(succ, rng.choice(["Cash", "UPI", "Credit Card", "Debit Card"], n,
                                                    p=[0.55, 0.40, 0.04, 0.01]), "Unknown"),
        "Ride_Distance": np.where(succ, dist, 0),
        "Driver_Ratings": np.where(succ, np.round(rng.uniform(3, 5, n), 1), np.nan),
        "Customer_Rating": np.where(succ, np.round(rng.uniform(3, 5, n), 1), np.nan),
    })


def norm(col):
    return re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")


ALIASES = {
    "date": ["date", "booking_date", "ride_date"],
    "time": ["time", "booking_time"],
    "booking_id": ["booking_id", "bookingid"],
    "booking_status": ["booking_status", "status"],
    "customer_id": ["customer_id", "customerid"],
    "vehicle_type": ["vehicle_type", "vehicle", "vehicletype"],
    "pickup_location": ["pickup_location", "pickup"],
    "drop_location": ["drop_location", "drop"],
    "canceled_rides_by_customer": ["canceled_rides_by_customer", "cancelled_rides_by_customer"],
    "canceled_rides_by_driver": ["canceled_rides_by_driver", "cancelled_rides_by_driver"],
    "incomplete_rides": ["incomplete_rides"],
    "incomplete_rides_reason": ["incomplete_rides_reason"],
    "booking_value": ["booking_value", "fare", "booking_amount"],
    "payment_method": ["payment_method", "payment"],
    "ride_distance": ["ride_distance", "distance"],
    "driver_ratings": ["driver_ratings", "driver_rating"],
    "customer_rating": ["customer_rating", "customer_ratings"],
}
TEXT_COLS = ["time", "booking_id", "booking_status", "customer_id", "vehicle_type", "pickup_location",
             "drop_location", "canceled_rides_by_customer", "canceled_rides_by_driver", "incomplete_rides",
             "incomplete_rides_reason", "payment_method"]
NUM_COLS = ["booking_value", "ride_distance", "driver_ratings", "customer_rating"]
REASON_COLS = ["canceled_rides_by_customer", "canceled_rides_by_driver", "incomplete_rides", "incomplete_rides_reason"]
VEHICLE_FIX = {"ebike": "E-Bike", "e-bike": "E-Bike", "go mini": "Mini", "mini": "Mini", "prime sedan": "Prime Sedan",
               "prime plus": "Prime Plus", "prime suv": "Prime SUV", "auto": "Auto", "bike": "Bike"}


def preprocess(raw):
    df = raw.copy()
    df.columns = [norm(c) for c in df.columns]
    rename = {}
    for std, alts in ALIASES.items():
        for a in alts:
            if a in df.columns and a != std and std not in df.columns:
                rename[a] = std
                break
    df = df.rename(columns=rename)
    for c in TEXT_COLS:
        if c not in df.columns:
            df[c] = np.nan
    for c in NUM_COLS:
        if c not in df.columns:
            df[c] = np.nan
    if "date" not in df.columns:
        df["date"] = pd.Timestamp.today().normalize()
    for c in TEXT_COLS:
        s = df[c]
        s = s.where(s.isna(), s.astype(str).str.strip().str.strip('"').str.strip())
        s = s.replace({"": np.nan, "nan": np.nan, "NaN": np.nan, "null": np.nan, "NULL": np.nan, "None": np.nan})
        df[c] = s
    for c in ["booking_status", "vehicle_type", "pickup_location", "drop_location", "payment_method",
              "booking_id", "customer_id"]:
        df[c] = df[c].fillna("Unknown")
    for c in REASON_COLS:
        df[c] = df[c].fillna("None")
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["day"] = df["date"].dt.normalize()
    df["weekday"] = df["date"].dt.day_name()
    df["hour"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.hour
    if df["hour"].isna().all():
        df["hour"] = pd.to_datetime(df["time"], errors="coerce").dt.hour
    df["vehicle_type"] = df["vehicle_type"].apply(lambda v: VEHICLE_FIX.get(str(v).lower(), v))
    status = df["booking_status"].str.lower()
    df["is_success"] = status.eq("success")
    df["is_cust_cancel"] = status.str.contains("customer")
    df["is_driver_cancel"] = status.str.contains("canceled by driver|cancelled by driver")
    df["is_not_found"] = status.str.contains("not found")
    df["is_incomplete"] = df["incomplete_rides"].str.lower().eq("yes")
    df["revenue"] = np.where(df["is_success"], df["booking_value"].fillna(0), 0.0)
    return df.reset_index(drop=True)


@st.cache_data(show_spinner="Loading data...")
def load_data(file_bytes, file_name):
    if file_bytes is not None:
        if str(file_name).lower().endswith((".xlsx", ".xls")):
            raw = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raw = pd.read_csv(io.BytesIO(file_bytes))
        return preprocess(raw), "uploaded file"
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    names = ["ola_cleaned.csv", "Ola_cleaned.csv", "Bookings.csv", "ola.csv", "OLA_DataSet.csv"]
    folders = [here, os.getcwd(), os.path.join(os.path.expanduser("~"), "Downloads")]
    for folder in folders:
        for n in names:
            p = os.path.join(folder, n)
            if os.path.exists(p):
                return preprocess(pd.read_csv(p)), p
    return preprocess(make_demo()), "sample data"


def compute(d):
    S = {}
    s = d[d.is_success]
    S["s"] = s
    S["total"] = len(d)
    S["n_success"] = len(s)
    S["succ_rate"] = pct(len(s), len(d))
    S["n_cust"] = int(d.is_cust_cancel.sum())
    S["n_drv"] = int(d.is_driver_cancel.sum())
    S["n_nf"] = int(d.is_not_found.sum())
    S["n_failed"] = S["total"] - S["n_success"]
    S["fail_rate"] = pct(S["n_failed"], S["total"])
    S["n_cancel"] = S["n_cust"] + S["n_drv"]
    S["revenue"] = float(s["booking_value"].sum())
    S["avg_value"] = float(s["booking_value"].mean()) if len(s) else 0.0
    fb = d.loc[~d.is_success, "booking_value"]
    S["lost"] = float(fb.sum()) if fb.notna().any() else S["n_failed"] * S["avg_value"]
    S["avg_dist"] = float(s["ride_distance"].mean()) if len(s) else 0.0
    S["n_incomplete"] = int(s.is_incomplete.sum())
    S["incomplete_rate"] = pct(S["n_incomplete"], len(s))
    S["avg_cust"] = float(s["customer_rating"].mean()) if s["customer_rating"].notna().any() else float("nan")
    S["avg_drv"] = float(s["driver_ratings"].mean()) if s["driver_ratings"].notna().any() else float("nan")
    rated = s["customer_rating"].dropna()
    S["sat"] = pct(int((rated >= 4).sum()), len(rated))
    S["high_sat"] = pct(int((rated >= 4.5).sum()), len(rated))
    S["low_sat"] = pct(int((rated < 3.5).sum()), len(rated))
    pay = s["payment_method"]
    S["cash_share"] = pct(int((pay == "Cash").sum()), len(s))
    S["digital_share"] = pct(int((~pay.isin(["Cash", "Unknown"])).sum()), len(s))
    S["upi_share"] = pct(int((pay == "UPI").sum()), len(s))
    hr = d.dropna(subset=["hour"]).groupby("hour").size()
    S["peak_hour"] = int(top_label(hr, 0)) if len(hr) else 0
    S["hour_spread"] = pct(hr.max() - hr.min(), hr.min()) if len(hr) and hr.min() else 0.0
    S["top_vehicle"] = top_label(d["vehicle_type"].value_counts())
    S["rev_vehicle"] = top_label(s.groupby("vehicle_type")["revenue"].sum())
    vs = d.groupby("vehicle_type")["is_success"].mean() * 100
    S["best_succ_vehicle"] = top_label(vs)
    S["best_succ_rate"] = float(vs.max()) if len(vs) else 0.0
    S["worst_succ_vehicle"] = vs.idxmin() if len(vs) else "N/A"
    S["worst_succ_rate"] = float(vs.min()) if len(vs) else 0.0
    cc = d.loc[~d.canceled_rides_by_customer.isin(["None", "Unknown"]), "canceled_rides_by_customer"].value_counts()
    dc = d.loc[~d.canceled_rides_by_driver.isin(["None", "Unknown"]), "canceled_rides_by_driver"].value_counts()
    ic = d.loc[~d.incomplete_rides_reason.isin(["None", "Unknown"]), "incomplete_rides_reason"].value_counts()
    S["cust_reasons"], S["drv_reasons"], S["inc_reasons"] = cc, dc, ic
    S["cust_driver_linked"] = pct(int(cc[cc.index.str.lower().str.contains("driver")].sum()), int(cc.sum()))
    areas = s.groupby("pickup_location")["revenue"].sum()
    areas = areas[areas.index != "Unknown"]
    S["top_area_rev"] = top_label(areas)
    top_book = d[d.pickup_location != "Unknown"]["pickup_location"].value_counts()
    S["top_area_book"] = top_book.index[0] if len(top_book) else "N/A"
    S["n_areas"] = int(d.loc[d.pickup_location != "Unknown", "pickup_location"].nunique())
    S["n_vehicles"] = int(d["vehicle_type"].nunique())
    return S


def area_stats(d):
    s = d[d.is_success & (d.pickup_location != "Unknown")]
    g = s.groupby("pickup_location").agg(
        successful_rides=("booking_id", "count"),
        driver_rating=("driver_ratings", "mean"),
        customer_rating=("customer_rating", "mean"),
        revenue=("revenue", "sum"),
    ).reset_index()
    g["overall_rating"] = (g["driver_rating"] + g["customer_rating"]) / 2
    return g


# ----------------------------------------------------------------------------
# REUSABLE FIGURES
# ----------------------------------------------------------------------------
def fig_status_donut(d):
    g = d["booking_status"].value_counts().reset_index()
    g.columns = ["status", "count"]
    return donut(g, "status", "count", "Booking status share", colors=STATUS_COLORS)


def fig_daily_status(d):
    g = d.groupby(["day", "booking_status"]).size().reset_index(name="bookings")
    fig = px.bar(g, x="day", y="bookings", color="booking_status", color_discrete_map=STATUS_COLORS,
                 color_discrete_sequence=PALETTE)
    fig = finish(fig, "Daily bookings by status", height=420, legend_bottom=True)
    fig.update_xaxes(tickformat="%d %b", title_text="Date")
    fig.update_yaxes(title_text="Bookings")
    return fig


def fig_daily_revenue(s):
    g = s.groupby("day")["revenue"].sum().reset_index()
    fig = px.line(g, x="day", y="revenue", markers=True, color_discrete_sequence=[BLUE])
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig = finish(fig, "Daily revenue from successful rides", height=400, yrange=[0, float(g["revenue"].max()) * 1.2])
    fig.update_xaxes(tickformat="%d %b", title_text="Date")
    fig.update_yaxes(title_text="Revenue (Rs)")
    return fig


def fig_rev_vehicle(s):
    g = s.groupby("vehicle_type")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    g["revenue_l"] = g["revenue"] / 1e5
    return vbar(g, "vehicle_type", "revenue_l", "Revenue by vehicle type (Rs lakh)", fmt=",.1f", ytitle="Rs lakh")


def fig_rev_payment(s):
    g = s[s.payment_method != "Unknown"].groupby("payment_method")["revenue"].sum().reset_index()
    g.columns = ["payment", "revenue"]
    return donut(g, "payment", "revenue", "Revenue by payment method")


def fig_reasons(d, col, title, color):
    g = d.loc[~d[col].isin(["None", "Unknown"]), col].value_counts().reset_index()
    g.columns = ["reason", "count"]
    if g.empty:
        return None
    g["share"] = g["count"] / g["count"].sum() * 100
    fig = hbar(g, "count", "reason", title, color=color, xtitle="Number of rides")
    return fig


def fig_rating_bands(s, col, title):
    r = s[col].dropna()
    bands = pd.cut(r, bins=[2.99, 3.49, 3.99, 4.49, 5.0],
                   labels=["Low (3.0-3.4)", "Average (3.5-3.9)", "Good (4.0-4.4)", "Excellent (4.5-5.0)"])
    g = bands.value_counts().reindex(["Low (3.0-3.4)", "Average (3.5-3.9)", "Good (4.0-4.4)",
                                      "Excellent (4.5-5.0)"]).reset_index()
    g.columns = ["band", "count"]
    g["share"] = g["count"] / max(g["count"].sum(), 1) * 100
    g["band"] = g["band"].astype(str)
    fig = px.bar(g, x="band", y="share")
    fig.update_traces(marker_color=[RED, GOLD, BLUE, TEAL], text=g["share"].values, texttemplate="%{text:.1f}%",
                      textposition="outside", textfont=dict(size=14, color=INK), cliponaxis=False)
    fig = finish(fig, title, height=400, yrange=[0, float(g["share"].max()) * 1.2 + 1])
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Share of rides (%)")
    return fig


# ----------------------------------------------------------------------------
# SECTIONS
# ----------------------------------------------------------------------------
def sec_title(d, S):
    head(1, "Project Title", "Cover page")
    st.markdown(
        '<div class="hero"><div class="hero-tag">DATA ANALYTICS PROJECT</div>'
        '<div class="hero-title">OLA Ride Analytics</div>'
        '<div class="hero-sub">Booking, Cancellation, Revenue and Customer Satisfaction Analysis</div>'
        '<div class="hero-tools">SQL Querying | Data Preprocessing | Power BI Dashboards | Streamlit App | '
        'Business Intelligence</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(f"{S['total']:,}", "Total bookings", f"{d['day'].min():%d %b} to {d['day'].max():%d %b %Y}")
    with c2:
        kpi(f"{S['succ_rate']:.1f}%", "Success rate", f"{S['n_success']:,} completed bookings", TEAL)
    with c3:
        kpi(inr(S["revenue"]), "Revenue", "From successful rides", ORANGE)
    with c4:
        kpi(f"{S['avg_cust']:.2f} / 5" if not np.isnan(S["avg_cust"]) else "N/A", "Avg customer rating",
            "Successful rides only", PURPLE)


def sec_summary(d, S):
    head(2, "Project Summary", "What this project is and how it was built")
    card("About the project",
         f"This project studies <b>{S['total']:,} OLA cab, auto and bike bookings</b> made between "
         f"<b>{d['day'].min():%d %b %Y}</b> and <b>{d['day'].max():%d %b %Y}</b>, across "
         f"<b>{S['n_vehicles']} vehicle types</b> and <b>{S['n_areas']} pickup areas</b>. "
         f"It shows how many bookings succeed, why rides get cancelled, how much revenue is earned, "
         f"and how happy customers are, so that OLA can take better decisions.")
    st.markdown("#### How the project was built")
    steps = [
        ("Step 1: SQL querying", "Booking data was queried with SQL to answer questions such as success rate, "
                                 "cancellations by reason, revenue by vehicle and average ratings."),
        ("Step 2: Data preprocessing", "Missing values were handled, dates and times were converted, "
                                       "flag columns (success, cancelled, incomplete) and revenue columns were created "
                                       "and the cleaned file <b>ola_cleaned.csv</b> was saved."),
        ("Step 3: Power BI dashboards", "A 5-page Power BI report was built: Overall, Vehicle Type, Revenue, "
                                        "Cancellation and Ratings."),
        ("Step 4: Streamlit app", "This web app brings every finding, chart and recommendation into one "
                                  "13-section story."),
    ]
    c1, c2 = st.columns(2)
    for i, (t, b) in enumerate(steps):
        with (c1 if i % 2 == 0 else c2):
            card(t, b, "gold" if i % 2 else "")
    st.markdown("#### Dataset at a glance")
    glance = pd.DataFrame({
        "Item": ["Total bookings", "Time period", "Vehicle types", "Pickup areas", "Successful bookings",
                 "Cancelled or not completed"],
        "Value": [f"{S['total']:,}", f"{d['day'].min():%d %b %Y} to {d['day'].max():%d %b %Y}",
                  str(S["n_vehicles"]), str(S["n_areas"]), f"{S['n_success']:,} ({S['succ_rate']:.1f}%)",
                  f"{S['n_failed']:,} ({S['fail_rate']:.1f}%)"],
    })
    html_table(glance)


def sec_objective(d, S):
    head(3, "Business Objective", "What OLA wants to achieve with this analysis")
    card("Main objective",
         "Increase the number of completed rides and the revenue from them, by understanding "
         "<b>why bookings fail</b> and <b>how satisfied customers are</b>.")
    c1, c2 = st.columns(2)
    with c1:
        card("Specific goals", bullets([
            "Measure booking success, cancellation and incomplete-ride rates.",
            "Find which vehicle types and payment methods earn the most revenue.",
            "Find the reasons behind customer and driver cancellations.",
            "Find the pickup areas with the best ratings.",
            "Measure customer satisfaction and find ways to raise it.",
            "Give clear, data-backed recommendations to the business team.",
        ]))
    with c2:
        card("Questions this project answers", bullets([
            "How many bookings are successful, and how many fail?",
            "Why are rides getting cancelled?",
            "Which vehicle types and areas bring the most revenue?",
            "Where are the top ratings coming from?",
            "How satisfied are customers, and what should be increased?",
        ]), "good")
    st.markdown("#### KPIs tracked")
    kp = pd.DataFrame({
        "KPI": ["Success rate", "Cancellation rate", "Revenue", "Average booking value",
                "Customer satisfaction (rated 4 or more)", "Incomplete ride rate"],
        "Current value": [f"{S['succ_rate']:.1f}%", f"{pct(S['n_cancel'], S['total']):.1f}%", inr(S["revenue"]),
                          inr(S["avg_value"]), f"{S['sat']:.1f}%", f"{S['incomplete_rate']:.1f}%"],
        "Why it matters": ["Shows how many requests turn into rides", "Shows lost demand due to cancels",
                           "Shows income from completed rides", "Shows value of a typical ride",
                           "Shows how many customers are happy", "Shows rides that start but do not finish"],
    })
    html_table(kp)


def sec_findings(d, S):
    head(4, "Key Findings", "The most important numbers from the data")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(f"{S['succ_rate']:.1f}%", "Success rate", f"{S['n_success']:,} rides", TEAL)
    with c2:
        kpi(f"{S['fail_rate']:.1f}%", "Bookings that fail", f"{S['n_failed']:,} requests", RED)
    with c3:
        kpi(inr(S["revenue"]), "Revenue earned", "Successful rides", BLUE)
    with c4:
        kpi(inr(S["lost"]), "Booking value lost", "On failed bookings", ORANGE)
    drv_share = pct(S["n_drv"], S["n_cancel"])
    dr = S["drv_reasons"]
    cr = S["cust_reasons"]
    c1, c2 = st.columns(2)
    with c1:
        card(f"1. Only {S['succ_rate']:.0f} in every 100 bookings succeed",
             f"<b>{S['succ_rate']:.1f}%</b> of bookings are completed. The other <b>{S['fail_rate']:.1f}%</b> "
             f"are cancelled by the customer, cancelled by the driver, or end with no driver found.", "warn")
        card("2. Drivers cancel more than customers",
             f"Drivers cancel <b>{S['n_drv']:,}</b> rides and customers cancel <b>{S['n_cust']:,}</b>. "
             f"Driver cancellations are <b>{drv_share:.0f}%</b> of all cancellations. "
             f"Another <b>{S['n_nf']:,}</b> requests found no driver at all.", "warn")
        card("3. Cancellation reasons",
             f"Top driver reason: <b>{dr.index[0] if len(dr) else 'N/A'}</b>. "
             f"Top customer reason: <b>{cr.index[0] if len(cr) else 'N/A'}</b>. "
             f"About <b>{S['cust_driver_linked']:.0f}%</b> of customer cancellations are linked to driver behaviour.")
        card("4. Vehicle types perform similarly",
             f"<b>{S['rev_vehicle']}</b> earns the most revenue. <b>{S['best_succ_vehicle']}</b> has the best "
             f"success rate (<b>{S['best_succ_rate']:.1f}%</b>) and <b>{S['worst_succ_vehicle']}</b> the lowest "
             f"(<b>{S['worst_succ_rate']:.1f}%</b>).", "good")
    with c2:
        card("5. Cash is still the biggest payment mode",
             f"<b>{S['cash_share']:.1f}%</b> of successful rides are paid in cash, "
             f"<b>{S['upi_share']:.1f}%</b> by UPI and <b>{S['digital_share']:.1f}%</b> through UPI or cards together.",
             "gold")
        card("6. Customers are fairly satisfied",
             f"Average customer rating is <b>{S['avg_cust']:.2f}</b> and driver rating is <b>{S['avg_drv']:.2f}</b> "
             f"out of 5. <b>{S['sat']:.1f}%</b> of rated rides are 4.0 or above.", "good")
        card("7. Some rides do not finish",
             f"<b>{S['n_incomplete']:,}</b> successful bookings (<b>{S['incomplete_rate']:.1f}%</b>) were "
             f"incomplete. Top reason: <b>{S['inc_reasons'].index[0] if len(S['inc_reasons']) else 'N/A'}</b>.")
        card("8. Demand is steady through the day",
             f"Busiest hour is <b>{S['peak_hour']:02d}:00</b>, but it is only <b>{S['hour_spread']:.0f}%</b> "
             f"busier than the quietest hour. Average ride distance is <b>{S['avg_dist']:.1f} km</b> and average "
             f"booking value is <b>{inr(S['avg_value'])}</b>.")


def sec_problem(d, S):
    head(5, "Problem Statement", "The business problem we are solving")
    card("The problem",
         f"Out of every 100 booking requests, about <b>{S['fail_rate']:.0f}</b> do not become a completed ride. "
         f"These failed bookings are worth about <b>{inr(S['lost'])}</b> in booking value that OLA does not earn. "
         f"At the same time, OLA does not clearly know <b>why</b> rides are cancelled, "
         f"<b>which areas</b> give the best service, or <b>how satisfied</b> customers really are.", "warn")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(f"{S['n_failed']:,}", "Failed bookings", f"{S['fail_rate']:.1f}% of all requests", RED)
    with c2:
        kpi(f"{S['n_drv']:,}", "Driver cancellations", f"{pct(S['n_drv'], S['total']):.1f}% of requests", ORANGE)
    with c3:
        kpi(f"{S['n_nf']:,}", "Driver not found", f"{pct(S['n_nf'], S['total']):.1f}% of requests", GOLD)
    with c4:
        kpi(inr(S["lost"]), "Booking value lost", "Failed bookings", RED)
    c1, c2 = st.columns(2)
    with c1:
        card("Challenges", bullets([
            "A large share of bookings is lost to cancellations and missing drivers.",
            "Customers cancel when drivers do not move towards the pickup point.",
            "Drivers cancel for personal, vehicle or customer-related reasons.",
            "Many rides are still paid in cash.",
            "Some rides start but are never completed.",
        ]))
    with c2:
        card("Problem statement in one line",
             "<b>How can OLA convert more booking requests into completed, well-rated rides by reducing "
             "cancellations and improving driver availability and customer satisfaction?</b>", "good")


def sec_increase(d, S):
    head(6, "What We Should Increase", "Growth levers with suggested targets")
    gain_rides = 0.05 * S["total"]
    gain_value = gain_rides * S["avg_value"]
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi(f"+{gain_rides:,.0f}", "Extra rides", "If success rate rises by 5 points", TEAL)
    with c2:
        kpi(inr(gain_value), "Extra revenue", "From those extra rides", BLUE)
    with c3:
        kpi(inr(S["lost"]), "Total value at stake", "Currently lost on failed bookings", RED)
    levers = pd.DataFrame({
        "Metric": ["Booking success rate", "Ride completion rate", "Digital payment share",
                   "Customers rating 4.0 or above", "Customers rating 4.5 or above"],
        "Current": [S["succ_rate"], 100 - S["incomplete_rate"], S["digital_share"], S["sat"], S["high_sat"]],
        "Target": [min(S["succ_rate"] + 5, 100), min(100 - S["incomplete_rate"] + 3, 100),
                   min(S["digital_share"] + 15, 100), min(S["sat"] + 10, 100), min(S["high_sat"] + 10, 100)],
    })
    long = levers.melt(id_vars="Metric", var_name="Type", value_name="Percent")
    fig = px.bar(long, x="Metric", y="Percent", color="Type", barmode="group",
                 color_discrete_map={"Current": BLUE, "Target": TEAL})
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", textfont=dict(size=13, color=INK),
                      cliponaxis=False)
    fig = finish(fig, "Current level vs suggested target (%)", height=440, yrange=[0, 118], legend_bottom=True)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Percent")
    show(fig)
    note("Targets are suggested goals for planning, not predictions.")
    st.markdown("#### What to increase and how")
    plan = pd.DataFrame({
        "Increase": ["Booking success rate", "Driver availability", "Pickup tracking and driver discipline",
                     "Digital payments", "Ride completion", "Customer ratings"],
        "Why": [f"{S['fail_rate']:.1f}% of requests fail",
                f"{S['n_nf']:,} requests found no driver",
                f"{S['cust_driver_linked']:.0f}% of customer cancels are driver-linked",
                f"Cash is {S['cash_share']:.0f}% of paid rides",
                f"{S['n_incomplete']:,} rides were incomplete",
                f"Only {S['sat']:.0f}% of rides are rated 4.0 or more"],
        "How": ["Fix the top cancellation reasons", "Driver incentives in busy areas and hours",
                "Live ETA, auto-reassign idle drivers", "UPI and card cashback offers",
                "Vehicle health checks before trips", "Driver training and feedback follow-up"],
    })
    html_table(plan)


def sec_charts(d, S):
    head(7, "Charts and Graphs", "Bookings, revenue, vehicles, areas and timing")
    s = S["s"]
    t1, t2, t3, t4 = st.tabs(["Bookings", "Revenue", "Vehicle types", "Areas and time"])
    with t1:
        c1, c2 = st.columns([3, 2])
        with c1:
            show(fig_daily_status(d))
        with c2:
            show(fig_status_donut(d))
        stages = pd.DataFrame({
            "stage": ["Booking requests", "Driver found", "Ride confirmed (not cancelled)", "Ride completed"],
            "count": [S["total"], S["total"] - S["n_nf"], S["n_success"], S["n_success"] - S["n_incomplete"]],
        })
        fig = px.funnel(stages, x="count", y="stage", color_discrete_sequence=[BLUE])
        fig.update_traces(textinfo="value+percent initial", textfont=dict(size=15, color="#FFFFFF"))
        fig = finish(fig, "Booking funnel: from request to completed ride", height=380)
        fig.update_yaxes(title_text="")
        show(fig)
    with t2:
        c1, c2 = st.columns([3, 2])
        with c1:
            show(fig_daily_revenue(s))
        with c2:
            show(fig_rev_payment(s))
        c3, c4 = st.columns(2)
        with c3:
            show(fig_rev_vehicle(s))
        with c4:
            g = s[s.pickup_location != "Unknown"].groupby("pickup_location")["revenue"].sum().nlargest(10)
            g = (g / 1e5).reset_index()
            g.columns = ["area", "revenue_l"]
            show(hbar(g, "revenue_l", "area", "Top 10 pickup areas by revenue (Rs lakh)", color=ORANGE, fmt=",.1f"))
    with t3:
        vs = d.groupby(["vehicle_type", "booking_status"]).size().reset_index(name="n")
        vs["share"] = vs["n"] / vs.groupby("vehicle_type")["n"].transform("sum") * 100
        fig = px.bar(vs, x="vehicle_type", y="share", color="booking_status", color_discrete_map=STATUS_COLORS,
                     color_discrete_sequence=PALETTE)
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="inside", textfont=dict(size=12, color="#FFFFFF"))
        fig = finish(fig, "Booking outcome by vehicle type (%)", height=440, legend_bottom=True)
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="Share of bookings (%)")
        show(fig)
        c1, c2 = st.columns(2)
        va = s.groupby("vehicle_type").agg(avg_dist=("ride_distance", "mean"),
                                           avg_value=("booking_value", "mean")).reset_index()
        with c1:
            show(vbar(va, "vehicle_type", "avg_dist", "Average ride distance (km)", fmt=".1f", ytitle="km"))
        with c2:
            show(vbar(va, "vehicle_type", "avg_value", "Average booking value (Rs)", fmt=",.0f", ytitle="Rs"))
    with t4:
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hm = d.dropna(subset=["hour"]).groupby(["weekday", "hour"]).size().unstack(fill_value=0)
        hm = hm.reindex([w for w in order if w in hm.index])
        fig = px.imshow(hm, aspect="auto", color_continuous_scale="Blues",
                        labels=dict(x="Hour of day", y="Day of week", color="Bookings"))
        fig = finish(fig, "When do bookings happen? (day of week by hour)", height=420)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_coloraxes(colorbar=dict(tickfont=dict(color=INK, size=12), title=dict(font=dict(color=INK))))
        show(fig)
        c1, c2 = st.columns(2)
        with c1:
            hh = d.dropna(subset=["hour"]).groupby("hour").size().reset_index(name="bookings")
            hh["hour"] = hh["hour"].astype(int)
            fig = px.bar(hh, x="hour", y="bookings", color_discrete_sequence=[BLUE])
            fig = finish(fig, "Bookings by hour of day", height=400, yrange=[0, float(hh["bookings"].max()) * 1.15])
            fig.update_xaxes(title_text="Hour (0-23)", dtick=2)
            fig.update_yaxes(title_text="Bookings")
            show(fig)
        with c2:
            fig = px.histogram(s, x="ride_distance", nbins=25, color_discrete_sequence=[TEAL])
            fig.update_traces(marker_line_color="white", marker_line_width=1)
            fig = finish(fig, "Ride distance of successful rides", height=400)
            fig.update_xaxes(title_text="Distance (km)")
            fig.update_yaxes(title_text="Number of rides")
            show(fig)


def sec_cancel(d, S):
    head(8, "Why Cancellation Is Happening", "Reasons given by customers and drivers")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(f"{S['n_cust']:,}", "Cancelled by customer", f"{pct(S['n_cust'], S['total']):.1f}% of bookings", ORANGE)
    with c2:
        kpi(f"{S['n_drv']:,}", "Cancelled by driver", f"{pct(S['n_drv'], S['total']):.1f}% of bookings", RED)
    with c3:
        kpi(f"{S['n_nf']:,}", "Driver not found", f"{pct(S['n_nf'], S['total']):.1f}% of bookings", GOLD)
    with c4:
        kpi(f"{S['n_incomplete']:,}", "Incomplete rides", f"{S['incomplete_rate']:.1f}% of successful", PURPLE)
    cr, dr = S["cust_reasons"], S["drv_reasons"]
    if len(cr) and len(dr):
        answer(f"Short answer: most cancellations come from the driver side. The top driver reason is "
               f"'{dr.index[0]}' ({pct(int(dr.iloc[0]), int(dr.sum())):.0f}% of driver cancels), and "
               f"{S['cust_driver_linked']:.0f}% of customer cancels are because of driver behaviour "
               f"(top: '{cr.index[0]}').")
    c1, c2 = st.columns([2, 3])
    with c1:
        g = pd.DataFrame({"who": ["Cancelled by driver", "Cancelled by customer", "Driver not found"],
                          "count": [S["n_drv"], S["n_cust"], S["n_nf"]]})
        show(donut(g, "who", "count", "Who or what causes failed bookings",
                   colors={"Cancelled by driver": RED, "Cancelled by customer": ORANGE, "Driver not found": GOLD}))
    with c2:
        f = fig_reasons(d, "canceled_rides_by_driver", "Why drivers cancel", RED)
        if f:
            show(f)
        else:
            note("No driver cancellation reasons in the current selection.")
    c1, c2 = st.columns(2)
    with c1:
        f = fig_reasons(d, "canceled_rides_by_customer", "Why customers cancel", ORANGE)
        if f:
            show(f)
        else:
            note("No customer cancellation reasons in the current selection.")
    with c2:
        f = fig_reasons(d, "incomplete_rides_reason", "Why rides stay incomplete", PURPLE)
        if f:
            show(f)
        else:
            note("No incomplete ride reasons in the current selection.")
    c1, c2 = st.columns(2)
    with c1:
        v = d.groupby("vehicle_type").apply(
            lambda x: pct(int((x.is_cust_cancel | x.is_driver_cancel).sum()), len(x))).reset_index()
        v.columns = ["vehicle_type", "rate"]
        show(vbar(v, "vehicle_type", "rate", "Cancellation rate by vehicle type (%)", fmt=".1f", suffix="%",
                  ytitle="% of bookings"))
    with c2:
        a = d[d.pickup_location != "Unknown"].groupby("pickup_location").apply(
            lambda x: pct(int((x.is_cust_cancel | x.is_driver_cancel).sum()), len(x))).nlargest(10).reset_index()
        a.columns = ["area", "rate"]
        show(hbar(a, "rate", "area", "Top 10 areas by cancellation rate (%)", color=RED, fmt=".1f", suffix="%"))


def sec_areas(d, S):
    head(9, "Top Rated Areas", "Which pickup areas receive the best ratings")
    g = area_stats(d)
    if g.empty:
        note("No rated rides in the current selection.")
        return
    max_v = max(int(g["successful_rides"].max()), 1)
    min_rides = st.slider("Minimum successful rides per area (to avoid ranking areas with very few rides)",
                          0, max_v, min(100, max_v))
    gg = g[g["successful_rides"] >= min_rides]
    if gg.empty:
        note("No area meets this minimum. Lower the slider.")
        return
    best = gg.sort_values("overall_rating", ascending=False).iloc[0]
    worst = gg.sort_values("overall_rating", ascending=True).iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi(best["pickup_location"], "Top rated area", f"Overall rating {best['overall_rating']:.3f}", TEAL)
    with c2:
        kpi(worst["pickup_location"], "Lowest rated area", f"Overall rating {worst['overall_rating']:.3f}", RED)
    with c3:
        kpi(f"{best['overall_rating'] - worst['overall_rating']:.3f}", "Gap between best and lowest",
            "Rating points (out of 5)", GOLD)
    answer(f"{best['pickup_location']} has the highest rating ({best['overall_rating']:.3f} out of 5), followed by "
           f"{gg.sort_values('overall_rating', ascending=False).iloc[1]['pickup_location'] if len(gg) > 1 else 'N/A'}. "
           f"The gap between best and lowest area is only {best['overall_rating'] - worst['overall_rating']:.3f}, "
           f"so service quality is very consistent across areas.")
    top = gg.sort_values("overall_rating", ascending=False).head(10)
    low = gg.sort_values("overall_rating", ascending=True).head(10)
    lo = float(min(top["overall_rating"].min(), low["overall_rating"].min())) - 0.02
    hi = float(max(top["overall_rating"].max(), low["overall_rating"].max())) + 0.012
    c1, c2 = st.columns(2)
    with c1:
        show(hbar(top, "overall_rating", "pickup_location", "Top 10 areas by overall rating", color=TEAL, fmt=".3f",
                  xrange=[lo, hi]))
    with c2:
        show(hbar(low, "overall_rating", "pickup_location", "10 lowest rated areas", color=RED, fmt=".3f",
                  xrange=[lo, hi]))
    note(f"The rating charts start near {lo:.2f} instead of 0 so that small differences between areas are visible.")
    c1, c2 = st.columns(2)
    with c1:
        b = gg.sort_values("successful_rides", ascending=False).head(10)
        show(hbar(b, "successful_rides", "pickup_location", "Top 10 areas by successful rides", color=BLUE))
    with c2:
        r = gg.sort_values("revenue", ascending=False).head(10).copy()
        r["revenue_l"] = r["revenue"] / 1e5
        show(hbar(r, "revenue_l", "pickup_location", "Top 10 areas by revenue (Rs lakh)", color=ORANGE, fmt=",.1f"))
    st.markdown("#### All areas (sorted by overall rating)")
    tbl = gg.sort_values("overall_rating", ascending=False).copy()
    tbl["revenue"] = tbl["revenue"].round(0)
    tbl[["driver_rating", "customer_rating", "overall_rating"]] = tbl[
        ["driver_rating", "customer_rating", "overall_rating"]].round(3)
    tbl.columns = ["Pickup area", "Successful rides", "Driver rating", "Customer rating", "Revenue (Rs)",
                   "Overall rating"]
    show_table(tbl)


def sec_satisfaction(d, S):
    head(10, "Customer Satisfaction", "How happy customers and drivers are")
    s = S["s"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(f"{S['avg_cust']:.2f}", "Avg customer rating", "Out of 5", PURPLE)
    with c2:
        kpi(f"{S['avg_drv']:.2f}", "Avg driver rating", "Out of 5", BLUE)
    with c3:
        kpi(f"{S['sat']:.1f}%", "Satisfied customers", "Rating 4.0 or above", TEAL)
    with c4:
        kpi(f"{S['low_sat']:.1f}%", "Unhappy customers", "Rating below 3.5", RED)
    answer(f"{S['sat']:.1f}% of customers rate their ride 4.0 or higher and {S['high_sat']:.1f}% rate it 4.5 or "
           f"higher. About {S['low_sat']:.1f}% rate below 3.5, so there is clear room to improve.")
    c1, c2 = st.columns(2)
    with c1:
        show(fig_rating_bands(s, "customer_rating", "Customer rating bands (share of rides)"))
    with c2:
        show(fig_rating_bands(s, "driver_ratings", "Driver rating bands (share of rides)"))
    c1, c2 = st.columns(2)
    with c1:
        v = s.dropna(subset=["customer_rating"]).groupby("vehicle_type")["customer_rating"].apply(
            lambda x: pct(int((x >= 4).sum()), len(x))).reset_index()
        v.columns = ["vehicle_type", "sat"]
        show(vbar(v, "vehicle_type", "sat", "Satisfied customers by vehicle type (%)", fmt=".1f", suffix="%",
                  ytitle="% rated 4.0 or above"))
    with c2:
        sb = s.dropna(subset=["customer_rating"]).copy()
        sb["band"] = pd.cut(sb["ride_distance"], bins=[0, 10, 20, 30, 40, 100],
                            labels=["0-10 km", "10-20 km", "20-30 km", "30-40 km", "40+ km"])
        k = sb.groupby("band", observed=True)["customer_rating"].apply(
            lambda x: pct(int((x >= 4).sum()), len(x))).reset_index()
        k.columns = ["band", "sat"]
        k["band"] = k["band"].astype(str)
        show(vbar(k, "band", "sat", "Satisfied customers by ride distance (%)", color=TEAL, fmt=".1f", suffix="%",
                  ytitle="% rated 4.0 or above"))
    st.markdown("#### Average ratings by vehicle type")
    t = s.groupby("vehicle_type").agg(rides=("booking_id", "count"), cust=("customer_rating", "mean"),
                                      drv=("driver_ratings", "mean")).reset_index()
    t.columns = ["Vehicle type", "Successful rides", "Avg customer rating", "Avg driver rating"]
    t["Successful rides"] = t["Successful rides"].map(lambda v: f"{v:,}")
    t["Avg customer rating"] = t["Avg customer rating"].map(lambda v: f"{v:.3f}")
    t["Avg driver rating"] = t["Avg driver rating"].map(lambda v: f"{v:.3f}")
    html_table(t)
    inc = s.dropna(subset=["customer_rating"])
    a = inc.loc[inc.is_incomplete, "customer_rating"].mean()
    b = inc.loc[~inc.is_incomplete, "customer_rating"].mean()
    if not (np.isnan(a) or np.isnan(b)):
        card("Do incomplete rides hurt ratings?",
             f"Average customer rating is <b>{b:.2f}</b> for completed rides and <b>{a:.2f}</b> for incomplete rides.")


DAX = """Total Bookings = COUNTROWS('Ola')

Successful Bookings =
CALCULATE(COUNTROWS('Ola'), 'Ola'[Booking_Status] = "Success")

Success Rate % = DIVIDE([Successful Bookings], [Total Bookings])

Cancellation Rate % =
DIVIDE(
    CALCULATE(COUNTROWS('Ola'),
        'Ola'[Booking_Status] IN {"Canceled by Customer", "Canceled by Driver"}),
    [Total Bookings])

Total Booking Value = SUM('Ola'[Booking_Value])

Success Booking Value =
CALCULATE(SUM('Ola'[Booking_Value]), 'Ola'[Booking_Status] = "Success")

Avg Distance Travelled = AVERAGE('Ola'[Ride_Distance])
Total Distance Travelled = SUM('Ola'[Ride_Distance])
Avg Driver Rating = AVERAGE('Ola'[Driver_Ratings])
Avg Customer Rating = AVERAGE('Ola'[Customer_Rating])"""


def sec_powerbi(d, S):
    head(11, "Power BI Dashboards", "The 5 report pages: Overall, Vehicle Type, Revenue, Cancellation, Ratings")
    s = S["s"]
    tabs = st.tabs(["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"])
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi(f"{S['total']:,}", "Total bookings", "", BLUE)
        with c2:
            kpi(f"{S['succ_rate']:.1f}%", "Success rate", "", TEAL)
        with c3:
            kpi(f"{pct(S['n_cancel'], S['total']):.1f}%", "Cancellation rate", "", RED)
        with c4:
            kpi(inr(S["revenue"]), "Success booking value", "", ORANGE)
        c1, c2 = st.columns([3, 2])
        with c1:
            show(fig_daily_status(d))
        with c2:
            show(fig_status_donut(d))
    with tabs[1]:
        t = d.groupby("vehicle_type").agg(total=("booking_value", "sum")).reset_index()
        sv = s.groupby("vehicle_type").agg(succ=("booking_value", "sum"), avgd=("ride_distance", "mean"),
                                           totd=("ride_distance", "sum")).reset_index()
        t = t.merge(sv, on="vehicle_type", how="left").fillna(0).sort_values("succ", ascending=False)
        out = pd.DataFrame({
            "Vehicle Type": t["vehicle_type"],
            "Total Booking Value": t["total"].map(inr),
            "Success Booking Value": t["succ"].map(inr),
            "Avg. Distance Travelled": t["avgd"].map(lambda v: f"{v:.1f} km"),
            "Total Distance Travelled": t["totd"].map(lambda v: f"{v:,.0f} km"),
        })
        html_table(out)
        show(fig_rev_vehicle(s))
    with tabs[2]:
        c1, c2 = st.columns([3, 2])
        with c1:
            show(fig_daily_revenue(s))
        with c2:
            show(fig_rev_payment(s))
    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1:
            f = fig_reasons(d, "canceled_rides_by_customer", "Customer cancellation reasons", ORANGE)
            if f:
                show(f)
        with c2:
            f = fig_reasons(d, "canceled_rides_by_driver", "Driver cancellation reasons", RED)
            if f:
                show(f)
    with tabs[4]:
        r = s.groupby("vehicle_type").agg(drv=("driver_ratings", "mean"), cust=("customer_rating", "mean"),
                                          n=("booking_id", "count")).reset_index()
        out = pd.DataFrame({
            "Vehicle Type": r["vehicle_type"],
            "Avg Driver Rating": r["drv"].map(lambda v: f"{v:.3f}"),
            "Avg Customer Rating": r["cust"].map(lambda v: f"{v:.3f}"),
            "Rated rides": r["n"].map(lambda v: f"{v:,}"),
        })
        html_table(out)
        c1, c2 = st.columns(2)
        with c1:
            show(fig_rating_bands(s, "driver_ratings", "Driver rating bands"))
        with c2:
            show(fig_rating_bands(s, "customer_rating", "Customer rating bands"))
    st.markdown("#### Use this data in Power BI")
    clean = d.drop(columns=["day", "weekday", "hour", "is_success", "is_cust_cancel", "is_driver_cancel",
                            "is_not_found", "is_incomplete", "revenue"])
    st.download_button("Download cleaned data (CSV)", clean.to_csv(index=False).encode("utf-8"), "ola_cleaned.csv",
                       "text/csv")
    st.markdown("**DAX measures used in the report**")
    st.code(DAX, language="sql")
    url = st.text_input("Power BI embed link (optional)", placeholder="https://app.powerbi.com/reportEmbed?reportId=...")
    if url.strip().startswith("https://"):
        frame = (f'<iframe title="Power BI" width="100%" height="600" src="{html.escape(url.strip())}" '
                 f'frameborder="0" allowFullScreen="true"></iframe>')
        try:
            import streamlit.components.v1 as components
            components.html(frame, height=620)
        except Exception:
            st.markdown(f"[Open the Power BI report]({url.strip()})")


def sec_insights(d, S):
    head(12, "Business Insights and Recommendations", "What the data says and what to do about it")
    s = S["s"]
    dr, cr = S["drv_reasons"], S["cust_reasons"]
    supply_share = pct(S["n_drv"] + S["n_nf"], S["n_failed"])
    st.markdown("#### Business insights")
    c1, c2 = st.columns(2)
    with c1:
        card("1. Failures are mostly a supply problem",
             f"Driver cancellations plus 'driver not found' make up <b>{supply_share:.0f}%</b> of all failed "
             f"bookings.", "warn")
        card("2. Money is being left on the table",
             f"Failed bookings represent about <b>{inr(S['lost'])}</b> of booking value, compared with "
             f"<b>{inr(S['revenue'])}</b> earned.", "warn")
        card("3. Customers cancel because of drivers",
             f"<b>{S['cust_driver_linked']:.0f}%</b> of customer cancellations are linked to the driver "
             f"(top reason: <b>{cr.index[0] if len(cr) else 'N/A'}</b>).")
    with c2:
        card("4. Demand is steady, so supply must be steady too",
             f"Bookings are spread evenly over the day (busiest hour {S['peak_hour']:02d}:00 is only "
             f"<b>{S['hour_spread']:.0f}%</b> above the quietest). Vehicle types perform similarly, "
             f"with <b>{S['best_succ_vehicle']}</b> slightly ahead.", "gold")
        card("5. Cash is still the largest payment mode",
             f"Cash is <b>{S['cash_share']:.0f}%</b> and UPI <b>{S['upi_share']:.0f}%</b> of paid rides.", "gold")
        card("6. Service quality is consistent",
             f"Ratings average about <b>{S['avg_cust']:.1f}</b> in every area and vehicle type, but only "
             f"<b>{S['sat']:.0f}%</b> of rides get 4.0 or more.", "good")
    st.markdown("#### Business recommendations")
    avg = S["avg_value"]
    recs = pd.DataFrame({
        "Priority": ["High", "High", "High", "Medium", "Medium", "Medium"],
        "Recommendation": [
            "Reduce driver cancellations",
            "Improve driver availability",
            "Fix pickup experience for customers",
            "Promote digital payments",
            "Cut incomplete rides",
            "Raise customer ratings",
        ],
        "Evidence from data": [
            f"{S['n_drv']:,} driver cancels; top reason: {dr.index[0] if len(dr) else 'N/A'}",
            f"{S['n_nf']:,} requests ({pct(S['n_nf'], S['total']):.1f}%) found no driver",
            f"Driver not moving towards pickup is the top customer reason; {S['cust_driver_linked']:.0f}% are driver-linked",
            f"Cash is {S['cash_share']:.0f}% of paid rides",
            f"{S['n_incomplete']:,} incomplete rides; top reason: "
            f"{S['inc_reasons'].index[0] if len(S['inc_reasons']) else 'N/A'}",
            f"Only {S['sat']:.0f}% rated 4.0+; {S['low_sat']:.0f}% rated below 3.5",
        ],
        "Action": [
            "Incentives for completed trips, penalties for repeat cancels, vehicle readiness checks",
            "Driver incentives in busy areas, better driver matching and pre-positioning",
            "Live ETA and driver tracking, auto-reassign drivers who are not moving",
            "UPI and card cashback, wallet offers",
            "Vehicle health checks before trips, quick replacement vehicle",
            "Driver training, quick feedback follow-up for low ratings",
        ],
        "Expected impact": [
            f"Recovering 25% of driver cancels = about {inr(0.25 * S['n_drv'] * avg)}",
            f"Finding drivers for half of them = about {inr(0.5 * S['n_nf'] * avg)}",
            "Fewer customer cancels and better ratings",
            "Faster payments, less cash handling",
            "More completed rides and happier customers",
            "More repeat bookings",
        ],
    })
    html_table(recs)


def sec_conclusion(d, S):
    head(13, "Conclusion", "Summary of the whole project")
    card("What we did",
         f"We cleaned and analysed <b>{S['total']:,}</b> OLA bookings using SQL, Python data preprocessing, "
         f"Power BI dashboards and this Streamlit app, and turned the data into clear business insights.")
    c1, c2 = st.columns(2)
    with c1:
        card("What we found", bullets([
            f"Only <b>{S['succ_rate']:.1f}%</b> of bookings are completed; <b>{S['fail_rate']:.1f}%</b> fail.",
            f"Most failures come from the driver side: driver cancellations and no driver found.",
            f"About <b>{inr(S['lost'])}</b> of booking value is lost on failed bookings.",
            f"Customers are fairly happy (average <b>{S['avg_cust']:.2f}</b>), but only "
            f"<b>{S['sat']:.0f}%</b> give 4.0 or more.",
            "Ratings and revenue are very similar across areas and vehicle types.",
        ]), "warn")
    with c2:
        card("What should be done", bullets([
            "Reduce driver cancellations with incentives and penalties.",
            "Add drivers in busy areas to cut 'driver not found'.",
            "Give customers live ETA and driver tracking.",
            "Push UPI and card payments with offers.",
            "Check vehicles before trips to reduce incomplete rides.",
            "Follow up on low ratings to lift satisfaction.",
        ]), "good")
    card("Final conclusion",
         "Improving driver availability and reducing cancellations is the fastest way for OLA to earn more "
         "revenue and raise customer satisfaction. Even a small rise in the success rate adds thousands of "
         "completed rides and lakhs of rupees in revenue.", "good")
    st.markdown(
        '<div class="credit"><div class="credit-small">Created by</div>'
        '<div class="credit-name">Challapalli Mamatha</div>'
        '<div class="credit-small">SQL | Data Preprocessing | Power BI | Streamlit | Business Intelligence</div></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# SIDEBAR: NAVIGATION, DATA, FILTERS
# ----------------------------------------------------------------------------
def go_to(idx):
    st.session_state["nav"] = SECTIONS[idx]


st.sidebar.markdown("### OLA Ride Analytics")
st.sidebar.markdown("**Navigation**")
page = st.sidebar.radio("Go to section", SECTIONS, key="nav", label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("**Data**")
up = st.sidebar.file_uploader("Upload ola_cleaned.csv (optional)", type=["csv", "xlsx", "xls"])
try:
    data, source = load_data(up.getvalue() if up else None, up.name if up else None)
except Exception as exc:
    st.error(f"Could not read the file: {exc}")
    st.stop()
if source == "sample data":
    st.sidebar.markdown("Showing sample data. Put ola_cleaned.csv next to this file or upload it above.")
else:
    st.sidebar.markdown(f"Data loaded from: {os.path.basename(source)}")

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")
dmin, dmax = data["day"].min().date(), data["day"].max().date()
date_sel = st.sidebar.date_input("Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
if isinstance(date_sel, (tuple, list)):
    start = date_sel[0]
    end = date_sel[1] if len(date_sel) > 1 else date_sel[0]
else:
    start = end = date_sel
veh_all = sorted(data["vehicle_type"].unique())
veh_sel = st.sidebar.multiselect("Vehicle type", veh_all, default=veh_all)

df = data[(data["day"].dt.date >= start) & (data["day"].dt.date <= end) & (data["vehicle_type"].isin(veh_sel))].copy()
if df.empty:
    st.warning("No bookings match the current filters. Please widen the filters in the sidebar.")
    st.stop()

STATS = compute(df)

ROUTES = {
    SECTIONS[0]: sec_title,
    SECTIONS[1]: sec_summary,
    SECTIONS[2]: sec_objective,
    SECTIONS[3]: sec_findings,
    SECTIONS[4]: sec_problem,
    SECTIONS[5]: sec_increase,
    SECTIONS[6]: sec_charts,
    SECTIONS[7]: sec_cancel,
    SECTIONS[8]: sec_areas,
    SECTIONS[9]: sec_satisfaction,
    SECTIONS[10]: sec_powerbi,
    SECTIONS[11]: sec_insights,
    SECTIONS[12]: sec_conclusion,
}
ROUTES[page](df, STATS)

# ----------------------------------------------------------------------------
# PREVIOUS / NEXT BUTTONS
# ----------------------------------------------------------------------------
idx = SECTIONS.index(page)
st.markdown("---")
b1, b2, b3 = st.columns([1, 4, 1])
with b1:
    if idx > 0:
        st.button("< Previous", key=f"prev_{idx}", on_click=go_to, args=(idx - 1,))
with b3:
    if idx < len(SECTIONS) - 1:
        st.button("Next >", key=f"next_{idx}", on_click=go_to, args=(idx + 1,))
