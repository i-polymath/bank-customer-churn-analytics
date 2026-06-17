"""
Notes:
- File paths are configurable.
- The transaction loop below is shown as a documentation-style loop:
  it reads each monthly file, performs monthly transforms, and
  accumulates lightweight summaries. For very large datasets, we typically consider
  streaming or chunked processing instead of concatenating full months in memory.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

# -------------------------
# Configurable file paths
# -------------------------
DATA_DIR = Path("data_raw")
CUSTOMER_FILES = [DATA_DIR / "customers_part1.xlsx", DATA_DIR / "customers_part2.xlsx"]
BRANCH_UPDATES_FILE = DATA_DIR / "Updated_Branch_Customers.xlsx"
UNSUCCESSFUL_LOANS_FILE = DATA_DIR / "Unsuccessful_Loans.xlsx"
CHURN_FILE = DATA_DIR / "Churn_deepdive.xlsx"

# Transaction monthly files (Names for Sept 2022 - Mar 2023)
MONTHLY_TX_FILES = [
    DATA_DIR / "transactions_2022_09.csv",
    DATA_DIR / "transactions_2022_10.csv",
    DATA_DIR / "transactions_2022_11.csv",
    DATA_DIR / "transactions_2022_12.csv",
    DATA_DIR / "transactions_2023_01.csv",
    DATA_DIR / "transactions_2023_02.csv",
    DATA_DIR / "transactions_2023_03.csv",
]

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# Helper functions
# -------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip and replace non-alphanumeric characters with underscores."""
    df = df.copy()
    df.columns = [
        "".join(c if c.isalnum() else "_" for c in str(col).strip().lower()).strip("_")
        for col in df.columns
    ]
    return df

def safe_read_excel(path: Path, dtype=None) -> pd.DataFrame:
    """Read an Excel file with a safe fallback."""
    try:
        return pd.read_excel(path, dtype=dtype)
    except Exception as e:
        raise RuntimeError(f"Error reading {path}: {e}")

def safe_read_csv(path: Path, dtype=None) -> pd.DataFrame:
    """Read a CSV file with a safe fallback."""
    try:
        return pd.read_csv(path, dtype=dtype)
    except Exception as e:
        raise RuntimeError(f"Error reading {path}: {e}")

# -------------------------
# Customer profile cleaning
# -------------------------
print("Loading customer files...")
cust_dfs = []
for f in CUSTOMER_FILES:
    df = safe_read_excel(f, dtype=str)
    df = standardize_columns(df)
    cust_dfs.append(df)
customers = pd.concat(cust_dfs, ignore_index=True)

# Quick EDA checks (suitable for demonstrating workflow)
print("\n--- Customer EDA ---")
print("Shape:", customers.shape)
print("Missing per column:\n", customers.isnull().sum().sort_values(ascending=False).head(10))
# Show top values for key columns if present
for col in ["gender", "branch_name", "hin", "id_number"]:
    if col in customers.columns:
        print(f"\nValue counts for {col} (top 5):")
        print(customers[col].value_counts(dropna=False).head(5))

# Replace common "NULL" placeholders and strip whitespace
customers.replace("NULL", pd.NA, inplace=True)
customers = customers.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Standardise identifiers: HIN and ID number (these should 13 digits)
if "id_number" in customers.columns:
    customers["id_number"] = customers["id_number"].astype(str).str.replace(r"\.0+$", "", regex=True).str.zfill(13)

# Check HIN presence and duplicates
if "hin" in customers.columns:
    print("\nHIN length distribution (sample):")
    try:
        print(customers["hin"].astype(str).str.len().value_counts().head())
    except Exception:
        pass
    dup_hin = customers[customers.duplicated(subset="hin", keep=False)]
    if not dup_hin.empty:
        print(f"Found {dup_hin['hin'].nunique()} duplicated HIN values (showing a few):")
        print(dup_hin.head())

# Drop full-empty rows (except keep_cols)
keep_cols = ["hin", "rn"] if "hin" in customers.columns else []
other_cols = [c for c in customers.columns if c not in keep_cols]
customers = customers.dropna(subset=other_cols, how="all")

# Drop duplicate HIN keeping first occurrence
if "hin" in customers.columns:
    customers = customers.drop_duplicates(subset="hin", keep="first")

# -------------------------
# Branch enrichment (generic)
# -------------------------
if BRANCH_UPDATES_FILE.exists():
    print("\nApplying branch updates...")
    branch_updates = safe_read_excel(BRANCH_UPDATES_FILE, dtype=str)
    branch_updates = standardize_columns(branch_updates)
    # keep only the join key and branch fields if available
    cols_to_keep = [c for c in ["hin", "branch_id", "branch_name"] if c in branch_updates.columns]
    branch_updates = branch_updates[cols_to_keep]
    customers = customers.merge(branch_updates, on="hin", how="left", suffixes=("", "_upd"))
    # Replace UNKNOWN or missing branch_name with the update if available
    if "branch_name_upd" in customers.columns:
        customers["branch_name"] = customers.apply(
            lambda r: r["branch_name_upd"] if (pd.isna(r.get("branch_name")) or str(r.get("branch_name")).strip().upper()=="UNKNOWN") and pd.notna(r.get("branch_name_upd")) else r.get("branch_name"),
            axis=1
        )
    if "branch_id_upd" in customers.columns:
        customers["branch_id"] = customers.apply(
            lambda r: r["branch_id_upd"] if pd.isna(r.get("branch_id")) and pd.notna(r.get("branch_id_upd")) else r.get("branch_id"),
            axis=1
        )
    # drop helper cols
    customers = customers[[c for c in customers.columns if not c.endswith("_upd")]]

# -------------------------
# Date conversions & derived features
# -------------------------
print("\nDeriving age and tenure features...")
# Note: input date format expected as YYYYMMDD in this dataset; errors coerced
for col in ["birth_date", "start_date"]:
    if col in customers.columns:
        customers[col] = pd.to_datetime(customers[col], format="%Y%m%d", errors="coerce")

now = pd.to_datetime("now")
if "birth_date" in customers.columns:
    customers["age"] = customers["birth_date"].apply(lambda x: relativedelta(now, x).years if pd.notna(x) else pd.NA)
else:
    customers["age"] = pd.NA

if "start_date" in customers.columns:
    customers["year_joined"] = customers["start_date"].dt.year
    customers["years_joined"] = customers["start_date"].apply(lambda x: relativedelta(now, x).years if pd.notna(x) else pd.NA)
else:
    customers["year_joined"] = pd.NA
    customers["years_joined"] = pd.NA

# Age groups (generic bins)
age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, 100, 200]
age_labels = ["Under 18", "18-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100", "100+"]
# cast to numeric for cut
customers["age_numeric"] = pd.to_numeric(customers["age"], errors="coerce")
customers["age_group"] = pd.cut(customers["age_numeric"], bins=age_bins, labels=age_labels, right=False)

# Recode gender values if they are numeric codes
if "gender" in customers.columns:
    gender_map = {"1": "Male", "2": "Female", 1: "Male", 2: "Female"}
    customers["gender"] = customers["gender"].replace(gender_map).fillna(customers["gender"])

# -------------------------
# Unsuccessful loans aggregation (generic)
# -------------------------
if UNSUCCESSFUL_LOANS_FILE.exists():
    print("\nProcessing unsuccessful loan records...")
    loans = safe_read_excel(UNSUCCESSFUL_LOANS_FILE, dtype=str)
    loans = standardize_columns(loans)
    # rename client_usn -> hin if present
    if "client_usn" in loans.columns:
        loans = loans.rename(columns={"client_usn": "hin"})
    # aggregate counts per customer
    if "hin" in loans.columns:
        loan_summary = loans.groupby("hin").agg(
            loan_status=("hin", lambda s: "Unsuccessful"),
            number_of_times_loan_declined=("hin", "count")
        ).reset_index()
        customers = customers.merge(loan_summary, on="hin", how="left")
    else:
        print("No join key found in loans file; skipping merge.")
else:
    print("Unsuccessful loans file not found; skipping.")

# -------------------------
# Churn merge & conversion
# -------------------------
if CHURN_FILE.exists():
    print("\nMerging churn dataset...")
    churn = safe_read_excel(CHURN_FILE, dtype=str)
    churn = standardize_columns(churn)
    # Use a generic id key name if present
    id_keys = [c for c in churn.columns if "id" in c]
    join_key = None
    if "idnumber" in churn.columns:
        churn = churn.rename(columns={"idnumber": "id_number"})
    if "id_number" in churn.columns:
        join_key = "id_number"
    # dedupe by id_number if present
    if join_key:
        churn = churn.drop_duplicates(subset=join_key, keep="first")
        # pick relevant columns if they exist
        keep_cols = [c for c in ["id_number", "account_status", "role_of_month", "no_of_bursaries", "bursary_description"] if c in churn.columns]
        churn_small = churn[keep_cols]
        # some customer tables may store ID as 'id_number' or 'id number'; attempt to align
        if "id_number" in customers.columns:
            customers = customers.merge(churn_small, on="id_number", how="left")
        elif "id_number" in customers.columns or "id_number" in churn_small.columns:
            customers = customers.merge(churn_small, on="id_number", how="left")
        else:
            # fallback: try to merge on alternative keys if present
            pass

        # Convert yearmonth (e.g., 202209) to readable Month-Year
        if "role_of_month" in customers.columns:
            def to_month_year(val):
                try:
                    if pd.isna(val) or str(val).lower() in ("nan","none"):
                        return pd.NA
                    return pd.to_datetime(str(val), format="%Y%m").strftime("%b-%Y")
                except Exception:
                    return pd.NA
            customers["month_year_of_churn"] = customers["role_of_month"].apply(to_month_year)
else:
    print("Churn file not present; skipping churn merge.")

# -------------------------
# Save cleaned customer base
# -------------------------
CUST_OUTPUT = OUTPUT_DIR / "customer_profile_base.csv"
print(f"\nSaving cleaned customer profile base to {CUST_OUTPUT}")
customers.to_csv(CUST_OUTPUT, index=False)

# -------------------------
# Transactions: monthly processing (documentation-style)
# -------------------------
print("\nProcessing monthly transactions (documentation-style loop)...")
# Approach:
# - For demonstration we will read each month's file, standardize columns, apply tags and a 'customer-initiated' flag,
#   compute per-month customer aggregates and collect summaries. This avoids concatenating all raw months into memory
#   when a true production pipeline would stream or process in batches.
tx_monthly_summaries = []

# Define a generic mapping for transaction description -> tag
txn_mapping = {
    "loan repayment": "loan_repayment",
    "insurance": "insurance",
    "atm": "atm_withdrawal",
    "pos": "pos_purchase",
    "eft": "eft",
    "transfer": "transfer",
    "fee": "fee",
    "deposit": "cash_deposit",
}

# Keywords that indicate the transaction was initiated by the customer (examples)
customer_initiated_keywords = ["pos", "withdrawal", "atm", "transfer", "payment", "deposit"]

for tx_file in MONTHLY_TX_FILES:
    if not tx_file.exists():
        print(f"Month file {tx_file.name} not found; skipping (placeholder for demonstration).")
        continue

    tx = safe_read_csv(tx_file)
    tx = standardize_columns(tx)

    # Basic EDA for the month (print a small sample)
    print(f"\nMonth: {tx_file.name} | rows: {len(tx)}")
    if "description" in tx.columns:
        print("Sample description values:", tx["description"].dropna().astype(str).head(3).tolist())

    # Ensure key columns exist; map possible column names to standard ones
    # Attempt to find customer id in transaction file
    cust_id_col = None
    for candidate in ["hin", "customer_id", "client_id", "account_number", "id_number"]:
        if candidate in tx.columns:
            cust_id_col = candidate
            break
    if cust_id_col is None:
        raise RuntimeError("No customer identifier column found in transactions file.")

    # Standardise amount column
    amount_col = None
    for candidate in ["amount", "amt", "tran_amount", "value"]:
        if candidate in tx.columns:
            amount_col = candidate
            break
    if amount_col is None:
        tx["amount_numeric"] = 0.0
    else:
        tx["amount_numeric"] = pd.to_numeric(tx[amount_col], errors="coerce").fillna(0.0)

    # Create lower-case description to help matching
    if "description" in tx.columns:
        tx["desc_lower"] = tx["description"].astype(str).str.lower()
    else:
        tx["desc_lower"] = ""

    # Tag transactions using substring mapping (first-match)
    def map_tag(desc):
        for k, v in txn_mapping.items():
            if pd.isna(desc):
                continue
            if k in desc:
                return v
        return "other"

    tx["txn_tag"] = tx["desc_lower"].apply(map_tag)

    # Assign a simple customer_initiated flag based on keywords and direction
    def is_customer_initiated(row):
        desc = row.get("desc_lower", "")
        # Example logic: if description contains keywords that imply the customer performed the action
        if any(kw in desc for kw in customer_initiated_keywords):
            return True
        # If there is a 'direction' or 'transaction_type' column, use it (example placeholders)
        for col in ["direction", "tran_type", "tran_dir"]:
            if col in row and pd.notna(row[col]):
                if str(row[col]).lower() in ("debit", "out", "payout"):
                    return True
        return False

    tx["customer_initiated"] = tx.apply(is_customer_initiated, axis=1)

    # Example: identify loan-related receipts/payments using tags + description heuristics
    tx["is_loan_transaction"] = tx["txn_tag"].apply(lambda x: True if "loan" in x else False)

    # Aggregate per customer for the month (counts & sums per tag)
    counts = tx.groupby([cust_id_col, "txn_tag"]).size().unstack(fill_value=0).add_prefix("txn_count_").reset_index()
    sums = tx.groupby([cust_id_col, "txn_tag"])["amount_numeric"].sum().unstack(fill_value=0).add_prefix("txn_sum_").reset_index()
    totals = tx.groupby(cust_id_col).agg(
        total_transactions=(cust_id_col, "count"),
        total_amount=("amount_numeric", "sum")
    ).reset_index()

    monthly_summary = totals.merge(counts, left_on=cust_id_col, right_on=cust_id_col, how="left").merge(sums, left_on=cust_id_col, right_on=cust_id_col, how="left")
    monthly_summary["month_file"] = tx_file.name

    # Store the lightweight monthly summary
    tx_monthly_summaries.append(monthly_summary)

# Concatenate monthly summaries into a single aggregated table (customer x tags across months)
if tx_monthly_summaries:
    tx_agg = pd.concat(tx_monthly_summaries, ignore_index=True)
    # Optional: roll up across months to get per-customer totals across the period
    rollup_counts = tx_agg.groupby(cust_id_col).agg(
        total_transactions_period=("total_transactions", "sum"),
        total_amount_period=("total_amount", "sum")
    ).reset_index()
    # For tag-level columns, sum numerics across months (simple heuristic)
    tag_cols = [c for c in tx_agg.columns if c.startswith("txn_count_") or c.startswith("txn_sum_")]
    rollup_tag_sums = tx_agg.groupby(cust_id_col)[tag_cols].sum().reset_index()
    tx_rollup = rollup_counts.merge(rollup_tag_sums, on=cust_id_col, how="left")
    # Save aggregated transaction summaries
    TX_OUTPUT = OUTPUT_DIR / "transactions_aggregated_by_customer.csv"
    print(f"\nSaving transaction aggregates to {TX_OUTPUT}")
    tx_rollup.to_csv(TX_OUTPUT, index=False)
else:
    print("No monthly transaction summaries were produced (no files found).")
