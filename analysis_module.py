"""
Analysis Module for Hostel Management System.
Implements NumPy numerical analysis, Pandas dataset processing, GroupBy,
statistical reporting, summary report generation, and report exporting.
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from data_manager import DataManager

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def format_table(data: List[Dict[str, Any]] | pd.DataFrame, headers: str = "keys", tablefmt: str = "grid") -> str:
    """Format data as an attractive terminal table using tabulate or fallback."""
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient="records")
    else:
        records = data

    if not records:
        return "(No records to display)"

    if HAS_TABULATE:
        return tabulate(records, headers=headers, tablefmt=tablefmt)

    # Fallback table formatter
    keys = list(records[0].keys())
    col_widths = {k: max(len(str(k)), max(len(str(r.get(k, ""))) for r in records)) for k in keys}

    sep = "+-" + "-+-".join("-" * col_widths[k] for k in keys) + "-+"
    header_line = "| " + " | ".join(f"{str(k).ljust(col_widths[k])}" for k in keys) + " |"

    lines = [sep, header_line, sep]
    for r in records:
        row_str = "| " + " | ".join(f"{str(r.get(k, '')).ljust(col_widths[k])}" for k in keys) + " |"
        lines.append(row_str)
    lines.append(sep)
    return "\n".join(lines)


# =====================================================================
# 1. NumPy Implementation (Section 5)
# =====================================================================
def run_numpy_analysis(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Perform comprehensive numerical analysis using NumPy on real CSV data.
    Demonstrates:
      - 1D NumPy arrays
      - 2D NumPy array
      - Array indexing
      - Array slicing
      - sum, mean, max, min, std
    """
    fees_df = data_mgr.load_fees_df()
    rooms_df = data_mgr.load_rooms_df()

    if fees_df.empty or rooms_df.empty:
        raise ValueError("Cannot perform NumPy analysis on empty datasets.")

    # 1. 1D NumPy arrays
    hostel_fees_1d = np.array(fees_df["Hostel_Fee"].values, dtype=float)
    hostel_paid_1d = np.array(fees_df["Hostel_Paid"].values, dtype=float)
    mess_fees_1d = np.array(fees_df["Mess_Fee"].values, dtype=float)
    mess_paid_1d = np.array(fees_df["Mess_Paid"].values, dtype=float)

    hostel_pending_1d = np.maximum(0.0, hostel_fees_1d - hostel_paid_1d)
    mess_pending_1d = np.maximum(0.0, mess_fees_1d - mess_paid_1d)
    total_paid_1d = hostel_paid_1d + mess_paid_1d
    total_pending_1d = hostel_pending_1d + mess_pending_1d

    room_capacities_1d = np.array(rooms_df["Capacity"].values, dtype=int)
    room_occupied_1d = np.array(rooms_df["Occupied"].values, dtype=int)
    room_vacancy_1d = np.array(rooms_df["Vacancy"].values, dtype=int)

    # 2. 2D NumPy arrays
    # 2D Fee Matrix: Shape (N, 4) -> [Hostel_Fee, Hostel_Paid, Mess_Fee, Mess_Paid]
    fee_matrix_2d = np.column_stack((hostel_fees_1d, hostel_paid_1d, mess_fees_1d, mess_paid_1d))
    # 2D Room Matrix: Shape (M, 3) -> [Capacity, Occupied, Vacancy]
    room_matrix_2d = np.column_stack((room_capacities_1d, room_occupied_1d, room_vacancy_1d))

    # 3. Array Indexing
    first_student_hostel_fee = float(fee_matrix_2d[0, 0])
    first_student_mess_paid = float(fee_matrix_2d[0, 3])
    fifth_student_total_paid = float(total_paid_1d[4]) if len(total_paid_1d) >= 5 else 0.0

    # 4. Array Slicing
    first_five_fee_slice = fee_matrix_2d[0:5, 0:2]  # First 5 students, Hostel Fee & Paid
    room_slice_top3 = room_matrix_2d[:3, :]

    # 5. Statistical operations (sum, mean, max, min, std)
    stats = {
        "hostel_fee_sum": float(np.sum(hostel_fees_1d)),
        "hostel_paid_sum": float(np.sum(hostel_paid_1d)),
        "hostel_pending_sum": float(np.sum(hostel_pending_1d)),
        "mess_fee_sum": float(np.sum(mess_fees_1d)),
        "mess_paid_sum": float(np.sum(mess_paid_1d)),
        "mess_pending_sum": float(np.sum(mess_pending_1d)),
        "total_paid_sum": float(np.sum(total_paid_1d)),
        "total_pending_sum": float(np.sum(total_pending_1d)),

        "hostel_fee_mean": float(np.mean(hostel_fees_1d)),
        "hostel_paid_mean": float(np.mean(hostel_paid_1d)),
        "mess_fee_mean": float(np.mean(mess_fees_1d)),
        "mess_paid_mean": float(np.mean(mess_paid_1d)),
        "total_paid_mean": float(np.mean(total_paid_1d)),

        "hostel_paid_max": float(np.max(hostel_paid_1d)),
        "hostel_paid_min": float(np.min(hostel_paid_1d)),
        "mess_paid_max": float(np.max(mess_paid_1d)),
        "mess_paid_min": float(np.min(mess_paid_1d)),
        "total_paid_max": float(np.max(total_paid_1d)),
        "total_paid_min": float(np.min(total_paid_1d)),

        "hostel_paid_std": float(np.std(hostel_paid_1d)),
        "mess_paid_std": float(np.std(mess_paid_1d)),
        "total_paid_std": float(np.std(total_paid_1d)),

        # Rooms stats
        "total_capacity": int(np.sum(room_capacities_1d)),
        "total_occupied": int(np.sum(room_occupied_1d)),
        "total_vacant": int(np.sum(room_vacancy_1d)),
        "mean_room_capacity": float(np.mean(room_capacities_1d)),
        "mean_room_occupancy": float(np.mean(room_occupied_1d)),
    }

    return {
        "stats": stats,
        "fee_matrix_shape": fee_matrix_2d.shape,
        "room_matrix_shape": room_matrix_2d.shape,
        "indexed_values": {
            "first_student_hostel_fee": first_student_hostel_fee,
            "first_student_mess_paid": first_student_mess_paid,
            "fifth_student_total_paid": fifth_student_total_paid,
        },
        "slice_sample": first_five_fee_slice.tolist(),
    }


# =====================================================================
# 2. Pandas Implementation (Section 6 & 10)
# =====================================================================
def get_students_head_tail(data_mgr: DataManager, n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Display first n and last n students (Demonstrating head and tail)."""
    df = data_mgr.load_students_df()
    return df.head(n), df.tail(n)


def get_selected_student_columns(data_mgr: DataManager, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Display selected columns of students dataset."""
    df = data_mgr.load_students_df()
    if columns is None:
        columns = ["Student_ID", "Name", "Course", "Room_No"]
    valid_cols = [c for c in columns if c in df.columns]
    return df[valid_cols]


def filter_pending_fees(data_mgr: DataManager, fee_type: str = "both") -> pd.DataFrame:
    """
    Filter students having pending fee balances using Pandas boolean indexing.
    fee_type: 'hostel', 'mess', or 'both' (either hostel or mess pending).
    """
    fees_df = data_mgr.load_fees_df()
    students_df = data_mgr.load_students_df()

    fees_df["Hostel_Pending"] = fees_df["Hostel_Fee"] - fees_df["Hostel_Paid"]
    fees_df["Mess_Pending"] = fees_df["Mess_Fee"] - fees_df["Mess_Paid"]
    fees_df["Total_Pending"] = fees_df["Hostel_Pending"] + fees_df["Mess_Pending"]

    if fee_type == "hostel":
        filtered_fees = fees_df[fees_df["Hostel_Pending"] > 0]
    elif fee_type == "mess":
        filtered_fees = fees_df[fees_df["Mess_Pending"] > 0]
    else:
        filtered_fees = fees_df[fees_df["Total_Pending"] > 0]

    merged = pd.merge(students_df, filtered_fees, on="Student_ID", how="inner")
    display_cols = [
        "Student_ID", "Name", "Course", "Room_No",
        "Hostel_Fee", "Hostel_Paid", "Hostel_Pending",
        "Mess_Fee", "Mess_Paid", "Mess_Pending", "Total_Pending"
    ]
    return merged[[c for c in display_cols if c in merged.columns]]


def sort_students_by_paid_fees(data_mgr: DataManager, ascending: bool = False) -> pd.DataFrame:
    """Sort students according to total fees paid (Demonstrating sort_values)."""
    fees_df = data_mgr.load_fees_df()
    students_df = data_mgr.load_students_df()

    fees_df["Total_Paid"] = fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]
    fees_df["Total_Fee"] = fees_df["Hostel_Fee"] + fees_df["Mess_Fee"]
    fees_df["Total_Pending"] = fees_df["Total_Fee"] - fees_df["Total_Paid"]

    merged = pd.merge(students_df, fees_df, on="Student_ID", how="inner")
    sorted_df = merged.sort_values(by="Total_Paid", ascending=ascending)

    display_cols = ["Student_ID", "Name", "Course", "Room_No", "Total_Fee", "Total_Paid", "Total_Pending"]
    return sorted_df[[c for c in display_cols if c in sorted_df.columns]]


def group_students_by_course(data_mgr: DataManager) -> pd.DataFrame:
    """Group students according to courses (Demonstrating GroupBy)."""
    students_df = data_mgr.load_students_df()
    grouped = students_df.groupby("Course").agg(
        Total_Students=("Student_ID", "count"),
        Allocated_Students=("Room_No", lambda s: (s.str.strip() != "").sum()),
    ).reset_index()
    grouped["Unallocated_Students"] = grouped["Total_Students"] - grouped["Allocated_Students"]
    return grouped.sort_values(by="Total_Students", ascending=False)


def group_room_occupancy_by_type(data_mgr: DataManager) -> pd.DataFrame:
    """Group room occupancy according to room type (Demonstrating GroupBy)."""
    rooms_df = data_mgr.load_rooms_df()
    grouped = rooms_df.groupby("Room_Type").agg(
        Total_Rooms=("Room_No", "count"),
        Total_Capacity=("Capacity", "sum"),
        Total_Occupied=("Occupied", "sum"),
        Total_Vacancy=("Vacancy", "sum"),
    ).reset_index()

    grouped["Occupancy_Rate_%"] = (
        (grouped["Total_Occupied"] / grouped["Total_Capacity"]) * 100
    ).round(2)
    return grouped


def group_room_occupancy_by_floor(data_mgr: DataManager) -> pd.DataFrame:
    """Group rooms by floor."""
    rooms_df = data_mgr.load_rooms_df()
    grouped = rooms_df.groupby("Floor").agg(
        Rooms=("Room_No", "count"),
        Capacity=("Capacity", "sum"),
        Occupied=("Occupied", "sum"),
        Vacancy=("Vacancy", "sum"),
    ).reset_index()
    grouped["Occupancy_%"] = ((grouped["Occupied"] / grouped["Capacity"]) * 100).round(2)
    return grouped


def demonstrate_missing_value_handling(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Demonstrate Pandas missing value detection and imputation (isna, fillna).
    Uses a temporary copy to illustrate without modifying actual datasets.
    """
    df = data_mgr.load_students_df().copy()
    # Introduce deliberate NaN in sample copy for demonstration
    sample_df = df.head(10).copy()
    sample_df.loc[sample_df.index[:2], "Room_No"] = np.nan
    sample_df.loc[sample_df.index[2:4], "Contact"] = np.nan

    missing_count = sample_df.isna().sum().to_dict()
    imputed_df = sample_df.fillna({"Room_No": "UNASSIGNED", "Contact": "NOT_AVAILABLE"})
    post_impute_missing = imputed_df.isna().sum().to_dict()

    return {
        "pre_impute_missing": missing_count,
        "post_impute_missing": post_impute_missing,
        "sample_cleaned_head": imputed_df[["Student_ID", "Name", "Room_No", "Contact"]].to_dict(orient="records"),
    }


def get_course_fee_breakdown(data_mgr: DataManager) -> pd.DataFrame:
    """Merge students and fees and group by Course to evaluate fee collection per branch."""
    students_df = data_mgr.load_students_df()
    fees_df = data_mgr.load_fees_df()

    fees_df["Total_Fee"] = fees_df["Hostel_Fee"] + fees_df["Mess_Fee"]
    fees_df["Total_Paid"] = fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]
    fees_df["Total_Pending"] = fees_df["Total_Fee"] - fees_df["Total_Paid"]

    merged = pd.merge(students_df, fees_df, on="Student_ID", how="inner")
    grouped = merged.groupby("Course").agg(
        Students=("Student_ID", "count"),
        Total_Billed=("Total_Fee", "sum"),
        Total_Collected=("Total_Paid", "sum"),
        Total_Pending=("Total_Pending", "sum"),
    ).reset_index()

    grouped["Collection_Rate_%"] = ((grouped["Total_Collected"] / grouped["Total_Billed"]) * 100).round(2)
    return grouped.sort_values(by="Total_Billed", ascending=False)


# =====================================================================
# 3. Summary Report (Section 9)
# =====================================================================
def generate_summary_report(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Generate dynamic summary report containing all 15 required metrics:
      1. Total registered students
      2. Total rooms
      3. Total room capacity
      4. Total occupied beds
      5. Total vacant beds
      6. Room occupancy percentage
      7. Total hostel fees
      8. Total hostel fees collected
      9. Total hostel outstanding balance
      10. Total mess fees
      11. Total mess fees collected
      12. Total mess outstanding balance
      13. Number of students with pending hostel fees
      14. Number of students with pending mess fees
      15. Number of fully paid students
    """
    students_df = data_mgr.load_students_df()
    rooms_df = data_mgr.load_rooms_df()
    fees_df = data_mgr.load_fees_df()

    total_registered_students = len(students_df)
    total_rooms = len(rooms_df)
    total_room_capacity = int(rooms_df["Capacity"].sum()) if not rooms_df.empty else 0
    total_occupied_beds = int(rooms_df["Occupied"].sum()) if not rooms_df.empty else 0
    total_vacant_beds = int(rooms_df["Vacancy"].sum()) if not rooms_df.empty else 0

    room_occupancy_pct = (
        round((total_occupied_beds / total_room_capacity) * 100, 2)
        if total_room_capacity > 0
        else 0.0
    )

    total_hostel_fees = float(fees_df["Hostel_Fee"].sum()) if not fees_df.empty else 0.0
    total_hostel_collected = float(fees_df["Hostel_Paid"].sum()) if not fees_df.empty else 0.0
    total_hostel_outstanding = round(total_hostel_fees - total_hostel_collected, 2)

    total_mess_fees = float(fees_df["Mess_Fee"].sum()) if not fees_df.empty else 0.0
    total_mess_collected = float(fees_df["Mess_Paid"].sum()) if not fees_df.empty else 0.0
    total_mess_outstanding = round(total_mess_fees - total_mess_collected, 2)

    if not fees_df.empty:
        pending_hostel_students = int((fees_df["Hostel_Fee"] > fees_df["Hostel_Paid"]).sum())
        pending_mess_students = int((fees_df["Mess_Fee"] > fees_df["Mess_Paid"]).sum())
        fully_paid_students = int(
            (
                (fees_df["Hostel_Fee"] <= fees_df["Hostel_Paid"])
                & (fees_df["Mess_Fee"] <= fees_df["Mess_Paid"])
            ).sum()
        )
    else:
        pending_hostel_students = 0
        pending_mess_students = 0
        fully_paid_students = 0

    report = {
        "Total Registered Students": total_registered_students,
        "Total Rooms": total_rooms,
        "Total Room Capacity": total_room_capacity,
        "Total Occupied Beds": total_occupied_beds,
        "Total Vacant Beds": total_vacant_beds,
        "Room Occupancy Percentage": f"{room_occupancy_pct}%",
        "Total Hostel Fees": f"₹{total_hostel_fees:,.2f}",
        "Total Hostel Fees Collected": f"₹{total_hostel_collected:,.2f}",
        "Total Hostel Outstanding Balance": f"₹{total_hostel_outstanding:,.2f}",
        "Total Mess Fees": f"₹{total_mess_fees:,.2f}",
        "Total Mess Fees Collected": f"₹{total_mess_collected:,.2f}",
        "Total Mess Outstanding Balance": f"₹{total_mess_outstanding:,.2f}",
        "Students with Pending Hostel Fees": pending_hostel_students,
        "Students with Pending Mess Fees": pending_mess_students,
        "Fully Paid Students": fully_paid_students,
        # Raw numeric values for programmatic use
        "_raw": {
            "total_registered_students": total_registered_students,
            "total_rooms": total_rooms,
            "total_room_capacity": total_room_capacity,
            "total_occupied_beds": total_occupied_beds,
            "total_vacant_beds": total_vacant_beds,
            "room_occupancy_pct": room_occupancy_pct,
            "total_hostel_fees": total_hostel_fees,
            "total_hostel_collected": total_hostel_collected,
            "total_hostel_outstanding": total_hostel_outstanding,
            "total_mess_fees": total_mess_fees,
            "total_mess_collected": total_mess_collected,
            "total_mess_outstanding": total_mess_outstanding,
            "pending_hostel_students": pending_hostel_students,
            "pending_mess_students": pending_mess_students,
            "fully_paid_students": fully_paid_students,
        }
    }

    return report


# =====================================================================
# 4. Advanced Comparative Analysis (Section 10)
# =====================================================================
def run_comparative_analysis(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Perform comparative fee and demographic analysis:
      - Compare hostel vs mess collection
      - Category with higher outstanding dues
      - Courses with highest student population
    """
    summary = generate_summary_report(data_mgr)["_raw"]
    students_df = data_mgr.load_students_df()

    hostel_out = summary["total_hostel_outstanding"]
    mess_out = summary["total_mess_outstanding"]

    if hostel_out > mess_out:
        higher_due_category = f"Hostel Fees (₹{hostel_out:,.2f} vs Mess ₹{mess_out:,.2f})"
    elif mess_out > hostel_out:
        higher_due_category = f"Mess Fees (₹{mess_out:,.2f} vs Hostel ₹{hostel_out:,.2f})"
    else:
        higher_due_category = "Both Equal"

    course_counts = students_df["Course"].value_counts().to_dict() if not students_df.empty else {}
    top_course = max(course_counts.items(), key=lambda x: x[1])[0] if course_counts else "N/A"

    gender_counts = students_df["Gender"].value_counts().to_dict() if not students_df.empty else {}
    year_counts = students_df["Year"].value_counts().to_dict() if not students_df.empty else {}

    return {
        "hostel_collected": summary["total_hostel_collected"],
        "mess_collected": summary["total_mess_collected"],
        "hostel_outstanding": hostel_out,
        "mess_outstanding": mess_out,
        "higher_due_category": higher_due_category,
        "course_distribution": course_counts,
        "top_course": top_course,
        "gender_distribution": gender_counts,
        "year_distribution": year_counts,
    }


def get_fee_statistics_describe(data_mgr: DataManager) -> pd.DataFrame:
    """
    Generate comprehensive Pandas statistical description table (df.describe()).
    Demonstrates describe() method on actual numerical fee attributes.
    """
    fees_df = data_mgr.load_fees_df()
    numeric_cols = ["Hostel_Fee", "Hostel_Paid", "Mess_Fee", "Mess_Paid"]
    describe_df = fees_df[numeric_cols].describe().round(2).reset_index()
    describe_df.rename(columns={"index": "Statistic"}, inplace=True)
    return describe_df


def analyze_data(data_mgr: DataManager) -> Dict[str, Any]:
    """
    Master analytical function consolidating NumPy and Pandas dataset analyses.
    Directly satisfies Section 4 & Section 10 reporting specifications.
    """
    numpy_results = run_numpy_analysis(data_mgr)
    pandas_describe = get_fee_statistics_describe(data_mgr)
    course_group = group_students_by_course(data_mgr)
    room_group = group_room_occupancy_by_type(data_mgr)
    floor_group = group_room_occupancy_by_floor(data_mgr)
    comparative = run_comparative_analysis(data_mgr)
    summary = generate_summary_report(data_mgr)

    return {
        "summary": summary,
        "numpy_stats": numpy_results["stats"],
        "numpy_indexing": numpy_results["indexed_values"],
        "numpy_slicing": numpy_results["slice_sample"],
        "pandas_describe": pandas_describe.to_dict(orient="records"),
        "course_distribution": course_group.to_dict(orient="records"),
        "room_type_occupancy": room_group.to_dict(orient="records"),
        "floor_occupancy": floor_group.to_dict(orient="records"),
        "comparative": comparative,
    }


# =====================================================================
# 5. Report Export (Section 10 & 11)
# =====================================================================
def export_report(data_mgr: DataManager, report_type: str = "all") -> List[str]:
    """
    Export administrative and analytical reports into reports/ directory.
    Outputs text summary and analytical CSVs.
    Returns list of generated file paths.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exported_files: List[str] = []

    # 1. Summary Report Text
    summary = generate_summary_report(data_mgr)
    summary_file = data_mgr.reports_dir / f"hostel_summary_report_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("      HOSTEL MANAGEMENT SYSTEM - EXECUTIVE SUMMARY\n")
        f.write(f"      Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for k, v in summary.items():
            if not k.startswith("_"):
                f.write(f"{k.ljust(35)}: {v}\n")
        f.write("\n" + "=" * 60 + "\n")
    exported_files.append(str(summary_file))

    # 2. Course-wise Fee Analysis CSV
    course_df = get_course_fee_breakdown(data_mgr)
    course_file = data_mgr.reports_dir / f"course_analysis_{timestamp}.csv"
    course_df.to_csv(course_file, index=False)
    exported_files.append(str(course_file))

    # 3. Room Occupancy Breakdown CSV
    room_type_df = group_room_occupancy_by_type(data_mgr)
    room_file = data_mgr.reports_dir / f"room_occupancy_analysis_{timestamp}.csv"
    room_type_df.to_csv(room_file, index=False)
    exported_files.append(str(room_file))

    # 4. Pending Dues List CSV
    pending_df = filter_pending_fees(data_mgr, fee_type="both")
    pending_file = data_mgr.reports_dir / f"defaulters_pending_list_{timestamp}.csv"
    pending_df.to_csv(pending_file, index=False)
    exported_files.append(str(pending_file))

    return exported_files
