import pandas as pd

def inspect_excel(file_path):
    """Inspect the structure of an Excel file"""
    try:
        # Load the Excel file
        xl = pd.ExcelFile(file_path)
        print(f"Excel file: {file_path}")
        print(f"Available sheets: {xl.sheet_names}")
        print()

        # Inspect each sheet
        for sheet_name in xl.sheet_names:
            print(f"Sheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  Columns: {list(df.columns)}")
            print(f"  Number of rows: {len(df)}")
            print(f"  First few rows:")
            print(df.head())
            print()

    except Exception as e:
        print(f"Error inspecting Excel file: {e}")

if __name__ == "__main__":
    # Path to the Excel file
    excel_file = "Attendance.xlsx"
    inspect_excel(excel_file)
