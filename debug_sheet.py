import gspread
from google.oauth2 import service_account

SHEET_NAME = "InsightFlow"
WORKSHEET_NAME = "Weekly Data"

try:
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    print("✅ Authorized")

    spreadsheet = client.open(SHEET_NAME)
    print(f"✅ Opened Spreadsheet: {spreadsheet.title}")

    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    print(f"✅ Opened Worksheet: {worksheet.title}")

    data = worksheet.get_all_records()
    print(f"✅ Rows fetched: {len(data)}")
    print("📄 Sample Row:", data[0] if data else "No data found")

except Exception as e:
    print("❌ ERROR:", e)
