"""
Unit tests for room_module.
Tests room allocation, over-allocation prevention, vacating, and reassignment.
"""

import shutil
import tempfile
import unittest
from data_manager import DataManager
import student_module
import room_module


class TestRoomModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_rooms_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Seed test rooms
        rooms = [
            {"Room_No": "101", "Floor": 1, "Room_Type": "Single", "Capacity": 1, "Occupied": 0, "Vacancy": 1},
            {"Room_No": "102", "Floor": 1, "Room_Type": "Double", "Capacity": 2, "Occupied": 0, "Vacancy": 2},
        ]
        self.mgr.save_rooms_list(rooms)
        # Seed student
        student_module.add_student("STU101", "Rahul", "Male", "CSE", 1, "9876543210", self.mgr)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_allocate_room_success(self):
        """Verify successful room allocation and vacancy reduction."""
        res = room_module.allocate_room("STU101", "101", self.mgr)
        self.assertEqual(res["status"], "Allocated")

        rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms if r["Room_No"] == "101")
        self.assertEqual(r101["Occupied"], 1)
        self.assertEqual(r101["Vacancy"], 0)

        # Student's record reflects allocated room
        st = student_module.search_student("STU101", self.mgr)
        self.assertEqual(st["Room_No"], "101")

    def test_allocate_over_capacity_prevented(self):
        """Verify allocating to a full room is rejected."""
        room_module.allocate_room("STU101", "101", self.mgr)

        # Add second student
        student_module.add_student("STU102", "Amit", "Male", "CSE", 1, "9876543211", self.mgr)
        with self.assertRaises(ValueError) as ctx:
            room_module.allocate_room("STU102", "101", self.mgr)
        self.assertIn("already full", str(ctx.exception))

    def test_allocate_nonexistent_room(self):
        """Verify allocating a room that does not exist raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            room_module.allocate_room("STU101", "999", self.mgr)
        self.assertIn("does not exist", str(ctx.exception))

    def test_allocate_already_allocated_student(self):
        """Verify cannot allocate a student who already has a room without reassigning."""
        room_module.allocate_room("STU101", "101", self.mgr)
        with self.assertRaises(ValueError) as ctx:
            room_module.allocate_room("STU101", "102", self.mgr)
        self.assertIn("already allocated", str(ctx.exception))

    def test_vacate_room(self):
        """Verify vacating room frees bed and clears student's room assignment."""
        room_module.allocate_room("STU101", "101", self.mgr)
        res = room_module.vacate_room("STU101", self.mgr)
        self.assertEqual(res["status"], "Vacated")

        st = student_module.search_student("STU101", self.mgr)
        self.assertEqual(st["Room_No"], "")

        rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms if r["Room_No"] == "101")
        self.assertEqual(r101["Occupied"], 0)
        self.assertEqual(r101["Vacancy"], 1)

    def test_reassign_room(self):
        """Verify room reassignment safely updates both source and destination rooms."""
        room_module.allocate_room("STU101", "101", self.mgr)
        res = room_module.reassign_room("STU101", "102", self.mgr)
        self.assertEqual(res["status"], "Reassigned")
        self.assertEqual(res["old_room"], "101")
        self.assertEqual(res["new_room"], "102")

        rooms = self.mgr.load_rooms_list()
        r101 = next(r for r in rooms if r["Room_No"] == "101")
        r102 = next(r for r in rooms if r["Room_No"] == "102")

        # 101 now vacant, 102 now has 1 occupant
        self.assertEqual(r101["Occupied"], 0)
        self.assertEqual(r101["Vacancy"], 1)
        self.assertEqual(r102["Occupied"], 1)
        self.assertEqual(r102["Vacancy"], 1)


if __name__ == "__main__":
    unittest.main()
