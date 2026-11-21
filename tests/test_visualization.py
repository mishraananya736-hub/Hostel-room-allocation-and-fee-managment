"""
Automated unit and integration tests for visualization_module.
Verifies all 5 graphs, file locations, handling of empty datasets,
zero values, repeated generations, and isolation with temporary test fixtures.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from data_manager import DataManager
from initialization import initialize_datasets
import visualization_module


class TestVisualizationModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="hostel_test_viz_")
        self.mgr = DataManager(data_dir=self.test_dir, reports_dir=self.test_dir)
        # Initialize realistic dataset with 50 records
        initialize_datasets(self.mgr, count=50, force=True)
        self.graphs_dir = Path(self.test_dir) / "graphs"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_all_five_graphs_generate_successfully(self):
        """Verify that all 5 Matplotlib graphs generate and exist on disk."""
        results = visualization_module.generate_all_graphs(self.mgr, self.graphs_dir)
        self.assertEqual(len(results), 5)
        for key, file_path in results.items():
            path_obj = Path(file_path)
            self.assertTrue(path_obj.exists(), f"Graph {key} at {file_path} was not created.")
            self.assertGreater(path_obj.stat().st_size, 5000, f"Graph {key} file is suspiciously small.")

    def test_each_graph_saved_in_correct_location(self):
        """Verify the specific filenames for all 5 graphs."""
        p1 = visualization_module.plot_room_occupancy(self.mgr, self.graphs_dir / "room_occupancy.png")
        p2 = visualization_module.plot_fee_collection(self.mgr, self.graphs_dir / "fee_collection.png")
        p3 = visualization_module.plot_hostel_mess_comparison(self.mgr, self.graphs_dir / "hostel_mess_comparison.png")
        p4 = visualization_module.plot_course_distribution(self.mgr, self.graphs_dir / "course_distribution.png")
        p5 = visualization_module.plot_payment_distribution(self.mgr, self.graphs_dir / "payment_distribution.png")

        self.assertEqual(Path(p1).name, "room_occupancy.png")
        self.assertEqual(Path(p2).name, "fee_collection.png")
        self.assertEqual(Path(p3).name, "hostel_mess_comparison.png")
        self.assertEqual(Path(p4).name, "course_distribution.png")
        self.assertEqual(Path(p5).name, "payment_distribution.png")

        for p in [p1, p2, p3, p4, p5]:
            self.assertTrue(Path(p).is_file())

    def test_empty_datasets_handled_gracefully(self):
        """Verify that empty datasets do not cause unhandled exceptions or crashes."""
        empty_dir = tempfile.mkdtemp(prefix="hostel_empty_viz_")
        try:
            empty_mgr = DataManager(data_dir=empty_dir, reports_dir=empty_dir)
            empty_graphs_dir = Path(empty_dir) / "graphs"

            # All functions must return valid image paths without raising exceptions
            res = visualization_module.generate_all_graphs(empty_mgr, empty_graphs_dir)
            self.assertEqual(len(res), 5)
            for k, p in res.items():
                self.assertTrue(Path(p).exists())
                self.assertGreater(Path(p).stat().st_size, 0)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_zero_value_categories_handled(self):
        """Verify handling of zero payments or zero vacancies."""
        fees = self.mgr.load_fees_list()
        for f in fees:
            f["Hostel_Paid"] = 0.0
            f["Mess_Paid"] = 0.0
        self.mgr.save_fees_list(fees)

        p = visualization_module.plot_fee_collection(self.mgr, self.graphs_dir / "zero_fee.png")
        self.assertTrue(Path(p).exists())

        p_hist = visualization_module.plot_payment_distribution(self.mgr, self.graphs_dir / "zero_hist.png")
        self.assertTrue(Path(p_hist).exists())

    def test_repeated_graph_generation(self):
        """Verify that overwriting and regenerating graphs works cleanly without locking."""
        res1 = visualization_module.generate_all_graphs(self.mgr, self.graphs_dir)
        mtime1 = {k: Path(p).stat().st_mtime_ns for k, p in res1.items()}

        # Regenerate
        res2 = visualization_module.generate_all_graphs(self.mgr, self.graphs_dir)
        for k, p in res2.items():
            self.assertTrue(Path(p).exists())

    def test_open_graph_image_safety(self):
        """Verify that open_graph_image does not crash if given non-existent or existing file."""
        self.assertFalse(visualization_module.open_graph_image("non_existent_file.png"))
        valid_img = self.graphs_dir / "test_img.png"
        visualization_module.plot_course_distribution(self.mgr, valid_img)
        # Should return boolean without crashing
        result = visualization_module.open_graph_image(valid_img)
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
