"""
Visualization Module for Hostel Management System.
Generates five professional, publication-grade analytical charts using Matplotlib.
Theme colors:
  - Navy blue:   #14213D
  - Royal blue:  #2563EB
  - Teal:        #0F766E
  - Gold:        #E9B44C
  - Light bg:    #F5F7FA
  - Dark text:   #1F2937
High resolution (300 DPI), clean typography, proper margins, and dynamic data integration.
"""

from __future__ import annotations
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import matplotlib
# Use Agg backend for reliable headless execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from data_manager import DataManager

# Consistent Design System
PALETTE = {
    "navy": "#14213D",
    "royal_blue": "#2563EB",
    "teal": "#0F766E",
    "gold": "#E9B44C",
    "coral": "#E11D48",
    "emerald": "#059669",
    "light_bg": "#F5F7FA",
    "card_bg": "#FFFFFF",
    "dark_text": "#1F2937",
    "muted_text": "#6B7280",
    "grid_line": "#E5E7EB",
}

FONT_FAMILY = "sans-serif"
DPI = 300


def get_default_graphs_dir(data_mgr: Optional[DataManager] = None) -> Path:
    """Return the default graphs directory and ensure it exists."""
    if data_mgr is not None and hasattr(data_mgr, "reports_dir"):
        graphs_dir = Path(data_mgr.reports_dir) / "graphs"
    else:
        graphs_dir = Path(__file__).resolve().parent / "reports" / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    return graphs_dir


def apply_chart_styling(fig: plt.Figure, ax: plt.Axes, title: str, subtitle: Optional[str] = None) -> None:
    """Apply consistent corporate styling to Matplotlib figures and axes."""
    fig.patch.set_facecolor(PALETTE["light_bg"])
    ax.set_facecolor(PALETTE["card_bg"])

    # Spines styling
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid_line"])
        spine.set_linewidth(1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Grid styling
    ax.grid(axis="y", linestyle="--", alpha=0.6, color=PALETTE["grid_line"], zorder=0)

    # Title and subtitle
    if subtitle:
        ax.set_title(f"{title}\n", fontsize=14, fontweight="bold", color=PALETTE["navy"], pad=15, loc="left")
        ax.text(
            0.0, 1.02, subtitle,
            transform=ax.transAxes, fontsize=10, color=PALETTE["muted_text"],
            ha="left", va="bottom"
        )
    else:
        ax.set_title(title, fontsize=14, fontweight="bold", color=PALETTE["navy"], pad=15, loc="left")

    ax.tick_params(colors=PALETTE["dark_text"], labelsize=9.5)


def safe_savefig(fig: plt.Figure, output_path: Path | str, **kwargs) -> None:
    """Save matplotlib figure safely handling transient Windows / OneDrive file locks."""
    target_path = Path(output_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    for attempt in range(6):
        try:
            fig.savefig(str(target_path), **kwargs)
            return
        except OSError as err:
            last_err = err
            time.sleep(0.15 * (attempt + 1))
    if last_err:
        raise last_err


def open_graph_image(file_path: str | Path) -> bool:
    """
    Safely open a generated image using the operating system's default viewer.
    Handles Windows os.startfile gracefully. Returns True if opened, False otherwise.
    """
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        return False
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path_obj))
            return True
        elif sys.platform.startswith("darwin"):
            import subprocess
            subprocess.Popen(["open", str(path_obj)])
            return True
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(path_obj)])
            return True
    except Exception:
        return False


# =====================================================================
# GRAPH 1: Room Occupancy Analysis
# =====================================================================
def plot_room_occupancy(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Graph 1: Room Occupancy Analysis.
    Displays rooms with occupied beds, available beds, and capacity.
    Visually distinguishes occupied and vacant beds with clear numerical labels,
    legend, and readable typography.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_path = get_default_graphs_dir(data_mgr) / "room_occupancy.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    rooms_df = data_mgr.load_rooms_df()

    fig, ax = plt.subplots(figsize=(14, 7), dpi=DPI)

    if rooms_df.empty:
        ax.text(0.5, 0.5, "No Room Data Available", ha="center", va="center", fontsize=14, color=PALETTE["muted_text"])
        apply_chart_styling(fig, ax, "HOSTEL ROOM OCCUPANCY ANALYSIS", "No rooms recorded in database")
        fig.tight_layout()
        safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    # Sort rooms logically by Room_No
    rooms_df = rooms_df.sort_values(by="Room_No").reset_index(drop=True)
    room_labels = [f"R-{r}" for r in rooms_df["Room_No"]]
    occupied = rooms_df["Occupied"].values
    vacancy = rooms_df["Vacancy"].values
    capacity = rooms_df["Capacity"].values

    x = np.arange(len(room_labels))
    width = 0.65

    # Stacked bars: Occupied (Royal Blue) + Vacant (Gold/Teal) = Total Capacity
    p1 = ax.bar(x, occupied, width, label="Occupied Beds", color=PALETTE["royal_blue"], edgecolor="none", zorder=3)
    p2 = ax.bar(x, vacancy, width, bottom=occupied, label="Available Beds", color=PALETTE["gold"], edgecolor="none", zorder=3)

    # Numerical labels inside or above bars
    for idx, (occ, vac, cap) in enumerate(zip(occupied, vacancy, capacity)):
        if occ > 0:
            ax.text(idx, occ / 2, f"{int(occ)}", ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold", zorder=4)
        if vac > 0:
            ax.text(idx, occ + (vac / 2), f"{int(vac)}", ha="center", va="center", color=PALETTE["navy"], fontsize=7.5, fontweight="bold", zorder=4)
        ax.text(idx, cap + 0.15, f"{int(cap)}", ha="center", va="bottom", color=PALETTE["muted_text"], fontsize=7, zorder=4)

    total_cap = int(capacity.sum())
    total_occ = int(occupied.sum())
    total_vac = int(vacancy.sum())
    occ_pct = round((total_occ / total_cap * 100), 1) if total_cap > 0 else 0.0

    subtitle = f"Total Capacity: {total_cap} Beds | Occupied: {total_occ} ({occ_pct}%) | Available: {total_vac} Across {len(rooms_df)} Rooms"
    apply_chart_styling(fig, ax, "HOSTEL ROOM OCCUPANCY ANALYSIS", subtitle)

    ax.set_xlabel("Hostel Room Numbers", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.set_ylabel("Bed Count", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(room_labels, rotation=90, fontsize=7.5)
    ax.set_ylim(0, max(capacity) + 1.2)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    ax.legend(loc="upper right", frameon=True, facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid_line"], fontsize=9)
    fig.tight_layout()
    safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# =====================================================================
# GRAPH 2: Fee Collection Donut Chart
# =====================================================================
def plot_fee_collection(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Graph 2: Fee Collection Donut Chart.
    Shows Total Fees Collected vs Total Outstanding Fees with percentage labels,
    rupee amounts, and a central total-fee figure in the donut center.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_path = get_default_graphs_dir(data_mgr) / "fee_collection.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    fees_df = data_mgr.load_fees_df()

    fig, ax = plt.subplots(figsize=(9, 8), dpi=DPI)
    fig.patch.set_facecolor(PALETTE["light_bg"])

    if fees_df.empty:
        ax.text(0.5, 0.5, "No Fee Data Available", ha="center", va="center", fontsize=14, color=PALETTE["muted_text"])
        ax.set_title("FEE COLLECTION AND OUTSTANDING DUES", fontsize=14, fontweight="bold", color=PALETTE["navy"])
        safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    total_hostel_fee = float(fees_df["Hostel_Fee"].sum())
    total_hostel_paid = float(fees_df["Hostel_Paid"].sum())
    total_mess_fee = float(fees_df["Mess_Fee"].sum())
    total_mess_paid = float(fees_df["Mess_Paid"].sum())

    total_billed = total_hostel_fee + total_mess_fee
    total_collected = total_hostel_paid + total_mess_paid
    total_outstanding = max(0.0, total_billed - total_collected)

    sizes = [total_collected, total_outstanding]
    colors = [PALETTE["teal"], PALETTE["gold"]]
    labels = ["Fees Collected", "Outstanding Dues"]
    explode = (0.02, 0.04)

    # Donut chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=None,
        autopct=lambda pct: f"{pct:.1f}%\n(₹{pct*total_billed/10000000:.2f}M)" if total_billed > 0 else "0%",
        startangle=140,
        colors=colors,
        pctdistance=0.72,
        wedgeprops=dict(width=0.42, edgecolor="#FFFFFF", linewidth=2.5)
    )

    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontsize(10)
        at.set_fontweight("bold")

    # Center circle label
    center_text = f"TOTAL BILLED\n₹{total_billed:,.0f}\n\nCOLLECTED\n₹{total_collected:,.0f}\n\nPENDING\n₹{total_outstanding:,.0f}"
    ax.text(
        0, 0, center_text,
        ha="center", va="center",
        fontsize=9.5, fontweight="bold",
        color=PALETTE["navy"],
        linespacing=1.2
    )

    ax.legend(
        wedges,
        [
            f"Collected: ₹{total_collected:,.2f} ({total_collected/total_billed*100:.1f}%)" if total_billed > 0 else "Collected: ₹0",
            f"Outstanding: ₹{total_outstanding:,.2f} ({total_outstanding/total_billed*100:.1f}%)" if total_billed > 0 else "Outstanding: ₹0",
        ],
        title="Payment Status Breakdown",
        loc="upper right",
        bbox_to_anchor=(1.05, 1.0),
        frameon=True,
        facecolor=PALETTE["card_bg"],
        edgecolor=PALETTE["grid_line"],
        fontsize=9
    )

    ax.set_title(
        "FEE COLLECTION AND OUTSTANDING DUES (DONUT ANALYSIS)\n",
        fontsize=14, fontweight="bold", color=PALETTE["navy"], pad=20
    )
    fig.tight_layout()
    safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# =====================================================================
# GRAPH 3: Hostel vs Mess Fee Comparison
# =====================================================================
def plot_hostel_mess_comparison(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Graph 3: Hostel vs Mess Fee Comparison.
    Grouped bar chart comparing Total Fees, Collected Fees, and Pending Fees
    with Rupee currency formatted labels.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_path = get_default_graphs_dir(data_mgr) / "hostel_mess_comparison.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    fees_df = data_mgr.load_fees_df()

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=DPI)

    if fees_df.empty:
        ax.text(0.5, 0.5, "No Financial Data Available", ha="center", va="center", fontsize=14, color=PALETTE["muted_text"])
        apply_chart_styling(fig, ax, "HOSTEL AND MESS FINANCIAL PERFORMANCE")
        safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    h_total = float(fees_df["Hostel_Fee"].sum())
    h_paid = float(fees_df["Hostel_Paid"].sum())
    h_pending = max(0.0, h_total - h_paid)

    m_total = float(fees_df["Mess_Fee"].sum())
    m_paid = float(fees_df["Mess_Paid"].sum())
    m_pending = max(0.0, m_total - m_paid)

    categories = ["Total Billed", "Collected Fees", "Pending Dues"]
    hostel_vals = [h_total, h_paid, h_pending]
    mess_vals = [m_total, m_paid, m_pending]

    x = np.arange(len(categories))
    width = 0.35

    rects1 = ax.bar(x - width / 2, hostel_vals, width, label="Hostel Fees", color=PALETTE["royal_blue"], edgecolor="none", zorder=3)
    rects2 = ax.bar(x + width / 2, mess_vals, width, label="Mess Fees", color=PALETTE["teal"], edgecolor="none", zorder=3)

    # Add Rupee labels above bars
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(
            f"₹{height:,.0f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 4), textcoords="offset points",
            ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=PALETTE["navy"]
        )

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(
            f"₹{height:,.0f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 4), textcoords="offset points",
            ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=PALETTE["teal"]
        )

    subtitle = "Comparative breakdown of total commitments, realized collections, and outstanding dues"
    apply_chart_styling(fig, ax, "HOSTEL AND MESS FINANCIAL PERFORMANCE", subtitle)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax.set_ylabel("Amount in Indian Rupees (₹)", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"₹{val*1e-5:.1f}L" if val >= 1e5 else f"₹{val:,.0f}"))
    max_val = max(max(hostel_vals), max(mess_vals))
    ax.set_ylim(0, max_val * 1.18)

    ax.legend(loc="upper right", frameon=True, facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid_line"], fontsize=9.5)
    fig.tight_layout()
    safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# =====================================================================
# GRAPH 4: Course-Wise Student Distribution
# =====================================================================
def plot_course_distribution(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Graph 4: Course-Wise Student Distribution.
    Horizontal bar chart showing course enrollment counts, sorted by student count,
    with numerical labels and total student count display.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_path = get_default_graphs_dir(data_mgr) / "course_distribution.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    students_df = data_mgr.load_students_df()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=DPI)

    if students_df.empty:
        ax.text(0.5, 0.5, "No Student Records Available", ha="center", va="center", fontsize=14, color=PALETTE["muted_text"])
        apply_chart_styling(fig, ax, "COURSE-WISE STUDENT DISTRIBUTION")
        safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    course_counts = students_df["Course"].value_counts().sort_values(ascending=True)
    courses = course_counts.index.tolist()
    counts = course_counts.values.tolist()
    total_students = len(students_df)

    y = np.arange(len(courses))
    bars = ax.barh(y, counts, color=PALETTE["royal_blue"], height=0.55, edgecolor="none", zorder=3)

    # Highlight top enrolled course in Gold
    if len(bars) > 0:
        bars[-1].set_color(PALETTE["gold"])

    # Labels on bars
    for idx, (bar, count) in enumerate(zip(bars, counts)):
        pct = (count / total_students) * 100 if total_students > 0 else 0
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{count} students ({pct:.1f}%)",
            va="center", ha="left",
            fontsize=8.5, fontweight="bold",
            color=PALETTE["navy"]
        )

    subtitle = f"Total Registered Students: {total_students} | Highest Enrollment: {courses[-1]} ({counts[-1]} students)"
    apply_chart_styling(fig, ax, "COURSE-WISE STUDENT DISTRIBUTION", subtitle)

    ax.grid(axis="x", linestyle="--", alpha=0.6, color=PALETTE["grid_line"], zorder=0)
    ax.grid(axis="y", visible=False)
    ax.set_yticks(y)
    ax.set_yticklabels(courses, fontsize=9.5, fontweight="bold")
    ax.set_xlabel("Number of Enrolled Students", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.set_xlim(0, max(counts) * 1.25)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.tight_layout()
    safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# =====================================================================
# GRAPH 5: Student Fee Payment Distribution
# =====================================================================
def plot_payment_distribution(data_mgr: Optional[DataManager] = None, output_path: Optional[str | Path] = None) -> str:
    """
    Graph 5: Student Fee Payment Distribution.
    Histogram analyzing the distribution of actual student payments for both
    Hostel and Mess fees, with mean payment markers.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_path is None:
        output_path = get_default_graphs_dir(data_mgr) / "payment_distribution.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    fees_df = data_mgr.load_fees_df()

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=DPI)

    if fees_df.empty:
        ax.text(0.5, 0.5, "No Payment Records Available", ha="center", va="center", fontsize=14, color=PALETTE["muted_text"])
        apply_chart_styling(fig, ax, "STUDENT FEE PAYMENT DISTRIBUTION")
        safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        return str(output_path)

    hostel_paid = fees_df["Hostel_Paid"].values
    mess_paid = fees_df["Mess_Paid"].values

    h_mean = float(np.mean(hostel_paid)) if len(hostel_paid) > 0 else 0.0
    m_mean = float(np.mean(mess_paid)) if len(mess_paid) > 0 else 0.0

    bins = np.linspace(0, max(max(hostel_paid, default=0), max(mess_paid, default=0), 60000), 15)

    ax.hist(hostel_paid, bins=bins, alpha=0.7, color=PALETTE["royal_blue"], label="Hostel Fee Payments", edgecolor="#FFFFFF", zorder=3)
    ax.hist(mess_paid, bins=bins, alpha=0.6, color=PALETTE["teal"], label="Mess Fee Payments", edgecolor="#FFFFFF", zorder=3)

    # Vertical lines for averages
    ax.axvline(h_mean, color=PALETTE["navy"], linestyle="--", linewidth=1.8, label=f"Mean Hostel Paid (₹{h_mean:,.0f})", zorder=4)
    ax.axvline(m_mean, color=PALETTE["gold"], linestyle=":", linewidth=2.0, label=f"Mean Mess Paid (₹{m_mean:,.0f})", zorder=4)

    subtitle = f"Sample Size: {len(fees_df)} Students | Mean Hostel: ₹{h_mean:,.2f} | Mean Mess: ₹{m_mean:,.2f}"
    apply_chart_styling(fig, ax, "STUDENT FEE PAYMENT DISTRIBUTION", subtitle)

    ax.set_xlabel("Payment Amount in Indian Rupees (₹)", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.set_ylabel("Student Frequency", fontsize=10, fontweight="bold", color=PALETTE["navy"], labelpad=8)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"₹{val:,.0f}"))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    ax.legend(loc="upper right", frameon=True, facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid_line"], fontsize=9)
    fig.tight_layout()
    safe_savefig(fig, output_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


# =====================================================================
# Master Function: Generate All Five Graphs
# =====================================================================
def generate_all_graphs(data_mgr: Optional[DataManager] = None, output_dir: Optional[str | Path] = None) -> Dict[str, str]:
    """
    Generate and save all five professional Matplotlib graphs in the specified folder.
    Returns a dictionary mapping chart names to their absolute file paths.
    """
    if data_mgr is None:
        data_mgr = DataManager()

    if output_dir is None:
        graphs_dir = get_default_graphs_dir(data_mgr)
    else:
        graphs_dir = Path(output_dir)
        graphs_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "room_occupancy": plot_room_occupancy(data_mgr, graphs_dir / "room_occupancy.png"),
        "fee_collection": plot_fee_collection(data_mgr, graphs_dir / "fee_collection.png"),
        "hostel_mess_comparison": plot_hostel_mess_comparison(data_mgr, graphs_dir / "hostel_mess_comparison.png"),
        "course_distribution": plot_course_distribution(data_mgr, graphs_dir / "course_distribution.png"),
        "payment_distribution": plot_payment_distribution(data_mgr, graphs_dir / "payment_distribution.png"),
    }

    return results


if __name__ == "__main__":
    mgr = DataManager()
    paths = generate_all_graphs(mgr)
    print("Generated Graphs:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
