"""
OLA project - STEP 5: BUSINESS INTELLIGENCE INSIGHTS
=====================================================
Computes the key findings from data/ola_clean.csv and writes a Markdown report
with numbers, a "so what", and a recommendation for each theme.
Every statement is generated from the data - nothing is hard-coded - so the
report is only as real as the file you feed it.

Usage (from project root):
    python insights/05_bi_insights.py
    python insights/05_bi_insights.py --input data/ola_clean.csv --out insights/ola_insights_report.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def pct(x):
    return f"{x:.1%}"


def inr(x):
    return f"₹{x:,.0f}"


def build_report(df: pd.DataFrame) -> str:
    ok = df[df["is_success"] == 1]
    n = len(df)
    L: list[str] = []
    add = L.append

    # ------------------------------------------------------------ headline
    success = df["is_success"].mean()
    cust_c, drv_c, nodrv = df["is_cancel_customer"].mean(), df["is_cancel_driver"].mean(), df["is_driver_not_found"].mean()
    revenue = ok["booking_value"].sum()
    add("# OLA Ride Analytics - Business Intelligence Insights\n")
    add(f"*Period: {df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y} · {n:,} bookings*\n")
    add("## 1. Executive summary\n")
    add(f"- **{pct(success)}** of bookings complete; **{pct(1 - success)}** fail "
        f"(customer cancels {pct(cust_c)}, driver cancels {pct(drv_c)}, no driver found {pct(nodrv)}).")
    add(f"- Completed rides generated **{inr(revenue)}** at an average of **{inr(ok['booking_value'].mean())}** per ride "
        f"and **{ok['ride_distance'].mean():.1f} km** average distance.")
    biggest = max([("customer cancellations", cust_c), ("driver cancellations", drv_c), ("no-driver-found", nodrv)],
                  key=lambda t: t[1])
    add(f"- The biggest leak is **{biggest[0]}** ({pct(biggest[1])} of all bookings).\n")

    # ------------------------------------------------------------ revenue / vehicles
    add("## 2. Vehicle type\n")
    v = df.groupby("vehicle_type").agg(
        bookings=("booking_id", "count"), success=("is_success", "mean"),
        revenue=("success_booking_value", "sum"), dist=("ride_distance", "sum"),
        rides=("is_success", "sum"), avg_dist=("ride_distance", "mean"))
    v["avg_fare"] = v["revenue"] / v["rides"].replace(0, np.nan)
    v["rev_km"] = v["revenue"] / v["dist"].replace(0, np.nan)
    v["rev_share"] = v["revenue"] / v["revenue"].sum()
    v = v.sort_values("revenue", ascending=False)
    top, bot = v.index[0], v.index[-1]
    add("| Vehicle | Bookings | Success rate | Revenue | Share | Avg fare | Revenue/km |")
    add("|---|---:|---:|---:|---:|---:|---:|")
    for name, r in v.iterrows():
        add(f"| {name} | {int(r.bookings):,} | {pct(r.success)} | {inr(r.revenue)} | {pct(r.rev_share)} | {inr(r.avg_fare)} | {r.rev_km:.1f} |")
    add("")
    add(f"- **{top}** is the revenue leader ({pct(v.loc[top, 'rev_share'])} of revenue); **{bot}** contributes the least "
        f"({pct(v.loc[bot, 'rev_share'])}).")
    best_km = v["rev_km"].idxmax()
    add(f"- **{best_km}** earns the most per km ({v.loc[best_km, 'rev_km']:.1f}), so its distance is the most monetised.")
    worst_s, best_s = v["success"].idxmin(), v["success"].idxmax()
    add(f"- Success rate ranges from **{pct(v.loc[worst_s, 'success'])} ({worst_s})** to **{pct(v.loc[best_s, 'success'])} ({best_s})**.")
    top2 = v["rev_share"].head(2).sum()
    add(f"- Revenue concentration: the top two vehicle types provide {pct(top2)} of revenue.")
    add(f"\n**Recommendation:** prioritise driver supply for **{worst_s}** (lowest completion), and protect "
        f"**{top}** capacity at peak hours. Review pricing for {bot} - either grow volume or reassess its role.\n")

    # ------------------------------------------------------------ demand & time
    add("## 3. Demand patterns\n")
    hr = df.groupby("hour").agg(b=("booking_id", "count"), s=("is_success", "mean"))
    peak_h = hr["b"].nlargest(3).index.tolist()
    worst_h = hr["s"].idxmin()
    add(f"- Peak booking hours: **{', '.join(f'{h}:00' for h in peak_h)}**. "
        f"Lowest completion happens at **{worst_h}:00** ({pct(hr.loc[worst_h, 's'])}).")
    wd = df.groupby("weekday").size()
    add(f"- Busiest day: **{wd.idxmax()}** ({wd.max():,} bookings); quietest: **{wd.idxmin()}** ({wd.min():,}).")
    tb = df.groupby("time_bucket").agg(b=("booking_id", "count"), s=("is_success", "mean"))
    add(f"- Time-of-day with the weakest completion: **{tb['s'].idxmin()}** ({pct(tb['s'].min())}).")
    m = df.groupby("year_month").agg(rev=("success_booking_value", "sum"))
    if len(m) > 1:
        gr = (m["rev"].iloc[-1] / m["rev"].iloc[0] - 1)
        add(f"- Monthly revenue moved from {inr(m['rev'].iloc[0])} ({m.index[0]}) to {inr(m['rev'].iloc[-1])} ({m.index[-1]}): **{gr:+.1%}**. "
            f"Best month: **{m['rev'].idxmax()}**, weakest: **{m['rev'].idxmin()}**.")
    add(f"\n**Recommendation:** schedule driver incentives/surge in the {', '.join(f'{h}:00' for h in peak_h)} window, "
        f"and run supply-side campaigns at {worst_h}:00 where completion dips.\n")

    # ------------------------------------------------------------ payments
    add("## 4. Revenue & payments\n")
    pay = ok[ok["payment_method"] != "Not Applicable"].groupby("payment_method")["booking_value"].agg(["sum", "mean", "count"])
    if not pay.empty:
        pay["share"] = pay["sum"] / pay["sum"].sum()
        pay = pay.sort_values("sum", ascending=False)
        add(f"- **{pay.index[0]}** is the dominant payment method ({pct(pay['share'].iloc[0])} of revenue). "
            f"Digital methods (everything except Cash) account for {pct(1 - pay['share'].get('Cash', 0))}.")
        hi = pay["mean"].idxmax()
        add(f"- Highest average ticket: **{hi}** ({inr(pay.loc[hi, 'mean'])}).")
    cust = ok.groupby("customer_id")["booking_value"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    top10 = cust["sum"].head(max(1, int(len(cust) * .1))).sum() / cust["sum"].sum()
    add(f"- Top 10% of customers ({max(1, int(len(cust) * .1)):,}) generate **{pct(top10)}** of revenue; "
        f"repeat customers (2+ rides): {pct((cust['count'] >= 2).mean())}.")
    add("\n**Recommendation:** use UPI/wallet cashbacks to shift cash users to digital, and run a loyalty "
        "programme for the top-spending decile.\n")

    # ------------------------------------------------------------ cancellations
    add("## 5. Cancellations\n")
    cc = df[df["is_cancel_customer"] == 1]["cancel_reason_customer"].value_counts(normalize=True)
    dc = df[df["is_cancel_driver"] == 1]["cancel_reason_driver"].value_counts(normalize=True)
    if len(cc):
        add(f"- Top customer cancellation reason: **{cc.index[0]}** ({pct(cc.iloc[0])} of customer cancels).")
    if len(dc):
        add(f"- Top driver cancellation reason: **{dc.index[0]}** ({pct(dc.iloc[0])} of driver cancels).")
    cv = df.groupby("vehicle_type").apply(
        lambda g: (g["is_cancel_customer"].sum() + g["is_cancel_driver"].sum()) / len(g), include_groups=False)
    add(f"- Highest cancellation rate: **{cv.idxmax()}** ({pct(cv.max())}); lowest: **{cv.idxmin()}** ({pct(cv.min())}).")
    ch = df.groupby("hour").apply(
        lambda g: (g["is_cancel_customer"].sum() + g["is_cancel_driver"].sum()) / len(g), include_groups=False)
    add(f"- Cancellations peak at **{ch.idxmax()}:00** ({pct(ch.max())}).")
    est_lost = 0.0
    fare = (v["revenue"] / v["rides"].replace(0, np.nan))
    fails = v["bookings"] - v["rides"]
    est_lost = float((fails * fare).sum())
    add(f"- Estimated revenue lost to failed bookings: **{inr(est_lost)}** "
        f"({pct(est_lost / (revenue + est_lost))} of potential revenue), using each vehicle's average fare.")
    inc = df[df["incomplete_ride"] == 1]
    if len(inc):
        add(f"- {len(inc):,} rides ended incomplete; top reason: **{inc['incomplete_reason'].value_counts().index[0]}**.")
    add("\n**Recommendation:** fix the top addressable reasons - show accurate pickup pins / ETAs to cut "
        "customer-side cancels, and penalise or coach drivers on avoidable cancels. Treat 'no driver found' as a "
        "supply problem in the weak hours and zones above.\n")

    # ------------------------------------------------------------ ratings
    add("## 6. Ratings & service quality\n")
    add(f"- Average driver rating **{ok['driver_rating'].mean():.2f}**, customer rating **{ok['customer_rating'].mean():.2f}**.")
    rv = ok.groupby("vehicle_type")["driver_rating"].mean()
    add(f"- Best-rated vehicle type: **{rv.idxmax()}** ({rv.max():.2f}); lowest: **{rv.idxmin()}** ({rv.min():.2f}).")
    low = (ok["driver_rating"] <= 2).sum() / max(ok["driver_rating"].notna().sum(), 1)
    add(f"- {pct(low)} of rated rides score a driver rating of 2 or below.")
    w = ok.dropna(subset=["v_tat", "customer_rating"])
    if len(w) > 30:
        r = w["v_tat"].corr(w["customer_rating"])
        add(f"- Correlation between vehicle arrival time and customer rating: **{r:+.2f}** "
            f"({'meaningful - longer waits lower ratings' if r < -0.2 else 'weak - waiting time alone does not explain ratings'}).")
    loc = ok.groupby("pickup_location").agg(r=("driver_rating", "mean"), n=("driver_rating", "count"))
    loc = loc[loc["n"] >= 30].sort_values("r")
    if len(loc):
        add(f"- Lowest-rated pickup areas (≥30 rides): {', '.join(f'{i} ({x:.2f})' for i, x in loc['r'].head(3).items())}.")
    add(f"\n**Recommendation:** run driver-quality coaching for **{rv.idxmin()}**, and investigate the low-rated "
        "pickup zones for road/ETA problems rather than assuming driver behaviour.\n")

    # ------------------------------------------------------------ action plan
    add("## 7. Priority actions\n")
    add("| # | Action | Evidence | Metric to track |")
    add("|---|---|---|---|")
    add(f"| 1 | Add supply in {', '.join(f'{h}:00' for h in peak_h)} and at {worst_h}:00 | Peak demand and weakest completion hours | Success rate by hour |")
    add(f"| 2 | Reduce {biggest[0]} | Largest failure bucket at {pct(biggest[1])} | {biggest[0].title()} % |")
    add(f"| 3 | Lift {worst_s} completion | Lowest success rate ({pct(v.loc[worst_s, 'success'])}) | Success rate by vehicle |")
    add(f"| 4 | Move cash users to digital | Cash share of revenue |"
        f" Digital payment share |")
    add(f"| 5 | Coach {rv.idxmin()} drivers | Lowest rating ({rv.min():.2f}) | Avg driver rating |")
    add("\n---\n*Caveat: associations shown here are descriptive. Test changes (e.g. incentives) with an A/B pilot "
        "before assuming cause and effect.*")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/ola_clean.csv")
    ap.add_argument("--out", default="insights/ola_insights_report.md")
    a = ap.parse_args()
    df = pd.read_csv(a.input, parse_dates=["date", "datetime"])
    for c in ["cancel_reason_customer", "cancel_reason_driver", "incomplete_reason", "payment_method"]:
        if c in df:
            df[c] = df[c].fillna("Not Applicable")
    report = build_report(df)
    Path(a.out).write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved -> {a.out}")


if __name__ == "__main__":
    main()
