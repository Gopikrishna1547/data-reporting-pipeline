import pandas as pd
import requests
import json
import schedule
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# ── Load environment variables ──
load_dotenv()
POWER_BI_URL = os.getenv("POWER_BI_PUSH_URL")

# ── Logging setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────
# STEP 1: Load raw CSV data
# ─────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    log.info(f"Loading data from: {filepath}")
    try:
        df = pd.read_csv(filepath)
        log.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        log.error(f"File not found: {filepath}")
        raise


# ─────────────────────────────────────────
# STEP 2: Clean & transform
# ─────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning data...")

    # Standardise column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Drop fully empty rows
    before = len(df)
    df.dropna(how="all", inplace=True)
    log.info(f"Dropped {before - len(df)} empty rows")

    # Fill missing numeric values with 0
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Add calculated revenue column if needed columns exist
    if "units_sold" in df.columns and "unit_price" in df.columns:
        df["revenue"] = df["units_sold"] * df["unit_price"]
        log.info("Calculated 'revenue' column added")

    # Add run timestamp
    df["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log.info(f"Clean data shape: {df.shape}")
    return df


# ─────────────────────────────────────────
# STEP 3: Generate summary report
# ─────────────────────────────────────────
def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Generating summary report...")

    if "category" not in df.columns:
        log.warning("No 'category' column found — skipping group summary")
        return df

    summary = df.groupby("category").agg(
        total_revenue=("revenue", "sum"),
        total_units=("units_sold", "sum"),
        avg_price=("unit_price", "mean"),
        num_records=("category", "count")
    ).reset_index()

    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["avg_price"] = summary["avg_price"].round(2)

    log.info(f"Summary has {len(summary)} categories")
    return summary


# ─────────────────────────────────────────
# STEP 4: Save report to Excel
# ─────────────────────────────────────────
def save_report(df: pd.DataFrame, summary: pd.DataFrame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"reports/report_{timestamp}.xlsx"
    os.makedirs("reports", exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Clean Data", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

    log.info(f"Report saved to: {output_path}")
    return output_path


# ─────────────────────────────────────────
# STEP 5: Push to Power BI
# ─────────────────────────────────────────
def push_to_powerbi(summary: pd.DataFrame):
    if not POWER_BI_URL:
        log.warning("POWER_BI_PUSH_URL not set in .env — skipping Power BI push")
        return

    log.info("Pushing data to Power BI...")
    data = summary.to_dict(orient="records")

    try:
        response = requests.post(
            POWER_BI_URL,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            log.info("Successfully pushed to Power BI")
        else:
            log.error(f"Power BI push failed: {response.status_code} — {response.text}")
    except requests.exceptions.RequestException as e:
        log.error(f"Network error pushing to Power BI: {e}")


# ─────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────
def run_pipeline():
    log.info("=" * 50)
    log.info("Pipeline started")
    log.info("=" * 50)

    try:
        df = load_data("data/raw_data.csv")
        df = clean_data(df)
        summary = generate_summary(df)
        save_report(df, summary)
        push_to_powerbi(summary)
        log.info("Pipeline completed successfully")
    except Exception as e:
        log.error(f"Pipeline failed: {e}")

    log.info("=" * 50)


# ─────────────────────────────────────────
# SCHEDULER — runs every day at 08:00
# ─────────────────────────────────────────
if __name__ == "__main__":
    log.info("Scheduler started — pipeline will run daily at 08:00")
    run_pipeline()  # Run once immediately on start

    schedule.every().day.at("08:00").do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)
