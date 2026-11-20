# HOSTEL ROOM ALLOCATION AND FEE MANAGEMENT SYSTEM

A comprehensive, modular, menu-driven Python application developed for academic demonstration (B.Tech Computer Science and Engineering). The system automates student registration, room allocations, hostel and mess fee collections, room occupancy tracking, and provides advanced numerical and statistical data analysis using **NumPy** and **Pandas**.

---

## 1. Project Overview

Managing hostel infrastructure manually leads to errors such as room over-allocation, fee calculation discrepancies, untracked payment defaults, and inconsistent occupancy reporting. 

The **Hostel Room Allocation and Fee Management System** provides an automated, terminal-driven solution built entirely in Python. It enforces data integrity across multiple relational CSV datasets, applies ACID-like transactional rollback mechanisms during file modifications, and performs analytical reporting directly on operational data.

---

## 2. Project Objectives

1. **Student Record Management**: Complete CRUD operations with strict field validation (contact format, academic year, unique student IDs).
2. **Room Allocation & Capacity Control**: Dynamic room allocation, vacancy tracking, and student reassignment preventing over-allocation.
3. **Independent Fee Tracking**: Independent tracking of Hostel and Mess fees, supporting `PAID`, `PARTIAL`, `PENDING`, and `OVERDUE` status detection.
4. **Data Integrity & Persistence**: Relational consistency between `students.csv`, `rooms.csv`, and `fees.csv` with safe atomic writes.
5. **Numerical Analysis with NumPy**: Fast vectorized computations on fee matrices, pending balances, and occupancy arrays.
6. **Dataset Processing with Pandas**: Advanced slicing, filtering, sorting, course/room GroupBy aggregations, and missing-value handling.
7. **Automated Verification**: End-to-end unit and integration test coverage using Python's standard `unittest` framework.

---

## 3. Key Features

- **Menu-Driven CLI Interface**: 12 top-level menu options with intuitive submenus, formatted ASCII tables, and Indian Rupee (₹) currency formatting.
- **Transactional File Safety**: Temporary backup and automatic rollback prevents half-written or corrupted CSV datasets in the event of an unexpected runtime failure.
- **Dynamic Occupancy Synchronization**: Automatic recalculation of occupied beds and vacancies directly against active student assignments.
- **Comprehensive Overdue Auditing**: Automatic comparison against due dates to flag overdue student accounts.
- **One-Click Analytical Reports**: Automated generation and export of executive summaries, defaulter lists, and course breakdown CSVs.

---

## 4. Technologies Used

- **Python 3.12+**: Core programming language.
- **NumPy (>= 1.24.0)**: 1D/2D array operations, matrix slicing, and statistical functions (`sum`, `mean`, `max`, `min`, `std`).
- **Pandas (>= 2.0.0)**: Tabular data processing, DataFrame manipulation, boolean filtering, multi-key GroupBy aggregations, and missing-value imputation.
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

---

## 8. Dataset Specifications

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

*The initial dataset includes **100 realistic student records**, **46 rooms** across 4 floors, and **100 fee records** with varied payment states (40% Paid, 30% Partial, 15% Pending, 15% Overdue).*

---

## 9. Project Directory Structure

```text
Wifey ka project/
│
├── main.py                     # Main CLI application and menu loop
├── student_module.py           # Student CRUD, validation, and fee initialization
├── room_module.py              # Room allocation, reassignment, vacancy tracking
├── fee_module.py               # Hostel/Mess payments, pending fee calculations
├── analysis_module.py          # NumPy numerical & Pandas analytical operations
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
├── reports/                    # Exported summaries and CSV analytical audits
│   ├── hostel_summary_report_*.txt
│   ├── course_analysis_*.csv
│   ├── room_occupancy_analysis_*.csv
│   └── defaulters_pending_list_*.csv
│
└── tests/                      # Automated unittest test suite
    ├── __init__.py
    ├── test_students.py        # Student module unit tests
    ├── test_rooms.py           # Room module unit tests
    ├── test_fees.py            # Fee module unit tests
    ├── test_data_manager.py    # Data manager unit tests
    ├── test_analysis.py        # NumPy/Pandas analysis unit tests
    └── test_integration.py     # 6 end-to-end integration workflows
```

---

## 10. Module Responsibilities

1. **`main.py`**:
   - User interface controller, input loops, submenus, and formatted table presentations.
2. **`student_module.py`**:
   - Registration, search by ID/Name, updates, and cascading deletion.
3. **`room_module.py`**:
   - Room allocations, capacity validation, room reassignment, and bed vacating.
4. **`fee_module.py`**:
   - Hostel and mess payments, payment date recording, status determination (`PAID`, `PARTIAL`, `PENDING`, `OVERDUE`).
5. **`analysis_module.py`**:
   - NumPy 1D/2D array manipulations, statistical calculations, Pandas aggregations (`describe()`, `value_counts()`, `groupby()`), master `analyze_data()` function, summary reporting, and report exports.
6. **`data_manager.py`**:
   - Schema enforcement, atomic temp-file replace, backup/rollback transaction wrapper, and cross-table synchronization.
7. **`initialization.py`**:
   - Realistic dataset generation (100 students, 46 rooms) and foreign key integrity audit.

---

## 11. Installation Instructions

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

## 12. Execution Instructions

Launch the application using:

```powershell
python main.py
```

---

## 13. Automated Testing Instructions

Run the complete automated test suite:

```powershell
python -m unittest discover -s tests -v
```

### Test Isolation Guarantee
All unit and integration tests run inside isolated temporary directories (`tempfile.mkdtemp()`). The production datasets in `data/` are **never touched or modified** during test execution.

---

## 14. Sample Terminal Output

### Main Menu
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
11. Export Reports
12. Exit
=================================================================
Enter choice (1-12):
```

### Executive Summary Report (Option 9)
```text
+-----------------------------------+---------------+
| Metric                            | Value         |
+===================================+===============+
| Total Registered Students         | 100           |
+-----------------------------------+---------------+
| Total Rooms                       | 46            |
+-----------------------------------+---------------+
| Total Room Capacity               | 112           |
+-----------------------------------+---------------+
| Total Occupied Beds               | 100           |
+-----------------------------------+---------------+
| Total Vacant Beds                 | 12            |
+-----------------------------------+---------------+
| Room Occupancy Percentage         | 89.29%        |
+-----------------------------------+---------------+
| Total Hostel Fees                 | ₹3,287,000.00 |
+-----------------------------------+---------------+
| Total Hostel Fees Collected       | ₹2,019,700.00 |
+-----------------------------------+---------------+
| Total Hostel Outstanding Balance  | ₹1,267,300.00 |
+-----------------------------------+---------------+
| Total Mess Fees                   | ₹2,500,000.00 |
+-----------------------------------+---------------+
| Total Mess Fees Collected         | ₹1,460,000.00 |
+-----------------------------------+---------------+
| Total Mess Outstanding Balance    | ₹1,040,000.00 |
+-----------------------------------+---------------+
| Students with Pending Hostel Fees | 60            |
+-----------------------------------+---------------+
| Students with Pending Mess Fees   | 60            |
+-----------------------------------+---------------+
| Fully Paid Students               | 40            |
+-----------------------------------+---------------+
```

### NumPy Numerical Analysis (Option 10 -> 1)
```text
--- 1D ARRAY STATISTICAL CALCULATIONS ---
Total Hostel Fees Billed (np.sum)  : ₹3,287,000.00
Total Hostel Fees Paid (np.sum)    : ₹2,019,700.00
Total Hostel Dues Pending (np.sum) : ₹1,267,300.00
Total Mess Fees Billed (np.sum)    : ₹2,500,000.00
Total Mess Fees Paid (np.sum)      : ₹1,460,000.00
Total Mess Dues Pending (np.sum)   : ₹1,040,000.00
Combined Total Fees Collected      : ₹3,479,700.00
Combined Total Outstanding Dues    : ₹2,307,300.00

Mean Hostel Fee Billed (np.mean)   : ₹32,870.00
Mean Hostel Fee Paid (np.mean)     : ₹20,197.00
Mean Mess Fee Paid (np.mean)       : ₹14,600.00
Mean Total Payment (np.mean)       : ₹34,797.00

Maximum Total Payment (np.max)     : ₹80,000.00
Minimum Total Payment (np.min)     : ₹0.00
Standard Deviation of Paid Fees    : ₹23,986.37

--- 2D ARRAY MATRIX OPERATIONS & SLICING ---
Fee Matrix Shape (N, 4)            : (100, 4)
Room Matrix Shape (M, 3)           : (46, 3)
Indexed [0, 0] (1st Student H-Fee) : ₹55,000.00
Indexed [0, 3] (1st Student M-Paid): ₹25,000.00
2D Slicing Sample [:5, :2] (First 5 students [Hostel_Fee, Hostel_Paid]):
  Student 1: Fee = ₹55,000.00, Paid = ₹55,000.00
  Student 2: Fee = ₹40,000.00, Paid = ₹40,000.00
  Student 3: Fee = ₹55,000.00, Paid = ₹55,000.00
  Student 4: Fee = ₹40,000.00, Paid = ₹40,000.00
  Student 5: Fee = ₹40,000.00, Paid = ₹40,000.00
```

---

## 15. Integration Testing Verification

The project includes 6 end-to-end integration workflows verified in `tests/test_integration.py`:
- **Workflow 1**: Student Registration -> Room Allocation -> Occupancy Verification -> Hostel & Mess Payment -> Summary Report Generation.
- **Workflow 2**: Student Search -> Attribute Updates -> Direct CSV Verification.
- **Workflow 3**: Student Room Reassignment -> Source Room Vacancy Restored -> Target Room Occupancy Increment.
- **Workflow 4**: Cascading Student Deletion -> Bed Vacated -> Associated Fee Record Settled.
- **Workflow 5**: Application Restart -> Persistence Verification across fresh `DataManager` sessions.
- **Workflow 6**: Boundary and Error Handling -> Over-allocation prevention, negative payment rejection, and state rollback.

---

## 16. Future Scope

1. **Biometric & Attendance Integration**: Adding RFID or biometric in-out logging to monitor student curfew timings.
2. **Online Payment Gateway API**: Direct integration with UPI/Razorpay APIs for automated payment receipts.
3. **Student Grievance & Maintenance Ticketing**: A complaint management module for plumbing, electrical, and internet repairs.
4. **Graphical Charts Export**: Generating Matplotlib PNG dashboards for administrative presentations.
