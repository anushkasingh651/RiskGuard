import sqlite3
import pandas as pd
from pathlib import Path

# ------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "database" / "riskguard.db"

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = REPORT_DIR / "audit_findings.csv"


# ------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------

connection = sqlite3.connect(DB_PATH)

findings = []


# ------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------

def add_finding(
    test_name,
    risk_level,
    record_id,
    description,
    amount_at_risk,
    recommendation
):

    findings.append({
        "Finding_ID": f"RG{len(findings) + 1:04d}",
        "Test_Name": test_name,
        "Risk_Level": risk_level,
        "Record_ID": str(record_id),
        "Description": description,
        "Amount_At_Risk": amount_at_risk,
        "Recommendation": recommendation
    })


def run_query(query):

    return pd.read_sql_query(query, connection)


# ------------------------------------------------
# TEST 1: DUPLICATE INVOICE DETECTION
# ------------------------------------------------

print("\nRunning duplicate invoice test...")

query = """
SELECT
    Vendor_ID,
    Invoice_Number,
    COUNT(*) AS Duplicate_Count,
    GROUP_CONCAT(Invoice_ID) AS Invoice_Records,
    MAX(Invoice_Amount) AS Amount
FROM invoices
GROUP BY Vendor_ID, Invoice_Number
HAVING COUNT(*) > 1
"""

duplicate_invoices = run_query(query)

for _, row in duplicate_invoices.iterrows():

    add_finding(
        "Duplicate Invoice",
        "Critical",
        row["Invoice_Records"],
        f"Vendor {row['Vendor_ID']} submitted "
        f"invoice number {row['Invoice_Number']} "
        f"{int(row['Duplicate_Count'])} times.",
        float(row["Amount"]),
        "Investigate duplicate submissions and "
        "verify whether duplicate payments occurred."
    )


# ------------------------------------------------
# TEST 2: INVOICE WITHOUT PURCHASE ORDER
# ------------------------------------------------

print("Running missing PO test...")

query = """
SELECT
    Invoice_ID,
    Vendor_ID,
    Invoice_Amount
FROM invoices
WHERE PO_ID IS NULL
"""

missing_pos = run_query(query)

for _, row in missing_pos.iterrows():

    add_finding(
        "Missing Purchase Order",
        "High",
        row["Invoice_ID"],
        f"Invoice {row['Invoice_ID']} has no "
        "associated purchase order.",
        float(row["Invoice_Amount"]),
        "Verify purchase authorization and obtain "
        "supporting purchase documentation."
    )


# ------------------------------------------------
# TEST 3: INVALID PURCHASE ORDER
# ------------------------------------------------

print("Running invalid PO test...")

query = """
SELECT
    i.Invoice_ID,
    i.PO_ID,
    i.Invoice_Amount
FROM invoices i
LEFT JOIN purchase_orders p
    ON i.PO_ID = p.PO_ID
WHERE i.PO_ID IS NOT NULL
AND p.PO_ID IS NULL
"""

invalid_pos = run_query(query)

for _, row in invalid_pos.iterrows():

    add_finding(
        "Invalid Purchase Order",
        "High",
        row["Invoice_ID"],
        f"Invoice references nonexistent PO "
        f"{row['PO_ID']}.",
        float(row["Invoice_Amount"]),
        "Validate the purchase order reference "
        "before processing the invoice."
    )


# ------------------------------------------------
# TEST 4: INVOICE AMOUNT EXCEEDS PO AMOUNT
# ------------------------------------------------

print("Running invoice-to-PO matching test...")

query = """
SELECT
    i.Invoice_ID,
    i.PO_ID,
    i.Invoice_Amount,
    p.PO_Amount
FROM invoices i
JOIN purchase_orders p
    ON i.PO_ID = p.PO_ID
WHERE i.Invoice_Amount > p.PO_Amount
"""

amount_mismatches = run_query(query)

for _, row in amount_mismatches.iterrows():

    difference = (
        row["Invoice_Amount"] - row["PO_Amount"]
    )

    add_finding(
        "Invoice Exceeds PO",
        "High",
        row["Invoice_ID"],
        f"Invoice amount exceeds PO amount by "
        f"{difference:.2f}.",
        float(difference),
        "Investigate price differences and obtain "
        "an authorized PO amendment if applicable."
    )


# ------------------------------------------------
# TEST 5: VENDOR MISMATCH
# ------------------------------------------------

print("Running vendor consistency test...")

query = """
SELECT
    i.Invoice_ID,
    i.Vendor_ID AS Invoice_Vendor,
    p.Vendor_ID AS PO_Vendor,
    i.Invoice_Amount
FROM invoices i
JOIN purchase_orders p
    ON i.PO_ID = p.PO_ID
WHERE i.Vendor_ID != p.Vendor_ID
"""

vendor_mismatches = run_query(query)

for _, row in vendor_mismatches.iterrows():

    add_finding(
        "Vendor Mismatch",
        "High",
        row["Invoice_ID"],
        f"Invoice vendor {row['Invoice_Vendor']} "
        f"does not match PO vendor {row['PO_Vendor']}.",
        float(row["Invoice_Amount"]),
        "Verify vendor identity and investigate "
        "potential unauthorized vendor substitution."
    )


# ------------------------------------------------
# TEST 6: PURCHASE ORDER APPROVAL
# ------------------------------------------------

print("Running approval control test...")

query = """
SELECT
    PO_ID,
    Vendor_ID,
    PO_Amount,
    Approval_Status
FROM purchase_orders
WHERE Approval_Status != 'Approved'
"""

unapproved_pos = run_query(query)

for _, row in unapproved_pos.iterrows():

    add_finding(
        "Unapproved Purchase Order",
        "High",
        row["PO_ID"],
        f"Purchase order has status "
        f"{row['Approval_Status']}.",
        float(row["PO_Amount"]),
        "Obtain documented approval before "
        "authorizing the purchase."
    )


# ------------------------------------------------
# TEST 7: MISSING GOODS RECEIPT
# ------------------------------------------------

print("Running goods receipt test...")

query = """
SELECT
    i.Invoice_ID,
    i.PO_ID,
    i.Invoice_Amount
FROM invoices i
JOIN purchase_orders p
    ON i.PO_ID = p.PO_ID
WHERE NOT EXISTS (
    SELECT 1
    FROM goods_receipts g
    WHERE g.PO_ID = i.PO_ID
)
"""

missing_grn = run_query(query)

for _, row in missing_grn.iterrows():

    add_finding(
        "Missing Goods Receipt",
        "Medium",
        row["Invoice_ID"],
        f"No goods receipt record found for "
        f"PO {row['PO_ID']}.",
        float(row["Invoice_Amount"]),
        "Verify goods or services were received "
        "before approving the invoice."
    )


# ------------------------------------------------
# TEST 8: PAYMENT EXCEEDS INVOICE
# ------------------------------------------------

print("Running payment audit test...")

query = """
SELECT
    p.Payment_ID,
    p.Invoice_ID,
    p.Payment_Amount,
    i.Invoice_Amount
FROM payments p
JOIN invoices i
    ON p.Invoice_ID = i.Invoice_ID
WHERE p.Payment_Amount > i.Invoice_Amount
"""

payment_mismatches = run_query(query)

for _, row in payment_mismatches.iterrows():

    difference = (
        row["Payment_Amount"] - row["Invoice_Amount"]
    )

    add_finding(
        "Payment Exceeds Invoice",
        "Critical",
        row["Payment_ID"],
        f"Payment exceeds invoice amount by "
        f"{difference:.2f}.",
        float(difference),
        "Investigate the excess payment and "
        "initiate recovery where appropriate."
    )


# ------------------------------------------------
# TEST 9: INACTIVE VENDOR TRANSACTIONS
# ------------------------------------------------

print("Running vendor status test...")

query = """
SELECT
    i.Invoice_ID,
    i.Vendor_ID,
    i.Invoice_Amount,
    v.Status
FROM invoices i
JOIN vendors v
    ON i.Vendor_ID = v.Vendor_ID
WHERE v.Status = 'Inactive'
"""

inactive_vendors = run_query(query)

for _, row in inactive_vendors.iterrows():

    add_finding(
        "Inactive Vendor Transaction",
        "High",
        row["Invoice_ID"],
        f"Invoice belongs to inactive vendor "
        f"{row['Vendor_ID']}.",
        float(row["Invoice_Amount"]),
        "Verify vendor status and investigate "
        "whether the transaction was authorized."
    )


# ------------------------------------------------
# EXPORT AUDIT FINDINGS
# ------------------------------------------------

findings_df = pd.DataFrame(findings)

if findings_df.empty:

    findings_df = pd.DataFrame(columns=[
        "Finding_ID",
        "Test_Name",
        "Risk_Level",
        "Record_ID",
        "Description",
        "Amount_At_Risk",
        "Recommendation"
    ])

findings_df.to_csv(OUTPUT_PATH, index=False)


# ------------------------------------------------
# SUMMARY
# ------------------------------------------------

print("\n======================================")
print("       RISKGUARD AUDIT RESULTS")
print("======================================")

print(f"\nTotal Audit Findings: {len(findings_df)}")

if not findings_df.empty:

    print("\nRisk Distribution:")

    print(
        findings_df["Risk_Level"]
        .value_counts()
        .to_string()
    )

    print(
        "\nTotal Amount at Risk:",
        round(
            findings_df["Amount_At_Risk"].sum(),
            2
        )
    )

    print("\nAudit Test Distribution:")

    print(
        findings_df["Test_Name"]
        .value_counts()
        .to_string()
    )

print("\nReport saved at:")
print(OUTPUT_PATH)

connection.close()

print("\nRiskGuard audit testing completed!")