"""
Initialization Module for Hostel Management System.
Generates realistic sample datasets (100 students, 46 rooms, 100 fee records)
respecting foreign key relationships, room capacities, and diverse payment statuses.
"""

from __future__ import annotations
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pandas as pd
from data_manager import DataManager, STUDENT_COLUMNS, ROOM_COLUMNS, FEE_COLUMNS

# Fixed configuration tuples (Demonstrating Tuple concept)
ROOM_TYPE_CONFIGS: Tuple[Tuple[str, int, float], ...] = (
    ("Single", 1, 55000.0),
    ("Double", 2, 40000.0),
    ("Triple", 3, 30000.0),
    ("Four-Bed", 4, 22000.0),
)

STANDARD_MESS_FEE = 25000.0

COURSES = (
    "B.Tech CSE",
    "B.Tech ECE",
    "B.Tech ME",
    "B.Tech Civil",
    "B.Tech IT",
    "MCA",
    "M.Tech",
)

FIRST_NAMES_MALE = [
    "Aarav", "Rohan", "Vikram", "Aditya", "Rahul", "Amit", "Kunal", "Siddharth",
    "Varun", "Manish", "Nikhil", "Gaurav", "Deepak", "Aniket", "Harsh", "Pranav",
    "Ayush", "Kartik", "Shubham", "Yash", "Dev", "Alok", "Akash", "Tushar", "Arjun"
]

FIRST_NAMES_FEMALE = [
    "Ananya", "Pooja", "Sneha", "Priya", "Ishita", "Riya", "Kavya", "Tanvi",
    "Megha", "Shreya", "Neha", "Divya", "Aditi", "Simran", "Preeti", "Bhavna",
    "Kritika", "Sanya", "Swati", "Nandini", "Pallavi", "Radhika", "Sakshi", "Aarti", "Muskan"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Patel", "Kumar", "Mishra",
    "Choudhary", "Joshi", "Saxena", "Bhatia", "Reddy", "Nair", "Das", "Deshmukh",
    "Yadav", "Agarwal", "Rao", "Mehta", "Iyer", "Kulkarni", "Chauhan", "Bansal"
]


def generate_initial_rooms() -> List[Dict[str, Any]]:
    """
    Generate room records across 4 floors with various types and capacities.
    Total capacity ~ 124 beds, allowing 100 students to occupy with remaining vacancies.
    """
    rooms: List[Dict[str, Any]] = []
    # Distribution of rooms per floor:
    # 4 floors (1, 2, 3, 4)
    # Floor 1: 101-112 (12 rooms)
    # Floor 2: 201-212 (12 rooms)
    # Floor 3: 301-311 (11 rooms)
    # Floor 4: 401-411 (11 rooms)
    # Total = 46 rooms
    floor_distribution = [
        (1, 12),
        (2, 12),
        (3, 11),
        (4, 11),
    ]

    config_cycle = [
        ("Single", 1),
        ("Double", 2),
        ("Double", 2),
        ("Triple", 3),
        ("Triple", 3),
        ("Four-Bed", 4),
    ]

    for floor, num_rooms in floor_distribution:
        for idx in range(1, num_rooms + 1):
            room_no = f"{floor}{idx:02d}"
            config = config_cycle[(idx - 1) % len(config_cycle)]
            room_type = config[0]
            capacity = config[1]
            rooms.append({
                "Room_No": room_no,
                "Floor": floor,
                "Room_Type": room_type,
                "Capacity": capacity,
                "Occupied": 0,
                "Vacancy": capacity,
            })

    return rooms


def generate_sample_dataset(count: int = 100, seed: int = 42) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate realistic 100 student records, rooms, and fees.
    Ensures:
      - Room capacity limits are strictly respected.
      - Foreign key integrity between students and fees.
      - Diverse payment states: Full (40%), Partial (30%), Pending (15%), Overdue (15%).
    """
    rng = random.Random(seed)
    rooms = generate_initial_rooms()

    # Create mapping of room_no -> capacity, room_type, fee
    room_type_fee_map = {cfg[0]: cfg[2] for cfg in ROOM_TYPE_CONFIGS}
    room_capacity_map = {r["Room_No"]: r["Capacity"] for r in rooms}
    room_type_map = {r["Room_No"]: r["Room_Type"] for r in rooms}

    # Available slots list for student allocation
    room_slots: List[str] = []
    for r in rooms:
        room_slots.extend([r["Room_No"]] * r["Capacity"])

    rng.shuffle(room_slots)
    # Take first 'count' slots for the students so room capacities are strictly respected
    allocated_slots = room_slots[:count]

    students: List[Dict[str, Any]] = []
    fees: List[Dict[str, Any]] = []

    today = datetime(2026, 11, 20)
    past_due_date = (today - timedelta(days=25)).strftime("%Y-%m-%d")
    future_due_date = (today + timedelta(days=35)).strftime("%Y-%m-%d")

    used_contacts = set()

    for i in range(1, count + 1):
        student_id = f"STU{1000 + i}"
        gender = "Male" if i % 2 == 1 else "Female"
        first_name = rng.choice(FIRST_NAMES_MALE) if gender == "Male" else rng.choice(FIRST_NAMES_FEMALE)
        last_name = rng.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        course = rng.choice(COURSES)
        year = rng.randint(1, 4) if "B.Tech" in course else rng.randint(1, 2)
        room_no = allocated_slots[i - 1]

        # Generate unique 10-digit Indian mobile number (starts with 9, 8, 7, 6)
        while True:
            contact = f"{rng.choice(['9', '8', '7', '6'])}{rng.randint(100000000, 999999999)}"
            if contact not in used_contacts:
                used_contacts.add(contact)
                break

        students.append({
            "Student_ID": student_id,
            "Name": name,
            "Gender": gender,
            "Course": course,
            "Year": year,
            "Room_No": room_no,
            "Contact": contact,
        })

        # Fee calculation
        room_type = room_type_map[room_no]
        hostel_fee = room_type_fee_map[room_type]
        mess_fee = STANDARD_MESS_FEE

        # Distribution of payment statuses:
        # 1-40: Fully Paid
        # 41-70: Partially Paid
        # 71-85: Pending (Unpaid, future due date)
        # 86-100: Overdue (Pending/Partial, past due date)
        payment_days_ago = rng.randint(5, 60)
        payment_date = (today - timedelta(days=payment_days_ago)).strftime("%Y-%m-%d")

        if i <= 40:
            # Fully Paid
            hostel_paid = hostel_fee
            mess_paid = mess_fee
            due_date = future_due_date
        elif i <= 70:
            # Partially Paid
            h_ratio = rng.choice([0.3, 0.5, 0.7])
            m_ratio = rng.choice([0.4, 0.5, 0.6])
            hostel_paid = round(hostel_fee * h_ratio, 2)
            mess_paid = round(mess_fee * m_ratio, 2)
            due_date = future_due_date
        elif i <= 85:
            # Pending (Zero or tiny payment, future due date)
            hostel_paid = 0.0
            mess_paid = 0.0
            due_date = future_due_date
            payment_date = ""
        else:
            # Overdue (Due date has passed, partial or zero payment)
            hostel_paid = round(hostel_fee * rng.choice([0.0, 0.2, 0.4]), 2)
            mess_paid = round(mess_fee * rng.choice([0.0, 0.3]), 2)
            due_date = past_due_date

        fees.append({
            "Student_ID": student_id,
            "Hostel_Fee": hostel_fee,
            "Hostel_Paid": hostel_paid,
            "Mess_Fee": mess_fee,
            "Mess_Paid": mess_paid,
            "Payment_Date": payment_date,
            "Due_Date": due_date,
        })

    # Update room occupancy numbers
    room_occupancy_counts: Dict[str, int] = {}
    for slot in allocated_slots:
        room_occupancy_counts[slot] = room_occupancy_counts.get(slot, 0) + 1

    for r in rooms:
        occ = room_occupancy_counts.get(r["Room_No"], 0)
        r["Occupied"] = occ
        r["Vacancy"] = r["Capacity"] - occ

    return students, rooms, fees


def initialize_datasets(data_mgr: DataManager, count: int = 100, force: bool = False) -> bool:
    """
    Initialize datasets if they don't already exist or if force=True.
    Returns True if initialized, False if existing datasets were retained.
    """
    students_exist = data_mgr.students_file.exists() and data_mgr.students_file.stat().st_size > 0
    rooms_exist = data_mgr.rooms_file.exists() and data_mgr.rooms_file.stat().st_size > 0
    fees_exist = data_mgr.fees_file.exists() and data_mgr.fees_file.stat().st_size > 0

    if not force and students_exist and rooms_exist and fees_exist:
        return False

    students, rooms, fees = generate_sample_dataset(count=count)
    data_mgr.save_students_list(students)
    data_mgr.save_rooms_list(rooms)
    data_mgr.save_fees_list(fees)
    return True


def verify_dataset_integrity(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Perform deep validation of datasets:
      - Valid student IDs
      - Foreign key matching between students and fees
      - Room capacity limits not exceeded
      - Room occupied count exactly equals student room assignments
      - Non-negative fee amounts and paid <= fee
    """
    students_df = data_mgr.load_students_df()
    rooms_df = data_mgr.load_rooms_df()
    fees_df = data_mgr.load_fees_df()

    issues: List[str] = []

    # 1. Unique Student_IDs
    student_ids = students_df["Student_ID"].tolist()
    if len(student_ids) != len(set(student_ids)):
        issues.append("Duplicate Student_IDs found in students.csv")

    # 2. Foreign Key Integrity (Fees -> Students)
    fee_student_ids = set(fees_df["Student_ID"].tolist())
    student_id_set = set(student_ids)
    orphan_fees = fee_student_ids - student_id_set
    if orphan_fees:
        issues.append(f"Orphan Student_IDs in fees.csv: {orphan_fees}")

    # 3. Room assignment and capacity check
    room_map = {str(row["Room_No"]): row for _, row in rooms_df.iterrows()}
    active_assignments = students_df[students_df["Room_No"].str.strip() != ""]
    occupant_counts = active_assignments["Room_No"].value_counts().to_dict()

    for room_no, count in occupant_counts.items():
        if room_no not in room_map:
            issues.append(f"Student allocated to non-existent room: {room_no}")
        else:
            capacity = int(room_map[room_no]["Capacity"])
            if count > capacity:
                issues.append(f"Room {room_no} over-allocated: {count} students > capacity {capacity}")

    for _, room_row in rooms_df.iterrows():
        room_no = str(room_row["Room_No"])
        actual_occ = occupant_counts.get(room_no, 0)
        recorded_occ = int(room_row["Occupied"])
        recorded_vac = int(room_row["Vacancy"])
        capacity = int(room_row["Capacity"])

        if actual_occ != recorded_occ:
            issues.append(f"Room {room_no} recorded occupied ({recorded_occ}) != actual students ({actual_occ})")
        if recorded_vac != (capacity - recorded_occ):
            issues.append(f"Room {room_no} vacancy mismatch: recorded {recorded_vac} != capacity {capacity} - occ {recorded_occ}")

    # 4. Fee non-negativity
    if (fees_df["Hostel_Fee"] < 0).any() or (fees_df["Hostel_Paid"] < 0).any():
        issues.append("Negative hostel fee or paid amount detected")
    if (fees_df["Mess_Fee"] < 0).any() or (fees_df["Mess_Paid"] < 0).any():
        issues.append("Negative mess fee or paid amount detected")

    is_valid = len(issues) == 0
    return {
        "is_valid": is_valid,
        "student_count": len(students_df),
        "room_count": len(rooms_df),
        "fee_count": len(fees_df),
        "issues": issues,
    }


if __name__ == "__main__":
    mgr = DataManager()
    initialize_datasets(mgr, count=100, force=True)
    report = verify_dataset_integrity(mgr)
    print("Dataset initialization & integrity check:")
    print(f"Valid: {report['is_valid']}")
    print(f"Students: {report['student_count']}, Rooms: {report['room_count']}, Fees: {report['fee_count']}")
    if report["issues"]:
        print("Issues found:", report["issues"])
    else:
        print("All integrity checks passed successfully!")
