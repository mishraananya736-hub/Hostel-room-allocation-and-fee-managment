"""
Data Manager Module for Hostel Management System.
Handles CSV file storage, persistence, transactional safety, and schema validation.
"""

from __future__ import annotations
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


# Schema definitions
STUDENT_COLUMNS = ["Student_ID", "Name", "Gender", "Course", "Year", "Room_No", "Contact"]
ROOM_COLUMNS = ["Room_No", "Floor", "Room_Type", "Capacity", "Occupied", "Vacancy"]
FEE_COLUMNS = ["Student_ID", "Hostel_Fee", "Hostel_Paid", "Mess_Fee", "Mess_Paid", "Payment_Date", "Due_Date"]


class DataManager:
    """Manages reading, writing, and transactional safety of CSV data files."""

    def __init__(self, data_dir: Optional[Path | str] = None, reports_dir: Optional[Path | str] = None) -> None:
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent / "data"
        else:
            self.data_dir = Path(data_dir).resolve()

        if reports_dir is None:
            self.reports_dir = Path(__file__).resolve().parent / "reports"
        else:
            self.reports_dir = Path(reports_dir).resolve()

        self.students_file = self.data_dir / "students.csv"
        self.rooms_file = self.data_dir / "rooms.csv"
        self.fees_file = self.data_dir / "fees.csv"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Backup & Safe Atomic Operations
    # ---------------------------------------------------------
    def _create_temp_backup(self) -> str:
        """Create a temporary directory backup of the current CSV files."""
        backup_dir = tempfile.mkdtemp(prefix="hostel_backup_")
        for f in [self.students_file, self.rooms_file, self.fees_file]:
            if f.exists():
                shutil.copy2(f, Path(backup_dir) / f.name)
        return backup_dir

    def _restore_backup(self, backup_dir: str) -> None:
        """Restore CSV files from a temporary directory backup."""
        b_path = Path(backup_dir)
        for f in [self.students_file, self.rooms_file, self.fees_file]:
            source = b_path / f.name
            if source.exists():
                shutil.copy2(source, f)
        shutil.rmtree(backup_dir, ignore_errors=True)

    def _cleanup_backup(self, backup_dir: str) -> None:
        """Clean up the temporary backup directory."""
        shutil.rmtree(backup_dir, ignore_errors=True)

    def _safe_write_df(self, df: pd.DataFrame, target_path: Path) -> None:
        """Atomically write a DataFrame to CSV to prevent corrupted or partial writes."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = target_path.with_suffix(".tmp")
        try:
            df.to_csv(temp_file, index=False)
            temp_file.replace(target_path)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise IOError(f"Failed to safely write to {target_path}: {e}") from e

    # ---------------------------------------------------------
    # Students Data Handling
    # ---------------------------------------------------------
    def load_students_df(self) -> pd.DataFrame:
        """Load students CSV as a pandas DataFrame."""
        if not self.students_file.exists() or self.students_file.stat().st_size == 0:
            return pd.DataFrame(columns=STUDENT_COLUMNS)
        try:
            df = pd.read_csv(self.students_file, dtype={"Student_ID": str, "Contact": str, "Room_No": str})
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(1).astype(int)
            # Fill missing text fields with empty string
            for col in ["Name", "Gender", "Course", "Room_No", "Contact"]:
                if col in df.columns:
                    df[col] = df[col].fillna("").astype(str)
            # Ensure schema completeness
            for col in STUDENT_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[STUDENT_COLUMNS]
        except Exception as e:
            raise IOError(f"Error reading students CSV ({self.students_file}): {e}") from e

    def save_students_df(self, df: pd.DataFrame) -> None:
        """Save students DataFrame to CSV."""
        self._safe_write_df(df[STUDENT_COLUMNS], self.students_file)

    def load_students_list(self) -> List[Dict[str, Any]]:
        """Load students as a Python list of dictionaries (Demonstrating List and Dict data structures)."""
        df = self.load_students_df()
        return df.to_dict(orient="records")

    def save_students_list(self, students_list: List[Dict[str, Any]]) -> None:
        """Save students from a Python list of dictionaries."""
        df = pd.DataFrame(students_list)
        for col in STUDENT_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        self.save_students_df(df)

    # ---------------------------------------------------------
    # Rooms Data Handling
    # ---------------------------------------------------------
    def load_rooms_df(self) -> pd.DataFrame:
        """Load rooms CSV as a pandas DataFrame."""
        if not self.rooms_file.exists() or self.rooms_file.stat().st_size == 0:
            return pd.DataFrame(columns=ROOM_COLUMNS)
        try:
            df = pd.read_csv(self.rooms_file, dtype={"Room_No": str, "Room_Type": str})
            df["Floor"] = pd.to_numeric(df["Floor"], errors="coerce").fillna(1).astype(int)
            df["Capacity"] = pd.to_numeric(df["Capacity"], errors="coerce").fillna(1).astype(int)
            df["Occupied"] = pd.to_numeric(df["Occupied"], errors="coerce").fillna(0).astype(int)
            df["Vacancy"] = pd.to_numeric(df["Vacancy"], errors="coerce").fillna(df["Capacity"]).astype(int)
            for col in ROOM_COLUMNS:
                if col not in df.columns:
                    df[col] = 0
            return df[ROOM_COLUMNS]
        except Exception as e:
            raise IOError(f"Error reading rooms CSV ({self.rooms_file}): {e}") from e

    def save_rooms_df(self, df: pd.DataFrame) -> None:
        """Save rooms DataFrame to CSV."""
        self._safe_write_df(df[ROOM_COLUMNS], self.rooms_file)

    def load_rooms_list(self) -> List[Dict[str, Any]]:
        """Load rooms as a Python list of dictionaries."""
        df = self.load_rooms_df()
        return df.to_dict(orient="records")

    def save_rooms_list(self, rooms_list: List[Dict[str, Any]]) -> None:
        """Save rooms from a Python list of dictionaries."""
        df = pd.DataFrame(rooms_list)
        for col in ROOM_COLUMNS:
            if col not in df.columns:
                df[col] = 0
        self.save_rooms_df(df)

    # ---------------------------------------------------------
    # Fees Data Handling
    # ---------------------------------------------------------
    def load_fees_df(self) -> pd.DataFrame:
        """Load fees CSV as a pandas DataFrame."""
        if not self.fees_file.exists() or self.fees_file.stat().st_size == 0:
            return pd.DataFrame(columns=FEE_COLUMNS)
        try:
            df = pd.read_csv(self.fees_file, dtype={"Student_ID": str, "Payment_Date": str, "Due_Date": str})
            df["Hostel_Fee"] = pd.to_numeric(df["Hostel_Fee"], errors="coerce").fillna(0.0).astype(float)
            df["Hostel_Paid"] = pd.to_numeric(df["Hostel_Paid"], errors="coerce").fillna(0.0).astype(float)
            df["Mess_Fee"] = pd.to_numeric(df["Mess_Fee"], errors="coerce").fillna(0.0).astype(float)
            df["Mess_Paid"] = pd.to_numeric(df["Mess_Paid"], errors="coerce").fillna(0.0).astype(float)
            df["Payment_Date"] = df["Payment_Date"].fillna("").astype(str)
            df["Due_Date"] = df["Due_Date"].fillna("").astype(str)
            for col in FEE_COLUMNS:
                if col not in df.columns:
                    df[col] = 0
            return df[FEE_COLUMNS]
        except Exception as e:
            raise IOError(f"Error reading fees CSV ({self.fees_file}): {e}") from e

    def save_fees_df(self, df: pd.DataFrame) -> None:
        """Save fees DataFrame to CSV."""
        self._safe_write_df(df[FEE_COLUMNS], self.fees_file)

    def load_fees_list(self) -> List[Dict[str, Any]]:
        """Load fees as a Python list of dictionaries."""
        df = self.load_fees_df()
        return df.to_dict(orient="records")

    def save_fees_list(self, fees_list: List[Dict[str, Any]]) -> None:
        """Save fees from a Python list of dictionaries."""
        df = pd.DataFrame(fees_list)
        for col in FEE_COLUMNS:
            if col not in df.columns:
                df[col] = 0
        self.save_fees_df(df)

    # ---------------------------------------------------------
    # Cross-Table Synchronization & Integrity
    # ---------------------------------------------------------
    def sync_room_occupancies(self) -> pd.DataFrame:
        """
        Recalculate and synchronize room Occupied and Vacancy numbers directly
        from the actual active student assignments in students.csv.
        """
        students_df = self.load_students_df()
        rooms_df = self.load_rooms_df()

        if rooms_df.empty:
            return rooms_df

        # Count active occupants per room (excluding empty or unallocated)
        valid_students = students_df[students_df["Room_No"].str.strip() != ""]
        counts = valid_students["Room_No"].value_counts().to_dict()

        for idx, row in rooms_df.iterrows():
            room_no = str(row["Room_No"])
            capacity = int(row["Capacity"])
            occupied = int(counts.get(room_no, 0))
            vacancy = max(0, capacity - occupied)
            rooms_df.at[idx, "Occupied"] = occupied
            rooms_df.at[idx, "Vacancy"] = vacancy

        self.save_rooms_df(rooms_df)
        return rooms_df

    def execute_transaction(self, update_fn) -> Any:
        """
        Execute an operation involving multiple tables with automatic rollback on error.
        update_fn receives self as argument.
        """
        backup_dir = self._create_temp_backup()
        try:
            result = update_fn(self)
            self._cleanup_backup(backup_dir)
            return result
        except Exception as e:
            self._restore_backup(backup_dir)
            raise e
