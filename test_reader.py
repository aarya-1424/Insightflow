from sheet_reader import get_sheet_data

df = get_sheet_data()

if df is None:
    print("❌ DataFrame is None — something went wrong while fetching the sheet.")
else:
    print("✅ Sheet loaded successfully:")
    print(df.head())
