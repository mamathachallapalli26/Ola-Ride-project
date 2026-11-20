# OLA Ride Analytics Project

| Step | File | What it does |
|---|---|---|
| 1 | `01_data_preprocessing.py` | Cleans the Excel file, creates derived columns, writes `data/ola_clean.csv` + SQLite `data/ola.db` |
| 2 | `sql/02_ola_queries.sql` (+ `sql/run_queries.py`) | 29 queries for the 5 dashboard pages |
| 3 | `powerbi/03a_power_query.m`, `03b_dax_measures.dax`, `03c_dashboard_build_guide.md` | Power BI data load, ~50 DAX measures, visual-by-visual page specs |
| 4 | `streamlit_app/04_streamlit_app.py` | 5-tab interactive dashboard with filters |
| 5 | `insights/05_bi_insights.py` | Generates a data-driven insights report (Markdown) |

## Run order
```bash
pip install -r requirements.txt
python 01_data_preprocessing.py --input OLA_DataSet.xlsx   # 1. clean data
python sql/run_queries.py                                  # 2. run all SQL
streamlit run streamlit_app/04_streamlit_app.py            # 4. dashboard
python insights/05_bi_insights.py                          # 5. insights report
# 3. Power BI: follow powerbi/03c_dashboard_build_guide.md
```

## If your column names differ
Edit only `COLUMN_ALIASES` / `VEHICLE_MAP` at the top of `01_data_preprocessing.py`.
Everything downstream uses the cleaned names.

## About `tests/`
`tests/make_sample_data.py` makes a **synthetic** file used only to verify the code.
Never report numbers from it.
