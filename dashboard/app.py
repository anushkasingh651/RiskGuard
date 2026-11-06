import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RiskGuard | Internal Audit Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME COLORS
# =========================================================

NAVY = "#14213D"
BLUE = "#274C77"
LIGHT_BLUE = "#6096BA"
PALE_BLUE = "#E7EFF6"
DARK_TEXT = "#14213D"
MUTED_TEXT = "#475569"
BORDER = "#E5E7EB"
WHITE = "#FFFFFF"

CHART_COLORS = [
    NAVY,
    BLUE,
    LIGHT_BLUE,
    "#8EACCD",
    "#B7CBE2"
]

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* Main background */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #FFFFFF !important;
    color: #14213D !important;
}

/* Hide Streamlit top bar */
[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Global typography */
html, body, [class*="css"] {
    font-family: Arial, sans-serif !important;
    color: #14213D !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #14213D !important;
    font-weight: 800 !important;
}

/* Text */
p, label, span {
    color: #14213D;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB;
}

section[data-testid="stSidebar"] * {
    color: #14213D !important;
    font-weight: 700 !important;
}

/* Sidebar navigation */
section[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: #FFFFFF;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 5px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(20,33,61,0.05);
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-weight: 800 !important;
}

[data-testid="stMetricValue"] {
    color: #14213D !important;
    font-weight: 800 !important;
}

/* Buttons */
.stButton > button {
    background-color: #14213D;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    padding: 8px 18px;
}

.stButton > button:hover {
    background-color: #274C77;
    color: #FFFFFF !important;
}

/* Download buttons */
.stDownloadButton > button {
    background-color: #14213D;
    color: #FFFFFF !important;
    border-radius: 8px;
    font-weight: 700;
}

/* Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}

/* Select boxes */
[data-testid="stSelectbox"] label {
    font-weight: 800 !important;
    color: #14213D !important;
}

/* Dividers */
hr {
    border: 1px solid #E5E7EB;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}

/* Captions */
.stCaption {
    color: #475569 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "riskguard.db"
)

REPORT_PATH = os.path.join(
    BASE_DIR,
    "reports",
    "audit_findings.csv"
)


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data
def load_findings():

    if not os.path.exists(REPORT_PATH):
        return pd.DataFrame()

    return pd.read_csv(REPORT_PATH)


@st.cache_data
def load_table(table_name):

    if not os.path.exists(DATABASE_PATH):
        return pd.DataFrame()

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        df = pd.read_sql_query(
            f'SELECT * FROM "{table_name}"',
            connection
        )

    except Exception:
        df = pd.DataFrame()

    finally:
        connection.close()

    return df


# =========================================================
# LOAD DATABASE TABLES
# =========================================================

findings_df = load_findings()

vendors_df = load_table("vendors")
purchase_orders_df = load_table("purchase_orders")
goods_receipts_df = load_table("goods_receipts")
invoices_df = load_table("invoices")
payments_df = load_table("payments")
approvals_df = load_table("approvals")


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_numeric_total(df, column):

    if df.empty or column not in df.columns:
        return 0

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0).sum()


def get_risk_count(df, risk_level):

    if df.empty or "Risk_Level" not in df.columns:
        return 0

    return (
        df["Risk_Level"]
        .astype(str)
        .str.upper()
        .eq(risk_level.upper())
        .sum()
    )


def display_table(df):

    if df.empty:
        st.info("No records available.")
    else:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )


def format_currency(value):

    return f"₹{value:,.2f}"


# =========================================================
# COMMON PLOTLY LAYOUT
# =========================================================

def apply_chart_theme(fig):

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial",
            color=NAVY,
            size=13
        ),
        title_font=dict(
            family="Arial",
            color=NAVY,
            size=17
        ),
        legend=dict(
            font=dict(
                family="Arial",
                color=NAVY,
                size=12
            ),
            title_font=dict(
                family="Arial",
                color=NAVY,
                size=13
            )
        ),
        margin=dict(
            l=20,
            r=25,
            t=45,
            b=25
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
        tickfont=dict(
            family="Arial",
            size=12,
            color=NAVY
        ),
        title_font=dict(
            family="Arial",
            size=13,
            color=NAVY
        )
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            family="Arial",
            size=13,
            color=NAVY
        ),
        title_font=dict(
            family="Arial",
            size=13,
            color=NAVY
        )
    )

    return fig


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style="font-size:30px; color:#14213D;">
            🛡️ RiskGuard
        </h1>

        <p style="font-size:12px; color:#475569;">
            INTERNAL AUDIT & CONTROLS ANALYTICS
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Executive Overview",
            "Audit Findings",
            "Transaction Explorer",
            "Audit Methodology"
        ]
    )

    st.divider()

    st.markdown(
        """
        **PROJECT STATUS**

        <span style="color:#274C77;">●</span> Analytics Dashboard

        <span style="color:#274C77;">●</span> SQL Database

        <span style="color:#274C77;">●</span> Audit Testing
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.caption("RiskGuard | Portfolio Project")
    st.caption("Version 1.0")


# =========================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":

    st.title("Executive Overview")

    st.markdown(
        "### Internal Audit & Financial Controls Monitoring"
    )

    st.caption(
        "A centralized view of transaction exceptions, "
        "control weaknesses and potential financial exposure."
    )

    st.divider()

    total_findings = len(findings_df)

    critical_findings = get_risk_count(
        findings_df,
        "Critical"
    )

    high_findings = get_risk_count(
        findings_df,
        "High"
    )

    medium_findings = get_risk_count(
        findings_df,
        "Medium"
    )

    total_amount_at_risk = get_numeric_total(
        findings_df,
        "Amount_At_Risk"
    )

    total_invoices = len(invoices_df)
    total_payments = len(payments_df)

    # KPI ROW 1

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Audit Findings",
        f"{total_findings:,}"
    )

    col2.metric(
        "Critical Findings",
        f"{critical_findings:,}"
    )

    col3.metric(
        "High-Risk Findings",
        f"{high_findings:,}"
    )

    col4.metric(
        "Medium-Risk Findings",
        f"{medium_findings:,}"
    )

    st.write("")

    # KPI ROW 2

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Invoices Reviewed",
        f"{total_invoices:,}"
    )

    col6.metric(
        "Payments Reviewed",
        f"{total_payments:,}"
    )

    col7.metric(
        "Amount at Risk",
        format_currency(total_amount_at_risk)
    )

    st.caption(
        "Amount at Risk is the sum of identified exception amounts. "
        "It is not a confirmed financial loss. Overlapping exceptions "
        "may be counted more than once."
    )

    st.divider()

    # CHARTS

    st.subheader("Audit Risk Analysis")

    chart_col1, chart_col2 = st.columns(2)

    # -----------------------------------------------------
    # RISK DISTRIBUTION PIE CHART
    # -----------------------------------------------------

    with chart_col1:

        st.markdown("#### Risk Distribution")

        if (
            not findings_df.empty
            and "Risk_Level" in findings_df.columns
        ):

            risk_data = (
                findings_df["Risk_Level"]
                .fillna("Unclassified")
                .value_counts()
                .reset_index()
            )

            risk_data.columns = [
                "Risk Level",
                "Count"
            ]

            fig = px.pie(
                risk_data,
                names="Risk Level",
                values="Count",
                hole=0.55,
                color_discrete_sequence=CHART_COLORS
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont=dict(
                    family="Arial",
                    size=12,
                    color=WHITE
                ),
                marker=dict(
                    line=dict(
                        color=WHITE,
                        width=2
                    )
                )
            )

            fig = apply_chart_theme(fig)

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info("Risk distribution data is not available.")

    # -----------------------------------------------------
    # FINDINGS BY AUDIT TEST
    # -----------------------------------------------------

    with chart_col2:

        st.markdown("#### Findings by Audit Test")

        if (
            not findings_df.empty
            and "Test_Name" in findings_df.columns
        ):

            test_data = (
                findings_df["Test_Name"]
                .value_counts()
                .reset_index()
            )

            test_data.columns = [
                "Audit Test",
                "Findings"
            ]

            fig = px.bar(
                test_data,
                x="Findings",
                y="Audit Test",
                orientation="h",
                text="Findings"
            )

            fig.update_traces(
                marker_color=BLUE,
                marker_line_color=NAVY,
                marker_line_width=0.5,
                textposition="outside",
                textfont=dict(
                    family="Arial",
                    size=13,
                    color=NAVY
                ),
                cliponaxis=False
            )

            fig = apply_chart_theme(fig)

            # Bold, dark Y-axis labels
            fig.update_yaxes(
                categoryorder="total ascending",
                tickfont=dict(
                    family="Arial",
                    size=13,
                    color=NAVY
                ),
                title_font=dict(
                    family="Arial",
                    size=14,
                    color=NAVY
                )
            )

            fig.update_xaxes(
                title_text="Number of Findings",
                tickfont=dict(
                    family="Arial",
                    size=12,
                    color=NAVY
                ),
                title_font=dict(
                    family="Arial",
                    size=13,
                    color=NAVY
                )
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info("Audit test data is not available.")

    st.divider()

    # PRIORITY FINDINGS

    st.subheader("Priority Audit Findings")

    if not findings_df.empty:

        priority_df = findings_df.copy()

        if "Risk_Level" in priority_df.columns:

            priority_order = {
                "Critical": 1,
                "High": 2,
                "Medium": 3,
                "Low": 4
            }

            priority_df["_priority"] = (
                priority_df["Risk_Level"]
                .astype(str)
                .str.title()
                .map(priority_order)
                .fillna(5)
            )

            priority_df = priority_df.sort_values(
                "_priority"
            )

            priority_df = priority_df.drop(
                columns=["_priority"]
            )

        display_columns = [
            column
            for column in [
                "Finding_ID",
                "Test_Name",
                "Risk_Level",
                "Record_ID",
                "Description",
                "Amount_At_Risk"
            ]
            if column in priority_df.columns
        ]

        st.dataframe(
            priority_df[display_columns].head(10),
            width="stretch",
            hide_index=True
        )

    else:

        st.success("No audit findings are currently available.")


# =========================================================
# PAGE 2: AUDIT FINDINGS
# =========================================================

elif page == "Audit Findings":

    st.title("Audit Findings")

    st.markdown(
        "### Exception Register & Risk Assessment"
    )

    st.caption(
        "Review identified exceptions, assess risk levels "
        "and examine recommended control actions."
    )

    st.divider()

    if findings_df.empty:

        st.warning(
            "Audit findings file not found. "
            "Run the audit tests before opening this page."
        )

    else:

        filtered_df = findings_df.copy()

        col1, col2 = st.columns(2)

        # RISK FILTER

        if "Risk_Level" in filtered_df.columns:

            risk_options = [
                "All"
            ] + sorted(
                filtered_df["Risk_Level"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_risk = col1.selectbox(
                "Filter by Risk Level",
                risk_options
            )

            if selected_risk != "All":

                filtered_df = filtered_df[
                    filtered_df["Risk_Level"].astype(str)
                    == selected_risk
                ]

        # AUDIT TEST FILTER

        if "Test_Name" in filtered_df.columns:

            test_options = [
                "All"
            ] + sorted(
                filtered_df["Test_Name"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_test = col2.selectbox(
                "Filter by Audit Test",
                test_options
            )

            if selected_test != "All":

                filtered_df = filtered_df[
                    filtered_df["Test_Name"].astype(str)
                    == selected_test
                ]

        st.write("")

        st.metric(
            "Filtered Findings",
            len(filtered_df)
        )

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            label="Download Filtered Findings",
            data=filtered_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="riskguard_filtered_findings.csv",
            mime="text/csv"
        )

        st.divider()

        st.subheader("Finding Details")

        if (
            "Finding_ID" in filtered_df.columns
            and not filtered_df.empty
        ):

            finding_ids = (
                filtered_df["Finding_ID"]
                .astype(str)
                .tolist()
            )

            selected_finding = st.selectbox(
                "Select a Finding",
                finding_ids
            )

            finding = filtered_df[
                filtered_df["Finding_ID"].astype(str)
                == selected_finding
            ].iloc[0]

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:

                st.markdown("#### Finding Information")

                for column in [
                    "Finding_ID",
                    "Test_Name",
                    "Risk_Level",
                    "Record_ID",
                    "Amount_At_Risk"
                ]:

                    if column in finding.index:

                        st.write(
                            f"**{column.replace('_', ' ')}:** "
                            f"{finding[column]}"
                        )

            with detail_col2:

                st.markdown("#### Audit Observation")

                if "Description" in finding.index:

                    st.write(
                        finding["Description"]
                    )

                st.markdown("#### Recommended Action")

                if "Recommendation" in finding.index:

                    st.write(
                        finding["Recommendation"]
                    )


# =========================================================
# PAGE 3: TRANSACTION EXPLORER
# =========================================================

elif page == "Transaction Explorer":

    st.title("Transaction Explorer")

    st.markdown(
        "### Procurement-to-Pay Transaction Data"
    )

    st.caption(
        "Explore the synthetic transaction records "
        "used in the audit procedures."
    )

    st.divider()

    dataset_options = {
        "Vendors": vendors_df,
        "Purchase Orders": purchase_orders_df,
        "Goods Receipts": goods_receipts_df,
        "Invoices": invoices_df,
        "Payments": payments_df,
        "Approvals": approvals_df
    }

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys())
    )

    selected_df = dataset_options[
        selected_dataset
    ]

    st.subheader(selected_dataset)

    if selected_df.empty:

        st.warning(
            "No data available. Check the database setup."
        )

    else:

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Records",
            f"{len(selected_df):,}"
        )

        col2.metric(
            "Total Columns",
            f"{len(selected_df.columns):,}"
        )

        st.dataframe(
            selected_df,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            label=f"Download {selected_dataset} CSV",
            data=selected_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                selected_dataset.lower()
                .replace(" ", "_") + ".csv"
            ),
            mime="text/csv"
        )


# =========================================================
# PAGE 4: AUDIT METHODOLOGY
# =========================================================

elif page == "Audit Methodology":

    st.title("Audit Methodology")

    st.markdown(
        "### Procurement-to-Pay Internal Controls Testing"
    )

    st.write(
        """
        RiskGuard is a portfolio project demonstrating how
        data analytics can support internal audit procedures,
        transaction monitoring and financial control reviews.
        """
    )

    st.divider()

    st.subheader("Audit Procedures")

    audit_tests = [
        {
            "Test": "Duplicate Invoice Detection",
            "Objective": "Identify repeated invoice numbers for the same vendor.",
            "Risk": "Duplicate or repeated invoice processing."
        },
        {
            "Test": "Missing Purchase Order",
            "Objective": "Identify invoices without an associated purchase order.",
            "Risk": "Purchases processed outside the approved procurement process."
        },
        {
            "Test": "Invalid Purchase Order Reference",
            "Objective": "Identify invoices referencing purchase orders that do not exist.",
            "Risk": "Incorrect or unsupported transaction references."
        },
        {
            "Test": "Invoice Amount Exceeds PO",
            "Objective": "Compare invoice amounts against purchase order values.",
            "Risk": "Potential overbilling or approval limit breach."
        },
        {
            "Test": "Vendor Mismatch",
            "Objective": "Compare invoice vendor information with purchase order vendor information.",
            "Risk": "Incorrect vendor association."
        },
        {
            "Test": "Unapproved Purchase Order",
            "Objective": "Identify purchase orders without an approval record.",
            "Risk": "Procurement authorization control weakness."
        },
        {
            "Test": "Missing Goods Receipt",
            "Objective": "Identify purchase orders without a corresponding goods receipt.",
            "Risk": "Insufficient evidence of goods receipt."
        },
        {
            "Test": "Payment Exceeds Invoice",
            "Objective": "Compare payment amounts with invoice amounts.",
            "Risk": "Potential overpayment requiring investigation."
        },
        {
            "Test": "Inactive Vendor Invoice",
            "Objective": "Identify invoices associated with inactive vendors.",
            "Risk": "Transactions involving vendors marked inactive."
        }
    ]

    methodology_df = pd.DataFrame(
        audit_tests
    )

    st.dataframe(
        methodology_df,
        width="stretch",
        hide_index=True
    )

    st.divider()

    st.subheader("Risk Classification")

    risk_col1, risk_col2 = st.columns(2)

    with risk_col1:

        st.markdown("#### Critical Risk")

        st.write(
            "Exceptions that may indicate significant control "
            "weaknesses or substantial financial exposure and "
            "require prompt review."
        )

        st.markdown("#### High Risk")

        st.write(
            "Exceptions that may expose the organization to "
            "material financial, operational or compliance risks."
        )

    with risk_col2:

        st.markdown("#### Medium Risk")

        st.write(
            "Exceptions requiring investigation and appropriate "
            "management review."
        )

        st.markdown("#### Low Risk")

        st.write(
            "Lower-priority exceptions that may require routine "
            "monitoring or documentation."
        )

    st.divider()

    st.subheader("Technology Stack")

    st.markdown(
        """
        - **Python:** Data processing and audit automation
        - **SQL / SQLite:** Transaction data storage and querying
        - **Pandas:** Data manipulation and exception analysis
        - **NumPy:** Numerical analysis
        - **Streamlit:** Interactive dashboard
        - **Plotly:** Data visualization
        - **Excel / OpenPyXL:** Audit reporting
        """
    )

    st.divider()

    st.subheader("Important Project Disclaimer")

    st.info(
        """
        RiskGuard uses artificially generated synthetic data
        for educational and portfolio demonstration purposes.

        Identified exceptions are indicators requiring further
        investigation. They do not establish fraud, misconduct
        or confirmed financial loss.

        The project does not use confidential data from any
        organization.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#475569;
        padding:10px;
        background-color:#FFFFFF;
    ">
        <b style="color:#14213D;">
            RISKGUARD
        </b>
        <br>
        Internal Audit & Controls Analytics
        <br>
        Synthetic Data | Portfolio Demonstration
    </div>
    """,
    unsafe_allow_html=True
)