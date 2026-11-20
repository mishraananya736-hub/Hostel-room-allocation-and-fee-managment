"""
Unit tests for fee_module.
Tests payments, balance calculations, over-payment prevention, negative payment checks,
and status determination (PAID, PARTIAL, PENDING, OVERDUE).
"""

import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from data_manager import DataManager
import student_module
import fee_module


class TestFeeModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_fees_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Register student (which auto-initializes fees)
        student_module.add_student("STU801", "Gaurav", "Male", "CSE", 1, "9876543210", self.mgr)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_record_partial_and_full_hostel_payment(self):
        """Verify recording partial and full hostel fee payments."""
        fee_module.update_hostel_fee("STU801", 40000.0, self.mgr)

        # 1. Partial payment
        res1 = fee_module.record_hostel_payment("STU801", 15000.0, self.mgr, payment_date="2026-11-01")
        self.assertEqual(res1["Total_Hostel_Paid"], 15000.0)
        self.assertEqual(res1["Remaining_Hostel_Balance"], 25000.0)

        stmt1 = fee_module.calculate_pending_fees("STU801", self.mgr)
        self.assertEqual(stmt1["Hostel_Status"], "PARTIAL")

        # 2. Complete payment
        res2 = fee_module.record_hostel_payment("STU801", 25000.0, self.mgr, payment_date="2026-11-05")
        self.assertEqual(res2["Total_Hostel_Paid"], 40000.0)
        self.assertEqual(res2["Remaining_Hostel_Balance"], 0.0)

        stmt2 = fee_module.calculate_pending_fees("STU801", self.mgr)
        self.assertEqual(stmt2["Hostel_Status"], "PAID")

    def test_record_mess_payment(self):
        """Verify mess fee payments."""
        fee_module.update_mess_fee("STU801", 25000.0, self.mgr)
        res = fee_module.record_mess_payment("STU801", 10000.0, self.mgr)
        self.assertEqual(res["Total_Mess_Paid"], 10000.0)
        self.assertEqual(res["Remaining_Mess_Balance"], 15000.0)

    def test_prevent_negative_payments(self):
        """Verify negative payment attempts are rejected."""
        with self.assertRaises(ValueError):
            fee_module.record_hostel_payment("STU801", -500.0, self.mgr)
        with self.assertRaises(ValueError):
            fee_module.record_mess_payment("STU801", 0.0, self.mgr)

    def test_prevent_payment_exceeding_balance(self):
        """Verify payment exceeding pending balance is rejected."""
        fee_module.update_hostel_fee("STU801", 30000.0, self.mgr)
        with self.assertRaises(ValueError) as ctx:
            fee_module.record_hostel_payment("STU801", 35000.0, self.mgr)
        self.assertIn("exceeds pending", str(ctx.exception))

    def test_overdue_status_detection(self):
        """Verify past due date leads to OVERDUE status when balance is unpaid."""
        # Set due date to 10 days ago
        past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        fees = self.mgr.load_fees_list()
        fees[0]["Due_Date"] = past_date
        self.mgr.save_fees_list(fees)

        stmt = fee_module.calculate_pending_fees("STU801", self.mgr)
        self.assertEqual(stmt["Hostel_Status"], "OVERDUE")
        self.assertEqual(stmt["Mess_Status"], "OVERDUE")
        self.assertEqual(stmt["Overall_Status"], "OVERDUE")


if __name__ == "__main__":
    unittest.main()
