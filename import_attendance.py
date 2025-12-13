import pandas as pd
from datetime import datetime
from db import db
from models import Student, Section, Attendance
from app import app

# Mapping for status codes
STATUS_MAPPING = {
    0: 'tardy',
    1: 'absent',
    2: 'present'
}

def import_students_from_excel(file_path, sheet_name=None):
    """Import student data from Excel file"""
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)

        print(f"Reading Excel file: {file_path}")
        if sheet_name:
            print(f"Sheet: {sheet_name}")
        print(f"Columns found: {list(df.columns)}")
        print(f"Number of rows: {len(df)}")

        # Check available sheets
        xl = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl.sheet_names}")

        with app.app_context():
            imported_count = 0
            skipped_count = 0

            for index, row in df.iterrows():
                # Extract student name and grade/section
                student_name = str(row.get('Name Of Student', row.get('Student Name', ''))).strip()
                grade_section = str(row.get('Grade And Section', row.get('Grade_Section', ''))).strip()

                if not student_name or not grade_section:
                    print(f"Missing student name or grade/section in row {index+1}, skipping...")
                    skipped_count += 1
                    continue

                # Parse grade and section
                try:
                    # Assuming format like "Grade 7 - Section A" or "7-A"
                    if ' - ' in grade_section:
                        grade_part, section_part = grade_section.split(' - ', 1)
                        grade = int(''.join(filter(str.isdigit, grade_part)))
                        section_name = section_part.strip()
                    elif '-' in grade_section:
                        grade_part, section_part = grade_section.split('-', 1)
                        grade = int(grade_part.strip())
                        section_name = section_part.strip()
                    else:
                        print(f"Could not parse grade/section '{grade_section}' for student '{student_name}', skipping...")
                        skipped_count += 1
                        continue
                except Exception as e:
                    print(f"Error parsing grade/section '{grade_section}' for student '{student_name}': {e}, skipping...")
                    skipped_count += 1
                    continue

                # Find or create section
                section = Section.query.filter_by(name=section_name, grade_level=grade).first()
                if not section:
                    section = Section(name=section_name, grade_level=grade)
                    db.session.add(section)
                    db.session.flush()  # Get the ID
                    print(f"Created section: {section_name} (Grade {grade})")

                # Check if student already exists
                existing_student = Student.query.filter_by(name=student_name).first()
                if existing_student:
                    print(f"Student '{student_name}' already exists, skipping...")
                    skipped_count += 1
                    continue

                # Create student
                student = Student(name=student_name, grade_level=grade, section_id=section.id)
                db.session.add(student)
                print(f"Added student: {student_name} (Grade {grade}, Section {section_name})")
                imported_count += 1

            db.session.commit()
            print(f"\nImport completed!")
            print(f"Imported: {imported_count}")
            print(f"Skipped: {skipped_count}")

    except Exception as e:
        print(f"Error importing students: {e}")

def import_attendance_from_excel(file_path, sheet_name=None):
    """Import attendance data from Excel file with pivot table format"""
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)

        print(f"Reading Excel file: {file_path}")
        if sheet_name:
            print(f"Sheet: {sheet_name}")
        print(f"Columns found: {list(df.columns)}")
        print(f"Number of rows: {len(df)}")

        with app.app_context():
            imported_count = 0
            skipped_count = 0

            # Get the date headers from the first row (skip the first column which is "NAME:")
            date_headers = df.columns[1:]  # Skip first column

            for index, row in df.iterrows():
                if index == 0:
                    continue  # Skip header row

                student_name = str(row.iloc[0]).strip()  # First column is student name

                # Find student by name
                student = Student.query.filter_by(name=student_name).first()
                if not student:
                    print(f"Student '{student_name}' not found, skipping...")
                    skipped_count += 1
                    continue

                # Process each date column
                for col_idx, date_header in enumerate(date_headers, 1):  # Start from 1 to skip name column
                    date_str = str(date_header).strip()
                    status_code = row.iloc[col_idx]

                    # Skip if status is NaN or empty
                    if pd.isna(status_code) or str(status_code).strip() == '':
                        continue

                    # Parse date from header
                    try:
                        # Extract date from string like "2025-10-01 00:00:00"
                        if ' ' in date_str:
                            date_part = date_str.split(' ')[0]
                            date = datetime.strptime(date_part, '%Y-%m-%d').date()
                        else:
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except Exception as e:
                        print(f"Error parsing date '{date_str}' for student '{student_name}': {e}, skipping...")
                        continue

                    # Convert status_code to int if it's not already
                    try:
                        status_code = int(status_code)
                    except (ValueError, TypeError):
                        print(f"Invalid status code '{status_code}' for student '{student_name}' on {date}, skipping...")
                        continue

                    # Map status code to string
                    if status_code not in STATUS_MAPPING:
                        print(f"Invalid status code '{status_code}' for student '{student_name}' on {date}, skipping...")
                        continue

                    status = STATUS_MAPPING[status_code]

                    # Check if attendance already exists
                    existing = Attendance.query.filter_by(student_id=student.id, date=date).first()
                    if existing:
                        existing.status = status
                        print(f"Updated attendance for {student_name} on {date}: {status}")
                    else:
                        attendance = Attendance(student_id=student.id, date=date, status=status)
                        db.session.add(attendance)
                        print(f"Added attendance for {student_name} on {date}: {status}")

                    imported_count += 1

            db.session.commit()
            print(f"\nImport completed!")
            print(f"Imported/Updated: {imported_count}")
            print(f"Skipped: {skipped_count}")

    except Exception as e:
        print(f"Error importing attendance: {e}")

if __name__ == "__main__":
    # Path to the Excel file
    excel_file = r"C:\Users\Windows 10\Desktop\Research Attendance.xlsx"

    # Import students from sheet 6 (assuming it's the 6th sheet, index 5)
    xl = pd.ExcelFile(excel_file)
    if len(xl.sheet_names) >= 6:
        sheet_6_name = xl.sheet_names[5]  # 0-indexed, so 5 is the 6th sheet
        print(f"Importing students from sheet '{sheet_6_name}' (sheet 6)")
        import_students_from_excel(excel_file, sheet_name=sheet_6_name)
    else:
        print(f"Excel file only has {len(xl.sheet_names)} sheets, importing from first sheet")
        import_students_from_excel(excel_file)
