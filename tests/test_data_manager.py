"""
Unit tests for data_manager module.
Verifies file operations, atomic writes, transactions, and synchronization in isolation.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
import pandas as pd

from data_manager import DataManager


class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_data_mgr_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_files_return_empty_dfs(self):
        """Verify that loading non-existent CSVs returns empty DataFrames with correct schemas."""
        st_df = self.mgr.load_students_df()
        rm_df = self.mgr.load_rooms_df()
        fe_df = self.mgr.load_fees_df()

        self.assertTrue(st_df.empty)
        self.assertIn("Student_ID", st_df.columns)
        self.assertTrue(rm_df.empty)
        self.assertIn("Room_No", rm_df.columns)
        self.assertTrue(fe_df.empty)
        self.assertIn("Hostel_Fee", fe_df.columns)

    def test_save_and_load_students(self):
        """Verify persisting and reading student records."""
        sample_students = [
            {
                "Student_ID": "STU9901",
                "Name": "Test Student",
                "Gender": "Male",
                "Course": "B.Tech CSE",
                "Year": 2,
                "Room_No": "101",
                "Contact": "9876543210",
            }
        ]
        self.mgr.save_students_list(sample_students)
        loaded = self.mgr.load_students_list()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["Student_ID"], "STU9901")
        self.assertEqual(loaded[0]["Name"], "Test Student")

    def test_save_and_load_rooms(self):
        """Verify persisting and reading room records."""
        sample_rooms = [
            {"Room_No": "101", "Floor": 1, "Room_Type": "Single", "Capacity": 1, "Occupied": 0, "Vacancy": 1}
        ]
        self.mgr.save_rooms_list(sample_rooms)
        loaded = self.mgr.load_rooms_list()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["Room_No"], "101")
        self.assertEqual(loaded[0]["Capacity"], 1)

    def test_save_and_load_fees(self):
        """Verify persisting and reading fee records."""
        sample_fees = [
            {
                "Student_ID": "STU9901",
                "Hostel_Fee": 40000.0,
                "Hostel_Paid": 20000.0,
                "Mess_Fee": 25000.0,
                "Mess_Paid": 25000.0,
                "Payment_Date": "2026-11-01",
                "Due_Date": "2026-12-01",
            }
        ]
        self.mgr.save_fees_list(sample_fees)
        loaded = self.mgr.load_fees_list()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["Student_ID"], "STU9901")
        self.assertEqual(float(loaded[0]["Hostel_Fee"]), 40000.0)

    def test_transaction_rollback_on_failure(self):
        """Verify transactional rollback prevents corrupted data on unexpected errors."""
        initial_students = [
            {"Student_ID": "STU1", "Name": "Alice", "Gender": "Female", "Course": "CSE", "Year": 1, "Room_No": "", "Contact": "9876543210"}
        ]
        self.mgr.save_students_list(initial_students)

        def faulty_tx(mgr):
            mgr.save_students_list([])
            raise RuntimeError("Database connection interrupted")

        with self.assertRaises(RuntimeError):
            self.mgr.execute_transaction(faulty_tx)

        # Confirm rollback
        restored = self.mgr.load_students_list()
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0]["Student_ID"], "STU1")

    def test_sync_room_occupancies(self):
        """Verify that room occupancy correctly mirrors student allocations."""
        rooms = [
            {"Room_No": "101", "Floor": 1, "Room_Type": "Double", "Capacity": 2, "Occupied": 0, "Vacancy": 2},
            {"Room_No": "102", "Floor": 1, "Room_Type": "Single", "Capacity": 1, "Occupied": 0, "Vacancy": 1},
        ]
        students = [
            {"Student_ID": "STU1", "Name": "A", "Gender": "M", "Course": "CSE", "Year": 1, "Room_No": "101", "Contact": "9876543210"},
            {"Student_ID": "STU2", "Name": "B", "Gender": "M", "Course": "CSE", "Year": 1, "Room_No": "101", "Contact": "9876543211"},
        ]
        self.mgr.save_rooms_list(rooms)
        self.mgr.save_students_list(students)

        self.mgr.sync_room_occupancies()
        updated_rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in updated_rooms if r["Room_No"] == "101")
        r102 = next(r for r in updated_rooms if r["Room_No"] == "102")

        self.assertEqual(r101["Occupied"], 2)
        self.assertEqual(r101["Vacancy"], 0)
        self.assertEqual(r102["Occupied"], 0)
        self.assertEqual(r102["Vacancy"], 1)


if __name__ == "__main__":
    unittest.main()
