"""
Main Application Entry Point for Hostel Room Allocation and Fee Management System.
Features a professional menu-driven command-line interface with submenu navigation,
robust input validation, formatted tables, and exception handling.
"""

from __future__ import annotations
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

from data_manager import DataManager
from initialization import initialize_datasets, verify_dataset_integrity
import student_module
import room_module
import fee_module
import analysis_module
from analysis_module import format_table


def print_header(title: str) -> None:
    """Print standard section header."""
    print("\n" + "=" * 65)
    print(f" {title.center(63)} ")
    print("=" * 65)


def pause() -> None:
    """Pause terminal execution until user presses Enter."""
    input("\nPress [Enter] to continue...")


# -------------------------------------------------------------
# 1. Student Management Submenu
# -------------------------------------------------------------
def student_management_menu(data_mgr: DataManager) -> None:
    while True:
        print_header("STUDENT MANAGEMENT")
        print("1. Add New Student")
        print("2. Display All Students")
        print("3. Search Student by ID / Name")
        print("4. Update Student Details")
        print("5. Delete Student Record")
        print("6. Return to Main Menu")
        print("-" * 65)

        choice = input("Enter choice (1-6): ").strip()
        if choice == "1":
            print_header("ADD NEW STUDENT")
            s_id = input("Enter Student ID (e.g. STU1101): ").strip()
            name = input("Enter Full Name: ").strip()
            gender = input("Enter Gender (Male/Female/Other): ").strip()
            course = input("Enter Course (e.g. B.Tech CSE, MCA): ").strip()
            year = input("Enter Academic Year (1-5): ").strip()
            contact = input("Enter 10-digit Contact Number: ").strip()
            room_no = input("Enter Room Number (optional, press Enter to skip): ").strip()

            try:
                added = student_module.add_student(
                    student_id=s_id,
                    name=name,
                    gender=gender,
                    course=course,
                    year=int(year) if year.isdigit() else year,  # type: ignore
                    contact=contact,
                    data_mgr=data_mgr,
                    room_no=room_no,
                )
                print(f"\n[SUCCESS] Student '{added['Name']}' ({added['Student_ID']}) registered successfully!")
                if room_no:
                    print(f"[INFO] Allocated to Room: {room_no}")
            except Exception as e:
                print(f"\n[ERROR] Failed to add student: {e}")
            pause()

        elif choice == "2":
            print_header("ALL REGISTERED STUDENTS")
            students = student_module.display_students(data_mgr)
            if not students:
                print("No students registered yet.")
            else:
                print(format_table(students))
                print(f"\nTotal Students: {len(students)}")
            pause()

        elif choice == "3":
            print_header("SEARCH STUDENT")
            query = input("Enter Student ID or Name: ").strip()
            if not query:
                print("[WARNING] Search query cannot be empty.")
            else:
                matches = student_module.search_students_multi(query, data_mgr)
                if not matches:
                    print(f"No student matching '{query}' found.")
                else:
                    print(format_table(matches))
            pause()

        elif choice == "4":
            print_header("UPDATE STUDENT DETAILS")
            s_id = input("Enter Student ID to update: ").strip()
            student = student_module.search_student(s_id, data_mgr)
            if not student:
                print(f"[ERROR] Student with ID '{s_id}' not found.")
                pause()
                continue

            print("\nCurrent Details:")
            print(format_table([student]))
            print("\nLeave blank to keep existing value.")

            name = input(f"New Name [{student.get('Name')}]: ").strip()
            gender = input(f"New Gender [{student.get('Gender')}]: ").strip()
            course = input(f"New Course [{student.get('Course')}]: ").strip()
            year = input(f"New Year [{student.get('Year')}]: ").strip()
            contact = input(f"New Contact [{student.get('Contact')}]: ").strip()

            updates: Dict[str, Any] = {}
            if name:
                updates["Name"] = name
            if gender:
                updates["Gender"] = gender
            if course:
                updates["Course"] = course
            if year:
                updates["Year"] = year
            if contact:
                updates["Contact"] = contact

            if not updates:
                print("[INFO] No changes entered.")
            else:
                try:
                    updated = student_module.update_student(s_id, updates, data_mgr)
                    print(f"\n[SUCCESS] Student '{s_id}' updated successfully!")
                    print(format_table([updated]))
                except Exception as e:
                    print(f"\n[ERROR] Failed to update: {e}")
            pause()

        elif choice == "5":
            print_header("DELETE STUDENT RECORD")
            s_id = input("Enter Student ID to delete: ").strip()
            student = student_module.search_student(s_id, data_mgr)
            if not student:
                print(f"[ERROR] Student '{s_id}' not found.")
                pause()
                continue

            print("\nTarget Student Record:")
            print(format_table([student]))

            confirm = input(f"\nAre you SURE you want to permanently delete student {s_id}? (yes/no): ").strip().lower()
            if confirm in ("yes", "y"):
                try:
                    deleted = student_module.delete_student(s_id, data_mgr, cascade=True)
                    print(f"\n[SUCCESS] Student '{deleted['Name']}' ({s_id}) deleted.")
                    print("[INFO] Associated room bed vacated and fee record settled.")
                except Exception as e:
                    print(f"\n[ERROR] Failed to delete: {e}")
            else:
                print("\n[INFO] Deletion cancelled by user.")
            pause()

        elif choice == "6":
            break
        else:
            print("[ERROR] Invalid choice. Please choose from 1 to 6.")
            pause()


# -------------------------------------------------------------
# 2. Room Allocation Submenu
# -------------------------------------------------------------
def room_allocation_menu(data_mgr: DataManager) -> None:
    while True:
        print_header("ROOM ALLOCATION MANAGEMENT")
        print("1. Display All Rooms")
        print("2. Allocate an Available Room")
        print("3. Check Available Beds / Vacancy")
        print("4. Display Occupied Rooms")
        print("5. Display Vacant Rooms")
        print("6. Change Student's Room (Reassign)")
        print("7. Vacate a Student's Room")
        print("8. Return to Main Menu")
        print("-" * 65)

        choice = input("Enter choice (1-8): ").strip()
        if choice == "1":
            print_header("ALL HOSTEL ROOMS")
            rooms = room_module.display_room_details(data_mgr)
            print(format_table(rooms))
            pause()

        elif choice == "2":
            print_header("ALLOCATE AVAILABLE ROOM")
            s_id = input("Enter Student ID: ").strip().upper()
            room_no = input("Enter Room Number to Allocate: ").strip()
            try:
                res = room_module.allocate_room(s_id, room_no, data_mgr)
                print(f"\n[SUCCESS] Room '{res['room_no']}' ({res['room_type']}) allocated to Student '{s_id}'.")
            except Exception as e:
                print(f"\n[ERROR] Allocation failed: {e}")
            pause()

        elif choice == "3":
            print_header("CHECK ROOM VACANCY")
            rtype = input("Filter by Room Type (Single/Double/Triple/Four-Bed, or Enter for all): ").strip()
            floor = input("Filter by Floor (1-4, or Enter for all): ").strip()
            vacant = room_module.check_vacancy(data_mgr, room_type=rtype or None, floor=int(floor) if floor.isdigit() else None)
            if not vacant:
                print("No rooms found matching the criteria.")
            else:
                print(format_table(vacant))
                total_vac = sum(r["Vacancy"] for r in vacant)
                print(f"\nTotal Available Beds: {total_vac} across {len(vacant)} rooms.")
            pause()

        elif choice == "4":
            print_header("OCCUPIED ROOMS")
            occ = room_module.get_occupied_rooms(data_mgr)
            if not occ:
                print("No occupied rooms.")
            else:
                print(format_table(occ))
                total_occ = sum(r["Occupied"] for r in occ)
                print(f"\nTotal Occupants: {total_occ} across {len(occ)} rooms.")
            pause()

        elif choice == "5":
            print_header("VACANT ROOMS (WITH AVAILABLE BEDS)")
            vac = room_module.get_vacant_rooms(data_mgr)
            if not vac:
                print("All rooms are completely full.")
            else:
                print(format_table(vac))
                total_beds = sum(r["Vacancy"] for r in vac)
                print(f"\nTotal Vacant Beds: {total_beds} across {len(vac)} rooms.")
            pause()

        elif choice == "6":
            print_header("CHANGE / REASSIGN STUDENT ROOM")
            s_id = input("Enter Student ID: ").strip().upper()
            new_room = input("Enter Target Room Number: ").strip()
            try:
                res = room_module.reassign_room(s_id, new_room, data_mgr)
                print(f"\n[SUCCESS] Student '{s_id}' moved from Room '{res['old_room']}' to Room '{res['new_room']}'.")
                print(f"[INFO] New Room Type: {res['new_room_type']}")
            except Exception as e:
                print(f"\n[ERROR] Reassignment failed: {e}")
            pause()

        elif choice == "7":
            print_header("VACATE A STUDENT'S ROOM")
            s_id = input("Enter Student ID: ").strip().upper()
            try:
                res = room_module.vacate_room(s_id, data_mgr)
                print(f"\n[SUCCESS] Student '{s_id}' vacated Room '{res['vacated_room']}'.")
            except Exception as e:
                print(f"\n[ERROR] Failed to vacate room: {e}")
            pause()

        elif choice == "8":
            break
        else:
            print("[ERROR] Invalid choice. Please choose from 1 to 8.")
            pause()


# -------------------------------------------------------------
# 3. Hostel Fee Management Submenu
# -------------------------------------------------------------
def hostel_fee_menu(data_mgr: DataManager) -> None:
    while True:
        print_header("HOSTEL FEE MANAGEMENT")
        print("1. Record Hostel Fee Payment")
        print("2. Update Hostel Fee Amount")
        print("3. View Hostel Fee Status & Balance")
        print("4. Return to Main Menu")
        print("-" * 65)

        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            print_header("RECORD HOSTEL FEE PAYMENT")
            s_id = input("Enter Student ID: ").strip().upper()
            try:
                statement = fee_module.calculate_pending_fees(s_id, data_mgr)
                print(f"Current Hostel Fee: ₹{statement['Hostel_Fee']:,.2f}")
                print(f"Amount Already Paid: ₹{statement['Hostel_Paid']:,.2f}")
                print(f"Pending Balance: ₹{statement['Hostel_Pending']:,.2f}")
                if statement["Hostel_Pending"] <= 0:
                    print("\n[INFO] Student has already fully paid hostel fees!")
                    pause()
                    continue

                amount_str = input("\nEnter Payment Amount (₹): ").strip()
                date_str = input("Enter Payment Date (YYYY-MM-DD or Enter for today): ").strip()
                res = fee_module.record_hostel_payment(
                    s_id,
                    float(amount_str),
                    data_mgr,
                    payment_date=date_str or None
                )
                print(f"\n[SUCCESS] Payment of ₹{res['Amount_Paid']:,.2f} recorded for {s_id}!")
                print(f"[INFO] New Hostel Paid Total: ₹{res['Total_Hostel_Paid']:,.2f}")
                print(f"[INFO] Remaining Hostel Balance: ₹{res['Remaining_Hostel_Balance']:,.2f}")
            except Exception as e:
                print(f"\n[ERROR] Failed to record payment: {e}")
            pause()

        elif choice == "2":
            print_header("UPDATE HOSTEL FEE AMOUNT")
            s_id = input("Enter Student ID: ").strip().upper()
            new_fee_str = input("Enter New Hostel Fee Amount (₹): ").strip()
            try:
                res = fee_module.update_hostel_fee(s_id, float(new_fee_str), data_mgr)
                print(f"\n[SUCCESS] Updated Hostel Fee for {s_id} to ₹{float(res['Hostel_Fee']):,.2f}")
            except Exception as e:
                print(f"\n[ERROR] Update failed: {e}")
            pause()

        elif choice == "3":
            print_header("HOSTEL FEE STATUS & BALANCE")
            s_id = input("Enter Student ID (or press Enter for all): ").strip().upper()
            try:
                status_list = fee_module.display_fee_status(data_mgr, student_id=s_id or None)
                if not status_list:
                    print("No records found.")
                else:
                    simplified = [
                        {
                            "Student_ID": s["Student_ID"],
                            "Hostel_Fee": f"₹{s['Hostel_Fee']:,.2f}",
                            "Hostel_Paid": f"₹{s['Hostel_Paid']:,.2f}",
                            "Hostel_Pending": f"₹{s['Hostel_Pending']:,.2f}",
                            "Status": s["Hostel_Status"],
                            "Due_Date": s["Due_Date"],
                        }
                        for s in status_list
                    ]
                    print(format_table(simplified))
            except Exception as e:
                print(f"\n[ERROR]: {e}")
            pause()

        elif choice == "4":
            break
        else:
            print("[ERROR] Invalid choice.")
            pause()


# -------------------------------------------------------------
# 4. Mess Fee Management Submenu
# -------------------------------------------------------------
def mess_fee_menu(data_mgr: DataManager) -> None:
    while True:
        print_header("MESS FEE MANAGEMENT")
        print("1. Record Mess Fee Payment")
        print("2. Update Mess Fee Amount")
        print("3. View Mess Fee Status & Balance")
        print("4. Return to Main Menu")
        print("-" * 65)

        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            print_header("RECORD MESS FEE PAYMENT")
            s_id = input("Enter Student ID: ").strip().upper()
            try:
                statement = fee_module.calculate_pending_fees(s_id, data_mgr)
                print(f"Current Mess Fee: ₹{statement['Mess_Fee']:,.2f}")
                print(f"Amount Already Paid: ₹{statement['Mess_Paid']:,.2f}")
                print(f"Pending Balance: ₹{statement['Mess_Pending']:,.2f}")
                if statement["Mess_Pending"] <= 0:
                    print("\n[INFO] Student has already fully paid mess fees!")
                    pause()
                    continue

                amount_str = input("\nEnter Payment Amount (₹): ").strip()
                date_str = input("Enter Payment Date (YYYY-MM-DD or Enter for today): ").strip()
                res = fee_module.record_mess_payment(
                    s_id,
                    float(amount_str),
                    data_mgr,
                    payment_date=date_str or None
                )
                print(f"\n[SUCCESS] Payment of ₹{res['Amount_Paid']:,.2f} recorded for {s_id}!")
                print(f"[INFO] New Mess Paid Total: ₹{res['Total_Mess_Paid']:,.2f}")
                print(f"[INFO] Remaining Mess Balance: ₹{res['Remaining_Mess_Balance']:,.2f}")
            except Exception as e:
                print(f"\n[ERROR] Failed to record payment: {e}")
            pause()

        elif choice == "2":
            print_header("UPDATE MESS FEE AMOUNT")
            s_id = input("Enter Student ID: ").strip().upper()
            new_fee_str = input("Enter New Mess Fee Amount (₹): ").strip()
            try:
                res = fee_module.update_mess_fee(s_id, float(new_fee_str), data_mgr)
                print(f"\n[SUCCESS] Updated Mess Fee for {s_id} to ₹{float(res['Mess_Fee']):,.2f}")
            except Exception as e:
                print(f"\n[ERROR] Update failed: {e}")
            pause()

        elif choice == "3":
            print_header("MESS FEE STATUS & BALANCE")
            s_id = input("Enter Student ID (or press Enter for all): ").strip().upper()
            try:
                status_list = fee_module.display_fee_status(data_mgr, student_id=s_id or None)
                if not status_list:
                    print("No records found.")
                else:
                    simplified = [
                        {
                            "Student_ID": s["Student_ID"],
                            "Mess_Fee": f"₹{s['Mess_Fee']:,.2f}",
                            "Mess_Paid": f"₹{s['Mess_Paid']:,.2f}",
                            "Mess_Pending": f"₹{s['Mess_Pending']:,.2f}",
                            "Status": s["Mess_Status"],
                            "Due_Date": s["Due_Date"],
                        }
                        for s in status_list
                    ]
                    print(format_table(simplified))
            except Exception as e:
                print(f"\n[ERROR]: {e}")
            pause()

        elif choice == "4":
            break
        else:
            print("[ERROR] Invalid choice.")
            pause()


# -------------------------------------------------------------
# 10. Data Analysis Submenu (NumPy & Pandas)
# -------------------------------------------------------------
def data_analysis_menu(data_mgr: DataManager) -> None:
    while True:
        print_header("DATA ANALYSIS (NUMPY & PANDAS)")
        print("1. Numerical & Statistical Analysis using NumPy")
        print("2. Pandas Dataset Processing (Head/Tail, Columns, Missing Values)")
        print("3. Course-wise Student & Fee Collection Breakdown")
        print("4. Room & Floor Occupancy Breakdown")
        print("5. Demographic Analysis (Gender & Academic Year)")
        print("6. Comparative Analysis (Hostel vs Mess Collections & Dues)")
        print("7. Return to Main Menu")
        print("-" * 65)

        choice = input("Enter choice (1-7): ").strip()
        if choice == "1":
            print_header("NUMPY NUMERICAL & STATISTICAL ANALYSIS")
            res = analysis_module.run_numpy_analysis(data_mgr)
            stats = res["stats"]

            print("--- 1D ARRAY STATISTICAL CALCULATIONS ---")
            print(f"Total Hostel Fees Billed (np.sum)  : ₹{stats['hostel_fee_sum']:,.2f}")
            print(f"Total Hostel Fees Paid (np.sum)    : ₹{stats['hostel_paid_sum']:,.2f}")
            print(f"Total Hostel Dues Pending (np.sum) : ₹{stats['hostel_pending_sum']:,.2f}")
            print(f"Total Mess Fees Billed (np.sum)    : ₹{stats['mess_fee_sum']:,.2f}")
            print(f"Total Mess Fees Paid (np.sum)      : ₹{stats['mess_paid_sum']:,.2f}")
            print(f"Total Mess Dues Pending (np.sum)   : ₹{stats['mess_pending_sum']:,.2f}")
            print(f"Combined Total Fees Collected      : ₹{stats['total_paid_sum']:,.2f}")
            print(f"Combined Total Outstanding Dues    : ₹{stats['total_pending_sum']:,.2f}")
            print()
            print(f"Mean Hostel Fee Billed (np.mean)   : ₹{stats['hostel_fee_mean']:,.2f}")
            print(f"Mean Hostel Fee Paid (np.mean)     : ₹{stats['hostel_paid_mean']:,.2f}")
            print(f"Mean Mess Fee Paid (np.mean)       : ₹{stats['mess_paid_mean']:,.2f}")
            print(f"Mean Total Payment (np.mean)       : ₹{stats['total_paid_mean']:,.2f}")
            print()
            print(f"Maximum Total Payment (np.max)     : ₹{stats['total_paid_max']:,.2f}")
            print(f"Minimum Total Payment (np.min)     : ₹{stats['total_paid_min']:,.2f}")
            print(f"Standard Deviation of Paid Fees    : ₹{stats['total_paid_std']:,.2f}")
            print()
            print("--- 2D ARRAY MATRIX OPERATIONS & SLICING ---")
            print(f"Fee Matrix Shape (N, 4)            : {res['fee_matrix_shape']}")
            print(f"Room Matrix Shape (M, 3)           : {res['room_matrix_shape']}")
            print(f"Indexed [0, 0] (1st Student H-Fee) : ₹{res['indexed_values']['first_student_hostel_fee']:,.2f}")
            print(f"Indexed [0, 3] (1st Student M-Paid): ₹{res['indexed_values']['first_student_mess_paid']:,.2f}")
            print("2D Slicing Sample [:5, :2] (First 5 students [Hostel_Fee, Hostel_Paid]):")
            for idx, row in enumerate(res["slice_sample"], 1):
                print(f"  Student {idx}: Fee = ₹{row[0]:,.2f}, Paid = ₹{row[1]:,.2f}")
            pause()

        elif choice == "2":
            print_header("PANDAS DATASET DEMONSTRATIONS")
            head_df, tail_df = analysis_module.get_students_head_tail(data_mgr, 5)
            print("--- FIRST 5 STUDENTS (df.head(5)) ---")
            print(format_table(head_df))
            print("\n--- LAST 5 STUDENTS (df.tail(5)) ---")
            print(format_table(tail_df))

            print("\n--- SELECTED COLUMNS (Student_ID, Name, Course, Room_No) ---")
            sel_df = analysis_module.get_selected_student_columns(data_mgr).head(5)
            print(format_table(sel_df))

            print("\n--- STATISTICAL DESCRIPTION (df.describe()) ---")
            describe_df = analysis_module.get_fee_statistics_describe(data_mgr)
            print(format_table(describe_df))

            print("\n--- MISSING VALUE HANDLING DEMONSTRATION (isna, fillna) ---")
            mv = analysis_module.demonstrate_missing_value_handling(data_mgr)
            print("Missing values detected before imputation:", mv["pre_impute_missing"])
            print("Missing values after safe fillna():", mv["post_impute_missing"])
            print("Sample Cleaned Table:")
            print(format_table(mv["sample_cleaned_head"][:4]))
            pause()

        elif choice == "3":
            print_header("COURSE-WISE STUDENT & FEE BREAKDOWN")
            df = analysis_module.get_course_fee_breakdown(data_mgr)
            # Format numbers for display
            display_df = df.copy()
            for col in ["Total_Billed", "Total_Collected", "Total_Pending"]:
                display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
            display_df["Collection_Rate_%"] = display_df["Collection_Rate_%"].apply(lambda x: f"{x:.2f}%")
            print(format_table(display_df))
            pause()

        elif choice == "4":
            print_header("ROOM & FLOOR OCCUPANCY ANALYSIS")
            print("--- OCCUPANCY BY ROOM TYPE ---")
            type_df = analysis_module.group_room_occupancy_by_type(data_mgr)
            print(format_table(type_df))

            print("\n--- OCCUPANCY BY FLOOR ---")
            floor_df = analysis_module.group_room_occupancy_by_floor(data_mgr)
            print(format_table(floor_df))
            pause()

        elif choice == "5":
            print_header("DEMOGRAPHIC DISTRIBUTION")
            comp = analysis_module.run_comparative_analysis(data_mgr)
            print("--- GENDER-WISE DISTRIBUTION ---")
            for g, count in comp["gender_distribution"].items():
                print(f"  {g.ljust(15)}: {count} students")

            print("\n--- ACADEMIC YEAR DISTRIBUTION ---")
            for y, count in sorted(comp["year_distribution"].items()):
                print(f"  Year {y}          : {count} students")

            print("\n--- COURSE ENROLLMENT RANKING ---")
            for c, count in sorted(comp["course_distribution"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {c.ljust(20)}: {count} students")
            pause()

        elif choice == "6":
            print_header("COMPARATIVE FEE ANALYSIS")
            comp = analysis_module.run_comparative_analysis(data_mgr)
            print(f"Total Hostel Fees Collected : ₹{comp['hostel_collected']:,.2f}")
            print(f"Total Mess Fees Collected   : ₹{comp['mess_collected']:,.2f}")
            print(f"Hostel Outstanding Dues     : ₹{comp['hostel_outstanding']:,.2f}")
            print(f"Mess Outstanding Dues       : ₹{comp['mess_outstanding']:,.2f}")
            print(f"Category with Higher Dues   : {comp['higher_due_category']}")
            print(f"Course with Highest Students: {comp['top_course']}")
            pause()

        elif choice == "7":
            break
        else:
            print("[ERROR] Invalid choice.")
            pause()


# -------------------------------------------------------------
# Main Application Flow
# -------------------------------------------------------------
def main() -> None:
    """Main program entry point."""
    data_mgr = DataManager()

    # Programmatic initialization: do not overwrite user data if present
    is_new = initialize_datasets(data_mgr, count=100, force=False)
    if is_new:
        print("[INIT] Created initial realistic datasets (100 students, 46 rooms, 100 fee records).")
    else:
        # Synchronize occupancy numbers with student assignments on start
        data_mgr.sync_room_occupancies()

    while True:
        print_header("HOSTEL MANAGEMENT SYSTEM")
        print(" 1. Student Management")
        print(" 2. Room Allocation Management")
        print(" 3. Hostel Fee Management")
        print(" 4. Mess Fee Management")
        print(" 5. Display All Student Records")
        print(" 6. Search Student")
        print(" 7. Room Vacancy Report")
        print(" 8. Fee Status Report")
        print(" 9. Generate Summary Report")
        print("10. Data Analysis using NumPy and Pandas")
        print("11. Export Reports")
        print("12. Exit")
        print("=" * 65)

        choice = input("Enter choice (1-12): ").strip()

        if choice == "1":
            student_management_menu(data_mgr)

        elif choice == "2":
            room_allocation_menu(data_mgr)

        elif choice == "3":
            hostel_fee_menu(data_mgr)

        elif choice == "4":
            mess_fee_menu(data_mgr)

        elif choice == "5":
            print_header("ALL REGISTERED STUDENTS")
            students = student_module.display_students(data_mgr)
            print(format_table(students))
            print(f"\nTotal Records: {len(students)}")
            pause()

        elif choice == "6":
            print_header("SEARCH STUDENT")
            query = input("Enter Student ID or Name: ").strip()
            if not query:
                print("[WARNING] Search query cannot be empty.")
            else:
                student = student_module.search_student(query, data_mgr)
                if not student:
                    print(f"No student record found for '{query}'.")
                else:
                    print("\nStudent Details:")
                    print(format_table([student]))
                    # Also show room and fee statement
                    try:
                        stmt = fee_module.calculate_pending_fees(student["Student_ID"], data_mgr)
                        print("\nFee Statement:")
                        fee_summary = [{
                            "Hostel_Fee": f"₹{stmt['Hostel_Fee']:,.2f}",
                            "Hostel_Paid": f"₹{stmt['Hostel_Paid']:,.2f}",
                            "Hostel_Due": f"₹{stmt['Hostel_Pending']:,.2f}",
                            "Hostel_Status": stmt["Hostel_Status"],
                            "Mess_Fee": f"₹{stmt['Mess_Fee']:,.2f}",
                            "Mess_Paid": f"₹{stmt['Mess_Paid']:,.2f}",
                            "Mess_Due": f"₹{stmt['Mess_Pending']:,.2f}",
                            "Mess_Status": stmt["Mess_Status"],
                            "Total_Due": f"₹{stmt['Total_Pending']:,.2f}",
                            "Overall": stmt["Overall_Status"],
                        }]
                        print(format_table(fee_summary))
                    except Exception:
                        pass
            pause()

        elif choice == "7":
            print_header("ROOM VACANCY REPORT")
            vacant = room_module.check_vacancy(data_mgr)
            if not vacant:
                print("No rooms currently have vacancies.")
            else:
                print(format_table(vacant))
                total_vac = sum(r["Vacancy"] for r in vacant)
                print(f"\nTotal Vacant Beds: {total_vac} across {len(vacant)} available rooms.")
            pause()

        elif choice == "8":
            print_header("FEE STATUS REPORT")
            print("Filter Options: 1. All | 2. Paid | 3. Partial | 4. Pending | 5. Overdue")
            filt_choice = input("Select filter (1-5, or press Enter for All): ").strip()
            filt_map = {"2": "PAID", "3": "PARTIAL", "4": "PENDING", "5": "OVERDUE"}
            target_filter = filt_map.get(filt_choice, None)

            status_list = fee_module.display_fee_status(data_mgr, status_filter=target_filter)
            if not status_list:
                print("No fee records matching filter.")
            else:
                formatted = [
                    {
                        "Student_ID": s["Student_ID"],
                        "Hostel_Fee": f"₹{s['Hostel_Fee']:,.2f}",
                        "Hostel_Paid": f"₹{s['Hostel_Paid']:,.2f}",
                        "Mess_Fee": f"₹{s['Mess_Fee']:,.2f}",
                        "Mess_Paid": f"₹{s['Mess_Paid']:,.2f}",
                        "Total_Due": f"₹{s['Total_Pending']:,.2f}",
                        "Hostel_Status": s["Hostel_Status"],
                        "Mess_Status": s["Mess_Status"],
                        "Overall": s["Overall_Status"],
                        "Due_Date": s["Due_Date"],
                    }
                    for s in status_list
                ]
                print(format_table(formatted[:30]))
                if len(formatted) > 30:
                    print(f"\n(Showing first 30 of {len(formatted)} matching records)")
                print(f"\nTotal Matching Records: {len(formatted)}")
            pause()

        elif choice == "9":
            print_header("HOSTEL MANAGEMENT SUMMARY REPORT")
            report = analysis_module.generate_summary_report(data_mgr)
            display_rows = []
            for k, v in report.items():
                if not k.startswith("_"):
                    display_rows.append({"Metric": k, "Value": v})
            print(format_table(display_rows))
            pause()

        elif choice == "10":
            data_analysis_menu(data_mgr)

        elif choice == "11":
            print_header("EXPORT REPORTS")
            files = analysis_module.export_report(data_mgr)
            print(f"[SUCCESS] Successfully generated {len(files)} reports:")
            for fp in files:
                print(f"  -> {fp}")
            pause()

        elif choice == "12":
            print("\nThank you for using the Hostel Management System. Goodbye!")
            sys.exit(0)

        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 12.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user. Exiting safely.")
        sys.exit(0)
