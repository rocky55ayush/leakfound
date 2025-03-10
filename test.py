import mysql.connector
import joblib
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import logging
from fpdf import FPDF
import os

# ✅ Setup Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# ✅ Load AI Risk Model
MODEL_PATH = "risk_model.pkl"
if not os.path.exists(MODEL_PATH):
    logger.error("❌ Error: risk_model.pkl not found! Train and save the model first.")
    exit()

model = joblib.load(MODEL_PATH)
logger.info("✅ AI Risk Model Loaded Successfully!")

# ✅ Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "retemex_db",
    "charset": "utf8mb4"
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    logger.info("✅ Database Connected Successfully!")
except mysql.connector.Error as e:
    logger.error(f"❌ Database Connection Error: {e}")
    exit()

# ✅ Load CSV File
CSV_PATH = "export_data.csv"
if not os.path.exists(CSV_PATH):
    logger.error("❌ Error: export_data.csv file not found!")
    exit()

compare_data = pd.read_csv(CSV_PATH, dtype=str).dropna()

# ✅ Define Required Columns
required_columns = ["Username", "Password", "email", "phone", "card_number", "expiry_date", "cvv"]

# ✅ Check if Required Columns Exist
if not all(col in compare_data.columns for col in required_columns):
    logger.error(f"❌ CSV File Missing Required Columns! Found columns: {list(compare_data.columns)}")
    exit()

# ✅ Select Only Required Columns
compare_data = compare_data[required_columns].map(str.strip)
logger.info(f"✅ Loaded export_data.csv with {len(compare_data)} entries.")

# ✅ Fetch Data from Database
try:
    cursor.execute("SELECT username, password, email, phone, card_number, expiry_date, cvv FROM RET_CLIENTES")
    db_data = {tuple(map(str.strip, row)) for row in cursor.fetchall()}
    total_db_records = len(db_data)
    logger.info(f"✅ Retrieved {total_db_records} records from the database.")
except mysql.connector.Error as e:
    logger.error(f"❌ Database Query Error: {e}")
    exit()

# ✅ Compare CSV Data with Database
matched_entries = [
    tuple(map(str.strip, row))
    for row in compare_data.itertuples(index=False, name=None)
    if tuple(map(str.strip, row)) in db_data
]

if not matched_entries:
    logger.info("✅ No compromised accounts found! Exiting.")
    cursor.close()
    conn.close()
    exit()

num_compromised_accounts = len(matched_entries)
logger.info(f"🚨 Found {num_compromised_accounts} compromised accounts.")

# ✅ Calculate Adjusted Risk Score Based on Percentage of Compromised Accounts
adjusted_risk_score = (num_compromised_accounts / total_db_records) * 100
adjusted_risk_score = min(max(adjusted_risk_score, 0), 100)
logger.info(f"🚨 Adjusted Risk Score: {adjusted_risk_score:.2f}%")

# ✅ Generate PDF Report
def generate_pdf_report(matched_entries, adjusted_risk_score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Breach Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Adjusted Risk Score: {adjusted_risk_score:.2f}%", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, f"Total Compromised Accounts: {len(matched_entries)}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)

    for i, (username, password, email, phone, card_number, expiry_date, cvv) in enumerate(matched_entries[:50]):
        pdf.cell(200, 10, f"{i+1}. {email} - {phone} - Card: {card_number} - CVV: {cvv}", ln=True)

    pdf_file = "breach_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

pdf_file = generate_pdf_report(matched_entries, adjusted_risk_score)
logger.info(f"✅ PDF Report Generated: {pdf_file}")

# ✅ Email Alert Function
def send_email_alert(pdf_filename):
    sender_email = "ay8010650@gmail.com"
    sender_password = "ovkk tjwe ojda hgxe"
    recipient_email = "ry8010650@gmail.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "🚨 ALERT: Breach Report Attached"
    message.attach(MIMEText("Please find the attached breach report.", "plain"))

    try:
        with open(pdf_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={pdf_filename}")
            message.attach(part)
    except Exception as e:
        logger.error(f"❌ Error Attaching PDF: {e}")
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        logger.info("✅ Email Sent Successfully with PDF Report")
    except smtplib.SMTPException as e:
        logger.error(f"❌ Error Sending Email: {e}")

# ✅ Send Email with Breach Report
send_email_alert(pdf_file)

# ✅ Close Database Connection
cursor.close()
conn.close()
logger.info("✅ Database Connection Closed Successfully.")

