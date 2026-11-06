import pandas as pd
import numpy as np
from pathlib import Path

# Reproducible synthetic data
np.random.seed(42)

# Project data directory
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# 1. VENDORS
# --------------------------------------------------

vendors = pd.DataFrame({
    "Vendor_ID": [f"V{str(i).zfill(3)}" for i in range(1, 21)],
    "Vendor_Name": [
        f"Vendor {i}" for i in range(1, 21)
    ],
    "Bank_Account": [
        f"ACC{np.random.randint(100000, 999999)}"
        for _ in range(20)
    ],
    "Status": np.random.choice(
        ["Active", "Inactive"],
        size=20,
        p=[0.9, 0.1]
    )
})

vendors.to_csv(DATA_DIR / "vendors.csv", index=False)


# --------------------------------------------------
# 2. PURCHASE ORDERS
# --------------------------------------------------

purchase_orders = pd.DataFrame({
    "PO_ID": [f"PO{str(i).zfill(4)}" for i in range(1, 101)],
    "Vendor_ID": np.random.choice(vendors["Vendor_ID"], 100),
    "PO_Amount": np.random.randint(5000, 100000, 100),
    "Approval_Status": np.random.choice(
        ["Approved", "Pending", "Rejected"],
        size=100,
        p=[0.85, 0.10, 0.05]
    )
})

purchase_orders.to_csv(
    DATA_DIR / "purchase_orders.csv",
    index=False
)


# --------------------------------------------------
# 3. GOODS RECEIPTS
# --------------------------------------------------

goods_receipts = pd.DataFrame({
    "GRN_ID": [f"GRN{str(i).zfill(4)}" for i in range(1, 91)],
    "PO_ID": purchase_orders["PO_ID"].iloc[:90].values,
    "Received_Quantity": np.random.randint(1, 100, 90)
})

goods_receipts.to_csv(
    DATA_DIR / "goods_receipts.csv",
    index=False
)


# --------------------------------------------------
# 4. INVOICES
# --------------------------------------------------

invoices = []

for i in range(1, 121):

    vendor_id = np.random.choice(vendors["Vendor_ID"])

    po_id = (
        np.random.choice(purchase_orders["PO_ID"])
        if i <= 100
        else None
    )

    invoice_amount = np.random.randint(5000, 110000)

    invoices.append({
        "Invoice_ID": f"INV{str(i).zfill(4)}",
        "Invoice_Number": f"INVOICE-{i:04d}",
        "Vendor_ID": vendor_id,
        "PO_ID": po_id,
        "Invoice_Amount": invoice_amount,
        "Invoice_Date": pd.Timestamp("2026-01-01")
        + pd.Timedelta(days=np.random.randint(0, 300))
    })


invoices = pd.DataFrame(invoices)


# Plant a duplicate invoice
invoices.loc[1, "Invoice_Number"] = invoices.loc[0, "Invoice_Number"]
invoices.loc[1, "Vendor_ID"] = invoices.loc[0, "Vendor_ID"]

# Plant an invoice without a PO
invoices.loc[2, "PO_ID"] = None

# Plant an unusually high invoice
invoices.loc[3, "Invoice_Amount"] = 250000

invoices.to_csv(
    DATA_DIR / "invoices.csv",
    index=False
)


# --------------------------------------------------
# 5. PAYMENTS
# --------------------------------------------------

payments = []

for i in range(1, 111):

    invoice_id = np.random.choice(invoices["Invoice_ID"])

    invoice_amount = invoices.loc[
        invoices["Invoice_ID"] == invoice_id,
        "Invoice_Amount"
    ].iloc[0]

    payment_amount = invoice_amount

    # Introduce an overpayment
    if i == 1:
        payment_amount = invoice_amount + 25000

    payments.append({
        "Payment_ID": f"PAY{str(i).zfill(4)}",
        "Invoice_ID": invoice_id,
        "Payment_Amount": payment_amount,
        "Payment_Date": pd.Timestamp("2026-01-01")
        + pd.Timedelta(days=np.random.randint(0, 300))
    })


payments = pd.DataFrame(payments)

payments.to_csv(
    DATA_DIR / "payments.csv",
    index=False
)


# --------------------------------------------------
# 6. APPROVALS
# --------------------------------------------------

approvals = []

for i in range(1, 101):

    approvals.append({
        "Approval_ID": f"APR{str(i).zfill(4)}",
        "Transaction_ID": f"PO{str(i).zfill(4)}",
        "Approver_ID": f"EMP{np.random.randint(1, 15):03d}",
        "Approval_Status": np.random.choice(
            ["Approved", "Pending", "Rejected"],
            p=[0.85, 0.10, 0.05]
        )
    })


approvals = pd.DataFrame(approvals)

# Plant a missing/pending approval
approvals.loc[0, "Approval_Status"] = "Pending"

approvals.to_csv(
    DATA_DIR / "approvals.csv",
    index=False
)


# --------------------------------------------------
# 7. GENERATION SUMMARY
# --------------------------------------------------

print("\n===================================")
print("       RISKGUARD DATA GENERATED")
print("===================================")

print(f"Vendors:          {len(vendors)}")
print(f"Purchase Orders:  {len(purchase_orders)}")
print(f"Goods Receipts:   {len(goods_receipts)}")
print(f"Invoices:         {len(invoices)}")
print(f"Payments:         {len(payments)}")
print(f"Approvals:        {len(approvals)}")

print("\nFiles saved successfully in:", DATA_DIR)

print("\nSynthetic audit exceptions planted:")
print("1. Duplicate invoice")
print("2. Invoice without purchase order")
print("3. Unusually high invoice")
print("4. Payment over invoice amount")
print("5. Pending purchase order approval")

print("\nRiskGuard data generation completed!")