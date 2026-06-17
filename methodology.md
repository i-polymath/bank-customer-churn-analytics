# Methodology

## Project Objective

The objective of this project was to transform raw customer and transaction data into analysis-ready datasets suitable for customer analytics and Power BI reporting.

The methodology consisted of two primary transformation streams:

1. Customer Profile Preparation
2. Transaction Data Preparation

---

# 1. Customer Profile Preparation

## Data Ingestion

Customer profile data was sourced from the client's customer database and converted into a usable CSV. The data contained customer demographic information, account details, and relationship information.

---

## Exploratory Data Analysis

Initial exploratory analysis was performed to understand:

* Dataset dimensions
* Missing values
* Duplicate records
* Identifier consistency
* Distribution of key attributes

Summary statistics and frequency distributions were reviewed to identify data quality issues requiring remediation.

---

## Data Cleaning

Several data quality procedures were applied:

* Standardization of column names
* Identifier formatting and validation
* Removal of duplicate customer records
* Handling of missing values
* Removal of invalid observations
* Standardization of categorical variables

These steps ensured consistency across source systems.

---

## Feature Engineering

Additional analytical variables were derived to support reporting and segmentation.

Examples include:

### Age

Customer age was calculated using date of birth information.

### Customer Tenure

Years since account opening were calculated to measure customer longevity.

### Age Groups

Customers were categorized into age bands to support demographic analysis.

### Branch Enrichment

Additional branch information was incorporated where available.

---

## Customer Enrichment

The customer base was enriched using supplementary datasets including:

### Churn Information

Customer churn records were merged to identify active and churned customers.

### Loan Outcomes

Loan application outcomes were aggregated to create customer-level indicators of unsuccessful loan applications.

---

## Customer Master Dataset

The resulting output was a cleaned and enriched customer profile dataset suitable for downstream reporting and analytics.

---

# 2. Transaction Data Preparation

## Monthly Data Processing

Transaction data was processed on a monthly basis from September 2022 to March 2023. Each monthly dataset underwent a consistent transformation workflow.

---

## Standardization

Transaction datasets were standardized to ensure consistency in:

* Column structures
* Customer identifiers
* Transaction amounts
* Transaction descriptions

---

## Transaction Categorization

Rule-based classification logic was used to group transaction descriptions into broader business categories.

Examples include:

* Loan-related transactions
* Insurance-related transactions
* Transfers
* Withdrawals
* Deposits
* Service charges

This enabled higher-level behavioural analysis.

---

## Customer-Initiated Activity Identification

Business rules were applied to distinguish customer-initiated activities from system-generated transactions.

This classification supported behavioural profiling and engagement analysis.

---

## Customer-Level Aggregation

Transactions were aggregated at customer level to produce metrics such as:

* Transaction volumes
* Transaction counts
* Product usage indicators
* Category-level activity measures

These summaries provided a concise view of customer behaviour over the reporting period.

---

# 3. Final Analytical Dataset

The customer profile dataset and transaction summaries were combined to create a consolidated analytical dataset.

The final dataset served as the primary data source for Power BI dashboards and customer analytics reporting.

---

# Output

The completed transformation pipeline produced:

1. Clean Customer Master Dataset
2. Customer Transaction Summary Dataset
3. Combined Analytical Dataset for Power BI

These outputs enabled customer segmentation, churn analysis, product engagement monitoring, and transaction behaviour reporting.
