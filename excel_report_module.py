"""
Excel Report Module for Hostel Management System.
Generates an executive, publication-grade, 7-sheet Excel Workbook with
KPI cards, native Openpyxl charts, conditional formatting, Indian Rupee currency
formatting, auto-filters, frozen panes, and dynamic formulas.

File Output: reports/Hostel_Management_Professional_Report.xlsx
"""

from __future__ import annotations
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference, Series
from openpyxl.formatting.rule import CellIsRule
import numpy as np
import pandas as pd

from data_manager import DataManager

# Design System Colors
NAVY_PRIMARY = "14213D"      # Dark Navy
ROYAL_BLUE = "2563EB"        # Royal Blue
TEAL_ACCENT = "0F766E"       # Teal
GOLD_ACCENT = "E9B44C"       # Gold / Amber
LIGHT_BG = "F5F7FA"          # Very light grey
CARD_BG = "FFFFFF"           # White
BORDER_GREY = "D1D5DB"       # Light grey border
DARK_TEXT = "1F2937"         # Charcoal dark text
MUTED_TEXT = "6B7280"        # Muted grey text

# Status Alert Colors
GREEN_FILL = "D1FAE5"
GREEN_TEXT = "065F46"
YELLOW_FILL = "FEF3C7"
YELLOW_TEXT = "92400E"
ORANGE_FILL = "FFEDD5"
ORANGE_TEXT = "9A3412"
RED_FILL = "FEE2E2"
RED_TEXT = "991B1B"

CURRENCY_FORMAT = '₹#,##0.00'
INTEGER_FORMAT = '#,##0'
PERCENT_FORMAT = '0.0%'


def get_thin_border(color: str = BORDER_GREY) -> Border:
    """Return standard thin cell border."""
    side = Side(style="thin", color=color)
    return Border(left=side, right=side, top=side, bottom=side)


def apply_header_style(cell, text: str, bg_color: str = NAVY_PRIMARY) -> None:
    """Format table header cells."""
    cell.value = text
    cell.font = Font(name="Calibri", size=10.5, bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = get_thin_border("4B5563")


def auto_fit_columns(ws, min_width: int = 12, max_width: int = 40) -> None:
    """Automatically adjust column widths to fit content comfortably."""
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Skip merged cells or extremely wide titles
            if cell.coordinate in ws.merged_cells:
                continue
            val = str(cell.value or "")
            if "\n" in val:
                val = max(val.split("\n"), key=len)
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, min_width), max_width)


def configure_sheet_page_setup(ws, landscape: bool = True, zoom: int = 100) -> None:
    """Configure professional print options, headers/footers, print area, and zoom."""
    ws.views.sheetView[0].showGridLines = True
    ws.views.sheetView[0].zoomScale = zoom

    if landscape:
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    else:
        ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT

    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    # Header and Footer
    ws.oddHeader.center.text = "&BHostel Room Allocation & Fee Management System"
    ws.oddFooter.left.text = "&D &T - Confidential Administrative Record"
    ws.oddFooter.right.text = "Page &P of &N"

    # Set Print Area
    if ws.max_row > 1 and ws.max_column > 1:
        last_col = get_column_letter(ws.max_column)
        ws.print_area = f"A1:{last_col}{ws.max_row}"


# =====================================================================
# SHEET 1: EXECUTIVE DASHBOARD
# =====================================================================
def build_executive_dashboard(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 1: Executive Dashboard with KPI Cards and native charts.
    """
    ws = wb.create_sheet(title="EXECUTIVE DASHBOARD", index=0)
    ws.views.sheetView[0].showGridLines = True

    students_df = data_mgr.load_students_df()
    rooms_df = data_mgr.load_rooms_df()
    fees_df = data_mgr.load_fees_df()

    now_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")

    # 1. Main Header Title Banner
    ws.merge_cells("A2:N2")
    title_cell = ws["A2"]
    title_cell.value = "HOSTEL MANAGEMENT SYSTEM - EXECUTIVE DASHBOARD"
    title_cell.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 36

    # Subtitle Banner
    ws.merge_cells("A3:N3")
    sub_cell = ws["A3"]
    sub_cell.value = f"Hostel Administration & Financial Overview  |  Report Generated: {now_str}  |  Operational Status: Active"
    sub_cell.font = Font(name="Calibri", size=10, italic=True, color="FFFFFF")
    sub_cell.fill = PatternFill(start_color=ROYAL_BLUE, end_color=ROYAL_BLUE, fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 22

    # Calculate metrics
    tot_students = len(students_df)
    tot_rooms = len(rooms_df)
    tot_cap = int(rooms_df["Capacity"].sum()) if not rooms_df.empty else 0
    tot_occ = int(rooms_df["Occupied"].sum()) if not rooms_df.empty else 0
    tot_vac = int(rooms_df["Vacancy"].sum()) if not rooms_df.empty else 0
    occ_rate = (tot_occ / tot_cap) if tot_cap > 0 else 0.0

    tot_h_fee = float(fees_df["Hostel_Fee"].sum()) if not fees_df.empty else 0.0
    tot_h_paid = float(fees_df["Hostel_Paid"].sum()) if not fees_df.empty else 0.0
    tot_h_pend = max(0.0, tot_h_fee - tot_h_paid)

    tot_m_fee = float(fees_df["Mess_Fee"].sum()) if not fees_df.empty else 0.0
    tot_m_paid = float(fees_df["Mess_Paid"].sum()) if not fees_df.empty else 0.0
    tot_m_pend = max(0.0, tot_m_fee - tot_m_paid)

    fully_paid = int(((fees_df["Hostel_Fee"] <= fees_df["Hostel_Paid"]) & (fees_df["Mess_Fee"] <= fees_df["Mess_Paid"])).sum()) if not fees_df.empty else 0
    pending_students = tot_students - fully_paid

    # 2. KPI Cards Helper
    def create_kpi_card(start_col: str, end_col: str, row: int, title: str, value: Any, num_fmt: Optional[str], color_theme: str):
        c1 = f"{start_col}{row}"
        c2 = f"{end_col}{row}"
        ws.merge_cells(f"{c1}:{c2}")
        top = ws[c1]
        top.value = title.upper()
        top.font = Font(name="Calibri", size=8.5, bold=True, color="FFFFFF")
        top.fill = PatternFill(start_color=color_theme, end_color=color_theme, fill_type="solid")
        top.alignment = Alignment(horizontal="center", vertical="center")

        v1 = f"{start_col}{row+1}"
        v2 = f"{end_col}{row+1}"
        ws.merge_cells(f"{v1}:{v2}")
        val_cell = ws[v1]
        val_cell.value = value
        val_cell.font = Font(name="Calibri", size=14, bold=True, color=NAVY_PRIMARY)
        val_cell.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")
        val_cell.alignment = Alignment(horizontal="center", vertical="center")
        if num_fmt:
            val_cell.number_format = num_fmt

        # Apply borders around card
        border = get_thin_border(BORDER_GREY)
        for r in range(row, row + 2):
            for col_idx in range(openpyxl.utils.column_index_from_string(start_col), openpyxl.utils.column_index_from_string(end_col) + 1):
                ws.cell(row=r, column=col_idx).border = border

    # Row 5-6: Occupancy & Student KPIs
    create_kpi_card("A", "B", 5, "Total Students", tot_students, INTEGER_FORMAT, NAVY_PRIMARY)
    create_kpi_card("C", "D", 5, "Total Rooms", tot_rooms, INTEGER_FORMAT, NAVY_PRIMARY)
    create_kpi_card("E", "F", 5, "Total Capacity", tot_cap, INTEGER_FORMAT, ROYAL_BLUE)
    create_kpi_card("G", "H", 5, "Occupied Beds", tot_occ, INTEGER_FORMAT, ROYAL_BLUE)
    create_kpi_card("I", "J", 5, "Available Beds", tot_vac, INTEGER_FORMAT, GOLD_ACCENT)
    create_kpi_card("K", "L", 5, "Occupancy Rate", occ_rate, PERCENT_FORMAT, TEAL_ACCENT)
    create_kpi_card("M", "N", 5, "Fully Paid Students", fully_paid, INTEGER_FORMAT, TEAL_ACCENT)

    # Row 8-9: Financial KPIs
    create_kpi_card("A", "B", 8, "Hostel Billed", tot_h_fee, CURRENCY_FORMAT, ROYAL_BLUE)
    create_kpi_card("C", "D", 8, "Hostel Collected", tot_h_paid, CURRENCY_FORMAT, TEAL_ACCENT)
    create_kpi_card("E", "F", 8, "Hostel Pending", tot_h_pend, CURRENCY_FORMAT, "E11D48")
    create_kpi_card("G", "H", 8, "Mess Billed", tot_m_fee, CURRENCY_FORMAT, ROYAL_BLUE)
    create_kpi_card("I", "J", 8, "Mess Collected", tot_m_paid, CURRENCY_FORMAT, TEAL_ACCENT)
    create_kpi_card("K", "L", 8, "Mess Pending", tot_m_pend, CURRENCY_FORMAT, "E11D48")
    create_kpi_card("M", "N", 8, "Students with Dues", pending_students, INTEGER_FORMAT, "E11D48")

    ws.row_dimensions[5].height = 18
    ws.row_dimensions[6].height = 28
    ws.row_dimensions[8].height = 18
    ws.row_dimensions[9].height = 28

    # 3. Reference Tables for Native Charts (Placed neatly below in rows 38+)
    # Table 1: Occupancy Summary (A40:B42)
    ws["A40"] = "Metric"
    ws["B40"] = "Beds"
    ws["A41"] = "Occupied Beds"
    ws["B41"] = tot_occ
    ws["A42"] = "Vacant Beds"
    ws["B42"] = tot_vac

    # Table 2: Fee Status Breakdown (D40:E42)
    ws["D40"] = "Fee Category"
    ws["E40"] = "Amount (₹)"
    ws["D41"] = "Fees Collected"
    ws["E41"] = tot_h_paid + tot_m_paid
    ws["D42"] = "Outstanding Dues"
    ws["E42"] = tot_h_pend + tot_m_pend

    # Table 3: Hostel vs Mess Financials (G40:I43)
    ws["G40"] = "Type"
    ws["H40"] = "Hostel (₹)"
    ws["I40"] = "Mess (₹)"
    ws["G41"] = "Total Billed"
    ws["H41"] = tot_h_fee
    ws["I41"] = tot_m_fee
    ws["G42"] = "Collected"
    ws["H42"] = tot_h_paid
    ws["I42"] = tot_m_paid
    ws["G43"] = "Pending"
    ws["H43"] = tot_h_pend
    ws["I43"] = tot_m_pend

    # Table 4: Course Breakdown for Chart (K40:L47)
    ws["K40"] = "Course"
    ws["L40"] = "Count"
    course_counts = students_df["Course"].value_counts() if not students_df.empty else pd.Series(dtype=int)
    for c_idx, (c_name, c_cnt) in enumerate(course_counts.items(), start=41):
        ws[f"K{c_idx}"] = str(c_name)
        ws[f"L{c_idx}"] = int(c_cnt)
    c_last_row = 40 + len(course_counts) if len(course_counts) > 0 else 41

    # Format numbers in the reference tables
    for r in range(40, 44):
        ws[f"E{r}"].number_format = CURRENCY_FORMAT
        ws[f"H{r}"].number_format = CURRENCY_FORMAT
        ws[f"I{r}"].number_format = CURRENCY_FORMAT

    # 4. Create Native Charts on Dashboard

    # Chart 1: Room Occupancy Bar Chart (Placed at A12)
    chart1 = BarChart()
    chart1.type = "col"
    chart1.style = 10
    chart1.title = "Room Bed Allocation"
    chart1.y_axis.title = "Number of Beds"
    chart1.x_axis.title = "Occupancy Status"
    data1 = Reference(ws, min_col=2, min_row=40, max_row=42)
    cats1 = Reference(ws, min_col=1, min_row=41, max_row=42)
    chart1.add_data(data1, titles_from_data=True)
    chart1.set_categories(cats1)
    chart1.width = 13
    chart1.height = 8.5
    ws.add_chart(chart1, "A12")

    # Chart 2: Fee Collection Doughnut Chart (Placed at G12)
    chart2 = PieChart()
    chart2.holeSize = 50
    chart2.title = "Fee Collection vs Dues"
    data2 = Reference(ws, min_col=5, min_row=40, max_row=42)
    cats2 = Reference(ws, min_col=4, min_row=41, max_row=42)
    chart2.add_data(data2, titles_from_data=True)
    chart2.set_categories(cats2)
    chart2.width = 13
    chart2.height = 8.5
    ws.add_chart(chart2, "G12")

    # Chart 3: Hostel vs Mess Financial Comparison (Placed at A26)
    chart3 = BarChart()
    chart3.type = "col"
    chart3.grouping = "clustered"
    chart3.title = "Hostel vs Mess Financial Performance"
    chart3.y_axis.title = "Amount in ₹"
    data3 = Reference(ws, min_col=8, max_col=9, min_row=40, max_row=43)
    cats3 = Reference(ws, min_col=7, min_row=41, max_row=43)
    chart3.add_data(data3, titles_from_data=True)
    chart3.set_categories(cats3)
    chart3.width = 13
    chart3.height = 8.5
    ws.add_chart(chart3, "A26")

    # Chart 4: Course-wise Student Distribution (Placed at G26)
    chart4 = BarChart()
    chart4.type = "bar"
    chart4.title = "Course Enrollment Distribution"
    chart4.x_axis.title = "Students"
    data4 = Reference(ws, min_col=12, min_row=40, max_row=c_last_row)
    cats4 = Reference(ws, min_col=11, min_row=41, max_row=c_last_row)
    chart4.add_data(data4, titles_from_data=True)
    chart4.set_categories(cats4)
    chart4.width = 13
    chart4.height = 8.5
    ws.add_chart(chart4, "G26")

    auto_fit_columns(ws, min_width=14)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# SHEET 2: STUDENT DIRECTORY
# =====================================================================
def build_student_directory_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 2: Student Directory with dark blue header, auto-filter,
    alternating row fills, and frozen header row.
    """
    ws = wb.create_sheet(title="STUDENT DIRECTORY")
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"

    headers = ["Student ID", "Name", "Gender", "Course", "Academic Year", "Room Number", "Contact Number"]
    for col_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=1, column=col_idx), h)
    ws.row_dimensions[1].height = 26

    students_df = data_mgr.load_students_df()
    border = get_thin_border()

    for r_idx, row in enumerate(students_df.itertuples(), start=2):
        bg = CARD_BG if r_idx % 2 == 0 else LIGHT_BG
        fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")

        vals = [
            (str(row.Student_ID), "center"),
            (str(row.Name), "left"),
            (str(row.Gender), "center"),
            (str(row.Course), "left"),
            (int(row.Year), "center"),
            (f"Room {row.Room_No}" if str(row.Room_No).strip() else "Unassigned", "center"),
            (str(row.Contact), "center"),
        ]

        for c_idx, (v, align) in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=v)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.fill = fill
            cell.alignment = Alignment(horizontal=align, vertical="center")
            cell.border = border

        ws.row_dimensions[r_idx].height = 20

    max_row = max(len(students_df) + 1, 2)
    ws.auto_filter.ref = f"A1:G{max_row}"
    auto_fit_columns(ws, min_width=14)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# SHEET 3: ROOM ALLOCATION
# =====================================================================
def build_room_allocation_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 3: Room Allocation with capacity, occupancy percentage,
    conditional formatting (Green: Available, Yellow: Partial, Red: Full),
    and an Openpyxl chart of Occupied vs Vacant beds.
    """
    ws = wb.create_sheet(title="ROOM ALLOCATION")
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"

    headers = ["Room Number", "Floor", "Room Type", "Capacity", "Occupied Beds", "Vacant Beds", "Occupancy %"]
    for col_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=1, column=col_idx), h)
    ws.row_dimensions[1].height = 26

    rooms_df = data_mgr.load_rooms_df()
    border = get_thin_border()

    for r_idx, row in enumerate(rooms_df.itertuples(), start=2):
        bg = CARD_BG if r_idx % 2 == 0 else LIGHT_BG
        fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")

        cap = int(row.Capacity)
        occ = int(row.Occupied)
        vac = int(row.Vacancy)
        occ_rate = occ / cap if cap > 0 else 0.0

        vals = [
            (f"Room {row.Room_No}", "center", None),
            (int(row.Floor), "center", INTEGER_FORMAT),
            (str(row.Room_Type), "left", None),
            (cap, "center", INTEGER_FORMAT),
            (occ, "center", INTEGER_FORMAT),
            (vac, "center", INTEGER_FORMAT),
            (occ_rate, "center", PERCENT_FORMAT),
        ]

        for c_idx, (v, align, n_fmt) in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=v)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.fill = fill
            cell.alignment = Alignment(horizontal=align, vertical="center")
            cell.border = border
            if n_fmt:
                cell.number_format = n_fmt

        ws.row_dimensions[r_idx].height = 20

    max_row = max(len(rooms_df) + 1, 2)
    ws.auto_filter.ref = f"A1:G{max_row}"

    # Conditional formatting on Vacant Beds (Column F):
    # Red for 0 vacancies (Full room)
    red_fill = PatternFill(start_color=RED_FILL, end_color=RED_FILL, fill_type="solid")
    red_font = Font(color=RED_TEXT, bold=True)
    ws.conditional_formatting.add(
        f"F2:F{max_row}",
        CellIsRule(operator="equal", formula=["0"], stopIfTrue=True, fill=red_fill, font=red_font)
    )

    # Green for Available rooms (Vacancy >= 1)
    green_fill = PatternFill(start_color=GREEN_FILL, end_color=GREEN_FILL, fill_type="solid")
    green_font = Font(color=GREEN_TEXT, bold=True)
    ws.conditional_formatting.add(
        f"F2:F{max_row}",
        CellIsRule(operator="greaterThan", formula=["0"], stopIfTrue=True, fill=green_fill, font=green_font)
    )

    # Native Excel Chart: Room Occupied vs Vacant by Room Type (aggregated on side)
    agg_df = rooms_df.groupby("Room_Type").agg(Total_Occupied=("Occupied", "sum"), Total_Vacant=("Vacancy", "sum")).reset_index()
    ref_start_row = 2
    ws["I1"] = "Room Type"
    ws["J1"] = "Occupied"
    ws["K1"] = "Vacant"
    apply_header_style(ws["I1"], "Room Type", ROYAL_BLUE)
    apply_header_style(ws["J1"], "Occupied", ROYAL_BLUE)
    apply_header_style(ws["K1"], "Vacant", ROYAL_BLUE)

    for idx, row in enumerate(agg_df.itertuples(), start=ref_start_row):
        ws[f"I{idx}"] = str(row.Room_Type)
        ws[f"J{idx}"] = int(row.Total_Occupied)
        ws[f"K{idx}"] = int(row.Total_Vacant)

    chart = BarChart()
    chart.type = "col"
    chart.grouping = "stacked"
    chart.title = "Bed Occupancy by Room Type"
    chart.y_axis.title = "Beds"
    data = Reference(ws, min_col=10, max_col=11, min_row=1, max_row=ref_start_row + len(agg_df) - 1)
    cats = Reference(ws, min_col=9, min_row=2, max_row=ref_start_row + len(agg_df) - 1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.width = 14
    chart.height = 9
    ws.add_chart(chart, "I8")

    auto_fit_columns(ws, min_width=14)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# SHEET 4: FEE MANAGEMENT
# =====================================================================
def build_fee_management_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 4: Fee Management with Indian currency formatting,
    pending balance calculations, and color-coded conditional formatting
    for statuses (PAID, PARTIAL, PENDING, OVERDUE).
    """
    ws = wb.create_sheet(title="FEE MANAGEMENT")
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"

    headers = [
        "Student ID", "Student Name", "Hostel Fee", "Hostel Paid", "Hostel Pending", "Hostel Status",
        "Mess Fee", "Mess Paid", "Mess Pending", "Mess Status", "Due Date"
    ]
    for col_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=1, column=col_idx), h)
    ws.row_dimensions[1].height = 26

    students_df = data_mgr.load_students_df()
    fees_df = data_mgr.load_fees_df()
    merged = pd.merge(fees_df, students_df[["Student_ID", "Name"]], on="Student_ID", how="left")

    today = datetime.datetime.now().date()
    border = get_thin_border()

    for r_idx, row in enumerate(merged.itertuples(), start=2):
        bg = CARD_BG if r_idx % 2 == 0 else LIGHT_BG
        fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")

        h_fee = float(row.Hostel_Fee)
        h_paid = float(row.Hostel_Paid)
        h_pend = max(0.0, h_fee - h_paid)

        m_fee = float(row.Mess_Fee)
        m_paid = float(row.Mess_Paid)
        m_pend = max(0.0, m_fee - m_paid)

        # Due date check
        due_str = str(row.Due_Date)
        is_overdue = False
        try:
            due_dt = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
            is_overdue = today > due_dt
        except Exception:
            pass

        # Determine statuses
        def get_stat(fee, paid, pend):
            if pend <= 0:
                return "PAID"
            elif is_overdue:
                return "OVERDUE"
            elif paid > 0:
                return "PARTIAL"
            return "PENDING"

        h_status = get_stat(h_fee, h_paid, h_pend)
        m_status = get_stat(m_fee, m_paid, m_pend)

        vals = [
            (str(row.Student_ID), "center", None),
            (str(row.Name), "left", None),
            (h_fee, "right", CURRENCY_FORMAT),
            (h_paid, "right", CURRENCY_FORMAT),
            (h_pend, "right", CURRENCY_FORMAT),
            (h_status, "center", None),
            (m_fee, "right", CURRENCY_FORMAT),
            (m_paid, "right", CURRENCY_FORMAT),
            (m_pend, "right", CURRENCY_FORMAT),
            (m_status, "center", None),
            (due_str, "center", None),
        ]

        for c_idx, (v, align, n_fmt) in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=v)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.fill = fill
            cell.alignment = Alignment(horizontal=align, vertical="center")
            cell.border = border
            if n_fmt:
                cell.number_format = n_fmt

        ws.row_dimensions[r_idx].height = 20

    max_row = max(len(merged) + 1, 2)
    ws.auto_filter.ref = f"A1:K{max_row}"

    # Conditional formatting on Status columns (F and J):
    rules = [
        ("PAID", GREEN_FILL, GREEN_TEXT),
        ("PARTIAL", YELLOW_FILL, YELLOW_TEXT),
        ("PENDING", ORANGE_FILL, ORANGE_TEXT),
        ("OVERDUE", RED_FILL, RED_TEXT),
    ]

    for status_val, f_color, t_color in rules:
        rule = CellIsRule(
            operator="equal",
            formula=[f'"{status_val}"'],
            stopIfTrue=True,
            fill=PatternFill(start_color=f_color, end_color=f_color, fill_type="solid"),
            font=Font(color=t_color, bold=True)
        )
        ws.conditional_formatting.add(f"F2:F{max_row}", rule)
        ws.conditional_formatting.add(f"J2:J{max_row}", rule)

    auto_fit_columns(ws, min_width=14)
    configure_sheet_page_setup(ws, landscape=True, zoom=95)


# =====================================================================
# SHEET 5: COURSE ANALYSIS
# =====================================================================
def build_course_analysis_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 5: Course Analysis with student counts, average fees,
    realized collections, and an Openpyxl bar chart.
    """
    ws = wb.create_sheet(title="COURSE ANALYSIS")
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"

    headers = [
        "Course", "Enrolled Students", "Average Hostel Fee", "Average Mess Fee",
        "Total Hostel Collection", "Total Mess Collection", "Combined Realization"
    ]
    for col_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=1, column=col_idx), h)
    ws.row_dimensions[1].height = 26

    students_df = data_mgr.load_students_df()
    fees_df = data_mgr.load_fees_df()
    merged = pd.merge(students_df, fees_df, on="Student_ID", how="inner")

    course_grp = merged.groupby("Course").agg(
        Students=("Student_ID", "count"),
        Avg_Hostel=("Hostel_Fee", "mean"),
        Avg_Mess=("Mess_Fee", "mean"),
        Tot_Hostel_Paid=("Hostel_Paid", "sum"),
        Tot_Mess_Paid=("Mess_Paid", "sum"),
    ).reset_index()

    border = get_thin_border()

    for r_idx, row in enumerate(course_grp.itertuples(), start=2):
        bg = CARD_BG if r_idx % 2 == 0 else LIGHT_BG
        fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")

        tot_paid = float(row.Tot_Hostel_Paid) + float(row.Tot_Mess_Paid)

        vals = [
            (str(row.Course), "left", None),
            (int(row.Students), "center", INTEGER_FORMAT),
            (float(row.Avg_Hostel), "right", CURRENCY_FORMAT),
            (float(row.Avg_Mess), "right", CURRENCY_FORMAT),
            (float(row.Tot_Hostel_Paid), "right", CURRENCY_FORMAT),
            (float(row.Tot_Mess_Paid), "right", CURRENCY_FORMAT),
            (tot_paid, "right", CURRENCY_FORMAT),
        ]

        for c_idx, (v, align, n_fmt) in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=v)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.fill = fill
            cell.alignment = Alignment(horizontal=align, vertical="center")
            cell.border = border
            if n_fmt:
                cell.number_format = n_fmt

        ws.row_dimensions[r_idx].height = 20

    max_row = max(len(course_grp) + 1, 2)
    ws.auto_filter.ref = f"A1:G{max_row}"

    # Native Excel Chart: Course-wise student distribution
    chart = BarChart()
    chart.type = "col"
    chart.title = "Student Enrollment by Course"
    chart.y_axis.title = "Students"
    data = Reference(ws, min_col=2, min_row=1, max_row=max_row)
    cats = Reference(ws, min_col=1, min_row=2, max_row=max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.width = 14
    chart.height = 8.5
    ws.add_chart(chart, "I3")

    auto_fit_columns(ws, min_width=15)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# SHEET 6: FINANCIAL SUMMARY
# =====================================================================
def build_financial_summary_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 6: Financial Summary with detailed revenue metrics,
    collection ratios, and key statistics.
    """
    ws = wb.create_sheet(title="FINANCIAL SUMMARY")
    ws.views.sheetView[0].showGridLines = True

    fees_df = data_mgr.load_fees_df()

    h_fee = float(fees_df["Hostel_Fee"].sum()) if not fees_df.empty else 0.0
    h_paid = float(fees_df["Hostel_Paid"].sum()) if not fees_df.empty else 0.0
    h_pend = max(0.0, h_fee - h_paid)

    m_fee = float(fees_df["Mess_Fee"].sum()) if not fees_df.empty else 0.0
    m_paid = float(fees_df["Mess_Paid"].sum()) if not fees_df.empty else 0.0
    m_pend = max(0.0, m_fee - m_paid)

    combined_fee = h_fee + m_fee
    combined_paid = h_paid + m_paid
    combined_pend = h_pend + m_pend
    realization_rate = (combined_paid / combined_fee) if combined_fee > 0 else 0.0

    # Summary Table Headers
    ws.merge_cells("A2:E2")
    t1 = ws["A2"]
    t1.value = "EXECUTIVE FINANCIAL STATEMENT & REVENUE METRICS"
    t1.font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    t1.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    t1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 28

    headers = ["Revenue Component", "Total Billed", "Total Realized", "Outstanding Dues", "Recovery Rate"]
    for c_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=3, column=c_idx), h, ROYAL_BLUE)
    ws.row_dimensions[3].height = 22

    financial_rows = [
        ("Hostel Fees", h_fee, h_paid, h_pend, (h_paid / h_fee) if h_fee > 0 else 0.0),
        ("Mess Fees", m_fee, m_paid, m_pend, (m_paid / m_fee) if m_fee > 0 else 0.0),
        ("Combined Total", combined_fee, combined_paid, combined_pend, realization_rate),
    ]

    border = get_thin_border()
    for r_idx, (cat, b, p, d, r) in enumerate(financial_rows, start=4):
        is_total = (cat == "Combined Total")
        f_font = Font(name="Calibri", size=10.5, bold=is_total, color=DARK_TEXT)
        f_fill = PatternFill(start_color=GOLD_ACCENT if is_total else (CARD_BG if r_idx % 2 == 0 else LIGHT_BG),
                             end_color=GOLD_ACCENT if is_total else (CARD_BG if r_idx % 2 == 0 else LIGHT_BG),
                             fill_type="solid")

        cells_data = [
            (cat, "left", None),
            (b, "right", CURRENCY_FORMAT),
            (p, "right", CURRENCY_FORMAT),
            (d, "right", CURRENCY_FORMAT),
            (r, "center", PERCENT_FORMAT),
        ]
        for c_idx, (val, align, nfmt) in enumerate(cells_data, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = f_font
            cell.fill = f_fill
            cell.alignment = Alignment(horizontal=align, vertical="center")
            cell.border = border
            if nfmt:
                cell.number_format = nfmt
        ws.row_dimensions[r_idx].height = 22

    # Section 2: Payment Distribution Statistics (Rows 9-16)
    ws.merge_cells("A8:C8")
    t2 = ws["A8"]
    t2.value = "STUDENT PAYMENT STATISTICS"
    t2.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    t2.fill = PatternFill(start_color=TEAL_ACCENT, end_color=TEAL_ACCENT, fill_type="solid")
    t2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[8].height = 22

    apply_header_style(ws["A9"], "Statistic Indicator", NAVY_PRIMARY)
    apply_header_style(ws["B9"], "Value", NAVY_PRIMARY)
    apply_header_style(ws["C9"], "Unit / Format", NAVY_PRIMARY)

    stats_data = [
        ("Average Fee per Student", combined_fee / len(fees_df) if len(fees_df) > 0 else 0.0, CURRENCY_FORMAT),
        ("Average Realization per Student", combined_paid / len(fees_df) if len(fees_df) > 0 else 0.0, CURRENCY_FORMAT),
        ("Highest Individual Payment", float((fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]).max()) if not fees_df.empty else 0.0, CURRENCY_FORMAT),
        ("Lowest Individual Payment", float((fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]).min()) if not fees_df.empty else 0.0, CURRENCY_FORMAT),
        ("Standard Deviation of Payments", float((fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]).std()) if not fees_df.empty else 0.0, CURRENCY_FORMAT),
    ]

    for s_idx, (label, s_val, s_fmt) in enumerate(stats_data, start=10):
        c_label = ws.cell(row=s_idx, column=1, value=label)
        c_val = ws.cell(row=s_idx, column=2, value=s_val)
        c_unit = ws.cell(row=s_idx, column=3, value="INR (₹)")
        c_val.number_format = s_fmt
        for c in (c_label, c_val, c_unit):
            c.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            c.border = border
            c.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")
        c_val.alignment = Alignment(horizontal="right", vertical="center")
        c_unit.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[s_idx].height = 20

    # Chart on Financial Summary
    chart = BarChart()
    chart.type = "col"
    chart.title = "Fee Revenue Distribution"
    chart.y_axis.title = "Amount in ₹"
    data = Reference(ws, min_col=2, max_col=4, min_row=3, max_row=5)
    cats = Reference(ws, min_col=1, min_row=4, max_row=5)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.width = 14
    chart.height = 8.5
    ws.add_chart(chart, "G2")

    auto_fit_columns(ws, min_width=18)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# SHEET 7: DATA ANALYSIS
# =====================================================================
def build_data_analysis_sheet(wb: openpyxl.Workbook, data_mgr: DataManager) -> None:
    """
    Build Sheet 7: Data Analysis showing comprehensive Pandas & NumPy
    statistical outputs: Mean, Median, Std Dev, Min, Max, Sum, and group statistics.
    """
    ws = wb.create_sheet(title="DATA ANALYSIS")
    ws.views.sheetView[0].showGridLines = True

    fees_df = data_mgr.load_fees_df()
    rooms_df = data_mgr.load_rooms_df()

    # Section 1: Statistical Description Table
    ws.merge_cells("A2:F2")
    t1 = ws["A2"]
    t1.value = "PARAMETRIC & DESCRIPTIVE STATISTICAL ANALYSIS (NUMPY & PANDAS)"
    t1.font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    t1.fill = PatternFill(start_color=NAVY_PRIMARY, end_color=NAVY_PRIMARY, fill_type="solid")
    t1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 28

    headers = ["Statistical Metric", "Hostel Fee", "Hostel Paid", "Mess Fee", "Mess Paid", "Total Paid"]
    for c_idx, h in enumerate(headers, start=1):
        apply_header_style(ws.cell(row=3, column=c_idx), h, ROYAL_BLUE)
    ws.row_dimensions[3].height = 22

    fees_df["Total_Paid"] = fees_df["Hostel_Paid"] + fees_df["Mess_Paid"]
    cols = ["Hostel_Fee", "Hostel_Paid", "Mess_Fee", "Mess_Paid", "Total_Paid"]

    metrics = [
        ("Mean", lambda c: float(fees_df[c].mean())),
        ("Median", lambda c: float(fees_df[c].median())),
        ("Standard Deviation", lambda c: float(fees_df[c].std())),
        ("Minimum", lambda c: float(fees_df[c].min())),
        ("Maximum", lambda c: float(fees_df[c].max())),
        ("Total Sum", lambda c: float(fees_df[c].sum())),
    ]

    border = get_thin_border()
    for r_idx, (m_name, m_func) in enumerate(metrics, start=4):
        bg = CARD_BG if r_idx % 2 == 0 else LIGHT_BG
        fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")

        c1 = ws.cell(row=r_idx, column=1, value=m_name)
        c1.font = Font(name="Calibri", size=10, bold=True, color=DARK_TEXT)
        c1.fill = fill
        c1.alignment = Alignment(horizontal="left", vertical="center")
        c1.border = border

        for c_idx, col_name in enumerate(cols, start=2):
            val = m_func(col_name) if not fees_df.empty else 0.0
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.fill = fill
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.border = border
            cell.number_format = CURRENCY_FORMAT

        ws.row_dimensions[r_idx].height = 20

    # Section 2: Room Type Grouping Table (Rows 12+)
    ws.merge_cells("A12:E12")
    t2 = ws["A12"]
    t2.value = "ROOM CONFIGURATION GROUPING (GROUPBY ANALYSIS)"
    t2.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    t2.fill = PatternFill(start_color=TEAL_ACCENT, end_color=TEAL_ACCENT, fill_type="solid")
    t2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[12].height = 24

    r_headers = ["Room Type", "Room Count", "Total Capacity", "Total Occupied", "Occupancy %"]
    for c_idx, h in enumerate(r_headers, start=1):
        apply_header_style(ws.cell(row=13, column=c_idx), h, NAVY_PRIMARY)

    room_grp = rooms_df.groupby("Room_Type").agg(
        Count=("Room_No", "count"),
        Cap=("Capacity", "sum"),
        Occ=("Occupied", "sum"),
    ).reset_index()

    for r_idx, row in enumerate(room_grp.itertuples(), start=14):
        cap = int(row.Cap)
        occ = int(row.Occ)
        rate = (occ / cap) if cap > 0 else 0.0

        vals = [
            (str(row.Room_Type), "left", None),
            (int(row.Count), "center", INTEGER_FORMAT),
            (cap, "center", INTEGER_FORMAT),
            (occ, "center", INTEGER_FORMAT),
            (rate, "center", PERCENT_FORMAT),
        ]
        for c_idx, (v, align, nfmt) in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=v)
            cell.font = Font(name="Calibri", size=10, color=DARK_TEXT)
            cell.border = border
            cell.alignment = Alignment(horizontal=align, vertical="center")
            if nfmt:
                cell.number_format = nfmt
        ws.row_dimensions[r_idx].height = 20

    auto_fit_columns(ws, min_width=16)
    configure_sheet_page_setup(ws, landscape=True, zoom=100)


# =====================================================================
# Master Function: Generate Complete Professional Excel Report
# =====================================================================
def export_professional_excel_report(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Generate the professional 7-sheet Excel Workbook using Openpyxl:
      1. EXECUTIVE DASHBOARD (KPI Cards & 4 Charts)
      2. STUDENT DIRECTORY (Filtered, styled table)
      3. ROOM ALLOCATION (Conditional formatting & chart)
      4. FEE MANAGEMENT (INR currency & status formatting)
      5. COURSE ANALYSIS (Course aggregations & chart)
      6. FINANCIAL SUMMARY (Revenue matrix & chart)
      7. DATA ANALYSIS (NumPy & Pandas statistical metrics)
    Returns the absolute path to the generated Excel file.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_file = Path(data_mgr.reports_dir) / "Hostel_Management_Professional_Report.xlsx"
    else:
        output_file = Path(output_path)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Initialize blank workbook
    wb = openpyxl.Workbook()
    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    # Build all 7 worksheets
    build_executive_dashboard(wb, data_mgr)
    build_student_directory_sheet(wb, data_mgr)
    build_room_allocation_sheet(wb, data_mgr)
    build_fee_management_sheet(wb, data_mgr)
    build_course_analysis_sheet(wb, data_mgr)
    build_financial_summary_sheet(wb, data_mgr)
    build_data_analysis_sheet(wb, data_mgr)

    # Safe atomic save to avoid corruption or permission errors
    temp_file = output_file.with_suffix(".tmp.xlsx")
    try:
        wb.save(temp_file)
        temp_file.replace(output_file)
    except PermissionError as pe:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        raise PermissionError(
            f"Cannot write to '{output_file.name}'. Please close the file if it is currently open in Excel and try again."
        ) from pe
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        raise IOError(f"Failed to export Excel report: {e}") from e

    return str(output_file.resolve())


if __name__ == "__main__":
    mgr = DataManager()
    path = export_professional_excel_report(mgr)
    print(f"Professional Excel Workbook generated successfully at: {path}")
