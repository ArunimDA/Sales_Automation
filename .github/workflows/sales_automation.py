# %%
import psycopg2
import pandas as pd
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "host": "aws-1-ap-northeast-1.pooler.supabase.com",
    "database": "postgres",
    "user": "postgres.udmzqpofidalbdgvedkt",
    "password": "Lobbing787868!!!???"
}

EMAIL_CONFIG = {
    "sender": "amlan007.s@gmail.com",
    "password": "xxnw usvp vbss eoco", # Use an App Password, not your login password
    "recipients": ["amlan007.s@gmail.com", "amlan008.s@outlook.com"],
    "subject": "Automated Sales Performance Report"
}

QUERY = """
SELECT 
    s.*,
    ROUND(s."Boxes" * pr."Cost_per_box" :: NUMERIC, 0) as total_cost,
    ROUND(s."Amount" - (s."Boxes" * pr."Cost_per_box" :: NUMERIC), 0) as total_profit,
    pr."Cost_per_box",
    s."Amount" / s."Boxes" as Amount_per_Box,
    ROUND((s."Amount" / s."Boxes") - pr."Cost_per_box" :: NUMERIC, 0) as profit_per_Box,
    ROUND(((s."Boxes" * pr."Cost_per_box" :: NUMERIC) / s."Amount") * 100, 0) as CTIR_Margin,
    ROUND(((s."Amount" - (s."Boxes" * pr."Cost_per_box" :: NUMERIC)) / s."Amount") * 100, 0) as profit_margin,
    g."Geo", g."Region", pr."Category", pr."Product", pr."Size",
    p."Location", p."Salesperson", p."Team"
FROM sales s
JOIN geo g ON g."GeoID" = s."GeoID"
JOIN people p ON p."SPID" = s."SPID"
JOIN products pr ON pr."PID" = s."PID"
WHERE p."SPID" IS NOT NULL 
    AND g."GeoID" IS NOT NULL 
    AND pr."PID" IS NOT NULL
    AND p."Team" <> '' 
    AND s."SaleDate" IS NOT NULL
    AND s."Amount" > 0 
    AND s."Boxes" > 0;
"""

def send_email(file_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG["sender"]
    msg['To'] = ", ".join(EMAIL_CONFIG["recipients"])
    msg['Subject'] = EMAIL_CONFIG["subject"]
    
    body = "Please find the latest Sales Automation Report attached."
    msg.attach(MIMEText(body, 'plain'))

    # Attach the Excel file
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {file_path}")
        msg.attach(part)

    # Sending logic (Using Gmail as example)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
    server.send_message(msg)
    server.quit()

def run_automation():
    print("Starting Data Extraction...")
    try:
        # Connect to Postgres and fetch data
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql_query(QUERY, conn)
        conn.close()

        if not df.empty:
            file_name = "Sales_Report.xlsx"
            df.to_excel(file_name, index=False)
            send_email(file_name)
            print(f"Success! Report sent at {time.ctime()}")
        else:
            print("No new data found.")

    except Exception as e:
        print(f"Error occurred: {e}")

# --- 2. THE LOOP ---
if __name__ == "__main__":
    while True:
        run_automation()
        print("Waiting 2 minutes for next run...")
        time.sleep(120) # 120 seconds = 2 minutes

