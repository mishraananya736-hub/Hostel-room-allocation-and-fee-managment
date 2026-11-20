"""
Room Management Module for Hostel Management System.
Handles room allocation, vacancy tracking, capacity validation, and reassignment.
Demonstrates: Tuples (room configurations), Sets (unique room numbers, occupancy checks),
Lists and Dictionaries.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any, Set
import pandas as pd
from data_manager import DataManager

# Room type configurations as Tuple
ROOM_CONFIG_TUPLE: Tuple[Tuple[str, int, float], ...] = (
    ("Single", 1, 55000.0),
    ("Double", 2, 40000.0),
    ("Triple", 3, 30000.0),
    ("Four-Bed", 4, 22000.0),
)


def display_room_details(data_mgr: DataManager, room_no: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Display details of a specific room or all rooms.
    Returns list of room dictionaries.
    """
    rooms_df = data_mgr.load_rooms_df()
    if room_no:
        room_clean = str(room_no).strip()
        filtered = rooms_df[rooms_df["Room_No"] == room_clean]
        if filtered.empty:
            raise ValueError(f"Room '{room_no}' not found.")
        return filtered.to_dict(orient="records")
    return rooms_df.to_dict(orient="records")


def check_vacancy(
    data_mgr: DataManager,
    room_type: Optional[str] = None,
    floor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Check and filter available rooms with vacant beds.
    Demonstrates filtering and set operations.
    """
    rooms_df = data_mgr.load_rooms_df()
    vacant_df = rooms_df[rooms_df["Vacancy"] > 0]

    if room_type:
        vacant_df = vacant_df[vacant_df["Room_Type"].str.lower() == room_type.strip().lower()]
    if floor is not None:
        try:
            fl_int = int(floor)
            vacant_df = vacant_df[vacant_df["Floor"] == fl_int]
        except (ValueError, TypeError):
            pass

    return vacant_df.to_dict(orient="records")


def get_occupied_rooms(data_mgr: DataManager) -> List[Dict[str, Any]]:
    """Return rooms that have at least one occupant."""
    rooms_df = data_mgr.load_rooms_df()
    occupied = rooms_df[rooms_df["Occupied"] > 0]
    return occupied.to_dict(orient="records")


def get_vacant_rooms(data_mgr: DataManager) -> List[Dict[str, Any]]:
    """Return rooms that have at least one vacant bed."""
    rooms_df = data_mgr.load_rooms_df()
    vacant = rooms_df[rooms_df["Vacancy"] > 0]
    return vacant.to_dict(orient="records")


def allocate_room(student_id: str, room_no: str, data_mgr: DataManager) -> Dict[str, Any]:
    """
    Allocate a room bed to a student.
    Enforces:
      - Student existence.
      - Room existence.
      - Student not already allocated (prevents duplicate allocation).
      - Room capacity not exceeded.
    Synchronizes students.csv, rooms.csv, and updates hostel fee if needed.
    """
    student_id = str(student_id).strip().upper()
    room_no = str(room_no).strip()

    def _tx(mgr: DataManager):
        students = mgr.load_students_list()
        student_idx = -1
        for idx, s in enumerate(students):
            if s.get("Student_ID") == student_id:
                student_idx = idx
                break

        if student_idx == -1:
            raise ValueError(f"Student '{student_id}' does not exist.")

        student = students[student_idx]
        current_room = student.get("Room_No", "").strip()
        if current_room:
            raise ValueError(f"Student '{student_id}' is already allocated to Room '{current_room}'. Use reassign_room instead.")

        # Check room
        rooms_df = mgr.load_rooms_df()
        room_match = rooms_df[rooms_df["Room_No"] == room_no]
        if room_match.empty:
            raise ValueError(f"Room '{room_no}' does not exist.")

        room_row = room_match.iloc[0]
        capacity = int(room_row["Capacity"])
        occupied = int(room_row["Occupied"])
        vacancy = int(room_row["Vacancy"])

        if vacancy <= 0 or occupied >= capacity:
            raise ValueError(f"Room '{room_no}' is already full (Capacity: {capacity}, Occupied: {occupied}).")

        # Perform allocation
        student["Room_No"] = room_no
        students[student_idx] = student
        mgr.save_students_list(students)
        mgr.sync_room_occupancies()

        # Update fee based on room type
        rtype = str(room_row["Room_Type"])
        fee_map = {cfg[0]: cfg[2] for cfg in ROOM_CONFIG_TUPLE}
        new_fee = fee_map.get(rtype, 35000.0)

        fees = mgr.load_fees_list()
        for f in fees:
            if f.get("Student_ID") == student_id:
                f["Hostel_Fee"] = new_fee
                break
        mgr.save_fees_list(fees)

        return {"student_id": student_id, "room_no": room_no, "room_type": rtype, "status": "Allocated"}

    return data_mgr.execute_transaction(_tx)


def vacate_room(student_id: str, data_mgr: DataManager) -> Dict[str, Any]:
    """
    Vacate a student's current room.
    Updates student record and recalculates room occupancy.
    """
    student_id = str(student_id).strip().upper()

    def _tx(mgr: DataManager):
        students = mgr.load_students_list()
        student_idx = -1
        for idx, s in enumerate(students):
            if s.get("Student_ID") == student_id:
                student_idx = idx
                break

        if student_idx == -1:
            raise ValueError(f"Student '{student_id}' does not exist.")

        student = students[student_idx]
        old_room = student.get("Room_No", "").strip()
        if not old_room:
            raise ValueError(f"Student '{student_id}' currently has no room allocated.")

        student["Room_No"] = ""
        students[student_idx] = student
        mgr.save_students_list(students)
        mgr.sync_room_occupancies()

        return {"student_id": student_id, "vacated_room": old_room, "status": "Vacated"}

    return data_mgr.execute_transaction(_tx)


def reassign_room(student_id: str, new_room_no: str, data_mgr: DataManager) -> Dict[str, Any]:
    """
    Change a student's allocated room from current room to new room.
    Enforces capacity check on the target room and adjusts occupancies for both rooms.
    """
    student_id = str(student_id).strip().upper()
    new_room_no = str(new_room_no).strip()

    def _tx(mgr: DataManager):
        students = mgr.load_students_list()
        student_idx = -1
        for idx, s in enumerate(students):
            if s.get("Student_ID") == student_id:
                student_idx = idx
                break

        if student_idx == -1:
            raise ValueError(f"Student '{student_id}' does not exist.")

        student = students[student_idx]
        old_room = student.get("Room_No", "").strip()

        if old_room == new_room_no:
            raise ValueError(f"Student is already in Room '{new_room_no}'.")

        # Validate target room
        rooms_df = mgr.load_rooms_df()
        new_match = rooms_df[rooms_df["Room_No"] == new_room_no]
        if new_match.empty:
            raise ValueError(f"Target room '{new_room_no}' does not exist.")

        new_row = new_match.iloc[0]
        if int(new_row["Vacancy"]) <= 0:
            raise ValueError(f"Target room '{new_room_no}' is full (Capacity: {new_row['Capacity']}, Occupied: {new_row['Occupied']}).")

        # Reassign
        student["Room_No"] = new_room_no
        students[student_idx] = student
        mgr.save_students_list(students)
        mgr.sync_room_occupancies()

        # Update fee for the new room type
        rtype = str(new_row["Room_Type"])
        fee_map = {cfg[0]: cfg[2] for cfg in ROOM_CONFIG_TUPLE}
        new_fee = fee_map.get(rtype, 35000.0)

        fees = mgr.load_fees_list()
        for f in fees:
            if f.get("Student_ID") == student_id:
                f["Hostel_Fee"] = new_fee
                break
        mgr.save_fees_list(fees)

        return {
            "student_id": student_id,
            "old_room": old_room,
            "new_room": new_room_no,
            "new_room_type": rtype,
            "status": "Reassigned",
        }

    return data_mgr.execute_transaction(_tx)
