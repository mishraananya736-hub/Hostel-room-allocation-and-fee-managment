"""
Student Management Module for Hostel Management System.
Implements CRUD operations, validations, and integration with room and fee modules.
Demonstrates: List, Dict, Set, Tuple, List methods (append, remove, sort), Dict methods (get, update, keys, values).
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple, Any, Set
import pandas as pd
from data_manager import DataManager

# Tuple of valid genders and years (Demonstrating Tuple concept)
VALID_GENDERS: Tuple[str, ...] = ("Male", "Female", "Other")
VALID_YEARS: Tuple[int, ...] = (1, 2, 3, 4, 5)


def validate_contact(contact: str) -> bool:
    """Validate 10-digit Indian phone number."""
    contact_str = str(contact).strip()
    return bool(re.fullmatch(r"[6-9]\d{9}", contact_str))


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format (alphanumeric, at least 3 chars)."""
    s_id = str(student_id).strip()
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,15}", s_id))


def add_student(
    student_id: str,
    name: str,
    gender: str,
    course: str,
    year: int,
    contact: str,
    data_mgr: DataManager,
    room_no: str = "",
) -> Dict[str, Any]:
    """
    Register a new student with comprehensive validation.
    Integrates with rooms (if room_no specified) and initializes default fees.
    """
    student_id = str(student_id).strip().upper()
    name = str(name).strip()
    gender = str(gender).strip().capitalize()
    course = str(course).strip()
    contact = str(contact).strip()
    room_no = str(room_no).strip()

    # Validations
    if not validate_student_id(student_id):
        raise ValueError(f"Invalid Student ID '{student_id}'. Must be 3-15 alphanumeric characters.")
    if not name or len(name) < 2:
        raise ValueError("Student name must be at least 2 characters.")
    if gender not in VALID_GENDERS:
        raise ValueError(f"Invalid gender '{gender}'. Must be one of {VALID_GENDERS}.")
    if not course:
        raise ValueError("Course cannot be empty.")
    try:
        year = int(year)
        if year not in VALID_YEARS:
            raise ValueError()
    except Exception:
        raise ValueError(f"Invalid year '{year}'. Must be an integer between 1 and 5.")
    if not validate_contact(contact):
        raise ValueError(f"Invalid contact '{contact}'. Must be a 10-digit number starting with 6-9.")

    # Load existing students list (Demonstrating List and Set data structures)
    students = data_mgr.load_students_list()
    existing_ids: Set[str] = {s.get("Student_ID") for s in students}  # Set concept
    if student_id in existing_ids:
        raise ValueError(f"Student with ID '{student_id}' already exists.")

    # Validate room if provided
    rooms_df = data_mgr.load_rooms_df()
    room_record = None
    if room_no:
        match = rooms_df[rooms_df["Room_No"] == room_no]
        if match.empty:
            raise ValueError(f"Room '{room_no}' does not exist.")
        room_row = match.iloc[0]
        if int(room_row["Vacancy"]) <= 0:
            raise ValueError(f"Room '{room_no}' has no vacancy (Capacity: {room_row['Capacity']}, Occupied: {room_row['Occupied']}).")
        room_record = room_row.to_dict()

    # Create new student dictionary (Demonstrating Dict and Dict methods)
    new_student: Dict[str, Any] = {
        "Student_ID": student_id,
        "Name": name,
        "Gender": gender,
        "Course": course,
        "Year": year,
        "Room_No": room_no,
        "Contact": contact,
    }

    # Atomic transaction across student, room, and fees
    def _tx(mgr: DataManager):
        # 1. Append student (Demonstrating List append method)
        st_list = mgr.load_students_list()
        st_list.append(new_student)
        mgr.save_students_list(st_list)

        # 2. Update room occupancy if allocated
        if room_no:
            mgr.sync_room_occupancies()

        # 3. Create initial fee record
        fees_list = mgr.load_fees_list()
        # Default hostel fee according to room type
        hostel_fee = 35000.0
        if room_record:
            rtype = room_record.get("Room_Type", "Double")
            fee_map = {"Single": 55000.0, "Double": 40000.0, "Triple": 30000.0, "Four-Bed": 22000.0}
            hostel_fee = fee_map.get(rtype, 35000.0)

        from datetime import datetime, timedelta
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        new_fee_entry: Dict[str, Any] = {
            "Student_ID": student_id,
            "Hostel_Fee": hostel_fee,
            "Hostel_Paid": 0.0,
            "Mess_Fee": 25000.0,
            "Mess_Paid": 0.0,
            "Payment_Date": "",
            "Due_Date": due_date,
        }
        fees_list.append(new_fee_entry)
        mgr.save_fees_list(fees_list)

    data_mgr.execute_transaction(_tx)
    return new_student


def search_student(query: str, data_mgr: DataManager) -> Optional[Dict[str, Any]]:
    """
    Search student by Student_ID (exact) or Name (case-insensitive substring).
    Returns student dictionary or None.
    """
    query_clean = str(query).strip()
    if not query_clean:
        return None

    students = data_mgr.load_students_list()
    # First attempt exact ID match
    for student in students:
        if student.get("Student_ID", "").upper() == query_clean.upper():
            return student

    # Second attempt name match
    for student in students:
        if query_clean.lower() in student.get("Name", "").lower():
            return student

    return None


def search_students_multi(query: str, data_mgr: DataManager) -> List[Dict[str, Any]]:
    """Search multiple students by partial ID, name, course, or room number."""
    query_clean = str(query).strip().lower()
    if not query_clean:
        return []

    students = data_mgr.load_students_list()
    matches: List[Dict[str, Any]] = []
    for s in students:
        if (
            query_clean in s.get("Student_ID", "").lower()
            or query_clean in s.get("Name", "").lower()
            or query_clean in s.get("Course", "").lower()
            or query_clean == s.get("Room_No", "").lower()
        ):
            matches.append(s)
    return matches


def update_student(student_id: str, update_fields: Dict[str, Any], data_mgr: DataManager) -> Dict[str, Any]:
    """
    Update student attributes (e.g. Name, Contact, Course, Year).
    Demonstrates dictionary update() and get() methods.
    """
    student_id = str(student_id).strip().upper()
    students = data_mgr.load_students_list()

    target_idx = -1
    for idx, s in enumerate(students):
        if s.get("Student_ID") == student_id:
            target_idx = idx
            break

    if target_idx == -1:
        raise ValueError(f"Student with ID '{student_id}' not found.")

    target_student = students[target_idx]

    # Validate updates
    if "Contact" in update_fields:
        if not validate_contact(update_fields["Contact"]):
            raise ValueError(f"Invalid contact '{update_fields['Contact']}'. Must be 10 digits starting with 6-9.")
    if "Year" in update_fields:
        try:
            y = int(update_fields["Year"])
            if y not in VALID_YEARS:
                raise ValueError()
            update_fields["Year"] = y
        except Exception:
            raise ValueError(f"Invalid academic year '{update_fields['Year']}'.")
    if "Gender" in update_fields:
        g = str(update_fields["Gender"]).strip().capitalize()
        if g not in VALID_GENDERS:
            raise ValueError(f"Invalid gender '{g}'.")
        update_fields["Gender"] = g

    # Prevent changing Student_ID or Room_No through generic update_student
    # (Room_No must be modified through room_module.reassign_room)
    allowed_keys = {"Name", "Gender", "Course", "Year", "Contact"}
    sanitized_updates = {k: v for k, v in update_fields.items() if k in allowed_keys}

    # Dict update method
    target_student.update(sanitized_updates)
    students[target_idx] = target_student

    data_mgr.save_students_list(students)
    return target_student


def delete_student(student_id: str, data_mgr: DataManager, cascade: bool = True) -> Dict[str, Any]:
    """
    Delete a student record permanently.
    Safely updates room occupancy and removes fee records within an atomic transaction.
    """
    student_id = str(student_id).strip().upper()

    def _tx(mgr: DataManager):
        students = mgr.load_students_list()
        found_student = None
        for s in students:
            if s.get("Student_ID") == student_id:
                found_student = s
                break

        if not found_student:
            raise ValueError(f"Student with ID '{student_id}' does not exist.")

        # Remove from students list (Demonstrating List remove method)
        students.remove(found_student)
        mgr.save_students_list(students)

        # Update room occupancy if was allocated
        if found_student.get("Room_No"):
            mgr.sync_room_occupancies()

        # Handle fee record
        if cascade:
            fees = mgr.load_fees_list()
            updated_fees = [f for f in fees if f.get("Student_ID") != student_id]
            mgr.save_fees_list(updated_fees)

        return found_student

    return data_mgr.execute_transaction(_tx)


def display_students(data_mgr: DataManager, students_list: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Return and optionally format students list.
    Demonstrates list sorting.
    """
    if students_list is None:
        students_list = data_mgr.load_students_list()

    # Sort students by Student_ID (Demonstrating List sort method)
    sorted_students = sorted(students_list, key=lambda s: s.get("Student_ID", ""))
    return sorted_students
