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
    """Import attendance data from Excel file"""
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

        # Assuming columns are: Student Name, Date, Status
        # Adjust column names if different
        student_col = 'Student Name'  # Adjust if different
        date_col = 'Date'  # Adjust if different
        status_col = 'Status'  # Adjust if different

        if student_col not in df.columns or date_col not in df.columns or status_col not in df.columns:
            print("Expected columns not found. Available columns:")
            for col in df.columns:
                print(f"  - {col}")
            return

        with app.app_context():
            imported_count = 0
            skipped_count = 0

            for index, row in df.iterrows():
                student_name = str(row[student_col]).strip()
                date_str = str(row[date_col]).strip()
                status_code = row[status_col]

                # Find student by name
                student = Student.query.filter_by(name=student_name).first()
                if not student:
                    print(f"Student '{student_name}' not found, skipping...")
                    skipped_count += 1
                    continue

                # Parse date
                try:
                    if isinstance(date_str, str):
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d %H:%M:%S']:
                            try:
                                date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            print(f"Could not parse date '{date_str}' for student '{student_name}', skipping...")
                            skipped_count += 1
                            continue
                    else:
                        # If it's already a date object
                        date = date_str.date() if hasattr(date_str, 'date') else date_str
                except Exception as e:
                    print(f"Error parsing date '{date_str}' for student '{student_name}': {e}, skipping...")
                    skipped_count += 1
                    continue

                # Map status code to string
                if status_code not in STATUS_MAPPING:
                    print(f"Invalid status code '{status_code}' for student '{student_name}', skipping...")
                    skipped_count += 1
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
