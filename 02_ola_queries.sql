/* =====================================================================
   OLA PROJECT - STEP 2: SQL QUERIES
   Table: ola_rides  (created by 01_data_preprocessing.py -> data/ola.db)
   Written in portable SQL; tested on SQLite. Notes for MySQL / PostgreSQL /
   SQL Server are marked with "-- PORT:".
   Sections follow the 5 dashboard pages in your slides.
   ===================================================================== */

/* ---------- 0. SANITY CHECKS ---------------------------------------- */
-- Q0.1 Row count and date range
SELECT COUNT(*) AS total_rows, MIN(date) AS first_date, MAX(date) AS last_date FROM ola_rides;

-- Q0.2 Duplicate booking IDs (should return 0 rows)
SELECT booking_id, COUNT(*) AS n FROM ola_rides GROUP BY booking_id HAVING COUNT(*) > 1;


/* ================= PAGE 1: OVERALL ================================== */
-- Q1.1 Headline KPIs
SELECT
    COUNT(*)                                              AS total_bookings,
    SUM(is_success)                                       AS successful_bookings,
    ROUND(100.0 * SUM(is_success) / COUNT(*), 2)          AS success_rate_pct,
    ROUND(100.0 * (SUM(is_cancel_customer) + SUM(is_cancel_driver) + SUM(is_driver_not_found)) / COUNT(*), 2)
                                                          AS failure_rate_pct,
    ROUND(SUM(success_booking_value), 0)                  AS total_revenue,
    ROUND(SUM(success_booking_value) / NULLIF(SUM(is_success), 0), 2) AS avg_booking_value,
    ROUND(AVG(ride_distance), 2)                          AS avg_ride_distance_km
FROM ola_rides;

-- Q1.2 Ride volume by booking status
SELECT booking_status,
       COUNT(*) AS bookings,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM ola_rides
GROUP BY booking_status
ORDER BY bookings DESC;

-- Q1.3 Daily ride volume with a 7-day moving average
SELECT date, bookings,
       ROUND(AVG(bookings) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS moving_avg_7d
FROM (SELECT date, COUNT(*) AS bookings FROM ola_rides GROUP BY date) d
ORDER BY date;

-- Q1.4 Monthly trend: bookings, success rate, revenue, month-over-month revenue growth
WITH m AS (
    SELECT year_month,
           COUNT(*) AS bookings,
           SUM(is_success) AS successful,
           SUM(success_booking_value) AS revenue
    FROM ola_rides
    GROUP BY year_month
)
SELECT year_month, bookings, successful,
       ROUND(100.0 * successful / bookings, 2) AS success_rate_pct,
       ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
             / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0), 2) AS revenue_mom_pct
FROM m
ORDER BY year_month;

-- Q1.5 Demand by weekday and time-of-day (heatmap data)
SELECT weekday, time_bucket, COUNT(*) AS bookings
FROM ola_rides
GROUP BY weekday, time_bucket
ORDER BY weekday, bookings DESC;

-- Q1.6 Peak hours
SELECT hour, COUNT(*) AS bookings, ROUND(100.0 * SUM(is_success) / COUNT(*), 2) AS success_rate_pct
FROM ola_rides
GROUP BY hour
ORDER BY bookings DESC
LIMIT 5;

-- Q1.7 Top 10 pickup locations and their success rate
SELECT pickup_location, COUNT(*) AS bookings,
       ROUND(100.0 * SUM(is_success) / COUNT(*), 2) AS success_rate_pct
FROM ola_rides
GROUP BY pickup_location
ORDER BY bookings DESC
LIMIT 10;


/* ================= PAGE 2: VEHICLE TYPE ============================= */
-- Q2.1 The exact table on your slide: Total Booking Value, Success Booking Value,
--      Avg. Distance, Total Distance by vehicle type
SELECT vehicle_type,
       ROUND(SUM(booking_value), 0)                   AS total_booking_value,
       ROUND(SUM(success_booking_value), 0)           AS success_booking_value,
       ROUND(AVG(ride_distance), 2)                   AS avg_distance_travelled,
       ROUND(SUM(ride_distance), 0)                   AS total_distance_travelled
FROM ola_rides
GROUP BY vehicle_type
ORDER BY success_booking_value DESC;

-- Q2.2 Vehicle performance: volume, success rate, avg fare, revenue per km
SELECT vehicle_type,
       COUNT(*)                                                     AS bookings,
       ROUND(100.0 * SUM(is_success) / COUNT(*), 2)                 AS success_rate_pct,
       ROUND(SUM(success_booking_value) / NULLIF(SUM(is_success), 0), 2) AS avg_fare,
       ROUND(SUM(success_booking_value) / NULLIF(SUM(ride_distance), 0), 2) AS revenue_per_km,
       ROUND(AVG(v_tat), 1)                                         AS avg_vehicle_tat_min
FROM ola_rides
GROUP BY vehicle_type
ORDER BY bookings DESC;

-- Q2.3 Rank vehicle types by revenue inside each month (window function)
SELECT year_month, vehicle_type, revenue,
       RANK() OVER (PARTITION BY year_month ORDER BY revenue DESC) AS revenue_rank
FROM (
    SELECT year_month, vehicle_type, ROUND(SUM(success_booking_value), 0) AS revenue
    FROM ola_rides GROUP BY year_month, vehicle_type
) t
ORDER BY year_month, revenue_rank;


/* ================= PAGE 3: REVENUE ================================== */
-- Q3.1 Revenue by payment method (successful rides only)
SELECT payment_method,
       COUNT(*) AS rides,
       ROUND(SUM(booking_value), 0) AS revenue,
       ROUND(100.0 * SUM(booking_value) / SUM(SUM(booking_value)) OVER (), 2) AS revenue_share_pct,
       ROUND(AVG(booking_value), 2) AS avg_fare
FROM ola_rides
WHERE is_success = 1
GROUP BY payment_method
ORDER BY revenue DESC;

-- Q3.2 Top 5 customers by total booking value
SELECT customer_id, COUNT(*) AS rides, ROUND(SUM(booking_value), 0) AS total_spend
FROM ola_rides
WHERE is_success = 1
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 5;

-- Q3.3 Revenue by day-of-week
SELECT weekday, ROUND(SUM(success_booking_value), 0) AS revenue, SUM(is_success) AS rides
FROM ola_rides
GROUP BY weekday
ORDER BY revenue DESC;

-- Q3.4 Ride distance distribution (buckets) with revenue
SELECT CASE WHEN ride_distance < 5  THEN '1) <5 km'
            WHEN ride_distance < 10 THEN '2) 5-10 km'
            WHEN ride_distance < 20 THEN '3) 10-20 km'
            WHEN ride_distance < 30 THEN '4) 20-30 km'
            ELSE '5) 30+ km' END AS distance_band,
       COUNT(*) AS rides,
       ROUND(SUM(booking_value), 0) AS revenue,
       ROUND(AVG(booking_value), 2) AS avg_fare
FROM ola_rides
WHERE is_success = 1 AND ride_distance IS NOT NULL
GROUP BY distance_band
ORDER BY distance_band;

-- Q3.5 Revenue lost to failed bookings (estimate = failed bookings x avg fare of that vehicle type)
WITH avg_fare AS (
    SELECT vehicle_type, SUM(success_booking_value) / NULLIF(SUM(is_success), 0) AS fare
    FROM ola_rides GROUP BY vehicle_type
)
SELECT r.vehicle_type,
       COUNT(*) - SUM(r.is_success)                                  AS failed_bookings,
       ROUND((COUNT(*) - SUM(r.is_success)) * a.fare, 0)             AS est_revenue_lost
FROM ola_rides r JOIN avg_fare a ON a.vehicle_type = r.vehicle_type
GROUP BY r.vehicle_type, a.fare
ORDER BY est_revenue_lost DESC;


/* ================= PAGE 4: CANCELLATION ============================= */
-- Q4.1 Cancellation overview
SELECT
    SUM(is_cancel_customer)   AS cancelled_by_customer,
    SUM(is_cancel_driver)     AS cancelled_by_driver,
    SUM(is_driver_not_found)  AS driver_not_found,
    ROUND(100.0 * SUM(is_cancel_customer) / COUNT(*), 2) AS cust_cancel_pct,
    ROUND(100.0 * SUM(is_cancel_driver)   / COUNT(*), 2) AS driver_cancel_pct,
    ROUND(100.0 * SUM(is_driver_not_found)/ COUNT(*), 2) AS no_driver_pct
FROM ola_rides;

-- Q4.2 Customer cancellation reasons
SELECT cancel_reason_customer AS reason, COUNT(*) AS cancellations,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM ola_rides
WHERE is_cancel_customer = 1
GROUP BY cancel_reason_customer
ORDER BY cancellations DESC;

-- Q4.3 Driver cancellation reasons
SELECT cancel_reason_driver AS reason, COUNT(*) AS cancellations,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM ola_rides
WHERE is_cancel_driver = 1
GROUP BY cancel_reason_driver
ORDER BY cancellations DESC;

-- Q4.4 Cancellation rate by vehicle type
SELECT vehicle_type,
       COUNT(*) AS bookings,
       ROUND(100.0 * SUM(is_cancel_customer)  / COUNT(*), 2) AS cust_cancel_pct,
       ROUND(100.0 * SUM(is_cancel_driver)    / COUNT(*), 2) AS driver_cancel_pct,
       ROUND(100.0 * SUM(is_driver_not_found) / COUNT(*), 2) AS no_driver_pct
FROM ola_rides
GROUP BY vehicle_type
ORDER BY cust_cancel_pct + driver_cancel_pct DESC;

-- Q4.5 Cancellation rate by hour of day
SELECT hour, COUNT(*) AS bookings,
       ROUND(100.0 * (SUM(is_cancel_customer) + SUM(is_cancel_driver)) / COUNT(*), 2) AS cancel_rate_pct
FROM ola_rides
GROUP BY hour
ORDER BY hour;

-- Q4.6 Pickup locations with the highest cancellation rate (min 50 bookings)
SELECT pickup_location, COUNT(*) AS bookings,
       ROUND(100.0 * (SUM(is_cancel_customer) + SUM(is_cancel_driver)) / COUNT(*), 2) AS cancel_rate_pct
FROM ola_rides
GROUP BY pickup_location
HAVING COUNT(*) >= 50
ORDER BY cancel_rate_pct DESC
LIMIT 10;

-- Q4.7 Incomplete rides and reasons
SELECT incomplete_reason, COUNT(*) AS rides
FROM ola_rides
WHERE incomplete_ride = 1
GROUP BY incomplete_reason
ORDER BY rides DESC;


/* ================= PAGE 5: RATINGS ================================== */
-- Q5.1 Average driver and customer rating by vehicle type
SELECT vehicle_type,
       ROUND(AVG(driver_rating), 2)   AS avg_driver_rating,
       ROUND(AVG(customer_rating), 2) AS avg_customer_rating,
       COUNT(driver_rating)           AS rated_rides
FROM ola_rides
WHERE is_success = 1
GROUP BY vehicle_type
ORDER BY avg_driver_rating DESC;

-- Q5.2 Rating distribution (1-5 buckets)
SELECT CAST(ROUND(driver_rating) AS INTEGER) AS rating_bucket,    -- PORT: use CAST(... AS INT) in MySQL/SQL Server
       COUNT(*) AS driver_ratings
FROM ola_rides
WHERE driver_rating IS NOT NULL
GROUP BY rating_bucket
ORDER BY rating_bucket;

-- Q5.3 Does a long wait hurt ratings? (customer rating by vehicle-arrival-time band)
SELECT CASE WHEN v_tat < 5  THEN '1) <5 min'
            WHEN v_tat < 10 THEN '2) 5-10 min'
            WHEN v_tat < 20 THEN '3) 10-20 min'
            ELSE '4) 20+ min' END AS wait_band,
       COUNT(*) AS rides,
       ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM ola_rides
WHERE is_success = 1 AND v_tat IS NOT NULL AND customer_rating IS NOT NULL
GROUP BY wait_band
ORDER BY wait_band;

-- Q5.4 Low-rated rides (<=2) by vehicle type
SELECT vehicle_type,
       SUM(CASE WHEN driver_rating   <= 2 THEN 1 ELSE 0 END) AS low_driver_ratings,
       SUM(CASE WHEN customer_rating <= 2 THEN 1 ELSE 0 END) AS low_customer_ratings,
       ROUND(100.0 * SUM(CASE WHEN driver_rating <= 2 THEN 1 ELSE 0 END) / COUNT(driver_rating), 2) AS low_driver_pct
FROM ola_rides
WHERE is_success = 1
GROUP BY vehicle_type
ORDER BY low_driver_pct DESC;

-- Q5.5 Top 5 and bottom 5 pickup areas by driver rating (min 30 rated rides)
SELECT * FROM (
    SELECT pickup_location, ROUND(AVG(driver_rating), 2) AS avg_driver_rating, COUNT(driver_rating) AS n
    FROM ola_rides GROUP BY pickup_location HAVING COUNT(driver_rating) >= 30
    ORDER BY avg_driver_rating DESC LIMIT 5
) top5
UNION ALL
SELECT * FROM (
    SELECT pickup_location, ROUND(AVG(driver_rating), 2), COUNT(driver_rating)
    FROM ola_rides GROUP BY pickup_location HAVING COUNT(driver_rating) >= 30
    ORDER BY AVG(driver_rating) ASC LIMIT 5
) bottom5;

-- PORT: SQLite UNION ALL of two subqueries with ORDER BY/LIMIT works as written; in SQL Server
-- replace LIMIT n with TOP n inside each ordered subquery.
