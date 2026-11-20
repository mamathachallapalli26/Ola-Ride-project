# Power BI Dashboard Build Guide

Matches your slide deck: five pages with a left/top navigation of
**Overall · Vehicle Type · Revenue · Cancellation · Ratings**.

> I can't generate a `.pbix` file here. This guide plus `03a_power_query.m` and
> `03b_dax_measures.dax` let you build it in Power BI Desktop in about 1–2 hours.

## 0. Setup (10 min)
1. **Get data:** Home → Transform data → New Source → Blank Query → Advanced Editor → paste `03a_power_query.m` (update the path) → Close & Apply.
2. **Date table:** Modeling → New table → paste the `DimDate` DAX from the bottom of `03a_power_query.m`. Create relationship `DimDate[Date]` (1) → `ola_rides[date]` (*). Mark as date table.
3. **Measures:** create an empty table `_Measures`, then add every measure from `03b_dax_measures.dax`.
4. **Sort columns:** `weekday` by `weekday_no`; `month_name` by `month`.
5. **Theme:** View → Themes. Suggested palette: Ola-style green `#1C8A3E`, dark `#1A1A1A`, accent yellow `#F9C80E`, alert red `#C62828`, neutral grey `#757575`.
6. **Navigation:** add 5 buttons (Insert → Buttons → Navigator → Page navigator) at the top of every page to match your slides' tab layout.

## 1. Overall page
| Visual | Fields | Notes |
|---|---|---|
| Card ×5 | Total Bookings · Success Rate % · Total Revenue · Avg Booking Value · Avg Ride Distance | Top row |
| Line + clustered column | X: `year_month` · Columns: Total Bookings · Line: Success Rate % | Monthly trend |
| Donut | Legend: `booking_status` · Values: Total Bookings | Status mix |
| Matrix (heatmap) | Rows: `weekday` · Columns: `time_bucket` · Values: Total Bookings | Conditional-format background colour scale |
| Bar | Axis: `pickup_location` · Values: Total Bookings · Top N = 10 | Filter pane → Top N |
| Slicers | `date` (between) · `vehicle_type` · `payment_method` | Sync across pages (View → Sync slicers) |

## 2. Vehicle Type page (your slide table)
| Visual | Fields |
|---|---|
| **Table / Matrix** | Rows: `vehicle_type` (Prime Sedan, Prime SUV, Prime Plus, Mini, Auto, Bike, E-Bike) · Values: **Total Booking Value, Success Booking Value, Avg Distance Travelled, Total Distance Travelled** |
| Clustered bar | `vehicle_type` × Total Revenue (sorted desc) |
| Column | `vehicle_type` × Success Rate % — use `Success Rate Color` for conditional formatting |
| Scatter | X: Avg Distance Travelled · Y: Avg Booking Value · Size: Total Bookings · Details: `vehicle_type` |
| Cards | Revenue per KM, Avg Vehicle TAT (min) – respond to the vehicle slicer |

Tip: set the table's column order exactly as on the slide.

## 3. Revenue page
| Visual | Fields |
|---|---|
| Cards | Total Revenue · Revenue MoM % · Revenue YTD · Revenue per Customer |
| Area chart | `year_month` × Total Revenue, Legend: `vehicle_type` |
| Donut / Treemap | `payment_method` × Total Revenue (filter `payment_method` ≠ "Not Applicable") |
| Column | `distance_band` × Total Revenue and Avg Booking Value (Combo) |
| Column | `weekday` × Total Revenue (sorted by `weekday_no`) |
| Bar | `vehicle_type` × Est Revenue Lost (lost revenue from failed bookings) |
| Table | Top 5 `customer_id` by Total Revenue (Top N filter) |

## 4. Cancellation page
| Visual | Fields |
|---|---|
| Cards | Cancellation Rate % · Customer Cancel % · Driver Cancel % · No Driver Found % |
| Bar (customer) | `cancel_reason` × Total Cancellations, filter `cancelled_by` = Customer |
| Bar (driver) | `cancel_reason` × Total Cancellations, filter `cancelled_by` = Driver |
| 100% stacked bar | `vehicle_type` × Customer Cancel %, Driver Cancel %, No Driver Found % |
| Line | `hour` × Cancellation Rate % — shows when cancellations peak |
| Bar | Incomplete ride reasons: `incomplete_reason` (filter `incomplete_ride` = 1) |
| Decomposition tree | Analyze: Total Cancellations · Explain by: `vehicle_type`, `pickup_location`, `time_bucket`, `cancel_reason` |

## 5. Ratings page
| Visual | Fields |
|---|---|
| Gauge ×2 | Avg Driver Rating, Avg Customer Rating (min 1, max 5, target 4.5) |
| Clustered bar | `vehicle_type` × Avg Driver Rating, Avg Customer Rating |
| Column | Rating distribution: `driver_rating` (as text, count) × Rated Rides |
| Column | `vehicle_type` × Low Driver Rating % |
| Scatter | X: Avg Vehicle TAT (min) · Y: Avg Customer Rating · Details: `pickup_location` — tests whether waiting hurts ratings |
| Table | Bottom 10 `pickup_location` by Avg Driver Rating (Top N → Bottom 10, with Rated Rides ≥ 30 filter) |

## 6. Finishing touches
- Turn on **Sync slicers** for `date`, `vehicle_type` across all pages.
- Add **tooltips pages** (hover details) for the vehicle bar charts.
- Add **bookmarks** for "Weekday view" vs "Hour view" toggles.
- Set the **page size** to 16:9 so screenshots paste cleanly into your slides.
- Publish: Home → Publish → choose workspace; schedule refresh if the CSV is on OneDrive/SharePoint.
