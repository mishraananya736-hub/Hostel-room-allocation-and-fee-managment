"""
Unit tests for student_module.
Tests addition, duplicate detection, field validations, searching, updating, and deletion.
"""

import shutil
import tempfile
import unittest
from data_manager import DataManager
import student_module


class TestStudentModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_students_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Seed test rooms
        rooms = [
            {"Room_No": "101", "Floor": 1, "Room_Type": "Double", "Capacity": 2, "Occupied": 0, "Vacancy": 2},
            {"Room_No": "102", "Floor": 1, "Room_Type": "Single", "Capacity": 1, "Occupied": 1, "Vacancy": 0},
        ]
        self.mgr.save_rooms_list(rooms)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_student_success(self):
        """Verify successful student addition and automatic fee record creation."""
        res = student_module.add_student(
            student_id="STU2001",
            name="Aarav Sharma",
            gender="Male",
            course="B.Tech CSE",
            year=1,
            contact="9876543210",
            data_mgr=self.mgr,
            room_no="101",
        )
        self.assertEqual(res["Student_ID"], "STU2001")
        self.assertEqual(res["Name"], "Aarav Sharma")
        self.assertEqual(res["Room_No"], "101")

        # Check fees were generated
        fees = self.mgr.load_fees_list()
        self.assertEqual(len(fees), 1)
        self.assertEqual(fees[0]["Student_ID"], "STU2001")

    def test_add_student_duplicate_id_prevented(self):
        """Verify duplicate student IDs are rejected."""
        student_module.add_student("STU2001", "Aarav", "Male", "CSE", 1, "9876543210", self.mgr)
        with self.assertRaises(ValueError) as ctx:
            student_module.add_student("STU2001", "Another Name", "Male", "CSE", 2, "9876543211", self.mgr)
        self.assertIn("already exists", str(ctx.exception))

    def test_add_student_invalid_contact(self):
        """Verify non-10 digit contact or invalid start digit is rejected."""
        with self.assertRaises(ValueError):
            student_module.add_student("STU2002", "Bob", "Male", "CSE", 1, "12345", self.mgr)
        with self.assertRaises(ValueError):
            student_module.add_student("STU2003", "Bob", "Male", "CSE", 1, "4876543210", self.mgr)

    def test_add_student_invalid_year_and_gender(self):
        """Verify invalid academic year and invalid gender are rejected."""
        with self.assertRaises(ValueError):
            student_module.add_student("STU2004", "Bob", "Male", "CSE", 8, "9876543210", self.mgr)
        with self.assertRaises(ValueError):
            student_module.add_student("STU2005", "Bob", "Robot", "CSE", 1, "9876543210", self.mgr)

    def test_search_student(self):
        """Verify search by ID and name."""
        student_module.add_student("STU3001", "Pooja Verma", "Female", "MCA", 1, "9876543210", self.mgr)

        # Search by ID
        found_id = student_module.search_student("STU3001", self.mgr)
        self.assertIsNotNone(found_id)
        self.assertEqual(found_id["Name"], "Pooja Verma")

        # Search by Name
        found_name = student_module.search_student("Pooja", self.mgr)
        self.assertIsNotNone(found_name)
        self.assertEqual(found_name["Student_ID"], "STU3001")

        # Search non-existent
        self.assertIsNone(student_module.search_student("NONEXISTENT", self.mgr))

    def test_update_student(self):
        """Verify updating mutable student fields."""
        student_module.add_student("STU4001", "Kunal Singh", "Male", "ECE", 1, "9876543210", self.mgr)

        updated = student_module.update_student(
            "STU4001",
            {"Name": "Kunal Singh Rajput", "Year": 2, "Contact": "8765432109"},
            self.mgr,
        )
        self.assertEqual(updated["Name"], "Kunal Singh Rajput")
        self.assertEqual(updated["Year"], 2)
        self.assertEqual(updated["Contact"], "8765432109")

    def test_delete_student(self):
        """Verify student deletion cascades to vacating room and fee record."""
        student_module.add_student("STU5001", "Vikram Patel", "Male", "ME", 2, "9876543210", self.mgr, room_no="101")
        # Confirm student is in 101
        rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms if r["Room_No"] == "101")
        self.assertEqual(r101["Occupied"], 1)

        # Delete student
        deleted = student_module.delete_student("STU5001", self.mgr, cascade=True)
        self.assertEqual(deleted["Student_ID"], "STU5001")

        # Check students list
        self.assertIsNone(student_module.search_student("STU5001", self.mgr))

        # Check room vacancy increased
        rooms = self.mgr.load_rooms_list()
        r101_after = next(r for r in rooms if r["Room_No"] == "101")
        self.assertEqual(r101_after["Occupied"], 0)
        self.assertEqual(r101_after["Vacancy"], 2)

        # Check fees removed
        fees = self.mgr.load_fees_list()
        self.assertEqual(len(fees), 0)


if __name__ == "__main__":
    unittest.main()
