"""
Fee Management Module for Hostel Management System.
Handles hostel and mess fee payments, balance tracking, and status calculations.
Statuses: PAID, PARTIAL, PENDING, OVERDUE.
Demonstrates: Dict methods, List operations, mathematical validations.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from data_manager import DataManager


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse YYYY-MM-DD date string safely."""
    clean = str(date_str).strip()
    if not clean:
        return None
    try:
        return datetime.strptime(clean, "%Y-%m-%d")
    except ValueError:
        return None


def calculate_status(total_fee: float, paid_amount: float, due_date_str: str) -> str:
    """
    Calculate fee payment status:
      - PAID: paid >= fee
      - OVERDUE: paid < fee and current date > due_date
      - PARTIAL: 0 < paid < fee and current date <= due_date
      - PENDING: paid == 0 and current date <= due_date
    """
    total = float(total_fee)
    paid = float(paid_amount)
    pending = total - paid

    if pending <= 0:
        return "PAID"

    due_dt = parse_date(due_date_str)
    is_past_due = False
    if due_dt:
        # Compare with today's date
        today = datetime.now()
        is_past_due = today.date() > due_dt.date()

    if is_past_due:
        return "OVERDUE"
    elif paid > 0:
        return "PARTIAL"
    else:
        return "PENDING"


def calculate_pending_fees(student_id: str, data_mgr: DataManager) -> Dict[str, Any]:
    """
    Calculate comprehensive fee statement for a student:
      Hostel Fee, Paid, Pending, Status;
      Mess Fee, Paid, Pending, Status;
      Combined Totals and Overall Status.
    """
    student_id = str(student_id).strip().upper()
    fees_list = data_mgr.load_fees_list()

    fee_rec = None
    for f in fees_list:
        if f.get("Student_ID") == student_id:
            fee_rec = f
            break

    if not fee_rec:
        raise ValueError(f"Fee record for Student '{student_id}' not found.")

    hostel_fee = float(fee_rec.get("Hostel_Fee", 0.0))
    hostel_paid = float(fee_rec.get("Hostel_Paid", 0.0))
    hostel_pending = max(0.0, hostel_fee - hostel_paid)

    mess_fee = float(fee_rec.get("Mess_Fee", 0.0))
    mess_paid = float(fee_rec.get("Mess_Paid", 0.0))
    mess_pending = max(0.0, mess_fee - mess_paid)

    due_date = str(fee_rec.get("Due_Date", ""))
    payment_date = str(fee_rec.get("Payment_Date", ""))

    hostel_status = calculate_status(hostel_fee, hostel_paid, due_date)
    mess_status = calculate_status(mess_fee, mess_paid, due_date)

    total_fee = hostel_fee + mess_fee
    total_paid = hostel_paid + mess_paid
    total_pending = hostel_pending + mess_pending

    # Overall status determination
    if total_pending <= 0:
        overall_status = "PAID"
    elif hostel_status == "OVERDUE" or mess_status == "OVERDUE":
        overall_status = "OVERDUE"
    elif total_paid > 0:
        overall_status = "PARTIAL"
    else:
        overall_status = "PENDING"

    return {
        "Student_ID": student_id,
        "Hostel_Fee": hostel_fee,
        "Hostel_Paid": hostel_paid,
        "Hostel_Pending": hostel_pending,
        "Hostel_Status": hostel_status,
        "Mess_Fee": mess_fee,
        "Mess_Paid": mess_paid,
        "Mess_Pending": mess_pending,
        "Mess_Status": mess_status,
        "Total_Fee": total_fee,
        "Total_Paid": total_paid,
        "Total_Pending": total_pending,
        "Overall_Status": overall_status,
        "Payment_Date": payment_date,
        "Due_Date": due_date,
    }


def record_hostel_payment(
    student_id: str,
    amount: float,
    data_mgr: DataManager,
    payment_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record payment towards hostel fees.
    Validations:
      - Positive amount.
      - Payment cannot exceed pending hostel balance.
    """
    student_id = str(student_id).strip().upper()
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except Exception:
        raise ValueError("Payment amount must be a positive number greater than zero.")

    if not payment_date:
        payment_date = datetime.now().strftime("%Y-%m-%d")
    else:
        if not parse_date(payment_date):
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")

    def _tx(mgr: DataManager):
        fees = mgr.load_fees_list()
        target_idx = -1
        for idx, f in enumerate(fees):
            if f.get("Student_ID") == student_id:
                target_idx = idx
                break

        if target_idx == -1:
            raise ValueError(f"Fee record for student '{student_id}' does not exist.")

        record = fees[target_idx]
        total_fee = float(record.get("Hostel_Fee", 0.0))
        current_paid = float(record.get("Hostel_Paid", 0.0))
        pending = total_fee - current_paid

        if amount > pending:
            raise ValueError(
                f"Payment amount ₹{amount:,.2f} exceeds pending hostel balance of ₹{pending:,.2f}."
            )

        new_paid = round(current_paid + amount, 2)
        record["Hostel_Paid"] = new_paid
        record["Payment_Date"] = payment_date
        fees[target_idx] = record
        mgr.save_fees_list(fees)

        return {
            "Student_ID": student_id,
            "Amount_Paid": amount,
            "Total_Hostel_Paid": new_paid,
            "Remaining_Hostel_Balance": round(total_fee - new_paid, 2),
            "Payment_Date": payment_date,
        }

    return data_mgr.execute_transaction(_tx)


def record_mess_payment(
    student_id: str,
    amount: float,
    data_mgr: DataManager,
    payment_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record payment towards mess fees.
    Validations:
      - Positive amount.
      - Payment cannot exceed pending mess balance.
    """
    student_id = str(student_id).strip().upper()
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except Exception:
        raise ValueError("Payment amount must be a positive number greater than zero.")

    if not payment_date:
        payment_date = datetime.now().strftime("%Y-%m-%d")
    else:
        if not parse_date(payment_date):
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")

    def _tx(mgr: DataManager):
        fees = mgr.load_fees_list()
        target_idx = -1
        for idx, f in enumerate(fees):
            if f.get("Student_ID") == student_id:
                target_idx = idx
                break

        if target_idx == -1:
            raise ValueError(f"Fee record for student '{student_id}' does not exist.")

        record = fees[target_idx]
        total_fee = float(record.get("Mess_Fee", 0.0))
        current_paid = float(record.get("Mess_Paid", 0.0))
        pending = total_fee - current_paid

        if amount > pending:
            raise ValueError(
                f"Payment amount ₹{amount:,.2f} exceeds pending mess balance of ₹{pending:,.2f}."
            )

        new_paid = round(current_paid + amount, 2)
        record["Mess_Paid"] = new_paid
        record["Payment_Date"] = payment_date
        fees[target_idx] = record
        mgr.save_fees_list(fees)

        return {
            "Student_ID": student_id,
            "Amount_Paid": amount,
            "Total_Mess_Paid": new_paid,
            "Remaining_Mess_Balance": round(total_fee - new_paid, 2),
            "Payment_Date": payment_date,
        }

    return data_mgr.execute_transaction(_tx)


def update_hostel_fee(student_id: str, new_fee: float, data_mgr: DataManager) -> Dict[str, Any]:
    """Update assigned hostel fee for a student."""
    student_id = str(student_id).strip().upper()
    try:
        new_fee = float(new_fee)
        if new_fee < 0:
            raise ValueError()
    except Exception:
        raise ValueError("Hostel fee amount cannot be negative.")

    def _tx(mgr: DataManager):
        fees = mgr.load_fees_list()
        for f in fees:
            if f.get("Student_ID") == student_id:
                f["Hostel_Fee"] = new_fee
                mgr.save_fees_list(fees)
                return f
        raise ValueError(f"Student '{student_id}' not found in fee records.")

    return data_mgr.execute_transaction(_tx)


def update_mess_fee(student_id: str, new_fee: float, data_mgr: DataManager) -> Dict[str, Any]:
    """Update assigned mess fee for a student."""
    student_id = str(student_id).strip().upper()
    try:
        new_fee = float(new_fee)
        if new_fee < 0:
            raise ValueError()
    except Exception:
        raise ValueError("Mess fee amount cannot be negative.")

    def _tx(mgr: DataManager):
        fees = mgr.load_fees_list()
        for f in fees:
            if f.get("Student_ID") == student_id:
                f["Mess_Fee"] = new_fee
                mgr.save_fees_list(fees)
                return f
        raise ValueError(f"Student '{student_id}' not found in fee records.")

    return data_mgr.execute_transaction(_tx)


def display_fee_status(
    data_mgr: DataManager,
    student_id: Optional[str] = None,
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve fee statuses for all students or filtered by student_id/status.
    Statuses: PAID, PARTIAL, PENDING, OVERDUE.
    """
    fees_list = data_mgr.load_fees_list()
    results: List[Dict[str, Any]] = []

    for f in fees_list:
        s_id = str(f.get("Student_ID", ""))
        if student_id and s_id != student_id.strip().upper():
            continue

        statement = calculate_pending_fees(s_id, data_mgr)
        if status_filter:
            target_status = status_filter.strip().upper()
            if statement["Overall_Status"] != target_status and statement["Hostel_Status"] != target_status and statement["Mess_Status"] != target_status:
                continue

        results.append(statement)

    return results
