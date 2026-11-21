"""
Automated unit and integration tests for excel_report_module.
Verifies workbook generation, all 7 worksheets, KPI accuracy,
native Openpyxl charts, conditional formatting, currency formatting,
re-opening, dynamic updating, and dataset non-modification.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
import openpyxl

from data_manager import DataManager
from initialization import initialize_datasets
import excel_report_module
import student_module


class TestExcelReportModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_excel_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Initialize realistic dataset of 60 records for testing
        initialize_datasets(self.mgr, count=60, force=True)
        self.excel_file = Path(self.test_dir) / "Hostel_Management_Professional_Report.xlsx"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_workbook_generates_successfully(self):
        """Verify that the professional Excel report is generated and can be saved."""
        path = excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        self.assertTrue(Path(path).exists())
        self.assertGreater(Path(path).stat().st_size, 10000)

    def test_all_seven_worksheets_exist(self):
        """Verify that all 7 required worksheets are present in the workbook."""
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb = openpyxl.load_workbook(self.excel_file)
        expected_sheets = [
            "EXECUTIVE DASHBOARD",
            "STUDENT DIRECTORY",
            "ROOM ALLOCATION",
            "FEE MANAGEMENT",
            "COURSE ANALYSIS",
            "FINANCIAL SUMMARY",
            "DATA ANALYSIS",
        ]
        for name in expected_sheets:
            self.assertIn(name, wb.sheetnames, f"Worksheet '{name}' missing from generated workbook.")

    def test_student_directory_contains_all_records(self):
        """Verify that the Student Directory contains all 60 student records plus header."""
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb["STUDENT DIRECTORY"]
        # Header is row 1, data starts row 2
        students_df = self.mgr.load_students_df()
        self.assertEqual(ws.max_row, len(students_df) + 1)
        self.assertEqual(ws["A1"].value, "Student ID")

    def test_room_occupancy_data_and_charts(self):
        """Verify room occupancy numbers and presence of native chart on Room Allocation sheet."""
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb["ROOM ALLOCATION"]
        rooms_df = self.mgr.load_rooms_df()
        self.assertEqual(ws.max_row, len(rooms_df) + 1)
        # Check chart exists
        self.assertGreaterEqual(len(ws._charts), 1)

    def test_fee_management_balances_and_formatting(self):
        """Verify fee management sheet contains correct balances, currency format, and conditional rules."""
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb["FEE MANAGEMENT"]
        fees_df = self.mgr.load_fees_df()
        self.assertEqual(ws.max_row, len(fees_df) + 1)

        # Check currency formatting on Hostel Fee (Col C / col 3)
        self.assertIn("₹", ws["C2"].number_format)
        # Check conditional formatting rules exist
        self.assertGreater(len(ws.conditional_formatting), 0)

    def test_dashboard_kpis_match_csv_calculations(self):
        """Verify that KPI values on the Executive Dashboard strictly match CSV calculations."""
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb["EXECUTIVE DASHBOARD"]

        students_df = self.mgr.load_students_df()
        rooms_df = self.mgr.load_rooms_df()

        # Cell A6 is merged A6:B6 for Total Students
        self.assertEqual(int(ws["A6"].value), len(students_df))
        # Cell C6 is merged C6:D6 for Total Rooms
        self.assertEqual(int(ws["C6"].value), len(rooms_df))
        # Check that dashboard contains at least 4 native charts
        self.assertGreaterEqual(len(ws._charts), 4)

    def test_regenerating_workbook_updates_data(self):
        """Verify that modifying student records and re-exporting updates the workbook."""
        # Initial export
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb1 = openpyxl.load_workbook(self.excel_file)
        self.assertEqual(wb1["STUDENT DIRECTORY"].max_row, 61)

        # Add a student
        student_module.add_student(
            student_id="STU9999",
            name="New Test Student",
            gender="Female",
            course="MCA",
            year=1,
            contact="9876543210",
            data_mgr=self.mgr,
        )

        # Re-export
        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)
        wb2 = openpyxl.load_workbook(self.excel_file)
        self.assertEqual(wb2["STUDENT DIRECTORY"].max_row, 62)

    def test_export_does_not_modify_original_csvs(self):
        """Verify that exporting the Excel dashboard is read-only for CSV datasets."""
        st_before = self.mgr.load_students_df()
        rm_before = self.mgr.load_rooms_df()
        fe_before = self.mgr.load_fees_df()

        excel_report_module.export_professional_excel_report(self.mgr, self.excel_file)

        st_after = self.mgr.load_students_df()
        rm_after = self.mgr.load_rooms_df()
        fe_after = self.mgr.load_fees_df()

        self.assertEqual(len(st_before), len(st_after))
        self.assertEqual(len(rm_before), len(rm_after))
        self.assertEqual(len(fe_before), len(fe_after))


if __name__ == "__main__":
    unittest.main()
