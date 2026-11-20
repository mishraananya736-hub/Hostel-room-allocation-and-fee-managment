"""
Integration tests for Hostel Management System.
Executes the 6 mandatory end-to-end integration workflows specified in Section 15.
Uses isolated temporary directories to ensure test repeatability and safety.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from data_manager import DataManager
import student_module
import room_module
import fee_module
import analysis_module


class TestIntegrationWorkflows(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_integration_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Seed basic room configuration
        rooms = [
            {"Room_No": "101", "Floor": 1, "Room_Type": "Double", "Capacity": 2, "Occupied": 0, "Vacancy": 2},
            {"Room_No": "102", "Floor": 1, "Room_Type": "Single", "Capacity": 1, "Occupied": 0, "Vacancy": 1},
        ]
        self.mgr.save_rooms_list(rooms)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_workflow_1_register_allocate_pay_report(self):
        """
        Workflow 1:
        Register new student -> Allocate room -> Verify room occupancy ->
        Record hostel payment -> Record mess payment -> Generate summary report.
        """
        # Step 1: Register new student
        student = student_module.add_student(
            student_id="INT1001",
            name="Rohit Sharma",
            gender="Male",
            course="B.Tech CSE",
            year=1,
            contact="9876543210",
            data_mgr=self.mgr,
        )
        self.assertEqual(student["Student_ID"], "INT1001")

        # Step 2: Allocate room 101
        res_alloc = room_module.allocate_room("INT1001", "101", self.mgr)
        self.assertEqual(res_alloc["status"], "Allocated")

        # Step 3: Verify room occupancy
        rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms if r["Room_No"] == "101")
        self.assertEqual(r101["Occupied"], 1)
        self.assertEqual(r101["Vacancy"], 1)

        # Step 4: Record hostel payment
        res_hpay = fee_module.record_hostel_payment("INT1001", 20000.0, self.mgr)
        self.assertEqual(res_hpay["Amount_Paid"], 20000.0)

        # Step 5: Record mess payment
        res_mpay = fee_module.record_mess_payment("INT1001", 15000.0, self.mgr)
        self.assertEqual(res_mpay["Amount_Paid"], 15000.0)

        # Step 6: Generate summary report
        report = analysis_module.generate_summary_report(self.mgr)
        raw = report["_raw"]
        self.assertEqual(raw["total_registered_students"], 1)
        self.assertEqual(raw["total_occupied_beds"], 1)
        self.assertEqual(raw["total_hostel_collected"], 20000.0)
        self.assertEqual(raw["total_mess_collected"], 15000.0)

    def test_workflow_2_search_update_verify_csv(self):
        """
        Workflow 2:
        Search student -> Update details -> Verify updated CSV record.
        """
        # Setup student
        student_module.add_student("INT2001", "Kavya Iyer", "Female", "MCA", 1, "9876543210", self.mgr)

        # Search
        found = student_module.search_student("INT2001", self.mgr)
        self.assertIsNotNone(found)
        self.assertEqual(found["Name"], "Kavya Iyer")

        # Update
        updated = student_module.update_student(
            "INT2001",
            {"Name": "Kavya S. Iyer", "Year": 2, "Contact": "8765432109"},
            self.mgr,
        )
        self.assertEqual(updated["Name"], "Kavya S. Iyer")

        # Verify from CSV file directly
        loaded_df = self.mgr.load_students_df()
        st_row = loaded_df[loaded_df["Student_ID"] == "INT2001"].iloc[0]
        self.assertEqual(st_row["Name"], "Kavya S. Iyer")
        self.assertEqual(int(st_row["Year"]), 2)
        self.assertEqual(st_row["Contact"], "8765432109")

    def test_workflow_3_reassign_room_verify_both_rooms(self):
        """
        Workflow 3:
        Reassign student to another room -> Verify old room vacancy -> Verify new room occupancy.
        """
        # Register and allocate to room 101
        student_module.add_student("INT3001", "Siddharth", "Male", "ECE", 2, "9876543210", self.mgr, room_no="101")
        rooms_pre = self.mgr.load_rooms_list()
        self.assertEqual(next(r for r in rooms_pre if r["Room_No"] == "101")["Occupied"], 1)
        self.assertEqual(next(r for r in rooms_pre if r["Room_No"] == "102")["Occupied"], 0)

        # Reassign to room 102
        res = room_module.reassign_room("INT3001", "102", self.mgr)
        self.assertEqual(res["status"], "Reassigned")

        # Verify rooms
        rooms_post = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms_post if r["Room_No"] == "101")
        r102 = next(r for r in rooms_post if r["Room_No"] == "102")
        self.assertEqual(r101["Occupied"], 0)
        self.assertEqual(r101["Vacancy"], 2)
        self.assertEqual(r102["Occupied"], 1)
        self.assertEqual(r102["Vacancy"], 0)

        # Verify student record in CSV
        st = student_module.search_student("INT3001", self.mgr)
        self.assertEqual(st["Room_No"], "102")

    def test_workflow_4_delete_student_cascade(self):
        """
        Workflow 4:
        Delete student -> Verify student record removal -> Verify room vacancy update ->
        Verify related fee records are handled according to defined policy.
        """
        student_module.add_student("INT4001", "Priya Nair", "Female", "ME", 3, "9876543210", self.mgr, room_no="102")

        # Verify student exists in all 3 files
        self.assertIsNotNone(student_module.search_student("INT4001", self.mgr))
        r102 = next(r for r in self.mgr.load_rooms_list() if r["Room_No"] == "102")
        self.assertEqual(r102["Occupied"], 1)
        fees = self.mgr.load_fees_list()
        self.assertTrue(any(f["Student_ID"] == "INT4001" for f in fees))

        # Delete student
        deleted = student_module.delete_student("INT4001", self.mgr, cascade=True)
        self.assertEqual(deleted["Student_ID"], "INT4001")

        # 1. Student removed
        self.assertIsNone(student_module.search_student("INT4001", self.mgr))

        # 2. Room vacancy restored
        r102_after = next(r for r in self.mgr.load_rooms_list() if r["Room_No"] == "102")
        self.assertEqual(r102_after["Occupied"], 0)
        self.assertEqual(r102_after["Vacancy"], 1)

        # 3. Fees removed
        fees_after = self.mgr.load_fees_list()
        self.assertFalse(any(f["Student_ID"] == "INT4001" for f in fees_after))

    def test_workflow_5_restart_persistence(self):
        """
        Workflow 5:
        Restart application -> Verify all previously saved data remains intact.
        """
        # Session 1: Create and allocate
        student_module.add_student("INT5001", "Aditya Joshi", "Male", "Civil", 1, "9876543210", self.mgr, room_no="101")
        fee_module.record_hostel_payment("INT5001", 10000.0, self.mgr)

        # Session 2: Instantiate new DataManager pointing to same directory (simulates app restart)
        new_mgr_instance = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        new_mgr_instance.sync_room_occupancies()

        st = student_module.search_student("INT5001", new_mgr_instance)
        self.assertIsNotNone(st)
        self.assertEqual(st["Name"], "Aditya Joshi")
        self.assertEqual(st["Room_No"], "101")

        stmt = fee_module.calculate_pending_fees("INT5001", new_mgr_instance)
        self.assertEqual(stmt["Hostel_Paid"], 10000.0)

        r101 = next(r for r in new_mgr_instance.load_rooms_list() if r["Room_No"] == "101")
        self.assertEqual(r101["Occupied"], 1)

    def test_workflow_6_error_handling_and_data_safety(self):
        """
        Workflow 6:
        Attempt invalid operations -> Verify application displays appropriate errors without crashing or corrupting data.
        """
        student_module.add_student("INT6001", "Manish Rao", "Male", "IT", 2, "9876543210", self.mgr, room_no="102")
        # 102 is Single room and now FULL (Capacity 1, Occupied 1)

        # Attempt 1: Over-allocating full room
        with self.assertRaises(ValueError):
            student_module.add_student("INT6002", "Deepak", "Male", "IT", 2, "9876543211", self.mgr, room_no="102")

        # Attempt 2: Negative fee payment
        with self.assertRaises(ValueError):
            fee_module.record_hostel_payment("INT6001", -5000.0, self.mgr)

        # Attempt 3: Overpaying hostel fee
        stmt = fee_module.calculate_pending_fees("INT6001", self.mgr)
        excess_amount = stmt["Hostel_Pending"] + 100000.0
        with self.assertRaises(ValueError):
            fee_module.record_hostel_payment("INT6001", excess_amount, self.mgr)

        # Attempt 4: Nonexistent student deletion
        with self.assertRaises(ValueError):
            student_module.delete_student("FAKE_ID_999", self.mgr)

        # Verify initial data remains intact and uncorrupted
        st = student_module.search_student("INT6001", self.mgr)
        self.assertIsNotNone(st)
        self.assertEqual(st["Name"], "Manish Rao")
        r102 = next(r for r in self.mgr.load_rooms_list() if r["Room_No"] == "102")
        self.assertEqual(r102["Occupied"], 1)


if __name__ == "__main__":
    unittest.main()
