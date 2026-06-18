# Bank Customer Churn Analytics – Data Preparation with Python

## Overview

This project demonstrates the preparation and transformation of anonymized banking data using Python and pandas to create analytical datasets for business intelligence reporting.

The project combines customer profile information, churn records, loan activity, and transactional data into structured datasets that can be consumed by Power BI for customer analytics, segmentation, and performance reporting.

The workflow focuses on transforming raw operational data into business-ready information through data cleaning, feature engineering, enrichment, categorization, and aggregation. 

Explore the [Dashboard](https://app.powerbi.com/view?r=eyJrIjoiYTExNTM0MDgtZTdlZC00MzQyLTk5YzctZjY1YmNhZjE0ODVlIiwidCI6ImQ4YWJjM2VkLWE2ZTEtNGUzNi1iMGFhLTQ1NzA3Zjc5M2YxMiJ9)

---

## Business Context

Financial institutions generate large volumes of customer and transaction data across multiple systems. Before meaningful analysis can take place, these datasets must be standardized, validated, enriched, and consolidated.

This project illustrates a typical analytics workflow in which Python is used to prepare data for downstream reporting and dashboarding applications.

---

## Key Data Preparation Activities

### Customer Profile Dataset

* Combined multiple customer source files
* Standardized customer identifiers
* Performed exploratory data analysis (EDA)
* Assessed missing values and data quality issues
* Removed duplicate and invalid records
* Derived customer age and tenure features
* Created customer age groups
* Integrated churn information
* Integrated loan application outcomes
* Exported a clean customer master dataset

### Transaction Dataset

* Processed seven months transaction files
* Standardized transaction structures and fields
* Categorized transactions using rule-based mappings
* Identified customer-initiated activities
* Flagged loan-related and insurance-related transactions
* Aggregated transactions at customer level
* Produced customer transaction summary tables
* Prepared analytical datasets for Power BI reporting

---

## Technology Stack

* Python
* Pandas
* NumPy
* OpenPyXL
* CSV / Excel
* Power BI

---

## Data Processing Workflow

Raw Customer Files
- Data Quality Checks
- Data Cleaning & Standardization
- Feature Engineering
- Churn & Loan Integration

Raw Transaction Files
- Transaction Categorization
- Customer-Initiated Classification
- Customer-Level Aggregation

Combined Analytical Dataset
- Power BI Dashboard & Reporting

---

## Dashboard Output

The transformed datasets were subsequently used to build an interactive Power BI dashboard focused on:

* Customer segmentation
* Customer churn analysis
* Product engagement
* Transaction behaviour
* Customer demographics
* Financial activity trends

Dashboard screenshots can be found in the images directory.

---

## Data Privacy

All datasets used within this repository have been anonymized.

No customer-identifiable information, confidential banking records, or proprietary classification dictionaries are included.

This repository is intended solely to demonstrate data preparation and analytics techniques.

---

## Future Enhancements

Potential future improvements include:

* Automated monthly data refresh processes
* Data quality monitoring dashboards
* Cloud-based data pipelines
* Incremental transaction processing
* Power BI Service integration
* Automated reporting workflows
