# Automated Data Reporting Pipeline

An end-to-end Python pipeline that reads raw CSV data, cleans and transforms it using Pandas, generates Excel reports, and pushes summary data to a Power BI dashboard automatically — scheduled to run daily.

## Features
- Automatic CSV ingestion and cleaning
- Revenue calculation and category-level summaries
- Excel report generation with two sheets (Clean Data + Summary)
- Power BI push via Streaming Dataset API
- Daily scheduler (runs at 08:00 every day)
- Full logging to file and console

## Project Structure
```
data-reporting-pipeline/
├── pipeline.py          # Main pipeline script
├── data/
│   └── raw_data.csv     # Sample input data
├── reports/             # Auto-generated Excel reports (git-ignored)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore
└── README.md
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/your-username/data-reporting-pipeline.git
cd data-reporting-pipeline
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Power BI Push URL
```

**4. Add your data**

Replace `data/raw_data.csv` with your own CSV file.  
The pipeline expects columns: `Category`, `Units Sold`, `Unit Price` (at minimum).

**5. Run the pipeline**
```bash
python pipeline.py
```

This runs the pipeline once immediately, then schedules it daily at 08:00.

## Power BI Setup

1. Go to Power BI → Create a **Streaming Dataset**
2. Add fields: `category`, `total_revenue`, `total_units`, `avg_price`, `num_records`
3. Copy the **Push URL** into your `.env` file

## Tech Stack
- Python 3.10+
- Pandas, OpenPyXL
- Requests, Schedule
- Python-dotenv
- Power BI Streaming API

## Author
Gopikrishna Bojedla  
[LinkedIn](https://www.linkedin.com/in/gopi-krishna-83856320a)
