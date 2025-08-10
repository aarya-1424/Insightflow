import gspread
import pandas as pd
from debug_sheet import SHEET_NAME, WORKSHEET_NAME

def get_sheet_data():
    try:
        # ✅ Authorize using gspread's built-in method
        client = gspread.service_account(filename="credentials.json")
        print("✅ Authorized Google API")

        # Open the spreadsheet and worksheet
        sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        print("✅ Sheet and worksheet accessed successfully")

        # Get all records
        data = sheet.get_all_records()
        print(f"📊 Raw data fetched: {len(data)} rows")

        if not data:
            print("⚠️ No data found in the worksheet!")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(data)
        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None