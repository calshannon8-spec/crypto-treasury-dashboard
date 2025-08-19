import os
import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Treasury Dashboard", layout="wide")

# --- Load credentials from GitHub Secret ---
creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(creds_info)

# --- Connect to Google Sheets ---
client = gspread.authorize(creds)

# Replace with the exact name of your sheet
SHEET_NAME = "Your Spreadsheet Name"
worksheet = client.open(SHEET_NAME).sheet1

# Get all values
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- Dashboard Display ---
st.title("📊 Treasury Dashboard")

st.write("Data pulled directly from Google Sheets:")
st.dataframe(df)

# Example metric display
if not df.empty:
    st.metric(label="Number of Rows", value=len(df))
    st.metric(label="Number of Columns", value=len(df.columns))
