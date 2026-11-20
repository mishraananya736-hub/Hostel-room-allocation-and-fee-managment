"""
Unit tests for analysis_module.
Tests NumPy 1D/2D arrays, indexing, slicing, statistical calculations,
Pandas head/tail, groupby, filtering, missing values, and report generation.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from data_manager import DataManager
from initialization import initialize_datasets
import analysis_module


class TestAnalysisModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_analysis_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Initialize realistic dataset of 60 records for testing
        initialize_datasets(self.mgr, count=60, force=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_numpy_analysis_operations(self):
        """
        Verify NumPy requirements:
        1D arrays, 2D arrays, indexing, slicing, sum, mean, max, min, std.
        """
        res = analysis_module.run_numpy_analysis(self.mgr)
        stats = res["stats"]

        # 1D & 2D array verification
        self.assertEqual(res["fee_matrix_shape"][1], 4)
        self.assertEqual(res["fee_matrix_shape"][0], 60)
        self.assertEqual(res["room_matrix_shape"][1], 3)

        # Mathematical operations check
        self.assertGreater(stats["hostel_fee_sum"], 0)
        self.assertGreater(stats["hostel_paid_sum"], 0)
        self.assertGreater(stats["total_paid_sum"], 0)

        # Mean check
        self.assertGreater(stats["hostel_fee_mean"], 10000)

        # Max and Min
        self.assertGreaterEqual(stats["total_paid_max"], stats["total_paid_min"])

        # Standard deviation
        self.assertGreaterEqual(stats["total_paid_std"], 0)

        # Indexing & Slicing check
        self.assertIn("first_student_hostel_fee", res["indexed_values"])
        self.assertEqual(len(res["slice_sample"]), 5)  # 5 rows sliced
        self.assertEqual(len(res["slice_sample"][0]), 2)  # 2 cols sliced

    def test_pandas_head_tail_and_selected_columns(self):
        """Verify Pandas head, tail, and column selection."""
        head_df, tail_df = analysis_module.get_students_head_tail(self.mgr, n=5)
        self.assertEqual(len(head_df), 5)
        self.assertEqual(len(tail_df), 5)

        sel_df = analysis_module.get_selected_student_columns(self.mgr, ["Student_ID", "Name"])
        self.assertEqual(list(sel_df.columns), ["Student_ID", "Name"])

    def test_pandas_filtering_and_sorting(self):
        """Verify Pandas boolean indexing and sort_values."""
        pending_df = analysis_module.filter_pending_fees(self.mgr, fee_type="both")
        self.assertFalse(pending_df.empty)
        # All returned must have Total_Pending > 0
        self.assertTrue((pending_df["Total_Pending"] > 0).all())

        sorted_df = analysis_module.sort_students_by_paid_fees(self.mgr, ascending=False)
        self.assertEqual(len(sorted_df), 60)
        # Check sorting order
        paid_values = sorted_df["Total_Paid"].tolist()
        self.assertEqual(paid_values, sorted(paid_values, reverse=True))

    def test_pandas_groupby(self):
        """Verify GroupBy operations on courses and room types."""
        course_grp = analysis_module.group_students_by_course(self.mgr)
        self.assertFalse(course_grp.empty)
        self.assertEqual(course_grp["Total_Students"].sum(), 60)

        room_grp = analysis_module.group_room_occupancy_by_type(self.mgr)
        self.assertFalse(room_grp.empty)
        self.assertIn("Occupancy_Rate_%", room_grp.columns)

    def test_missing_value_handling_demo(self):
        """Verify Pandas isna and fillna demonstration."""
        demo = analysis_module.demonstrate_missing_value_handling(self.mgr)
        self.assertGreater(demo["pre_impute_missing"]["Room_No"], 0)
        self.assertEqual(demo["post_impute_missing"]["Room_No"], 0)

    def test_summary_report_15_metrics(self):
        """Verify summary report contains all 15 required metrics dynamically calculated."""
        report = analysis_module.generate_summary_report(self.mgr)
        raw = report["_raw"]

        self.assertEqual(raw["total_registered_students"], 60)
        self.assertGreater(raw["total_rooms"], 0)
        self.assertGreater(raw["total_room_capacity"], 0)
        self.assertEqual(raw["total_occupied_beds"], 60)
        self.assertEqual(raw["total_vacant_beds"], raw["total_room_capacity"] - 60)
        self.assertGreater(raw["room_occupancy_pct"], 0)
        self.assertGreater(raw["total_hostel_fees"], 0)
        self.assertGreater(raw["total_mess_fees"], 0)
        self.assertGreaterEqual(raw["fully_paid_students"], 0)
        self.assertGreater(raw["pending_hostel_students"], 0)

    def test_fee_statistics_describe(self):
        """Verify Pandas describe() method returns valid statistical metrics on fee data."""
        describe_df = analysis_module.get_fee_statistics_describe(self.mgr)
        self.assertFalse(describe_df.empty)
        stat_names = describe_df["Statistic"].tolist()
        self.assertIn("mean", stat_names)
        self.assertIn("std", stat_names)
        self.assertIn("min", stat_names)
        self.assertIn("max", stat_names)

    def test_analyze_data_master_function(self):
        """Verify analyze_data() consolidates NumPy, Pandas, GroupBy, and Summary metrics."""
        analysis = analysis_module.analyze_data(self.mgr)
        self.assertIn("summary", analysis)
        self.assertIn("numpy_stats", analysis)
        self.assertIn("pandas_describe", analysis)
        self.assertIn("course_distribution", analysis)
        self.assertIn("room_type_occupancy", analysis)
        self.assertIn("comparative", analysis)

    def test_export_report(self):
        """Verify report files export properly to reports directory."""
        files = analysis_module.export_report(self.mgr)
        self.assertGreaterEqual(len(files), 4)
        for fp in files:
            p = Path(fp)
            self.assertTrue(p.exists())
            self.assertGreater(p.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
