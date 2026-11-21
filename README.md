# HOSTEL ROOM ALLOCATION AND FEE MANAGEMENT SYSTEM
## Advanced Python Terminal Application with Matplotlib Visualizations & Professional Excel Dashboard

A comprehensive, modular, menu-driven Python application developed for academic demonstration (B.Tech Computer Science and Engineering). The system automates student registration, room allocations, hostel and mess fee collections, room occupancy tracking, and provides advanced numerical, statistical, visual, and spreadsheet analytics using **NumPy**, **Pandas**, **Matplotlib**, and **Openpyxl**.

---

## 1. Project Overview

Managing hostel infrastructure manually leads to errors such as room over-allocation, fee calculation discrepancies, untracked payment defaults, and inconsistent occupancy reporting. 

The **Hostel Room Allocation and Fee Management System** provides an automated, terminal-driven solution built entirely in Python. It enforces data integrity across multiple relational CSV datasets, applies ACID-like transactional rollback mechanisms during file modifications, generates high-resolution Matplotlib graphical analytics, and exports a publication-grade, 7-worksheet Excel Dashboard workbook.

---

## 2. Project Objectives

1. **Student Record Management**: Complete CRUD operations with strict field validation (contact format, academic year, unique student IDs).
2. **Room Allocation & Capacity Control**: Dynamic room allocation, vacancy tracking, and student reassignment preventing over-allocation.
3. **Independent Fee Tracking**: Independent tracking of Hostel and Mess fees, supporting `PAID`, `PARTIAL`, `PENDING`, and `OVERDUE` status detection.
4. **Data Integrity & Persistence**: Relational consistency between `students.csv`, `rooms.csv`, and `fees.csv` with safe atomic writes.
5. **Numerical Analysis with NumPy**: Fast vectorized computations on fee matrices, pending balances, and occupancy arrays.
6. **Dataset Processing with Pandas**: Advanced slicing, filtering, sorting, course/room GroupBy aggregations, and missing-value handling.
7. **Professional Visual Analytics**: 5 publication-ready Matplotlib charts saved at 300 DPI in `reports/graphs/`.
8. **Executive Excel Dashboard**: A multi-sheet business intelligence workbook created with Openpyxl containing KPI cards, native Excel charts, auto-filters, and conditional formatting.
9. **Automated Verification**: End-to-end unit and integration test coverage using Python's standard `unittest` framework (53 automated tests).

---

## 3. Key Features

- **Menu-Driven CLI Interface**: 15 top-level menu options with intuitive submenus, formatted ASCII tables, and Indian Rupee (₹) currency formatting.
- **Transactional File Safety**: Temporary backup and automatic rollback prevents half-written or corrupted CSV datasets in the event of an unexpected runtime failure.
- **Dynamic Occupancy Synchronization**: Automatic recalculation of occupied beds and vacancies directly against active student assignments.
- **Comprehensive Overdue Auditing**: Automatic comparison against due dates to flag overdue student accounts.
- **One-Click Analytical Reports**: Automated generation and export of executive summaries, defaulter lists, and course breakdown CSVs.
- **Visual Analytics Suite (Matplotlib)**: Dynamic charts for room occupancy, fee collections, mess comparisons, course distributions, and payment histograms.
- **Executive Excel Dashboard (Openpyxl)**: 7 distinct worksheets with KPI metric cards, conditional formatting rules, and native Excel charts.

---

## 4. Technologies Used

- **Python 3.12+**: Core programming language.
- **NumPy (>= 1.24.0)**: 1D/2D array operations, matrix slicing, and statistical functions (`sum`, `mean`, `max`, `min`, `std`).
- **Pandas (>= 2.0.0)**: Tabular data processing, DataFrame manipulation, boolean filtering, multi-key GroupBy aggregations, and missing-value imputation.
- **Matplotlib (>= 3.7.0)**: High-resolution (300 DPI) data visualizations using the object-oriented API and Agg headless backend.
- **Openpyxl (>= 3.1.0)**: Advanced Excel workbook generation with KPI cards, native charts, auto-filters, and conditional formatting.
- **Tabulate (>= 0.9.0)**: Terminal table formatting (with automatic fallback formatter).
- **unittest**: Comprehensive automated testing framework.
- **Pathlib**: Robust, cross-platform filesystem path resolution.

---

## 5. Python Data Structures Implementation

The application explicitly demonstrates and integrates core Python data structures:

1. **Lists (`list`)**:
   - Stores ordered collections of student dictionaries, active room numbers, and exported report file paths.
   - *List Methods*: `append()` (registering students), `remove()` (deleting student records), `sort()` (sorting records by ID or name).
2. **Tuples (`tuple`)**:
   - Fixed, immutable room configuration profiles:
     ```python
     ROOM_TYPE_CONFIGS: Tuple[Tuple[str, int, float], ...] = (
         ("Single", 1, 55000.0),
         ("Double", 2, 40000.0),
         ("Triple", 3, 30000.0),
         ("Four-Bed", 4, 22000.0),
     )
     ```
   - Immutable validation sets for genders `("Male", "Female", "Other")` and valid academic years `(1, 2, 3, 4, 5)`.
3. **Sets (`set`)**:
   - Fast $O(1)$ membership checks for unique Student IDs preventing duplicates.
   - Set difference operations to identify vacant rooms and unallocated students (`all_rooms - occupied_rooms`).
   - Extracting unique academic courses and room types.
4. **Dictionaries (`dict`)**:
   - Key-value representation of entity records (students, rooms, fee statements).
   - Fast index lookup maps: `{student_id: student_record}`.
   - *Dictionary Methods*: `get()` (safe field retrieval with defaults), `update()` (updating mutable student attributes), `keys()`, `values()`, and `items()`.

---

## 6. NumPy Implementation

NumPy is utilized directly on actual dataset records extracted from `fees.csv` and `rooms.csv`:

1. **1D NumPy Arrays**:
   - Fee vectors: `hostel_fees_1d`, `hostel_paid_1d`, `mess_fees_1d`, `mess_paid_1d`.
   - Vectorized pending calculations: `np.maximum(0.0, hostel_fees_1d - hostel_paid_1d)`.
   - Room vectors: `room_capacities_1d`, `room_occupied_1d`, `room_vacancy_1d`.
2. **2D NumPy Arrays**:
   - 2D Fee Matrix with shape `(N, 4)`: `[Hostel_Fee, Hostel_Paid, Mess_Fee, Mess_Paid]`.
   - 2D Room Occupancy Matrix with shape `(M, 3)`: `[Capacity, Occupied, Vacancy]`.
3. **Array Indexing**:
   - Direct scalar retrieval: e.g. `fee_matrix_2d[0, 0]` (First student's hostel fee), `fee_matrix_2d[0, 3]` (First student's mess payment).
4. **Array Slicing**:
   - Extracting sub-matrices: `fee_matrix_2d[:5, :2]` (First 5 students' hostel fee and paid amounts).
5. **Statistical Calculations**:
   - `np.sum()`: Total fees billed, total fees collected, total outstanding balances.
   - `np.mean()`: Average hostel fee, average mess fee, average student payment.
   - `np.max()` & `np.min()`: Maximum and minimum student fee payments.
   - `np.std()`: Standard deviation of fee collections demonstrating payment distribution variance.

---

## 7. Pandas Implementation

Pandas handles tabular dataset transformations, aggregation, and reporting:

1. **DataFrame Creation & CSV Reading**: `pd.read_csv()` with explicit column typing and missing value guards.
2. **Head & Tail Inspections**: `df.head(5)` and `df.tail(5)` for inspectable data samples.
3. **Column & Row Selection**: Projection of selected attributes (`Student_ID`, `Name`, `Course`, `Room_No`).
4. **Data Filtering**:
   - Boolean indexing for pending dues: `fees_df[fees_df['Hostel_Pending'] > 0]`.
   - Identification of overdue students whose `Due_Date < Today`.
5. **Sorting**: `sort_values(by="Total_Paid", ascending=False)` to rank fee collections.
6. **GroupBy Aggregations**:
   - Course-level enrollment and collection rate: `students_df.groupby("Course")`.
   - Room-type capacity vs occupancy: `rooms_df.groupby("Room_Type")[["Capacity", "Occupied", "Vacancy"]].sum()`.
   - Floor-level occupancy distribution: `rooms_df.groupby("Floor")`.
7. **Missing-Value Handling**:
   - Detection with `isna()`.
   - Imputation with `fillna({"Room_No": "UNASSIGNED", "Contact": "NOT_AVAILABLE"})`.
8. **Statistical Descriptions**: `df.describe()` computed on numerical fee columns.

---

## 8. Professional Visual Analytics (Matplotlib)

The `visualization_module.py` module creates 5 publication-ready, 300 DPI analytical graphs saved in `reports/graphs/`:

### Palette System
- Navy Blue: `#14213D`
- Royal Blue: `#2563EB`
- Teal Accent: `#0F766E`
- Gold / Amber: `#E9B44C`
- Light Background: `#F5F7FA`
- Dark Text: `#1F2937`

### Graph Specifications
1. **Room Occupancy Analysis** (`reports/graphs/room_occupancy.png`):
   - Stacked bar chart showing Occupied Beds (Royal Blue) and Available Beds (Gold) for all rooms.
   - Exact numerical labels inside bars and total capacity indicated above bars.
   - Subtitle displays overall capacity, occupancy percentage, and total available beds.
2. **Fee Collection Donut Chart** (`reports/graphs/fee_collection.png`):
   - Donut chart depicting Realized Collections vs Outstanding Dues.
   - Percentage labels and Rupee amounts on slices.
   - Central hole displays total billed amount, total collected, and total pending.
3. **Hostel vs Mess Fee Comparison** (`reports/graphs/hostel_mess_comparison.png`):
   - Clustered grouped bar chart comparing Total Billed, Realized Collections, and Pending Dues.
   - Value annotations formatted in Indian Rupees (₹) above each bar.
4. **Course-Wise Student Distribution** (`reports/graphs/course_distribution.png`):
   - Horizontal bar chart sorted by enrollment.
   - Percentage share and student counts annotated on each bar.
   - Top-enrolled course highlighted in Gold.
5. **Student Fee Payment Distribution** (`reports/graphs/payment_distribution.png`):
   - Bi-variate histogram analyzing actual payments for Hostel vs Mess fees.
   - Dashed vertical lines indicating mean payments for both categories.

---

## 9. Professional Excel Dashboard (Openpyxl)

The `excel_report_module.py` module generates an executive multi-sheet workbook saved at:
`reports/Hostel_Management_Professional_Report.xlsx`

### Worksheet Architecture
1. **EXECUTIVE DASHBOARD**:
   - Merged title banner with subtitle and report generation timestamp.
   - 14 distinct KPI metric cards with merged borders and color fills:
     * Total Students, Total Rooms, Bed Capacity, Occupied Beds, Available Beds, Occupancy Rate, Fully Paid Students.
     * Hostel Billed, Hostel Collected, Hostel Pending, Mess Billed, Mess Collected, Mess Pending, Students with Dues.
   - 4 Native Excel Charts linked to worksheet reference data:
     * Room Bed Allocation Bar Chart
     * Fee Collection vs Dues Doughnut Chart
     * Hostel vs Mess Performance Clustered Column Chart
     * Course Enrollment Distribution Bar Chart
2. **STUDENT DIRECTORY**:
   - Complete roster of student records with dark navy headers, white bold text, alternating row fills (`#FFFFFF` / `#F5F7FA`), frozen header row, and Excel auto-filter.
3. **ROOM ALLOCATION**:
   - Room-by-room capacity and occupancy data with occupancy rate formulas.
   - Native Excel Bar Chart of bed allocation by room type.
   - Conditional formatting: Red fill for Full rooms (0 vacancies), Green fill for Available rooms.
4. **FEE MANAGEMENT**:
   - Student fee statements with Indian currency formatting (`₹#,##0.00`).
   - Dynamic status calculation (`PAID`, `PARTIAL`, `PENDING`, `OVERDUE`).
   - Conditional formatting: Green for PAID, Yellow for PARTIAL, Orange for PENDING, Red for OVERDUE.
5. **COURSE ANALYSIS**:
   - Course enrollment counts, average hostel/mess fees, and total realized collections.
   - Native Excel Bar Chart displaying student counts per course.
6. **FINANCIAL SUMMARY**:
   - Complete revenue breakdown matrix with recovery rates, payment statistics (average, highest, lowest, standard deviation), and financial chart.
7. **DATA ANALYSIS**:
   - Comprehensive statistical table with Mean, Median, Standard Deviation, Minimum, Maximum, and Sum for all fee columns.
   - GroupBy room-type occupancy table.

---

## 10. Dataset Specifications

The system operates on three persistent CSV files inside the `data/` directory:

### `students.csv`
| Column | Type | Description |
|---|---|---|
| `Student_ID` | String (Primary Key) | Alphanumeric identifier (e.g. `STU1001`) |
| `Name` | String | Full name of student |
| `Gender` | String | Male / Female / Other |
| `Course` | String | Academic program (e.g. B.Tech CSE, MCA) |
| `Year` | Integer | Academic year (1 to 5) |
| `Room_No` | String (Foreign Key) | Assigned room number |
| `Contact` | String | 10-digit Indian mobile number |

### `rooms.csv`
| Column | Type | Description |
|---|---|---|
| `Room_No` | String (Primary Key) | Room identifier (e.g. `101`, `204`) |
| `Floor` | Integer | Floor level (1 to 4) |
| `Room_Type` | String | Single, Double, Triple, Four-Bed |
| `Capacity` | Integer | Total beds available |
| `Occupied` | Integer | Current number of allocated occupants |
| `Vacancy` | Integer | Available beds (`Capacity - Occupied`) |

### `fees.csv`
| Column | Type | Description |
|---|---|---|
| `Student_ID` | String (Foreign Key) | Reference to student |
| `Hostel_Fee` | Float | Total semester hostel fee |
| `Hostel_Paid` | Float | Amount paid towards hostel |
| `Mess_Fee` | Float | Total semester mess fee |
| `Mess_Paid` | Float | Amount paid towards mess |
| `Payment_Date`| String | Date of last payment (YYYY-MM-DD) |
| `Due_Date` | String | Deadline for fee payment (YYYY-MM-DD) |

---

## 11. Project Directory Structure

```text
Wifey ka project/
│
├── main.py                     # Main CLI application (15 menu options)
├── student_module.py           # Student CRUD, validation, and fee initialization
├── room_module.py              # Room allocation, reassignment, vacancy tracking
├── fee_module.py               # Hostel/Mess payments, pending fee calculations
├── analysis_module.py          # NumPy numerical & Pandas analytical operations
├── visualization_module.py     # Matplotlib 5-chart high-resolution visual suite
├── excel_report_module.py      # Professional 7-sheet Openpyxl Excel dashboard
├── data_manager.py             # CSV persistence, atomic writes, transactions
├── initialization.py           # Programmatic dataset generator and integrity audit
├── requirements.txt            # Project dependencies
├── README.md                   # Complete academic documentation
├── .gitignore                  # Git ignore rules
│
├── data/                       # Operational persistent CSV datasets
│   ├── students.csv
│   ├── rooms.csv
│   └── fees.csv
│
├── reports/                    # Exported summaries, Excel workbook, and CSV audits
│   ├── Hostel_Management_Professional_Report.xlsx
│   ├── hostel_summary_report_*.txt
│   ├── course_analysis_*.csv
│   ├── room_occupancy_analysis_*.csv
│   ├── defaulters_pending_list_*.csv
│   └── graphs/                 # High-resolution PNG charts (300 DPI)
│       ├── room_occupancy.png
│       ├── fee_collection.png
│       ├── hostel_mess_comparison.png
│       ├── course_distribution.png
│       └── payment_distribution.png
│
└── tests/                      # Automated unittest test suite (53 tests)
    ├── __init__.py
    ├── test_students.py        # Student module unit tests
    ├── test_rooms.py           # Room module unit tests
    ├── test_fees.py            # Fee module unit tests
    ├── test_data_manager.py    # Data manager unit tests
    ├── test_analysis.py        # NumPy/Pandas analysis unit tests
    ├── test_integration.py     # 6 end-to-end integration workflows
    ├── test_visualization.py   # Visual analytics and graph generation tests
    └── test_excel_report.py    # Professional Excel workbook & chart tests
```

---

## 12. Installation Instructions

### Prerequisites
- Python 3.10 or higher installed.

### Setup (Windows PowerShell)

```powershell
# 1. Navigate to the project root directory
cd "c:\Users\devdw\OneDrive\Desktop\Wifey ka project"

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 13. Execution Instructions

### Launch Main Application
```powershell
python main.py
```

### Main Menu Overview
```text
=================================================================
                     HOSTEL MANAGEMENT SYSTEM                    
=================================================================
 1. Student Management
 2. Room Allocation Management
 3. Hostel Fee Management
 4. Mess Fee Management
 5. Display All Student Records
 6. Search Student
 7. Room Vacancy Report
 8. Fee Status Report
 9. Generate Summary Report
10. Data Analysis using NumPy and Pandas
11. Export Reports (Text & CSV)
12. Dataset Integrity Audit
13. Visual Analytics and Graphical Reports
14. Export Professional Excel Dashboard
15. Exit
=================================================================
```

- Select **`13`** to enter the Visual Analytics menu and generate or view all 5 Matplotlib charts.
- Select **`14`** to generate the 7-sheet Professional Excel Dashboard (`Hostel_Management_Professional_Report.xlsx`).

---

## 14. Automated Testing Instructions

Run the complete 53-test automated test suite:

```powershell
python -m unittest discover -s tests -v
```

### Test Suite Summary
- **Original Tests**: 39 test cases (CRUD, rooms, fees, data manager, integration workflows) $\rightarrow$ **100% Passed**.
- **Visualization Tests**: 6 test cases in `test_visualization.py` $\rightarrow$ **100% Passed**.
- **Excel Report Tests**: 8 test cases in `test_excel_report.py` $\rightarrow$ **100% Passed**.
- **Total Tests**: **53 tests**, 0 failures, 0 errors.
- **Isolation Guarantee**: All tests execute inside temporary directories (`tempfile.mkdtemp()`); operational data in `data/` remains completely untouched.

---

## 15. Future Scope

1. **Biometric Curfew Logging**: Integration with RFID/biometric turnstile logs.
2. **Automated Email Fee Invoices**: Auto-dispatching PDF receipts and payment reminders via SMTP.
3. **Student Grievance Ticketing**: Maintenance request workflow for hostel repairs.
4. **Web Portal Integration**: Optional FastAPI REST interface for mobile clients.
